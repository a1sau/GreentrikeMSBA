import psycopg2
from configparser import ConfigParser
import config
import csv

def config(filename='C:/Users/Benjamin/Documents/UWTacoma/MSBA/database.ini', section='postgresql'):
    parser = ConfigParser()# create a parser
    parser.read(filename)# read config file
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def connect(): #Found def config and def connect from https://www.postgresqltutorial.com/postgresql-python/connect/
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()# read connection parameters
        print('Connecting to the PostgreSQL database...')# connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        ##
        ETL_Building_Count = 'SELECT COUNT(*) FROM "ETL_Building"'
        cur = conn.cursor()
        cur.execute(ETL_Building_Count)# execute a statement
        count_test = cur.fetchone() #Fetch the results of the statement (Notice fetchone ONLY grabs the first record of the result)
        print("We are starting with {} records in the ETL Table.".format(count_test[0]))
        ETL_Buildng_wipe = 'TRUNCATE "ETL_Building"'
        if count_test[0] != 0:
            cur.execute(ETL_Buildng_wipe)
            print("{} records deleted from the ETL table.".format(count_test[0]))
            conn.commit()
        cur.close()
        # # TODO copy data from csv to Building ETL
            #Ensure that filename will be correct name of most current scrape
        col_names = ("CS_ID","url","Address_Line","City","State","Postal_Code","bg_geo_id","Property_Type","Price","SquareFeet","Building_Class","Year_Built","Sale_Type","Picture_url","Upload_Date","Currently_Listed","Sale_Leased")
        cur = conn.cursor()
        with open('loopnet_listings_2021_03_02-07_49_55_AM.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row.
            for row in reader:
                data = (row[2], row[3],row[4], row[5],row[7], row[6],row[0], row[1],row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16])
                ETL_Building_insert =  "INSERT INTO \"ETL_Building\" VALUES (nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,'')," \
                                       " nullif(%s,''), nullif(%s,''), nullif(%s,'',) cast(nullif(%s,'') as double precision), cast(nullif(%s,'') as double precision)," \
                                       " nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''))"
                ######
                cur.execute("INSERT INTO \"ETL_Building\" (\"CS_ID\",url,\"Address_Line\",\"City\",\"State\",\"Postal_Code\","
                                                  "\"bg_geo_id\",\"Property_Type\",\"Price\",\"SquareFeet\","
                                                  "\"Building_Class\",\"Year_Built\",\"Sale_Type\",\"Picture_url\","
                                                  "\"Upload_Date\",\"Currently_listed\",\"Sale_Lease\")"
                        " VALUES (nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''),"
                                " nullif(%s,''), nullif(%s,''), nullif(%s,''), cast(nullif(%s,'')as double precision), cast(nullif(%s,'') as double precision),"
                                " nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), %s,"
                                " %s, nullif(%s,''))",
                        row)
        conn.commit()
        cur.close()
        #
        cur = conn.cursor()
        # Statement to check ETL_Building against Building.
        left_exclude_join = 'SELECT "ETL_Building".* FROM "ETL_Building" Left JOIN "Building" ON "ETL_Building"."CS_ID" = "Building"."CS_ID" WHERE "Building"."CS_ID" IS NULL'
        cur.execute(left_exclude_join)
        left_exclude_join = cur.fetchall()
        print("There are {} records to be updated from ETL_Building.".format(len(left_exclude_join)))
        for i in left_exclude_join:  #i[6] is CS_ID  i[-2] is Currently_listed  ("Address_Line", "City", "State", "Postal_Code", "Property_Type", "bg_geo_id", "CS_ID", "url", "Price", "SquareFeet", "Building_Class", "Year_Built", "Sale_Type", "Picture_url", "Upload_Date", "Currently_listed", "Sale_Lease")
            data = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12], i[13], i[14], i[15], i[16])
            print("Inserting {} into the Building table".format(i[6]))
            insert_command = "INSERT INTO \"Building\" VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"# insert statement to Builing Table
            cur.execute(insert_command, data) #Pass in two arguments to make life easier.
            # Update Currently listed column to TRUE
            update_command = "UPDATE \"Building\" SET \"Currently_listed\" = true WHERE \"CS_ID\" = '{}'".format(i[6])
            cur.execute(update_command)
        conn.commit()  #ensure that changes are updated to the database
        cur.close()
        #
        ###TODO Check to see if listing are still on loopnet.  This can be done through getting the url and finding if the listing is still active?  Other ideas.
        #
        cur = conn.cursor()
        print('PostgreSQL database version:')# execute a statement
        cur.execute('SELECT version()')
        db_version = cur.fetchone()# display the PostgreSQL database server version
        print(db_version)
        cur.close()# close the communication with the PostgreSQL
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()
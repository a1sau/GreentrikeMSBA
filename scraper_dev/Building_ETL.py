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
        Building_Count = 'SELECT COUNT(*) FROM "Building"'
        cur = conn.cursor()
        cur.execute(ETL_Building_Count)
        count_test = cur.fetchone()
        print("We are starting with {} records in the ETL_Building Table.".format(count_test[0]))
        cur.execute(Building_Count)
        count_test = cur.fetchone()
        print("We are starting with {} records in the Building Table.".format(count_test[0]))
        cur.close()
        # # TODO copy data from csv to Building ETL
        #     #Ensure that filename will be correct name of most current scrape
        col_names = ("CS_ID","url","Address_Line","City","State","Postal_Code","bg_geo_id","Property_Type","Price","SquareFeet","Building_Class","Year_Built","Sale_Type","Picture_url","Upload_Date","Currently_Listed","Sale_Leased")
        # cur = conn.cursor()
        # with open('loopnet_listings_2021_02_10-03_11_00_PM.csv', 'r') as f:
        #     reader = csv.reader(f)
        #     next(reader)  # Skip the header row.
        #     for row in reader:
        #         ETL_Building_insert =  "INSERT INTO \"ETL_Building\" (\"CS_ID\",url,\"Address_Line\",\"City\",\"State\",\"Postal_Code\",\"bg_geo_id\",\"Property_Type\",\"Price\",\"SquareFeet\",\"Building_Class\",\"Year_Built\",\"Sale_Type\",\"Picture_url\",\"Upload_Date\",\"Currently_listed\",\"Sale_Lease\") VALUES (nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''))",row
        #         cur.execute(
        #             "INSERT INTO \"ETL_Building\" (\"CS_ID\",url,\"Address_Line\",\"City\",\"State\",\"Postal_Code\","
        #                                           "\"bg_geo_id\",\"Property_Type\",\"Price\",\"SquareFeet\","
        #                                           "\"Building_Class\",\"Year_Built\",\"Sale_Type\",\"Picture_url\","
        #                                           "\"Upload_Date\",\"Currently_listed\",\"Sale_Lease\")"
        #                 " VALUES (nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''),"
        #                         " nullif(%s,''), nullif(%s,''), nullif(%s,''), cast(nullif(%s,'')as double precision), cast(nullif(%s,'') as double precision),"
        #                         " nullif(%s,''), nullif(%s,''), nullif(%s,''), nullif(%s,''), %s,"
        #                         " %s, nullif(%s,''))",
        #                 row)
        # conn.commit()
        # cur.close()
        #
        cur = conn.cursor()
        left_exclude_join = 'SELECT "ETL_Building".* FROM "ETL_Building" Left JOIN "Building" ON "ETL_Building"."CS_ID" = "Building"."old_CS_ID" WHERE "Building"."CS_ID" IS NULL'
        cur.execute(left_exclude_join)
        left_exclude_join = cur.fetchall()
        original = 'SELECT "Building" FROM "Building"'
        cur.execute(original)
        originallist = cur.fetchall()
        for i in left_exclude_join:  #i[6] is CS_ID  i[-2] is Currently_listed  ("Address_Line", "City", "State", "Postal_Code", "Property_Type", "bg_geo_id", "CS_ID", "url", "Price", "SquareFeet", "Building_Class", "Year_Built", "Sale_Type", "Picture_url", "Upload_Date", "Currently_listed", "Sale_Lease")
            # insert statement
            insert_command = "INSERT INTO \"Building\" VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            data = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12], i[13], i[14], i[15], i[16])
            cur.execute(insert_command, data)
            # Update Currently listed
            update_command = "UPDATE \"Building\" SET \"Currently_listed\" = true WHERE \"CS_ID\" = '{}'".format(i[6])
            cur.execute(update_command)
        conn.commit()
        cur.close()

        cur = conn.cursor()
        cur.execute(ETL_Building_Count)
        count_test = cur.fetchone()
        print("There are now {} records in the ETL Table".format(count_test[0]))
        cur.execute(Building_Count)
        count_test = cur.fetchone()
        print("There are now {} records in the Building Table.".format(count_test[0]))
        cur.close()
        cur = conn.cursor()
        # #
        # # TODO Statement to check ETL table against db table.
        #     #If ON db table and NOT ETL table than mark "Currently_Listed" as False
        #     #If NOT on db table and ON ETL table than update to db table
        #       # Change value of "Currently_Listed" to TRUE at inset.
        #     #If ON db table and ON ETL table than do nothing


        ##  This is where your SQL querry will be
        print('PostgreSQL database version:')# execute a statement
        cur.execute('SELECT version()')
        db_version = cur.fetchone()# display the PostgreSQL database server version
        print(db_version)
        cur.close()# close the communication with the PostgreSQL

        ## We can do multiple SQL statements as long as we set cur and close cur in between.
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()
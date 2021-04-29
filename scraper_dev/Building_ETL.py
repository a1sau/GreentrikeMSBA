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

            # Here is the order of columns as they exist in the Buildings Table.  They have the numerical index for ease of reference.
        # Address_Line[0], City[1], State[2], Postal_Code[3], Property_Type[4], bg_geo_id[5],
        # CS_ID[6], url[7], Price[8], SquareFeet[9], Building_class[10], YearBuilt[11],
        # Sale_Type[12], Picture_URL[13], Upload_Date[14], Currently_Listed[15], Sale_Lease[16], old_CS_ID[17], Price_monthly[18],
        # Price_yearly[19], Expansion_SqrFt[20], Space[21], Condition[22], Available[23], Term[24]

            # Here is the order of columns as they show up in the loopnet_Sale_csv.
        # CS_ID[0] ,url[1] ,Address_Line[2] ,City[3] ,State[4],Postal_Code[5],
        # bg_geo_id[6], Property_Type[7], Price[8], SquareFeet[9], Building_Class[10],Year_Built[11],
        # Sale_Type[12], Picture_url[13], Upload_Date[14], Currently_Listed[15], Sale_Leased[16]

        cur = conn.cursor()
        # Upload Buildings for Sale to ETL_Buildings. loopnet_listings_2021_04_07-09_20_15_AM
        with open('loopnet_listings_2021_04_07-09_20_15_AM.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row.
            for i in reader:
                data = (i[2], i[3], i[4], i[5], i[7], i[6],
                        i[0], i[1], i[8], i[9], i[10], i[11],
                        i[12], i[13], i[14], i[15], i[16], None, None,
                        None, None, None, None, None, None)
                ETL_Building_insert ='INSERT INTO "ETL_Building" VALUES ' \
                               '(%s, %s, %s, %s, %s, %s,' \
                               ' %s, %s, cast(nullif(%s,\'\') as double precision), cast(nullif(%s,\'\') as double precision), %s, %s,' \
                               ' %s, %s, %s, %s, %s, %s, cast(nullif(%s,\'\') as double precision),' \
                               ' cast(nullif(%s,\'\') as double precision), cast(nullif(%s,\'\') as double precision), %s, %s, %s, %s)'
                print(data)
                cur.execute(ETL_Building_insert, data)
        conn.commit()
        cur.close()

        # Upload Buildings for Lease to ETL_Buildings.

            # Here is the order of columns as they exist in the Buildings Table.  They have the numerical index for ease of reference.
        # Address_Line[0], City[1], State[2], Postal_Code[3], Property_Type[4], bg_geo_id[5],
        # CS_ID[6], url[7], Price[8], SquareFeet[9], Building_class[10], YearBuilt[11],
        # Sale_Type[12], Picture_URL[13], Upload_Date[14], Currently_Listed[15], Sale_Lease[16], old_CS_ID[17], Price_monthly[18],
        # Price_yearly[19], Expansion_SqrFt[20], Space[21], Condition[22], Available[23], Term[24]

            # Here is the order of columns as they are listed in the loopnet_Lease_csv.
        # Address_Line[0], City[1], State[2], Postal_Code[3], Property_Type[4],bg_geo_id[5],
        # CS_ID[6], url[7], Price_month[8], Price_year[9], SquareFeet[10], Expansion_SqrFt[11],
        # Space[12], Condition[13],  Available[14], Term[15], Upload_Date[16], Currently_Listed[17], Sale_Lease[18]
        cur = conn.cursor()
        with open('loopnet_listings_lease_2021_04_07-01_52_PM.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)
            for i in reader: #In same order as reference above.
                data = (i[0], i[1], i[2], i[3], i[4], i[5],
                        i[6], i[7], None, i[10], None, None,
                        None, None, i[16], i[17], i[18], None, i[8],
                        i[9], i[11], i[12], i[13], i[14], i[15])
                lease_insert = 'INSERT INTO "ETL_Building" VALUES ' \
                               '(%s, %s, %s, %s, %s, %s,' \
                               ' %s, %s, cast(%s as double precision), cast(%s as double precision), %s, %s,' \
                               ' %s, %s, %s, %s, %s, %s, cast(nullif(%s,\'\') as double precision),' \
                               ' cast(nullif(%s,\'\') as double precision), cast(nullif(%s,\'\') as double precision), %s, %s, %s, %s)'
                print(data)
                cur.execute(lease_insert, data)
            conn.commit()

        # Statement to check ETL_Building against Building.
        cur = conn.cursor()
        left_exclude_join = 'SELECT "ETL_Building".* FROM "ETL_Building" Left JOIN "Building" ON "ETL_Building"."CS_ID" = "Building"."CS_ID" WHERE "Building"."CS_ID" IS NULL'
        cur.execute(left_exclude_join)
        left_exclude_join = cur.fetchall()
        print("There are {} records to be updated from ETL_Building.".format(len(left_exclude_join)))
        for i in left_exclude_join:
            data = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12], i[13], i[14], i[15], i[16],i[17],i[18],i[19],i[20],i[21],i[22],i[23],i[24])
            print("Inserting {} into the Building table".format(i[6]))
            insert_command = 'INSERT INTO "Building" VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' # insert statement to Builing Table
            cur.execute(insert_command, data) #Pass in two arguments to make life easier.
            # Update Currently listed column to TRUE
            update_command = 'UPDATE "Building" SET "Currently_listed" = true WHERE "CS_ID" = \'{}\''.format(i[6])
            cur.execute(update_command)
        conn.commit()  #ensure that changes are updated to the database
        cur.close()

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
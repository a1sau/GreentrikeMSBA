import psycopg2
from configparser import ConfigParser
import config
import csv

def config(filename='C:/Users/Benjamin/Documents/UWTacoma/MSBA/GreentrikeMSBA/database.ini', section='postgresql'):
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
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "ETL_Building"')
        connect_test = cur.fetchone()
        print(connect_test)
        cur.close()
        # # TODO copy data from csv to Building ETL
        #     #Ensure that filename will be correct name of most current scrape
        col_names = ("CS_ID","url","Address_Line","City","State","Postal_Code","bg_geo_id","Property_Type","Price","SquareFeet","Building_Class","Year_Built","Sale_Type","Picture_url","Upload_Date","Currently_Listed","Sale_Leased")

        cur = conn.cursor()
        with open('loopnet_listings_2021_02_11-09_44_13_AM.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row.
            for row in reader:
                if row[9] == '':
                    row[9] = .1
                cur.execute(
                    "INSERT INTO \"ETL_Building\" (\"CS_ID\",url,\"Address_Line\",\"City\",\"State\",\"Postal_Code\","
                                                  "\"bg_geo_id\",\"Property_Type\",\"Price\",\"SquareFeet\","
                                                  "\"Building_Class\",\"Year_Built\",\"Sale_Type\",\"Picture_url\","
                                                  "\"Upload_Date\",\"Currently_listed\",\"Sale_Lease\")"
                        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        row
                )
        conn.commit()
        cur.close()
        #
        cur = conn.cursor()
        cur.execute('UPDATE \"ETL_Building\" SET \"SquareFeet\" = null WHERE \"SquareFeet\"  = .1;')
        conn.commit()
        cur.close()
        cur = conn.cursor()
        # with open('loopnet_listings_2021_01_03-05_52_57_PM.csv', 'r') as f:
        #     # Notice that we don't need the `csv` module.
        #     next(f)  # Skip the header row.
        #     cur.copy_from(f, "\"ETL_Building\"", sep=',')
        # conn.commit()
        # cur.close()
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
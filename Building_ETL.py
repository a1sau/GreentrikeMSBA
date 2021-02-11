import psycopg2
from configparser import ConfigParser
import config

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
        cur = conn.cursor()# create a cursor

        # # TODO copy data from csv to Building ETL
        #     #Ensure that filename will be correct name of most current scrape
        # cur = conn.cursor()
        # with open('Loopnet_Listing_INSERT_DATE_HERE.csv', 'r') as f:
        #     # Notice that we don't need the `csv` module.
        #     next(f)  # Skip the header row.
        #     cur.copy_from(f, 'users', sep=',')
        # conn.commit()
        # cur.close()
        #
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
        ##
        cur = conn.cursor()
        cur.execute('SELECT * FROM "connection_test"')
        connect_test = cur.fetchone()
        print(connect_test)
        cur.close()
        ## We can do multiple SQL statements as long as we set cur and close cur in between.
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()
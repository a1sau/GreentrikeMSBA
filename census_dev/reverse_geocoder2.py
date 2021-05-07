import reverse_geocoder as rg
import sys
import os.path
import psycopg2
import configparser as cp
from uszipcode import SearchEngine


def read_config():
    config_object = cp.ConfigParser()
    config_object.read("config.ini",encoding="utf8")
    return config_object


def create_config() -> None:
    config_object = cp.ConfigParser()
    config_object["Database"] = {
        "host_ip":  'greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com',
        "port": '5432',
        "database": 'TEST',
        "user": '',
        "password": ''
    }
    config_object["Email"] = {
        "email": 'MSBA.Greentrike@gmail.com',
        "password": ''
    }
    with open('config.ini', 'w') as conf:
        config_object.write(conf)


def start(outfilename,limit=0):
    outfile = open(outfilename, 'w')
    count=0
    config = read_config()
    database_config = config['Database']
    try:
        conn = psycopg2.connect(
            host=database_config['host_ip'],
            port=database_config['port'],
            database=database_config['database'],
            user=database_config['user'],
            password=database_config['password'])
    except Exception as e:
        print('Database could not be connected to:')
        print(e)
        return None
    cur = conn.cursor()
    # cur.execute("select * from \"Block_Group\" as bg where bg.city is null")
    sql_statement = "select bg.bg_geo_id, bg.longitude, bg.latitude from \"Block_Group\" as bg " \
                    "where bg.city is null order by bg.bg_geo_id"
    if limit > 0:
        sql_statement += " limit {}".format(limit)
    cur.execute(sql_statement)
    rows = cur.fetchall() #todo Combine all the long/lat into an array and call rg only once
    for row in rows:
        print(row)
        bg_geo=row[0]
        long=row[1]
        lat=row[2]
        result=rg.search((lat,long))
        search=SearchEngine(simple_zipcode=True)
        zip=search.by_coordinates(lat,long,30,returns=1)
        # print(zip)
        print(bg_geo,zip[0].zipcode,result[0]['name'],sep=",")
        print(bg_geo,zip[0].zipcode,result[0]["name"],sep=",",file=outfile)
        count+=1
        if limit and (count >= limit):
            print("Limit reached")
            break
    outfile.close()
    return None


def check_for_config(create_if_missing=False):
    if os.path.isfile("config.ini"):
        return True
    else:
        print("Config is not exists.")
        if create_if_missing:
            print("Attempting to create new config file.")
            create_config()
        print("Please configure ""config.ini"" before running script again.")
        return False


if __name__ == '__main__':
    if check_for_config():
        limit_results = 10   #Comment out line for full results
        start('bg_zip_city2.csv',limit_results)
    else:
        sys.exit("Configure ""config.ini"" before running script again.")


import reverse_geocoder as rg
import multiprocessing as mp
import os.path
import psycopg2
import configparser as cp
from uszipcode import SearchEngine


def read_config():
    config_object = cp.ConfigParser()
    config_object.read("config.ini")
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
    with open('config.ini', 'w') as conf:
        config_object.write(conf)

def read_config():
    config_object = cp.ConfigParser()
    config_object.read("config.ini")
    return config_object

def start(outfilename):
    outfile = open(outfilename, 'w')
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
    cur.execute("select bg.bg_geo_id, bg.longitude, bg.latitude from \"Block_Group\" as bg where bg.city is null order by bg.bg_geo_id")
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
    outfile.close()
    return None


if __name__ == '__main__':
    if os.path.isfile("config.ini"):
        pass
    else:
        print("Config is not exists, attempting to create new file")
        # create_config()
    start('bg_zip_city.csv')

    # mp.freeze_support()
    # coordinates = (51.5214588,-0.1729636),(9.936033, 76.259952),(37.38605,-122.08385)
    # results = rg.search(coordinates,mode=1)
    # print(results)
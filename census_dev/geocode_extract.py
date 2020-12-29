import json
from configparser import ConfigParser
import psycopg2


def create_config() -> None:
    config_object = ConfigParser()
    config_object["Database"] = {
        "host":  'greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com',
        "port": '5432',
        "database": 'TEST',
        "user": '',
        "password": ''
    }
    with open(r'C:\MSBA\config.ini', 'w') as conf:
        config_object.write(conf)


def read_config():
    config_object = ConfigParser()
    config_object.read(r"C:\MSBA\config.ini")
    return config_object


def test_connection():
    config = read_config()
    database_config = config['Database']
    try:
        conn = psycopg2.connect(
            host=database_config['host'],
            port=database_config['port'],
            database=database_config['database'],
            user=database_config['user'],
            password=database_config['password'])
    except Exception as e:
        print('Database could not be connected to:')
        print(e)
        return None
    cur = conn.cursor()
    cur.execute("SELECT tract_geo_id from \"C_Tract\"")
    rows = cur.fetchone()
    print(rows)
    return None


def read_tract(outfilename=None):
    with open(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GeoShapes\tl_2018_53_tract.json') as file:
        data = json.load(file)
    print(len(data['objects']['tl_2018_53_tract']['geometries']))
    print(len(data))
    if outfilename:
        outfile = open(outfilename, 'w')
    else:
        outfile = None
    print('tract_geo_id','latitude','longitude','county_fips_code','tract_geo_id','tract_id','land_area','water_area',sep=",", file=outfile)
    for tract in data['objects']['tl_2018_53_tract']['geometries']:
        geo_id = tract['properties']['GEOID']
        county = int(geo_id[2:5])
        if geo_id[0:5] in ['53033','53053','53067']:
            print(geo_id,tract['properties']['INTPTLAT'][1:],tract['properties']['INTPTLON'],county,
                  tract['properties']['GEOID'][0:11], tract['properties']['GEOID'][5:11],
                  tract['properties']['ALAND'], tract['properties']['AWATER'], sep=",", file=outfile)
    if outfile:
        outfile.close()


def read_bg(outfilename):
    with open(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GeoShapes\tl_2018_53_bg.json') as file:
        data = json.load(file)
    print(len(data['objects']['tl_2018_53_bg']['geometries']))
    print(len(data))
    if outfilename:
        outfile = open(outfilename, 'w')
    else:
        outfile = None
    print('bg_geo_id','latitude','longitude','county_fips_code','tract_geo_id','tract_id','block_group_id','land_area','water_area',sep=",", file=outfile)
    for bg in data['objects']['tl_2018_53_bg']['geometries']:
        # print(tract['properties']['GEOID'][0:5])
        geo_id = bg['properties']['GEOID']
        county = int(geo_id[2:5])
        if geo_id[0:5] in ['53033','53053','53067']:
            print(geo_id,bg['properties']['INTPTLAT'][1:],bg['properties']['INTPTLON'],county,
                  bg['properties']['GEOID'][0:11], bg['properties']['GEOID'][5:11],bg['properties']['GEOID'][11:],
                  bg['properties']['ALAND'], bg['properties']['AWATER'], sep=",", file=outfile)
    if outfile:
        outfile.close()


# read_bg(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GeoShapes\bgLongLat.csv')
# read_bg(None)

# read_tract(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GeoShapes\tractLongLat.csv')
# read_tract(None)

test_connection()
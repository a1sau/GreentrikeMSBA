


import matplotlib.pyplot as plt
import geopandas as gpd
import cenpy as cp
import json

def plot_shape():
    print("start")
    map1 = gpd.read_file("C:/Users/Lugal/OneDrive/Documents/MSBA/Project/Geoshapes/gz_2010_53_150_00_500k.shp", crs='EPSG:4326')
    print(map1.head())
    print(map1.geometry)
    print(map1.columns)
    # map1 = map1[map1['COUNTY'] == '053']
    #map1[map1['COUNTY'] == '075'].plot()
    print("plot2")
    fig,ax = plt.subplots(figsize = (15,15))
    # map1.plot(ax=ax, column='TRACT')
    # fig.show()
    map1[map1['COUNTY'] == '053'].plot(ax=ax, column='TRACT')
    fig.show()
    return None


def basic_pull():
    print('product')
    cp.set_sitekey("6050a96e1b4bd539c1813f17d6607d70760fd718",True)
    product=cp.ACS().from_county('Pierce, WA', level='block group', variables=('B01001_003','B01001_027','^B19001_'),return_geometry=False)
    # product=cp.ACS().from_county('Pierce, WA', level='tract', return_geometry=False)
    # variables.to_csv("C:/Users/Lugal/OneDrive/Documents/MSBA/Project/pierceCensusVariables.csv")
    print('tacoma')
    # tacoma = product.from_county('Pierce, WA', level='tract', variables=('B01001_003E','B01001_027E'))
    tacoma = product
    tacoma.to_csv("C:/Users/Lugal/OneDrive/Documents/MSBA/Project/pierceCensus3.csv")
    for tract in tacoma:
        print(tract)
        print(tacoma[tract])
    # print(tacoma.head())
    # fig,ax = plt.subplots(figsize = (15,15))
    # tacoma.plot(ax=ax, column='B01001_003E',legend=True)
    # fig.show()
    # tacoma.plot(ax=ax, column='B01001_027E')
    # fig.show()
    # # print(tacoma[0:5][1:3])
    # # print(product.from_place("Tacoma, WA",'B001001'))
    # # print(cp.ACS.variables())
    return None


def pull_census_data(cen_vars: str, outfile: str, county: str = 'Pierce, WA', level: str = 'blockgroup'):
    cp.set_sitekey("6050a96e1b4bd539c1813f17d6607d70760fd718",True)
    product = cp.ACS().from_county(county, level=level, variables=cen_vars, return_geometry=False)
    product.to_csv(outfile)
    return None


print("start")

# basic_pull()
#plot_shape()
# pull_census_data(["B01003_001E","B01002_001E","B01001_026E","B01001_028E","B01001_004E","B01001_002E","B01001_001E"],"C:/Users/Lugal/OneDrive/Documents/MSBA/Project/pierceCensus4King.csv")
pull_census_data(["B19001_012E","B19001_007E","B19001_006E","B01001_027E","B01001_003E","B19001_011E","B19001_016E",
                  "B19001_010E","B19001_015E","B19001_017E","B19001_008E","B19001_009E","B19001_002E","B19001_001E","B19001_004E","B19001_013E","B19001_014E","B19001_005E","B19001_003E"],
                 "C:/Users/Lugal/OneDrive/Documents/MSBA/Project/pierceCensus10.csv")

# Call to pull male and female kids ages 0-5
# https://api.census.gov/data/2018/acs/acs5?get=NAME,B01001_003E,B01001_027E&for=block%20group:*&in=state:53%20county:053&key=6050a96e1b4bd539c1813f17d6607d70760fd718



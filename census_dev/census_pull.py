


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
    product=cp.ACS().from_county('Pierce, WA', level='tract', variables=('B01001_003','B01001_027','^B19001_'),return_geometry=False)
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



print("start")
cp.set_sitekey("6050a96e1b4bd539c1813f17d6607d70760fd718",True)
basic_pull()
#plot_shape()

# Call to pull male and female kids ages 0-5
# https://api.census.gov/data/2018/acs/acs5?get=NAME,B01001_003E,B01001_027E&for=block%20group:*&in=state:53%20county:053&key=6050a96e1b4bd539c1813f17d6607d70760fd718


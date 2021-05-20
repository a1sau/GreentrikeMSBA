


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

#Before being able to pull blockgroup info, you may need to run this command:
#pip install git+https://github.com/jbousquin/cenpy.git
def pull_census_data(cen_vars: str, outfile: str, county: str = 'Pierce, WA', level: str = 'blockgroup', year=2018):
    cp.set_sitekey("6050a96e1b4bd539c1813f17d6607d70760fd718",True)
    cp.ACS(year=2018)
    product = cp.ACS(year=year).from_county(county, level=level, variables=cen_vars, return_geometry=False)
    product.to_csv(outfile)
    return None




# basic_pull()
#plot_shape()
# pull_census_data(["B01003_001E","B01002_001E","B01001_026E","B01001_028E","B01001_004E","B01001_002E","B01001_001E"],"C:/Users/Lugal/OneDrive/Documents/MSBA/Project/pierceCensus4King.csv")
counties=["Pierce","King","Thurston"]
for county in counties:
    print("start",county)
    pull_census_data(["B14001_001E","B14001_002E","B14001_003E","B14001_004E","B14001_005E","B14001_006E","B14001_007E",
                      "B14001_008E","B14001_009E","B14001_010E","B10002_001E",
                      "B10002_002E","B10002_003E","B10002_004E","B10002_005E","B01001A_003E","B01001A_004E",
                      "B01001A_005E","B01001A_018E","B01001A_019E","B01001A_020E","B01001B_003E","B01001B_004E",
                      "B01001B_005E","B01001B_018E","B01001B_019E","B01001B_020E","B01001C_003E","B01001C_004E",
                      "B01001C_005E","B01001C_018E","B01001C_019E","B01001C_020E","B01001D_003E","B01001D_004E",
                      "B01001D_005E","B01001D_018E","B01001D_019E","B01001D_020E","B01001A_001E","B01001B_001E",
                      "B01001C_001E","B01001D_001E","B01001E_001E","B01001F_001E","B01001G_001E","B01001H_001E",
                      "B01001I_001E","B05012_001E","B05012_002E","B05012_003E","B08006_001E","B08006_002E",
                      "B08006_003E","B08006_004E","B08006_008E","B08006_014E","B08006_015E","B08006_016E","B08006_017E",
                      "B01001E_003E","B01001E_004E","B01001E_005E","B01001E_018E","B01001E_019E","B01001E_020E",
                      "B01001F_003E","B01001F_004E","B01001F_005E","B01001F_018E","B01001F_019E","B01001F_020E",
                      "B01001G_003E","B01001G_004E","B01001G_005E","B01001G_018E","B01001G_019E","B01001G_020E",
                      "B01001H_003E","B01001H_004E","B01001H_005E","B01001H_018E","B01001H_019E","B01001H_020E",
                      "B01001I_003E","B01001I_004E","B01001I_005E","B01001I_018E","B01001I_019E","B01001I_020E"],
                 r"C:\Users\Lugal\OneDrive\Documents\MSBA\Project\{}Census_tract_2018_May2021C.csv".format(county),county="{}, WA".format(county),level='tract')

# Call to pull male and female kids ages 0-5
# https://api.census.gov/data/2018/acs/acs5?get=NAME,B01001_003E,B01001_027E&for=block%20group:*&in=state:53%20county:053&key=6050a96e1b4bd539c1813f17d6607d70760fd718



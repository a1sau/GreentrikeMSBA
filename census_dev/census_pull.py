


import matplotlib.pyplot as plt
import geopandas as gpd


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
map1[map1['COUNTY'] == '053'].plot(ax=ax, column='BLKGRP')
fig.show()

import mercantile
import PIL
import requests
import shutil

lat_lng = [47.6198948, -122.3239006]

delta=0.01
tl = [lat_lng[0]+delta, lat_lng[1]-delta]
br = [lat_lng[0]-delta, lat_lng[1]+delta]
z = 13 # Set the resolution (max at 15)

tl_tiles = mercantile.tile(tl[1],tl[0],z)
br_tiles = mercantile.tile(br[1],br[0],z)
x_tile_range =[tl_tiles.x,br_tiles.x];print(x_tile_range)
y_tile_range = [tl_tiles.y,br_tiles.y];print(y_tile_range)


for i,x in enumerate(range(x_tile_range[0],x_tile_range[1]+1)):
    for j,y in enumerate(range(y_tile_range[0],y_tile_range[1]+1)):
        r =requests.get('https://api.mapbox.com/v4/mapbox.mapbox-traffic-v1/'+
                        str(z)+'/'+str(x)+'/'+str(y)+'@2x.pngraw?access_token=pk.eyJ1Ijoia29ib2wiLCJhIjoiY2ttNW16b3lvMGZ6aDJ2bzR1Z3hyOHpseSJ9.TUYsIgf1hE32YaN_XbaTDw', stream=True)

        with open(r'C:/output/satellite_images/' + str(i) + '.' + str(j) + '.png','wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
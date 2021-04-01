import pandas as pd
import numpy as np

df = pd.read_excel(r'D:\Templates\UW Stuff\Classes\MSBA\Classes\PM Stuff for me\Environments\Building_Data_Score1.xlsx')

df = df[['City', 'PostalCode', 'GeoCode', 'PropertyType', 'Price', 'YearBuilt', 'SaleType','Total_Score_Norm']]
df

#Converting NaN of GeoCode to 0
def convert_int(x):
    try:
        return int(x)
    except:
        return 0


#Applying convert_int to the GeoCode
df['GeoCode'] = df['GeoCode'].apply(convert_int)
df['GeoCode']


def build_chart(df, percentile=0.8):
    #Ask for preferred City
    print("Input preferred City")
    City = input()

    #Ask for preferred PostalCode
    print("Input preferred PostalCode")
    PostalCode = input()

    #Ask for preferred PropertyType
    print("Input preferred PropertyType")
    PropertyType = input()

    #Ask for lower limit of price
    print("Input lowest Price")
    low_price = int(input())

    #Ask for upper limit of Price
    print('Input highest Price')
    high_Price = int(input())

    #Ask for lower limit of YearBuilt
    print("Input lowest YearBuilt")
    low_YearBuilt = int(input())

    #Ask for upper limit of YearBuilt
    print("Input highest YearBuilt")
    high_YearBuilt = int(input())

    #Ask for preferred SaleType
    print("Input preferred SaleType")
    SaleType = input()

    #Define a new buildings variable to store the preferred buildings. Copy the contents of df to movies
    bg_geo_id = df.copy()
    bg_geo_id.head()

    #Filter based on the condition
    bg_geo_id = bg_geo_id[(bg_geo_id['City'] == City) &
                    (bg_geo_id['PostalCode'] == PostalCode) &
                    (bg_geo_id['PropertyType'] == PropertyType) &
                    (bg_geo_id['Price'] >= low_price) &
                    (bg_geo_id['Price'] <= high_Price) &
                    (bg_geo_id['YearBuilt'] >= low_YearBuilt) &
                    (bg_geo_id['YearBuilt'] >= high_YearBuilt) &
                    (bg_geo_id['SaleType'] == SaleType)]

    #Compute the values of C and m for the filtered movies
    #C = movies['vote_average'].mean()
   # m = bg_geo_id['Total_Score_Norm'].quantile(percentile)

    #Only consider movies that have higher than m votes. Save this in a new dataframe q_movies
    #rec_Buildings = bg_geo_id.copy().loc[bg_geo_id['Total_Score_Norm'] >= m]

    #Calculate score using the IMDB formula
    #q_movies['score'] = q_movies.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average'])
                                                # + (m/(m+x['vote_count']) * C)
                                                # ,axis=1)

    #Sort movies in descending order of their scores
    bg_geo_id = bg_geo_id.sort_values('Total_Score_Norm', ascending=False)
    return bg_geo_id

build_chart(df).head()
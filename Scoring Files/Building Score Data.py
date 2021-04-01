import pandas as pd
from sklearn import preprocessing

Building_Data = pd.read_excel(r'D:\Templates\UW Stuff\Classes\MSBA\Classes\PM Stuff for me\Environments\Scoring Data.xlsx', sheet_name = 'Building')
Building_Data

#First Criteria (function method)
def checkCity(n):
    if n == 'Tacoma':
        return 1
    elif n == 'Puyallup':
        return 0.5
    else:
        return 0

def checkPostalCode(n):
    if n == 98499:
        return 1
    elif n == 98373:
        return 0.5
    else:
        return 0

def checkPropertyType(n):
    if n == 'Office':
        return 1
    elif n == 'Retail':
        return 0.5
    else:
        return 0

def checkPrice(n):
    if (1500000 < n > 3000000):
        return 0.5
    elif (500000 < n > 1499999):
        return 1
    else:
        return 0

def checkYearBuilt(n):
    if (2000 < n > 2020):
        return 1
    elif (1980 < n > 1999):
        return 0.5
    else:
        return 0

def checkSaleType(n):
    if n == 'Investment':
        return 1
    elif n == 'Owner User':
        return 0.5
    else:
        return 0


#apply scores to dataset (function method)
Building_Data['City_Score'] = Building_Data['City'].apply(checkCity)
Building_Data['Postal_Score'] = Building_Data['PostalCode'].apply(checkPostalCode)
Building_Data['Property_Score'] = Building_Data['PropertyType'].apply(checkPropertyType)
Building_Data['Price_Score'] = Building_Data['Price'].apply(checkPrice)
Building_Data['Year_Built_Score'] = Building_Data['YearBuilt'].apply(checkYearBuilt)
Building_Data['Sale_Score'] = Building_Data['SaleType'].apply(checkSaleType)
Building_Data
#add total scores to dataset (function method)
Building_Data['Total_Score'] = Building_Data['City_Score'] + Building_Data['Postal_Score'] \
                               + Building_Data['Property_Score'] + Building_Data['Price_Score'] \
                               + Building_Data['Year_Built_Score'] + Building_Data['Sale_Score']
Building_Data
#normalize total scores (function method)
xx = Building_Data[['Total_Score']].values.astype(float)
min_max_scaler = preprocessing.MinMaxScaler()
xx_scaled = min_max_scaler.fit_transform(xx)
Total_Score_Norm = pd.DataFrame(xx_scaled)

#append normalized score to (function method)
Building_Data['Total_Score_Norm'] = Total_Score_Norm

#to see if it worked, export to xlsx (function method)
Building_Datatoexcel = pd.ExcelWriter('Building_Data_Score1.xlsx')
Building_Data.to_excel(Building_Datatoexcel)
Building_Datatoexcel.save()




#This is my first Criteria under original method
Building_Data['score'] = ((Building_Data['City'] == 'Tacoma').astype(int)
                          + (Building_Data['PostalCode'] == 98499).astype(int)
                          + (Building_Data['PropertyType'] == 'Office').astype(int)
                          + (Building_Data['Price'] > 500000).astype(int)
                          + (Building_Data['YearBuilt'] > 1985).astype(int)
                          + (Building_Data['SaleType'] == 'Investment').astype(int))

#This is the first score (original method)
Building_Data['score']
Building_Data
#To normalize first score (original method)
x = Building_Data[['score']].values.astype(float)
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
Score_Norm = pd.DataFrame(x_scaled)

#first score normalized (original method)
Score_Norm

#appending normalized score to dataset (original method)
Building_Data['score_norm'] = Score_Norm
Building_Data



#Second Criteria (original method)
Building_Data['score1'] = ((Building_Data['City'] == 'Tacoma').astype(int)
                          + (Building_Data['City'] == 'Puyallup').astype(int)
                          + (Building_Data['PostalCode'] == 98499).astype(int)
                          + (Building_Data['PostalCode'] == 98373).astype(int)
                          + (Building_Data['PropertyType'] == 'Office').astype(int)
                          + (Building_Data['PropertyType'] == 'Retail').astype(int)
                          + (Building_Data['Price'] > 500000).astype(int)
                          + (Building_Data['Price'] < 1500000).astype(int)
                          + (Building_Data['YearBuilt'] > 1985).astype(int)
                          + (Building_Data['YearBuilt'] < 2010).astype(int)
                          + (Building_Data['SaleType'] == 'Investment').astype(int)
                          + (Building_Data['SaleType'] == 'Owner User').astype(int))

#This is the second score (original method)
Building_Data['score1']
Building_Data
#To normalize second score (original method)
x = Building_Data[['score1']].values.astype(float)
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
Score_Norm1 = pd.DataFrame(x_scaled)

#second score normalized (original method)
Score_Norm1

#appending normalized score1 to dataset (original method)
Building_Data['score_norm1'] = Score_Norm1
Building_Data



#to see if it worked, export to xlsx (original method)
Building_Datatoexcel = pd.ExcelWriter('Building_Data_Score.xlsx')
Building_Data.to_excel(Building_Datatoexcel)
Building_Datatoexcel.save()
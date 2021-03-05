import pandas as pd
from sklearn import preprocessing

Census_Data = pd.read_excel(r'D:\Templates\UW Stuff\Classes\MSBA\Classes\PM Stuff for me\Environments\Scoring Data.xlsx', sheet_name = 'Census')
Census_Data

#assigning variable_id and values to a dataframe
SCensus_Data = pd.DataFrame(Census_Data['bg_geo_id'])
SCensus_Data['variable_id'] = (Census_Data['variable_id'])
SCensus_Data['value'] = (Census_Data['value'])
SCensus_Data

#reverse melt (pivot) so that variable_id are columns and values are observations
SCensus_Data = SCensus_Data.pivot(index = 'bg_geo_id', columns = 'variable_id')
SCensus_Data = SCensus_Data['value'].reset_index()
SCensus_Data.columns.name = None
SCensus_Data

#this will also rename the variable_id's into their full variable names
SCensus_Data.rename(columns = {'B01001_001E':'Sex by Age Total', 'B01001_002E':'Sex by Age Males Total',
                               'B01001_003E':'Sex by Age Males Under 5 Years Old',
                               'B01001_004E':'Sex by Age Males 5 to 9 Years Old',
                               'B01001_026E':'Sex by Age Female Total',
                               'B01001_027E':'Sex by Age Females Under 5 Years Old',
                               'B01001_028E':'Sex by Age Females 5 to 9 Years Old',
                               'B01002_001E':'Median Age by Sex',
                               'B01003_001E':'Total Population',
                               'B19001_001E':'Income in Last 12 Total',
                               'B19001_002E':'Income in Last 12 < $10,000',
                               'B19001_003E':'Income in last 12 $10,000 to $14,999',
                               'B19001_004E':'Income in last 12 $15,000 to $19,999',
                               'B19001_005E': 'Income in last 12 $20,000 to $24,999',
                               'B19001_006E': 'Income in last 12 $25,000 to $29,999',
                               'B19001_007E': 'Income in last 12 $30,000 to $34,999',
                               'B19001_008E': 'Income in last 12 $35,000 to $39,999',
                               'B19001_009E': 'Income in last 12 $40,000 to $44,999',
                               'B19001_010E': 'Income in last 12 $45,000 to $49,999',
                               'B19001_011E': 'Income in last 12 $50,000 to $59,999',
                               'B19001_012E': 'Income in last 12 $60,000 to $74,999',
                               'B19001_013E': 'Income in last 12 $75,000 to $99,999',
                               'B19001_014E': 'Income in last 12 $100,000 to $124,999',
                               'B19001_015E': 'Income in last 12 $125,000 to $149,999',
                               'B19001_016E': 'Income in last 12 $150,000 to $199,999',
                               'B19001_017E': 'Income in last 12 $200,000 or more'}, inplace = True)
SCensus_Data

#to see if new datafram SCensus_Data worked, export to xlsx
SCensus_Datatoexcel = pd.ExcelWriter('SCensus_Data_Score.xlsx')
SCensus_Data.to_excel(SCensus_Datatoexcel)
SCensus_Datatoexcel.save()

#function scoring of SCensus_Data
def checkSexAgeTotal(n):
    if (3964 <= n <=5946):
        return 1
    elif (1983 <= n <= 3963):
        return 0.5
    else:
        return 0

def checkSexAgeTotalMale(n):
    if (2263 <= n <=3395):
        return 1
    elif (1132 <= n <= 2262):
        return 0.5
    else:
        return 0

def checkSexAgeMUnder5(n):
    if (231 <= n <= 345):
        return 1
    elif (115 <= n <= 230):
        return 0.5
    else:
        return 0

def checkSexAgeM5to9(n):
    if (213 <= n <= 318):
        return 1
    elif (135 <= n <= 212):
        return 0.5
    else:
        return 0

def checkSexAgeFemaleTotal(n):
    if (2013 <= n <= 3019):
        return 1
    elif (1007 <= n <= 2012):
        return 0.5
    else:
        return 0

def checkSexAgeFUnder5(n):
    if (269 <= n <= 403):
        return 1
    elif (135 <= n <= 268):
        return 0.5
    else:
        return 0

def checkSexAgeF5to9(n):
    if (217 <= n <= 326):
        return 1
    elif (109 <= n <= 216):
        return 0.5
    else:
        return 0

def checkMedianSexAge(n):
    if (50 <= n <= 78):
        return 1
    elif (27 <= n <= 49):
        return 0.5
    else:
        return 0

def checkIncomeL12Total(n):
    if (1367 <= n <= 2051):
        return 1
    elif (684 <= n <= 1366):
        return 0.5
    else:
        return 0

def checkIncomeL12_40to44(n):
    if (154 <= n <= 172):
        return 1
    elif (58 <= n <= 144):
        return 0.5
    else:
        return 0

def checkIncomeL12_45to49(n):
    if (83 <= n <= 125):
        return 1
    elif (42 <= n <= 82):
        return 0.5
    else:
        return 0

def checkIncomeL12_50to59(n):
    if (163 <= n <= 245):
        return 1
    elif (82 <= n <= 162):
        return 0.5
    else:
        return 0

def checkIncomeL12_60to74(n):
    if (265 <= n <= 398):
        return 1
    elif (133 <= n <= 264):
        return 0.5
    else:
        return 0

def checkIncomeL12_75to99(n):
    if (325 <= n <= 486):
        return 1
    elif (163 <= n <= 324):
        return 0.5
    else:
        return 0

def checkIncomeL12_100to124(n):
    if (295 <= n <= 441):
        return 1
    elif (148 <= n <= 294):
        return 0.5
    else:
        return 0

def checkIncomeL12_125to149(n):
    if (125 <= n <= 186):
        return 1
    elif (63 <= n <= 124):
        return 0.5
    else:
        return 0

def checkIncomeL12_150to199(n):
    if (177 <= n <= 265):
        return 1
    elif (89 <= n <= 176):
        return 0.5
    else:
        return 0

def checkIncomeL12_200orMore(n):
    if (237 <= n <= 490):
        return 1
    elif (164 <= n <= 326):
        return 0.5
    else:
        return 0



#apply scores to dataset (function method)
SCensus_Data['SexbyAge_Total'] = SCensus_Data['Sex by Age Total'].apply(checkSexAgeTotal)
SCensus_Data['SexbyAgeMale_Total'] = SCensus_Data['Sex by Age Males Total'].apply(checkSexAgeTotalMale)
SCensus_Data['SexbyAgeMale_5orUnder'] = SCensus_Data['Sex by Age Males Under 5 Years Old'].apply(checkSexAgeMUnder5)
SCensus_Data['SexbyAgeMale_5to9'] = SCensus_Data['Sex by Age Males 5 to 9 Years Old'].apply(checkSexAgeM5to9)
SCensus_Data['SexbyAgeFemale_Total'] = SCensus_Data['Sex by Age Female Total'].apply(checkSexAgeFemaleTotal)
SCensus_Data['SexbyAgeFemale_5Under'] = SCensus_Data['Sex by Age Females Under 5 Years Old'].apply(checkSexAgeFUnder5)
SCensus_Data['SexbyAgeFemale_5to9'] = SCensus_Data['Sex by Age Females 5 to 9 Years Old'].apply(checkSexAgeF5to9)
SCensus_Data['SexbyAgeMedian_Total'] = SCensus_Data['Median Age by Sex'].apply(checkMedianSexAge)
SCensus_Data['IncomeL12_Total'] = SCensus_Data['Income in Last 12 Total'].apply(checkIncomeL12Total)
SCensus_Data['IncomeL12_40to44'] = SCensus_Data['Income in last 12 $40,000 to $44,999'].apply(checkIncomeL12_40to44)
SCensus_Data['IncomeL12_45to49'] = SCensus_Data['Income in last 12 $45,000 to $49,999'].apply(checkIncomeL12_45to49)
SCensus_Data['IncomeL12_50to59'] = SCensus_Data['Income in last 12 $50,000 to $59,999'].apply(checkIncomeL12_50to59)
SCensus_Data['IncomeL12_60to74'] = SCensus_Data['Income in last 12 $60,000 to $74,999'].apply(checkIncomeL12_60to74)
SCensus_Data['IncomeL12_74to99'] = SCensus_Data['Income in last 12 $75,000 to $99,999'].apply(checkIncomeL12_75to99)
SCensus_Data['IncomeL12_100to124'] = SCensus_Data['Income in last 12 $100,000 to $124,999'].apply(checkIncomeL12_125to149)
SCensus_Data['IncomeL12_125to149'] = SCensus_Data['Income in last 12 $125,000 to $149,999'].apply(checkIncomeL12_125to149)
SCensus_Data['IncomeL12_150to199'] = SCensus_Data['Income in last 12 $150,000 to $199,999'].apply(checkIncomeL12_150to199)
SCensus_Data['IncomeL12_200orMore'] = SCensus_Data['Income in last 12 $200,000 or more'].apply(checkIncomeL12_200orMore)


#to see if new datafram SCensus_Data worked, export to xlsx
SCensus_Datatoexcel = pd.ExcelWriter('SCensus_Data_Score.xlsx')
SCensus_Data.to_excel(SCensus_Datatoexcel)
SCensus_Datatoexcel.save()

#add total scores to dataset (function method)
SCensus_Data['Total_Score'] = SCensus_Data['SexbyAge_Total'] + SCensus_Data['SexbyAgeMale_Total'] \
                               + SCensus_Data['SexbyAgeMale_5orUnder'] + SCensus_Data['SexbyAgeMale_5to9'] \
                               + SCensus_Data['SexbyAgeFemale_Total'] + SCensus_Data['SexbyAgeFemale_5Under'] \
                              + SCensus_Data['SexbyAgeFemale_5to9'] + SCensus_Data['SexbyAgeMedian_Total'] \
                              + SCensus_Data['IncomeL12_Total'] + SCensus_Data['IncomeL12_40to44'] \
                              + SCensus_Data['IncomeL12_45to49'] + SCensus_Data['IncomeL12_50to59'] \
                              + SCensus_Data['IncomeL12_60to74'] + SCensus_Data['IncomeL12_74to99'] \
                              + SCensus_Data['IncomeL12_100to124'] + SCensus_Data['IncomeL12_125to149'] \
                              + SCensus_Data['IncomeL12_150to199'] + SCensus_Data['IncomeL12_200orMore']

SCensus_Data

#normalize total scores (function method)
xxx = SCensus_Data[['Total_Score']].values.astype(float)
min_max_scaler = preprocessing.MinMaxScaler()
xxx_scaled = min_max_scaler.fit_transform(xxx)
Total_Score_Norm = pd.DataFrame(xxx_scaled)

#append normalized score to (function method)
SCensus_Data['Total_Score_Norm'] = Total_Score_Norm

#to see if new datafram SCensus_Data worked, export to xlsx
SCensus_Datatoexcel = pd.ExcelWriter('SCensus_Data_Score.xlsx')
SCensus_Data.to_excel(SCensus_Datatoexcel)
SCensus_Datatoexcel.save()




















#This is my first Criteria
Census_Data['score'] = ((Census_Data['variable_id'] == 'B19001_012E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_007E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_006E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_011E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_010E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_008E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_009E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_002E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_004E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_005E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_003E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_003E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_004E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_027E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_028E').astype(int)
                        + (Census_Data['zip_code'] == 98499).astype(int)
                        + (Census_Data['zip_code'] == 98373).astype(int))

#This is the first score
Census_Data['score']
Census_Data
#To normalize first score
x = Census_Data[['score']].values.astype(float)
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
Score_Norm = pd.DataFrame(x_scaled)

#first score normalized
Score_Norm

#appending normalized score to dataset
Census_Data['score_norm'] = Score_Norm
Census_Data




#This is my second Criteria
Census_Data['score1'] = ((Census_Data['variable_id'] == 'B19001_015E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_013E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_014E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_003E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_004E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_027E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_028E').astype(int)
                        + (Census_Data['zip_code'] == 98499).astype(int)
                        + (Census_Data['zip_code'] == 98373).astype(int))

#This is the second score
Census_Data['score1']
Census_Data
#To normalize first score
x1 = Census_Data[['score1']].values.astype(float)
min_max_scaler = preprocessing.MinMaxScaler()
x1_scaled = min_max_scaler.fit_transform(x1)
Score_Norm1 = pd.DataFrame(x1_scaled)

#first score normalized
Score_Norm1

#appending normalized score to dataset
Census_Data['score_norm1'] = Score_Norm1
Census_Data



#This is my third Criteria
Census_Data['score2'] = ((Census_Data['variable_id'] == 'B19001_016E').astype(int)
                        + (Census_Data['variable_id'] == 'B19001_017E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_003E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_004E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_027E').astype(int)
                        + (Census_Data['variable_id'] == 'B01001_028E').astype(int)
                        + (Census_Data['zip_code'] == 98499).astype(int)
                        + (Census_Data['zip_code'] == 98373).astype(int))

#This is the second score
Census_Data['score2']
Census_Data
#To normalize first score
x2 = Census_Data[['score2']].values.astype(float)
min_max_scaler = preprocessing.MinMaxScaler()
x2_scaled = min_max_scaler.fit_transform(x2)
Score_Norm2 = pd.DataFrame(x2_scaled)

#first score normalized
Score_Norm2

#appending normalized score to dataset
Census_Data['score_norm2'] = Score_Norm2
Census_Data


#to see if it worked, export to xlsx
Census_Datatoexcel = pd.ExcelWriter('Census_Data_Score.xlsx')
Census_Data.to_excel(Census_Datatoexcel)
Census_Datatoexcel.save()
import pandas as pd
import re

column_list = []
var_list = []
outcsv = {}
df = pd.read_csv(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\pierceCensus2.csv')
print(df.columns)
re_col = re.compile('^B\d.+_\d+[a-zA-Z]?')
for column in df.columns:
    if re_col.match(column):
        var_list.append(column)
        # print(var_list)
    else:
        print("FAIL:", column)
# print("VAR:",var_list)
column_list = var_list.copy()
column_list.append("GEOID")
new_df = df[column_list]
print(new_df)
for var in var_list:
    # print("!!",var)
    for i, row in new_df.iterrows():
        print(row['GEOID'],var,row[var],sep='|')


##Output = GEOID,variable_ID,value
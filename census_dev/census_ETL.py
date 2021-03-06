import pandas as pd
import re
import math
import sys

def build_import_csv(infile: str, outfile_str: str):
    column_list = []
    var_list = []
    outcsv = {}
    outfile = open(outfile_str, 'w')
    df = pd.read_csv(infile)
    # print(df.columns)
    re_col = re.compile('^B\d.+_\d+[a-zA-Z]?')
    for column in df.columns:
        if re_col.match(column):
            var_list.append(column)
            print("SUCCESS:",column)
        else:
            print("FAIL:", column)
    # print("VAR:",var_list)
    column_list = var_list.copy()
    column_list.append("GEOID")
    new_df = df[column_list]
    # print(new_df)
    print("bg_geo_id","variable_id","value", sep='|',file=outfile)
    for var in var_list:
        # print("!!",var)
        for i, row in new_df.iterrows():
            if math.isnan(row[var]):   # handle blank values
                value = ""
            elif int(row[var]) == row[var]:
                value = int(row[var])
            else:
                value = row[var]
            #print(int(row['GEOID']), var, value, sep='|')
            print(int(row['GEOID']), var, value, sep='|', file=outfile)
    outfile.close()
    print('Import file created at',outfile_str)
    return None


# build_import_csv(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\pierceCensus4.csv',r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\pierceCensus4OUT.csv')
build_import_csv(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\pierceCensus10.csv',
                 r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\pierceCensus_nonull_1_15_20_OUT.csv')
##Output = GEOID,variable_ID,value
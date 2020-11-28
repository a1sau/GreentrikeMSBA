import pandas as pd
import re
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
            # print(var_list)
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
            if int(row[var]) == row[var]:
                value = int(row[var])
            else:
                value = row[var]
            print(int(row['GEOID']), var, value, sep='|', file=outfile)
    outfile.close()
    print('Import file created at',outfile_str)
    return None


build_import_csv(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\pierceCensus4.csv',r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\pierceCensus4OUT.csv')
##Output = GEOID,variable_ID,value
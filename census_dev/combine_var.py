from timeit import default_timer as timer
import pandas as pd
import psycopg2
import reverse_geocoder2 as rg2
from math import cos, acos, sin, radians
from multiprocessing import Process, Queue, current_process
import os
import sys
from math import isnan

#method 0=Sum, 1=Average, 2=linear decrease
def calc_bg(variable='B01003_001E',method=0,distance=1,conn=None):
    if not conn:
        conn=getConn()
    if distance<=0:
        return None
    new_full_variable=calcVarName(variable, method, distance)
    if method==0:   #Sum
        sql_command="select bg1.bg_geo_id \"bg_geo_id\",\'{0}\' \"variable_id\" " \
                    ",coalesce(sum(bg2.value)+bg1.value,bg1.value) \"value\" " \
                    "from \"BG_Data\" as bg1 " \
                    "left join \"BG_Distance\" as dist on bg1.bg_geo_id = dist.bg_geo_id1 and dist.distance<={2}" \
                    "left join \"BG_Data\" as bg2 on bg2.bg_geo_id = dist.bg_geo_id2 " \
                    "where bg1.variable_id='{1}' and (dist.distance is null or " \
                    "(bg2.variable_id='{1}' and dist.distance <= {2})) " \
                    "group by bg1.bg_geo_id, bg1.variable_id, bg1.value " \
                    "order by count(bg2.value) asc;".format(new_full_variable,variable,str(distance))
    if method==1:   #Average
        sql_command="select bg1.bg_geo_id \"bg_geo_id\",\'{0}\' \"variable_id\" " \
                    ",coalesce(round((sum(bg2.value)+bg1.value)/(count(bg2.value)+1)),bg1.value) \"value\" " \
                    "from \"BG_Data\" as bg1 " \
                    "left join \"BG_Distance\" as dist on bg1.bg_geo_id = dist.bg_geo_id1 and dist.distance<={2} " \
                    "left join \"BG_Data\" as bg2 on bg2.bg_geo_id = dist.bg_geo_id2 " \
                    "where bg1.variable_id='{1}' and (dist.distance is null or " \
                    "(bg2.variable_id='{1}' and dist.distance <= {2})) " \
                    "group by bg1.bg_geo_id, bg1.variable_id, bg1.value " \
                    "order by count(bg2.value) asc;".format(new_full_variable,variable,str(distance))
    if method==2:   #Linear decrease
        sql_command="select bg1.bg_geo_id \"bg_geo_id\",\'{0}\' \"variable_id\"" \
                    ",coalesce(round(sum(bg2.value*(({2}-dist.distance)/distance))+bg1.value),bg1.value) \"value\" " \
                    "from \"BG_Data\" as bg1 " \
                    "left join \"BG_Distance\" as dist on bg1.bg_geo_id = dist.bg_geo_id1 and dist.distance<={2} " \
                    "left join \"BG_Data\" as bg2 on bg2.bg_geo_id = dist.bg_geo_id2 " \
                    "where bg1.variable_id='{1}' and (dist.distance is null or " \
                    "(bg2.variable_id='{1}' and dist.distance <= {2})) " \
                    "group by bg1.bg_geo_id, bg1.variable_id, bg1.value " \
                    "order by count(bg2.value) asc;".format(new_full_variable,variable,str(distance))
    print(sql_command)
    cur = conn.cursor()
    cur.execute(sql_command)
    df_data = cur.fetchall()
    return df_data

#Return new full variable name for combo variable
def calcVarName(variable,method,distance=1):
    if not variable:
        return None
    if method==0:   #sum
        return variable+"_"+str(distance)+"MS"
    elif method==1:   #average
        return variable+"_"+str(distance)+"MA"
    elif method==2:   #linear decrease
        return variable+"_"+str(distance)+"ML"
    else:
        return None


def getConn():
    config = rg2.read_config()
    database_config = config['Database']
    try:
        conn = psycopg2.connect(
            host=database_config['host_ip'],
            port=database_config['port'],
            database=database_config['database'],
            user=database_config['user'],
            password=database_config['password'])
    except Exception as e:
        print('Database could not be connected to:')
        print(e)
        return None

    return conn


def pull_data(var_list=None,outfileVar=None,outfileData=None,distance=1,method=0):
    count=0
    conn=getConn()
    if conn is None:
        print("No Connection")
        return None
    try:
            outputfile = open(file=outfileData,mode="w")
    except:
        print("Could not open output file:",outfileData)
    cur = conn.cursor()
    print("bg_geo_id,variable_id,value",file=outputfile) #create csv header
    for var in var_list:
        print("Running query for ",var)
        df = calc_bg(variable=var,method=method,distance=distance,conn=conn)  #run query to get combo results
        for line in df: #output results into file for import
            count+=1
            print(line[0],line[1],line[2],sep=",",file=outputfile)
    return count


#Build an new variable import file for Demo_var table
def build_new_var(var_list=None,method=0,distance=1,outfileVar=None,conn=None):
    if var_list==None:
        print("No variables provided")
        return None
    if not conn:
        conn=getConn()
    if conn is None:
        print("No Connection")
        return None
    try:
        if outfileVar:
            outputfile = open(file=outfileVar,mode="w")
        else:
            outputfile=None
    except:
        print("Could not open output file:",outfileVar)
        return None
    cur = conn.cursor()
    #Get list of all existing variables:
    sql_command="select source_id,full_name,type,url,census_table,base_variable_id,base_variable_name,full_variable_id,minimum,maximum,data_year," \
                "census_variable from \"Demo_Var\" where full_variable_id in ("
    for var in var_list:
        sql_command+="\'{}\',".format(var)
    sql_command=sql_command[0:-1]+")"   #Remove extra , and close statement
    try:
        df_var=pd.read_sql_query(sql_command,conn)
    except (Exception, psycopg2.DatabaseError) as err:
        show_psycopg2_exception(err)
    print(df_var)
    df_var['type']="calc"
    df_var['full_variable_id']=df_var['full_variable_id'].apply(calcVarName,args=[method,distance])  #set new variable ID
    df_var['full_name']=df_var['full_name'].apply(calcVarName,args=[method,distance])  #set new variable ID
    print(df_var[['full_variable_id','type','census_table']])
    new_var_str = ""
    for var in df_var['full_variable_id']:
        try:
            new_var_str += "\'" + var + "\',"
        except:
            print("Error:", var)
    new_var_str=new_var_str[0:-1]
    sql_command="select full_variable_id from \"Demo_Var\" as dv where dv.full_variable_id in ({})".format(new_var_str)
    print(sql_command)
    exist_df=pd.read_sql_query(sql_command,conn)

    ##Build variable import file
    import_col="source_id,full_name,type,url,census_table,base_variable_id,base_variable_name,full_variable_id,minimum,maximum,data_year,census_variable"
    print(import_col)
    print(import_col,file=outputfile)   #create csv header

    #Loop over column values and add to import
    count=0
    for var_line in df_var.iterrows():
        vl=var_line[1]
        full_variable_id = vl['full_variable_id']
        if exist_df[exist_df['full_variable_id']==full_variable_id].empty:
            count+=1
            first = True
            for item in vl:
                if first:   #deal with no comma for first item
                    print(clean_var(item), end="", file=outputfile)
                    first = False
                else:       #all other items
                    print(","+clean_var(item), end="", file=outputfile)
            print("\n", end="", file=outputfile)
        else:
            print("duplicate",full_variable_id)
    return count


##Convert item to format that can be imported into SQL CSV file
def clean_var(item):
    if item is None:
        return ""
    if isinstance(item, float):
        if isnan(item):
            return ""
        if int(item) == item:
            return str(int(item))  #remove extra .0 from str
        else:
            return str(item)
    if isinstance(item,str):
        if item.find(",")!=-1:   #check if commas in variable
           return "\""+item+"\""
    return str(item)


def show_psycopg2_exception(err):
    # get details about the exception
    err_type, err_obj, traceback = sys.exc_info()
    # get the line number when exception occured
    line_n = traceback.tb_lineno
    # print the connect() error
    print ("\npsycopg2 ERROR:", err, "on line number:", line_n)
    print ("psycopg2 traceback:", traceback, "-- type:", err_type)
    # psycopg2 extensions.Diagnostics object attribute
    print ("\nextensions.Diagnostics:", err.diag)
    # print the pgcode and pgerror exceptions
    print ("pgerror:", err.pgerror)
    print ("pgcode:", err.pgcode, "\n")


if __name__ == "__main__":
    # pull_data(r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GreentrikeMSBA\census_dev\newVarImport.csv',
    #           r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GreentrikeMSBA\census_dev\newData.csv')
    var_list = ["B19001_012E","B19001_007E","B19001_006E","B01001_027E","B01001_003E","B19001_011E","B19001_016E",
                "B19001_010E","B19001_015E","B19001_017E","B19001_008E","B19001_009E","B19001_002E","B19001_001E","B19001_004E",
                "B19001_013E","B19001_014E","B19001_005E","B19001_003E","B01001_001E","B01001_002E","B01001_004E","B01001_028E","B01001_026E"]
    method=2
    distance=3
    var_count = build_new_var(var_list,method=method,distance=distance,outfileVar=r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GreentrikeMSBA\census_dev\newVar_{0}.csv'.format(distance))
    count = pull_data(var_list=var_list,method=method,distance=distance,outfileData=r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GreentrikeMSBA\census_dev\newData_{0}.csv'.format(distance))
    print("New Variables",var_count)
    print("Rows generated:",count)
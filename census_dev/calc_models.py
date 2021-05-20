import pandas as pd
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
import reverse_geocoder2 as rg2
from combine_var import getConn
import sys


#Run R script for KNN sale building data
def calc_knn_sale(user,password,host,database,port):
    r = robjects.r
    r['source']('for_sale_KNN_dynamic_script.R')  #object of R file
    try:
        get_main_function_r = robjects.globalenv['main_forsale_knn']  #loading R function to use
        df_result_r = get_main_function_r(user,password,host,database,port)
        df_result = pandas2ri.rpy2py(df_result_r)
    except Exception as e:
        print("KNN Sale Building model failed:",e)
        return None
    return df_result


#Run R script for KNN census block group data
def calc_knn_census(user,password,host,database,port):
    r = robjects.r
    r['source']('census_KNN_dynamic_script.R')  #object of R file
    try:
        get_main_function_r = robjects.globalenv['main_census_knn']  #loading R function to use
        df_result_r = get_main_function_r(user,password,host,database,port)
        df_result = pandas2ri.rpy2py(df_result_r)
    except Exception as e:
        print("KNN Census model failed:",e)
        return None
    return df_result


#Run R script for Neural Net sale building data
def calc_neuralnet_sale(user,password,host,database,port):
    r = robjects.r
    r['source']('nn_building_script.R')  #object of R file
    try:
        get_main_function_r = robjects.globalenv['mainfunction.all']  #loading R function to use
        df_result_r = get_main_function_r(host,user,password,database,port)
        df_result = pandas2ri.rpy2py(df_result_r)
    except Exception as e:
        print("NeuralNet Sale Building model failed:",e)
        return None
    return df_result

#Run R script for Neural Net census block group data
def calc_neuralnet_census(user,password,host,database,port):
    r = robjects.r
    r['source']('nn_census_script.R')  #object of R file
    try:
        get_main_function_r = robjects.globalenv['mainfunction.all']  #loading R function to use
        df_result_r = get_main_function_r(host,user,password,database,port)
        df_result = pandas2ri.rpy2py(df_result_r)
    except Exception as e:
        print("NeuralNet Census model failed:",e)
        return None
    return df_result


def calc_ensemble_sale(conn):
    if conn is None:
        return False
    try:
        cur=conn.cursor()
        sql_command = """
                insert into "Building_Model_Score" (cs_id, raw_score, model_id, score, date_calculated) select 
                    cs_id
                    ,avg(score)
                    ,17
                    ,round(avg(score))
                    ,now()::date
                    FROM "Building_Model_Score" as bms
                    where bms.model_id in (13,15)
                    GROUP BY cs_id
                on conflict on constraint building_model_pk do update
                set score = excluded.score,
                raw_score = excluded.raw_score,
                date_calculated = excluded.date_calculated;
        """
        cur.execute(sql_command)
        conn.commit()
    except Exception as e:
        print("Ensemble update failed:",e)
        return False
    return True

def calc_ensemble_census(conn):
    if conn is None:
        return False
    try:
        cur=conn.cursor()
        sql_command = """
            insert into "BG_Model_Score" (bg_geo_id, raw_score, model_id, score, date_calculated) select 
                bg_geo_id
                ,avg(score)
                ,18
                ,round(avg(score))
                ,now()::date
                FROM "BG_Model_Score" as bms
                where bms.model_id in (14,16)
                GROUP BY bg_geo_id
            on conflict on constraint bg_model_pk do update
            set score = excluded.score,
            raw_score = excluded.raw_score,
            date_calculated = excluded.date_calculated;
    """
        cur.execute(sql_command)
        conn.commit()
    except Exception as e:
        print("Ensemble update failed:",e)
        return False
    return True


#Takes a dataframe and uploads to SQL server
def update_db_score(conn,df,model,is_building=True):
    if conn is None:
        return False
    if model is None:
        return False
    if df is None:
        return False
    if is_building:  #Building dataframe being used
        table_name="Building_Model_Score"
        id_name="cs_id"
        constraint_name="building_model_pk"
        if 'raw_score' in list(df):
            column_list=['CS_ID','score','raw_score']
            raw_available=True
        else:
            column_list=['CS_ID','score']
            raw_available=False
    else:   #Census dataframe
        table_name="BG_Model_Score"
        id_name="bg_geo_id"
        constraint_name="bg_model_pk"
        if 'raw_score' in list(df):
            column_list=['bg_geo_id','score','raw_score']
            raw_available=True
        else:
            column_list=['bg_geo_id','score']
            raw_available=False
    cur=conn.cursor()
    print("Updating database",end='')
    max_count=df.shape[0]
    ten_percent=round(max_count/10)
    if ten_percent == 0:
        ten_percent = 1
    count=0
    try:
        for row in df[column_list].itertuples(index=False):
            count+=1
            if count % ten_percent == 0:
                print(" ...",(count // ten_percent)*10," %",end="",sep="")
            id = row[0]
            score = row[1]
            if raw_available:
                raw_score = row[2]
            else:
                raw_score = "NULL"
            # print("Updating:",id,score,raw_score)
            if id is None:
                continue
            if score is None:
                continue
            sql_command = """
            insert into "{}" ({}, model_id, score, raw_score, date_calculated) VALUES ('{}',{},{},{},NOW()::date)
            on conflict on constraint {} do update
            set score = excluded.score,
            raw_score = excluded.raw_score,
            date_calculated = excluded.date_calculated;
            """.format(table_name,id_name,id,model,score,raw_score,constraint_name)
            # print(sql_command)
            cur.execute(sql_command)
        conn.commit()
    except Exception as e:
        print("SQL command to update scores has failed:",e)
        return False
    print('\n')
    return True


def main(conn=None):
    if conn is None:
        conn=getConn()
    if conn is None:
        sys.exit("Failed to get SQL connection")
    if rg2.check_for_config():
        config = rg2.read_config()
        database_config = config['Database']
        host=database_config['host_ip']
        port=database_config['port']
        database=database_config['database']
        user=database_config['user']
        password=database_config['password']
    else:
        sys.exit("Configuration file not present")
    success=[] #Run each R model one at a time and store if they were successfully run

    print("Running KNN Sale Model")
    df = calc_knn_sale(user,password,host,database,port)
    model = str(int(df['model_id'].iat[0])) #model 13
    success.append(update_db_score(conn,df,model))

    print("Running KNN Census Model")
    df = calc_knn_census(user,password,host,database,port)
    success.append(update_db_score(conn,df,14,is_building=False))

    print("Running Neural Network Sale Model")
    df = calc_neuralnet_sale(user,password,host,database,port)
    success.append(update_db_score(conn,df,15))

    print("Running Neural Network Census Model")
    df = calc_neuralnet_census(user,password,host,database,port)
    success.append(update_db_score(conn,df,16,is_building=False))

    print("Running Building Ensemble")
    success.append(calc_ensemble_sale(conn))

    print("running Census Ensemble")
    success.append(calc_ensemble_census(conn))

    return success


if __name__ == '__main__':
    print(main())

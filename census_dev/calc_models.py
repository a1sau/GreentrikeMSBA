import pandas as pd
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
import reverse_geocoder2 as rg2
from combine_var import getConn
import sys


def calc_knn_sale(user,password,host,database,port):
    r = robjects.r
    r['source']('for_sale_KNN_dynamic_script.R')  #object of R file
    get_main_function_r = robjects.globalenv['main_forsale_knn']  #loading R function to use
    df_result_r = get_main_function_r(user,password,host,database,port)
    df_result = pandas2ri.rpy2py(df_result_r)
    return df_result


def calc_neuralnet_sale(user,password,host,database,port):
    r = robjects.r
    r['source']('nn_building_script.R')  #object of R file
    get_main_function_r = robjects.globalenv['mainfunction.all']  #loading R function to use
    df_result_r = get_main_function_r(host,user,password,database,port)
    df_result = pandas2ri.rpy2py(df_result_r)
    return df_result


def update_db_score(conn,df,model):
    if conn is None:
        return False
    if model is None:
        return False
    cur=conn.cursor()
    if 'raw_score' in list(df):
        column_list=['CS_ID','score','raw_score']
        raw_available=True
    else:
        column_list=['CS_ID','score']
        raw_available=False
    try:
        for row in df[column_list].itertuples(index=False):
            cs_id = row[0]
            score = row[1]
            if raw_available:
                raw_score = row[2]
            else:
                raw_score = "NULL"
            print("Updating:",cs_id,score,raw_score)
            if cs_id is None:
                continue
            if score is None:
                continue
            sql_command = """
            insert into "Building_Model_Score" (cs_id, model_id, score, raw_score, date_calculated) VALUES ('{}',{},{},{},NOW()::date)
            on conflict on constraint building_model_pk do update
            set score = excluded.score,
            raw_score = excluded.raw_score,
            date_calculated = excluded.date_calculated;
            """.format(cs_id,model,score,raw_score)
            # print(sql_command)
            cur.execute(sql_command)
        conn.commit()
    except Exception as e:
        print("SQL command to update scores has failed:",e)
        return False
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
    success=[]
    df = calc_knn_sale(user,password,host,database,port)
    model=str(int(df['model_id'].iat[0]))
    success.append(update_db_score(conn,df,model))
    df = calc_neuralnet_sale(user,password,host,database,port)
    success.append(update_db_score(conn,df,15))
    return success


if __name__ == '__main__':
    print(main())

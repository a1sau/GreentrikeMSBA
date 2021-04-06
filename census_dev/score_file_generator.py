import os.path
import pandas as pd
import psycopg2
import configparser as cp
from combine_var import getConn
import reverse_geocoder2 as rg2
import xlsxwriter
from math import isnan

#Grab records, pick best records, create excel file, file in excel file, add formatting, handle multiple item versions


##Pull combination of building and census data
def pull_building(score_user,no_score_only):
    conn=getConn()

##Pull only census data
def pull_census(score_user,no_score_only=True):
    pass

##pick buildings
def select_building(conn,filename,limit=10):
    if limit<=0:
        limit=10
    sql_command="""\
    select
    bld."CS_ID"
    ,avg(bs."Score") "Average Building Score"
    ,bld."Address_Line"
    ,bld."City"
    ,bld."Postal_Code"
    ,bld."Property_Type"
    ,bld."Year_Built"
    ,bld."Price"
    ,bld."SquareFeet"
    ,round(cast(coalesce(bld."Price" / bld."SquareFeet",NULL) as numeric),0) "$ per sq ft"
     ,bld."Sale_Type"
     ,'' as "Building Score"
     ,'' as "-"
     ,bg.bg_geo_id "Block Group ID"
     ,max(case when dv.sid='pop' then bgd.value Else 0 END) "Population"
     ,max(case when dv.sid='pop_MF_3MS' then bgd.value Else 0 END) "Population: 3 Miles"
     ,max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) "Households: 3 Miles"
    ,max(case when dv.sid='M_0_5' then bgd.value Else 0 END)+max(case when dv.sid='F_0_5' then bgd.value Else 0 END) "Kids under 5"
     ,round(cast((max(case when dv.sid='M_0_5' then bgd.value Else 0 END)+max(case when dv.sid='F_0_5' then bgd.value Else 0 END)) /
        max(case when dv.sid='pop' then bgd.value Else null END) as numeric),3) "Percent Kids under 5"
    ,max(case when dv.sid='M_0_5_3MS' then bgd.value Else 0 END)+max(case when dv.sid='F_0_5_3MS' then bgd.value Else 0 END) "Kids under 5: 3 Miles"
     ,round(cast((max(case when dv.sid='M_0_5_3MS' then bgd.value Else 0 END)+max(case when dv.sid='F_0_5_3MS' then bgd.value Else 0 END)) /
        max(case when dv.sid='pop_MF_3MS' then bgd.value Else null END) as numeric),3) "Percent Kids under 5: 3 Miles"
    ,max(case when dv.sid='M_5_9' then bgd.value Else 0 END)+max(case when dv.sid='F_5_9' then bgd.value Else 0 END) "Kids 5 to 9"
     ,round(cast((max(case when dv.sid='M_5_9' then bgd.value Else 0 END)+max(case when dv.sid='F_5_9' then bgd.value Else 0 END)) /
        max(case when dv.sid='pop' then bgd.value Else null END) as numeric),3) "Percent Kids 5 to 9"
    ,max(case when dv.sid='M_5_9_3MS' then bgd.value Else 0 END)+max(case when dv.sid='F_5_9_3MS' then bgd.value Else 0 END) "Kids 5 to 9: 3 Miles"
    ,round(cast((max(case when dv.sid='M_5_9_3MS' then bgd.value Else 0 END)+max(case when dv.sid='F_5_9_3MS' then bgd.value Else 0 END)) /
         max(case when dv.sid='pop_MF_3MS' then bgd.value Else null END) as numeric),3)  "Percent Kids 5 to 9: 3 Miles"
    ,max(case when dv.sid='avg_age' then bgd.value Else 0 END) "Average Age"
    ,round(cast(sum(case when dv.sid in('hi_0_10_3MS','hi_10_15_3MS','hi_15_20_3MS','hi_20_25_3MS','hi_25_30_3MS','hi_30_35_3MS','hi_35_40_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income under 40K: 3 Mile"
    ,round(cast(sum(case when dv.sid in('hi_40_45_3MS','hi_45_50_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income 40K to 50K: 3 Mile"
    ,round(cast(sum(case when dv.sid in('hi_50_60_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income 50K to 60K: 3 Mile"
    ,round(cast(sum(case when dv.sid in('hi_60_75_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income 60K to 75K: 3 Mile"
    ,round(cast(sum(case when dv.sid in('hi_75_100_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income 75K to 100K: 3 Mile"
    ,round(cast(sum(case when dv.sid in('hi_100_125_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income 100K to 125K: 3 Mile"
    ,round(cast(sum(case when dv.sid in('hi_125_150_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income 125K to 150K: 3 Mile"
    ,round(cast(sum(case when dv.sid in('hi_150_200_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income 150K to 200K: 3 Mile"
    ,round(cast(sum(case when dv.sid in('hi_200_999_3MS') then bgd.value  else 0 END) /
      max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) as numeric),3) "Household income 200K+: 3 Mile"
    ,'' as "Block Group Score"
    from "Building" as bld
    left join "Block_Group" as bg on bg.bg_geo_id = bld.bg_geo_id
    left join "BG_Data" as bgd on bg.bg_geo_id = bgd.bg_geo_id
    inner join "Demo_Var" as dv on dv.full_variable_id=bgd.variable_id
    left join "BG_Score" as bgs on bg.bg_geo_id = bgs.bg_geo_id
    left join "Building_Score" as bs on bld."CS_ID" = bs.cs_id
    group by bld."CS_ID",bld."Address_Line",bld."City",bld."Postal_Code",bld."Property_Type",bld."Price",bld."Year_Built",bld."SquareFeet",bld."Sale_Type",bg.bg_geo_id
    having
    max(case when dv.sid='pop' then bgd.value Else 0 END) > 0     --Handle BGs with no population
    and max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END)>0
    limit {};
    """.format(limit)
    print(sql_command)
    cur = conn.cursor()
    cur.execute(sql_command)
    try:
        df_var=pd.read_sql_query(sql_command,conn)
    except (Exception, psycopg2.DatabaseError) as err:
        show_psycopg2_exception(err)
    print(df_var)
    xrow=-1
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Score")
    for colnam in df_var.columns:
        xrow+=1
        worksheet.write(xrow,0,colnam)
        xcol=0
        for row in df_var[colnam]:
            print(row,type(row))
            if isinstance(row,float):
                if isnan(row):
                    row=""
            xcol+=1
            worksheet.write(xrow,xcol,row)
    try:
        workbook.close()
    except:
        print("File creation error")




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


def select_census(df_census,limit=10):
    pass

def determine_excel_path(type):
    pass


def xlsx_test(filename):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet("Score")
    worksheet.write('A1', 'Hello world')
    try:
        workbook.close()
    except:
        print("File creation error")


if __name__ == '__main__':
    conn=getConn()
    if rg2.check_for_config():
        config = rg2.read_config()
        email_config = config['Email']
        password = email_config.get('password',raw=True)
        work_dir = email_config.get('attachment',raw=True)
        if work_dir:
            os.chdir(work_dir)
            print("Working directory:",os.getcwd())
    select_building(conn,"test2.xlsx",5)

    # xlsx_test('test.xlsx')



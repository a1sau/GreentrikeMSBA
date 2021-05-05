import os.path
import pandas as pd
import psycopg2
import configparser as cp
from combine_var import getConn
import reverse_geocoder2 as rg2
import xlsxwriter
from math import isnan
import sys
from datetime import datetime,date,timedelta
import emailer as em


#Grab records, pick best records, create excel file, file in excel file, add formatting, handle multiple item versions


def select_lease_building(conn,user='',limit=10):
    if limit<=0:
        limit=10
    if user:
        user_filter = 'and bs.uid='+str(user)
    sql_command="""\
    select
    bld."CS_ID"
    ,bld."Address_Line"
    ,bld."City"
    ,bld."Postal_Code"
    ,bld."Property_Type"
    ,bld."Year_Built"
    ,bld."Price_monthly" "Monthly Rent"
    ,bld."SquareFeet"
    ,bld."Expansion_sqft" "Available Expansion Sq Ft"
    ,bld."Space"
    ,bld."Available" "Availability"
    ,bld."Term" "Lease Term"
    ,round(cast(coalesce(bld."Price_monthly" / bld."SquareFeet",NULL) as numeric),2) "$ per sq ft"
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
    left join "Building_Score" as bs on bld."CS_ID" = bs.cs_id {}
    where
        bs."Score" is null and bld."Currently_listed"=True and bld."Sale_Lease"='Lease'
    group by bld."CS_ID",bld."Address_Line",bld."City",bld."Postal_Code",bld."Property_Type",bld."Price",bld."Year_Built",bld."SquareFeet",bld."Sale_Type",bg.bg_geo_id
    having
    max(case when dv.sid='pop' then bgd.value Else 0 END) > 0     --Handle BGs with no population
    and max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END)>0
    order by RANDOM()
    limit {};
    """.format(user_filter,limit)
    # cur = conn.cursor()
    # cur.execute(sql_command)
    try:
        df_var=pd.read_sql_query(sql_command,conn)
    except (Exception, psycopg2.DatabaseError) as err:
        show_psycopg2_exception(err)
        sys.exit()
    return df_var

##Pull only census data
def pull_census(score_user,no_score_only=True):
    pass

##pick buildings
def select_sale_building(conn,user='',limit=10):
    if limit<=0:
        limit=10
    if user:
        user_filter = 'and bs.uid='+str(user)
    sql_command="""\
    select
    bld."CS_ID"
    ,bld.url "URL"
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
    left join "Building_Score" as bs on bld."CS_ID" = bs.cs_id {}
    where
        bs."Score" is null and bld."Currently_listed"=True and bld."Sale_Lease"='Sale'
    group by bld."CS_ID",bld."Address_Line",bld."City",bld."Postal_Code",bld."Property_Type",bld."Price",bld."Year_Built",bld."SquareFeet",bld."Sale_Type",bg.bg_geo_id
    having
    max(case when dv.sid='pop' then bgd.value Else 0 END) > 0     --Handle BGs with no population
    and max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END)>0
    order by RANDOM()
    limit {};
    """.format(user_filter,limit)
    # cur = conn.cursor()
    # cur.execute(sql_command)
    try:
        df_var=pd.read_sql_query(sql_command,conn)
    except (Exception, psycopg2.DatabaseError) as err:
        show_psycopg2_exception(err)
        sys.exit()
    return df_var


#Generate score sheet with formatting from DF
def gen_excel(sale_df,filename,lease_df):

    workbook = xlsxwriter.Workbook(filename)
    cell_bold = workbook.add_format({'bold':True})
    cell_underline= workbook.add_format({'underline':True})
    cell_dollar = workbook.add_format({'num_format':'$#,##0.00_);($#,##0.00)'})
    cell_percent = workbook.add_format({'num_format':'0.0%'})
    cell_score = workbook.add_format({'bg_color':'#33CCCC','bold':True})
    format_dict={"cell_bold":cell_bold,"cell_underline":cell_underline,"cell_dollar":cell_dollar,
                 "cell_percent":cell_percent,"cell_score":cell_score}
    workbook=gen_sheet(workbook,sale_df,format_dict,"Sale")
    workbook=gen_sheet(workbook,lease_df,format_dict,"Lease")
    try:
        workbook.close()
        return True
    except:
        print("File creation error")
    return False


def gen_sheet(workbook,df_var,format_dict,worksheet_name="Sheet"):
    prop_count=len(df_var)
    xrow=-1
    worksheet = workbook.add_worksheet(worksheet_name)
    worksheet.set_column(0,0,36)  #Set column A width
    worksheet.set_column(1,prop_count,20)  #Set column A width
    for colnam in df_var.columns:
        xrow+=1
        if colnam[0]=="-":    #treat "-" as a blank row
            continue
        else:
            worksheet.write(xrow,0,colnam,format_dict["cell_bold"])
        xcol=0
        for row in df_var[colnam]:
            if isinstance(row,float):
                if isnan(row):
                    row=""
            xcol+=1
            if colnam[-5:] == "Score":
                worksheet.write(xrow,xcol,row,format_dict["cell_score"])
            elif colnam in ("Price","Monthly Rent","$ per sq ft"):
                worksheet.write(xrow,xcol,row,format_dict["cell_dollar"])
            elif colnam in ('CS_ID','Block Group ID'):
                worksheet.write(xrow,xcol,row,format_dict["cell_underline"])
            elif colnam in ('URL'):
                worksheet.write_url(xrow,xcol,row,string='Link')
            else:
                worksheet.write(xrow,xcol,row)
    return workbook


#print out SQl errors
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


def control_building(conn,uid,limit):
    filename=gen_filename(uid,1)

    sale_df = select_sale_building(conn,uid,limit)
    lease_df=select_lease_building(conn,uid,limit)
    ok = gen_excel(sale_df,filename,lease_df)
    if ok:
        return filename
    else:
        print("Excel generation failed")
        return None
    return None


def gen_filename(uid,type=1):
    now=datetime.now()
    if type == 1:
        filename="Building_"+str(uid)+"_"+now.strftime("%Y%m%d_%H%M%S")+".xlsx"
    elif type == 2:
        filename="Census_"+str(uid)+"_"+now.strftime("%Y%m%d_%H%M%S")+".xlsx"
    else:
        return None
    return filename


def get_user_email(conn,uid):
    if not uid:
        print('No user ID specified')
        return None
    sql_command =   """select
                    use.email
                    from "User" as use
                    where
                    use.uid = {};
                    """.format(uid)
    cur = conn.cursor()
    cur.execute(sql_command)
    email = cur.fetchone()[0]
    #TODO add email validation
    return email


def email_users_main():
    conn=getConn()
    if rg2.check_for_config():
        config = rg2.read_config()
        email_config = config['Email']
        email = email_config.get('email')
        password = email_config.get('password',raw=True)
        work_dir = email_config.get('excel_output',raw=True)
        if work_dir:
            os.chdir(work_dir)
            print("Working directory:",os.getcwd())
        else:
            print("")
    #Get list of users from server
    sql_command="""select
    use.uid
    ,use.last_building_email
    ,use.email_frequency
    from "User" as use
    where
    use.subscribed_building = TRUE
    and use.active = TRUE; 
    """
    try:
        df_user=pd.read_sql_query(sql_command,conn)
    except (Exception, psycopg2.DatabaseError) as err:
        show_psycopg2_exception(err)
        sys.exit()
    today=date.today()
    for i,user_line in df_user.iterrows():
        print(i,user_line)
        uid=user_line['uid']
        freq=user_line['email_frequency']
        last_email_dt=user_line['last_building_email']
        print(type(last_email_dt))
        if (freq is None) or isnan(freq):
            freq = 7
            update_user_frequency(conn,uid,freq)  #set default on server if missing
        time_for_email=False
        if user_line['last_building_email'] is None:  #email not previously sent
            time_for_email=True
        else:
            next_email_dt=last_email_dt+timedelta(days=freq)
            time_for_email = (today>=next_email_dt)
        if time_for_email:  #generate new score file and email user
            print("Creating email for UID",uid)
            file=control_building(conn,uid,10)
            to_email = get_user_email(conn,uid)
            if file:
                print("Sending email:",to_email,file)
                email_sent=em.create_email(to_email,email,password,file)
                if email_sent:
                    update_last_sent(conn,uid)  #update user with latest email date
                    #TODO delete file after sent

    conn.close()
    return True


def update_user_frequency(conn,uid,freq=7):
    if uid is None:
        return False
    cur=conn.cursor()
    sql_command="""
    update "User" as use
    set email_frequency = {}
    where
    use.uid={};
    """.format(freq,uid)
    try:
        cur.execute(sql_command)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as err:
        show_psycopg2_exception(err)
        sys.exit()
    return True


def update_last_sent(conn,uid,building=True):
    if uid is None:
        return False
    cur=conn.cursor()
    if building:
        field='last_building_email'
    else:
        field='last_census_email'
    sql_command="""
    update "User" as use
    set {} = NOW()::date
    where
    use.uid={};
    """.format(field,uid)
    try:
        cur.execute(sql_command)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as err:
        show_psycopg2_exception(err)
        sys.exit()
    return True


if __name__ == '__main__':
    email_users_main()




from timeit import default_timer as timer
import pandas as pd
import psycopg2
import reverse_geocoder2 as rg2
from math import cos, acos, sin, radians
from multiprocessing import Process, Queue, current_process
import os
import numpy as np


def distance_lat_long(lat1, lat2, lon1, lon2):
    e_radius = 3963.0 #earth radius in miles
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    if (lat1==lat2 and lon1==lon2):
        return 0
    return e_radius * acos((sin(lat1)*sin(lat2))+cos(lat1)*cos(lat2)*cos(lon2-lon1))


def eta_time(start_time,complete,total):
    time_left_str=""
    if complete <= 0:
        complete=1
    time_run = timer()-start_time
    if time_run<=0:
        time_run = 1
    remaining_tasks = total-complete
    task_per_second = complete / time_run
    remaining_time = remaining_tasks / task_per_second
    if remaining_time < 1:
        return "Less than a second"
    remaining_min = round(remaining_time // 60,0)
    remaining_seconds = round(remaining_time % 60,0)
    if remaining_min > 0:
        if remaining_min == 1:
            time_left_str = "1 minute "
        else:
            time_left_str = str(remaining_min)+" minutes "
    if remaining_seconds > 0:
        if remaining_seconds == 1:
            time_left_str = time_left_str+"1 second"
        else:
            time_left_str = time_left_str+str(remaining_seconds)+" seconds"
    return time_left_str

def calc_dist(dist_df,geo_df,dis_limit=0,queue=None):
    count=0
    list_arr=[]
    start=timer()
    row_time=start
    for index,row in dist_df.iterrows():
        count+=1
        if (count % 10 == 0):
            ptime=round(timer()-row_time,1)
            row_time=timer()
            print(current_process().name,"Processing row:",count, "-","Segment Process Time:",ptime, "seconds",
                  "ETA:",eta_time(start,count-1,len(dist_df)))
            print()
        latA=geo_df.loc[index,['LAT']].values[0]
        longA=geo_df.loc[index,['LONG']].values[0]
        # print("Index:",index)
        for col in row.index:
            # print("Index:",index,"Column",col)
            latB=geo_df.loc[col,['LAT']].values[0]
            longB=geo_df.loc[col,['LONG']].values[0]
            distance=distance_lat_long(latA,latB,longA,longB)
            if (dis_limit <= 0) or (distance<dis_limit):
                list_arr.append([index,col,round(distance,1)])
            # dist_df.loc[[index],[col]]=round(distance,1)
            # print(count,latA,latB,longA,longB,distance_lat_long(latA,latB,longA,longB))
    if queue is not None:
        print("Uploading: PID",current_process().name)
        queue.put(list_arr)
    return list_arr


def pull_data(limit=0,outfile=None,dis_limit=0):
    count=0
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
    try:
        outputfile = open(file=outfile,mode="w")
    except:
        print("Could not open output file:",outfile)
        return None
    print("point_a","point_b","distance",sep=",",file=outputfile)
    cur = conn.cursor()
    # cur.execute("select * from \"Block_Group\" as bg where bg.city is null")
    sql_statement = "select bg.bg_geo_id, bg.longitude, bg.latitude from \"Block_Group\" as bg " \
                    "where bg.city is null order by bg.bg_geo_id"
    if limit > 0:
        sql_statement += " limit {}".format(limit)
    cur.execute(sql_statement)
    rows = cur.fetchall()
    geo_list=[]
    lat_list=[]
    long_list=[]
    print("Block groups found:",len(rows))
    print("Starting Data Processing")
    for row in rows:
        geo_id=row[0]
        long=row[1]
        lat=row[2]
        geo_list.append(geo_id)
        lat_list.append(lat)
        long_list.append(long)
    print("Starting Distance Calculations")
    geo_df = pd.DataFrame(zip(geo_list,lat_list,long_list),columns=("GEO_ID","LAT","LONG"))
    # print(geo_df)
    geo_df.index=geo_list
    # print(geo_df)
    dist_df = pd.DataFrame(data=0,index=geo_df["GEO_ID"],columns=geo_df["GEO_ID"])
    # print(dist_df)
    start = timer()
    row_time=start
    if len(dist_df)>10:    #don't multiprocess unless there are enough record
        num_process = os.cpu_count()
    else:
        num_process = 1
    print("CPUs used:",num_process)
    dist_arr = np.array_split(dist_df,num_process)
    queue = Queue()
    processes = []
    for x in range(num_process):
        processes.append(Process(name="Section_"+str(x+1),target=calc_dist, args=(dist_arr[x], geo_df, dis_limit, queue)))
    x = 0
    for p in processes:
        p.start()
        print("Starting Process:",p.name)
    # for p in processes:
    #     p.join()
    results = []
    for p in processes:
        results.append(queue.get(block=True))
    # print(results)
    print(len(results),len(results[0]))
    for group in results:
        print(group)
        for row in group:
            print(row[0],row[1],row[2],file=outputfile,sep=",")
    # print(dist_df)
    print("Total Time:",round(timer()-start,1),"seconds")
    # dist_df.to_csv('distanceB.csv')
    return None


if __name__ == "__main__":
    pull_data(limit=200, outfile=r'C:\Users\Lugal\OneDrive\Documents\MSBA\Project\GreentrikeMSBA\census_dev\distanceD.csv',dis_limit=5)




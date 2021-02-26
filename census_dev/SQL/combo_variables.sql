select
    dist.bg_geo_id1
    ,dist.bg_geo_id2
    ,bg2.variable_id
    ,bg2.value
from "BG_Distance" as dist
inner join "BG_Data" as bg1 on bg1.bg_geo_id = dist.bg_geo_id1
inner join "BG_Data" as bg2 on bg2.bg_geo_id = dist.bg_geo_id2
where
dist.distance<=1
  and bg1.bg_geo_id='530330001001'
  and bg1.variable_id='B01003_001E'
  and bg2.variable_id='B01003_001E'
--group by dist.bg_geo_id1, dist.bg_geo_id2, bg2.variable_id, bg2.value


select
    dist.bg_geo_id1
    ,concat(bg2.variable_id,'_1MS') "variable_id"
    ,sum(bg2.value) "Sum BG2"
    ,bg1.value "BG1 Value"
    ,sum(bg2.value)+bg1.value "value"
     ,count(bg2.value)
    ,(sum(bg2.value)+bg1.value)/(count(bg2.value)+1)
    ,avg(dist.distance)
from "BG_Distance" as dist
inner join "BG_Data" as bg1 on bg1.bg_geo_id = dist.bg_geo_id1
inner join "BG_Data" as bg2 on bg2.bg_geo_id = dist.bg_geo_id2
where
dist.distance<=1
  and bg1.variable_id='B01003_001E'
  and bg2.variable_id='B01003_001E'
group by dist.bg_geo_id1, bg2.variable_id, bg1.value;

select
    bg1.bg_geo_id
    ,concat(bg1.variable_id,'_1MS') "variable_id"
    ,sum(bg2.value) "Sum BG2"
    ,bg1.value "BG1 Value"
    ,sum(bg2.value)+bg1.value "value"
     ,count(bg2.value)
     ,coalesce((sum(bg2.value)+bg1.value)/(count(bg2.value)+1),bg1.value) "average"
     ,coalesce(round((sum(bg2.value*((1-dist.distance)/distance))+bg1.value)),bg1.value) "linear"
     ,coalesce(round(sum(bg2.value*((1-dist.distance)/distance))+bg1.value),bg1.value)
     ,coalesce(avg(dist.distance),0) "Average distance"
from "BG_Data" as bg1
left join "BG_Distance" as dist on bg1.bg_geo_id = dist.bg_geo_id1 and distance <= 1
left join "BG_Data" as bg2 on bg2.bg_geo_id = dist.bg_geo_id2
where
    bg1.variable_id='B01003_001E'
    and (dist.distance is null or
    (dist.distance<=1
  and bg2.variable_id='B01003_001E'))
group by bg1.bg_geo_id, bg1.variable_id, bg1.value
order by count(bg2.value) asc;

select
    count(bg1.variable_id)
from "BG_Data" as bg1
left join "BG_Distance" as dist on bg1.bg_geo_id = dist.bg_geo_id1 and dist.distance<=1
left join "BG_Data" as bg2 on bg2.bg_geo_id = dist.bg_geo_id2
where
    bg1.variable_id='B01001_002E'
    and (bg1.variable_id is null or bg2.variable_id='B01001_002E')
group by bg1.variable_id

select
    bg1.variable_id
from "BG_Data" as bg1
where
    bg1.variable_id='B01001_002E'


select
    count(bg1.variable_id)
from "BG_Data" as bg1
where
    bg1.variable_id='B01001_002E'
group by bg1.bg_geo_id

select var.full_variable_id, var.base_variable_name
from "Demo_Var" as var

select source_id,full_name,type,url,census_table,base_variable_id,full_variable_id,minimum,maximum,data_year,census_variable
from "Demo_Var"
where
      full_variable_id in ('B19001_012E','B19001_007E','B19001_006E','B01001_027E','B01001_003E','B19001_011E','B19001_016E','B19001_010E','B19001_015E','B19001_017E','B19001_008E','B19001_009E','B19001_002E','B19001_001E','B19001_004E','B19001_013E','B19001_014E','B19001_005E','B19001_003E','B01001_001E','B01001_002E','B01001_004E','B01001_028E','B01001_026E')

select full_variable_id from "Demo_Var" as dv where dv.full_variable_id in ("B01001_026E_1MS","B19001_014E_1MS","B19001_007E_1MS","B19001_008E_1MS","B19001_004E_1MS","B19001_011E_1MS","B19001_006E_1MS","B01001_004E_1MS","B19001_003E_1MS","B01001_027E_1MS","B19001_012E_1MS","B01001_028E_1MS","B01001_003E_1MS","B19001_002E_1MS","B19001_010E_1MS","B19001_013E_1MS","B19001_005E_1MS","B01001_002E_1MS","B19001_001E_1MS","B19001_009E_1MS","B19001_015E_1MS","B19001_016E_1MS","B01001_001E_1MS","B19001_017E_1MS")

select
    dv.full_variable_id
    ,count(bg.variable_id)
from "Demo_Var" as dv
left join "BG_Data" as bg on bg.variable_id = dv.full_variable_id
group by dv.full_variable_id

delete from "BG_Data" where variable_id like '%_3MS'
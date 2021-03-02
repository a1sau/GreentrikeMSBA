--old way
select
    bgd.bg_geo_id
    ,max(case when bgd.variable_id='B01001_003E' then bgd.value Else 0 END) "Boys under 5"
    ,max(case when bgd.variable_id='B19001_014E' then bgd.value else 0 END) "Household income between 100K and 125K"
from "BG_Data" as bgd
group by bgd.bg_geo_id;

--New way with sid
select
    bgd.bg_geo_id
    ,max(case when dv.sid='M_0_5' then bgd.value Else 0 END) "Boys under 5"
    ,max(case when dv.sid='hi_100_125' then bgd.value else 0 END) "Household income between 100K and 125K"
from "BG_Data" as bgd
left join "Demo_Var" as dv on dv.full_variable_id=bgd.variable_id
group by bgd.bg_geo_id;


select
    bld."CS_ID"
    ,bld."Address_Line"
    ,bld."City"
    ,bld."Postal_Code"
    ,bld."Property_Type"
    ,bld."Year_Built"
    ,bld."Price"
    ,bld."SquareFeet"
    ,round(cast(coalesce(bld."Price" / bld."SquareFeet",NULL) as numeric),0) "$ per sq ft"
     ,bld."Sale_Type"
     ,bg.bg_geo_id "Block Group ID"
     ,max(case when dv.sid='pop' then bgd.value Else 0 END) "Population"
     ,max(case when dv.sid='pop_MF_3MS' then bgd.value Else 0 END) "Population: 3 Miles"
     ,max(case when dv.sid='hi_tot_3MS' then bgd.value Else 0 END) "Households: 3 Miles"
    ,max(case when dv.sid='M_0_5' then bgd.value Else 0 END)+max(case when dv.sid='F_0_5' then bgd.value Else 0 END) "Kids under 5"
    ,max(case when dv.sid='M_0_5_3MS' then bgd.value Else 0 END)+max(case when dv.sid='F_0_5_3MS' then bgd.value Else 0 END) "Kids under 5: 3 Miles"
    ,max(case when dv.sid='M_5_9' then bgd.value Else 0 END)+max(case when dv.sid='F_5_9' then bgd.value Else 0 END) "Kids 5 to 9"
    ,max(case when dv.sid='M_5_9_3MS' then bgd.value Else 0 END)+max(case when dv.sid='F_5_9_3MS' then bgd.value Else 0 END) "Kids 5 to 9: 3 Miles"
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
from "Building" as bld
inner join "Block_Group" as bg on bg.bg_geo_id = bld.bg_geo_id
left join "BG_Data" as bgd on bg.bg_geo_id = bgd.bg_geo_id
inner join "Demo_Var" as dv on dv.full_variable_id=bgd.variable_id
group by bld."CS_ID",bld."Address_Line",bld."City",bld."Postal_Code",bld."Property_Type",bld."Price",bld."Year_Built",bld."SquareFeet",bld."Sale_Type",bg.bg_geo_id



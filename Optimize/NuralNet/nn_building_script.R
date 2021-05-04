library(DBI)
library(sqldf)
library(dplyr)
library(neuralnet)
library(Metrics)
library(caret)
library(config)
library(datapackage.r)
library(jsonlite)
library(fastDummies)
library(datarium)
library(ggplot2)


get_data <- function(scores_or_new, server, user, password, database, port){
  library(odbc)
  con <- DBI::dbConnect(odbc::odbc(),
                        driver = "PostgreSQL Unicode(x64)",
                        database = as.character(database),
                        UID      = as.character(user),
                        PWD      = as.character(password),
                        server = as.character(server),
                        port = port)
  import.building <- 'SELECT
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
     ,bg.bg_geo_id "Block Group ID"
     ,avg(bgs.score) "Average Block Group Score"
     ,max(case when dv.sid=\'pop\' then bgd.value Else 0 END) "Population"
     ,max(case when dv.sid=\'pop_MF_3MS\' then bgd.value Else 0 END) "Population: 3 Miles"
     ,max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) "Households: 3 Miles"
    ,max(case when dv.sid=\'M_0_5\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_0_5\' then bgd.value Else 0 END) "Kids under 5"
     ,round(cast((max(case when dv.sid=\'M_0_5\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_0_5"\' then bgd.value Else 0 END)) /
        max(case when dv.sid=\'pop\' then bgd.value Else null END) as numeric),3) "Percent Kids under 5"
    ,max(case when dv.sid=\'M_0_5_3MS\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_0_5_3MS\' then bgd.value Else 0 END) "Kids under 5: 3 Miles"
     ,round(cast((max(case when dv.sid=\'M_0_5_3MS\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_0_5_3MS\' then bgd.value Else 0 END)) /
        max(case when dv.sid=\'pop_MF_3MS\' then bgd.value Else null END) as numeric),3) "Percent Kids under 5: 3 Miles"
    ,max(case when dv.sid=\'M_5_9\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_5_9\' then bgd.value Else 0 END) "Kids 5 to 9"
     ,round(cast((max(case when dv.sid=\'M_5_9\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_5_9\' then bgd.value Else 0 END)) /
        max(case when dv.sid=\'pop\' then bgd.value Else null END) as numeric),3) "Percent Kids 5 to 9"
    ,max(case when dv.sid=\'M_5_9_3MS\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_5_9_3MS\' then bgd.value Else 0 END) "Kids 5 to 9: 3 Miles"
    ,round(cast((max(case when dv.sid=\'M_5_9_3MS\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_5_9_3MS\' then bgd.value Else 0 END)) /
         max(case when dv.sid=\'pop_MF_3MS\' then bgd.value Else null END) as numeric),3)  "Percent Kids 5 to 9: 3 Miles"
    ,max(case when dv.sid=\'avg_age\' then bgd.value Else 0 END) "Average Age"
    ,round(cast(sum(case when dv.sid in(\'hi_0_10_3MS\',\'hi_10_15_3MS\',\'hi_15_20_3MS\',\'hi_20_25_3MS\',\'hi_25_30_3MS\',\'hi_30_35_3MS\',\'hi_35_40_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income under 40K: 3 Mile"
    ,round(cast(sum(case when dv.sid in(\'hi_40_45_3MS\',\'hi_45_50_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income 40K to 50K: 3 Mile"
    ,round(cast(sum(case when dv.sid in(\'hi_50_60_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income 50K to 60K: 3 Mile"
    ,round(cast(sum(case when dv.sid in(\'hi_60_75_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income 60K to 75K: 3 Mile"
    ,round(cast(sum(case when dv.sid in(\'hi_75_100_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income 75K to 100K: 3 Mile"
    ,round(cast(sum(case when dv.sid in(\'hi_100_125_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income 100K to 125K: 3 Mile"
    ,round(cast(sum(case when dv.sid in(\'hi_125_150_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income 125K to 150K: 3 Mile"
    ,round(cast(sum(case when dv.sid in(\'hi_150_200_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income 150K to 200K: 3 Mile"
    ,round(cast(sum(case when dv.sid in(\'hi_200_999_3MS\') then bgd.value  else 0 END) /
      max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) as numeric),3) "Household income 200K+: 3 Mile"
from "Building" as bld
left join "Block_Group" as bg on bg.bg_geo_id = bld.bg_geo_id
left join "BG_Data" as bgd on bg.bg_geo_id = bgd.bg_geo_id
inner join "Demo_Var" as dv on dv.full_variable_id=bgd.variable_id
left join "BG_Score" as bgs on bg.bg_geo_id = bgs.bg_geo_id
left join "Building_Score" as bs on bld."CS_ID" = bs.cs_id
group by bld."CS_ID",bld."Address_Line",bld."City",bld."Postal_Code",bld."Property_Type",bld."Price",bld."Year_Built",bld."SquareFeet",bld."Sale_Type",bg.bg_geo_id
having
    max(case when dv.sid=\'pop\' then bgd.value Else 0 END) > 0
    and max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) > 0;'
  
  building.import <- dbGetQuery(con,import.building)
  
  if(scores_or_new == 'scores'){
    building.scores <- sqldf('SELECT CS_ID, "Average Building Score", Address_Line, City, Postal_Code, Property_Type, Year_Built, Price, SquareFeet, "$ per sq ft", Sale_Type FROM "building.import" WHERE "Average Building Score" IS NOT NULL')
    return(building.scores)
  }
  if(scores_or_new == 'new'){
    building.new <- sqldf('SELECT CS_ID, "Average Building Score", Address_Line, City, Postal_Code, Property_Type, Year_Built, Price, SquareFeet, "$ per sq ft", Sale_Type FROM "building.import" WHERE "Average Building Score" IS NULL') 
    return(building.new)
  }
  if(scores_or_new == 'all'){
    building.all <- sqldf('SELECT CS_ID, "Average Building Score", Address_Line, City, Postal_Code, Property_Type, Year_Built, Price, SquareFeet, "$ per sq ft", Sale_Type FROM "building.import"') 
    return(building.all)
  }
  return("")
}

clean_building_data <- function(dataframe){
  build.scores <- dataframe
  build.scores$Score <- as.factor(build.scores$Score)
  #dummy code catigorical variables
  build.scores <- fastDummies::dummy_cols(build.scores, select_columns = "City")
  build.scores <- fastDummies::dummy_cols(build.scores, select_columns = "Postal_Code")
  build.scores <- fastDummies::dummy_cols(build.scores, select_columns = "Property_Type")
  build.scores <- fastDummies::dummy_cols(build.scores, select_columns = "Sale_Type")
  #subset the data so it does not contain any useless variables
  building.scores <- subset(building.scores, select = -c(City, Postal_Code, Property_Type, 
                                                         Year_Built, Sale_Type, Property_Type_IndustrialOfficeIndustrialLiveWorkUnit, 
                                                         `Property_Type_OfficeOfficeGeneral Retail Convenience StoreGeneral Retail RestaurantGeneral Retail Storefront Retail/OfficeOffice`, 
                                                         `Property_Type_OfficeOfficeGeneral Retail Daycare CenterGeneral Retail StorefrontGeneral Retail Storefront Retail/OfficeOffice`, 
                                                         `Sale_Type_Investment NNN`, `Sale_Type_InvestmentorOwnerUser`, Sale_Type_OwnerUser))
  #remove na's
  build.scores <- na.omit(build.scores)
  #normalize numeric variables
  build.scores$Price <- (build.scores$Price - min(build.scores$Price))/(max(build.scores$Price) - min(build.scores$Price))
  build.scores$SquareFeet <- (build.scores$SquareFeet - min(build.scores$SquareFeet))/(max(build.scores$SquareFeet) - min(build.scores$SquareFeet))
  build.scores$`$ per sq ft` <- (build.scores$`$ per sq ft` - min(build.scores$`$ per sq ft`))/(max(build.scores$`$ per sq ft`) - min(build.scores$`$ per sq ft`))
  build.scores$`Average Building Score` <- (build.scores$`Average Building Score` - min(build.scores$`Average Building Score`))/(max(build.scores$`Average Building Score`) - min(build.scores$`Average Building Score`))
  #remove duplicates
  #build.scores <- build.scores[!duplicated(build.scores[ , "Price"]),]
  #rename select columns for modeling purposes
  names(build.scores)[names(build.scores) == "$ per sq ft"] <- "price_per_sq_ft"
  names(build.scores)[names(build.scores) == "Sale_Type_Investment or Owner User"] <- "Sale_Type_Investment_or_Owner_User"
  names(build.scores)[names(build.scores) == "Sale_Type_Owner User"] <- "Sale_Type_Owner_User"
  names(build.scores)[names(build.scores) == "City_Gig Harbor"] <- "City_Gig_Harbor"
  #insert model
  set.seed(3)
  build.new.model <- neuralnet(`Average Building Score` ~ Price + SquareFeet + City_Tacoma + City_Puyallup + Property_Type_Industrial + 
                                 Property_Type_Office + Sale_Type_Investment + Sale_Type_Investment_or_Owner_User + Sale_Type_Owner_User, 
                               data = build.scores, linear.output = T, hidden = c(5,1), act.fct = "logistic")
  #extract scores and set scale 1-5
  predicted.scores <- prediction(build.new.model)
  predict.scores <- predicted.scores$rep1[,10]
  norm.predict.scores <- predict.scores * 5
  Scores.predict <- data.frame(build.scores$CS_ID, norm.predict.scores)
  
  return(Scores.predict)
}

mainfunction <- function(server, user, password, database, port){
  got_scores_data <- get_data('scores', as.character(server), as.character(user), as.character(password), as.character(database), port)
  got_new_data <- get_data('new', as.character(server), as.character(user), as.character(password), as.character(database), port)
  got_all_data <- get_data('all', as.character(server), as.character(user), as.character(password), as.character(database), port)
  clean.scores.data <- clean_building_data(got_scores_data)
  clean.new.data <- clean_building_data(got_new_data)
  clean.all.data <- clean_building_data(got_all_data)
  return(clean.bld.data)
}





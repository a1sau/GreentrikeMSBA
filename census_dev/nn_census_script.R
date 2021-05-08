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
  import.census <- 'select
     bg.bg_geo_id "Block Group ID"
     ,(select avg(bgs.score) from "BG_Score" as bgs where bgs.bg_geo_id=bg.bg_geo_id) "Average Block Group Score"
     ,max(case when dv.sid=\'pop\' then bgd.value Else 0 END) "Population"
     ,max(case when dv.sid=\'pop_MF_3MS\' then bgd.value Else 0 END) "Population: 3 Mile"
     ,max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END) "Households: 3 Mile"
    ,max(case when dv.sid=\'M_0_5\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_0_5\' then bgd.value Else 0 END) "Kids under 5"
     ,round(cast((max(case when dv.sid=\'M_0_5\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_0_5\' then bgd.value Else 0 END)) /
        max(case when dv.sid=\'pop\' then bgd.value Else null END) as numeric),3) "Percent Kids under 5"
    ,max(case when dv.sid=\'M_0_5_3MS\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_0_5_3MS\' then bgd.value Else 0 END) "Kids under 5: 3 Mile"
     ,round(cast((max(case when dv.sid=\'M_0_5_3MS\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_0_5_3MS\' then bgd.value Else 0 END)) /
        max(case when dv.sid=\'pop_MF_3MS\' then bgd.value Else null END) as numeric),3) "Percent Kids under 5: 3 Mile"
    ,max(case when dv.sid=\'M_5_9\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_5_9\' then bgd.value Else 0 END) "Kids 5 to 9"
     ,round(cast((max(case when dv.sid=\'M_5_9\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_5_9\' then bgd.value Else 0 END)) /
        max(case when dv.sid=\'pop\' then bgd.value Else null END) as numeric),3) "Percent Kids 5 to 9"
    ,max(case when dv.sid=\'M_5_9_3MS\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_5_9_3MS\' then bgd.value Else 0 END) "Kids 5 to 9: 3 Mile"
    ,round(cast((max(case when dv.sid=\'M_5_9_3MS\' then bgd.value Else 0 END)+max(case when dv.sid=\'F_5_9_3MS\' then bgd.value Else 0 END)) /
         max(case when dv.sid=\'pop_MF_3MS\' then bgd.value Else null END) as numeric),3)  "Percent Kids 5 to 9: 3 Mile"
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
  from "Block_Group" as bg
  left join "BG_Data" as bgd on bg.bg_geo_id = bgd.bg_geo_id
  inner join "Demo_Var" as dv on dv.full_variable_id=bgd.variable_id
  group by bg.bg_geo_id
  having
  max(case when dv.sid=\'pop\' then bgd.value Else 0 END) > 0
  and max(case when dv.sid=\'hi_tot_3MS\' then bgd.value Else 0 END)>0'
  
  census.import <- dbGetQuery(con,import.census)
  
  if(scores_or_new == 'scores'){
    census.df <- sqldf('SELECT "Block Group ID" AS "Block.Group.ID", "Average Block Group Score" AS "Average.Block.Group.Score", Population, 
                           "Population: 3 Mile" AS "Population.3.Mile", "Households: 3 Mile" AS "Households.3.Mile", 
                           "Percent Kids under 5" AS "Percent.Kids.under.5", "Percent Kids under 5: 3 Mile" AS "Percent.Kids.under.5.3.Mile", 
                           "Percent Kids 5 to 9" AS "Percent.Kids.5.to.9", "Percent Kids 5 to 9: 3 Mile" AS "Percent.Kids.5.to.9.3 Mile", 
                           "Average Age" AS "Average.Age", "Household income under 40K: 3 Mile" AS "Household.income.under.40K.3Mile", 
                           "Household income 40K to 50K: 3 Mile" AS "Household.income.40K.to.50K.3.Mile", 
                           "Household income 50K to 60K: 3 Mile" AS "Household.income.50K.to.60K.3.Mile", 
                           "Household income 60K to 75K: 3 Mile" AS "Household.income.60K.to.75K.3.Mile", 
                           "Household income 75K to 100K: 3 Mile" AS "Household.income.75K.to.100K.3.Mile", 
                           "Household income 100K to 125K: 3 Mile" AS "Household.income.100:.125K.3.Mile", 
                           "Household income 125K to 150K: 3 Mile" AS "Household.income.125K.to.150K.3.Mile", 
                           "Household income 150K to 200K: 3 Mile" AS "Household.income.150K.to.200K.3.Mile", 
                           "Household income 200K+: 3 Mile"  AS "Household.income.200K+.3Mile" FROM "census.import" 
                           WHERE "Average.Block.Group.Score" IS NOT NULL')
  }
  if(scores_or_new == 'new'){
    census.df <- sqldf('SELECT "Block Group ID" AS "Block.Group.ID", "Average Block Group Score" AS "Average.Block.Group.Score", Population, 
                           "Population: 3 Mile" AS "Population.3.Mile", "Households: 3 Mile" AS "Households.3.Mile", 
                           "Percent Kids under 5" AS "Percent.Kids.under.5", "Percent Kids under 5: 3 Mile" AS "Percent.Kids.under.5.3.Mile", 
                           "Percent Kids 5 to 9" AS "Percent.Kids.5.to.9", "Percent Kids 5 to 9: 3 Mile" AS "Percent.Kids.5.to.9.3 Mile", 
                           "Average Age" AS "Average.Age", "Household income under 40K: 3 Mile" AS "Household.income.under.40K.3Mile", 
                           "Household income 40K to 50K: 3 Mile" AS "Household.income.40K.to.50K.3.Mile", 
                           "Household income 50K to 60K: 3 Mile" AS "Household.income.50K.to.60K.3.Mile", 
                           "Household income 60K to 75K: 3 Mile" AS "Household.income.60K.to.75K.3.Mile", 
                           "Household income 75K to 100K: 3 Mile" AS "Household.income.75K.to.100K.3.Mile", 
                           "Household income 100K to 125K: 3 Mile" AS "Household.income.100:.125K.3.Mile", 
                           "Household income 125K to 150K: 3 Mile" AS "Household.income.125K.to.150K.3.Mile", 
                           "Household income 150K to 200K: 3 Mile" AS "Household.income.150K.to.200K.3.Mile", 
                           "Household income 200K+: 3 Mile"  AS "Household.income.200K+.3Mile" FROM "census.import" 
                           WHERE "Average.Block.Group.Score" IS NULL')
  }
  if(scores_or_new == 'all'){
    census.df <- sqldf('SELECT "Block Group ID" AS "Block.Group.ID", "Average Block Group Score" AS "Average.Block.Group.Score", Population, 
                           "Population: 3 Mile" AS "Population.3.Mile", "Households: 3 Mile" AS "Households.3.Mile", 
                           "Percent Kids under 5" AS "Percent.Kids.under.5", "Percent Kids under 5: 3 Mile" AS "Percent.Kids.under.5.3.Mile", 
                           "Percent Kids 5 to 9" AS "Percent.Kids.5.to.9", "Percent Kids 5 to 9: 3 Mile" AS "Percent.Kids.5.to.9.3 Mile", 
                           "Average Age" AS "Average.Age", "Household income under 40K: 3 Mile" AS "Household.income.under.40K.3Mile", 
                           "Household income 40K to 50K: 3 Mile" AS "Household.income.40K.to.50K.3.Mile", 
                           "Household income 50K to 60K: 3 Mile" AS "Household.income.50K.to.60K.3.Mile", 
                           "Household income 60K to 75K: 3 Mile" AS "Household.income.60K.to.75K.3.Mile", 
                           "Household income 75K to 100K: 3 Mile" AS "Household.income.75K.to.100K.3.Mile", 
                           "Household income 100K to 125K: 3 Mile" AS "Household.income.100:.125K.3.Mile", 
                           "Household income 125K to 150K: 3 Mile" AS "Household.income.125K.to.150K.3.Mile", 
                           "Household income 150K to 200K: 3 Mile" AS "Household.income.150K.to.200K.3.Mile", 
                           "Household income 200K+: 3 Mile"  AS "Household.income.200K+.3Mile"FROM "census.import"')
  }
  return(census.df)
}


clean_census_data <- function(dataframe){
  census.scores <- dataframe
  

  
  for (i in 2:length(census.scores)) {
    census.scores[i] <- min.max.norm(census.scores[i])
  }
  return(census.scores)
}

min.max.norm <- function(x) {
  return((x - min(x)) / (max(x) - min(x)))
}

nn.model.score <- function(df){
  #insert model
  set.seed(5)
  neun.cens <- neuralnet(Average.Block.Group.Score ~ Population + Population.3.Mile + Households.3.Mile + Percent.Kids.under.5 + 
                                  Percent.Kids.under.5.3.Mile + Percent.Kids.5.to.9 + Average.Age + Household.income.40K.to.50K.3.Mile + 
                                  Household.income.50K.to.60K.3.Mile + Household.income.60K.to.75K.3.Mile, data = df, linear.output = T, 
                                  hidden = c(4,1))
  #extract scores and set scale 1-5
  predicted.scores <- prediction(neun.cens,newdata=df)
  predict.scores <- predicted.scores$rep1[,11]
  norm.predict.scores <- predict.scores * 5
  Scores.predict <- data.frame(data$CS_ID, norm.predict.scores)
  return(Scores.predict)
}

nn.model.new <- function(server, user, password, database, port){
  got_scores_data <- get_data("scores", server, user, password, database, port)
  cleaned.scores.data <- clean_census_data(got_scores_data)
  #insert model
  neun.cens <- neuralnet(Average.Block.Group.Score ~ Population + Population.3.Mile + Households.3.Mile + Percent.Kids.under.5 + 
                           Percent.Kids.under.5.3.Mile + Percent.Kids.5.to.9 + Average.Age + Household.income.40K.to.50K.3.Mile + 
                           Household.income.50K.to.60K.3.Mile + Household.income.60K.to.75K.3.Mile, data = cleaned.scores.data, linear.output = T, 
                           hidden = c(4,1))
  return(neun.cens)
}

new.predictions <- function(data1, data2){
  Scores.predict.new <- predict(data1, data2, all.units = FALSE)
  return(Scores.predict.new)
}

mainfunction.scores <- function(server, user, password, database, port=5432){
  
  got_scores_data <- get_data("scores", server, user, password, database, port)
  
  clean.scores.data <- clean_census_data(got_scores_data)
  
  score.model <- nn.model(clean.scores.data)
  
  return(score.model)
}


mainfunction.new <- function(server, user, password, database, port){
  #get the data
  
  got_new_data <- get_data("new", server, user, password, database, port)
  #clean the data
  
  clean.new.data <- clean_census_data(got_new_data)
  #load in the subfunction
  
  model.new <- nn.model.new(server, user, password, database, port)
  
  #then predict with new
  
  Scores.predict.new <- new.predictions(model.new,clean.new.data) * 5
  return(Scores.predict.new)
}

mainfunction.all <- function(server, user, password, database, port=5432){
  #get the data
  print("Getting Data")
  got_all_data <- get_data("all", server, user, password, database, port)

  #clean the data
  print("Cleaning Data")
  clean.census.data <- clean_census_data(got_all_data)
  
  #load in the subfunction
  print("Building Model")
  model.all <- nn.model.new(server, user, password, database, port)
  
  #predict with scores first
  print("Predicting new results")
  Scores.predict.raw <- new.predictions(model.all, clean.census.data) * 5
  Scores.rounded<-round(Scores.predict.raw)
  Scores.rounded[Scores.rounded<1] <- 1
  Scores.rounded[Scores.rounded>5] <- 5
  df<-as.data.frame(clean.census.data$Block.Group.ID)
  df$raw_score<-as.numeric(Scores.predict.raw)
  df$score<-as.integer(Scores.rounded)
  colnames(df)<-c("bg_geo_id","raw_score","score")
  return(df)
}


library(DBI, quietly = TRUE, warn.conflicts = FALSE)
library(sqldf, quietly = TRUE, warn.conflicts = FALSE)
library(dplyr, quietly = TRUE, warn.conflicts = FALSE)
library(neuralnet, quietly = TRUE, warn.conflicts = FALSE)
library(Metrics, quietly = TRUE, warn.conflicts = FALSE)
library(caret, quietly = TRUE, warn.conflicts = FALSE)
library(config, quietly = TRUE, warn.conflicts = FALSE)
library(datapackage.r, quietly = TRUE, warn.conflicts = FALSE)
library(jsonlite, quietly = TRUE, warn.conflicts = FALSE)
library(fastDummies, quietly = TRUE, warn.conflicts = FALSE)
library(datarium, quietly = TRUE, warn.conflicts = FALSE)


get_data <- function(scores_or_new, server, user, password, database, port){
  library(odbc)
  con <- DBI::dbConnect(odbc::odbc(),
                        driver = "PostgreSQL Unicode(x64)",
                        database = as.character(database),
                        UID      = as.character(user),
                        PWD      = as.character(password),
                        server = as.character(server),
                        port = as.character(port))
  sql.building <- 'SELECT
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
    from "Building" as bld
    left join "Building_Score" as bs on bld."CS_ID" = bs.cs_id
    where bld."Sale_Lease"=\'Sale\'
    group by bld."CS_ID",bld."Address_Line",bld."City",bld."Postal_Code",bld."Property_Type",bld."Price",bld."Year_Built",bld."SquareFeet",bld."Sale_Type"'
  
  building.import <- dbGetQuery(con,sql.building)
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


clean_building_data <- function(build.scores){
  #build.scores$Score <- as.factor(build.scores$Score)
  #dummy code catigorical variables
  build.scores <- fastDummies::dummy_cols(build.scores, select_columns = "City")
  build.scores <- fastDummies::dummy_cols(build.scores, select_columns = "Postal_Code")
  build.scores <- fastDummies::dummy_cols(build.scores, select_columns = "Property_Type")
  build.scores <- fastDummies::dummy_cols(build.scores, select_columns = "Sale_Type")
  #rename select columns for modeling purposes
  names(build.scores)[names(build.scores) == "$ per sq ft"] <- "price_per_sq_ft"
  names(build.scores)[names(build.scores) == "Sale_Type_Investment or Owner User"] <- "Sale_Type_Investment_or_Owner_User"
  names(build.scores)[names(build.scores) == "Sale_Type_Owner User"] <- "Sale_Type_Owner_User"
  names(build.scores)[names(build.scores) == "City_Gig Harbor"] <- "City_Gig_Harbor"
  names(build.scores)[names(build.scores) == "Average Building Score"] <- "Average_Building_Score"
  #subset the data so it does not contain any useless variables
  building.scores <- subset(build.scores, select = c(CS_ID, Average_Building_Score, Address_Line, Price, SquareFeet, price_per_sq_ft, City_Fife, 
                                                     City_Gig_Harbor, City_Lakewood, City_Puyallup, City_Spanaway, City_Tacoma, Property_Type_Flex, 
                                                     Property_Type_Industrial, Property_Type_Office, Property_Type_Retail, Sale_Type_Investment, 
                                                     Sale_Type_Investment_or_Owner_User, Sale_Type_Owner_User, Sale_Type_OwnerUser))
  non_na <- complete.cases(building.scores[, c("Price", "SquareFeet", "price_per_sq_ft", "City_Fife", "City_Gig_Harbor", "City_Lakewood", 
                                               "City_Puyallup", "City_Spanaway", "City_Tacoma", "Property_Type_Flex", "Property_Type_Industrial", 
                                               "Property_Type_Office",         "Property_Type_Retail", "Sale_Type_Investment", 
                                               "Sale_Type_Investment_or_Owner_User", "Sale_Type_Owner_User", "Sale_Type_OwnerUser")])
  out <- building.scores[non_na, ]
  #normalize numeric variables
  out$Price <- convert_to_01(out$Price)
  out$SquareFeet <- convert_to_01(out$SquareFeet)
  out$price_per_sq_ft <- convert_to_01(out$price_per_sq_ft)
  out$Average_Building_Score <- convert_to_01(out$Average_Building_Score)
  #remove duplicates
  # out <- out[!duplicated(out[ , "Price"]),]
  
  return(out)
}

#Convert array of numbers to a range from 0 to 1
convert_to_01<-function(array,min.amt=NULL,max.amt=NULL){
  if (is.null(min.amt)){
    min.amt <- min(array)
  }
  if (is.null(max.amt)){
    max.amt<-max(array)
  }
  new.range <- (array-min.amt)/(max.amt-min.amt)
  return(new.range)
}

#Convert array of numbers from 0-1 range to full range
convert_from_01<-function(array,min.amt,max.amt){
  full.range=(array*(max.amt-min.amt))+min.amt
  return(full.range)
}

nn.model.score <- function(data){
  #insert model
  set.seed(3)
  build.new.model <- neuralnet(Average_Building_Score ~ Price + SquareFeet + City_Tacoma + City_Puyallup + Property_Type_Industrial + 
                                 Property_Type_Office + Sale_Type_Investment + Sale_Type_Investment_or_Owner_User + Sale_Type_Owner_User, 
                               data = data, linear.output = T, hidden = c(5,1), act.fct = "logistic")
  #extract scores and set scale 1-5
  predicted.scores <- prediction(build.new.model)
  predict.scores <- predicted.scores$rep1[,10]
  norm.predict.scores <- predict.scores * 5
  Scores.predict <- data.frame(data$CS_ID, norm.predict.scores)
  return(Scores.predict)
}

nn.model.new <- function(server, user, password, database, port, data){
  scores_data <- get_data("scores", server, user, password, database, port)
  cleaned.scores.data <- clean_building_data(scores_data)
  #insert model
  build.new.model <- neuralnet(Average_Building_Score ~ Price + SquareFeet + City_Tacoma + City_Puyallup + Property_Type_Industrial + 
                                 Property_Type_Office + Sale_Type_Investment + Sale_Type_Investment_or_Owner_User + Sale_Type_Owner_User, 
                               data = cleaned.scores.data, linear.output = T, hidden = c(5,1), act.fct = "logistic")
  return(build.new.model)
}

new.predictions <- function(model, data2){
  pred.scores <- convert_from_01(predict(model, newdata=data2, all.units = FALSE),1,5)
  return(pred.scores)
}

mainfunction.scores <- function(server, user, password, database, port){
  
  got_scores_data <- get_data("scores", as.character(server), as.character(user), as.character(password), as.character(database), port)
  
  clean.scores.data <- clean_building_data(got_scores_data)
  
  score.model <- nn.model(clean.scores.data)
  
  return(score.model)
}

# mainfunction.scores('greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com', 'xxx', 'xxxxxx', 'TEST', 5432)

mainfunction.new <- function(server, user, password, database, port){
  #get the data
  
  got_new_data <- get_data("new", as.character(server), as.character(user), as.character(password), as.character(database), port)
  #clean the data
  
  clean.new.data <- clean_building_data(got_new_data)
  #load in the subfunction
  
  model.new <- nn.model.new('greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com', 'xxx', 'xxxxxx', 'TEST', 5432)
  
  #then predict with new
  
  Scores.predict.new <- convert_from_01(new.predictions(model.new,clean.new.data),1,5)
  return(Scores.predict.new)
}

# mainfunction.new('greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com', 'xxx', 'xxxxxx', 'TEST', 5432)

mainfunction.all <- function(server, user, password, database, port){
  #get the data
  print("Getting Data")
  building.data <- get_data("all", server, user, password, database, port)

  #clean the data
  print("cleaning Data")
  clean.building.data <- clean_building_data(building.data)
  
  #load in the subfunction
  print("Modeling Data")
  model.all <- nn.model.new(server, user, password, database, port)
  
  #predict with scores first
  print("Predicting data")
  Scores.predict.raw <- new.predictions(model.all, clean.building.data)
  Scores.rounded<-round(Scores.predict.raw)
  Scores.rounded[Scores.rounded<1] <- 1
  Scores.rounded[Scores.rounded>5] <- 5
  df<-as.data.frame(clean.building.data$CS_ID)
  df$raw_score<-as.numeric(Scores.predict.raw)
  df$score<-as.integer(Scores.rounded)
  colnames(df)<-c("CS_ID","raw_score","score")
  return(df)
}

# df<-mainfunction.all('greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com', 'xxx', 'xxxx', 'TEST', 5432)
# print(df)
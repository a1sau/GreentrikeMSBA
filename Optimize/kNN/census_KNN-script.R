library(DBI)
library(odbc)
library(data.table)
library(caret)
library(FNN)
library(class)
library(psych)


get_data <- function(scored_or_new, server, user, password, database,model_number){
  library(odbc)
  bg.scored.3ms.raw = 'SELECT BGD.bg_geo_id, BGD.variable_id, BGD.Value, round((select avg(bgs.score) from "BG_Score" as BGS where BGS.bg_geo_id=BGD.bg_geo_id)) as score
FROM "BG_Data" BGD
RIGHT JOIN "BG_Score" BGS ON BGS.bg_geo_id = BGD.bg_geo_id
JOIN "Block_Group" BG on BGD.bg_geo_id = BG.bg_geo_id
WHERE variable_id LIKE \'%_3MS\';'
  
  bg.new.3ms.raw = 'SELECT BGD.bg_geo_id, BGD.variable_id, BGD.Value
                    FROM "BG_Data" BGD
                    LEFT JOIN "BG_Score" BGS on BGD.bg_geo_id = BGS.bg_geo_id
                    JOIN "Block_Group" BG on BGD.bg_geo_id = BG.bg_geo_id
                    WHERE BGS.bg_geo_id IS NULL AND variable_id LIKE \'%_3MS\';'
  
  con <- DBI::dbConnect(odbc::odbc(),
                        driver = "PostgreSQL Unicode(x64)",
                        database = as.character(database),
                        UID      = as.character(user),
                        PWD      = as.character(password),
                        server = as.character(server),
                        port = 5432)
  if(scored_or_new == 'scored'){
    df <- dbGetQuery(con,bg.scored.3ms.raw)
  }
  if(scored_or_new == 'new'){
    df <- dbGetQuery(con,bg.new.3ms.raw)
  }
  return (df)
}

#Create Dataframe for dynamic export
create_output <- function(predicted_values,original_dataframe, model_name){
  outscore <- as.data.frame(predicted_values)
  bg_geo_id <- original_dataframe$bg_geo_id
  model_number <- model_name
  date <- Sys.Date()
  output <- cbind(bg_geo_id, model_number, outscore, date)
  setnames(output, (c( "bg_geo_id", "model_id", "score", "date_calculated")))
  return (output)
}

reshape_census <- function(dataframe){
  if (dim(dataframe)[2] == 4){
    df <- reshape2::dcast(dataframe, bg_geo_id + score ~ variable_id, fun.aggregate = mean)
  }
  if (dim(dataframe)[2]==3){
    df<- reshape2::dcast(dataframe, bg_geo_id ~ variable_id, fun.aggregate = mean)
  }
  return(df)
}

#Clean data and normalize
norm_data <- function(dataframe){
  if(dim(dataframe)[2] == 26){
    norm.values <- caret::preProcess(dataframe[,3:dim(dataframe)[2]], method = c("center","scale"))
    dataframe[,3:dim(dataframe)[2]] <- stats::predict(norm.values, dataframe[,3:dim(dataframe)[2]])
    dataframe$score <- as.factor(dataframe$score)
  }
  if(dim(dataframe)[2] == 25){
    norm.values <- caret::preProcess(dataframe[,2:dim(dataframe)[2]], method = c("center","scale"))
    dataframe[,2:dim(dataframe)[2]] <- stats::predict(norm.values, dataframe[,2:dim(dataframe)[2]])
  } 
  return(dataframe)
}

find_best_knn <- function(train_dataframe,valid_dataframe){
  k.num = nrow(train.df)
  census.accuracy.df <- data.frame(k = seq(1, k.num, 1), accuracy = rep(0, k.num))
  # compute knn for different k on validation.
  for(i in 1:k.num) {
    knn.pred<- class::knn(train = train.df[,3:26], test = valid.df[,3:26], cl = train.df[,2],k=i)
    
    census.accuracy.df[i,2] <- confusionMatrix(knn.pred, valid.df$score)$overall[1]
  }
  return(census.accuracy.df)
}

census_KNN <- function(scored_bg, new_bg, K){
  knn.pred.new<- class::knn(train = scored_bg[,3:26], test = new_bg[,2:25], cl = scored_bg[,2],k=K)
  return(knn.pred.new)
}


##Here is where the functions are actually Used.  

#
#Get list of building that have scores for them 
bg.scored.3ms.raw <- get_data('scored',"greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com","bpope","somepassword","TEST")

bg.new.3ms.raw <- get_data('new',"greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com","bpope","somepassword","TEST")

#unmelt the data back together
bg.scored.3ms <- reshape_census(bg.scored.3ms.raw)
bg.new.3ms <- reshape_census(bg.new.3ms.raw)

#normalize the data
bg.scored.3ms.norm <- norm_data(bg.scored.3ms)
bg.new.3ms.norm <- norm_data(bg.new.3ms)

#Run the predictions
census.scores.knn <- census_KNN(bg.scored.3ms.norm,bg.new.3ms.norm,1)

#Create an output
output <-create_output(census.scores.knn, bg.new.3ms.norm, "Census_KNN_5")


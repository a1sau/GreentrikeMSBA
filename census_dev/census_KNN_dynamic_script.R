library(DBI, quietly = TRUE, warn.conflicts = FALSE)
library(odbc, quietly = TRUE, warn.conflicts = FALSE)
library(data.table, quietly = TRUE, warn.conflicts = FALSE)
library(caret, quietly = TRUE, warn.conflicts = FALSE)
library(FNN, quietly = TRUE, warn.conflicts = FALSE)
library(class, quietly = TRUE, warn.conflicts = FALSE)
library(psych, quietly = TRUE, warn.conflicts = FALSE)
#SQL query to get data frames for either "scored" or "new" block groups 
get_data <- function(scored_or_new, server, user, password, database,port=5432){
  library(odbc, quietly = TRUE, warn.conflicts = FALSE)
  bg.scored.3ms.raw ='SELECT BGD.bg_geo_id, BGD.variable_id, BGD.Value,
                      round((select avg(bgs.score) from "BG_Score" as BGS where BGS.bg_geo_id=BGD.bg_geo_id)) as score 
                      FROM "BG_Data" BGD 
                      RIGHT JOIN "BG_Score" BGS ON BGS.bg_geo_id = BGD.bg_geo_id 
                      JOIN "Block_Group" BG on BGD.bg_geo_id = BG.bg_geo_id 
                      WHERE variable_id LIKE \'%_3MS\';'
  bg.new.3ms.raw = 'SELECT BGD.bg_geo_id, BGD.variable_id, BGD.Value
                    FROM "BG_Data" BGD
                    LEFT JOIN "BG_Score" BGS on BGD.bg_geo_id = BGS.bg_geo_id
                    JOIN "Block_Group" BG on BGD.bg_geo_id = BG.bg_geo_id
                    WHERE BGS.bg_geo_id IS NULL AND variable_id LIKE \'%_3MS\';'
  bg.all.3ms.raw = 'SELECT BGD.bg_geo_id, BGD.variable_id, BGD.Value
                    FROM "BG_Data" BGD
                    LEFT JOIN "BG_Score" BGS on BGD.bg_geo_id = BGS.bg_geo_id
                    JOIN "Block_Group" BG on BGD.bg_geo_id = BG.bg_geo_id
                    WHERE variable_id LIKE \'%_3MS\';'
  con <- DBI::dbConnect(odbc::odbc(),
                        driver = "PostgreSQL Unicode(x64)",
                        database = as.character(database),
                        UID      = as.character(user),
                        PWD      = as.character(password),
                        server = as.character(server),
                        port = port)
  if(scored_or_new == 'scored'){
    df <- dbGetQuery(con,bg.scored.3ms.raw)
  }
  if(scored_or_new == 'new'){
    df <- dbGetQuery(con,bg.new.3ms.raw)
  }
  if(scored_or_new == 'all'){
    df <- dbGetQuery(con,bg.all.3ms.raw)
  }
  return (df)
}
# Uses dcast to un-melt the census data and turn it back to its horizontal format for analysis
reshape_census <- function(dataframe){
  if (dim(dataframe)[2] == 4){
    df <- reshape2::dcast(dataframe, bg_geo_id + score ~ variable_id, fun.aggregate = mean)
  }
  if (dim(dataframe)[2]==3){
    df<- reshape2::dcast(dataframe, bg_geo_id ~ variable_id, fun.aggregate = mean)
  }
  return(df)
}

#Clean census data and normalizes based on if its scored or new data
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
#function to run model on new data and create output data frame. 
census_KNN_model <- function(scored_bg, new_bg, K){
  knn.pred.new<- class::knn(train = scored_bg[,3:26], test = new_bg[,2:25], cl = scored_bg[,2],k=K)
  outscore <- as.data.frame(knn.pred.new)
  bg_geo_id <- new_bg$bg_geo_id
  model_number <- 14 #utils::capture.output(cat("for_sale_KNN_",K,sep =""))
  date <- Sys.Date()
  output <- cbind(bg_geo_id, model_number, outscore, date)
  setnames(output, (c( "bg_geo_id", "model_id", "score", "date_calculated")))
  return (output)
}

#returns a df of the accuracy associated with each K. Requires a train.df and valid.df ran through reshape_census() and norm_data()
get_accuracy<- function(train.df,valid.df){
  #TODO either 15 or half the training rows (round if divide)
  k.num = nrow(train.df)
  if (nrow(train.df) >= 30){
    k.num <- 15
  } else {
    k.num <- ceiling(nrow(train.df)/2)
  }
  build.accuracy.df <- data.frame(k = seq(1, k.num, 1), accuracy = rep(0, k.num))
  # compute knn for different k on validation.
  for(i in 1:k.num) {
    knn.pred<- class::knn(train = train.df[,3:26], test = valid.df[,3:26], cl = train.df[,2],k=i)
    build.accuracy.df[i,2] <- sum(ifelse(knn.pred==valid.df$score,1,0)) / length(knn.pred)
    # build.accuracy.df[i,2] <- confusionMatrix(knn.pred, as.factor(valid.df$score))$overall[1]##IMPORTANT NOTE## score is undercase in cencsus and Title case (Score) in building data.
  }
  return(build.accuracy.df)
}

#Takes in the scored dataset and returns the optimal value for K. This requires the function get_accuracy()
find_best_knn<- function(clean_scored_data){
  trials = 100
  t.df <- data.frame(first = rep(0,trials),second = rep(0,trials), third = rep(0,trials))
  for(i in 1:trials){
    train_index <- sample(row.names(clean_scored_data),0.7*dim(clean_scored_data)[1])
    valid_index <- setdiff(row.names(clean_scored_data), train_index)
    train.df <- clean_scored_data[train_index,]
    valid.df <- clean_scored_data[valid_index,]
    
    temp.df <-get_accuracy(train.df,valid.df)
    t.df[i,1] <- order(-temp.df$accuracy)[1]
    t.df[i,2] <- order(-temp.df$accuracy)[2]
    t.df[i,3] <- order(-temp.df$accuracy)[3]
    print(temp.df$accuracy[1])
    }
  a <-table(t.df$first)*4
  b <- table(t.df$second)*2
  n <- intersect(names(a), names(b)) 
  res <- c(a[!(names(a) %in% n)], b[!(names(b) %in% n)], a[n] + b[n])
  answer <-res[order(-res)][1]
  print(answer)

  return(as.numeric(names(answer)))
}

# Our main function to run all the sub-functions and produce a scored data frame
main_census_knn <- function(user, password, server, database,port){
  #Get the data from the database
  print("Acquiring data")
  bg.scored.3ms.raw <- get_data('scored',server,user,password,database,port)
  bg.new.3ms.raw <- get_data('all',server,user,password,database,port)
  #un-melt the data
  print("Shape Data")
  bg.scored.3ms <- reshape_census(bg.scored.3ms.raw)
  bg.new.3ms <- reshape_census(bg.new.3ms.raw)
  #normalize the data
  bg.scored.3ms.norm <- norm_data(bg.scored.3ms)
  bg.new.3ms.norm <- norm_data(bg.new.3ms)
  #Run the model on the new data and get output
  print("Scoring Data")
  census.scored.knn <- census_KNN_model(bg.scored.3ms.norm, bg.new.3ms.norm, find_best_knn(bg.scored.3ms.norm))
  return(census.scored.knn)
}

config<-read.csv('C:/Users/Lugal/OneDrive/Documents/MSBA/Project/GreentrikeMSBA/Optimize/NuralNet/Config_File.csv')
result<-main_census_knn(config$UID,config$PWD,config$server,'TEST','5432')
print(result)

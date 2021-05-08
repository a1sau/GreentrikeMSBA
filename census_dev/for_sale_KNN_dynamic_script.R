library(DBI)
library(odbc)
library(data.table)
library(caret)
library(FNN)
library(class)
library(psych)

#This creates the connection to the database and returns the query depending on if the user wants "scored" or "new" data.
get_data <- function(scored_or_new, server, user, password, database,port){
  library(odbc)
  scored_sale_buildings = 'SELECT b."CS_ID", BS."Score", b."City", b."Property_Type", b."SquareFeet", b."Price", b."Building_Class", b."Sale_Type" FROM "Building" b RIGHT JOIN "Building_Score" BS on b."CS_ID" = BS.cs_id WHERE "Sale_Lease" = \'Sale\';'
  
  new_sale_buildings = 'SELECT b."CS_ID", BS."Score", b."City", b."Property_Type", b."SquareFeet", b."Price", b."Building_Class", b."Sale_Type" FROM "Building" b LEFT JOIN "Building_Score" BS on b."CS_ID" = BS.cs_id WHERE "Sale_Lease" = \'Sale\' AND BS."Score" IS null;'
  all_sale_buildings = 'SELECT b."CS_ID", BS."Score", b."City", b."Property_Type", b."SquareFeet", b."Price", b."Building_Class", b."Sale_Type" FROM "Building" b LEFT JOIN "Building_Score" BS on b."CS_ID" = BS.cs_id WHERE "Sale_Lease" = \'Sale\';'
  con <- DBI::dbConnect(odbc::odbc(),
                        driver = "PostgreSQL Unicode(x64)",
                        database = as.character(database),
                        UID      = as.character(user),
                        PWD      = as.character(password),
                        server = as.character(server),
                        port = as.character(port))
  if(scored_or_new == 'scored'){
    df <- dbGetQuery(con,scored_sale_buildings)
  }
  if(scored_or_new == 'new'){
    df <- dbGetQuery(con,new_sale_buildings)
  }
  if(scored_or_new == 'all'){
    df <- dbGetQuery(con,all_sale_buildings)
  }
  return (df)
}
# This takes the data frame from get_data(), and cleans the categorical variables, normalizes numerical variables and standardizes the output data frame. 
clean_sale_data <- function(dataframe){
  #Look at and clean data
  build.scores <- dataframe
  build.scores$Score <- as.factor(build.scores$Score)
  #City Dummy 
  city_tacoma <- list('tacoma','university place','ruston','fircrest')
  city_puy <- list('puyallup','sumner','south hill')
  city_other <- list('City_Tacoma','City_Puyallup')
  build.scores$City <- tolower(build.scores$City)
  build.scores$City <- ifelse(build.scores$City %in% city_tacoma,'City_Tacoma',build.scores$City) #Groups together Tacoma
  build.scores$City <- ifelse(build.scores$City %in% city_puy ,'City_Puyallup',build.scores$City) #Groups together Puyallup
  build.scores$City <- ifelse(build.scores$City %in% city_other,build.scores$City, 'City_Other') # Groups together all others into "Other"
  build.scores$City<-  as.factor(build.scores$City)
  
  #Sale Type Dummy
  st_invest <-list('investment','investment nnn')
  st_owner <- list('owneruser','owner user')
  st_both <- list('investment or owner user','investmentorowneruser')
  build.scores$Sale_Type <- tolower(build.scores$Sale_Type)
  build.scores$Sale_Type <- ifelse(build.scores$Sale_Type %in% st_invest,'ST_Both',build.scores$Sale_Type)
  build.scores$Sale_Type <- ifelse(build.scores$Sale_Type %in% st_owner,'ST_Investment',build.scores$Sale_Type)
  build.scores$Sale_Type <- ifelse(build.scores$Sale_Type %in% st_both,'ST_Owner',build.scores$Sale_Type)
  build.scores$sale_Type <- as.factor(build.scores$Sale_Type)
  
  #Building Class Dummy
  build.scores$Building_Class <- tolower(build.scores$Building_Class)
  build.scores$Building_Class <- ifelse(build.scores$Building_Class == 'a','BC_A',build.scores$Building_Class)
  build.scores$Building_Class <- ifelse(build.scores$Building_Class == 'b','BC_B',build.scores$Building_Class)
  build.scores$Building_Class <- ifelse(build.scores$Building_Class == 'c','BC_C',build.scores$Building_Class)
  build.scores$Building_Class <- ifelse(build.scores$Building_Class == 'n/a','BC_Unkown',build.scores$Building_Class)
  
  #Property Type Dummy
  pt_office <- list('office')
  pt_retail <- list('retail')
  pt_other <- list('PT_Office','PT_Retail')
  build.scores$Property_Type <- tolower(build.scores$Property_Type)
  build.scores$Property_Type <- ifelse(build.scores$Property_Type %in% pt_office,'PT_Office',build.scores$Property_Type)
  build.scores$Property_Type <- ifelse(build.scores$Property_Type %in% pt_retail,'PT_Retail',build.scores$Property_Type)
  build.scores$Property_Type <- ifelse(build.scores$Property_Type %in% pt_other ,build.scores$Property_Type,'PT_Other')
  build.scores$Property_Type <- as.factor(build.scores$Property_Type)
  #create dummy columns 
  city <- as.data.frame(dummy.code(build.scores$City))
  build_class <- as.data.frame(dummy.code(build.scores$Building_Class))
  sale_type <- as.data.frame(dummy.code(build.scores$Sale_Type))
  property_type <- as.data.frame(dummy.code(build.scores$Property_Type))
  #ensure same order for columns
  city <-city[,order(names(city))]
  build_class <- build_class[,order(names(build_class))]
  sale_type <- sale_type[,order(names(sale_type))]
  property_type <- property_type[,order(names(property_type))]
  #Integer handling
  build.scores$SquareFeet <- (ifelse(is.na(build.scores$SquareFeet),0,build.scores$SquareFeet))
  build.scores$Price <- ifelse(is.na(build.scores$Price),999999999999,build.scores$Price)
  norm.values <- preProcess(build.scores[,5:6], method = c("center","scale"))
  build.scores[,5:6] <- predict(norm.values,build.scores[,5:6])
  
  #remove original and replace with dummy var.
  final_sale_df <- cbind(build.scores[,c(1:2,5:6)],city,property_type,build_class,sale_type)
  return(final_sale_df)
}

#returns a df of the accuracy associated with each K. Requires a train.df and valid.df ran through clean_sale_data()
get_accuracy<- function(train.df,valid.df){
  #TODO either 15 or half the training rows (round if divide)
  k.num = nrow(train.df)
  if (nrow(train.df) >= 30){
    k.num <- 20
  } else {
    k.num <- ceiling(nrow(train.df)/2)
  }
  build.accuracy.df <- data.frame(k = seq(1, k.num, 1), accuracy = rep(0, k.num))
  # compute knn for different k on validation.
  for(i in 1:k.num) {
    knn.pred<- class::knn(train = train.df[,3:17], test = valid.df[,3:17], cl = train.df[,2],k=i)
    
    build.accuracy.df[i,2] <- confusionMatrix(knn.pred, valid.df$Score)$overall[1]
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
  }
  a <-table(t.df$first)*4
  b <- table(t.df$second)*2
  n <- intersect(names(a), names(b)) 
  res <- c(a[!(names(a) %in% n)], b[!(names(b) %in% n)], a[n] + b[n])
  answer <-res[order(-res)][1]
  return(as.numeric(names(answer)))
}

#Run KNN on new records and get output data frame.
for_sale_KNN_model <- function(scored_buildings, new_buildings, K){
  knn.pred.new<- class::knn(train = scored_buildings[,3:17], test = new_buildings[,3:17], cl = scored_buildings[,2],k=K)
  outscore <- as.data.frame(knn.pred.new)
  cs_id <- new_buildings$CS_ID
  model_number <- 13 #utils::capture.output(cat("for_sale_KNN_",K,sep =""))
  date <- Sys.Date()
  output <- cbind(cs_id,model_number,outscore,date)
  setnames(output, (c( "CS_ID", "model_id", "score", "date_calculated")))
  return (output)
}
main_forsale_knn <- function(user, password, server, database,port=5432){ 
  #Get data frame of scored buildings 
  building.scores <- get_data('scored',as.character(server),as.character(user),as.character(password),as.character(database),port)
  #Get data frame of new buildings
  new.buildings <- get_data('all',as.character(server),as.character(user),as.character(password),as.character(database),port)
  #Clean scored buildings
  clean_scored_data <- clean_sale_data(building.scores)
  #Clean new buildings
  clean_new_data <- clean_sale_data(new.buildings)
  #Optimize best K, run model on new data, return output of scores and model information
  knn.scores <- for_sale_KNN_model(clean_scored_data, clean_new_data,find_best_knn(clean_scored_data))
  return(knn.scores)
}

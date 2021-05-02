library(DBI)
library(odbc)
library(data.table)
library(caret)
library(FNN)
library(class)
library(psych)

get_data <- function(scored_or_new, server, user, password, database,model_number){
  library(odbc)
  scored_sale_buildings = 'SELECT b."CS_ID", BS."Score", b."City", b."Property_Type", b."SquareFeet", b."Price", b."Building_Class", b."Sale_Type" FROM "Building" b RIGHT JOIN "Building_Score" BS on b."CS_ID" = BS.cs_id WHERE "Sale_Lease" = \'Sale\';'
  
  new_sale_buildings = 'SELECT b."CS_ID", BS."Score", b."City", b."Property_Type", b."SquareFeet", b."Price", b."Building_Class", b."Sale_Type" FROM "Building" b LEFT JOIN "Building_Score" BS on b."CS_ID" = BS.cs_id WHERE "Sale_Lease" = \'Sale\' AND BS."Score" IS null;'
  
  con <- DBI::dbConnect(odbc::odbc(),
                        driver = "PostgreSQL Unicode(x64)",
                        database = as.character(database),
                        UID      = as.character(user),
                        PWD      = as.character(password),
                        server = as.character(server),
                        port = 5432)
  if(scored_or_new == 'scored'){
    df <- dbGetQuery(con,scored_sale_buildings)
  }
  if(scored_or_new == 'new'){
    df <- dbGetQuery(con,new_sale_buildings)
  }
  return (df)
}

clean_sale_data <- function(dataframe){
  #Look at and clean data
  build.scores <- dataframe
  build.scores$Score <- as.factor(build.scores$Score)
  #City Dummy 
  city_tacoma <- "(Tacoma|University Place|Ruston|Fircrest)"
  city_puy <- '(Puyallup|Sumner|South hill)'
  city_other <- '(Tacoma|Puyallup)'
  build.scores$City <- ifelse(grepl(city_tacoma,build.scores$City),'City_Tacoma',build.scores$City) #Groups together Tacoma
  build.scores$City <- ifelse(grepl(city_puy,build.scores$City),'City_Puyallup',build.scores$City) #Groups together Puyallup
  build.scores$City <- ifelse(grepl(city_other,build.scores$City),build.scores$City, 'City_Other') # Groups together all others into "Other"
  build.scores$City<-  as.factor(build.scores$City)
  
  #Sale Type Dummy
  st_invest <-'(Investment|Investment NNN)'
  st_owner <- '(OwnerUser|Owner User)'
  st_both <- '(or)'
  build.scores$Sale_Type <- ifelse(grepl(st_both,build.scores$Sale_Type),'ST_Both',build.scores$Sale_Type)
  build.scores$Sale_Type <- ifelse(grepl(st_invest,build.scores$Sale_Type),'ST_Investment',build.scores$Sale_Type)
  build.scores$Sale_Type <- ifelse(grepl(st_owner,build.scores$Sale_Type),'ST_Owner',build.scores$Sale_Type)
  
  #Building Class Dummy
  build.scores$Building_Class <- ifelse(build.scores$Building_Class == 'A','BC_A',build.scores$Building_Class)
  build.scores$Building_Class <- ifelse(build.scores$Building_Class == 'B','BC_B',build.scores$Building_Class)
  build.scores$Building_Class <- ifelse(build.scores$Building_Class == 'C','BC_C',build.scores$Building_Class)
  build.scores$Building_Class <- ifelse(build.scores$Building_Class == 'N/A','BC_Unkown',build.scores$Building_Class)
  
  #Property Type Dummy
  pt_office <- 'Office|office'
  pt_retail <- 'Retail|retail'
  pt_other <- '(PT_Office|PT_Retail)'
  build.scores$Property_Type <- ifelse(grepl(pt_office,build.scores$Property_Type),'PT_Office',build.scores$Property_Type)
  build.scores$Property_Type <- ifelse(grepl(pt_retail,build.scores$Property_Type),'PT_Retail',build.scores$Property_Type)
  build.scores$Property_Type <- ifelse(grepl(pt_other,build.scores$Property_Type),build.scores$Property_Type,'PT_Other')
  
  #create dummy columns 
  city <- as.data.frame(dummy.code(build.scores$City))
  build_class <- as.data.frame(dummy.code(build.scores$Building_Class))
  sale_type <- as.data.frame(dummy.code(build.scores$Sale_Type))
  property_type <- as.data.frame(dummy.code(build.scores$Property_Type))
  
  #Integer handling
  build.scores$SquareFeet <- (ifelse(is.na(build.scores$SquareFeet),0,build.scores$SquareFeet))
  build.scores$Price <- ifelse(is.na(build.scores$Price),100000000,build.scores$Price)
  norm.values <- preProcess(build.scores[,5:6], method = c("center","scale"))
  build.scores[,5:6] <- predict(norm.values,build.scores[,5:6])
  
  #remove original and replace with dummy var.
  final_sale_df <- cbind(build.scores[,c(1:2,5:6)],city,property_type,build_class,sale_type)
  return(final_sale_df)
}
#This Takes the scored buildings data set (once standardized, normalized and cleaned) the new buildings dataset (once standardized, normalized and cleaned) and produces an output dataset with the information needed for importing to the Building_Model_Score table.
for_sale_KNN_model <- function(scored_buildings, new_buildings, K){
  knn.pred.new<- class::knn(train = scored_buildings[,3:17], test = new_buildings[,3:17], cl = scored_buildings[,2],k=K)
  outscore <- as.data.frame(knn.pred.new)
  cs_id <- new_buildings$CS_ID
  model_number <- utils::capture.output(cat("for_sale_KNN_",K,sep =""))
  date <- Sys.Date()
  output <- cbind(cs_id,model_number,outscore,date)
  setnames(output, (c( "CS_ID", "model_id", "score", "date_calculated")))
  return (output)
}

#Get list of building that have scores for them 
building.scores <- get_data('scored',"greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com","bpope","somepassword","TEST")

new.buildings <- get_data('new',"greentrike.cfvgdrxonjze.us-west-2.rds.amazonaws.com","bpope","somepassword","TEST")

clean_scored_data <- clean_sale_data(building.scores)
clean_new_data <- clean_sale_data(new.buildings)

sale_knn <- for_sale_KNN(clean_scored_data, clean_new_data, K=2)

sale_knn



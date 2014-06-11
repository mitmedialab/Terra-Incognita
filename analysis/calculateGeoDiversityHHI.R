# TODO - INCLUDE NAMIBIA

DOWNLOAD=FALSE
# Download files
# WARNING - THIS FILE TAKES REALLY LONG TO DOWNLOAD
if (DOWNLOAD){
    download.file("https://terra-incognita.co/exportgeo/", method="curl", destfile="TerraIncognitaExportGeo.csv")
}
df<-read.csv("TerraIncognitaExportGeo_06112014.csv")

#replace NA country code with NAM
#df[df$countrycode,]<-df[df$countrycode=="NAM"]

countrycodes<-read.csv("countries.csv")
countrycodes<-countrycodes$countrycode

# Set up resulting data frame
columns <- c("userID","countrycode","preinstallation.count","preinstallation.days","postinstallation.count","postinstallation.days")
result <- data.frame(t(rep(NA,length(columns))))
names(result) <- columns
result <- result[-1,]

uniqueUsers <- unique(df$userID)

# probably a way to do this without the for loops but I'm a noob
for (user in uniqueUsers){
    for (country in countrycodes){
        
        #Skip Namibia for the moment
        if (is.na(country)){
            next
        }
        resultIndex<-nrow(result)+1
        result[resultIndex,"userID"]<-user
        result[resultIndex,"countrycode"]<-country
        days<-df[(df$userID==user & !is.na(df$preinstallation.days)),"preinstallation.days"]
        
        if (length(days) != 0 && !is.na(days[[1]])){
            result[resultIndex,"preinstallation.days"]<- days[[1]]
        } else{
            result[resultIndex,"preinstallation.days"]<- 0
            print(user)
            print("HAS NO PREINSTALL DAYS")
        }
        days<-df[(df$userID==user & !is.na(df$postinstallation.days)),"postinstallation.days"]
        
        if (length(days) != 0 && !is.na(days[[1]])){
            result[resultIndex,"postinstallation.days"]<- days[[1]]
        } else{
            result[resultIndex,"postinstallation.days"]<- 0
            print(user)
            print("HAS NO POSTINSTALL DAYS")
        }
        
        # Does user have a preinstall count for this country?
        preinstallCount <- df[df$userID==user & df$countrycode==country,"preinstallation.count"]
        if (length(preinstallCount) != 0 && !is.na(preinstallCount) && !is.na(preinstallCount[[1]])){
            result[resultIndex,"preinstallation.count"]<- preinstallCount[[1]]
        } else{
            result[resultIndex,"preinstallation.count"]<- 0
        }
        # Does user have a postinstall count for this country?
        postinstallCount <- df[df$userID==user & df$countrycode==country,"postinstallation.count"]
        if (length(postinstallCount) != 0 && !is.na(postinstallCount) && !is.na(postinstallCount[[1]])){
            result[resultIndex,"postinstallation.count"]<- postinstallCount[[1]]
            
        } else{
            result[resultIndex,"postinstallation.count"]<- 0
        }
        
    }
}
result$preinstallation.normalized <-result$preinstallation.count/result$preinstallation.days
result$postinstallation.normalized <-result$postinstallation.count/result$postinstallation.days

write.csv(result,"userGeographyCounts.csv",quote=FALSE)


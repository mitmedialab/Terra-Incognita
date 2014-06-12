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
        preinstallCount <- df[df$userID==user & df$countrycode==country & !is.na(df$preinstallation.count),"preinstallation.count"]
        if (length(preinstallCount) != 0 && !is.na(preinstallCount) && !is.na(preinstallCount[[1]])){
            result[resultIndex,"preinstallation.count"]<- preinstallCount[[1]]
        } else{
            result[resultIndex,"preinstallation.count"]<- 0
        }
        # Does user have a postinstall count for this country?
        postinstallCount <- df[df$userID==user & df$countrycode==country & !is.na(df$postinstallation.count),"postinstallation.count"]
        if (length(postinstallCount) != 0 && !is.na(postinstallCount) && !is.na(postinstallCount[[1]])){
            result[resultIndex,"postinstallation.count"]<- postinstallCount[[1]]
            
        } else{
            result[resultIndex,"postinstallation.count"]<- 0
        }
        
    }
}

# normalize raw counts by days in system
result$preinstallation.normalized <-result$preinstallation.count/result$preinstallation.days
result$postinstallation.normalized <-result$postinstallation.count/result$postinstallation.days

# convert cols to numerics
result[,c("preinstallation.count","preinstallation.days","postinstallation.count","postinstallation.days","preinstallation.normalized","postinstallation.normalized")] <- as.numeric(as.character(unlist(result[,c("preinstallation.count","preinstallation.days","postinstallation.count","postinstallation.days","preinstallation.normalized","postinstallation.normalized")])))

# get individual user preinstall and postinstall normalized totals
preinstalltotals=setNames(aggregate(result$preinstallation.normalized,by=list(result$userID),FUN=sum), c("userID","normalized.total"))
postinstalltotals=setNames(aggregate(result$postinstallation.normalized,by=list(result$userID),FUN=sum), c("userID","normalized.total"))

# create columns of normalized totals by user
result$preinstallation.total=lapply(result$userID,function(x){   preinstalltotals[preinstalltotals$userID==x,"normalized.total"]})
result$postinstallation.total=lapply(result$userID,function(x){   postinstalltotals[postinstalltotals$userID==x,"normalized.total"]})

# convert cols to numerics
result[,c("preinstallation.total","postinstallation.total")] <- as.numeric(as.character(unlist(result[,c("preinstallation.total","postinstallation.total")])))

# add precent of total rows
result$preinstallation.percent <-result$preinstallation.normalized/result$preinstallation.total * 100
result$postinstallation.percent <-result$postinstallation.normalized/result$postinstallation.total * 100

# write all this to CSV
write.csv(result,"userGeographyCounts.csv",quote=FALSE)

# make a new table with userID, preinstallation.HHI, postinstallation.HHI, pre/post difference
result$preinstallation.squares=lapply(result$preinstallation.percent, function(x) { x * x})
result$postinstallation.squares=lapply(result$postinstallation.percent, function(x) { x * x})
    
preinstallation.hhi<-setNames(aggregate(unlist(result$preinstallation.squares),by=list(result$userID),FUN=sum), c("userID","hhi.preinstallation"))
postinstallation.hhi<-setNames(aggregate(unlist(result$postinstallation.squares),by=list(result$userID),FUN=sum), c("userID","hhi.postinstallation"))

hhiDF<-merge(preinstallation.hhi, postinstallation.hhi)

# convert cols to numerics
hhiDF[,c("hhi.preinstallation","hhi.postinstallation")] <- as.numeric(as.character(unlist(hhiDF[,c("hhi.preinstallation","hhi.postinstallation")])))

hhiDF$difference<-hhiDF$hhi.postinstallation-hhiDF$hhi.preinstallation
write.csv(hhiDF,"userHHI.csv",quote=FALSE)

# subset the ones whose diversity increased, THAT IS, whose HHI went DOWN because DOWN is more DIVERSE, OK? OK!
print(paste(round(nrow(hhiDF[hhiDF$difference<0,])/nrow(hhiDF)*100, 1), "% of users showed an increase in geographic diversity of newsreading after installing Terra Incognita",sep=""))
print(paste("For users who increased diversity,", round(mean(hhiDF[hhiDF$difference<0,"difference"],na.rm=TRUE), 1), "is the average amount of increased diversity on the Herfindahl–Hirschman Index scale of 1-10000 (lower = more diversity)"))
print(paste("For users who increased diversity,", round(median(hhiDF[hhiDF$difference<0,"difference"],na.rm=TRUE), 1), "is the median amount of increased diversity on the Herfindahl–Hirschman Index scale of 1-10000 (lower = more diversity)"))


library("zoo")
library("chron")
library("plyr")
library(reshape2)

# set up results that will be returned
columns <- c("userID","mean.nogeo.preinstallation","mean.geo.preinstallation","mean.nogeo.postinstallation","mean.geo.postinstallation")
result <- data.frame(t(rep(NA,length(columns))))
names(result) <- columns
result <- result[-1,]

# read in data file from /export/
df<-read.csv("TerraIncognitaExport_05252014.csv")

#remove blank userid rows
df<- df[!df$userID =="", ]

# get a list of user IDs
users <- unique(df$userID)

# probably a way to do this without the for loops but I'm a noob
for (user in users){
    
    #subset by user for the moment
    userSubset<-unique(df[df$userID==user,])
    
    # order by date
    userSubset<-userSubset[order(userSubset$datetime),]
    
    # summarize by count per day + hasGeo, presinstall
    counts<-ddply(userSubset, c("humanDate", "hasGeo","preinstallation"), function(x) c(count=nrow(x)))
    
    # Looks like this with counts broken out per day and by geo & preinstall:
    #   humanDate        hasGeo preinstallation count
    # 1  03/06/2014      0               1     1
    # 2  03/06/2014      1               1     1
    # 3  03/07/2014      0               1     3
    
    # subset into 4 groups by noGeo-preinstall, hasGeo-preinstall, nogeo-postInstall, hasGeo-postinstall
    groups <- split(counts, list(counts$hasGeo, counts$preinstallation), drop=TRUE) 
    
    resultIndex<-nrow(result)+1
    result[resultIndex,"userID"]<-user
    
    # iterate through groups, fill in missing dates and get mean over days
    for (group in groups){
        
        #convert human date to machine date
        group$humanDate<-as.POSIXct(group$humanDate,format="%m/%d/%Y")
        
        if (nrow(group) == 1){
            mean <-group$count[1]
        } else{
            # fill in any missing date counts with NA
            z <- read.zoo(group, FUN=as.POSIXct, index.column=1)
            g <- seq(start(z), end(z), by = "days")
            
            # merge data back into table
            m<-merge(z, zoo(, g))
            
            # set NA counts to 0
            m$count[is.na(m$count)] <- 0
            
            # get mean for that group
            mean <-mean(m$count)
        }
        # fill in row
        if (group$hasGeo[1]==1 & group$preinstallation[1]==1 ){
            result[resultIndex, "mean.geo.preinstallation"]=mean
        } else if(group$hasGeo[1]==0 & group$preinstallation[1]==1 ){
            result[resultIndex, "mean.nogeo.preinstallation"]=mean
        } else if (group$hasGeo[1]==1 & group$preinstallation[1]==0 ){
            result[resultIndex, "mean.geo.postinstallation"]=mean
        } else if (group$hasGeo[1]==0 & group$preinstallation[1]==0 ){
            result[resultIndex, "mean.nogeo.postinstallation"]=mean
        }
    }
}
# write means
#convert NAs to 0s
result[is.na(result)] <- 0
result$withGeoDifference <- result$mean.geo.postinstallation - result$mean.geo.preinstallation
result$withoutGeoDifference <- result$mean.nogeo.postinstallation - result$mean.nogeo.preinstallation
write.csv(result, "meanCountsByUser.csv", quote=FALSE)

#now compute summary data and save in another spreadsheet
greaterWithGeo <- result[result$withGeoDifference >1,]
greaterWithoutGeo <- result[result$withoutGeoDifference >1,]
total<- nrow(result)

df<-data.frame(label=rep("", 4),num=rep(NA, 4),stringsAsFactors=FALSE)
df[1,]<-c("Percent of users who browsed more geographically-related news stories after installing Terra Incognita",nrow(greaterWithGeo)/total*100)
df[2,]<-c("Percent of users who browsed more overall news stories without geography after installing Terra Incognita:",nrow(greaterWithoutGeo)/total*100)
df[3,]<-c("Average increase in # of geo-related news stories people read per day after installing TI", mean(result$withGeoDifference))
df[4,]<-c("Average increase in # of non-geo-related news stories people read per day after installing TI",mean(result$withGeoDifference))


print(paste("Percent of users who browsed more geographically-related news stories after installing Terra Incognita:", nrow(greaterWithGeo)/total*100,"%"))
print(paste("Percent of users who browsed more overall news stories without geography after installing Terra Incognita:", nrow(greaterWithoutGeo)/total*100,"%"))
write.csv(df, "meanCountsByUser_summary.csv", quote=FALSE)

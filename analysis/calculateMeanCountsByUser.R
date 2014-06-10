library("zoo")
library("chron")
library("plyr")
library(reshape2)

# set up results that will be returned
columns <- c("userID","days.with.data.preinstallation","days.with.data.postinstallation","urls.preinstallation","urls.postinstallation","mean.nogeo.preinstallation","mean.geo.preinstallation","mean.nogeo.postinstallation","mean.geo.postinstallation")
result <- data.frame(t(rep(NA,length(columns))))
names(result) <- columns
result <- result[-1,]

# read in data file from /export/
df<-read.csv("TerraIncognitaExport_06102014.csv")

#remove blank userid rows, remove Catherine & Matt user IDs
df<- df[!df$userID =="" & df$userID !="53401d97c183f236b23d0d40" & df$userID !="5345c2f9c183f20b81e78eec", ]

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
    
    # input the day and url counts by user
    # this is so we can verify that someone has at least 5 days of data pre- and post-installation
    # otherwise there is not a good basis to compare
    daysWithData<-ddply(userSubset, c("humanDate", "preinstallation"), function(x) c(count=nrow(x)))
    
    daysWithDataPreinstallation <- daysWithData[daysWithData$preinstallation==1,]
    daysWithDataPostinstallation <- daysWithData[daysWithData$preinstallation==0,]
    urlsPreinstallation <- sum(daysWithDataPreinstallation$count)
    urlsPostinstallation <- sum(daysWithDataPostinstallation$count)
    
    result[resultIndex,"days.with.data.preinstallation"]<-nrow(daysWithDataPreinstallation)
    result[resultIndex,"days.with.data.postinstallation"]<-nrow(daysWithDataPostinstallation)
    result[resultIndex,"urls.preinstallation"]<-urlsPreinstallation
    result[resultIndex,"urls.postinstallation"]<-urlsPostinstallation
        
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

# write CSV
write.csv(result, "meanCountsByUser.csv", quote=FALSE)

# SUMMARY STATISTICS
# now compute summary data and save in another spreadsheet
# only compute summary stats for users with MINIMUM_DAYS_OF_DATA or more days of data pre- and post-installation
MINIMUM_DAYS_OF_DATA = 5
greaterWithGeo <- result[result$withGeoDifference >0 & result$days.with.data.preinstallation >= MINIMUM_DAYS_OF_DATA & result$days.with.data.postinstallation >= MINIMUM_DAYS_OF_DATA,]
greaterWithoutGeo <- result[result$withoutGeoDifference >0 & result$days.with.data.preinstallation >= MINIMUM_DAYS_OF_DATA & result$days.with.data.postinstallation >= MINIMUM_DAYS_OF_DATA,]
total<- nrow(result[result$days.with.data.preinstallation >= MINIMUM_DAYS_OF_DATA & result$days.with.data.postinstallation >= MINIMUM_DAYS_OF_DATA,])

# Write TXT file in human readable way
fileConn<-file("meanCountsByUser_summary.txt")
line1= paste(nrow(greaterWithGeo)/total*100, "% of users browsed more geographically-related news stories after installing TI",sep="")
line2=paste(nrow(greaterWithoutGeo)/total*100, "% of users browsed more overall news stories without geography after installing TI",sep="")
line3=paste(round(mean(result[result$days.with.data.preinstallation >= MINIMUM_DAYS_OF_DATA & result$days.with.data.postinstallation >= MINIMUM_DAYS_OF_DATA,"withGeoDifference"]), digits=1 ),  " is the average increase in # of geo-related news stories people read per day after installing TI")
line4=paste(round(mean(result[result$days.with.data.preinstallation >= MINIMUM_DAYS_OF_DATA & result$days.with.data.postinstallation >= MINIMUM_DAYS_OF_DATA,"withoutGeoDifference"]), digits=1), "is the average increase in # of non-geo-related news stories people read per day after installing TI")
line5="NOTES: In these summary statistics we are filtering out user data for users who have less than 5 days in the system either pre or post installation. This could mean they did not use Chrome prior to installing the extension or else they haven't been in the system using it for more than 5 days."
line6="OTHER NOTES: In these summary statistics we are also filtering out user data for the creators of the tool (C.D'Ignazio and M. Stempeck) who are biased users."
writeLines(c(line1,line2,line3,line4,line5,line6), fileConn)
close(fileConn)

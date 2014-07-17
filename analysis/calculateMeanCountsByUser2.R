library("plyr")

# read in data file from /export/
df<-read.csv("Download_Export_07172014_DatesRevised.csv",colClasses=c("character","numeric","character",rep("numeric",4)))

# subset if userID isn't the right length (one weird val in there)
df<-df[nchar(df$userID) == nchar("538d8b62c183f2213b8864e3"),]

# make a separate table for users & pre/post install days
daysTable<-df[(df$preinstallation.days>0 & df$postinstallation.days>0 & !is.na(df$preinstallation.days) & !is.na(df$postinstallation.days)),c("userID","preinstallation.days", "postinstallation.days")]

# make a table without those vals
historyTable<-df[(is.na(df$preinstallation.days) & is.na(df$postinstallation.days)),c("userID","datetime", "humanDate","hasGeo","preinstallation")]

# group by user
# By User, sum records for hasGeo and preinstallation
userHistoryCounts <- ddply(historyTable, c("userID", "hasGeo", "preinstallation"), function(x) c(count=nrow(x)))

userIDs <- unique(userHistoryCounts$userID)

result <- daysTable

#nogeo.preinstallation
result<-merge(result,userHistoryCounts[userHistoryCounts$preinstallation==1 & userHistoryCounts$hasGeo==0,],by="userID")
names(result)[names(result)=="count"] <- "nogeo.preinstallation.count"
result<-result[c("userID","preinstallation.days","postinstallation.days", "nogeo.preinstallation.count")]

#geo.preinstallation
result<-merge(result,userHistoryCounts[userHistoryCounts$preinstallation==1 & userHistoryCounts$hasGeo==1,],by="userID")
names(result)[names(result)=="count"] <- "geo.preinstallation.count"
result<-result[c("userID","preinstallation.days","postinstallation.days", "nogeo.preinstallation.count","geo.preinstallation.count")]

#nogeo.postinstallation
result<-merge(result,userHistoryCounts[userHistoryCounts$preinstallation==0 & userHistoryCounts$hasGeo==0,],by="userID")
names(result)[names(result)=="count"] <- "nogeo.postinstallation.count"
result<-result[c("userID","preinstallation.days","postinstallation.days", "nogeo.preinstallation.count","geo.preinstallation.count","nogeo.postinstallation.count")]

#geo.postinstallation
result<-merge(result,userHistoryCounts[userHistoryCounts$preinstallation==0 & userHistoryCounts$hasGeo==1,],by="userID")
names(result)[names(result)=="count"] <- "geo.postinstallation.count"
result<-result[c("userID","preinstallation.days","postinstallation.days", "nogeo.preinstallation.count","geo.preinstallation.count","nogeo.postinstallation.count","geo.postinstallation.count")]

#normalize counts by days in system
result$nogeo.preinstallation.normalized=result$nogeo.preinstallation.count/result$preinstallation.days
result$geo.preinstallation.normalized=result$geo.preinstallation.count/result$preinstallation.days
result$nogeo.postinstallation.normalized=result$nogeo.postinstallation.count/result$postinstallation.days
result$geo.postinstallation.normalized=result$geo.postinstallation.count/result$postinstallation.days
    
#calculate difference between geo and nogeo, pre and post
result$nogeo.daily.difference=result$nogeo.postinstallation.normalized-result$nogeo.preinstallation.normalized
result$geo.daily.difference=result$geo.postinstallation.normalized-result$geo.preinstallation.normalized

print( paste(round(nrow(result[result$geo.daily.difference>0,])/nrow(result) * 100, 1), "% of users increased how much geographically related news they read after installing TI" ))
print( paste(round(nrow(result[result$nogeo.daily.difference>0,])/nrow(result) * 100, 1), "% of users increased how much news (not related to geography) they read after installing TI" ))       

print(paste("For users who increased their geographically-related news, they read on average",round(mean(result[result$geo.daily.difference>0,"geo.daily.difference"]), 1), "more articles per day after installing TI" ))
print(paste("For users who increased their non-geographically-related news, they read on average",round(mean(result[result$nogeo.daily.difference>0,"nogeo.daily.difference"]), 1), "more articles per day after installing TI" ))

print(paste("Across all users reading geographically-related news, they read on median",round(median(result[,"geo.daily.difference"]), 1), "more articles per day after installing TI" ))
print(paste("Across all users reading non-geographically-related news, they read on median",round(median(result[,"nogeo.daily.difference"]), 1), "more articles per day after installing TI" ))

write.csv(result, "meanCountsByUser.csv",quote=FALSE)
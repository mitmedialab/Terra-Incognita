library(ggplot2)
library(plyr)
DOWNLOAD=FALSE

exportClicksFile="Download_ExportClicks_07172014.csv"
totalUsersFile="Download_TotalUsers_07162014.csv"

# Download files
if (DOWNLOAD){
    download.file("https://terra-incognita.co/exportclicks/", method="curl", destfile=exportClicksFile)
    download.file("https://terra-incognita.co/totalusers/", method="curl", destfile=totalUsersFile)   
}

# Get total Users #
totalUsersDF<-read.csv(totalUsersFile)
totalUsers=totalUsersDF[1,1]

# Read in click data
df<-read.csv(exportClicksFile)

# Remove blank and null userID rows
df<- df[!df$userID =="" & !df$userID =="null", ]

# SUMMARY
# % who clicked at all
userCount<-length(unique(df$userID,))
print(paste(round(userCount/totalUsers * 100,1), "% of users have clicked on something in Terra Incognita", sep="") )

# % who clicked more than once
freqClicks=as.data.frame(table(df$userID))
moreThanOnce=nrow(freqClicks[freqClicks$Freq>1,])
print(paste(round(moreThanOnce/totalUsers * 100,1), "% of users have clicked more than once", sep=""))


# Summary clicks
print("-----------------------------------")
print(paste( round(min(freqClicks$Freq),1), "is the minimum clicks someone did"))
print(paste( round(max(freqClicks$Freq),1), "is the maximum clicks someone did"))
print(paste( round(median(freqClicks$Freq),1), "is the median clicks per user"))
print(paste( round(mean(freqClicks$Freq),1), "is the average clicks per user"))

# Group by ui_source
print("-----------------------------------")
groups=aggregate(df$userID,by=list(df$ui_source),FUN=length)
redButtonClicks=groups[groups$Group.1=="redbutton",2]
systemStoryClicks=groups[groups$Group.1=="system-story",2]
userStoryClicks=groups[groups$Group.1=="user-story",2]
totalClicks=nrow(df)

print(paste("People clicked the red button", round(redButtonClicks/totalClicks * 100, 1), "% of the time"))
print(paste("People clicked on a recommended story", round(systemStoryClicks/totalClicks * 100, 1), "% of the time"))
print(paste("People clicked on a story they had already read", round(userStoryClicks/totalClicks * 100, 1), "% of the time"))

# Group by random_city
print("-----------------------------------")
groups=aggregate(df$userID,by=list(df$random_city),FUN=length)
randomCityClicks=groups[groups$Group.1==1,2]
notRandomCityClicks=groups[groups$Group.1==0,2]

print(paste("People clicked on cities that they chose", round(notRandomCityClicks/totalClicks * 100, 1), "% of the time"))
print(paste("People clicked on cities chosen by the system", round(randomCityClicks/totalClicks * 100, 1), "% of the time"))

print("-----------------------------------")

# MAKE A BARPLOT TO SHOW INDIVIDUAL USER TOTALS FOR CLICKS
freqClicks = freqClicks[with(freqClicks, order(-Freq)), ]
png("userClicksBarplot.png",width=640, height=480)
barplot(freqClicks$Freq,ylim=c(0,100),xlab="Users", ylab="Total Clicks",main="Total Recommendations Clicked By Users",col="red")
abline(h=5,col="blue",lty=1)
text(93.5, 7, "median = 5", col = "blue") 
dev.off()

# MAKE A BARPLOT TO SHOW WHICH WAY USERS PREFERRED TO ACCESS RECS
png("userClicksPrefs.png",width=1000, height=480)
d1<-ddply(df, c("userID","ui_source"), function(x) c(count=nrow(x)))
 
ggplot(d1, aes(factor(userID), count, fill = ui_source)) + 
    geom_bar(stat="identity", position = "dodge") + coord_cartesian(ylim = c(0, 35)) + xlab("Users") + ylab("Clicks") + 
    scale_fill_brewer(palette = "Set1")
dev.off()

# SUMMARY STATS ABOUT INDIV USERS
freqSources=as.data.frame(table(d1$userID))
moreThanOnce=nrow(freqSources[freqSources$Freq>1,])
print(paste(round(moreThanOnce/totalUsers * 100,1), "% of users tried more than one way of accessing recommendations", sep=""))

# SUMMARY STATS ABOUT INDIV USER PREFS
#whittles down to what users have clicked on the most
d2 = ddply(d1, "userID", subset, count == max(count))

# still has duplicate userIDs if they were tied for clicks btw red button & jheadlines
freqSources2=as.data.frame(table(d2$userID))

# filter if they show a clear preference
usersWithPrefs = freqSources2[freqSources2$Freq==1,]
#usersWithPrefs = usersWithPrefs$userID


d3 = d2[d2$userID %in% usersWithPrefs$Var1,]
print(paste(round(nrow(d3)/totalUsers * 100,1), "% of users showed a clear preference for where they clicked", sep=""))

freqPrefs=as.data.frame(table(d3$ui_source))

# SHOW INDIVIDUAL USER FAVORITE WAY OF ACCESSING RECS
png("userClicksPrefs2.png",width=640, height=480)

barplot(freqPrefs$Freq, main="How did users prefer to get to recommendations?", xlab="UI Source", col="red", names.arg=c("Red Button", "Click on Headline", "Click on Story They Read"))
dev.off()
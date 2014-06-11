DOWNLOAD=FALSE
REMOVE_USERIDS=c("53401d97c183f236b23d0d40","5345c2f9c183f20b81e78eec")

# Download files
if (DOWNLOAD){
    download.file("https://terra-incognita.co/exportclicks/", method="curl", destfile="TerraIncognitaExportClicks.csv")
    download.file("https://terra-incognita.co/totalusers/", method="curl", destfile="TerraIncognitaTotalUsers.csv")   
}

# Get total Users #
totalUsersDF<-read.csv("TerraIncognitaTotalUsers.csv")
totalUsers=totalUsersDF[1,1]
totalUsers=totalUsers-length(REMOVE_USERIDS)

# Read in click data
df<-read.csv("TerraIncognitaExportClicks.csv")

# Remove Catherine & Matt, Remove blank and null userID rows
df<- df[!df$userID =="" & !df$userID =="null" & df$userID !="53401d97c183f236b23d0d40" & df$userID !="5345c2f9c183f20b81e78eec", ]

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
# Q: Should I filter users who only have 5 days pre and post-installation info?
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
print("NOTES: Filtering out M.Stempeck and C.D'Ignazio user IDs")
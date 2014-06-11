DOWNLOAD=TRUE
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
print(totalUsers)

# Read in click data
df<-read.csv("TerraIncognitaExportClicks.csv")

# Remove Catherine & Matt, Remove blank userID rows
df<- df[!df$userID =="" & df$userID !="53401d97c183f236b23d0d40" & df$userID !="5345c2f9c183f20b81e78eec", ]


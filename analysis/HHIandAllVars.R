library('plyr')

transnationality = read.csv("transnationality/transnationalIndices.csv")
HHI = read.csv("userHHI.csv")
presurvey=read.csv("Download_ExportPresurvey_07222014.csv")
postsurvey=read.csv("Download_PostSurvey_07222014.csv")
postsurvey=postsurvey[,c("userID","Q3globalnewsimportanttowork")]
clicks = read.csv("Download_ExportClicks_07172014.csv")

# Only HHI diffs
df = HHI
write.csv(df, "HHI.csv")

# only complete cases
presurvey=presurvey[complete.cases(presurvey),]
presurvey=presurvey[,c("userID", "Q1gender", "Q6newsreading", "Q7newsimportance")]


# MERGE HHI PRESURVEY & CLICKS
# Note - this does drop several rows where we don't have presurvey data
df = merge(df, presurvey)

# MERGE WITH CLICKS
clickCounts=count(clicks, "userID")
names(clickCounts)[names(clickCounts) == 'freq'] <- 'total.clicks'
df = merge(df, clickCounts, all.x=T)
df$total.clicks[is.na(df$total.clicks)] <- 0

# MERGE HHI TRANSNATIONALITY
transnationality = transnationality[,c("userID","transnationality.index")]

#Note - this does drop several rows where we don't have transnationality data
df = merge(df, transnationality)

write.csv(df, "HHI.Gender.NewsReading.NewsImportance.Clicks.Transnationality.csv")

# Now merge with postsurvey
# n=like 27
df = merge(df, postsurvey)
write.csv(df, "HHI.Gender.NewsReading.NewsImportance.Transnationality.NewsImportantToWork.Clicks.csv")
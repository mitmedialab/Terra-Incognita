library("ggplot2")
library("plyr")
postsurvey=read.csv("../Download_PostSurvey_07222014.csv")
presurvey=read.csv("../Download_ExportPresurvey_07222014.csv")
presurvey=presurvey[complete.cases(presurvey),]

# Bar plot of ratings frequencies
freqs = count(postsurvey, "Q4raterecommendations")
freqs = rbind(freqs, c(5,0))
png("userratings.png", width=640, height=480)
ggplot(freqs, aes(x=Q4raterecommendations, y=freq)) + geom_bar(fill="coral3",stat="identity") + 
    labs(x="Rating", y="Frequency")+ ggtitle("User ratings of Terra Incognita's Recommendations (1 = bad, 5 = good)")

dev.off()

# Bar plot of sharing frequencies
freqs = count(postsurvey, "Q8share")
png("usershares.png", width=640, height=480)
ggplot(freqs, aes(x=Q8share, y=freq)) + geom_bar(fill="darkgoldenrod3",stat="identity") + 
    labs(x="Shared", y="Frequency")+ ggtitle("User shares of TI's recommendations")

dev.off()

# Bar plot of bad articles
freqs = count(postsurvey, "Q13badarticles")
png("badarticles.png", width=640, height=480)
ggplot(freqs, aes(x=Q13badarticles, y=freq)) + geom_bar(fill="cadetblue",stat="identity") + 
    labs(x="", y="Frequency")+ ggtitle("Do you remember any bad articles you discovered from Terra Incognita?")

dev.off()

# Bar plot of good articles
freqs = count(postsurvey, "Q15goodarticles")
png("Q15goodarticles.png", width=640, height=480)
ggplot(freqs, aes(x=Q15goodarticles, y=freq)) + geom_bar(fill="chartreuse3",stat="identity") + 
    labs(x="", y="Frequency")+ ggtitle("Do you remember any good articles you discovered from Terra Incognita?")

dev.off()

# Bar plot of top reader
freqs = count(postsurvey, "Q5topreaderorrecommender")
png("Q5topreaderorrecommender.png", width=640, height=480)
ggplot(freqs, aes(x=Q5topreaderorrecommender, y=freq)) + geom_bar(fill="cornflowerblue",stat="identity") + 
    labs(x="", y="Frequency")+ ggtitle("Were you ever a top reader or recommender for a city?")

dev.off()

# Bar plot of search to become top reader
freqs = count(postsurvey, "Q6searchtobecometopreader")
png("Q6searchtobecometopreader.png", width=640, height=480)
ggplot(freqs, aes(x=Q6searchtobecometopreader, y=freq)) + geom_bar(fill="darkolivegreen",stat="identity") + 
    labs(x="", y="Frequency")+ ggtitle("Did you ever go out searching for articles so that you could be Top Reader for a city?")

dev.off()

# Bar plot of search to collect cities
freqs = count(postsurvey, "Q7searchtocollectmorecities")
png("Q7searchtocollectmorecities.png", width=640, height=480)
ggplot(freqs, aes(x=Q7searchtocollectmorecities, y=freq)) + geom_bar(fill="darkorchid3",stat="identity") + 
    labs(x="", y="Frequency")+ ggtitle("Did you ever go out searching for articles about a city in order to increment your city count?")

dev.off()

# Bar plot of would have improved rankings
freqs = count(postsurvey, "Q23seeleaderboard")
png("Q23seeleaderboard.png", width=640, height=480)
ggplot(freqs, aes(x=Q23seeleaderboard, y=freq)) + geom_bar(fill="goldenrod3",stat="identity") + 
    labs(x="", y="Frequency")+ ggtitle("Do you wish you could see a leaderboard with the top 10 users in the system?")

dev.off()

# Look at whether boys like rankings more than girls
df = merge(presurvey, postsurvey, by.x="userID", by.y="userID")
df = ddply(df, c('Q1gender','Q19improverankings'), function(x) c(count=nrow(x)))
png("genderAndRankings.png", width=640, height=480)
ggplot(df, aes(x = Q19improverankings, y = count,fill=Q1gender)) +
    geom_bar(stat='identity')+ggtitle("Do males like rankings more than females?") + labs(x="If you had known your ranking while using TI would you have tried to improve it?", y="Frequency")
dev.off()

# Look at whether boys like leaderboards more than girls
df = merge(presurvey, postsurvey, by.x="userID", by.y="userID")
df = ddply(df, c('Q1gender','Q23seeleaderboard'), function(x) c(count=nrow(x)))
png("genderAndLeaderboard.png", width=640, height=480)
ggplot(df, aes(x = Q23seeleaderboard, y = count,fill=Q1gender)) +
    geom_bar(stat='identity')+ggtitle("Do males like leaderboards more than females?") + labs(x="Do you wish you could see a leaderboard of the top 10 users?", y="Frequency")
dev.off()

## LEARNING AND REFLECTION

# Bar plot of new place
freqs = count(postsurvey, "Q11newplace")
png("Q11newplace.png", width=640, height=480)
ggplot(freqs, aes(x=Q11newplace, y=freq)) + geom_bar(fill="darkslateblue",stat="identity") + 
    labs(x="", y="Frequency")+ ggtitle("Do you feel that you learned something about a new place from using Terra Incognita?")

dev.off()

# Bar plot of reflection
freqs = count(postsurvey, "Q9reflect")
png("Q9reflect.png", width=640, height=480)
ggplot(freqs, aes(x=Q9reflect, y=freq)) + geom_bar(fill="lightblue3",stat="identity") + 
    labs(x="", y="Frequency")+ ggtitle("Did you reflect more on the geography of your news reading after you installed Terra Incognita?")

dev.off()





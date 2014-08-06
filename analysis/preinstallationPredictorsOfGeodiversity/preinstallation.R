library("ggplot2")
HHI = read.csv("../userHHI.csv")
presurvey=read.csv("../Download_ExportPresurvey_07222014.csv")
presurvey=presurvey[complete.cases(presurvey),]
presurvey=presurvey[,c("userID", "Q1gender", "Q6newsreading", "Q7newsimportance")]

#Note - this does drop several rows where we don't have presurvey data
df = merge(HHI, presurvey)

png("genderAndPreinstallationHHI.png", width=640, height=480)
qplot(df$Q1gender,df$hhi.preinstallation,  data=df, geom=c("boxplot", "jitter"), 
        fill=df$Q1gender, main="Gender and Reading Diversity",
        xlab="Gender (female, male, transgender)", ylab="HHI Prior to Installation")+
        scale_fill_manual(name = "Gender", values = c("forestgreen", "maroon"), 
        labels = c("male" = "Male (maroon)", "female" = "Female (forestgreen"))
dev.off()

png("selfReportedNewsReadingAndPreinstallationHHI.png", width=640, height=480)
medians <- ddply(df, .(Q6newsreading), summarize, med = median(hhi.preinstallation))
ggplot(df, aes(x=Q6newsreading,y=  hhi.preinstallation, fill=Q6newsreading)) + 
    geom_boxplot() + geom_text(data = medians, aes(y = med, label = round(med,2)),size = 3, vjust = -0.5)+
    scale_fill_manual(name = "Do you read a lot of global news?", values = c( "blanchedalmond", "pink","maroon"), 
    labels = c("notmuch"="Not much", 
    "mediaattention" = "Follow countries getting media attention", 
    "regularlyfollowcountries" = "Regularly follow many countries")) +
    xlab("") + ylab("HHI Preinstallation") + ggtitle("Reading Diversity and Self-reported Behavior")
dev.off()

png("newsReadingImportantAndPreinstallationHHI.png", width=640, height=480)
medians <- ddply(df, .(Q7newsimportance), summarize, med = median(hhi.preinstallation))
ggplot(df, aes(x=Q7newsimportance,y=  hhi.preinstallation, fill=Q7newsimportance)) + 
    geom_boxplot() + geom_text(data = medians, aes(y = med, label = round(med,2)),size = 3, vjust = -0.5)+
    scale_fill_manual(name = "Is reading global news important?", values = c( "blanchedalmond", "cadetblue","chocolate3"), 
                      labels = c("notreally"="Not really", 
                                 "yesbuttime" = "Yes, but I don't always have time", 
                                 "yesandeffort" = "Yes, and I make an effort to do so")) +
    xlab("") + ylab("HHI Preinstallation") + ggtitle("Reading Diversity and Attitudes towards Global News")
dev.off()


png("newsReadingImportantAndDifferenceHHI.png", width=640, height=480)
medians <- ddply(df, .(Q7newsimportance), summarize, med = median(difference))
ggplot(df, aes(x=Q7newsimportance,y=  difference, fill=Q7newsimportance)) + 
    geom_boxplot() + geom_text(data = medians, aes(y = med, label = round(med,2)),size = 3, vjust = -0.5)+
    scale_fill_manual(name = "Is reading global news important?", values = c( "blanchedalmond", "cadetblue","chocolate3"), 
                      labels = c("notreally"="Not really", 
                                 "yesbuttime" = "Yes, but I don't always have time", 
                                 "yesandeffort" = "Yes, and I make an effort to do so")) +
    xlab("") + ylab("HHI Change (lower = more diverse)") + ggtitle("Reading Diversity and Attitudes towards Global News")
dev.off()

png("selfReportedNewsReadingAndDifferenceHHI.png", width=640, height=480)
medians <- ddply(df, .(Q6newsreading), summarize, med = median(difference))
ggplot(df, aes(x=Q6newsreading,y= difference, fill=Q6newsreading)) + 
    geom_boxplot() + geom_text(data = medians, aes(y = med, label = round(med,2)),size = 3, vjust = -0.5)+
    scale_fill_manual(name = "Do you read a lot of global news?", values = c( "blanchedalmond", "pink","maroon"), 
                      labels = c("notmuch"="Not much", 
                                 "mediaattention" = "Follow countries getting media attention", 
                                 "regularlyfollowcountries" = "Regularly follow many countries")) +
    xlab("") + ylab("HHI Change (lower = more diverse)") + ggtitle("Reading Diversity and Self-reported Behavior")
dev.off()

png("genderAndDifferenceHHI.png", width=640, height=480)
medians <- ddply(df, .(Q1gender), summarize, med = median(difference))
ggplot(df, aes(x=Q1gender,y= difference, fill=Q1gender)) + 
    geom_boxplot() + geom_text(data = medians, aes(y = med, label = round(med,2)),size = 3, vjust = -0.5)+
    scale_fill_manual(name = "Gender", values = c("forestgreen", "maroon"), 
                      labels = c("male" = "Male (maroon)", "female" = "Female (forestgreen)")) +
    xlab("") + ylab("HHI Change (lower = more diverse)") + ggtitle("Gender and Change in Diversity of Reading")
dev.off()


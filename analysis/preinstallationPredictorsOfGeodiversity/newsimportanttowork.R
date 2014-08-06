library("ggplot2")
HHI = read.csv("../userHHI.csv")
postsurvey=read.csv("../Download_PostSurvey_07222014.csv")
postsurvey=postsurvey[,c("userID", "Q3globalnewsimportanttowork")]
df = merge(HHI, postsurvey)

medians <- ddply(df, .(Q3globalnewsimportanttowork), summarize, med = median(hhi.preinstallation))
png("professionalAndPreinstallationHHI.png", width=640, height=480)
ggplot(df, aes(x=Q3globalnewsimportanttowork,y=  hhi.preinstallation, fill=Q3globalnewsimportanttowork)) + 
    geom_boxplot() + geom_text(data = medians, aes(y = med, label = round(med,2)),size = 3, vjust = -0.5)+
    scale_fill_manual(name = "Is reading global news important to your job?", values = c( "blanchedalmond", "cadetblue","chocolate3", "red","purple"), 
                      labels = c("agree"="agree", 
                                 "disagree" = "disagree", 
                                 "neutral" = "neutral",
                                 "stronglydisagree" = "strongly disagree", 
                                 "stronglyagree" = "strongly agree")) +
    xlab("") + ylab("HHI Preinstallation") + ggtitle("Reading Diversity and Professional Stake in Global News")
dev.off()

medians <- ddply(df, .(Q3globalnewsimportanttowork), summarize, med = median(difference))
png("professionalAndDifferenceHHI.png", width=640, height=480)
ggplot(df, aes(x=Q3globalnewsimportanttowork,y=  difference, fill=Q3globalnewsimportanttowork)) + 
    geom_boxplot() + geom_text(data = medians, aes(y = med, label = round(med,2)),size = 3, vjust = -0.5)+
    scale_fill_manual(name = "Is reading global news important to your job?", values = c( "blanchedalmond", "cadetblue","chocolate3", "red","purple"), 
                      labels = c("agree"="agree", 
                                 "disagree" = "disagree", 
                                 "neutral" = "neutral",
                                 "stronglydisagree" = "strongly disagree", 
                                 "stronglyagree" = "strongly agree")) +
    xlab("") + ylab("HHI Change (lower = more diverse)") + ggtitle("Reading Diversity Change and Professional Stake in Global News")
dev.off()
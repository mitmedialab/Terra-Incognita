library('plyr')
df<-read.csv("Download_Export_07172014.csv",colClasses=c("character","numeric","character",rep("numeric",4)))
df<-df[df$humanDate != '',]
df$plotdate <- as.Date(df$humanDate, format="%m/%d/%Y")

# sort by highest # of days users have used TI
d1<-ddply(df[df$preinstallation==0,], c("userID","plotdate"), function(x) c(count=nrow(x)))
d1<-ddply(d1, c("userID"), function(x) c(postinstalldays=nrow(x)))
d1=d1[with(d1, order(-postinstalldays)), ]
users = d1$userID

# set up image
png("userHistograms.png", width=4320, height=6720)
par(mfrow=c(14,9))

#iterate users and make histograms
for (userID in users){
    
    print(userID)
    userDF<-df[df$userID==userID,]
    
    #weird bug where if there is only one date then it breaks so add another date
    # as a total hack
    postDates = unique(userDF$plotdate[userDF$preinstallation==0])
    if (length(postDates) == 1){
        print("hack-fixing one bug")
        userDF = rbind(userDF,c(userID,NA,NA,0,0,NA,NA,"2014-07-16"))
    }
    freqs = count(userDF, "plotdate")
    minFreq = min(freqs$freq)
    maxFreq = max(freqs$freq)
    minDate = as.Date("2014-03-25")#min(userDF$plotdate[userDF$preinstallation==1])
    maxDate = as.Date("2014-07-16")#max(userDF$plotdate[userDF$preinstallation==0])
    

    h1 = hist(userDF$plotdate[userDF$preinstallation==1],"days", ylim=c(minFreq,maxFreq), xlim=c(minDate,maxDate),axes=T,freq=T,col="red", main=userID, xlab="")   
    h2 = hist(userDF$plotdate[userDF$preinstallation==0], "days", ylim=c(minFreq,maxFreq),xlim=c(minDate,maxDate),axes=T,freq=T, col="blue",add=T)

}

dev.off()
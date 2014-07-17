library('plyr')
df<-read.csv("Download_Export_07162014.csv",colClasses=c("character","numeric","character",rep("numeric",4)))
df<-df[df$humanDate != '',]
df$plotdate <- as.Date(df$humanDate, format="%m/%d/%Y")
users = unique(df$userID)
print(length(users))
#pdf(file ="userHistograms.pdf")
png("userHistograms.png", width=1440, height=20640)
par(mfrow=c(43,3))
#count=0
for (userID in users){
    #count=count+1
    #if (count > 4){
       # break
    #}
    
   
    print(userID)
    userDF<-df[df$userID==userID,]
    postDates = unique(userDF$plotdate[userDF$preinstallation==0])
    if (length(postDates) == 1){
        print("fixing one bug")
        userDF = rbind(userDF,c(userID,NA,NA,0,0,NA,NA,"2014-07-16"))
    }
    freqs = count(userDF, "plotdate")
    minFreq = min(freqs$freq)
    maxFreq = max(freqs$freq)
    minDate = as.Date("2014-03-25")#min(userDF$plotdate[userDF$preinstallation==1])
    maxDate = as.Date("2014-07-16")#max(userDF$plotdate[userDF$preinstallation==0])
    
    #buggy1 = as.POSIXlt(paste(strftime(userDF$plotdate[userDF$preinstallation==1], format="%Y-%m-%d"), " 00:00:01"))
    #buggy1 = as.Date(buggy1)
    h1 = hist(userDF$plotdate[userDF$preinstallation==1],"days", ylim=c(minFreq,maxFreq), xlim=c(minDate,maxDate),axes=T,freq=T,col="red", main=userID, xlab="")
   
    h2 = hist(userDF$plotdate[userDF$preinstallation==0], "days", ylim=c(minFreq,maxFreq),xlim=c(minDate,maxDate),axes=T,freq=T, col="blue",add=T)
    print(userID)
}

dev.off()
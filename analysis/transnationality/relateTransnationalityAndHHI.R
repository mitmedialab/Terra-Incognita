library("ggplot2")
transnationality = read.csv("transnationalIndices.csv")
HHI = read.csv("../userHHI.csv")
transnationality = transnationality[,c("userID","transnationality.index")]

#Note - this does drop several rows where we don't have transnationality data
df = merge(HHI, transnationality)

write.csv(df,"HHITNI.csv")

png("cosmopolitanismAndReadingDiversity.png", width=640, height=640)
qplot(main="Cosmopolitanism and Reading Diversity", data = df, df$transnationality.index, df$hhi.preinstallation, xlab="Transnationality Index", ylab="HHI Preinstallation (lower = more diverse)")+ geom_smooth(method = "lm", size = 1.5) 
dev.off()

png("preinstallationHHIAndHHIChange.png", width=640, height=480)
qplot(main="Relationship between HHI Preinstallation and change in HHI after using TI", data = df, df$difference, df$hhi.preinstallation, xlab="HHI Change", ylab="HHI Preinstallation (lower = more diverse)")+ geom_smooth(method = "loess", size = 1.5) 
dev.off()

png("cosmopolitanismAndHHIChange.png", width=640, height=480)
qplot(main="Change in Reading Diversity Related to Cosmopolitanism",data = df, df$transnationality.index, df$difference,xlab="Transnationality Index", ylab="Difference in HHI pre- and post-study (lower = more diverse)")+ geom_smooth(method = "loess", size = 1.5)
dev.off()

png("cosmopolitanismAndHHIChange_zoom.png", width=640, height=480)
qplot(main="Change in Reading Diversity Related to Cosmopolitanism",data = df, df$transnationality.index, df$difference,xlab="Transnationality Index", ylab="Difference in HHI pre- and post-study (lower = more diverse)")+ geom_smooth(method = "loess", size = 1.5)+coord_cartesian(ylim = c(-2000, 2000))
dev.off()

# HHI PRE and POST INSTALLATION
png("preAndPostInstallHHI_loess.png", width=640, height=480)
qplot(main="HHI Pre and Post Installation", data = df,  df$hhi.preinstallation, df$hhi.postinstallation, xlab="HHI Preinstallation (lower = more diverse)", ylab="HHI Postinstallation (lower = more diverse)")+ geom_smooth(method = "loess", size = 1.5) + geom_abline(intercept=0, slope=1,col="red") + scale_x_continuous(breaks=c(2500,5000,7500,10000)) + scale_y_continuous(breaks=c(2500,5000,7500,10000)) + ylim(0,10000) + xlim(0,10000)
dev.off()
png("preAndPostInstallHHI_lm.png", width=640, height=480)
qplot(main="HHI Pre and Post Installation", data = df,  df$hhi.preinstallation, df$hhi.postinstallation, xlab="HHI Preinstallation (lower = more diverse)", ylab="HHI Postinstallation (lower = more diverse)")+ geom_smooth(method = "lm", size = 1.5) + geom_abline(intercept=0, slope=1,col="red") + scale_x_continuous(breaks=c(2500,5000,7500,10000)) + scale_y_continuous(breaks=c(2500,5000,7500,10000)) + ylim(0,10000) + xlim(0,10000)
dev.off()

"preinstallHHIToTNI <- lm(df$hhi.preinstallation~df$transnationality.index)
par(cex=.8)
plot(df$transnationality.index, df$hhi.preinstallation)
abline(preinstallHHIToTNI)

postinstallHHIToTNI <- lm(df$hhi.postinstallation~df$transnationality.index)
par(cex=.8)
plot(df$transnationality.index, df$hhi.postinstallation)
abline(postinstallHHIToTNI)


differenceHHIToTNI <- lm(df$difference~df$transnationality.index)
par(cex=.8)
plot(df$transnationality.index, df$difference)
abline(differenceHHIToTNI)
"
# LOESS SMOOTHER WITH BASE GRAPHICS
# plot(df$transnationality.index, df$difference,col="#999999",ylim=c(-1000,1000), xlab="Transnationality Index", ylab="Difference in HHI (lower = more diverse)")
# lines(loess.smooth(df$transnationality.index,df$difference), col="red", lty=2, lwd=2)

# LOESS WITH QPLOT
#qplot(data = df, df$transnationality.index, df$difference)+ geom_smooth(method = "loess", size = 1.5)+coord_cartesian(ylim = c(-2000, 2000))


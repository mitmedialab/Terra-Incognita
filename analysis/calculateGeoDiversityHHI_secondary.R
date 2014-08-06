# takes file from calculateGeoDiversityHHI.R and computes more stuff on it
df <- read.csv("userHHI.csv")
priorCount= nrow(df)

# TRY REMOVING PEOPLE WHO HAVE 100 OR -100 OF DIFFERENCE (ON BASIS THAT DOJ SAYS THAT DOESN'T AFFECT MARKET MUCH)
print("----------------------------------------")
print("Removed users from the analysis who show change of 100 or less. On the basis that DOJ says that that amount does not affect market concentration.")
df1 = df[df$difference>100 | df$difference< -100,]
print(paste("Removed ", round((priorCount - nrow(df1))/priorCount * 100, 1), " % of the users" ))
print(paste(round(nrow(df1[df1$difference<0,])/nrow(df1)*100, 2), "% of users showed an increase in geographic diversity of newsreading after installing Terra Incognita",sep=""))
print(paste("For users who increased diversity,", round(mean(df1[df1$difference<0,"difference"],na.rm=TRUE), 2), "is the average amount of increased diversity on the Herfindahl–Hirschman Index scale of 1-10000 (lower = more diversity)"))
print(paste("For users who increased diversity,", round(median(df1[df1$difference<0,"difference"],na.rm=TRUE), 2), "is the median amount of increased diversity on the Herfindahl–Hirschman Index scale of 1-10000 (lower = more diversity)"))


print("----------------------------------------")
# TRY ONLY LOOKING AT PEOPLE THAT START WITH 'HIGHLY CONCENTRATED' READING HABITS
print("Removed users that started with less than 2500 HHI. On the basis that DOJ says that 2500 = high market concentration. Does the tool show diffs for these least diverse people?")
df2 = df[df$hhi.preinstallation>=2500,]
print(paste("Removed ", round((priorCount - nrow(df2))/priorCount * 100, 1), " % of the users" ))
print(paste(round(nrow(df2[df2$difference<0,])/nrow(df2)*100, 2), "% of users showed an increase in geographic diversity of newsreading after installing Terra Incognita",sep=""))
print(paste("For users who increased diversity,", round(mean(df2[df2$difference<0,"difference"],na.rm=TRUE), 2), "is the average amount of increased diversity on the Herfindahl–Hirschman Index scale of 1-10000 (lower = more diversity)"))
print(paste("For users who increased diversity,", round(median(df2[df2$difference<0,"difference"],na.rm=TRUE), 2), "is the median amount of increased diversity on the Herfindahl–Hirschman Index scale of 1-10000 (lower = more diversity)"))

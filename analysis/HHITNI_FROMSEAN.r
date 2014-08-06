tidata <- read.csv("~/Desktop/HHITNI.csv")

#pre-post comparison
t.test(tidata$hhi.preinstallation,tidata$hhi.postinstallation)


#
changebyprehhi = lm(difference~hhi.preinstallation,data=tidata)
summary(changebyprehhi)

#transnationality
changebyprehhi.transnationality <- lm(difference~hhi.preinstallation+transnationality.index,data=tidata)
summary(changebyprehhi.transnationality)


prehhibytn <- lm(hhi.preinstallation~transnationality.index,data=tidata)
summary(prehhibytn)

# looks like it's significant -- and fits with how we think the world should work

## gender
hhidata <- read.csv("~/Desktop/HHI.Gender.NewsReading.NewsImportance.Clicks.Transnationality.csv")
prebygender <- lm(hhi.preinstallation~as.factor(Q1gender),data=hhidata)
changebygender <- lm(difference~as.factor(Q1gender),data=hhidata)


tidata.importance <- read.csv("~/Desktop/HHI.Gender.NewsReading.NewsImportance.Transnationality.NewsImportantToWork.Clicks.csv")

#again should probably be ordinal, but not going to look it up
changebyimportance <- lm(difference~q3num,data=tidata.importance)


## prop test for games

#yesses = c(#womenwhosaidyes,#menwhosaidyes)
#totals = c(#totalwomen,#totalmen)
#prop.test(yesses,totals)

## fill in and uncomment 

#yesses = c(#womenwhosaidyes,#menwhosaidyes)
#totals = c(#totalwomen,#totalmen)
#prop.test(yesses,totals)
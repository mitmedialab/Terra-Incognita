presurvey=read.csv("../Download_ExportPresurvey_07222014.csv")

# omit rows with no data
presurvey=presurvey[complete.cases(presurvey),]

# compute transnationality index
# 
# Private transnational Relations - 30%
# Short-term stays - 30%
# Long-term stays - 40%

presurvey$private.transnational.relations = presurvey$Q8family*0.25 + presurvey$Q9friendsabroad*0.25 + presurvey$Q10foreignfriends*0.25
presurvey$short.term.stays= ifelse(presurvey$Q11travel == 0, 0, ifelse(presurvey$Q11travel == 1 | presurvey$Q11travel == 2, 2, 3))
presurvey$long.term.stays= ifelse(presurvey$Q12liveabroad == 0, 0, ifelse(presurvey$Q12liveabroad == 1, 2, ifelse(presurvey$Q12liveabroad == 2, 4, NA)))
    
presurvey$transnationality.index = presurvey$private.transnational.relations + presurvey$short.term.stays + presurvey$long.term.stays
write.csv(presurvey, "transnationalIndices.csv")
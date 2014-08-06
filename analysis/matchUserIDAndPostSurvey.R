postsurvey=read.csv("Download_PostSurvey_07222014.csv")
userIDs=read.csv("USERIDTOHUMANREADABLE.csv")
df = merge(postsurvey, userIDs, all.x=TRUE)
write.csv(df, "postsurveyWithMatchedUserIDs.csv")
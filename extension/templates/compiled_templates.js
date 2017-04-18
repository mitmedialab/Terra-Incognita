TEMPLATES=[];
TEMPLATES['city-test-template']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n  You are trying to figure out your own code. What is up?\n';
}
return __p;
}
TEMPLATES['city-selector-template']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n  You have read about '+
((__t=( visitedCityCount ))==null?'':__t)+
' cities. Wanna go somewhere else?\n';
}
return __p;
}
TEMPLATES['login-modal-template']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n  <div id="login-modal" class="modal fade">\n    <div class="modal-dialog">\n      <div class="modal-content">\n        <div class="modal-header">\n          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>\n          <h4 class="modal-title">One-time Login</h4>\n        </div>\n        <div class="modal-body">\n          <p>You are not logged in to Terra Incognita. Please click below to login once and youll be set for awhile after that.</p>\n        </div>\n        <div class="modal-footer">\n          \n          <a role="button" class="btn btn-primary" href="'+
((__t=( loginURL ))==null?'':__t)+
'">Login Now</a>\n        </div>\n      </div>\n    </div>\n  </div>\n';
}
return __p;
}
TEMPLATES['forms-modal-template']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n  <div id="forms-modal" class="modal fade">\n    <div class="modal-dialog">\n      <div class="modal-content">\n        <div class="modal-header">\n          \n          \n          ';
 if (hasSignedConsentForm == "0") { 
__p+='\n          <h4 class="modal-title">User Consent Form</h4>\n          ';
 } else if (hasCompletedPreSurvey == "0"){ 
__p+='\n            <h4 class="modal-title">Short Pre-Study Survey</h4>\n          ';
} else if (needsToDoPostSurvey == "1") { 
__p+='\n            <h4 class="modal-title">Short Final Survey</h4>\n            ';
}
__p+='\n        </div>\n        <div class="modal-body">\n          \n          ';
 if (hasSignedConsentForm == "0") { 
__p+='\n          <p>Sorry for the interruption! You cannot use Terra Incognita until you fill out the user consent form. </p>\n          ';
 } else if (hasCompletedPreSurvey == "0"){ 
__p+='\n            <p>Sorry for the interruption! You need to fill out a short survey before using Terra Incognita. It will take about 2 minutes.</p>\n          ';
} else if (needsToDoPostSurvey == "1") { 
__p+='\n            <p>Please fill out a short, final survey about your experience with Terra Incognita. The survey will also show you your rankings.</p>\n\n            <p><em>Estimated time: 5 minutes</em></p>\n            ';
}
__p+='\n        </div>\n        <div class="modal-footer">\n          \n          <a role="button" class="btn btn-primary" href="'+
((__t=( linkURL ))==null?'':__t)+
'">Click here to complete</a>\n        </div>\n      </div>\n    </div>\n  </div>\n';
}
return __p;
}
TEMPLATES['city-zoomed-reading-lists']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='  \n        \n        <div id="city-zoomed"><h1>'+
((__t=( city_name ))==null?'':__t)+
', '+
((__t=( country_name ))==null?'':__t)+
'</h1>\n        ';
 if (population != "0") { 
__p+='\n          <p id="city-zoomed-population" class="city-stats">'+
((__t=( isCapitalCity ? "Capital City, " : "" ))==null?'':__t)+
' pop. '+
((__t=( population ))==null?'':__t)+
'</p>\n        ';
 } 
__p+='\n         \n          <div class="city-stats">            \n            ';
 if (cityStats) { 
              
__p+='\n               <div id="top-reader">\n                \n                ';
 if (!_.isEmpty(cityStats.get("mostRead")) ) { 
__p+='\n                  <p><span style="text-transform:uppercase">Top Reader</span>: '+
((__t=( cityStats.get("mostRead")["username"] ))==null?'':__t)+
' \n                  ';
 if (cityStats.get("mostRead")["isCurrentUser"] == "true"){
__p+=' - YOU! ';
 } 
__p+='('+
((__t=( cityStats.get("mostRead")["count"] ))==null?'':__t)+
')\n                  </p>\n                ';
 } 
__p+='\n\n                \n                  </div>\n        \n                <div id="top-recommender">\n                \n\n                \n\n                ';
 if (!_.isEmpty(cityStats.get("mostRecommendations")) ) { 
__p+='\n                  <p><span style="text-transform:uppercase">Top Recommender</span>: '+
((__t=( cityStats.get("mostRecommendations")["username"] ))==null?'':__t)+
' \n                  ';
 if (cityStats.get("mostRecommendations")["isCurrentUser"] == "true"){
__p+=' - YOU!';
 } 
__p+=' ('+
((__t=( cityStats.get("mostRecommendations")["count"]))==null?'':__t)+
')\n                ';
 } 
__p+='\n                </p>\n                  \n                 \n                     \n                  \n                </div>\n            ';
 } 
__p+='\n            </div>\n            <div id="go-now">\n                <a href="'+
((__t=( serverURL ))==null?'':__t)+
'go/'+
((__t=( userID ))==null?'':__t)+
'/'+
((__t=( cityID ))==null?'':__t)+
'?r='+
((__t=( isRandomCity ))==null?'':__t)+
'" role="button" class="btn btn-lg btn-danger btn-go">'+
((__t=( randomSaying ))==null?'':__t)+
'</a>\n                \n            </div> \n            <!--<img src="../img/hr.png">-->\n            <div id="what-people-read">\n              ';
 if (systemStories && systemStories.size() > 0) { 
__p+='\n              <div id="what-others-read">\n                <table class="table table-condensed">\n                  <thead>\n                        <tr>\n                          <th>'+
((__t=(systemStories.size() == 1 ? "1" : (systemStories.size() >= 5 ? "5" : systemStories.size() )))==null?'':__t)+
' Things to Read \n                              ';
 if (systemStories.size() > 5) { 
__p+='\n                              (<a href="#" class="show-all-system-stories">'+
((__t=( "See all " + systemStories.size()  ))==null?'':__t)+
'</a>)\n                              ';
 } 
__p+='\n                          </th>\n                        </tr>\n                      </thead>\n                    <tbody>\n\n                    \n                      ';
 if (systemStories) { 
                        var count = 1;
                        systemStories.each(function(story){ 
                          

                        rec = story.get('recommended');
                            hasBeenReviewed = (rec != null);
                            isThumbsUp = false;
                            if (hasBeenReviewed){
                              if (rec == 1){
                                isThumbsUp = true;
                              } else{
                                isThumbsUp = false;
                              }
                            }
                            
                          
__p+='\n                        <tr class="system-story-row" style="'+
((__t=( count > 5 ? 'display:none' : '' ))==null?'':__t)+
'"><td>';
 if (isThumbsUp) {
__p+='<span class="glyphicon glyphicon-thumbs-up"></span>';
}
__p+='<a class="system-story" href="'+
((__t=(story.get('url')))==null?'':__t)+
'">'+
((__t=(story.get('title') == "" ? story.get('url').slice(0,40) + "..." : story.get('title') ))==null?'':__t)+
'</a></td></tr>\n                    ';
 
                        count++;

                      });
                      } 
__p+='\n                    </tbody>\n                </table> \n              </div> \n              ';
 } 
__p+='\n\n              ';
 if (userStories && userStories.size() > 0) { 
__p+='\n              <div id="what-you-read">\n                <table class="table table-condensed">\n                  <thead>\n                        <tr>\n                          <th>What You Read ('+
((__t=(userStories.size()))==null?'':__t)+
')</th>\n                        </tr>\n                      </thead>\n                    <tbody>\n                       ';
 if (userStories) { 
                        userStories.each(function(story){ 
                            rec = story.get('recommended');
                            hasBeenReviewed = (rec != null);
                            if (hasBeenReviewed){
                              if (rec == 1){
                                isThumbsUp = true;
                              } else{
                                isThumbsUp = false;
                              }
                            }
                          
__p+='\n                        <tr><td><a href="'+
((__t=(story.get('url')))==null?'':__t)+
'" title="I recommend this!"><span class="glyphicon glyphicon-thumbs-up '+
((__t=( hasBeenReviewed ? ( isThumbsUp ? 'glyphicon-chosen' : 'glyphicon-unchosen') : '' ))==null?'':__t)+
'"></span></a> <a href="'+
((__t=(story.get('url')))==null?'':__t)+
'" title="I do not recommend this!"><span class="glyphicon glyphicon-thumbs-down '+
((__t=( hasBeenReviewed ? ( isThumbsUp ? 'glyphicon-unchosen' : 'glyphicon-chosen') : '' ))==null?'':__t)+
' " style="padding-right:10px"></span></a> <a class="user-story" href="'+
((__t=(story.get('url')))==null?'':__t)+
'">'+
((__t=(story.get('title') == "" ? story.get('url').slice(0,40) + "..." : story.get('title') ))==null?'':__t)+
'</a></td></tr>\n                    ';
 }); 
                      } 
__p+='\n                    </tbody>\n                </table>  \n              </div>\n              ';
 } 
__p+='\n              </div>\n             ';
 if (userStories && userStories.size() > 5) { 
__p+='\n              <h4 class="submit-recommendation">Submit a recommendation about '+
((__t=( city_name ))==null?'':__t)+
'</h4>\n              <form class="form-inline" role="form" style="margin-bottom:20px;text-align:left">\n                <div class="form-group">\n                  <input style="min-width:200px" type="url" class="form-control" id="url_recommendation" placeholder="http://www.'+
((__t=( randomWord ))==null?'':__t)+
'.com">\n                </div>\n                <button type="submit" class="btn btn-default">Submit</button>\n              </form>\n            ';
 } 
__p+='\n          </div>\n        \n\n\n        </div>\n        \n        \n';
}
return __p;
}
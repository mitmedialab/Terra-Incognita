TEMPLATES=[];
TEMPLATES['login-modal-template']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n  <div id="login-modal" class="modal fade">\n    <div class="modal-dialog">\n      <div class="modal-content">\n        <div class="modal-header">\n          <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>\n          <h4 class="modal-title">One-time Login</h4>\n        </div>\n        <div class="modal-body">\n          <p>You are not logged in to Terra Incognita. Please click below to login once and youll be set for awhile after that.</p>\n        </div>\n        <div class="modal-footer">\n          \n          <a role="button" class="btn btn-primary" href="'+
((__t=( loginURL ))==null?'':__t)+
'">Login Now</a>\n        </div>\n      </div>\n    </div>\n  </div>\n';
}
return __p;
}
TEMPLATES['city-zoomed-reading-lists']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='  \n        <div id="city-zoomed"><h1>'+
((__t=( city_name ))==null?'':__t)+
', '+
((__t=( country_name ))==null?'':__t)+
'</h1>\n        ';
 if (population != "0") { 
__p+='\n          <p id="city-zoomed-population" class="city-stats">pop. '+
((__t=( population ))==null?'':__t)+
'</p>\n        ';
 } 
__p+='\n        <div class="city-stats">\n          <p><strong>erhardt</strong>: First Reader</p>\n          <p><strong>stempeck</strong>: First Recommender</p>\n          \n          <p><strong>kanarinka</strong>: Top Scholar of '+
((__t=( city_name ))==null?'':__t)+
'</p>\n          \n\n          <p><strong>ethanz</strong>: Top Recommender of '+
((__t=( city_name ))==null?'':__t)+
'</p>\n          <br/>\n          <br/>\n          <p><em>Read 4 more articles to be the Top Scholar</em></p>\n          <p><em>Recommend 1 more article to be the Top Recommender</em></p>\n          <h5 style="margin-top:20px">Submit a recommendation about '+
((__t=( city_name ))==null?'':__t)+
'</h5>\n          <form class="form-inline" role="form">\n            <div class="form-group">\n              <input type="email" class="form-control" id="url_recommendation" placeholder="http://www.yoururlgoeshere.com">\n            </div>\n            <button type="submit" class="btn btn-default">Submit</button>\n          </form>\n        </div>\n        </div>\n        <div id="go-now">\n              <div style="position: relative; left: -50%;">\n                  <a href="http://localhost:5000/go/'+
((__t=( cityID ))==null?'':__t)+
'" role="button" class="btn btn-lg btn-danger btn-go">Read About '+
((__t=( city_name ))==null?'':__t)+
'</a></th>\n              </div>\n        </div> \n        <div id="what-people-read">\n        ';
 if (systemStories && systemStories.size() > 0) { 
__p+='\n        <div id="what-others-read">\n          <table class="table table-condensed">\n            <thead>\n                  <tr>\n                    <th>What Others Are Reading About '+
((__t=( city_name ))==null?'':__t)+
'</th>\n                  </tr>\n                </thead>\n              <tbody>\n                ';
 if (systemStories) { 
                  systemStories.each(function(story){ 
__p+='\n                  <tr><td><a href="'+
((__t=(story.get('url')))==null?'':__t)+
'">'+
((__t=(story.get('title')))==null?'':__t)+
'</a></td></tr>\n              ';
 });
                } 
__p+='\n              </tbody>\n          </table> \n        </div> \n        ';
 } 
__p+='\n        ';
 if (userStories && userStories.size() > 0) { 
__p+='\n        <div id="what-you-read">\n          <table class="table table-condensed">\n            <thead>\n                  <tr>\n                    <th>What You Read About '+
((__t=( city_name ))==null?'':__t)+
'</th>\n                  </tr>\n                </thead>\n              <tbody>\n                 ';
 if (userStories) { 
                  userStories.each(function(story){ 
__p+='\n                  <tr><td><a href="'+
((__t=(story.get('url')))==null?'':__t)+
'">'+
((__t=(story.get('title')))==null?'':__t)+
'</a></td></tr>\n              ';
 }); 
                } 
__p+='\n              </tbody>\n          </table>  \n        </div>\n        ';
 } 
__p+='\n        </div>\n';
}
return __p;
} 
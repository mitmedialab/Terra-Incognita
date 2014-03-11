TEMPLATES=[];
TEMPLATES['city-zoomed-reading-lists']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='  \n        <div id="city-zoomed"><h1>'+
((__t=( city_name ))==null?'':__t)+
', '+
((__t=( country_name ))==null?'':__t)+
'</h1>\n        <div style="font-size:12px;line-height:10px">\n          <p><strong>erhardt</strong>: First Reader</p>\n          <p><strong>stempeck</strong>: First Recommender</p>\n          \n          <p><strong>kanarinka</strong>: Top Scholar of Kayes</p>\n          \n\n          <p><strong>ethanz</strong>: Top Recommender of Kayes</p>\n          <br/>\n          <br/>\n          <p><em>Read 4 more articles to be the Top Scholar</em></p>\n          <p><em>Recommend 1 more article to be the Top Recommender</em></p>\n        </div>\n        </div>\n        <div id="go-now" style="position: absolute; left: 50%; top:35%;">\n              <div style="position: relative; left: -50%;">\n                  <a href="http://localhost:5000/go/'+
((__t=( city_name ))==null?'':__t)+
' '+
((__t=( country_name ))==null?'':__t)+
'"><img src="img/gobutton.png" target="_blank"></a></th>\n              </div>\n        </div> \n        <div id="what-others-read">\n          <table class="table table-condensed">\n            <thead>\n                  <tr>\n                    <th>What Others Are Reading About '+
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
__p+='\n              </tbody>\n          </table> \n        </div> \n        <div id="what-you-read">\n          <table class="table table-condensed">\n            <thead>\n                  <tr>\n                    <th>What You Read About '+
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
__p+='\n              </tbody>\n          </table>  \n        </div>\n';
}
return __p;
} 
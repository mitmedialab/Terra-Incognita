TEMPLATES=[];
TEMPLATES['geo-incognita-view']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n    <td><a target=\'_blank\' href=\'http://localhost:5000/go/'+
((__t=( name ))==null?'':__t)+
'\'>'+
((__t=( name ))==null?'':__t)+
'</a></td>\n';
}
return __p;
}
TEMPLATES['geo-cognita-view']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n    <td>'+
((__t=( name ))==null?'':__t)+
'</td><td>'+
((__t=( name ))==null?'':__t)+
'</td>\n';
}
return __p;
}
TEMPLATES['incognita-table']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n<table style="width:18%;float:left;border-right:1px solid gray;border-left:1px solid gray;margin:0 5px 0 5px" class="table table-striped table-condensed">\n  <thead>\n      <tr>\n        <th>'+
((__t=( title ))==null?'':__t)+
'</th>\n      </tr>\n   </thead>\n</table>\n';
}
return __p;
}
TEMPLATES['cognita-table']=function(obj){
var __t,__p='',__j=Array.prototype.join,print=function(){__p+=__j.call(arguments,'');};
with(obj||{}){
__p+='\n<table style="width:18%;float:left;border-right:1px solid gray;border-left:1px solid gray;margin:0 5px 0 5px" class="table table-striped table-condensed">\n  <thead>\n      <tr>\n        <th>'+
((__t=( title ))==null?'':__t)+
'</th>\n        <th>Count</th>\n      </tr>\n   </thead>\n</table>\n';
}
return __p;
} 
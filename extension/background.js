// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Called when the user clicks on the browser action.
/*chrome.browserAction.onClicked.addListener(function(tab) {
  // No tabs or host permissions needed!
  console.log('Turning ' + tab.url + ' red!');
  chrome.tabs.executeScript({
    code: 'document.body.style.backgroundColor="red"'
  });
});
*/
var urlMap = new Array();
var serverURL = "http://dhcp-18-111-26-19.dyn.mit.edu:5000/";
var daysHistory = 30;
/*
  Stuff to do right when app is installed:
  - Get 30 days of browser history & send to server
  - mark the data as history i.e. "not using the extension"
  - save metadata and URLs
*/
chrome.runtime.onInstalled.addListener(function(details) {
  console.log("on installed");
  var today = new Date();
  var startCollecting = today.getTime() - daysHistory*24*60*60*1000;
  chrome.history.search({text: '', startTime:startCollecting, maxResults:1000000000}, function(results) 
    { 
      console.log("logging " + daysHistory + " days browsing history"); 
      console.log(results.length + " results");
      postData('history/', 'history', results);
    });

});

/*
  Experiment with downloading JSON data from server if there were map data ready
*/
chrome.tabs.onCreated.addListener(function(tab) {
  console.log('New tab created');
  var xhr = new XMLHttpRequest();
  xhr.open("GET",serverURL + 'map.json', true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      // JSON.parse does not evaluate the attacker's scripts.
      var resp = JSON.parse(xhr.responseText);
      console.log(resp);
    }
  }
  xhr.send();
});

/*
  Tab changes or new tab 
*/
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
        
    if (changeInfo.status == "loading" && changeInfo.url != "undefined"){
            urlMap[tabId] = true;
    }
    else if (urlMap[tabId] && changeInfo.status == "complete"){
            urlMap[tabId] = false;
           // chrome.tts.speak('I just got your url. hahahahaha',{'enqueue': true, 'gender':'female','lang':'en-US'});
            //retrieve latest URL from history so we get the metadata
            chrome.history.search({text: '', maxResults:1}, function(results) 
            { 
              
              if (tab.url == results[0].url){
                postData('monitor/', 'logURL', results[0]);

              }
            });
    }
});

/*
  Handles post requests to server
*/
function postData(routeName, paramName, data){
  console.log("Route: " + routeName);
  var json = JSON.stringify(data);
  var http = new XMLHttpRequest();
  var params = paramName+"="+encodeURIComponent(json);

  http.open("POST", serverURL + routeName, false);
  http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

  http.onreadystatechange = function() {
      if(http.readyState == 4 && http.status == 200) {
          console.log(http.responseText);
      }
  };
  http.send(params);
}

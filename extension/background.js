// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var urlMap = [];
var tabToCityMap ={};

function checkLoggedIn(callback){
	chrome.cookies.get({ url: COOKIE_PATH, name: USER_COOKIE },
			function (cookie) {
				if (cookie) {
						console.log("user logged in");
						IS_LOGGED_IN = true;
						USER_ID = cookie.value;
						
				}else{
					console.log("user not logged in");
					IS_LOGGED_IN = false;
					USER_ID = null;
					
				}
				callback();
		});
	
}
function initBackground(){
	if (DEBUG) {console.log("initBackground");}
	checkLoggedIn(function(){console.log("initBackground::checkLoggedIn: " + IS_LOGGED_IN)});
}
initBackground();

/*
	Listens for pages sending stuff
*/
chrome.runtime.onMessage.addListener(
	function(request, sender, sendResponse)
	{
		if (request.msg == "checkLoggedIn")
		{
				checkLoggedIn( function(){
					sendResponse({isLoggedIn: IS_LOGGED_IN, loginURL : SERVER_URL + LOGIN_PAGE, userID : USER_ID});
				});
				return true;
		}
		
		else if (request.msg == "loadReadingLists")
		{
				var xhr = new XMLHttpRequest();
				
				xhr.open("GET",SERVER_URL + 'readinglist/' + USER_ID + '/' + request.city_id, true);
				
				xhr.onreadystatechange = function() {
					if (xhr.readyState == 4) {
						
						readingListJSON = JSON.parse(xhr.responseText);
						console.log(readingListJSON);
						sendResponse({readingLists: readingListJSON});
					}
				}
				xhr.send();
				return true;
		}
		else if (request.msg == "loadCityStats")
		{
				var xhr = new XMLHttpRequest();
				
				xhr.open("GET",SERVER_URL + 'citystats/' + USER_ID + '/' + request.city_id, true);
				
				xhr.onreadystatechange = function() {
					if (xhr.readyState == 4) {
						
						cityStatsJSON = JSON.parse(xhr.responseText);
						console.log(cityStatsJSON);
						sendResponse({cityStats: cityStatsJSON});
					}
				}
				xhr.send();
				return true;
		}
		else if (request.msg == "submitRecommendation")
		{
				var xhr = new XMLHttpRequest();
				
				xhr.open("GET",SERVER_URL + 'recommend/' + USER_ID + '/' + request.city_id +'?url=' + request.url, true);
				
				xhr.onreadystatechange = function() {
					if (xhr.readyState == 4) {
						
						resultJSON = JSON.parse(xhr.responseText);
						console.log(resultJSON);
						sendResponse({result: resultJSON});
					}
				}
				xhr.send();
				return true;
		}
		else if (request.msg == "logCityClick")
		{
				var xhr = new XMLHttpRequest();
				
				xhr.open("GET",SERVER_URL + 'logcityclick/' + USER_ID + '/' + request.city_id, true);
				
				xhr.onreadystatechange = function() {
					if (xhr.readyState == 4) {
						
						resultJSON = JSON.parse(xhr.responseText);
						console.log(resultJSON);
						sendResponse({result: resultJSON});
					}
				}
				xhr.send();
				return true;
		}
		else if (request.msg == "logStoryClick")
		{
				var params = {"ui_source" : request.ui_source, "url" : request.url, "isRandomCity" : request.isRandomCity };
				postData('logstoryclick/' + USER_ID + '/' + request.city_id, params, function(response){
																resultJSON = JSON.parse(response);
																console.log(resultJSON);
																sendResponse({result: resultJSON});
															});
				
				return true;

		}
		else if (request.msg == "submitHistoryItemRecommendation")
		{
				var params = {"isThumbsUp" : request.isThumbsUp, "url" : request.url};
				postData('like/' + USER_ID + '/' + request.city_id, params, function(response){
																resultJSON = JSON.parse(response);
																console.log(resultJSON);
																sendResponse({result: resultJSON});
															});
				
				return true;
		}
		else if (request.msg == "saveCityFromTab")
		{
				console.log("saveCityFromTab")
				var cityID = request.cityID;
				var isRandomCity = request.isRandomCity;
				var tabID = sender.tab.id;
				console.log("city ID is " + cityID)
				console.log("tab ID is " + tabID)
				console.log("isRandomCity is " + isRandomCity)
				tabToCityMap[tabID]= {"cityID":cityID,"isRandomCity":isRandomCity};
				sendResponse({status: "ok"});
				return true;
		}
		else if (request.msg == "checkForCityInTab")
		{	
				var cityID = "";
				var tabID = sender.tab.id;
				if (tabID in tabToCityMap){
					console.log("THERE SHOULD BE A CITY LOADED IN TAB ALREADY")
					cityID = tabToCityMap[sender.tab.id]["cityID"];
					isRandomCity = tabToCityMap[sender.tab.id]["isRandomCity"];
				}
				sendResponse({cityID: cityID, isRandomCity:isRandomCity});
				return true;
		}
	}
);
/*
	Stuff to do right when app is installed:
	- Get 30 days of browser history, filter to see which URLs to keep & send to server
	- store in localStorage until they have a userID
*/
chrome.runtime.onInstalled.addListener(function(details) {
	if (DEBUG) {console.log("onInstalled");}
	
	chrome.storage.local.get("terraIncognitaUserHistory", 
			function(result){
				if ("terraIncognitaUserHistory" in result){
					var val = result["terraIncognitaUserHistory"]
					console.log("terraIncognitaUserHistory" + " is " + val)
					console.log("User pre-installation history has already been saved.")
				} else{
					
					console.log("Launching new tab because they installed TI for the first time")
					chrome.tabs.create({
					    url: 'chrome://newtab'
					});
					console.log("Saving user pre-installation history.")
					var today = new Date();
					var startCollecting = today.getTime() - DAYS_HISTORY*24*60*60*1000;
					filteredResults = [];

					chrome.history.search({text: '', startTime:startCollecting, maxResults:1000000000}, function(results) 
						{ 
							
							console.log("logging " + DAYS_HISTORY + " days browsing history"); 
							
							for (var i = 0;i<results.length;i++){
								var result = results[i];
								if (keepURL(result.url)){
									filteredResults.push(result);
								}
							}
							console.log(filteredResults.length + " results after filtering");
							chrome.storage.local.set({"terraIncognitaUserHistory":filteredResults});
						});
					
					
				}
			});

	
	
});


/*
	Launch app on new tab
*/
chrome.tabs.onCreated.addListener(function(tab) {
	console.log('New tab created');

	if (USER_ID != null){

		/*
			Check if we should send their prior browsing history or if we've already done that
		*/
		chrome.storage.local.get("terraIncognitaUserHistory", 
												function(result){
													if ("terraIncognitaUserHistory" in result){
														var val = result["terraIncognitaUserHistory"]
														if (val != "done"){
															console.log("Posting history data to the server")
															postData('history/' + USER_ID + '/', {"history":JSON.stringify(val)}, function(){
																chrome.storage.local.set({"terraIncognitaUserHistory":"done"});
															});
															
														}
													} 
												});
		
		/*
			Then get user information like cities visited, etc
		*/
		var xhr = new XMLHttpRequest();
		xhr.open("GET",SERVER_URL + 'user/' + USER_ID, true);
		xhr.onreadystatechange = function() {
			if (xhr.readyState == 4) {
				
				USER_JSON = JSON.parse(xhr.responseText);
				console.log(USER_JSON);

				chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
				  chrome.tabs.sendMessage(tabs[0].id, {user: USER_JSON}, function(response) {
				    console.log(response);
				  });
				});
			}
		}
		xhr.send();
	}
	
});

/*
	Tab changes or new tab 
*/
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
		console.log("onUpdated")
		if (changeInfo.status == "loading" && changeInfo.url != "undefined"){
						urlMap[tabId] = true;
		}
		else if (urlMap[tabId] && changeInfo.status == "complete"){
			urlMap[tabId] = false;
			
			checkLoggedIn(function(){
				//retrieve latest URL from history so we get the metadata
				chrome.history.search({text: '', maxResults:1}, function(results)
				{
					if (tab.url == results[0].url && keepURL(results[0].url)){
						historyObject = results[0];
						historyObject.userID = USER_ID;
						console.log(historyObject)
						postData('monitor/', {'logURL': JSON.stringify(historyObject)}, null);
					}
				});
			});
		}
});
/* 
	Terra Incognita only looks at news sites as defined by MediaCloud - www.mediacloud.org.
	It doesn't analyze your email, facebook, twitter. 
*/
function keepURL(url){
	//first check url against blacklist
	for (var i=0;i<BLACKLIST.length;i++){
		if (url.indexOf(BLACKLIST[i]) > -1){
			return false;
		}
	}
	//then check url against whitelist
	for (i=0;i<WHITELIST.length;i++){
		if (url.indexOf(WHITELIST[i]) > -1){
			return true;
		}
	}
	return false;
}

/*
	Handles post requests to server
	IMPORTANT - if your params contain JSON objects you should call JSON.stringify on them before 
	sending them to this method
*/
function postData(routeName, params, successCallback){
	console.log("Route: " + routeName);
	
	var http = new XMLHttpRequest();

	//Prepare key value pairs for submitting
	var keys = Object.keys(params);
	var newParams = "";
	_.each(keys, function(key) {
		//var data = JSON.stringify(params[key]);
		var data = params[key];
		if (newParams.length > 0)
			newParams = newParams+"&"
		newParams = newParams + key + "=" + encodeURIComponent(data);
		});

	
	http.open("POST", SERVER_URL + routeName, false);
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

	http.onreadystatechange = function() {
			if(http.readyState == 4 && http.status == 200) {
					console.log(http.responseText);
					if (successCallback)
						successCallback(http.responseText);
			}
	};
	http.send(newParams);
}





function logUserStatus(isLoggedIn, loginURL) {
	if (isLoggedIn){
		$('#loggedIn').html("You are logged in to Terra Incognita. <a href='"+loginURL+"'>Logout</a>");
	}
	else{
		console.log("User is not logged in. Redirecting to login page.");
		window.location.href=loginURL;
	}
}
document.addEventListener('DOMContentLoaded', onInit, false);
function onInit(){
	chrome.runtime.sendMessage({msg: "checkLoggedIn"}, function(response) {
		logUserStatus(response.isLoggedIn, response.loginURL);
	});
}
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
	if (request.userJSON){
	  sendResponse({msg: "thanks for the JSON dodohead"});
	  //$('#userJSON').html('<pre>' + JSON.stringify(request.userJSON, undefined, 2) + '</pre>');
	  
	  var tableRows = "";
	  var continents = request.userJSON["continents"][0];
	  var regions = request.userJSON["regions"][0];
	  var countries = request.userJSON["countries"][0];
	  var states = request.userJSON["states"][0];
	  var cities = request.userJSON["cities"][0];
	  console.log(request.userJSON)

	  //continents
	  $.each(continents, function(i, continent){
			tableRows += "<tr><td>"+ continent._id.continent_name + "</td><td>" + continent.count + "</td></tr>";
	   });
	  $('#continentCounts tr:last').after(tableRows);
	  tableRows ="";
	  
	  //regions
	  $.each(regions, function(i, region){
			tableRows += "<tr><td>"+ region._id.region_name + "</td><td>" + region.count + "</td></tr>";
	   });
	  
	  $('#regionCounts tr:last').after(tableRows);
	  tableRows ="";

	  //countries
	  $.each(countries, function(i, country){
			tableRows += "<tr><td>"+ country._id.country_code + "</td><td>" + country.count + "</td></tr>";
	   });
	  $('#countryCounts tr:last').after(tableRows);

	  tableRows ="";
	  //states
	  $.each(states, function(i, state){
			tableRows += "<tr><td>"+ state._id.state_code + "</td><td>" + state.count + "</td></tr>";
	   });
	  $('#stateCounts tr:last').after(tableRows);

	  tableRows ="";
	  //cities
	  $.each(cities, function(i, city){
			tableRows += "<tr><td>"+ city._id.name + ", " + city._id.state_code + ", " + city._id.country_code + "</td><td>" + city.count + "</td></tr>";
	   });
	  $('#cityCounts tr:last').after(tableRows);
	}
  });
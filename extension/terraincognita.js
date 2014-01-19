
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
	  $('#userJSON').html('<pre>' + JSON.stringify(request.userJSON, undefined, 2) + '</pre>');
	}
  });
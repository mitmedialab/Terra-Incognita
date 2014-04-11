

document.addEventListener('DOMContentLoaded', onInit, false);
function onInit(){
	console.log('DOMContentLoaded')

	//request the app from the background script DB
	console.log("Checking to see if last loaded city exists for this tab")
	chrome.runtime.sendMessage({msg: "checkForCityInTab"}, function(response){
		console.log("The last loaded city for this tab was " + response.cityID)
		App.initialize(response.cityID); 
	});
	

}

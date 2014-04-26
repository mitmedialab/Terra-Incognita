

document.addEventListener('DOMContentLoaded', onInit, false);
function onInit(){
	console.log('DOMContentLoaded')

	//request the app from the background script DB
	chrome.runtime.sendMessage({msg: "checkForCityInTab"}, function(response){
		App.initialize(response.cityID, response.isRandomCity); 
	});
	

}

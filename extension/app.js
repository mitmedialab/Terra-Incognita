App = {
	
	config: {
		debug: true
	},
	
	initialize: function () {
		App.debug('App.initialize()');
		App.instance = this;
		this.router = new App.Router()
		this.router.navigate('');
		Backbone.history.start();
		App.log
		App.listenForUserData();
	},
	
	debug: function (message) {
		if (App.config.debug) {
			console.log(message);
		}
	},
	listenForUserData: function(){
		chrome.runtime.onMessage.addListener(
			function(request, sender, sendResponse) {
				if (request.userJSON){
					sendResponse({msg: "thanks for the JSON dodohead"});
					App.loadUserData(request.userJSON);
				}
			});
	},
	loadUserData: function(json){
		var tableRows="";
		var continents = json["continents"][0];
		var regions = json["regions"][0];
		var countries = json["countries"][0];
		var continentsIncognita = json["continents_incognita"][0];
		var regionsIncognita = json["regions_incognita"][0];
		var countriesIncognita = json["countries_incognita"][0];
		var states = json["states"][0];
		var cities = json["cities"][0];
		var citiesIncognita = json["cities_incognita"][0];
		console.log(json)

		/***************************************************************/
		/* Continents Incognita 
		/***************************************************************/
		var continentIncognitaModels = [];
		$.each(continentsIncognita, function(i, continent){
				var continent = new App.ContinentModel({	"name":continent.name, 
															"continent_code":continent.continent_code,
															"count":0,
															"cognita":false
														});
				continentIncognitaModels.push(continent);
		 });

		App.continentIncognitaCollection = new App.ContinentCollection(continentIncognitaModels);

		App.continentIncognitaCollectionView = new App.UpdatingCollectionView({
			  collection           : App.continentIncognitaCollection,
			  childViewConstructor : App.GeoIncognitaView,
			  childViewTagName     : 'tr',
			  el                   : $('#continent-incognita-list')[0],
			  template: 'incognita-table',
			  title:'Continents Incognita'
		});
		App.continentIncognitaCollectionView.render();

		/***************************************************************/
		/* Regions Incognita 
		/***************************************************************/
		var regionIncognitaModels = [];
		$.each(regionsIncognita, function(i, region){
				var region = new App.RegionModel({			"name":region.region_name, 
															"region_code":region.region_code,
															"continent_code":region.continent_code,
															"count":0,
															"cognita":false
														});
				regionIncognitaModels.push(region);
		 });
		App.regionIncognitaCollection = new App.RegionCollection(regionIncognitaModels);

		App.regionIncognitaCollectionView = new App.UpdatingCollectionView({
			  collection           : App.regionIncognitaCollection,
			  childViewConstructor : App.GeoIncognitaView,
			  childViewTagName     : 'tr',
			  el                   : $('#region-incognita-list')[0],
			  template: 'incognita-table',
			  title:'Regions Incognita'
		});
		App.regionIncognitaCollectionView.render();
		
		/***************************************************************/
		/* Countries Incognita 
		/***************************************************************/
		var countryIncognitaModels = [];
		$.each(countriesIncognita, function(i, country){
				var country = new App.CountryModel({		"name":country.country_name,
															"country_code":country.country_code, 
															"un_country_code":country.un_country_code, 
															"region_name":country.region_name,
															"region_code":country.region_code,
															"continent_code":country.continent_code,
															"continent_name":country.continent_name,
															"count":0,
															"cognita":false
														});
				countryIncognitaModels.push(country);
		 });
		App.countryIncognitaCollection = new App.CountryCollection(countryIncognitaModels);

		App.countryIncognitaCollectionView = new App.UpdatingCollectionView({
			  collection           : App.countryIncognitaCollection,
			  childViewConstructor : App.GeoIncognitaView,
			  childViewTagName     : 'tr',
			  el                   : $('#country-incognita-list')[0],
			  template: 'incognita-table',
			  title:'Countries Incognita'
		});
		App.countryIncognitaCollectionView.render();

		/***************************************************************/
		/* Cities Incognita 
		/***************************************************************/
		var cityIncognitaModels = [];
		$.each(citiesIncognita, function(i, city){
				var city = new App.CityModel({				"name":city.city1,
															"country_code":city.country_code, 
															"un_country_code":city.un_country_code, 
															"region_name":city.region_name,
															"region_code":city.region_code,
															"continent_code":city.continent_code,
															"continent_name":city.continent_name,
															"count":0,
															"cognita":false
														});
				cityIncognitaModels.push(city);
		 });
		App.cityIncognitaCollection = new App.CityCollection(cityIncognitaModels);

		App.cityIncognitaCollectionView = new App.UpdatingCollectionView({
			  collection           : App.cityIncognitaCollection,
			  childViewConstructor : App.GeoIncognitaView,
			  childViewTagName     : 'tr',
			  el                   : $('#city-incognita-list')[0],
			  template: 'incognita-table',
			  title:'Cities Incognita'
		});
		App.cityIncognitaCollectionView.render();
	}
}


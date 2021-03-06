App.UserModel = Backbone.Model.extend({

	id: 'login',
	defaults: {
		authenticated: false,
		loginURL:'',
		userID:'',
		userCityVisits:[],
		username:''
	},
	initialize: function () {
		App.debug('App.UserModel.initialize()')
		_.bindAll(this, 'checkUserStatus');
		_.bindAll(this, 'logUserStatus');
		_.bindAll(this, 'checkUserForms');
		_.bindAll(this, 'logUserForms');

		var that = this;
		//User's city visits are cached in localstorage or else loaded from file
		chrome.storage.local.get("userCityVisits",
										function(result){
											if (Object.keys(result).length === 0){
												var userCityVisits = {};
												_.each(CITIES_RAW_DATA["cities"], function(city){
													userCityVisits[parseInt(city["geonames_id"])] = 0;
												});
											} else {
												that.set({"userCityVisits" : result["userCityVisits"]});
											}
										});

		this.checkUserStatus();

	},
	checkUserStatus: function(){
		App.debug('App.UserModel.checkUserStatus()');
		var that = this;
		chrome.runtime.sendMessage({msg: "checkLoggedIn"}, function(response) {
			that.logUserStatus(response.isLoggedIn, response.serverURL,response.loginURL, response.userID);
		});
	},
	checkUserForms: function(){
		App.debug('App.UserModel.checkUserForms()');
		var that = this;
		chrome.runtime.sendMessage({msg: "checkFormsFilledOut"}, that.logUserForms);
	},
	logUserStatus: function(isLoggedIn, serverURL, loginURL, userID){
		App.debug('App.UserModel.logUserStatus()');
		if (isLoggedIn){
			App.debug("User is logged in");
			this.set({"authenticated": true, "loginURL":loginURL, "serverURL":serverURL, "userID":userID});
			this.checkUserForms();
		}
		else{
			App.debug("User is not logged in.");
			App.debug("LoginURL is: " + loginURL);
			this.set({"authenticated": false, "serverURL":serverURL, "loginURL":loginURL, "userID":userID});
		}
	},
	logUserForms: function(response){
		App.debug('App.UserModel.logUserForms()');
		this.set({"needsToDoPostSurvey": response["needsToDoPostSurvey"], "hasSignedConsentForm": response["hasSignedConsentForm"], "hasCompletedPreSurvey":response["hasCompletedPreSurvey"]});
	},
	getCityVisitCount: function(geonames_id){
		var userCityVisits = this.get("userCityVisits");
		var count = userCityVisits[geonames_id];
		if (count == null){
			count = 0;
		}
		return count;
	},
	getUnvisitedCityID: function(){
		App.debug('App.UserModel.getUnvisitedCityID()');
		var userCityVisits = this.get("userCityVisits");
		var keys = Object.keys(userCityVisits);
		var randomCity = App.router.cityCollection.getRandomCityModel();
		while (_.contains(keys, randomCity.get("geonames_id"))){
			randomCity = App.router.cityCollection.getRandomCityModel();
		}
		return randomCity.get("geonames_id");
	},
	// Cache user city visits to local storage
	loadUser: function(json){
		App.debug('App.UserModel.loadUser()');
		this.set({
					'userCityVisits' : json.cities,
					'username' : json.username
				 });
		chrome.storage.local.set({'userCityVisits': json.cities}, function() {
          App.debug('Updated userCityVisits saved to local storage');
        });

	}
});

/*
	App.CityModel - A city, when the user has visited it, what stories they read in relation, and
					what stories users overall have read about that city
		cityID
		lat
		long
		name
		country_code
		country_name
		region_code
		region_name
		continent_code
		continent_name
		visitCount
		lastVisitDate

	* Below fields are loaded when user looks at city *

	userHistoryItemCollection(HistoryItemModel)
	systemHistoryItemCollection(HistoryItemModel)
	cityStats (CityStatsModel)
*/
App.CityModel = Backbone.Model.extend({
	idAttribute : 'geonames_id',
    randomUrl: '',
	defaults: {

	},

	initialize: function () {
		App.debug('App.CityModel.initialize()');
	},
	fetchReadingLists: function(){
		App.debug('App.CityModel.fetchReadingLists()');
		var that = this;

		chrome.runtime.sendMessage({msg: "loadReadingLists", "city_id": this.get("geonames_id")}, function(response) {
		  console.log("GEONAMES ID " + that.get("geonames_id"))
		  console.log(App.router.mapView.cityZoomedView.model.get("geonames_id"))
		  if (that.get("geonames_id") == App.router.mapView.cityZoomedView.model.get("geonames_id")){
		  	that.loadReadingLists(response.readingLists);
		  }
		});
	},
	loadReadingLists: function(readingLists){
		App.debug('App.CityModel.loadReadingLists()');
		App.debug('readingLists["systemHistoryItemCollection"] size is ' + readingLists["systemHistoryItemCollection"].length)
		this.set({
					'userHistoryItemCollection': new App.HistoryItemCollection(readingLists["userHistoryItemCollection"]),
					'systemHistoryItemCollection': new App.HistoryItemCollection(readingLists["systemHistoryItemCollection"])
					/* if you want a random URL from system stories
						'randomUrl': readingLists["systemHistoryItemCollection"][Math.floor((Math.random() * readingLists["systemHistoryItemCollection"].length))]['url']
					*/
				});

	},
	fetchCityStats: function(){
		App.debug('App.CityModel.fetchCityStats()');
		var that = this;

		chrome.runtime.sendMessage({msg: "loadCityStats", "city_id": this.get("geonames_id")}, function(response) {
		  if (that.get("geonames_id") == App.router.mapView.cityZoomedView.model.get("geonames_id")){
			  that.loadCityStats(response.cityStats);
		  }
		});
	},
	loadCityStats: function(cityStats){
		App.debug('App.CityModel.loadCityStats()');
		this.set({
					'cityStats': new App.CityStatsModel(cityStats),
				});
	},
  fetchRandomUrl: function(){
    App.debug('App.CityModel.fetchRandomUrl()');
    var that = this;

    chrome.runtime.sendMessage({
      'msg': 'loadRandomUrl',
      'city_id': this.get('geonames_id')
    }, function(response) {
    	//Only update the UI if they haven't shifted to a new city
    	if (that.get("geonames_id") == App.router.mapView.cityZoomedView.model.get("geonames_id")){
    		that.set({'randomUrl': response.randomUrl});
    	}
    });
  
  }

});
/*
	City Collection stores cities as raw data until the model is created by user
	looking at the city and fetching articles related to it.

	This is because creating 1000 city models in the browser makes for bad performance!
*/
App.CityCollection = Backbone.Collection.extend({
    model: App.CityModel,
    defaults: { rawData : [] },
    initialize: function (models, options) {
		App.debug('App.CityCollection.initialize()');
		if (options)
			this.rawCitiesData = options.rawCitiesData;

	},
	/*
		gets city model from collection
		If it doesn't already exist in collection then load it from cached raw data
	*/
	getCityModel: function(id){
		App.debug('App.CityCollection.getCityModel()');
		if (this.get(id) != null){
			return this.get(id);
		} else{
			for (var i=0; i<this.rawCitiesData.length; i++){
				var city = this.rawCitiesData[i];
				if (city["geonames_id"] == id){
					return this.add(city);
				}
			}
			App.debug('ERROR: No corresponding city found for id: ' + id);
		}
	},
	getRandomCityModel: function(){
		App.debug('App.CityCollection.getRandomCityModel()');
		var city = this.rawCitiesData[Math.round( Math.random() * this.rawCitiesData.length-1 )];
		return this.getCityModel(city.geonames_id);
	},

});
App.CityStatsModel = Backbone.Model.extend({
	defaults: {},

	initialize: function () {
		App.debug('App.CityStatsModel.initialize()');
	}
});
/*
	App.HistoryItemModel - One story/url that user has read
		url
		title
		dateVisited
		etc
		cityID/s
*/
App.HistoryItemModel = Backbone.Model.extend({
	defaults: {},

	initialize: function () {
		App.debug('App.HistoryItemModel.initialize()');
	}
});
App.HistoryItemCollection = Backbone.Collection.extend({
    model: App.HistoryItemModel
});
/*
	App.CompassModel - aggregate & personal stats about user reading
		userGlobalNorth %
		userGlobalSouth %
		userEast%
		userWest%
		systemGlobalNorth%
		systemGlobalSouth%
		systemEast%
		systemWest%
		totalCities
*/
App.CompassModel = Backbone.Model.extend({
	defaults: {},

	initialize: function () {
		App.debug('App.CompassModel.initialize()');
	}
});

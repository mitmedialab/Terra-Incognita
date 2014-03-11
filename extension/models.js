App.UserModel = Backbone.Model.extend({
	
	id: 'login',
	defaults: {
		authenticated: false,
		loginURL:'',
		userID:''
	},
	initialize: function () {
		App.debug('App.UserModel.initialize()')
		_.bindAll(this, 'checkUserStatus');
		_.bindAll(this, 'logUserStatus');
		this.checkUserStatus();

	},
	checkUserStatus: function(){
		App.debug('App.UserModel.checkUserStatus()');
		var that = this;
		chrome.runtime.sendMessage({msg: "checkLoggedIn"}, function(response) {
			that.logUserStatus(response.isLoggedIn, response.loginURL, response.userID);
		});
	},
	logUserStatus: function(isLoggedIn, loginURL, userID){
		App.debug('App.UserModel.logUserStatus()');
		if (isLoggedIn){
			App.debug("user is logged in");
			this.set({"authenticated": true, "loginURL":loginURL, "userID":userID});
		}
		else{
			App.debug("User is not logged in. Redirecting to login page.");
			this.set({"authenticated": false, "loginURL":loginURL, "userID":userID});
		}
	},
	getCityVisitCount: function(geonames_id){
		var userCityVisits = this.get("userCityVisits");
		var count = userCityVisits[geonames_id];
		if (count == null){
			count = 0;
		}
		return count;
	},
	loadUser: function(json){
		App.debug('App.UserModel.loadUser()');
		
		this.set({	
					'userCityVisits' : json.cities,
					'userHistoryPath':new App.HistoryItemCollection(json.last10HistoryItems)
				 });
		console.log(this.get("userCityVisits"))
		console.log("userCItyVisits loadUser")

		
		//TODO create compass model
		
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
*/
App.CityModel = Backbone.Model.extend({
	idAttribute : 'geonames_id',
	defaults: {

	},
	
	initialize: function () {
		App.debug('App.CityModel.initialize()');
	},
	fetchReadingLists: function(){
		App.debug('App.CityModel.fetchReadingLists()');
		var that = this;
		
		chrome.runtime.sendMessage({msg: "loadReadingLists", "city_id": this.get("geonames_id")}, function(response) {
		  that.loadReadingLists(response.readingLists);
		});
	},
	loadReadingLists: function(readingLists){
		App.debug('App.CityModel.loadReadingLists()');
		this.set({
					'userHistoryItemCollection': new App.HistoryItemCollection(readingLists["userHistoryItemCollection"]),
					'systemHistoryItemCollection': new App.HistoryItemCollection(readingLists["systemHistoryItemCollection"])
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

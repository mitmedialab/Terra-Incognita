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
	
});
App.ContinentModel = Backbone.Model.extend({
	defaults: {
		name: '',
		continent_code:'',
		count:0,
		cognita: true
	},
	initialize: function () {
		App.debug('App.ContinentModel.initialize()');
	}
});

App.RegionModel = Backbone.Model.extend({
	defaults: {
		name: '',
		region_code:'',
		count:0,
		cognita:true,
		//Should contain its parent info for looking up? Or ref to model? 
		//Or continent model contains region collection?
		continent_code:'',
		continent_name:''
	},
	
	initialize: function () {
		App.debug('App.RegionModel.initialize()');
	}
});
App.CountryModel = Backbone.Model.extend({
	defaults: {
		name: '',
		country_code:'',
		count:0,
		cognita:true,
		//Should contain its parent info for looking up? Or ref to model? 
		//Or continent model contains region collection?
		region_code:'',
		region_name:'',
		continent_code:'',
		continent_name:''
	},
	
	initialize: function () {
		App.debug('App.CountryModel.initialize()');
	}
});
App.CityModel = Backbone.Model.extend({
	defaults: {
		name: '',
		city_name:'',
		geonames_id:'',
		state_code:'',
		count:0,
		cognita:true,
		//Should contain its parent info for looking up? Or ref to model? 
		//Or continent model contains region collection?
		country_code:'',
		country_name:'',
		region_code:'',
		region_name:'',
		continent_code:'',
		continent_name:''
	},
	
	initialize: function () {
		App.debug('App.CityModel.initialize()');
	}
});
App.ContinentCollection = Backbone.Collection.extend({
    model: App.ContinentModel
});
App.RegionCollection = Backbone.Collection.extend({
    model: App.RegionModel
});
App.CountryCollection = Backbone.Collection.extend({
    model: App.CountryModel
});
App.StateCollection = Backbone.Collection.extend({
    model: App.StateModel
});
App.CityCollection = Backbone.Collection.extend({
    model: App.CityModel
});

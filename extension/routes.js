App.Router = Backbone.Router.extend({
	routes: {
		'': 'home'
		, '/': 'home'
	},
	
	initialize: function (options) {
		App.debug('App.Router.initialize()');
		this.userModel = new App.UserModel();
		this.cityCollection = new App.CityCollection([],{"rawCitiesData":CITIES_RAW_DATA["cities"]});
		this.mapView = new App.MapView({
			userModel: this.userModel,
			cityCollection: this.cityCollection
		})
		
		this.listenForUserData();
	},
	
	home: function () {
		App.debug('Route: home');
		//$('#hello').html(this.mapView.el);
		
	},
	defaultRoute: function (routeId) {
		App.debug('Default route');
		console.log('Default route: ' + routeId);
	},
	/*
		Listens for incoming data from background.js communicating
		with server. Data is User + Cities + Compass + Recent User History
	*/
	listenForUserData: function(){
		App.debug('App.Router.listenForUserData()');
		var that = this;
		chrome.runtime.onMessage.addListener(
			function(request, sender, sendResponse) {
				if (request.user){
					sendResponse({msg: "thanks for the JSON dodohead"});
					App.debug('Received User Data');
					console.log(request.user)
					that.userModel.loadUser(request.user);
					that.citySelectorView = new App.CitySelectorView({cityCollection: that.cityCollection, userModel: that.userModel});
				}
			});
	},
})
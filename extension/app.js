App = {
	
	config: {
		debug: true
	},
	
	initialize: function (cityID, isRandomCity) {
		App.debug('App.initialize()');
		App.instance = this;
		
		/*
			From the extension.config.js
		*/
		App.serverURL = SERVER_URL;
		App.loginURL = LOGIN_URL;
		
		this.router = new App.Router({"cityID":cityID, "isRandomCity":isRandomCity})
		this.router.navigate('');
		Backbone.history.start();
		App.log	
	},
	
	debug: function (message) {
		if (App.config.debug) {
			console.log(message);
		}
	},
}


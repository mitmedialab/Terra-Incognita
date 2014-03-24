/**
 * Main application view.
 */
App.MapView = Backbone.View.extend({
	el: $("html"),
	events: {
		"click #user-history-path": "toggleUserHistoryPath"
	},
	initialize: function (options) {
		App.debug('App.MapView.initialize()');
		this.options = options || {};
		
		_.bindAll(this, 'render','toggleUserHistoryPath');
		
		// Create models
		this.cityCollection = options.cityCollection;
		this.userModel = options.userModel;
		this.userModel.on('change:loginURL', this.renderLogin,this);
		this.map = L.mapbox.map('map', 'kanarinka.hcc1900i');//random spot -- .setView([this.getRandomInRange(-90,90,3), this.getRandomInRange(-180,180,3)], 9);
		
		App.map = this.map;
		this.cityZoomedView = new App.CityZoomedView(
		{
			model: this.cityCollection.getRandomCityModel()
		});

		// Create sub-views
		this.render();
	},
	
	render: function () {
		App.debug('App.MapView.render()')
		
		if (this.userModel.get('authenticated')) {
			this.$el.find("#hello").append('Hello, ' + this.userModel.get('userID'));
			/* THIS WAS FROM GLOBAL MAP VIEWS - not using at the moment
				
			if (this.userModel.get('userHistoryPath') && this.userModel.get('userHistoryPath').length > 0 && !this.userHistoryPathView) {
				this.userHistoryPathView = new App.HistoryItemMarkerCollectionView({collection:this.userModel.get('userHistoryPath')})
			}
			if (this.userModel.get('userCities') && this.userModel.get('userCities').length > 0 && !this.userCitiesView) {
				this.userCitiesView = new App.CityMarkerCollectionView({collection:this.userModel.get('userCities')})
			}*/
		} 
		
		return this;
	},

	renderLogin: function(){
		if (this.userModel.get('loginURL') != '')
			this.loginView = new App.LoginView({ model: this.userModel });
	},
	unloadCityZoomView: function(){
		App.debug('App.MapView.unloadCityZoomView()')
		if (this.cityZoomedView)
			this.cityZoomedView.clearAll();
	},
	toggleUserHistoryPath: function(){
		App.debug('App.MapView.toggleUserHistoryPath()')
		if (this.userHistoryPathView){
			if (this.userHistoryPathView.showing){
				this.userHistoryPathView.clearAll();
				this.userCitiesView.render();
			}
			else{
				this.unloadCityZoomView();
				this.userHistoryPathView.render();
			}
		} 
	},
	toggleCities: function(){
		App.debug('App.MapView.toggleCities()')
		if (this.userCitiesView){
			if (this.userCitiesView.showing){
				this.userCitiesView.clearAll();
			}
			else{
				this.userCitiesView.render();
			}
		} 
	},
	/*
		Fun! getting random lat longs
		lon range is -180 to +180
		lat range is -90 to +90
	*/
	getRandomInRange: function(from, to, fixed) {
		return (Math.random() * (to - from) + from).toFixed(fixed) * 1;
	}

});
App.CityMarkerCollectionView = Backbone.View.extend({
	
	initialize: function (options) {
		App.debug('App.CityMarkerCollectionView.initialize()');
		this.options = options || {};
		this.showing = false;
		this.geojson = {};
		this.geojson["type"]="FeatureCollection";
		this.geojson["features"] = [];
		that = this;
		this.collection.each(function(city) {
			
			if (city.get("lon")){
				var json = {};
				json["type"]="Feature";
				json["properties"]={	 
										"marker-color":"#f0f",
										'marker-size': 'medium',
										'marker-symbol': 'embassy',
										'modelId':city.cid,
										"url": 'http://127.0.0.1:5000/go/' + city.get('geonames_id') 
									};
				json["geometry"]={		"type": 'Point',
										"coordinates": [parseFloat(city.get("lon")), parseFloat(city.get("lat"))]};				
				that.geojson["features"].push(json);
			}
		});

		
	},
	clearAll: function(){
		App.debug('App.CityMarkerCollectionView.clearAll()');
		App.map.featureLayer.clearLayers();
		App.map.featureLayer.clearAllEventListeners();
		this.showing = false;
	},
	render: function () {
		App.debug('App.CityMarkerCollectionView.render()');
		
		//turn on marker layer
		App.map.featureLayer.setFilter(function() { return true; });
		App.map.featureLayer.setGeoJSON(this.geojson);
		var that = this;
		App.map.featureLayer.on('click', function(e) {
			e.layer.unbindPopup();
			App.router.mapView.cityZoomedView = new App.CityZoomedView(
														{
															model: that.collection.get(e.layer.feature.properties.modelId)
														});
		});
		App.map.fitBounds(App.map.featureLayer.getBounds());
		this.showing = true;
		
		return this;
	}
});
App.HistoryItemMarkerCollectionView = Backbone.View.extend({
	
	initialize: function (options) {
		App.debug('App.HistoryItemMarkerCollectionView.initialize()');
		this.options = options || {};
		this.polyline = L.polyline([],{color:'white',weight:1.5,opacity:0.8});
		this.geojson = {};
		this.geojson["type"]="FeatureCollection";
		this.geojson["features"] = [];
		that = this;
		this.collection.each(function(historyItem) {
			
			var primaryCities = historyItem.get('geodata')["primaryCities"];
			if (primaryCities.length > 0){
				var city = primaryCities[0];
				var json = {};
				json["type"]="Feature";
				json["properties"]={	
										"marker-color":"#f00",
										'marker-size': 'small',
										'marker-symbol': 'harbor',

										"url": historyItem.get('url')
									};
				json["geometry"]={		"type": 'Point',
										"coordinates": [city.lon, city.lat]};				
				that.geojson["features"].push(json);
				that.polyline.addLatLng(L.latLng(city.lat,city.lon));
				
			}

		});
		this.showing = false;
	},
	clearAll: function(){
		App.debug('App.HistoryItemMarkerCollectionView.clearAll()');
		App.map.featureLayer.clearLayers();
		App.map.removeLayer(this.polyline);
		App.map.featureLayer.clearAllEventListeners();
		this.showing = false;
	},
	render: function () {
		App.debug('App.HistoryItemMarkerCollectionView.render()');

		//turn on marker layer
		App.map.featureLayer.setFilter(function() { return true; });

		//this.polyline.addTo(App.map);
		App.map.featureLayer.setGeoJSON(this.geojson);
		App.map.featureLayer.on('click', function(e) {
			e.layer.unbindPopup();
			window.open(e.layer.feature.properties.url);
		});
		//App.map.setView([App.router.mapView.getRandomInRange(-90,90,3), App.router.mapView.getRandomInRange(-180,180,3)], 9);
		App.map.fitBounds(App.map.featureLayer.getBounds());
		
		this.showing = true;
		return this;
	}
});
App.CityZoomedView = Backbone.View.extend({
	el: $("#city-zoomed-view"),
	template: TEMPLATES['city-zoomed-reading-lists'],
	initialize: function (options) {
		App.debug('App.CityZoomedView.initialize()');
		this.options = options || {};
		_.bindAll(this, 'render');
		this.model.on('change',this.render,this);
		this.model.fetchReadingLists();
		this.render();
	},
	clearAll: function(){
		App.debug('App.CityZoomedView.clearAll()');
		this.showing = false;
		this.$el.empty();
	},
	render: function () {
		App.debug('App.CityZoomedView.render()');
		
		//turn off marker layer
		App.map.featureLayer.setFilter(function() { return false; });
		
		App.map.setView([this.model.get("lat"), this.model.get("lon")], 12);
		var html = this.template({ population : this.addCommas(this.model.get("pop")), cityID : this.model.get("geonames_id"), city_name: this.model.get("city_name"), country_name:this.model.get("country_name"), userStories:this.model.get("userHistoryItemCollection"), systemStories:this.model.get("systemHistoryItemCollection") });
		this.$el.html(html);
		this.showing = true;
		return this;
	},
	addCommas: function(nStr)
    {
      nStr += '';
      x = nStr.split('.');
      x1 = x[0];
      x2 = x.length > 1 ? '.' + x[1] : '';
      var rgx = /(\d+)(\d{3})/;
      while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + ',' + '$2');
      }
      return x1 + x2;
    },
});

/*
	D3.js control that functions to show users which cities they have read about & how much
	and also use to select cities
*/
App.CitySelectorView = Backbone.View.extend({
	initialize: function (options) {
		App.debug('App.CitySelectorView.initialize()');
		this.options = options || {};
		this.userModel = options.userModel;
		this.rawCitiesData = options.cityCollection.rawCitiesData;
		this.render();
	},
	render: function () {
		App.debug('App.CitySelectorView.render()');
		var margin = {top: 0, right: 0, bottom: 0, left: 0},
			width = $(window).width(),
			height = 50;

		var x = d3.scale.ordinal();
		x.rangeRoundBands([0, width], 0,0);

		var y = d3.scale.linear()
			.range([height, 0]);

		var filler = function(d) { 
				if (d.cityVisitCount > 0)
					return "#555";
				else 
					//return "#efe3cb"; //light land
					return "#cdb368"; //dark land
					//return "#c0d47d"; //green land
					//return "#a5dada"; //blue 
			};
		var svg = d3.select("body").append("svg")
			.attr("width", width + margin.left + margin.right)
			.attr("height", height + margin.top + margin.bottom)
			.append("g")
			.attr("transform", "scale(2,1),translate(-254,0)");
			
		var data = this.rawCitiesData;

		x.domain(data.map(function(d) { return d.city_name; }));
		var that = this;
		y.domain([0, d3.max(data, function(d) { 
			d.cityVisitCount = that.userModel.getCityVisitCount(d.geonames_id);
			return d.cityVisitCount; 
		})]);

		svg.selectAll(".bar")
			.data(data)
		  .enter().append("rect")
			.attr("class", "bar")
			.attr("x", function(d) { 
			  return x(d.city_name); 
			})
			.attr("width", x.rangeBand())
			.attr("y", function(d) { return 0; })
			//.attr("y", function(d) { return y(d.cityVisitCount); })
			//.attr("height", function(d) { return height - y(d.cityVisitCount); })
			//all bars are same height, just differ in color
			.attr("height", function(d) { return height;
			})
			.attr("fill", filler)
			.attr("fill-opacity", 1)
			.on("click", function(d, i){
				
				var cityModel = App.router.cityCollection.getCityModel(d.geonames_id);
				App.router.mapView.cityZoomedView = new App.CityZoomedView(
					{
						model: cityModel
					});
			})
			.on("mouseover", function(d) {   
				d3.select(this).attr('fill-opacity', 1.0);

				$('#city-selector-tooltip').text(d.city_name + ", " + d.country_name);
				$('#city-selector-tooltip').css({left:d3.mouse(this)[0],bottom:height});
				   
			})                  
			.on("mouseout", function(d) {       
				d3.select(this).attr('fill-opacity', filler);
				$('#city-selector-tooltip').text(""); 
			});

			//Once it's done, make a copy and paste it up on the top of the frame too
			$('svg').clone().attr("id", "svg-extra").appendTo('body');
	}
});
/**
 * Login form.
 */
App.LoginView = Backbone.View.extend({
	el: $("#login-view"),
	template: TEMPLATES['login-modal-template'],
	initialize: function (options) {
		App.debug('App.LoginView.initialize()');
		this.options = options || {};
		_.bindAll(this, 'render');
		_.bindAll(this, 'login');
		_.bindAll(this, 'error');
		//this.model.on('unauthorized', this.error);
		//this.model.on('change',this.render,this);
		this.render();
	},
	events: {
		'click button': 'login'
	},
	render: function () {
		App.debug('App.LoginView.render()');
		console.log(this.model.get("loginURL"))
		var html = this.template({ loginURL : this.model.get("loginURL") });
		this.$el.html(html);
		
		//call window into being
		this.$el.find('#login-modal').modal();
		
		/*this.$el=$("#loggedIn");
		
		if (this.model.get("authenticated") == true)
			this.$el.html("You are logged in to Terra Incognita. <a href='"+this.model.get("loginURL")+"'>Logout</a>");
		else
			this.$el.html("You are not logged into Terra Incognita. <a href='"+this.model.get("loginURL")+"'>Login now</a>");
			//window.location.href=this.model.get("loginURL");
		*/
		return this;
	},
	
	login: function (event) {
		App.debug('App.LoginView.login()');
		event.preventDefault();
		username = $('input[name=username]', this.$el).val();
		password = $('input[name=password]', this.$el).val();
		$('input[name=username]', this.$el).val('');
		$('input[name=password]', this.$el).val('');
		this.model.signIn(username, password);
	},
	
	error: function (message) {
		$('.message', this.$el).html(message);
		$('input[name=username]', this.$el).focus();
	}
});
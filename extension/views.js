/**
 * Main application view.
 */
App.MapView = Backbone.View.extend({
	el: $("html"),

	initialize: function (options) {
		App.debug('App.MapView.initialize()');
		this.options = options || {};

		_.bindAll(this, 'render');

		// Create models

		this.cityCollection = options.cityCollection;
		this.userModel = options.userModel;
		this.userModel.on('change', this.render,this);
		this.userModel.on('change:loginURL', this.renderLogin,this);
		this.userModel.on('change:hasSignedConsentForm', this.renderFormsNotification,this);
		this.map = L.mapbox.map('map', 'kanarinka.hcc1900i', { zoomControl:false });

		App.map = this.map;
		this.citySelectorView = new App.CitySelectorView({cityCollection: this.cityCollection, model: this.userModel});

		var that = this;
		this.userModel.on("change:userCityVisits", function() {
			that.citySelectorView.render()

				/*if (that.cityZoomedView){
						that.cityZoomedView.clearAll();
				}*/
			//Only render if city zoomed view hasn't been set up already
			//This is to try to patch the loading 3x bug
			if (!that.cityZoomedView){
				var cityID ="";
				var isRandomCity = true;
				if (that.options.cityID && that.options.cityID !=""){
					cityID = that.options.cityID;
					isRandomCity = that.options.isRandomCity;
				}
				else{
					cityID = that.userModel.getUnvisitedCityID();
					isRandomCity = true;
				}
			    that.cityZoomedView = new App.CityZoomedView(
					{
						model: that.cityCollection.getCityModel(cityID),
						isRandomCity:isRandomCity
					});
			    // Create sub-views

			}
			that.render();
		})


	},

	render: function () {
		App.debug('App.MapView.render()')
		if (this.userModel.get('username')) {
			$("#hello").html('Hello, ' + this.userModel.get('username'));
		}

		return this;
	},

	renderLogin: function(){
		if (this.userModel.get('loginURL') != '' && !this.userModel.get('authenticated'))
			this.loginView = new App.LoginView({ model: this.userModel });
		else if (this.userModel.get('loginURL') != ''){
      $("#logoutURL").attr("href", this.userModel.get('loginURL').replace('login', 'logout'));
			$("#changeUsernameURL").attr("href", this.userModel.get('loginURL'));
		}
	},
	renderFormsNotification: function(){
		App.debug('App.MapView.renderFormsNotification()')
		if ( (this.userModel.get('needsToDoPostSurvey') != null && this.userModel.get('needsToDoPostSurvey')) || (this.userModel.get('hasSignedConsentForm') != null && (!this.userModel.get('hasSignedConsentForm') || !this.userModel.get('hasCompletedPreSurvey')))){
			this.formsNotificationView = new App.FormsNotificationView({ model: this.userModel });
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

App.CityZoomedView = Backbone.View.extend({
	el: $("#city-zoomed-view"),
	template: TEMPLATES['city-zoomed-reading-lists'],
	events : {
		"submit" : "submitRecommendation",
		"click .glyphicon-thumbs-up,.glyphicon-thumbs-down": "submitHistoryItemRecommendation",
		"click .system-story,.user-story": "logStoryClick",
		"click .show-all-system-stories" : "toggleSystemStories"
	},
	initialize: function (options) {
		App.debug('App.CityZoomedView.initialize()');

		this.options = options || {};
		_.bindAll(this, 'render');
		_.bindAll(this, 'clearAll');
		_.bindAll(this, 'submitRecommendation');
		_.bindAll(this, 'submitHistoryItemRecommendation');
		_.bindAll(this, 'logStoryClick');
		this.isRandomCity = this.options.isRandomCity;
		this.model.on('change', this.render, this);
    App.user.on('change:userID', this.render, this);
		this.model.fetchReadingLists();
		this.model.fetchCityStats();
    if (!this.model.get('randomUrl')) {
      this.model.fetchRandomUrl();
    }
		this.randomWords = ["fun", "weird", "local","different","interesting","what","alternative","whoa", "notwar"];
		this.randomSayings =["Fortune favors the bold", "Fortune favors the brave","Chance favors the prepared mind"];
		//Background page caches cityID in relation to tab for "Back purposes"
		chrome.runtime.sendMessage({msg: "saveCityFromTab", "cityID":this.model.get("geonames_id"),"isRandomCity":this.isRandomCity}, function(response){
			console.log("Saved city with tab")
		});
		this.render();
	},
	toggleSystemStories : function(event){
		App.debug('App.CityZoomedView.showSystemStories()');
		event.preventDefault();
		if ($('.system-story-row:hidden').size() > 0){
			$('.system-story-row').show();
		} else{
			$('.system-story-row:gt(4)').hide();
		}


	},
	logStoryClick : function(event){
		App.debug('App.CityZoomedView.logStoryClick()');
		chrome.runtime.sendMessage({msg: "logStoryClick", "city_id": this.model.get("geonames_id"), "isRandomCity":(this.isRandomCity ? 1 : 0), "ui_source":  ($(event.target).hasClass("system-story") ? "system-story" : "user-story"), "url" : $(event.target).attr("href"), }, function(response) {
		  App.debug(response)
		});
	},
	submitRecommendation : function( event) {
            event.preventDefault();
            //send to server. Upon return, update city stats to show user that their work paid off
            var that = this;

            chrome.runtime.sendMessage({msg: "submitRecommendation", "city_id": this.model.get("geonames_id"), "url" : $("#url_recommendation").val()}, function(response) {

			  if (response.result["response"] =="ok")
				  	that.model.fetchCityStats();
			});
			$(".submit-recommendation").text("Got it, thanks! Care to enter another?");
			$("#url_recommendation").attr("placeholder","");
            $("#url_recommendation").val("");
            return false;
    },
    submitHistoryItemRecommendation : function(event) {
            event.preventDefault();
            var isThumbsUp = $(event.target).attr("class").indexOf("up") != -1;
            var url = $(event.target).parent().attr("href");
            var that = this;
            chrome.runtime.sendMessage({msg: "submitHistoryItemRecommendation", "city_id" : this.model.get("geonames_id"), "url": url, "isThumbsUp" : isThumbsUp}, function(response) {
			  App.debug(response)
			  if (response.result["response"] =="ok")

				  	//$(event.target).addClass("glyphicon-chosen");
				  	//$(event.target).parent().siblings().find(".glyphicon").addClass("glyphicon-unchosen");
				  	//TODO: AWFUL! Must break up this view into subviews instead of re-fetching from server.
				  	//This is reloading everything from server to update the screen.
				  	//Sorry for bad behavior to anyone who looks at this...
				  	that.model.fetchReadingLists();
				  	that.model.fetchCityStats();
			});
            return false;
    },

	clearAll: function(){
		App.debug('App.CityZoomedView.clearAll()');
		this.minimap.removeFrom(App.map);
		this.undelegateEvents();
		this.unbind();
		$(this.el).empty();

	},
	render: function () {
		App.debug('App.CityZoomedView.render()');

		App.map.setView([this.model.get("lat"), this.model.get("lon")], 12);
		var that = this;


			if (!this.minimap){

				var markerPos = new L.LatLng(that.model.get("lat"), that.model.get("lon"));
				var pinAnchor = new L.Point(5, 5);
				var pin = new L.Icon({ iconUrl: "img/dot.png", iconAnchor: pinAnchor });
				var cityMarker = L.marker(markerPos, { icon: pin });


				var tileLayer = L.mapbox.tileLayer('kanarinka.hcc1900i');
				var cityLayerGroup = L.layerGroup([tileLayer, cityMarker]);
				this.minimap = new L.Control.MiniMap(cityLayerGroup, {zoomLevelFixed:1, position:"bottomright"}).addTo(App.map);
			}

		//random spot -- .setView([this.getRandomInRange(-90,90,3), this.getRandomInRange(-180,180,3)], 9);

		var html = this.template({
                  randomWord: this.randomWords[Math.floor(Math.random() * this.randomWords.length)],
									randomSaying: this.randomSayings[Math.floor(Math.random() * this.randomSayings.length)],
									population : this.addCommas(this.model.get("pop")),
									cityID : this.model.get("geonames_id"),
									city_name: this.model.get("city_name"),
									country_name:this.model.get("country_name"),
									userStories:this.model.get("userHistoryItemCollection"),
									systemStories:this.model.get("systemHistoryItemCollection"),
									cityStats : this.model.get("cityStats"),
									userID : App.user.get("userID"),
									serverURL : App.serverURL,
									isRandomCity : (this.isRandomCity ? 1 : 0),
									isCapitalCity : this.model.get("capital") == 1 ? true : false
								});
		this.$el.html(html);
	    if (this.model.get('randomUrl')) {
	      this.$('.btn-go')
	        .attr('href', this.model.get('randomUrl'));
	    } 
	    else {
	    	// Fill the red button with a URL to google news for that place in the meantime while waiting for reddit
	    	// Better behavior would be to scrape first entry from gnews and put it here but this is fallback til we do that
	    	var googleNews = "https://www.google.com/search?tbm=nws&q=";
	    	var q = this.model.get('city_name') + " " + this.model.get('country_name');
	    	this.$('.btn-go').attr('href', googleNews + q);
	    }

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
	id: "city-selector-tooltip",
	template: TEMPLATES['city-selector-template'],
	initialize: function (options) {
		App.debug('App.CitySelectorView.initialize()');
		_.bindAll(this, 'render');
		this.options = options || {};
		//this.model.on('change:userCityVisits', this.render,this);
		this.rawCitiesData = options.cityCollection.rawCitiesData;

	    if(this.model.get("userCityVisits") && Object.keys(this.model.get("userCityVisits")).length != 0)
			this.render();

	},
	render: function () {
		App.debug('App.CitySelectorView.render()');

		var html = this.template({ visitedCityCount : Object.keys(this.model.get("userCityVisits")).length });

		this.$el.html(html);

		this.$el.appendTo('body');

		var margin = {top: 0, right: 0, bottom: 0, left: 0},
			width = $(window).width(),
			height = 50;

		var x = d3.scale.ordinal();
		x.rangeBands([0, width], 0,0);

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
			//.attr("transform", "scale(2,1),translate(-254,0)");

		var data = this.rawCitiesData;

		x.domain(data.map(function(d) { return d.city_name; }));
		var that = this;
		y.domain([0, d3.max(data, function(d) {
			d.cityVisitCount = that.model.getCityVisitCount(d.geonames_id);
			return d.cityVisitCount;
		})]);

		svg.selectAll(".bar")
			.data(data)
		  .enter().append("rect")
			.attr("class", "bar")
			.attr("x", function(d) {
			  return Math.round(x(d.city_name));
			})
			.attr("width", function(d) { return Math.round(x.rangeBand() + x(d.city_name)) - Math.round( x(d.city_name) ); })
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
				if (App.router.mapView.cityZoomedView){
					App.router.mapView.cityZoomedView.clearAll();
				}
				App.router.mapView.cityZoomedView = new App.CityZoomedView(
					{
						model: cityModel,
						isRandomCity : false
					});
				chrome.runtime.sendMessage({msg: "logCityClick", "city_id":d.geonames_id}, function(response){
					//console.log("Logged city click")
				});

			})
			.on("mouseover", function(d) {

				d3.select(this).attr('fill-opacity', 1.0);
				that.$el.text(d.continent_name.toUpperCase() + " :: " + d.country_name + " :: " +d.city_name);
				if (d3.mouse(this)[0] > width/2){
					that.$el.css({left:d3.mouse(this)[0] - that.$el.outerWidth(),bottom:height+1});
				} else {
					that.$el.css({left:d3.mouse(this)[0],bottom:height+1});
				}

			})
			.on("mouseout", function(d) {
				d3.select(this).attr('fill-opacity', filler);
				that.$el.html(html);
				that.$el.css({left:0,bottom:height+1});
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

		//this.model.on('unauthorized', this.error);
		//this.model.on('change',this.render,this);
		this.render();
	},
	events: {
		'click button': 'login'
	},
	render: function () {
		App.debug('App.LoginView.render()');

		var html = this.template({ loginURL : this.model.get("loginURL") });
		this.$el.html(html);

		//call window into being
		this.$el.find('#login-modal').modal();

		return this;
	},


});
/**
 * FormsNotificationView modal.
 */
App.FormsNotificationView = Backbone.View.extend({
	el: $("#forms-notification-view"),
	template: TEMPLATES['forms-modal-template'],
	initialize: function (options) {
		App.debug('App.FormsNotificationView.initialize()');
		this.options = options || {};
		_.bindAll(this, 'render');

		//this.model.on('unauthorized', this.error);
		//this.model.on('change',this.render,this);
		this.render();
	},
	events: {
		'click button': 'login'
	},
	render: function () {
		App.debug('App.FormsNotificationView.render()');
		var linkURL = this.model.get("serverURL");

		if (this.model.get("hasSignedConsentForm") == 0){
			linkURL = linkURL + "consent/" + this.model.get("userID")
		}
		else if (this.model.get("hasCompletedPreSurvey") ==0){
			linkURL = linkURL + "presurvey/" + this.model.get("userID")
		}
		else if(this.model.get("needsToDoPostSurvey") != null && this.model.get("needsToDoPostSurvey") == 1){
			linkURL = linkURL + "postsurvey/" + this.model.get("userID")
		}
		var html = this.template({ linkURL : linkURL, needsToDoPostSurvey : this.model.get("needsToDoPostSurvey"), hasSignedConsentForm : this.model.get("hasSignedConsentForm"), hasCompletedPreSurvey : this.model.get("hasCompletedPreSurvey") });
		this.$el.html(html);

		this.$el.find('#forms-modal').modal();
		$('#forms-modal').on('hidden.bs.modal', function (e) {
		  $('body').html("<a href='"+linkURL +"'>Click here to fill out the forms.</a>");
		})
		return this;
	},


});

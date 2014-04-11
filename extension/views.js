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
		this.map = L.mapbox.map('map', 'kanarinka.hcc1900i');//random spot -- .setView([this.getRandomInRange(-90,90,3), this.getRandomInRange(-180,180,3)], 9);
		
		App.map = this.map;
		this.citySelectorView = new App.CitySelectorView({cityCollection: this.cityCollection, model: this.userModel});
		
		var that = this;
		this.userModel.on("change:userCityVisits", function() {
		    that.cityZoomedView = new App.CityZoomedView(
				{
					model: that.cityCollection.getCityModel(that.userModel.getUnvisitedCityID())
				});
		    })
		// Create sub-views
		this.render();
	},
	
	render: function () {
		App.debug('App.MapView.render()')
		if (this.userModel.get('authenticated')) {	
			$("#hello").html('Hello, ' + this.userModel.get('userID'));
		} 
		
		return this;
	},

	renderLogin: function(){
		if (this.userModel.get('loginURL') != '' && !this.userModel.get('authenticated'))
			this.loginView = new App.LoginView({ model: this.userModel });
		else if (this.userModel.get('loginURL') != ''){
			$("#loginURL, #changeUsernameURL").attr("href", this.userModel.get('loginURL'));
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
		"click .glyphicon-thumbs-up,.glyphicon-thumbs-down": "submitHistoryItemRecommendation"
	},
	initialize: function (options) {
		App.debug('App.CityZoomedView.initialize()');
		
		this.options = options || {};
		_.bindAll(this, 'render');
		_.bindAll(this, 'clearAll');
		_.bindAll(this, 'submitRecommendation');
		_.bindAll(this, 'submitHistoryItemRecommendation');
		this.model.on('change',this.render,this);
		this.model.fetchReadingLists();
		this.model.fetchCityStats();
		this.randomWords = ["fun", "weird", "local","different","interesting","what","alternative","whoa", "notwar"];
		this.render();
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
		this.undelegateEvents();
  		$(this.el).empty();
	},
	render: function () {
		App.debug('App.CityZoomedView.render()');
		
		App.map.setView([this.model.get("lat"), this.model.get("lon")], 12);
		
		var html = this.template({ 	randomWord: this.randomWords[Math.floor(Math.random() * this.randomWords.length)], 
									population : this.addCommas(this.model.get("pop")), 
									cityID : this.model.get("geonames_id"), 
									city_name: this.model.get("city_name"), 
									country_name:this.model.get("country_name"), 
									userStories:this.model.get("userHistoryItemCollection"), 
									systemStories:this.model.get("systemHistoryItemCollection"), 
									cityStats : this.model.get("cityStats"),
									userID : App.user.get("userID"),
									serverURL : App.serverURL
								});
		this.$el.html(html);
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
		this.model.on('change:userCityVisits', this.render,this);
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
						model: cityModel
					});
				
			})
			.on("mouseover", function(d) {   

				d3.select(this).attr('fill-opacity', 1.0);
				that.$el.text(d.continent_name.toUpperCase() + " :: " + d.country_name + " :: " +d.city_name);
				if (width - d3.mouse(this)[0] < that.$el.width()){
					that.$el.css({left:d3.mouse(this)[0] - that.$el.width(),bottom:height+1});
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
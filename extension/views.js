
/**
 * Main application view.
 */
App.AppView = Backbone.View.extend({
	
	initialize: function (options) {
		App.debug('App.AppView.initialize()');
		this.options = options || {};
		this.userModel = options.userModel;
		_.bindAll(this, 'render');
		// Create models
		options.userModel.on('change:authenticated', this.render);
		// Create sub-views
		this.render();
	},
	
	render: function () {
		App.debug('App.AppView.render()')
		this.loginView = new App.LoginView({ model: this.userModel });
		
		this.$el.html('');
		
		if (this.options.userModel.get('authenticated')) {
			this.$el.append('Hello, ' + this.userModel.get('userID'))
		} else {
			this.$el.append(this.loginView.el);
		}
		return this;
	}
});

/**
 * Login form.
 */
App.LoginView = Backbone.View.extend({
	
	//template: _.template($('#tpl-login-view').html()),
	//template: TEMPLATES['tpl-login-view'],
	//el: $("#loggedIn"),  //WHY DOESNT THIS WORK, it takes el out of DOM and doesn't put it back?
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
		this.$el=$("#loggedIn");
		
		if (this.model.get("authenticated") == true)
			this.$el.html("You are logged in to Terra Incognita. <a href='"+this.model.get("loginURL")+"'>Logout</a>");
		else
			this.$el.html("You are not logged into Terra Incognita. <a href='"+this.model.get("loginURL")+"'>Login now</a>");
			//window.location.href=this.model.get("loginURL");
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
App.GeoIncognitaView = Backbone.View.extend({
	//tagName:'tr',
	template: TEMPLATES['geo-incognita-view'],
	initialize: function (options) {
		App.debug('App.GeoIncognitaView.initialize()');
		this.options = options || {};
		_.bindAll(this, 'render');	
		this.render();
	},
	render: function () {
		App.debug('App.GeoIncognitaView.render()');
		var html = this.template({ name: this.model.get("name") });
		this.$el.html(html);
		return this;
	},
});

App.UpdatingCollectionView = Backbone.View.extend({
  initialize : function(options) {
  	App.debug('App.UpdatingCollectionView.initialize()');
    _(this).bindAll('add', 'remove');
 
    if (!options.childViewConstructor) throw "no child view constructor provided";
    if (!options.childViewTagName) throw "no child view tag name provided";
 	if (options.template) this.template = TEMPLATES[options.template];
 	if (options.title) 
 		this.title = options.title; 
 	else 
 		this.title = "No title";
    this._childViewConstructor = options.childViewConstructor;
    this._childViewTagName = options.childViewTagName;
    this._childViews = [];

    this.collection.each(this.add);
 
    this.collection.bind('add', this.add);
    this.collection.bind('remove', this.remove);
  },
 
  add : function(model) {
  	App.debug('App.UpdatingCollectionView.add()');
    var childView = new this._childViewConstructor({
      tagName : this._childViewTagName,
      model : model
    });
 
    this._childViews.push(childView);
 
    if (this._rendered) {
      $(this.el).children(this._childViewTagName).last().append(childView.render().el);
    }
  },
 
  remove : function(model) {
  	App.debug('App.UpdatingCollectionView.remove()');
    var viewToRemove = _(this._childViews).select(function(cv) { return cv.model === model; })[0];
    this._childViews = _(this._childViews).without(viewToRemove);
 
    if (this._rendered) $(viewToRemove.el).remove();
  },
 
  render : function() {
  	App.debug('App.UpdatingCollectionView.render()');
    var that = this;
    this._rendered = true;
 
    $(this.el).empty();
    console.log(this.template)
    if (this.template != null){
    	
    	var html = this.template({"title":this.title});
		this.$el.html(html);
 	}
    _(this._childViews).each(function(childView) {
      $(that.el).children(this._childViewTagName).last().append(childView.render().el);
    });
 
    return this;
  }
});

/**
 * Controls drop-down menu
 */
App.ControlsView = Backbone.View.extend({
	
	//template: _.template($('#tpl-controls-view').html()),
	
	initialize: function (options) {
		App.debug('App.ControlsView.initialize()');
		this.options = options || {};
		this.userModel = options.userModel;
		_.bindAll(this, 'render');
		this.controlsSignOutView = new App.ControlsSignOutView({ userModel: this.userModel });
		this.render();
	},
	
	render: function () {
		App.debug('App.ControlsView.render()');
		this.$el.addClass('controls');
		var disabled = true;
		//this.$el.html(this.template());
		this.$el.html("PLIP");
		if (this.userModel.get('authenticated')) {
			disabled = false;
			$('ul', this.$el).append(this.controlsSignOutView.el);
		}
		if (disabled) {
			$('button', this.$el).attr('disabled', 'disabled');
		}
		return this;
	}
});

App.ControlsSignOutView = Backbone.View.extend({
	tagName: 'li',
	//template: _.template($('#tpl-controls-sign-out-view').html()),
	events: {
		'click a': 'signOut'
	},
	initialize: function (options) {
		App.debug('App.ControlSignOutView.initialize()');
		this.options = options || {}
		_.bindAll(this, 'render');
		this.render();
	},
	render: function () {
		App.debug('App.ControlSignoutView.render()');
		//this.$el.html(this.template());
		this.$el.html("PLUP");
		$('span', this.$el).html(this.options.userModel.get('username'));
		return this;
	},
	signOut: function () {
		App.debug('App.ControlsSignOutView.signOut()');
		this.options.userModel.signOut();
	}
});

from bson.objectid import ObjectId
from bson import BSON
from bson import json_util
from flask import Flask, redirect, session, render_template, json, jsonify, request
from flask.ext.browserid import BrowserID
from flask.ext.login import LoginManager
from pymongo import MongoClient
from user import *
from bitly_recommendations import *
import ConfigParser
import datetime
import httplib
import json
import os
import pprint
import pymongo
import requests
import requests.exceptions
from database_queries import *
from text_processing.geoprocessing import *
from text_processing.tasks import start_text_processing_queue
from cities_array import *
import logging

# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

app = Flask(__name__,static_url_path='')
app.secret_key= config.get('app','secret_key')
app.debug = True

# Geoserver
app.geoserver = config.get('geoparser','geoserver_url')

# MongoDB & links to each collection
db_client = MongoClient()
app.db = db_client[config.get('db','name')]
app.db_user_history_collection = app.db[config.get('db','user_history_item_collection')]
app.db_user_collection = app.db[config.get('db','user_collection')]
app.db_recommendation_collection = app.db[config.get('db','recommendation_item_collection')]

# setup logging
handler = logging.FileHandler('server.log')
logging.basicConfig(filename='server.log',level=logging.DEBUG)
log = logging.getLogger('server')
log.info("---------------------------------------------------------------------------")

# ------------------------- -------------------------------------
# MOVE THIS SOMEWHERE ELSE
# This callback is used to reload the user object from the user ID stored in the session.
# It should take the unicode ID of a user, and return the corresponding user object.
# It should return None (not raise an exception) if the ID is not valid.
# (In that case, the ID will manually be removed from the session and processing will continue.)
def get_user_by_id(id):
	user = None
	for row in app.db_user_collection.find({ '_id': ObjectId(id) }):
		user = get_user_from_DB_row(row)
		user.lastLoginDate = datetime.datetime.utcnow();
		break
	if (user is not None):
		app.db_user_collection.save(user.__dict__)
	return user


#	Given the response from BrowserID, finds or creates a user.
#	If a user can neither be found nor created, returns None.
#	NOTE THAT ID must be converted to STRING from MongoDB
def get_user_for_browserid(kwargs):
	
	for row in app.db_user_collection.find({ 'email': kwargs.get('email') }):
		if row is not None:
			return get_user_from_DB_row(row)
	for row in app.db_user_collection.find({ '_id': kwargs.get('id') }):
		if row is not None:
			return get_user_from_DB_row(row)
	# not found - create the user
	return create_browserid_user(kwargs)


#	Takes browserid response and creates a user.
def create_browserid_user(kwargs):
	
	if kwargs['status'] == 'okay':
		user = create_new_user(kwargs["email"])
		
		user_id = app.db_user_collection.insert(user.__dict__)
		user._id = user_id
		return user
	else:
		return None

# END MOVE THIS SOMEWHERE ELSE
# ------------------------- -------------------------------------

#Mozilla Persona
login_manager = LoginManager()
login_manager.user_loader(get_user_by_id)
login_manager.init_app(app)

browser_id = BrowserID()
browser_id.user_loader(get_user_for_browserid)
browser_id.init_app(app)

#Index test 
@app.route('/')
@app.route('/index.html')
@app.route('/index.htm')
def hello():
	return app.send_static_file('googleForm.html')

#Index test 
@app.route('/1000cities')
@app.route('/1000cities.html')
@app.route('/1000cities.htm')
def cities():
	return app.send_static_file('1000cities.html')


#Send user their city data
#consider storing 1000 cities data in localstorage for faster retrieval later
@app.route('/user/<userID>')
@app.route('/user/')
def user(userID='52dbeee6bd028634678cd069'):
	if (userID is not None):
		
		userData = {"userID":userID,"cities":[], "last10HistoryItems":[]}
		cursor = app.db_user_history_collection.find({ "geodata.primaryCities.id": { "$in": THE1000CITIES_IDS_ARRAY },"userID":userID }, {"typedCount":1,"title":1,"url":1,"lastVisitTime":1,"geodata.primaryCities":1,"visitCount":1}).sort([("lastVisitTime",-1)]).skip(0).limit(10)
		last10HistoryItems = list( record for record in cursor)

		cities = {}
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=CITY_COUNT_PIPELINE ) 
		for row in q["result"]:
			geonames_id = row["_id"]["geonames_id"]
			count = row["count"]
			cities[geonames_id] = count

		userData["cities"] = cities
		userData["last10HistoryItems"] = last10HistoryItems

		return json.dumps(userData, sort_keys=True, indent=4, default=json_util.default) 
	else:
		return jsonify(error='No user ID specified');

@app.route('/readinglist/<userID>/<cityID>')
@app.route('/readinglist/')
def get_reading_list(userID='52dbeee6bd028634678cd069',cityID=703448):
	cityID = int(cityID)
	result = {"userHistoryItemCollection":[], "systemHistoryItemCollection":[]}
	#cursor = app.db_user_history_collection.find({"userID":userID, "geodata.primaryCities": { "$elemMatch": { "id": int(cityID) } } }, {"url":1,"title":1}).sort([("lastVisitTime",-1)]).skip(0).limit(100)
	
	USER_CITY_HISTORY_PIPELINE = [
		
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": userID, "title":{"$ne":"" } }},
		{ "$sort" : { "lastVisitTime" : 1 } },
		{ "$group": {"_id": {"url":"$url", "title":"$title" }, "count": {"$sum": 1}}},
		{ "$limit" : 50 },
		
	]
	q = app.db_user_history_collection.aggregate(USER_CITY_HISTORY_PIPELINE)

	result["userHistoryItemCollection"] = list(row["_id"] for row in q["result"])
	
	#cursor = app.db_user_history_collection.find({"userID":{ "$ne": userID }, "geodata.primaryCities": { "$elemMatch": { "id": int(cityID) } } }, {"url":1,"title":1}).sort([("lastVisitTime",-1)]).skip(0).limit(100)
	
	SYSTEM_CITY_HISTORY_PIPELINE = [
		
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": {"$ne" : userID}, "title":{"$ne":"" } }},
		{ "$sort" : { "lastVisitTime" : 1 } },
		{ "$group": {"_id": {"url":"$url", "title":"$title" }, "count": {"$sum": 1}}},
		{ "$limit" : 50 },
		
	]
	q = app.db_user_history_collection.aggregate(SYSTEM_CITY_HISTORY_PIPELINE)

	result["systemHistoryItemCollection"] = list(row["_id"] for row in q["result"])
	return json.dumps(result, sort_keys=True, indent=4, default=json_util.default) 

#Test Aggregation Pipeline db requests
@app.route('/testdb/<userID>/<cityID>')
@app.route('/testdb/')
def testdb(userID='52dbeee6bd028634678cd069',cityID=4930956):
	result = {"firstVisitUserID":[], "mostReadUserID":[], "firstRecommendationUserID":[], "mostRecommendationUserID":[]}

	#first person to visit city
	firstVisitUserID = ''
	cursor = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID}, {userID:1}).sort([("lastVisitTime",1)]).skip(0).limit(1)
	if cursor.count() != 0:
		firstVisitUserID = str(cursor[0]["_id"])
	result["firstVisitUserID"] = firstVisitUserID

	#person with most articles read about city
	USER_WITH_MOST_READ_PIPELINE = [
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": {"$exists":"true"} }},		
		{ "$group": {"_id": "$userID", "count": {"$sum": 1}}},
		{ "$sort" : {"count" : -1} },
		{ "$limit" : 1 },
	]
	q = app.db_user_history_collection.aggregate(USER_WITH_MOST_READ_PIPELINE)
	result["mostReadUserID"] = list(row for row in q["result"])

	#first person to recommend article from city
	firstRecommendationUserID = ''
	cursor = app.db_recommendation_collection.find({"cityIDS.id" : cityID}, {userID:1}).sort([("dateEntered",1)]).skip(0).limit(1)
	if cursor.count() != 0:
		firstRecommendationUserID = str(cursor[0]["userID"])
	result["firstRecommendationUserID"] = firstRecommendationUserID

	#person with most recommendations from city
	USER_WITH_MOST_RECOMMENDED_PIPELINE = [
		{ "$match" : { "cityIDS.id": cityID, "userID": {"$exists":"true"} }},		
		{ "$group": {"_id": "$userID", "count": {"$sum": 1}}},
		{ "$sort" : {"count" : -1} },
		{ "$limit" : 1 },
	]
	q = app.db_recommendation_collection.aggregate(USER_WITH_MOST_RECOMMENDED_PIPELINE)
	result["mostRecommendationUserID"] = list(row for row in q["result"])

	return json.dumps(result, sort_keys=True, indent=4, default=json_util.default) 

#Send user their map data
@app.route('/map/<user>')
def map(user=None):
	if (user is not None):
		userHistory = {"continents":[],"continents_incognita":[],"regions":[],"regions_incognita":[],"countries":[],"countries_incognita":[], "states":[], "cities":[],"cities_incognita":[]}
		
		#continents
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=CONTINENT_COUNT_PIPELINE )
		userHistory["continents"].append(q['result'])
		inverted = invertGeodata(userHistory["continents"][0], "continent")
		userHistory["continents_incognita"].append(inverted)

		#regions
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=REGION_COUNT_PIPELINE )
		userHistory["regions"].append(q['result'])
		userHistory["regions_incognita"].append(invertGeodata(userHistory["regions"][0], "region"))

		#countries
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=COUNTRY_COUNT_PIPELINE )
		userHistory["countries"].append(q['result'])
		userHistory["countries_incognita"].append(invertGeodata(userHistory["countries"][0], "nation"))

		#states
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=STATE_COUNT_PIPELINE )
		userHistory["states"].append(q['result'])

		#cities
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=CITY_COUNT_PIPELINE )
		userHistory["cities"].append(q['result'])
		userHistory["cities_incognita"].append(invertGeodata(userHistory["cities"][0], "city"))
		
		return json.dumps(userHistory, sort_keys=True, indent=4, default=json_util.default) 
	else:
		return jsonify(error='No user ID specified');

#Send user to an exciting destination
@app.route('/go/<cityID>')
def go(cityID=None):
	url = "http://globalvoicesonline.org"
	url = get_recommended_url(cityID)
	return redirect(url, code=302)

@app.route('/history/', methods=['POST'])
def processHistory():
	print "Processing browser history"
	historyItems = json.loads(request.form['history'])

	for historyObject in historyItems:
		historyObject["preinstallation"] = "true";
		start_text_processing_queue.delay(historyObject, config)
	
	return 'Celery is processing ' + str(len(historyItems)) + ' history items'

#Login/Logout page
@app.route('/login/')
def loginpage():
	return render_template('login.html')


# Receives a single URL object from user and starts celery text processing queue
@app.route('/monitor/', methods=['POST','GET'])
def processURL():
	print "Receiving new URL"
	historyObject = json.loads(request.form['logURL'])
	start_text_processing_queue.delay(historyObject, config)
	return 'Celery is processing your URL dude - ' + historyObject["url"]

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
	print "Started Server"

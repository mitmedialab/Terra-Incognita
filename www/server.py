
from bson.objectid import ObjectId
from bson import BSON
from bson import json_util
from flask import Flask, redirect, session, render_template, json, jsonify, request
from flask.ext.browserid import BrowserID
from flask.ext.login import LoginManager
from pymongo import MongoClient
from user import *
from recommendations_bitly import *
import ConfigParser
import datetime
import httplib
import json
import os
import pprint
import pymongo
import requests
import requests.exceptions
from text_processing.geoprocessing import *
from text_processing.tasks import start_text_processing_queue
from cities_array import *
import logging
from random import shuffle,randint
from text_processing.content_extraction import *

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
	log.info("server.py >> get_user_by_id")
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
	log.info("server.py >> get_user_for_browserid")
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
	log.info("server.py >> create_browserid_user")
	log.info("server.py >> create_browserid_user >> kwargs")
	log.info(kwargs)
	if kwargs['status'] == 'okay':
		user = create_new_user(kwargs["email"])
		log.info("server.py >> create_browserid_user >> Created new user")
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
	CITY_COUNT_PIPELINE = [
		{ "$unwind" : "$geodata.primaryCities" },
		{ "$match" : { "userID":userID, "geodata.primaryCities.id": {"$in": THE1000CITIES_IDS_ARRAY } }},
		{ "$group": {"_id": {"geonames_id":"$geodata.primaryCities.id" }, "count": {"$sum": 1}}},
		{ "$sort" : { "count" : -1 } }
	]
	if (userID is not None):
		
		userData = {"userID":userID,"cities":[], "last10HistoryItems":[]}
		
		# removing last 10 history items for the moment
		#cursor = app.db_user_history_collection.find({ "geodata.primaryCities.id": { "$in": THE1000CITIES_IDS_ARRAY },"userID":userID }, {"typedCount":1,"title":1,"url":1,"lastVisitTime":1,"geodata.primaryCities":1,"visitCount":1}).sort([("lastVisitTime",-1)]).skip(0).limit(10)
		#last10HistoryItems = list( record for record in cursor)
		#userData["last10HistoryItems"] = last10HistoryItems
		
		cities = {}
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=CITY_COUNT_PIPELINE ) 
		for row in q["result"]:
			geonames_id = row["_id"]["geonames_id"]
			count = row["count"]
			cities[geonames_id] = count

		userData["cities"] = cities
		

		return json.dumps(userData, sort_keys=True, indent=4, default=json_util.default) 
	else:
		return jsonify(error='No user ID specified');

@app.route('/readinglist/<userID>/<cityID>')
@app.route('/readinglist/')
def get_reading_list(userID='53303d525ae18c2083bcc6f9',cityID=4930956):
	cityID = int(cityID)
	result = {"userHistoryItemCollection":[], "systemHistoryItemCollection":[]}
	#cursor = app.db_user_history_collection.find({"userID":userID, "geodata.primaryCities": { "$elemMatch": { "id": int(cityID) } } }, {"url":1,"title":1}).sort([("lastVisitTime",-1)]).skip(0).limit(100)
	
	USER_CITY_HISTORY_PIPELINE = [
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": userID }},
		{ "$unwind" : "$geodata.primaryCities" },
		{ "$sort" : { "lastVisitTime" : 1, "geodata.primaryCities.recommended" : -1 } },
		{ "$group": {"_id": {"url":"$url", "title":"$title"}, "recommended": { "$first" : "$geodata.primaryCities.recommended" }, "count": {"$sum": 1}}},
		{ "$limit" : 50 },
		
	]
	q = app.db_user_history_collection.aggregate(USER_CITY_HISTORY_PIPELINE)
	for row in q["result"]:
		result["userHistoryItemCollection"].append({ "title": row["_id"]["title"], "url":row["_id"]["url"], "recommended":row["recommended"]})
	#result["userHistoryItemCollection"] = list(row for row in q["result"])
	
	SYSTEM_CITY_HISTORY_PIPELINE = [
		
		{ "$match" : { "geodata.primaryCities.id": cityID, "geodata.primaryCities.recommended": {"$ne" : 0}, "userID": {"$ne" : userID}, "title":{"$ne":"" } }},
		{ "$sort" : { "geodata.primaryCities.recommended":1, "lastVisitTime" : 1 } },
		{ "$group": {"_id": {"url":"$url", "title":"$title" }, "count": {"$sum": 1}}},
		{ "$limit" : 50 },
		
	]
	q = app.db_user_history_collection.aggregate(SYSTEM_CITY_HISTORY_PIPELINE)
	systemHistoryItemCollection = list(row["_id"] for row in q["result"])

	# If not much in the way of system history, then grab recommendations from the recs DB
	# Todo: randomize access so doesn't always show the top 20
	if len(systemHistoryItemCollection) < 10:
		RECOMMENDATION_PIPELINE = [
			{ "$match" : { "geodata.primaryCities.id": cityID, "title":{"$ne":"" } }},
			{ "$sort" : { "_id" : 1 } },
			{ "$group": {"_id": {"url":"$url", "title":"$title" }, "count": {"$sum": 1}}},
			{ "$limit" : 20 },
		]
		q = app.db_recommendation_collection.aggregate(RECOMMENDATION_PIPELINE)

		systemHistoryItemCollection.extend(list(row["_id"] for row in q["result"]))
		shuffle(systemHistoryItemCollection)
	result["systemHistoryItemCollection"] = systemHistoryItemCollection
	return json.dumps(result, sort_keys=True, indent=4, default=json_util.default) 

@app.route('/recommend/<userID>/<cityID>/', methods=['GET'])
@app.route('/recommend/', methods=['GET'])
def recommend(userID='53303d525ae18c2083bcc6f9',cityID=4990729):
	cityID = int(cityID)
	url=request.args.get('url')
	
	if len(url) < 1:
		return json.dumps({"error":"no url"}, sort_keys=True, indent=4, default=json_util.default)
	
	if not url.startswith('http'):
		url = "http://" + url
	doc = {}
	doc["url"] = url
	newDoc = extractSingleURL(doc)
	if newDoc:
		doc = newDoc
	else:
		doc["title"] = url

	
	doc["source"] = "user"
	doc["userID"] = userID
	doc["geodata"] = {}
	doc["geodata"]["primaryCities"] = []
	doc["geodata"]["primaryCities"].append({"id" : cityID})
	
	doc = addCityGeoDataToDoc(doc)
	
	app.db_recommendation_collection.insert(doc)
	return json.dumps({"response":"ok"}, sort_keys=True, indent=4, default=json_util.default) 

@app.route('/like/<userID>/<cityID>/', methods=['GET'])
@app.route('/like/', methods=['GET'])
def like(userID='53303d525ae18c2083bcc6f9',cityID=4990729):
	cityID = int(cityID)
	
	url=request.args.get('url')

	isThumbsUp=request.args.get('isThumbsUp')
	if isThumbsUp == "true":
		isThumbsUp=1
	else:
		isThumbsUp=0
	
	if len(url) < 1:
		return json.dumps({"error":"no url"}, sort_keys=True, indent=4, default=json_util.default)

	# update docs associated with this user and this url and particular city
	# set recommended/not recommended property on geodata.primaryCities.city item
	# because what they are giving feedback on is relevance of that article for that particular city
	# article could still be good/bad rec related to a different geo
	 
	app.db_user_history_collection.update({	"userID":userID,
												"url":url,
												"geodata.primaryCities": { "$elemMatch": { "id": cityID } } },
												{ "$set" : {"geodata.primaryCities.$.recommended": isThumbsUp } },
												upsert=False,
												multi=True)
	result = app.db.command({"getLastError" : 1})
	return json.dumps({"response": "ok", "count" : result["n"]}, sort_keys=True, indent=4, default=json_util.default) 

@app.route('/citystats/<userID>/<cityID>')
@app.route('/citystats/')
def citystats(userID='53303d525ae18c2083bcc6f9',cityID=4930956):
	cityID = int(cityID)
	result = {	"firstVisitUsername":"", 
				"mostRead":{}, 
				"firstRecommendationUsername":"", 
				"mostRecommendations":{},
				"currentUserStoryCount":"",
				"currentUserRecommendationCount":""
			}
	currentUsername = getUsername(userID)
	
	#current user counts
	result["currentUserStoryCount"] = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID, "userID" : userID }).skip(0).count()
	
	#recommendations come from two different collections and get added together
	userRecs = app.db_recommendation_collection.find({"geodata.primaryCities.id" : cityID, "userID" : userID }).skip(0).count();
	userHistoryRecs = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID, "geodata.primaryCities.recommended" : {"$exists" : 1}, "userID" : userID }).skip(0).count();
	result["currentUserRecommendationCount"] = userRecs + userHistoryRecs;
	
	#first person to visit city
	firstVisitUserID = ''
	cursor = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID, "userID" : {"$exists" : "true"}}, {"userID" :1}).sort([("lastVisitTime",1)]).skip(0).limit(1)
	if cursor.count() != 0:
		doc = cursor.next()
		firstVisitUserID = doc["userID"]
		result["firstVisitUsername"] = getUsername(firstVisitUserID)

	#person with most articles read about city
	USER_WITH_MOST_READ_PIPELINE = [
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": {"$exists":"true"} }},		
		{ "$group": {"_id": "$userID", "count": {"$sum": 1}}},
		{ "$sort" : {"count" : -1} },
		{ "$limit" : 1 },
	]
	q = app.db_user_history_collection.aggregate(USER_WITH_MOST_READ_PIPELINE)
	if q["result"]:
		mostReadUsername = getUsername(q["result"][0]["_id"])
		result["mostRead"] = { 	"count" : q["result"][0]["count"], 
								"username" : mostReadUsername,
								"isCurrentUser" : "true" if mostReadUsername == currentUsername else "false"	
							}

	# first person to recommend article from city
	# compare from recommendations and from user history table
	firstRecommendationUsername = ''
	doc = ''
	userRecs = app.db_recommendation_collection.find({"geodata.primaryCities.id" : cityID, "userID" : {"$exists" : "true"}}, {"userID" :1,"dateEntered":1}).sort([("dateEntered",1)]).skip(0).limit(1)
	userHistoryRecs = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID, "userID" : {"$exists" : "true"}, "geodata.primaryCities.recommended": {"$exists":"true"}}, {"userID" :1,"lastVisitTime":1}).sort([("lastVisitTime",1)]).skip(0).limit(1)
	if userRecs.count() != 0 and userHistoryRecs.count() != 0:
		userRecDoc = userRecs.next()
		userHistoryRecDoc = userHistoryRecs.next()
		doc = userHistoryRecDoc
		if userRecDoc["dateEntered"] < userHistoryRecDoc["lastVisitTime"]:
			doc = userRecDoc
	elif userRecs.count() != 0:
		doc = userRecs.next()
	elif userHistoryRecs.count() != 0:
		doc = userHistoryRecs.next()
	if doc:
		firstRecommendationUserID = doc["userID"]
		firstRecommendationUsername = getUsername(firstRecommendationUserID)
	result["firstRecommendationUsername"] = firstRecommendationUsername

	# person with most recommendations from city
	# do two queries because recommendations can be either new urls or "likes"
	USER_WITH_MOST_RECOMMENDED_PIPELINE = [
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": {"$exists":"true"} }},		
		{ "$group": {"_id": "$userID", "count": {"$sum": 1}}},
		{ "$sort" : {"count" : -1} },
		{ "$limit" : 1 },
	]
	USER_WITH_MOST_HISTORY_RECOMMENDED_PIPELINE = [
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": {"$exists":"true"}, "geodata.primaryCities.recommended": {"$exists":"true"} }},		
		{ "$group": {"_id": "$userID", "count": {"$sum": 1}}},
		{ "$sort" : {"count" : -1} },
		{ "$limit" : 1 },
	]
	q = app.db_recommendation_collection.aggregate(USER_WITH_MOST_RECOMMENDED_PIPELINE)
	q2 = app.db_user_history_collection.aggregate(USER_WITH_MOST_HISTORY_RECOMMENDED_PIPELINE)
	qResult = False
	if q["result"] and q2["result"]:
		qResult = q["result"][0]
		if q["result"][0]["count"] < q2["result"][0]["count"]:
			qResult = q2["result"][0]
	elif q["result"]:
		qResult = q["result"][0]
	elif q2["result"]:
		qResult = q2["result"][0]
	if qResult:
		mostRecommendationsUsername = getUsername(qResult["_id"])
		result["mostRecommendations"] = { 	"count" : qResult["count"], 
											"username" : mostRecommendationsUsername,
											"isCurrentUser" : "true" if mostRecommendationsUsername == currentUsername else "false"

										}

	return json.dumps(result, sort_keys=True, indent=4, default=json_util.default) 

#Test Aggregation Pipeline db requests
@app.route('/testdb/<userID>/<cityID>')
@app.route('/testdb/')
def testdb(userID='52dbeee6bd028634678cd069',cityID=4930956):
	return "hi"

def getUsername(userID):
	doc = app.db_user_collection.find({"_id": ObjectId(userID)}, {"username":1}).skip(0).limit(1).next()
	return doc["username"]

#Send user their map data
#This is outdated and not currently used
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

# Send user to an exciting destination
# 1/3 the time it gets a recommendation from bitly
# 1/3 the time it gets a recommendatino from the recommendation collection
# 1/3 the time it gets a recommendation from another user

# if the latter two methods don't work then fall back on bitly
@app.route('/go/')
@app.route('/go/<cityID>')
@app.route('/go/<userID>/<cityID>')
def go(userID='52dbeee6bd028634678cd069',cityID=703448):
	cityID = int(cityID)
	url = ''
	random = randint(0,2)
	if random == 0:
		print "Recommendation from Bitly"
		url = get_recommended_bitly_url(cityID)
	elif random == 1:
		print "Recommendation from recommendation collection"
		count = app.db_recommendation_collection.find({ "geodata.primaryCities.id": cityID }, {url:1}).count()
		if count:
			doc = app.db_recommendation_collection.find({ "geodata.primaryCities.id": cityID }).skip(randint(1, count - 1)).limit(1).next()
			url = doc["url"]
	elif random == 2:
		print "Recommendation from user history collection"
		count = app.db_user_history_collection.find({ "geodata.primaryCities.id": cityID, "userID": {"$ne" : userID} }, {url:1}).count()
		if count:
			doc = app.db_user_history_collection.find({ "geodata.primaryCities.id": cityID, "userID": {"$ne" : userID} }).skip(randint(1, count - 1)).limit(1).next()
			url = doc["url"]

	if not url:
		print "Fallback recommendation from Bitly"
		url = get_recommended_bitly_url(cityID)

	return redirect(url, code=302)

@app.route('/history/', methods=['POST'])
def processHistory():
	print "Processing browser history"
	historyItems = json.loads(request.form['history'])

	for historyObject in historyItems:
		historyObject["preinstallation"] = "true";
		args = (historyObject, config, False);
		start_text_processing_queue.delay(*args)
	
	return 'Celery is processing ' + str(len(historyItems)) + ' history items'

#Login/Logout page AND change username
@app.route('/login/', methods=['GET', 'POST'])
def loginpage():
	error = ""
	if request.method == 'POST':
		oldusername = request.form['oldusername']
		newusername = request.form['newusername']
		userID = request.form['userID']
		
		if newusername == oldusername:
			error="Your new username is the same as your old username"
		elif app.db_user_collection.find({ "username": newusername }).count():
			error = "That username already exists"
		else:
			r = app.db_user_collection.update({ "_id": ObjectId(userID)}, { "$set" : {"username":newusername}})
			
	return render_template('login.html', error=error)


# Receives a single URL object from user and starts celery text processing queue
@app.route('/monitor/', methods=['POST','GET'])
def processURL():
	print "Receiving new URL"
	historyObject = json.loads(request.form['logURL'])
	args = (historyObject, config, False);

	start_text_processing_queue.delay(*args)
	return 'Celery is processing your URL dude - ' + historyObject["url"]

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
	print "Started Server"

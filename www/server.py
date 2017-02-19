from flask import Flask, Response, redirect, session, render_template, json, jsonify, request, make_response, url_for
from flask_login import LoginManager, login_user, logout_user
from flask_oauthlib.client import OAuth, OAuthException
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import BSON
from bson import json_util
from terra_incognita_user import *
from recommendations_bitly import *
import ConfigParser
import time
import httplib
import json
import os
import pprint
import requests
import requests.exceptions
from text_processing.textprocessing import *
from cities_array import *
import logging
from random import shuffle,randint
import datetime
import csv


# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR,'logs')

# constant for data analysis
MINIMUM_DAYS_OF_DATA = 5 	#user must have at least 5 days of data pre and post installation
MINIMUM_HISTORY_COUNT = 10 #user must have at least 10 items pre and post installation

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

app = Flask(__name__,static_url_path='')
app.secret_key= config.get('app','secret_key')
app.debug = True

# Geoserver
app.geoserver = config.get('geoparser','geoserver_url')

# MongoDB & links to each collection
uri = "mongodb://"+ config.get('db','user')+ ":"+ config.get('db','pass')+"@" +config.get('db','host') + ":" + config.get('db','port')
db_client = MongoClient(uri)
app.db = db_client[config.get('db','name')]

app.db_user_history_collection = app.db[config.get('db','user_history_item_collection')]
app.db_user_collection = app.db[config.get('db','user_collection')]
app.db_recommendation_collection = app.db[config.get('db','recommendation_item_collection')]
app.db_user_behavior_collection = app.db[config.get('db','user_behavior_collection')]
app.db_user_city_clicks_collection = app.db[config.get('db','user_city_clicks_collection')]

# setup logging
handler = logging.FileHandler(os.path.join(LOG_DIR,'terra-flask-server.log'))
logging.basicConfig(filename=os.path.join(LOG_DIR,'terra-flask-server.log'),level=logging.DEBUG)
log = logging.getLogger('server')
log.info("---------------------------------------------------------------------------")

#Index test
@app.route('/')
@app.route('/index.html')
@app.route('/index.htm')
def hello():
	return app.send_static_file('index.html')

#Index test
@app.route('/1000cities')
@app.route('/1000cities.html')
@app.route('/1000cities.htm')
def cities():
	return app.send_static_file('1000cities.html')

@app.route('/consent/<userID>', methods=['GET', 'POST'])
def consentForm(userID):
	error = ""
	today = datetime.date.today()
	signature = ''
	signature_date = ''
	researcher_signature_date = False

	if request.method == 'GET':
		user = app.db_user_collection.find({ "_id": ObjectId(userID)}).next()

		if "signed_consent" in user:
			signature = user['signature']
			signature_date = user['signature_date']
			researcher_signature_date = user['researcher_signature_date']
	elif request.method == 'POST':
		user = app.db_user_collection.find({ "_id": ObjectId(userID)}).next()
		user["signed_consent"] = 1
		user["signature"] = request.form['signature']
		user["signature_date"] = request.form['signature_date']
		user["researcher_signature_date"] = today.strftime('%m-%d-%Y')
		userID = request.form['userID']

		if user["signature"] == "":
			error="Please enter your signature."
		elif user["signature_date"] == "":
			error = "Please enter today's date."
		else:
			app.db_user_collection.save(user)
			if 'filled_out_presurvey' in user and user['filled_out_presurvey'] == 1:
				return redirect('/login')
			else:
				return redirect('/presurvey/'+userID)

	return render_template('couhes/consentform.htm', error=error, userID=userID, today=today.strftime('%m-%d-%Y'), signature=signature, signature_date=signature_date, researcher_signature_date=researcher_signature_date)

@app.route('/formsfilledout/<userID>/')
@app.route('/formsfilledout/<userID>')
def formsfilledout(userID):


	needsToDoPostSurvey = 0
	userDoc = app.db_user_collection.find({ "_id": ObjectId(userID)},{"history-pre-installation":0}).next()

	hasSignedConsentForm = 1 if "signed_consent" in userDoc and int(userDoc["signed_consent"]) == 1 else 0
	hasCompletedPreSurvey = 1 if "filled_out_presurvey" in userDoc and int(userDoc["filled_out_presurvey"]) == 1 else 0

	# check if they've already completed it
	# they can't complete postsurvey without already having filled out other forms
	hasCompletedPostSurvey = 1 if "filled_out_postsurvey" in userDoc and int(userDoc["filled_out_postsurvey"]) == 1 else 0
	if (hasCompletedPostSurvey > 0 or not hasCompletedPreSurvey or not hasSignedConsentForm):
		needsToDoPostSurvey = 0

	# check for having been in system at least 30 days
	else:
		firstLoginDate = datetime.datetime.fromtimestamp(int(userDoc["firstLoginDate"]/1000))
		nowDate = datetime.datetime.now()

		dateDiff = nowDate - firstLoginDate
		if ( dateDiff.days >= 30):
			needsToDoPostSurvey = 1

	return json.dumps({"needsToDoPostSurvey":needsToDoPostSurvey,"hasSignedConsentForm":hasSignedConsentForm, "hasCompletedPreSurvey":hasCompletedPreSurvey}, sort_keys=True, indent=4, default=json_util.default)

@app.route('/postsurveyrankings/<userID>', methods=['GET', 'POST'])
def postsurveyrankings(userID):
	userCities = getAllUserCityCounts()
	totalUserCount = app.db_user_collection.count()

	ranking = 1
	for row in userCities:
		if userID == str(row["_id"]["userID"]):
			cityCount = row["totalcitiesvisited"]
			break
		ranking=ranking+1

	return json.dumps({"cityCount":cityCount,"totalUserCount":totalUserCount, "ranking":ranking}, sort_keys=True, indent=4, default=json_util.default)

@app.route('/postsurvey/<userID>', methods=['GET', 'POST'])
def postsurvey(userID):
	error={}
	errorCount = 0
	responses={}
	postsurvey={}


	if request.method == 'POST':
		user = app.db_user_collection.find({ "_id": ObjectId(userID)}).next()
		fields = 	[	'Q1chromeprimarybefore',
						'Q2chromeprimaryafter',
						'Q3globalnewsimportanttowork',
						'Q4raterecommendations',
						'Q5topreaderorrecommender',
						'Q6searchtobecometopreader',
						'Q7searchtocollectmorecities',
						'Q8share',
						'Q9reflect',
						'Q10reflect_explain',
						'Q11newplace',
						'Q12newplace_explain',
						'Q13badarticles',
						'Q14badarticles_explain',
						'Q15goodarticles',
						'Q16goodarticles_explain',
						'Q17improverecommendations',
						'Q18rankings_explain',
						'Q19improverankings',
						'Q20feelings_explain',
						'Q21anythingelse_explain',
						'Q22contactyou',
						'Q23seeleaderboard'
					]
		for field in fields:

			if (field in request.form and len(request.form[field]) > 0) or (field in request.form and len(request.form[field]) == 0 and "_explain" in field):
				postsurvey[field]=request.form[field]
				error[field]=0
			else:
				error[field]=1
				errorCount+=1
		if errorCount==0:
			user["filled_out_postsurvey"] =1
			user["postsurvey"]=postsurvey
			app.db_user_collection.save(user)
			return redirect('/login')
		else:
			responses=request.form
		print error

	return render_template('postsurvey.html', userID=userID, error=error,errorCount=errorCount, responses=responses)

@app.route('/presurvey/<userID>', methods=['GET', 'POST'])
def presurvey(userID):
	error={}
	errorCount = 0
	responses={}
	if request.method == 'POST':
		user = app.db_user_collection.find({ "_id": ObjectId(userID)}).next()
		fields = 	[	'Q1gender',
						'Q2country',
						'Q3fair',
						'Q4profession',
						'Q5language',
						'Q6newsreading',
						'Q7newsimportance',
						'Q8family',
						'Q9friendsabroad',
						'Q10foreignfriends',
						'Q11travel',
						'Q12liveabroad'
					]
		for field in fields:
			if field in request.form and len(request.form[field]) > 0:
				user[field]=request.form[field]
				error[field]=0
			else:
				error[field]=1
				errorCount+=1
		if errorCount==0:
			user["filled_out_presurvey"] =1
			app.db_user_collection.save(user)
			return redirect('/login')
		else:
			responses=request.form
		print error

	return render_template('presurvey.html', userID=userID, error=error,errorCount=errorCount, responses=responses)


# queries for user visits by city
def getUserCityCounts(userID):
	CITY_COUNT_PIPELINE = [
		{ "$unwind" : "$geodata.primaryCities" },
		{ "$match" : { "userID":userID, "preinstallation":{"$exists":0}, "geodata.primaryCities.id": { "$in": THE1000CITIES_IDS_ARRAY } }},
		{ "$group": {"_id": {"geonames_id":"$geodata.primaryCities.id" }, "count": {"$sum": 1}}},
		{ "$sort" : { "count" : -1 } }
	]
	q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=CITY_COUNT_PIPELINE )
	return q["result"]

# queries for all user visits by city
def getAllUserCityCounts():
	ALL_USERS_CITY_COUNT_PIPELINE = [
		{ "$unwind" : "$geodata.primaryCities" },
		{ "$match" : { "preinstallation":{"$exists":0}, "geodata.primaryCities.id": { "$in": THE1000CITIES_IDS_ARRAY } }},
		{ "$group": {"_id": {"userID":"$userID", "geonames_id":"$geodata.primaryCities.id" }, "count": {"$sum": 1}}},

		{ "$group": {"_id": {"userID":"$_id.userID"}, "totalcitiesvisited": {"$sum": 1}}},
		{ "$sort" : { "totalcitiesvisited" : -1 } }
	]
	q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=ALL_USERS_CITY_COUNT_PIPELINE )
	return q["result"]

#Send user their city data
#consider storing 1000 cities data in localstorage for faster retrieval later
@app.route('/user/<userID>')
@app.route('/user/')
def user(userID='52dbeee6bd028634678cd069'):

	if (userID is not None):

		userData = {"userID":userID,"username":getUsername(userID), "cities":[]}

		# removing last 10 history items for the moment
		#cursor = app.db_user_history_collection.find({ "geodata.primaryCities.id": { "$in": THE1000CITIES_IDS_ARRAY },"userID":userID }, {"typedCount":1,"title":1,"url":1,"lastVisitTime":1,"geodata.primaryCities":1,"visitCount":1}).sort([("lastVisitTime",-1)]).skip(0).limit(10)
		#last10HistoryItems = list( record for record in cursor)
		#userData["last10HistoryItems"] = last10HistoryItems

		cities = {}

		result = getUserCityCounts(userID)
		for row in result:
			geonames_id = row["_id"]["geonames_id"]
			count = row["count"]
			cities[geonames_id] = count

		userData["cities"] = cities


		return json.dumps(userData, sort_keys=True, indent=4, default=json_util.default)
	else:
		return jsonify(error='No user ID specified')
# exports all city clicks as counts
# exclude developers
@app.route('/totalusercount/')
def totalusercount():
	count = app.db_user_collection.find({}).count()
	preinstallneedsprocessing = app.db_user_collection.find({ "history-pre-installation": {"$exists":1}, "history-pre-installation-processed":{"$exists":0}}).count()
	return json.dumps({"count":count, "preinstallneedsprocessing":preinstallneedsprocessing}, sort_keys=True, indent=4, default=json_util.default)

# exports all city clicks as counts
# exclude developers
@app.route('/exportcityclicks/')
def exportcities():
	result=[]
	CITY_CLICK_COUNT_PIPELINE = [
		{ "$match" : {"$and": [{ "userID":{"$ne":"53401d97c183f236b23d0d40"}}, { "userID":{"$ne":"5345c2f9c183f20b81e78eec"}}] }},
		{ "$group": {"_id": {"cityID":"$cityID" }, "count": {"$sum": 1}}},
		{ "$sort" : { "count" : -1 } }
	]
	q = app.db.command('aggregate', config.get('db','user_city_clicks_collection'), pipeline=CITY_CLICK_COUNT_PIPELINE )
	for row in q["result"]:
		cityID=row["_id"]["cityID"]
		for city in THE1000CITIES:
			if int(city["geonames_id"]) == int(cityID):
				cityname = city["city_name"]
				result.append({"name":cityname, "count":row["count"]})
		print cityID

	return json.dumps(result, sort_keys=True, indent=4, default=json_util.default)

# Export presurvey data to CSV
# not currently filtering for days in system or creator IDs
@app.route('/exportpresurvey')
def exportpresurvey():
	test_file = open(app.static_folder + '/data/exportpresurvey.csv','wb')
	fieldnames = ["userID","username", "Q1gender", "Q2country", "Q3fair", "Q4profession", "Q5language", "Q6newsreading", "Q7newsimportance", "Q8family", "Q9friendsabroad", "Q10foreignfriends", "Q11travel", "Q12liveabroad"]
	csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
	csvwriter.writeheader()

	cursor = app.db_user_collection.find({},{"username":1, "Q1gender":1, "Q2country":1, "Q3fair":1, "Q4profession":1, "Q5language":1, "Q6newsreading":1, "Q7newsimportance":1, "Q8family":1, "Q9friendsabroad":1, "Q10foreignfriends":1, "Q11travel":1, "Q12liveabroad":1})
	for record in cursor:

		new_row = {}
		new_row["userID"] = str(record["_id"])
		for key in record:
			if key != "_id":
				new_row[key]=record[key]

		csvwriter.writerow(DictUnicodeProxy(new_row))

	test_file.close()
	return app.send_static_file('data/exportpresurvey.csv')

# Export postsurvey data to CSV
# not currently filtering for days in system or creator IDs
@app.route('/exportpostsurvey')
def exportpostsurvey():
	test_file = open(app.static_folder + '/data/exportpostsurvey.csv','wb')
	fieldnames = ["userID","username", 'Q1chromeprimarybefore',
						'Q2chromeprimaryafter',
						'Q3globalnewsimportanttowork',
						'Q4raterecommendations',
						'Q5topreaderorrecommender',
						'Q6searchtobecometopreader',
						'Q7searchtocollectmorecities',
						'Q8share',
						'Q9reflect',
						'Q10reflect_explain',
						'Q11newplace',
						'Q12newplace_explain',
						'Q13badarticles',
						'Q14badarticles_explain',
						'Q15goodarticles',
						'Q16goodarticles_explain',
						'Q17improverecommendations',
						'Q18rankings_explain',
						'Q19improverankings',
						'Q20feelings_explain',
						'Q21anythingelse_explain',
						'Q22contactyou',
						'Q23seeleaderboard']
	csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
	csvwriter.writeheader()

	cursor = app.db_user_collection.find({"filled_out_postsurvey":{"$exists":1}, "postsurvey":{"$exists":1}},{"username":1, 'postsurvey' : 1})
	for record in cursor:

		new_row = {}
		new_row["userID"] = str(record["_id"])
		postsurvey = record["postsurvey"]
		for key in postsurvey:
			if key != "_id":
				new_row[key]=postsurvey[key]

		csvwriter.writerow(DictUnicodeProxy(new_row))

	test_file.close()
	return app.send_static_file('data/exportpostsurvey.csv')

# exports email addresses who haven't filled out post survey
# and who have been in system for more than 30 days
# and who have been using app
@app.route('/exportemailsforpostsurvey/')
def exportemailsforpostsurvey():
	emails=[]
	users = app.db_user_collection.find({"signed_consent":1,"filled_out_presurvey":1,"filled_out_postsurvey":{"$exists":0}},{"history-pre-installation":0})
	for user in users:
		userID = str(user["_id"])
		days=getPreinstallAndPostinstallDays(user)
		if days["postinstallation.days"] >= 30:
			emails.append(user["email"])
	return json.dumps(emails, sort_keys=True, indent=4, default=json_util.default)

# exports all user history records for counting and operating on
# filter records that have no userID - bug that they ended up there anyways
# excludes userIDs from creators of TI
@app.route('/export/')
def export():

	test_file = open(app.static_folder + '/data/exportUserHistoryCount.csv','wb')
	fieldnames = ["userID","datetime", "humanDate", "hasGeo", "preinstallation","preinstallation.days","postinstallation.days"]
	csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
	csvwriter.writeheader()

	# GET USERS, EXCLUDE M & C
	users = getUsersFilterCreators()
	userIDs = []
	for user in users:
		userID = str(user["_id"])
		days=getPreinstallAndPostinstallDays(user)

		if (excludeUserFromStudyData(days)):
			continue

		# OK, USER MEETS DATA REQUIREMENT, GET THEIR USER HISTORY #
		# Write a row with their pre and post install days for later tallying #
		new_row = {}
		new_row["userID"] = userID
		new_row["preinstallation.days"] = days["preinstallation.days"]
		new_row["postinstallation.days"] = days["postinstallation.days"]
		csvwriter.writerow(DictUnicodeProxy(new_row))

		#user IDs to keep
		userIDs.append(userID)

	cursor = app.db_user_history_collection.find({"userID" : {"$in": userIDs}}, {"userID":1,"lastVisitTime":1,"preinstallation":1, "geodata.primaryCities.id":1, "geodata.primaryCountries":1})
	for record in cursor:
		if "lastVisitTime" not in record:
			continue
		new_row = {}
		new_row["userID"] = record["userID"]

		new_row["datetime"] = record["lastVisitTime"]

		date = datetime.datetime.fromtimestamp( record["lastVisitTime"]/1000 )
		new_row["humanDate"] = date.strftime('%m/%d/%Y')
		if "preinstallation" in record:
			new_row["preinstallation"] =1
		else:
			new_row["preinstallation"] =0

		if "geodata" in record and ("primaryCities" in record["geodata"] or "primaryCountries" in record["geodata"]):
			new_row["hasGeo"] =1
		else:
			new_row["hasGeo"] =0
		csvwriter.writerow(new_row)

	return app.send_static_file('data/exportUserHistoryCount.csv')

class DictUnicodeProxy(object):
	def __init__(self, d):
		self.d = d
	def __iter__(self):
		return self.d.__iter__()
	def get(self, item, default=None):
		i = self.d.get(item, default)
		if isinstance(i, unicode):
			return i.encode('utf-8')
		return i

def getUsersFilterCreators():
	result = []
	users = app.db_user_collection.find({"$and": [{ "_id":{"$ne":ObjectId("53401d97c183f236b23d0d40")}}, { "_id":{"$ne":ObjectId("5345c2f9c183f20b81e78eec")}}]},{"_id":1,"firstLoginDate":1, "username":1})
	for user in users:
		result.append(user)
	return result

def excludeUserFromStudyData(userDaysResult):
	if (userDaysResult["postinstallation.days"] <MINIMUM_DAYS_OF_DATA):
		return True
	if (userDaysResult["preinstallation.days"] <MINIMUM_DAYS_OF_DATA):
		return True
	if (userDaysResult["postinstallation.count"] <MINIMUM_HISTORY_COUNT):
		return True
	if (userDaysResult["preinstallation.count"] <MINIMUM_HISTORY_COUNT):
		return True
	return False

def getPreinstallAndPostinstallDays(userDoc):
	userID = str(userDoc["_id"])
	userDaysResult = dict()

	# IF NO LOGIN DATE THEN WE CANT FIGURE ANYTHING OUT
	if "firstLoginDate" not in userDoc:
		userDaysResult["preinstallation.days"]=0
		userDaysResult["postinstallation.days"]=0
		return userDaysResult

	firstLoginDate = datetime.datetime.fromtimestamp(int(userDoc["firstLoginDate"]/1000))

	# # POSTINSTALL DAYS WITH RECORDS
	# OMG THIS IS GOING TO BE SO SLOOOOOW
#	daysOfHistory = {}
#	result = app.db_user_history_collection.find({"userID":str(userID), "preinstallation":{"$exists":0}}, {"lastVisitTime":1})
#	userDaysResult["postinstallation.count"] = result.count()
#	for record in result:
#		visitDate = datetime.datetime.fromtimestamp(int(record["lastVisitTime"]/1000))
#		daysOfHistory[visitDate.strftime("%Y-%m-%d")] = 1

#	userDaysResult["postinstallation.days"] = len(daysOfHistory)

	# measure days from first login to the latest day with a browser record
	firstLoginDate = datetime.datetime.fromtimestamp(int(userDoc["firstLoginDate"]/1000))
	result = app.db_user_history_collection.find({"userID":str(userID), "preinstallation":{"$exists":0}}, {"lastVisitTime":1}).sort([("lastVisitTime",-1)]).limit(1)

	if result.count() == 0:
		userDaysResult["postinstallation.days"] = 0
	else:
		result = result.next()
		latestDayWithData = datetime.datetime.fromtimestamp(int(result["lastVisitTime"]/1000))
		dateDiff = latestDayWithData - firstLoginDate
		userDaysResult["postinstallation.days"] = dateDiff.days


	# # PREINSTALL DAYS WITH RECORDS
	result = app.db_user_history_collection.find({"userID":str(userID), "preinstallation":{"$exists":1}}, {"lastVisitTime":1}).sort([("lastVisitTime",1)]).limit(1)
	if result.count() == 0:
		userDaysResult["preinstallation.days"] = 0
	else:
		result = result.next()
		firstPreinstallHistoryItemDate = datetime.datetime.fromtimestamp(int(result["lastVisitTime"]/1000))
		dateDiff = firstLoginDate - firstPreinstallHistoryItemDate
		userDaysResult["preinstallation.days"] = dateDiff.days

	# POST INSTALL COUNT
	result = app.db_user_history_collection.find({"userID":str(userID), "preinstallation":{"$exists":0}}).count()
	userDaysResult["postinstallation.count"] = result

	#PRE INSTALL COUNT
	result = app.db_user_history_collection.find({"userID":str(userID), "preinstallation":{"$exists":1}}).count()
	userDaysResult["preinstallation.count"] = result

	return userDaysResult

# exports user browsing geo to see if geo diversity goes up post-TI-install
# excludes userIDs from creators of TI
# excludes data from people who don't have at least 5 days of preinstall and postinstall history
@app.route('/exportgeo/')
def exportgeo():
	test_file = open(app.static_folder + '/data/exportUserGeo.csv','wb')
	fieldnames = ["userID","countrycode", "preinstallation.count", "preinstallation.days", "postinstallation.count", "postinstallation.days"]
	csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
	csvwriter.writeheader()

	# GET USERS, EXCLUDE M & C
	users = getUsersFilterCreators()
	for user in users:
		userID = str(user["_id"])
		days=getPreinstallAndPostinstallDays(user)

		if (excludeUserFromStudyData(days)):
			continue

		# OK, USER MEETS DATA REQUIREMENT, GET THEIR COUNTRY COUNTS #
		# Write a row with their pre and post install days #
		new_row = {}
		new_row["userID"] = userID
		new_row["preinstallation.days"] = days["preinstallation.days"]
		new_row["postinstallation.days"] = days["postinstallation.days"]
		csvwriter.writerow(DictUnicodeProxy(new_row))

		COUNTRY_COUNT_POSTINSTALL_PIPELINE = [
		{ "$unwind" : "$geodata.primaryCountries" },
		{ "$match" : { "userID":userID, "preinstallation":{"$exists":0} }},
		{ "$group": {"_id": {"countrycode":"$geodata.primaryCountries" }, "count": {"$sum": 1}}},
		{ "$sort" : { "count" : -1 } }
		]

		COUNTRY_COUNT_PREINSTALL_PIPELINE = [
		{ "$unwind" : "$geodata.primaryCountries" },
		{ "$match" : { "userID":userID, "preinstallation":{"$exists":1} }},
		{ "$group": {"_id": {"countrycode":"$geodata.primaryCountries" }, "count": {"$sum": 1}}},
		{ "$sort" : { "count" : -1 } }
		]

		# Preinstall country counts
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=COUNTRY_COUNT_PREINSTALL_PIPELINE )
		for row in q["result"]:
			new_row = {}
			new_row["userID"] = userID
			new_row["countrycode"] = row["_id"]["countrycode"]
			new_row["preinstallation.count"] = row["count"]
			new_row["preinstallation.days"] = days["preinstallation.days"]
			csvwriter.writerow(DictUnicodeProxy(new_row))

		# Postinstall country counts
		q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=COUNTRY_COUNT_POSTINSTALL_PIPELINE )
		for row in q["result"]:
			new_row = {}
			new_row["userID"] = userID
			new_row["countrycode"] = row["_id"]["countrycode"]
			new_row["postinstallation.count"] = row["count"]
			new_row["postinstallation.days"] = days["postinstallation.days"]
			csvwriter.writerow(DictUnicodeProxy(new_row))

		# File is a little messy but we will clean it up in R

	test_file.close()
	return app.send_static_file('data/exportUserGeo.csv')

# exports all user clicks on recommendations
# excludes userIDs from creators of TI
# excludes data from people who haven't been in the system for at least 5 days
@app.route('/exportclicks/')
def exportclicks():
	test_file = open(app.static_folder + '/data/exportUserClicks.csv','wb')
	fieldnames = ["recommendation_source","url", "userID", "city", "random_city","clicked_at","ui_source"]
	csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
	csvwriter.writeheader()

	userIDs = []
	users = getUsersFilterCreators()
	for user in users:
		userID = str(user["_id"])
		days=getPreinstallAndPostinstallDays(user)

		if (excludeUserFromStudyData(days)):
			continue
		userIDs.append(userID)

	print str(len(userIDs)) + " users meet the criteria"

	cursor = app.db_user_behavior_collection.find({ "userID":{"$in":userIDs}})

	for record in cursor:
		userID = record["userID"]
		result = app.db_user_collection.find({"_id":ObjectId(userID)},{"firstLoginDate":1})
		if result.count() == 0:
			continue
		else:
			result =result.next()

		new_row = {}
		if "recommendation_source" in record:
			new_row["recommendation_source"] = record["recommendation_source"]
		new_row["url"] = record["url"]
		new_row["userID"] = record["userID"]

		new_row["random_city"] = record["random_city"]
		new_row["clicked_at"] = record["clicked_at"]
		new_row["ui_source"] = record["ui_source"]

		for city in THE1000CITIES:
			if int(city["geonames_id"]) == int(record["cityID"]):
				new_row["city"] = city["city_name"]
		csvwriter.writerow(DictUnicodeProxy(new_row))

	test_file.close()
	return app.send_static_file('data/exportUserClicks.csv')

# exports total # of users in the system
# excludes creators of TI
# excludes data from people who haven't been in the system for at least 5 days
@app.route('/totalusers/')
def totalusers():

	test_file = open(app.static_folder + '/data/totalusers.csv','wb')
	fieldnames = ["totalusers"]
	csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
	csvwriter.writeheader()
	new_row = {}
	total=0

	users = getUsersFilterCreators()

	for user in users:
		days=getPreinstallAndPostinstallDays(user)

		if (excludeUserFromStudyData(days)):
			continue
		total=total+1


	new_row["totalusers"] = total
	csvwriter.writerow(DictUnicodeProxy(new_row))
	test_file.close()

	return app.send_static_file('data/totalusers.csv')

@app.route('/report/<userID>')
@app.route('/report/')
def report(userID='5340168960de7dd9d8394aa7'):

	#OK so I should have been storing the lastTimeVisited as a DATE type instead of number (UTC time)
	#So now when I query, I will get user's entire history 2 ways (no geo & geo) and sort using python into day bins
	result = {}
	firstLogin = app.db_user_collection.find({"_id":ObjectId(userID)},{"firstLoginDate":1}).next()["firstLoginDate"]

	result["installDate"] = datetime.datetime.fromtimestamp( firstLogin/1000 ).strftime('%m/%d/%Y')

	# HISTORY WITH GEO
	cursor = app.db_user_history_collection.find({"userID":userID, "geodata.primaryCities.id": { "$in": THE1000CITIES_IDS_ARRAY } }, {"lastVisitTime":1,"preinstallation":1}).sort([("lastVisitTime",-1)])
	result["count_historyWithGeo"] = cursor.count()

	historyWithGeo = dict()
	for record in cursor:
		date = datetime.datetime.fromtimestamp( record["lastVisitTime"]/1000 )
		dateKey = date.strftime('%m/%d/%Y')
		if dateKey in historyWithGeo:
			historyWithGeo[dateKey] = historyWithGeo[dateKey] + 1
		else:
			historyWithGeo[dateKey] = 1
	result["historyWithGeo"] = historyWithGeo



	# HISTORY WITHOUT GEO
	cursor = app.db_user_history_collection.find({"userID":userID, "$or" :
								[ {"geodata.primaryCountries": { "$exists": 0 }}, {"geodata.primaryCities.id": { "$nin": THE1000CITIES_IDS_ARRAY }} ]
								}, {"lastVisitTime":1,"preinstallation":1}).sort([("lastVisitTime",-1)])

	result["count_historyNoGeo"] = cursor.count()
	historyNoGeo = dict()
	for record in cursor:
		date = datetime.datetime.fromtimestamp( record["lastVisitTime"]/1000 )
		dateKey = date.strftime('%m/%d/%Y')
		if dateKey in historyNoGeo:
			historyNoGeo[dateKey] = historyNoGeo[dateKey] + 1
		else:
			historyNoGeo[dateKey] = 1
	result["historyNoGeo"] = historyNoGeo


	totalCount = app.db_user_history_collection.find({"userID":userID}).count()
	result["count_total"]=totalCount

	if result:
		return json.dumps(result, sort_keys=True, indent=4, default=json_util.default)
	else:
		return jsonify(error='Erreur. That is French.')

@app.route('/readinglist/<userID>/<cityID>')
@app.route('/readinglist/')
def get_reading_list(userID='53303d525ae18c2083bcc6f9',cityID=4930956):
	cityID = int(cityID)
	result = {"userHistoryItemCollection":[], "systemHistoryItemCollection":[]}
	#cursor = app.db_user_history_collection.find({"userID":userID, "geodata.primaryCities": { "$elemMatch": { "id": int(cityID) } } }, {"url":1,"title":1}).sort([("lastVisitTime",-1)]).skip(0).limit(100)

	USER_CITY_HISTORY_PIPELINE = [
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": userID, "preinstallation":{"$exists":0} }},
		{ "$unwind" : "$geodata.primaryCities" },
		{ "$sort" : { "lastVisitTime" : 1, "geodata.primaryCities.recommended" : -1 } },
		{ "$group": {"_id": {"url":"$url", "title":"$title"}, "recommended": { "$first" : "$geodata.primaryCities.recommended" }, "count": {"$sum": 1}}},
		{ "$limit" : 50 },

	]
	q = app.db_user_history_collection.aggregate(USER_CITY_HISTORY_PIPELINE)
	for row in q["result"]:
		if next((x for x in result["userHistoryItemCollection"] if "title" in x and "title" in row["_id"] and x["title"] == row["_id"]["title"]), None):
			continue
		else:
			result["userHistoryItemCollection"].append({ "title": row["_id"]["title"], "url":row["_id"]["url"], "recommended":row["recommended"]})


	SYSTEM_CITY_HISTORY_PIPELINE = [
		{ "$match" : { "geodata.primaryCities.id": cityID, "geodata.primaryCities.recommended": {"$ne" : 0}, "userID": {"$ne" : userID}, "title":{"$ne":"" } }},
		{ "$unwind" : "$geodata.primaryCities" },
		{ "$sort" : { "geodata.primaryCities.recommended":-1, "lastVisitTime" : 1 } },
		{ "$group": {"_id": {"url":"$url", "title":"$title" }, "recommended": { "$first" : "$geodata.primaryCities.recommended" }, "count": {"$sum": 1}}},
		{ "$limit" : 50 },

	]
	q = app.db_user_history_collection.aggregate(SYSTEM_CITY_HISTORY_PIPELINE)
	systemHistoryItemCollection = []

	for row in q["result"]:

		#quick fix for duplicate titles showing up, really this should be done at DB level
		if next((x for x in systemHistoryItemCollection if x["title"] == row["_id"]["title"]), None):
			continue
		systemHistoryItemCollection.append({ "title": row["_id"]["title"], "url":row["_id"]["url"], "recommended":row["recommended"]})

	# If not much in the way of system history, then grab recommendations from the recs DB
	# then shuffle it -- randomize access so doesn't always show the top 20
	if len(systemHistoryItemCollection) < 10:
		RECOMMENDATION_PIPELINE = [
			{ "$match" : { "geodata.primaryCities.id": cityID, "title":{"$ne":"" } }},
			{ "$sort" : { "_id" : 1 } },
			{ "$group": {"_id": {"url":"$url", "title":"$title" }, "count": {"$sum": 1}}},
			{ "$limit" : 20 },
		]
		q = app.db_recommendation_collection.aggregate(RECOMMENDATION_PIPELINE)
		for row in q["result"]:
			if next((x for x in systemHistoryItemCollection if "title" in x and "title" in row["_id"] and x["title"] == row["_id"]["title"]), None):
				continue
			else:
				systemHistoryItemCollection.append(row["_id"])
		#systemHistoryItemCollection.extend(list(row["_id"] for row in q["result"]))
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
	doc = extractSingleURL(doc, url, config.get('extractor','extractor_url'))
	if not "extractedText" in doc:
		doc["title"] = url

	doc["source"] = "user"
	doc["userID"] = userID
	doc["geodata"] = {}
	doc["geodata"]["primaryCities"] = []
	doc["geodata"]["primaryCities"].append({"id" : cityID})

	doc = addCityGeoDataToDoc(doc)

	app.db_recommendation_collection.insert(doc)
	return json.dumps({"response":"ok"}, sort_keys=True, indent=4, default=json_util.default)

@app.route('/like/<userID>/<cityID>', methods=['POST'])
@app.route('/like/', methods=['GET'])
def like(userID='53303d525ae18c2083bcc6f9',cityID=4990729):
	cityID = int(cityID)

	url=request.form['url']


	isThumbsUp=request.form['isThumbsUp']
	if isThumbsUp == "true":
		isThumbsUp=1
	else:
		isThumbsUp=0

	if url is None or len(url) < 1:
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

	if userID is None or cityID is None or str(userID) == "null" or str(cityID) =="null":
		return json.dumps({"result":"error - null user or null city"}, sort_keys=True, indent=4, default=json_util.default)

	currentUsername = getUsername(userID)

	#current user counts
	result["currentUserStoryCount"] = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID, "userID" : userID, "preinstallation":{"$exists":0} }).skip(0).count()

	#recommendations come from two different collections and get added together
	userRecs = app.db_recommendation_collection.find({"geodata.primaryCities.id" : cityID, "userID" : userID }).skip(0).count();
	userHistoryRecs = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID, "geodata.primaryCities.recommended" : {"$exists" : 1}, "userID" : userID }).skip(0).count();
	result["currentUserRecommendationCount"] = userRecs + userHistoryRecs;

	#first person to visit city
	firstVisitUserID = ''
	cursor = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID, "userID" : {"$exists" : "true"}, "preinstallation":{"$exists":0}}, {"userID" :1}).sort([("lastVisitTime",1)]).skip(0).limit(1)
	if cursor.count() != 0:
		doc = cursor.next()
		firstVisitUserID = doc["userID"]
		result["firstVisitUsername"] = getUsername(firstVisitUserID)

	#person with most articles read about city
	USER_WITH_MOST_READ_PIPELINE = [
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": {"$exists":"true"}, "preinstallation":{"$exists":0} }},
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
	userHistoryRecs = app.db_user_history_collection.find({"geodata.primaryCities.id" : cityID, "userID" : {"$exists" : "true"}, "preinstallation":{"$exists":0}, "geodata.primaryCities.recommended": {"$exists":"true"}}, {"userID" :1,"lastVisitTime":1}).sort([("lastVisitTime",1)]).skip(0).limit(1)
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
		{ "$match" : { "geodata.primaryCities.id": cityID, "userID": {"$exists":"true"}, "preinstallation":{"$exists":0}, "geodata.primaryCities.recommended": {"$exists":"true"} }},
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

#Test function for various things
@app.route('/testdb/')
def testdb():

	ALL_USERS_CITY_COUNT_PIPELINE = [
		{ "$unwind" : "$geodata.primaryCities" },
		{ "$match" : { "preinstallation":{"$exists":0}, "geodata.primaryCities.id": { "$in": THE1000CITIES_IDS_ARRAY } }},
		{ "$group": {"_id": {"userID":"$userID", "geonames_id":"$geodata.primaryCities.id" }, "count": {"$sum": 1}}},

		{ "$group": {"_id": {"userID":"$_id.userID"}, "totalcitiesvisited": {"$sum": 1}}},
		{ "$sort" : { "totalcitiesvisited" : -1 } }
	]
	q = app.db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=ALL_USERS_CITY_COUNT_PIPELINE )
	for row in q["result"]:
		print row

	return "Updated your user"

def getUsername(userID):
	cursor = app.db_user_collection.find({"_id": ObjectId(userID)}, {"username":1}).skip(0).limit(1)
	if cursor.count() >0:
		doc= cursor.next()
		if "username" in doc:
			return doc["username"]
		else:
			return None
	else:
		return None


# Metrics: Log when a user clicks on a story in the app
@app.route('/logstoryclick/<userID>/<cityID>', methods=['POST'])
def logStoryClick(userID='52dbeee6bd028634678cd069',cityID=703448):
	doc = {}
	doc["cityID"] = int(cityID)
	doc["userID"] = userID
	doc["clicked_at"] = time.time() * 1000
	doc["ui_source"] = request.form['ui_source']
	doc["random_city"] = int(request.form['isRandomCity']) #should be 1 or 0
	doc["url"] = request.form['url']

	app.db_user_behavior_collection.insert(doc)
	return json.dumps({"result":"ok"}, sort_keys=True, indent=4, default=json_util.default)

# Metrics: Log when a user clicks on a city in the app
@app.route('/logcityclick/<userID>/<cityID>')
def logCityClick(userID='52dbeee6bd028634678cd069',cityID=703448):
	doc ={}
	doc["userID"] = userID
	doc["cityID"] = int(cityID)
	doc["clicked_at"] = time.time() * 1000
	app.db_user_city_clicks_collection.insert(doc)
	return json.dumps({"result":"ok"}, sort_keys=True, indent=4, default=json_util.default)

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
	recommendationSource = ""
	if random == 0:
		log.debug("Recommendation from Bitly")
		recommendationSource = "bitly"
		url = get_recommended_bitly_url(cityID, config.get('app','bitly_token'))
	elif random == 1:
		log.debug("Recommendation from recommendation collection")
		recommendationSource = "recommendation_collection"
		count = app.db_recommendation_collection.find({ "geodata.primaryCities.id": cityID }, {url:1}).count()
		if count:
			doc = app.db_recommendation_collection.find({ "geodata.primaryCities.id": cityID }).skip(randint(0, count - 1)).limit(1).next()
			url = doc["url"]
	elif random == 2:
		log.debug("Recommendation from user history collection")
		recommendationSource = "user_history_collection"
		count = app.db_user_history_collection.find({ "geodata.primaryCities.id": cityID, "userID": {"$ne" : userID} }, {url:1}).count()
		if count:
			doc = app.db_user_history_collection.find({ "geodata.primaryCities.id": cityID, "userID": {"$ne" : userID} }).skip(randint(0, count - 1)).limit(1).next()
			url = doc["url"]

	if not url:
		recommendationSource = "bitly"
		log.debug("Fallback recommendation from Bitly")
		url = get_recommended_bitly_url(cityID, config.get('app','bitly_token'))

	#Red Button Metric: Log to the DB that they clicked on the red button, when, and where we sent them
	doc = {}
	doc["cityID"] = cityID
	doc["userID"] = userID
	doc["clicked_at"] = time.time() * 1000
	doc["ui_source"] = "redbutton"
	doc["recommendation_source"] = recommendationSource
	doc["random_city"] = int(request.args.get('r')) #should be 1 or 0
	doc["url"] = url

	app.db_user_behavior_collection.insert(doc)

	return redirect(url, code=302)

@app.route('/history/<userID>', methods=['GET', 'POST'])
@app.route('/history/<userID>/', methods=['GET', 'POST'])
def processHistory(userID):
	log.debug("Processing browser history for " + userID)
	if request.method != 'POST':
		return 'I need to have a POST with some history data'
	historyItems = json.loads(request.form['history'])
	log.debug(str(len(historyItems)) + " in browser history")

	# save entire history object to DB - this is a backup in case the queue messes things up
	app.db_user_collection.update({ "_id": ObjectId(userID)}, { "$set" : {"history-pre-installation":historyItems}})

	# then start text queue for each item
	'''for historyObject in historyItems:
		historyObject["userID"] = userID;
		historyObject["preinstallation"] = "true"
		count = app.db_user_history_collection.find({ "userID" : userID, "url":historyObject["url"], "lastVisitTime": historyObject["lastVisitTime"] }).count()
		if count == 0:
			args = (historyObject, config, False);
			start_text_processing_queue(*args)'''

	return 'Processing ' + str(len(historyItems)) + ' history items'

# ------------------------- -------------------------------------
# MOVE THIS SOMEWHERE ELSE
# This callback is used to reload the user object from the user ID stored in the session.
# It should take the unicode ID of a user, and return the corresponding user object.
# It should return None (not raise an exception) if the ID is not valid.
# (In that case, the ID will manually be removed from the session and processing will continue.)
def get_user_by_id(id):
	log.debug("server.py >> get_user_by_id")
	user = None
	for row in app.db_user_collection.find({ '_id': ObjectId(id) }):
		user = get_user_from_DB_row(row)
		user.lastLoginDate = time.time() * 1000
		break
	if (user is not None):
		app.db_user_collection.save(user.__dict__)
	return user

# LoginManager
login_manager = LoginManager()
login_manager.user_loader(get_user_by_id)
login_manager.init_app(app)

# OAuth endpoints
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.get('oauth', 'facebook_consumer_key'),
    consumer_secret=config.get('oauth', 'facebook_consumer_secret'),
    request_token_params={'scope': 'email'}
)

@facebook.tokengetter
def get_facebook_token():
    return session.get('oauth_token')

google = oauth.remote_app('google',
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
	consumer_key=config.get('oauth', 'google_consumer_key'),
	consumer_secret=config.get('oauth', 'google_consumer_secret'),
    request_token_params={'scope': 'email'}
)

@google.tokengetter
def get_google_token():
    return session.get('oauth_token')

twitter = oauth.remote_app('twitter',
	base_url='https://api.twitter.com/1/',
	request_token_url='https://api.twitter.com/oauth/request_token',
	access_token_url='https://api.twitter.com/oauth/access_token',
	authorize_url='https://api.twitter.com/oauth/authenticate',
	consumer_key=config.get('oauth', 'twitter_consumer_key'),
	consumer_secret=config.get('oauth', 'twitter_consumer_secret')
)

@twitter.tokengetter
def get_twitter_token():
    return session.get('oauth_token')

# Login/Logout page AND change username
@app.route('/login/', methods=['GET', 'POST'])
def login():
	error = ""
	userID = ""
	hasSignedConsentForm = False
	hasCompletedPreSurvey = False
	hasCompletedPostSurvey = False
	needsToDoPostSurvey = False

	if "user_id" in session:
		userID = session['user_id']
	if userID != "":
		needsToDoPostSurvey = 0
		userDoc = app.db_user_collection.find({ "_id": ObjectId(userID)},{"history-pre-installation":0}).next()

		hasSignedConsentForm = 1 if "signed_consent" in userDoc and int(userDoc["signed_consent"]) == 1 else 0
		hasCompletedPreSurvey = 1 if "filled_out_presurvey" in userDoc and int(userDoc["filled_out_presurvey"]) == 1 else 0

		# check if they've already completed it
		# they can't complete postsurvey without already having filled out other forms
		hasCompletedPostSurvey = 1 if "filled_out_postsurvey" in userDoc and int(userDoc["filled_out_postsurvey"]) == 1 else 0
		if (hasCompletedPostSurvey > 0 or not hasCompletedPreSurvey or not hasSignedConsentForm):
			needsToDoPostSurvey = 0

		# check for having been in system at least 30 days
		else:
			firstLoginDate = datetime.datetime.fromtimestamp(int(userDoc["firstLoginDate"]/1000))
			nowDate = datetime.datetime.now()

			dateDiff = nowDate - firstLoginDate
			if ( dateDiff.days >= 30):
				needsToDoPostSurvey = 1

	if request.method == 'POST':
		oldusername = request.form['oldusername']
		newusername = request.form['newusername']
		userID = request.form['userID']

		if newusername == oldusername:
			error="Your new username is the same as your old username."
		elif app.db_user_collection.find({ "username": newusername }).count():
			error = "That username already exists. Try using a different name."
		else:
			r = app.db_user_collection.update(	{ "_id": ObjectId(userID)},
												{ "$set" : {"username":newusername}})

	return render_template('login.html', error=error, needsToDoPostSurvey=needsToDoPostSurvey, hasSignedConsentForm=hasSignedConsentForm,hasCompletedPreSurvey=hasCompletedPreSurvey,hasCompletedPostSurvey=hasCompletedPostSurvey)

# Logout
@app.route('/logout/')
def logout():
	session.pop('oauth_token', None)
	logout_user()
	return redirect(url_for('login'))

# OAuth by service
@app.route('/oauth/<service>')
def oauth(service):
	callback_url = url_for('oauthorized',
		_external=True,
		service=service
	)
	if service == 'facebook':
		return facebook.authorize(callback=callback_url)
	elif service == 'google':
		return google.authorize(callback=callback_url)
	elif service == 'twitter':
		return twitter.authorize(callback=callback_url)
	else:
		return redirect(url_for('login'))

# Returns matching user for a service/id, otherwise returns None
def get_oauth_user(service, service_id):
	user = None
	for row in app.db_user_collection.find({ 'service': service, 'service_id': service_id }):
		user = get_user_from_DB_row(row)
		break
	if user is None:
		return None
	else:
		user.lastLoginDate = time.time() * 1000
		return user

# Callback for OAuth
@app.route('/oauthorized/<service>')
def oauthorized(service):
	if service == 'facebook':
		try:
			resp = facebook.authorized_response()
		except OAuthException:
			return oauth_error()
		if resp is None:
			return oauth_error()
		session['oauth_token'] = (resp['access_token'], '')
		data = facebook.get('/me?fields=id,email,name').data
		service_id = data['id']
		email = data['email']
		if email is None:
			username = data['name'].lower().replace(' ', '')
		else:
			username = email.split('@')[0]
	elif service == 'google':
		try:
			resp = google.authorized_response()
		except OAuthException:
			return oauth_error()
		if resp is None:
			return oauth_error()
		session['oauth_token'] = (resp['access_token'], '')
		data = google.get('userinfo').data
		service_id = data['id']
		username = data['email'].split('@')[0]
	elif service == 'twitter':
		try:
			resp = twitter.authorized_response()
		except OAuthException:
			return oauth_error()
		if resp is None:
			return oauth_error()
		session['oauth_token'] = (resp['oauth_token'], resp['oauth_token_secret'])
		service_id = resp['user_id']
		username = resp['screen_name']
	else:
		return oauth_error()

	# Lookup user based on service and unique ID
	user = get_oauth_user(service, service_id)

	# If user does not currently exist
	if user is None:
		# Append '-1', '-2', ..., '-n' to username if it already exists
		duplicates = 0
		deduped_username = username
		while app.db_user_collection.find({ "username": deduped_username }).count():
			duplicates += 1
			deduped_username = username + '-' + str(duplicates)

		# Add the new user to the db
		user = create_new_user(service, service_id, deduped_username)
		user_id = app.db_user_collection.insert(user.__dict__)
		user._id = user_id

	login_user(user)
	return redirect(url_for('login'))

def oauth_error():
	error = 'There was an error authenticating your account. Please try again, or use a different login service.'
	return render_template('login.html', error=error)

# Receives a single URL object from user and logs it through the text processing queue
@app.route('/monitor/', methods=['POST','GET'])
def processURL():
	print "Receiving new URL"
	historyObject = json.loads(request.form['logURL'])
	if "userID" in historyObject and historyObject["userID"] is not None:
		args = (historyObject, config, False);
		start_text_processing_queue(*args)
	else:
		print "Was sent URL with no userID so I'm ignoring it"

	return 'We is processing your URL dude - ' + historyObject["url"]



if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
	print "Started Server"

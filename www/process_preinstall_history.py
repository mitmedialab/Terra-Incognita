# This script runs nightly to process users' preinstall history
# no it doesn't, you liar
from bson.objectid import ObjectId
import ConfigParser
import os
from text_processing.textprocessing import start_text_processing_queue
from pymongo import MongoClient
import time
from os import listdir
from os.path import isfile, join

CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMPORT_DIR = os.path.join(BASE_DIR, "static", "import")

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

#DB
uri = "mongodb://"+ config.get('db','user')+ ":"+ config.get('db','pass')+"@" +config.get('db','host') + ":" + config.get('db','port')
db_client = MongoClient(uri)
db = db_client[config.get('db','name')]
db_user_history_collection = db[config.get('db','user_history_item_collection')]
db_user_collection = db[config.get('db','user_collection')]

#find users who have preinstall history
users = db_user_collection.find({ "history-pre-installation": {"$exists":1}, "history-pre-installation-processed": {"$exists":0} }, {"history-pre-installation":1, "_id":1, "username":1}).limit(1)

for user in users:
	print "Processing browser history for " + user["username"]
	historyItems = user["history-pre-installation"]
	print str(len(historyItems)) + " items to process"
	userID = str(user["_id"])
	# start text queue for each item
	for historyObject in historyItems:
		print historyObject["url"]
		historyObject["userID"] = userID;
		historyObject["preinstallation"] = "true"

		#check that we haven't already added this item
		count = db_user_history_collection.find({ "userID" : userID, "url":historyObject["url"], "lastVisitTime": historyObject["lastVisitTime"] }).count()
		if count == 0:
			args = (historyObject, config, False);
			start_text_processing_queue(*args)
		else:
			print "Already added this item - skipping..."

	#mark that we've processed their browsing history
	db_user_collection.update({ "_id": ObjectId(userID)},{ "$set":{'history-pre-installation-processed':1}})
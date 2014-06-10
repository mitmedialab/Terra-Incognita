import ConfigParser
import os
from pymongo import MongoClient
from random import randrange
import time
# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

#DB
uri = "mongodb://"+ config.get('db','user')+ ":"+ config.get('db','pass')+"@" +config.get('db','host') + ":" + config.get('db','port')
db_client = MongoClient(uri)
db = db_client[config.get('db','name')]
db_user_history_collection = db[config.get('db','user_history_item_collection')]

#update each ID with a new scheme - lastVisitTime + randomNumber + userID
for doc in db_user_history_collection.find():
	
	theTime = time.time()
	doc["_id"] = str(int(theTime * 1000)) + "_" + str(randrange(10000, 99999)) 
	if "userID" in doc:
		doc["_id"] = doc["_id"] + "_" + doc["userID"]
		
	db_user_history_collection.save(doc)
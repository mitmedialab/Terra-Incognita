import ConfigParser
import os
from pymongo import MongoClient
from random import randrange
import time

# One time script to update IDs to manually ascending order
# Run this, then modify app.config file to point to the "new" user history db collection

# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.abspath(os.path.join(BASE_DIR, "..", CONFIG_FILENAME))

# read in app config
config = ConfigParser.ConfigParser()
config.read(filepath)

#DB
uri = "mongodb://"+ config.get('db','user')+ ":"+ config.get('db','pass')+"@" +config.get('db','host') + ":" + config.get('db','port')
db_client = MongoClient(uri)
db = db_client[config.get('db','name')]
db_user_history_collection = db[config.get('db','user_history_item_collection')]
new_db_user_history_collection = db[config.get('db','user_history_item_collection') + "_new"]

i = 0
for doc in db_user_history_collection.find().sort([("_id",-1)]):
	theTime = time.time()
	doc["_id"] = str(int(theTime * 1000)) + "_" + str(randrange(10000, 99999))
	if "userID" in doc and doc["userID"] is not None:
		doc["_id"] = doc["_id"] + "_" + doc["userID"]
	new_db_user_history_collection.insert(doc)
	i=i+1
	if i % 1000 == 0:
		print str(i) + " records processed"

	

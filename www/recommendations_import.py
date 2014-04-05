import ConfigParser
import os
from text_processing.tasks import start_text_processing_queue
from pymongo import MongoClient
import time
from os import listdir
from os.path import isfile, join

# script that imports INSTAPAPER URLS in the static/import directory
# stuff in .txt files should just be lists of URLS to run through the text processing queue
# and add to the DB

# constants
SOURCE = "Instapaper"
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMPORT_DIR = os.path.join(BASE_DIR, "static", "import")

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

#DB
db_client = MongoClient()
db = db_client[config.get('db','name')]
db_recommendation_collection = db[config.get('db','recommendation_item_collection')]

files_to_import = [ join(IMPORT_DIR,f) for f in listdir(IMPORT_DIR) if isfile(join(IMPORT_DIR,f)) and f.endswith('.txt') ]

for myFile in files_to_import:
	
	urls = [line.strip() for line in open(myFile)]
	for url in urls:
		doc ={}
		doc["url"] = "http://"+url

		#check for url already in recommendations DB
		if db_recommendation_collection.find({"url": doc["url"]}).skip(0).limit(1).count() == 0: 
			doc["source"]=SOURCE
			doc["dateEntered"] = time.time() * 1000
			
			#start text processing queue to add it
			start_text_processing_queue(doc, config, True)
		else:
			print "Skipping " + doc["url"]
			

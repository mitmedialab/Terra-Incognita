import ConfigParser
import os
from text_processing.tasks import start_text_processing_queue
from pymongo import MongoClient

#IMPORT FILE
FILE_TO_IMPORT = '/Users/kanarinka/Sites/Terra Incognita/www/static/import/instapaper-no-nytimes2.txt'

# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

#DB
db_client = MongoClient()
db = db_client[config.get('db','name')]
db_recommendation_collection = db[config.get('db','recommendation_item_collection')]


urls = [line.strip() for line in open(FILE_TO_IMPORT)]

for url in urls:
	doc ={}
	doc["url"] = "http://"+url
	

	#check for url already in recommendations DB
	if db_recommendation_collection.find({"url": doc["url"]}).skip(0).limit(1).count() == 0: 
		doc["source"]="Instapaper"
		doc["dateEntered"] = time.time() * 1000
		
		#start text processing queue to add it
		start_text_processing_queue(doc, config)
	else:
		print "Skipping " + doc["url"]

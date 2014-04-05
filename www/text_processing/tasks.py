from celery import Celery
from celery.utils.log import get_task_logger
from content_extraction import *
from map_topics import *
from geoprocessing import *
import httplib
from pymongo import MongoClient
from cities_array import *


## Celery text processing queue
app = Celery('text_processing.tasks', backend ="amqp", broker='amqp://guest@localhost//')
logger = get_task_logger(__name__)

@app.task()
def start_text_processing_queue(*args,**kwargs):
	logger.info("starting text processing queue")
	
	doc = args[0]
	
	config = args[1]
	
	isRecommendation = args[2]
	

	db_client = MongoClient()
	app.db = db_client[config.get('db','name')]
	if isRecommendation:
		app.db_collection = app.db[config.get('db','recommendation_item_collection')]
	else:
		app.db_collection = app.db[config.get('db','user_history_item_collection')]
		
	# Content Extraction & add Web page title
	doc = extractSingleURL(doc)

	
	if doc is not None and "extractedText" in doc:
		# Geoparsing
		print "geoserver url is "
		print config.get('geoparser','geoserver_url')
		doc["geodata"] = geoparseSingleText(doc["extractedText"], config.get('geoparser','geoserver_url'))
		
		# Chance that the geodata might come from the recommendation database instead of geoparser
		# i.e. user submitted video recommendation
		# try that as a second shot at geodata
		# Currently taking the most recently submitted recommendation's geodata, maybe in the future merge all
		# matching recommendations' geodata?
		if "geodata" not in doc:
			print "NO GEO DATA FOUND FOR URL - WHUT?"
			recommendationCollection = app.db[config.get('db','recommendation_item_collection')]
			recDocMatches = recommendationCollection.find({'url':doc["url"], "geodata.primaryCities.id" : {"$exists":"true"}}).sort([("lastVisitTime",1)]).limit(1)
			if recDocMatches.count() > 0:
				match = recDocMatches.next()
				doc["geodata"] = match["geodata"]

		# Add Continent and Region info to geodata
		if "geodata" in doc and doc["geodata"] is not None:
			doc["geodata"] = lookupContinentAndRegion(doc["geodata"])
			# if there is country data but not city data then make the primary city the country's capital city
			if "primaryCountries" in doc["geodata"]:
				doc["geodata"] = lookupCountryCapitalCity(doc["geodata"])


		# Topic Mapping
		doc["topics"] = map_topics(doc["extractedText"])

		# Saves to DB if there is geodata
		# If it is a user history item then remove extracted text (space reasons) and save it to DB
		# because we want to be able to compare user browsing with and without geo
		# If it's a recommendation and no geodata then just discard it because it's not useful to us

		if "geodata" in doc and "primaryCities" in doc["geodata"]:
			print "Saved doc"
			app.db_collection.save(doc)
		elif "userID" in doc and not isRecommendation:
			print "No geodata, but deleting extracted text and saving to DB for user metrics"
			doc["extractedText"] = ""
			app.db_collection.save(doc)
		else:
			print "Discarding because no geodata and it's a recommendation: " + doc["url"]

	logger.info("done with text processing queue")
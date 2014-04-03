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

#TODO - KAWRGS ARGS BLARGS! So we can pass in whether it's a recommendation or not...
@app.task()
def start_text_processing_queue(doc, config):
	logger.info("starting text processing queue")
	
	isRecommendation = False

	db_client = MongoClient()
	app.db = db_client[config.get('db','name')]
	if isRecommendation:
		app.db_collection = app.db[config.get('db','recommendation_item_collection')]
	else:
		app.db_collection = app.db[config.get('db','user_history_item_collection')]
		
	# Content Extraction & add Web page title
	doc = extractSingleURL(doc)
	
	if (doc and any(doc["extractedText"])):
		# Geoparsing
		doc["geodata"] = geoparseSingleText(doc["extractedText"], config.get('geoparser','geoserver_url'))
		if any(doc["geodata"]):
			doc["geodata"] = lookupContinentAndRegion(doc["geodata"])
			# if there is country data but not city data then make the primary city the country's capital city
			if any(doc["geodata"]["primaryCountries"]) and not (any(doc["geodata"]["primaryCities"])):
				doc["geodata"] = lookupCountryCapitalCity(doc["geodata"])


		# Topic Mapping
		doc["topics"] = map_topics(doc["extractedText"])

		# Should Save to DB only if primarycities IDs are in our list, otherwise discard data
		# TODO - Map things that have country data to country capital city
		if any(doc["geodata"]) and any(doc["geodata"]["primaryCities"]):
			for city in doc["geodata"]["primaryCities"]:
				if int(city["id"]) in THE1000CITIES_IDS_ARRAY:
					print "SAVING BECAUSE A MATCH ON " + city["name"]
					app.db_collection.save(doc)
					break
		else:
			print "Discarding because no geodata: " + doc["url"]
	logger.info("done with text processing queue")

'''@app.task()
def geoparse(doc):
	logger.info("geoparsing task")
	doc["geodata"] = geoparseSingleText(doc["extractedText"], CONFIG.get('geoparser','geoserver_url'))
	doc["geodata"] = lookupContinentAndRegion(doc["extractedText"])
	doc = saveThatDoc(doc)
	map_topics.delay(doc)

@app.task()
def map_topics(doc):
	logger.info("mapping topics")
	
	doc["topics"] = map_topics(doc["extractedText"])
	doc = saveThatDoc(doc)
	
	logger.info("Done with text processing queue for URL " + doc["url"])

def saveThatDoc(doc):
	logger.info("saving doc to DB")
	logger.info(app.db_user_history_collection)
	docID = app.db_user_history_collection.save(doc)
	logger.info("returned from save - docID s ")
	logger.info(docID)
	doc = app.db_user_history_collection.find_one({ '_id': docID })
	return doc
'''
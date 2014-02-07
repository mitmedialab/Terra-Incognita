from celery import Celery
from celery.utils.log import get_task_logger
from content_extraction import *
from map_topics import *
from geoprocessing import *
import httplib
from pymongo import MongoClient


## Celery text processing queue
## Right now this is saving to DB on each task in case fails

app = Celery('text_processing.tasks', backend ="amqp", broker='amqp://guest@localhost//')
logger = get_task_logger(__name__)

@app.task()
def start_text_processing_queue(doc, config):
  db_client = MongoClient()

  app.db = db_client[config.get('db','name')]
  app.db_user_history_collection = app.db[config.get('db','user_history_item_collection')]

  logger.info("starting text processing queue")

  # Content Extraction  
  doc["extractedText"] = extractSingleURL(doc["url"])
  
  # Geoparsing
  doc["geodata"] = geoparseSingleText(doc["extractedText"], config.get('geoparser','geoserver_url'))
  if any(doc["geodata"]):  
    doc["geodata"] = lookupContinentAndRegion(doc["geodata"])

  # Topic Mapping
  doc["topics"] = map_topics(doc["extractedText"])

  # Save to MongoDB
  app.db_user_history_collection.save(doc)
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
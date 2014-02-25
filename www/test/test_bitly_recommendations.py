from batch_seed_recommendations import *

import ConfigParser
import pymongo
from pymongo import MongoClient
from batch_extractor import BatchExtractor
import os

#test script to see if we can batch extract all urls in the selected DB

# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.abspath(os.path.join(BASE_DIR, "..", CONFIG_FILENAME))

# read in app config
config = ConfigParser.ConfigParser()
config.read(filepath)

db_client = MongoClient()
db = db_client[config.get('db','name')]
db_collection = db[config.get('db','recommendation_item_collection')]
doc_cursor = db_collection.find(timeout=False)

batcher = BatchSeedRecommendations(doc_cursor, db_collection)
batcher.run()

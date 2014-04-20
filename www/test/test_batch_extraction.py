import ConfigParser
import pymongo
from pymongo import MongoClient
from batch_extractor import BatchExtractor
import os

#test script to see if we can batch extract all urls in the selected DB

# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

uri = "mongodb://"+ config.get('db','user')+ ":"+ config.get('db','pass')+"@" +config.get('db','host') + ":" + config.get('db','port')
db_client = MongoClient(uri)
db = db_client[config.get('db','name')]
db_collection = db[config.get('db','collection')]
doc_cursor = db_collection.find(timeout=False)
batcher = BatchExtractor(doc_cursor, db_collection)
batcher.run()

print "done yo"

import ConfigParser
import pymongo
from pymongo import MongoClient
from batch_extractor import BatchExtractor
import os

#test script to import url history from txt file

# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

db_client = MongoClient()
db = db_client[config.get('db','name')]
db_collection = db[config.get('db','collection')]

urls = [line.rstrip('\n') for line in open('history-rb.txt')]
docs = []

for url in urls:
	doc = dict()
	doc['url'] = url
	docs.append(doc)

db_collection.insert(docs)

print "done adding urls"

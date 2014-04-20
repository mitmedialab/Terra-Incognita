import ConfigParser
import pymongo
from pymongo import MongoClient
import os
from batch_geoparser import BatchGeoparser

#test script to see if we can batch geoparse all content in the selected DB

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
doc_cursor = db_collection.find({ "extracted_text" : { "$exists" : True } })

geoserver_url = config.get('geoparser','geoserver_url')
geoparser = BatchGeoparser(doc_cursor, db_collection, geoserver_url)
geoparser.run()

print "done yo"

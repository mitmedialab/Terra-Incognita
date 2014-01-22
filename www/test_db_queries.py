import pymongo
import ConfigParser
from pymongo import MongoClient
import os

# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# read in config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))# MongoDB & links to each collection

db_client = MongoClient()
db = db_client[config.get('db','name')]
db_user_history_collection = db[config.get('db','user_history_item_collection')]
db_user_collection = db[config.get('db','user_collection')]
db_recommendation_collection = db[config.get('db','recommendation_item_collection')]

pipeline = [
	{ "$project" : { "geodata.primaryCities":1 }},
	{ "$unwind" : "$geodata.primaryCities" },
	{ "$group": {"_id": {"geonames_id":"$geodata.primaryCities.id", "name":"$geodata.primaryCities.name","state_code":"$geodata.primaryCities.stateCode","country_code":"$geodata.primaryCities.countryCode" }, "count": {"$sum": 1}}},
	{ "$sort" : { "count" : -1 } }
]
q = db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=pipeline )
print q['result']


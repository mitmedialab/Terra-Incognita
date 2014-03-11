import pymongo
import ConfigParser
from pymongo import MongoClient
import os
from database_queries import *

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

import pdb; pdb.set_trace()
#q = db.command('aggregate', config.get('db','user_history_item_collection'), pipeline=CONTINENT_COUNT_PIPELINE )
#print q['result']


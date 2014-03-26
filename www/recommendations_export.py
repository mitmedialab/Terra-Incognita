import ConfigParser
import os
from text_processing.tasks import start_text_processing_queue
from pymongo import MongoClient
import csv


class DictUnicodeProxy(object):
    def __init__(self, d):
        self.d = d
    def __iter__(self):
        return self.d.__iter__()
    def get(self, item, default=None):
        i = self.d.get(item, default)
        if isinstance(i, unicode):
            return i.encode('utf-8')
        return i


test_file = open('instapaper_geo.csv','wb')
fieldnames = ["geonames_id","city_name", "url"]
csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
csvwriter.writeheader()

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

recs = db_recommendation_collection.find({"geodata.primaryCities.name" : {"$exists" : 1}}, {"geodata.primaryCities.id":1,"geodata.primaryCities.name":1,"url":1}).skip(0).limit(0)

for row in recs:
	print row
	new_row = {}
	new_row["geonames_id"] = row["geodata"]["primaryCities"][0]["id"]
	new_row["city_name"] = row["geodata"]["primaryCities"][0]["name"]
	new_row["url"] = row["url"]
	csvwriter.writerow(DictUnicodeProxy(new_row))

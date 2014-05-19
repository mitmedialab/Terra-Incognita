import ConfigParser
import os
from text_processing.textprocessing import start_text_processing_queue
from pymongo import MongoClient
import time
import csv
from os import listdir
from os.path import isfile, join

# script that imports CITY LOCATED URLS in the static/import directory
# to run through the text processing queue
# and add to the DB
# stuff in files should just be lists of URLS already matched to a geonames ID for a city
# like this:
# 1783621,http://www.eguizhou.gov.cn/2013-09/18/content_16979121.htm, http://www.blah.gov.cn/2013-09/18/content_16979121.htm


# constants
SOURCE = "Crowdsourced"
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMPORT_DIR = os.path.join(BASE_DIR, "static", "import","crowdsourced")
CITIES = list(csv.DictReader(open("static/data/1000cities.csv",'rU')))

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

#DB
uri = "mongodb://"+ config.get('db','user')+ ":"+ config.get('db','pass')+"@" +config.get('db','host') + ":" + config.get('db','port')
db_client = MongoClient(uri)
db = db_client[config.get('db','name')]
db_recommendation_collection = db[config.get('db','recommendation_item_collection')]

files_to_import = [ join(IMPORT_DIR,f) for f in listdir(IMPORT_DIR) if isfile(join(IMPORT_DIR,f)) ]

for myFile in files_to_import:
	with open(myFile, 'rU') as f:
		reader = csv.reader(f)
		for row in reader:
			cityID = ""
			
			for idx, val in enumerate(row):
				if idx == 0:
					cityID = val
				elif not val:
					continue
				else:
					url = val
					doc ={}
					if url.startswith("http"):
						doc["url"] = url
					else:
						doc["url"] = "http://"+url

					# add geodata from CITIES lookup
					doc["geodata"] = {}
					doc["geodata"]["primaryCities"] = []
					primaryCity = {}

					for city in CITIES:
						if city["geonames_id"] == cityID:
							print "Matched " + cityID + " to " + city["city_name"]
							primaryCity = city
							# map fields slightly differently to match how they get returned from geonames.org
							primaryCity["id"] = int(city["geonames_id"])
							primaryCity["name"] = city["city_name"]
							primaryCity["toponymName"] = city["toponym_name"]
							primaryCity["lat"] = city["lat"]
							primaryCity["lng"] = city["lon"]
							primaryCity["population"] = city["pop"]
							primaryCity["countryName"] = city["country_name"]
							primaryCity["countryCode"] = city["country_code"]
							doc["geodata"]["primaryCities"].append(primaryCity)

							db_recommendation_collection.remove({"url": doc["url"]})
							print "removed " + doc["url"]
							#check for url already in recommendations DB
							if db_recommendation_collection.find({"url": doc["url"]}).skip(0).limit(1).count() == 0: 
								doc["source"]=SOURCE
								doc["dateEntered"] = time.time() * 1000
								#start text processing queue to add it
								start_text_processing_queue(doc, config, True)
						
					else:
						print "Skipping " + doc["url"]
			

import os
import ConfigParser
import pymongo
from pymongo import MongoClient
import json
import collections

# tests tabulating metadata for the user's geo records so that we can make a map
# should go through records, get all geodata ones and say:
# totals_by_country
# totals_by_us_state
# lat/longs (but discard if place reference is a country
# total_record_count
# total_extracted_text_count
# total_geodata_count
# date_range based on the field 'lastVisitTime' -- {start_date is earliest, end_date is latest}

# should store results in collection username.metadata? or somewhere else?

def addGeocoords(geocoords, newCoord):
	for coord in geocoords:
		if coord["lat"] == newCoord["lat"] and coord["lon"] == newCoord["lon"]:
			coord["count"] += 1
			return geocoords

	geocoords.append(newCoord)
	return geocoords


# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

db_client = MongoClient()
db = db_client[config.get('db','name')]
db_collection = db[config.get('db','collection')]

#gather stats
totalDocs = db_collection.find().count()
totalExtractedTextDocs = db_collection.find({ "extracted_text" : { "$exists" : True } }).count()
geoparsedDocs = db_collection.find({ "geodata" : { "$exists" : True } })

metadata = {}

mentionedStates = {}
mentionedCountries = {}

primaryStates = []
primaryCountries = []

geocoords = []

for geoDoc in geoparsedDocs:
	'''
	data should be like 
	primaryCountries[
		{countryCode: "US", count: "132", titles : ['babywearing waltham', 'blah', blah'] }
	]
	'''
	
	for country in geoDoc["geodata"]["primaryCountries"]:
		entered = None
		title = geoDoc["url"]
		if "title" in geoDoc and len(geoDoc["title"]) > 0: 
			title = geoDoc["title"]
		
		for countryEntry in primaryCountries:
			if countryEntry["countryCode"] == country:
				countryEntry["count"] = countryEntry["count"] + 1
				countryEntry["titles"].append(title)
				entered = True
		if entered == None:
			primaryCountries.append({'countryCode':country, 'count':1, 'titles':[ title ]})
			entered = True
		
		# only US states for now
		if country == "US":
			for state in geoDoc["geodata"]["primaryStates"]:
				entered = None

				if len(state) == 2 and state.isalpha():
					for stateEntry in primaryStates:
						if stateEntry["stateCode"] == state:
							stateEntry["count"] = stateEntry["count"] + 1
							stateEntry["titles"].append(title)
							entered = True
					if entered == None:
						primaryStates.append({'stateCode':state, 'count':0, 'titles':[ title ]})
						entered = True
		

	for place in geoDoc["geodata"]["places"]:
		countryCode = place["countryCode"]
		stateCode = place["state"]
		
		# only want lat/longs for places that are NOT countries and NOT states 
		# since we are measuring those with a heatmap
		# see http://www.geonames.org/export/codes.html
		if not str(place["featureCode"]).startswith("PCL") and not str(place["featureCode"]).startswith("ADM1") and not str(place["featureCode"]) == "CONT":
			geocoords = addGeocoords(geocoords, dict(lat=place["lat"], lon=place["lon"], count=1, name=place["name"]))

		if (len(countryCode) > 0):
			mentionedCountries[countryCode] = mentionedCountries.get(countryCode,0) + 1
		
		# only US states for now
		if (len(stateCode) ==2 and countryCode == 'US' and stateCode.isalpha()):
			mentionedStates[stateCode] = mentionedStates.get(stateCode,0) + 1

metadata["total_docs"] = totalDocs
metadata["total_extracted_docs"] = totalExtractedTextDocs
metadata["total_geoparsed_docs"] = geoparsedDocs.count()
metadata["primaryCountries"] = primaryCountries
metadata["primaryStates"] = primaryStates
metadata["mentionedCountries"] = mentionedCountries
metadata["mentionedStates"] = mentionedStates
metadata["geocoords"] = geocoords

with open(config.get('db','name') + '_metadata.txt', 'w') as outfile:
  json.dump(metadata,outfile,sort_keys=True,indent=4, separators=(',', ': '))
print "yah ya'll"


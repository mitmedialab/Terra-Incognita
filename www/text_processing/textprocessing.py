import csv
import requests
import json
import os
from cities_array import *
import httplib
from pymongo import MongoClient

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
reader = csv.DictReader(open(os.path.join(BASE_DIR,"geocodes.csv"),'rU'))
COUNTRIES = [row for row in reader]
reader = csv.DictReader(open(os.path.join(BASE_DIR,"continents.csv"),'rU'))
CONTINENTS = [row for row in reader]
reader = csv.DictReader(open(os.path.join(BASE_DIR,"regions_to_continents.csv"),'rU'))
REGIONS = [row for row in reader]
reader = csv.DictReader(open(os.path.join(BASE_DIR,"cities.csv"),'rU'))
CITIES = [row for row in reader]
GEO_LEVELS = ["continent","region","nation","state","city"]

def addCityGeoDataToDoc(doc):
	for cityToAdd in doc["geodata"]["primaryCities"]:
		for city in THE1000CITIES:
			if int(city["geonames_id"]) == int(cityToAdd["id"]):
				cityToAdd["lat"] = city["lat"]
				cityToAdd["lon"] = city["lon"]
				cityToAdd["population"] = city["pop"]
				cityToAdd["countryCode"] = city["country_code"]
				cityToAdd["countryName"] = city["country_name"]
				cityToAdd["capital"] = city["capital"]
				cityToAdd["global_north"] = city["global_north"]
				cityToAdd["global_south"] = city["global_south"]
				cityToAdd["east"] = city["east"]
				cityToAdd["west"] = city["west"]
				cityToAdd["name"] = city["city_name"]
				break
	return doc

def map_topics(text):
	return ""

# pull out relevant text for url
def extractSingleURL(url,extractorURL):
	result = ""
	try:
		params = {'url':url}
		r = requests.get(extractorURL, params=params)

		if r.status_code == 200:
			json = r.json()

			if "results" in json.keys():
				json = json["results"]
				title = ""
				text = ""
				if "title" in json:
					title = json["title"]
				if "text" in json:
					text = json["text"]
				return title + " " + text

	except requests.exceptions.RequestException as e:
		print "ERROR RequestException " + str(e)

	return result

# pull out geodata for single text from CLIFF_CLAVIN
# optionall merge with existing geodata
def geoparseSingleText(text,geoserver):
	result = {}
	try:
		
		params = {'q':text}
		
		r = requests.post(geoserver, data=params)

		if r.status_code == 200:
			json = r.json()

			if "results" in json.keys():
				json = json["results"]

				#store people for the moment in case we need it later
				if "people" in json.keys():
					result["people"] = json["people"]

				#map CLIFF format to TERRA format, drop place mentions because we don't need them
				if "places" in json.keys() and "about" in json["places"].keys():
					
					json = json["places"]["about"]
					if "cities" in json:
						result["primaryCities"] = json["cities"]
					if "states" in json:
						result["primaryStates"] = json["states"]
					if "countries" in json:
						result["primaryCountries"] = json["countries"]

	except requests.exceptions.RequestException as e:
		print "ERROR RequestException " + str(e)

	return result


# function to match primaryCountry capitals as primaryCities
def lookupCountryCapitalCity(geodata):
	newPrimaryCities = []
	existingPrimaryCities = geodata["primaryCities"]
	for country in geodata["primaryCountries"]:
		
		for cityrow in CITIES:
			
			if cityrow["country_code"] == country and cityrow["capital"] == "1":
		
				newPrimaryCities.append({
					"id" : int(cityrow["geonames_id"]),
					"lat" : cityrow["lat"],
					"lon" : cityrow["lon"],
					"name" : cityrow["city_name"],
					"countryCode" : cityrow["country_code"],
					"population" : cityrow["pop"]
				})
				break

	
	for newcity in newPrimaryCities:
		for existingcity in existingPrimaryCities:
			if newcity["id"] == existingcity["id"]:
				newcity["remove"] = True
				break
	
	newPrimaryCities = [city for city in newPrimaryCities if not "remove" in newcity]
	geodata["primaryCities"].extend(newPrimaryCities)
		
	return geodata

# append continent and region data to the geodata from CLIFF-CLAVIN
# be careful not to modify geodata object while iterating it bc it 
# produces weird behavior
def lookupContinentAndRegion(geodata):
	if geodata is None or not "primaryCountries" in geodata:
		return geodata

	primaryRegions = []
	primaryContinents = []

	for country in geodata["primaryCountries"]:
		region = {}
		continent = {}
		for geocode in COUNTRIES:
			if geocode["country_code"].strip() == country.strip():
				region["country_code"] = geocode["country_code"]
				region["region_name"] = geocode["region_name"]
				region["region_code"] = geocode["region_code"]
				region["continent_name"] = geocode["continent_name"]
				region["continent_code"] = geocode["continent_code"]
				continent["country_code"] = geocode["country_code"]
				continent["continent_name"] = geocode["continent_name"]
				continent["continent_code"] = geocode["continent_code"]
				primaryRegions.append(region)
				primaryContinents.append(continent)
				break
	geodata["primaryRegions"] = primaryRegions
	geodata["primaryContinents"] = primaryContinents

	return geodata

#returns the inverse of the geodata for a particular level, i.e. which continents they HAVEN'T visited, etc
def invertGeodata(geodata, currentLevel):
	invertedResults = []

	if currentLevel == "continent":
		for continent in CONTINENTS:
			invertedResults.append(continent)
		for visitedContinent in geodata:
			continent_code = visitedContinent["_id"]["continent_code"]
			for idx, removeContinent in enumerate(invertedResults):
				if removeContinent["continent_code"] == continent_code:
					invertedResults.pop(idx)
		return invertedResults
	if currentLevel == "nation":
		for nation in COUNTRIES:
			invertedResults.append(nation)
		for visitedNation in geodata:
			country_code = visitedNation["_id"]["country_code"]
			for idx, removeCountry in enumerate(invertedResults):
				if removeCountry["country_code"] == country_code:
					invertedResults.pop(idx)
		return invertedResults
	if currentLevel == "region":
		for region in REGIONS:
			invertedResults.append(region)
		for visitedRegion in geodata:
			region_code = visitedRegion["_id"]["region_code"]
			for idx, removeRegion in enumerate(invertedResults):
				if removeRegion["region_code"] == region_code:
					invertedResults.pop(idx)
		return invertedResults
	if currentLevel == "city":
		for row in CITIES:
			if len(row["city_name"]) > 0:
				invertedResults.append(row)
			
		for visitedCity in geodata:
			city = visitedCity["_id"]["name"]
			for idx, removeCity in enumerate(invertedResults):
				if removeCity["city1"] == city:
					invertedResults.pop(idx)
		return invertedResults

	return 1

def start_text_processing_queue(*args,**kwargs):
	doc = args[0]
	print "starting text processing queue for " + doc['url']

	config = args[1]	
	isRecommendation = args[2]

	uri = "mongodb://"+ config.get('db','user')+ ":"+ config.get('db','pass')+"@" +config.get('db','host') + ":" + config.get('db','port')
	db_client = MongoClient(uri)
	db = db_client[config.get('db','name')]
	alreadyAdded = 0

	if isRecommendation:
		print "the doc is a recommendation"
		db_collection = db[config.get('db','recommendation_item_collection')]
	else:
		print "the doc is a user history item"
		db_collection = db[config.get('db','user_history_item_collection')]

		# make sure doc doesn't already exist
		alreadyAdded = db_collection.find({"userID":doc["userID"], "lastVisitTime":doc["lastVisitTime"], "url":doc["url"]}).count()
		
	if alreadyAdded > 0:
		print "Already added this document for this user. I'm ignoring it now."
	else:
		print "This document is not in the DB"

		# Content Extraction
		doc["extractedText"] = extractSingleURL(doc["url"], config.get('extractor','extractor_url'))

		if (doc["extractedText"] is None or doc["extractedText"] == "") and not isRecommendation:
			print "No extracted Text returned, but saving to DB for user metrics"
			doc["extractedText"] = ""
			db_collection.save(doc)
		else:
			# Geoparsing
			# Only geoparses if there is not already geodata in the doc

			if "geodata" not in doc or ("geodata" in doc and "primaryCities" not in doc["geodata"]):
				print "No prior geodata, moving to geoparse"
				doc["geodata"] = geoparseSingleText(doc["extractedText"], config.get('geoparser','geoserver_url'))
			else:
				print "skipping geoparsing because doc already has geodata"

			# Chance that the geodata might come from the recommendation database instead of geoparser
			# i.e. user submitted video recommendation
			# try that as a second shot at geodata
			# Currently taking the most recently submitted recommendation's geodata, maybe in the future merge all
			# matching recommendations' geodata?
			if "geodata" not in doc:
				print "No geodata found for URL: " + doc['url']
				recommendationCollection = db[config.get('db','recommendation_item_collection')]
				recDocMatches = recommendationCollection.find({'url':doc["url"], "geodata.primaryCities.id" : {"$exists":"true"}}).sort([("lastVisitTime",1)]).limit(1)
				if recDocMatches.count() > 0:
					match = recDocMatches.next()
					doc["geodata"] = match["geodata"]

			# Add Continent and Region info to geodata
			if "geodata" in doc and doc["geodata"] is not None:
				print "Geodata found"
				print "Adding continent and region info to geodata"
				
				doc["geodata"] = lookupContinentAndRegion(doc["geodata"])
				
				# if there is country data but not city data then make the primary city the country's capital city
				if "primaryCountries" in doc["geodata"]:
					doc["geodata"] = lookupCountryCapitalCity(doc["geodata"])


			# Topic Mng
			doc["topics"] = map_topics(doc["extractedText"])

			# Saves to DB 
			# If it is a user history item then remove extracted text (space reasons) and save it to DB
			# because we want to be able to compare user browsing with and without geo
			# If it's a recommendation and no geodata then just discard it because it's not useful to us

			if "geodata" in doc and "primaryCities" in doc["geodata"]:
				print "Saved doc"
				db_collection.save(doc)
			elif "userID" in doc and not isRecommendation:
				print "No geodata, but deleting extracted text and saving to DB for user metrics"
				doc["extractedText"] = ""
				db_collection.save(doc)
			else:
				print "Discarding because no geodata and it's a recommendation: " + doc["url"]

	

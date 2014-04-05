import csv
import requests
import json
import os
from cities_array import *


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

			
#pull out geodata for single text from CLIFF_CLAVIN
def geoparseSingleText(text,geoserver):
	try:
		params = {'text':text}
		
		r = requests.get(geoserver, params=params)
		
		result = r.json()

		if "where" in result.keys() and any(result["where"]):
			print "There's geodata in this text"
			return result["where"]
		else: 
			return {}	

	except requests.exceptions.RequestException as e:
		print "ERROR RequestException " + str(e)

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
	if not "primaryCountries" in geodata:
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

import csv
import requests
import json
import os


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


#pull out geodata for single text from CLIFF_CLAVIN
def geoparseSingleText(text,geoserver):
	try:
		params = {'text':text}
		
		r = requests.get(geoserver, params=params)
		print "geoparsed " + r.url
		
		geodata = r.json()

		if "places" in geodata.keys() and any(geodata["places"]):
			print "RETURNING geodata JSON"
			return geodata
		else: 
			return {}	

	except requests.exceptions.RequestException as e:
		print "ERROR RequestException " + str(e)

# append continent and region data to the geodata from CLIFF-CLAVIN
# be careful not to modify geodata object while iterating it bc it 
# produces weird behavior
def lookupContinentAndRegion(geodata):
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
			if len(row["city1"]) > 0:
				invertedResults.append(row)
			
		for visitedCity in geodata:
			city = visitedCity["_id"]["name"]
			for idx, removeCity in enumerate(invertedResults):
				if removeCity["city1"] == city:
					invertedResults.pop(idx)
		return invertedResults

	return 1

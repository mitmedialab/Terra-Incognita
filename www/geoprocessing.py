import csv
import requests
import json 

GEOCODES = csv.DictReader(open("static/data/geocodes.csv"))
GEO_LEVELS = ["continent","region","nation","state","city"]

#pull out geodata for single text from CLIFF_CLAVIN
def geoparseSingleText(text,geoserver):
	try:
		params = {'text':text}
		
		r = requests.get(geoserver, params=params)
		print r.url
		print json.dumps(r.json(),sort_keys=True,indent=4, separators=(',', ': '))
		
		geodata = r.json()
		if len(geodata["places"]) > 0:
			return geodata
			
	except requests.exceptions.RequestException as e:
		print "ERROR RequestException " + str(e)

#append continent and region data to the geodata from CLIFF-CLAVIN
def lookupContinentAndRegion(geodata):
	geodata["primaryRegions"] = []
	geodata["primaryContinents"] = []

	for country in geodata["primaryCountries"]:
		region = {}
		continent = {}
		print country
		for geocode in GEOCODES:
			if geocode["country_code"].strip() == country.strip():
				region["country_code"] = geocode["country_code"]
				region["region_name"] = geocode["region_name"]
				region["region_code"] = geocode["region_code"]
				region["continent_name"] = geocode["continent_name"]
				region["continent_code"] = geocode["continent_code"]
				continent["country_code"] = geocode["country_code"]
				continent["continent_name"] = geocode["continent_name"]
				continent["continent_code"] = geocode["continent_code"]
				geodata["primaryRegions"].append(region)
				geodata["primaryContinents"].append(continent)

	return geodata

#returns the inverse of the geodata for a particular level, i.e. which continents they HAVEN'T visited, etc
def reverseGeodata(geodata, currentLevel):
	return 1

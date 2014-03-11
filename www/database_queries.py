import csv
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
reader = csv.DictReader(open(os.path.join(BASE_DIR,"static/data/1000cities.csv"),'rU'))
THE1000CITIES = [row for row in reader]

THE1000CITIES_IDS_ARRAY = []
for row in THE1000CITIES:
	if "geonames_id" in row.keys() and len(row["geonames_id"]) > 0:
		THE1000CITIES_IDS_ARRAY.append(int(row["geonames_id"]))


CONTINENT_COUNT_PIPELINE=[
	{ "$project" : { "geodata.primaryContinents":1 }},
	{ "$unwind" : "$geodata.primaryContinents" },
	{ "$group": {"_id": {"continent_code":"$geodata.primaryContinents.continent_code", "continent_name":"$geodata.primaryContinents.continent_name"}, "count": {"$sum": 1}}},
	{ "$sort" : { "count" : -1 } }
]
REGION_COUNT_PIPELINE=[
	{ "$project" : { "geodata.primaryRegions":1 }},
	{ "$unwind" : "$geodata.primaryRegions" },
	{ "$group": {"_id": {"region_code":"$geodata.primaryRegions.region_code", "region_name":"$geodata.primaryRegions.region_name"}, "count": {"$sum": 1}}},
	{ "$sort" : { "count" : -1 } }
]
COUNTRY_COUNT_PIPELINE=[
	{ "$project" : { "geodata.primaryCountries":1 }},
	{ "$unwind" : "$geodata.primaryCountries" },
	{ "$group": {"_id": {"country_code":"$geodata.primaryCountries"}, "count": {"$sum": 1}}},
	{ "$sort" : { "count" : -1 } }
]
STATE_COUNT_PIPELINE=[
	{ "$project" : { "geodata.primaryStates":1 }},
	{ "$unwind" : "$geodata.primaryStates" },
	{"$group": {"_id": {"state_code":"$geodata.primaryStates"}, "count": {"$sum": 1}}},
	{ "$sort" : { "count" : -1 } }
]
CITY_COUNT_PIPELINE = [
	{ "$unwind" : "$geodata.primaryCities" },
	{ "$match" : { "geodata.primaryCities.id": {"$in": THE1000CITIES_IDS_ARRAY } }},
	{ "$group": {"_id": {"geonames_id":"$geodata.primaryCities.id" }, "count": {"$sum": 1}}},
	{ "$sort" : { "count" : -1 } }

]
#THIS DOES NOT WORK PROPERLY
HISTORY_PATH_PIPELINE = [
	{ "$sort" : { "lastVisitTime" : -1 } },
	{ "$match": {"geodata.primaryCities.0":{"$exists": "true"}}},
	{ "$project" : { "url": 1, "title":1,"lastVisitTime":1, "geodata.primaryCities":1 }},

	{"$group" : { "_id" : "$url"}},
	#{ "$group": {"_id": {"url": "$url", "title":"$title","lastVisitTime":"$lastVisitTime"} }},
	#{ "$skip" : 0},
	
	{ "$limit" : 10}

]

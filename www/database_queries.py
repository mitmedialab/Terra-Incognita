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
	{ "$project" : { "geodata.primaryCities":1 }},
	{ "$unwind" : "$geodata.primaryCities" },
	{ "$group": {"_id": {"geonames_id":"$geodata.primaryCities.id", "name":"$geodata.primaryCities.name","state_code":"$geodata.primaryCities.stateCode","country_code":"$geodata.primaryCities.countryCode" }, "count": {"$sum": 1}}},
	{ "$sort" : { "count" : -1 } }

]

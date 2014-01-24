COUNTRY_COUNT_MAP = """function(){
	if (this.geodata){
		for (i in this.geodata.primaryCountries){
			var key = this.geodata.primaryCountries[i];
    			var value = 1;
    			emit(key, value);
		
		}
	}
}"""

STATE_COUNT_MAP = """function(){
	if (this.geodata){
		for (i in this.geodata.primaryStates){
			var key = this.geodata.primaryStates[i];
    			var value = 1;
    			emit(key, value);
		
		}
	}
}"""

CITY_COUNT_MAP="""function(){
	if (this.geodata){
		for (i in this.geodata.primaryCities){
				var key = {id:this.geodata.primaryCities[i].id, name
 : this.geodata.primaryCities[i].name};
    				var value = 1;
    				emit(key, value);
		}
	}
}"""
ALL_COUNT_REDUCE = """function(key, count){
	return Array.sum(count);
}"""

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

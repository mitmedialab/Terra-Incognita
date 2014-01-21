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
	{"$group": {"_id": {"country_code":"$geodata.primaryCountries"}, "count": {"$sum": 1}}},
	{ "$sort" : { "_id" : -1 } }
]
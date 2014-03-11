# Looks up city meta data from the Geonames.org web service
# Format is like this: http://api.geonames.org/searchJSON?q=Z%C3%BCrich,Switzerland&maxRows=1&style=LONG&lang=en&featureClass=P&username=kanarinka

import csv
import requests
import requests.exceptions
import json

CITIES = list(csv.DictReader(open("952Cities_NEW_SMALL_REMOVED.csv",'rU')))


test_file = open('952Cities_NEW.csv','wb')
fieldnames = ["geonames_id","city_name", "toponym_name", "lat", "lon", "population_rank", "pop", "country_name", "country_code", "un_country_code","region_code", "region_name", "continent_code", "continent_name","citation"]
csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
csvwriter.writeheader()

GEONAMES = 'http://api.geonames.org/searchJSON'

class DictUnicodeProxy(object):
    def __init__(self, d):
        self.d = d
    def __iter__(self):
        return self.d.__iter__()
    def get(self, item, default=None):
        i = self.d.get(item, default)
        if isinstance(i, unicode):
            return i.encode('utf-8')
        return i

for row in CITIES:
	new_row = row.copy()
	if len(row["geonames_id"]) > 0:
		csvwriter.writerow(DictUnicodeProxy(new_row))
	else:
		
		try:
			params = {'q': row["city_name"] + "," + row["country_name"], 'maxRows':1, 'lang':'en', 'style':'LONG','featureClass':'P','username':'kanarinka' }
			
			r = requests.get(GEONAMES, params=params)
			#print r.url
			#print json.dumps(r.json(),sort_keys=True,indent=4, separators=(',', ': '))
			
			res = r.json()
			if res.get("geonames") == None or (res.get("geonames") is not None and len(res["geonames"]) == 0):
				#print 'No match. Trying with just city name.'
				
				params = {'q': row["city_name"], 'maxRows':1, 'lang':'en', 'style':'LONG','featureClass':'P','username':'kanarinka' }
				r = requests.get(GEONAMES, params=params)
				
				res = r.json()
				if res.get("geonames") == None or (res.get("geonames") is not None and len(res["geonames"]) == 0):
					print "NO GEONAMES MATCH FOR " + row["city_name"] + ", " + row["country_name"]
					new_row["city_name"] = row["city_name"]
					new_row["country_name"] = row["country_name"]
					new_row["population_rank"] = row["population_rank"]
					new_row["lat"] = row["lat"]
					new_row["lon"] = row["long"]
					csvwriter.writerow(DictUnicodeProxy(new_row))
					continue

			resGeo = res["geonames"][0]
			print row["city_name"]
			new_row["geonames_id"] = resGeo["geonameId"]
			new_row["city_name"] = resGeo["name"]
			new_row["toponym_name"] = resGeo["toponymName"]
			new_row["lat"] = resGeo["lat"]
			new_row["lon"] = resGeo["lng"]
			new_row["population_rank"] = row["population_rank"]
			new_row["pop"] = resGeo["population"]
			new_row["country_name"] = resGeo["countryName"]
			new_row["country_code"] = resGeo["countryCode"]
			csvwriter.writerow(DictUnicodeProxy(new_row))
			
		except requests.exceptions.RequestException as e:
			print "ERROR RequestException " + str(e)

	



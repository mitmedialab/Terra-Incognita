import bitly_api
import os
import json
import csv
import time

'''
Iterate through ~ 400 cities from file and search bitly API for recommendations

Privilege globalvoicesonline domain because alternate perspectives on geography 
so try stories that are trending from that domain first.

Rec Search logic:
- Country geo + globalvoicesonline.org domain (map to city anyways)
- City geo + topic 
- just City geo

Stop when have received max 10 recommendations for that city. Save to recommendations collection in DB.
'''

BITLY_ACCESS_TOKEN = "BITLY_ACCESS_TOKEN"
TOPICS = ["advertising","agriculture","art","automotive","aviation","banking","business","celebrity","computer","disasters","drugs","economics","education","energy","entertainment","fashion","finance","food","games","health","hobbies","humor","intellectual property","labor","legal","lgbt","marriage","military","mobile devices","news","philosophy","politics","real estate","reference","science","sexuality","shopping","social media","sports","technology","travel","weapons","weather"]

#	Batch Seed Recommendations seeds geo-specific news recommendations in the DB
#
#
class BatchSeedRecommendations():
	def __init__(self, doc_cursor, db_collection):
		self.doc_cursor = doc_cursor
		self.db_collection = db_collection
		self.bitly = self.get_bitly_connection()
		self.cities = list(csv.DictReader(open("cities.csv",'rU')))

	def get_bitly_connection(self):
		"""Create a Connection based on username and access token credentials"""
		if BITLY_ACCESS_TOKEN not in os.environ:
			raise ValueError("Environment variable '{}' required".format(BITLY_ACCESS_TOKEN))
		access_token = os.getenv(BITLY_ACCESS_TOKEN)
		bitly = bitly_api.Connection(access_token=access_token)
		return bitly
	
	def run(self):
		for city_row in self.cities:
			r = self.search_city(city_row["city1"])
			
			print str(len(r)) + " RESULTS"
			for result in r:
				print result["title"]
				print result["url"]
				
			
			#r = self.search_city(city_row["city2"])
			#print json.dumps(r, sort_keys=True,indent=4, separators=(',', ': '))
			
			print "sleeping"
			time.sleep(5)
			print "woke up"
			
			break
			
	def search_city(self, city):
		print "SEARCH FOR " + city
		return self.bitly.search(city, fields="title,summaryTitle,description,url")
		
		

		'''print "SEARCH FOR global voices & " + city_row["country_name"]
		r = self.bitly.search(city_row["country_name"], fields="title,summaryTitle, description, url", domain="globalvoicesonline.org")
		'''

		'''for topic in TOPICS:
			print "SEARCH FOR " + topic  + " " + city
			r = self.bitly.search("topic:[{" + topic + "}] '" + city + "'", fields="title,summaryTitle, description, url", domain="globalvoicesonline.org")
			print json.dumps(r, sort_keys=True,indent=4, separators=(',', ': '))'''

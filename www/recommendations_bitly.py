import os
import bitly_api
from cities_array import *

TOPICS = ["advertising","agriculture","art","automotive","aviation","banking","business","celebrity","computer","disasters","drugs","economics","education","energy","entertainment","fashion","finance","food","games","health","hobbies","humor","intellectual property","labor","legal","lgbt","marriage","military","mobile devices","news","philosophy","politics","real estate","reference","science","sexuality","shopping","social media","sports","technology","travel","weapons","weather"]

#until we really integrate topic mapping
TMP_USER_TOPICS = ["news","politics","entertainment"]

def get_recommended_bitly_url(cityID, bitlyToken):
	bitly = get_bitly_connection(bitlyToken)
	placedata = {}
	for row in THE1000CITIES:
		if cityID == int(row["geonames_id"]):
			placedata = row
			break
	if not placedata:
		print "No recommendation because ID not in Cities list"
		return "http://globalvoicesonline.org"

	#adjust place text that search for based on how big place is
	if int(placedata["pop"]) > 15000 and int(placedata["pop"]) < 10000000:
		place = placedata["city_name"] + " " + placedata["country_name"] 
	elif int(placedata["pop"]) > 10000000:
		place = placedata["city_name"]
	else:
		place = placedata["country_name"]

	#try global voices but only with city name since their
	#articles tend to mention long lists of countries
	results = bitly.search(placedata["city_name"], domain="globalvoicesonline.org")
	if len(results) > 0:
		print "Global Voices Recommendation"
		result = pick_longest_result(results)
		return result["url"]
	else:
		#try topics
		for topic in TMP_USER_TOPICS:
			results = bitly.search("topic:[{"+ topic +"}] '"+ place + "'")
			if len(results) > 0:
				print "Topic Recommendation: " + topic
				result = pick_longest_result(results)
				return result["url"]
		
		#try just geo
		results = bitly.search(place)
		if len(results) > 0:
			print "Non-Topic Recommendation " + results[0]["url"]
			result = pick_longest_result(results)
			return result["url"]
		else:
			print "No recommendation"
			return "https://en.wikipedia.org/wiki/" + place

def pick_longest_result(results):
	result = None
	longest_length = 0
	for site in results:
		if len(site["content"]) > longest_length:
			longest_length = len(site["content"])
			result = site
	return result


def get_bitly_connection(token):
	"""Create a Connection based on username and access token credentials"""
	if not token:
		raise ValueError("Can't connect to bitly without a token!")
	#access_token = os.getenv(BITLY_ACCESS_TOKEN)
	bitly = bitly_api.Connection(access_token=token)
	return bitly

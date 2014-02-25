import os
import bitly_api

BITLY_ACCESS_TOKEN = "BITLY_ACCESS_TOKEN"
TOPICS = ["advertising","agriculture","art","automotive","aviation","banking","business","celebrity","computer","disasters","drugs","economics","education","energy","entertainment","fashion","finance","food","games","health","hobbies","humor","intellectual property","labor","legal","lgbt","marriage","military","mobile devices","news","philosophy","politics","real estate","reference","science","sexuality","shopping","social media","sports","technology","travel","weapons","weather"]

#until we really integrate topic mapping
TMP_USER_TOPICS = ["news","politics","entertainment"]

def get_recommended_url(place):
	bitly = get_bitly_connection()

	#try global voices
	results = bitly.search(place, domain="globalvoicesonline.org")
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
			print "resetting result to the longer"
			longest_length = len(site["content"])
			result = site
	return result


def get_bitly_connection():
	"""Create a Connection based on username and access token credentials"""
	if BITLY_ACCESS_TOKEN not in os.environ:
		raise ValueError("Environment variable '{}' required".format(BITLY_ACCESS_TOKEN))
	access_token = os.getenv(BITLY_ACCESS_TOKEN)
	bitly = bitly_api.Connection(access_token=access_token)
	return bitly

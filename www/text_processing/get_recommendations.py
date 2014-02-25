import bitly_api
import os
import json

'''
Receives geography and topics. Privilege globalvoicesonline domain because
alternate perspectives on geography so try stories that are trending from that
domain first.

Rec Search starts with finest grain:
- City geo + topic + globalvoicesonline.org domain

- If no city, then go to country as geo

- geo + topic

- just geo

Stop when have received 3 recommendations. Save to recommendations collection in DB.
'''

BITLY_ACCESS_TOKEN = "BITLY_ACCESS_TOKEN"

def get_connection():
	"""Create a Connection based on username and access token credentials"""
	if BITLY_ACCESS_TOKEN not in os.environ:
		raise ValueError("Environment variable '{}' required".format(BITLY_ACCESS_TOKEN))
	access_token = os.getenv(BITLY_ACCESS_TOKEN)
	bitly = bitly_api.Connection(access_token=access_token)
	return bitly

bitly = get_connection()
resp = conn.search("topic:[{sports}] 'New Zealand'", fields="title,summaryTitle, description, cities, url")

print json.dumps(resp, sort_keys=True,indent=4, separators=(',', ': '))

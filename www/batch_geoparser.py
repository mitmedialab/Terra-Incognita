import requests
import requests.exceptions
import json

#	BatchExtractor takes a cursor of MongoDB docs,
# 	grabs the content, extracts the geodata, and saves the content back to the DB


class BatchGeoparser():
	def __init__(self, doc_cursor, db_collection, geoserver_url):
		self.doc_cursor = doc_cursor
		self.db_collection = db_collection
		self.geoserver_url = geoserver_url
		
	def run(self):
		for doc in self.doc_cursor:
			
			text = doc['extracted_text']
			if len(text) > 0:
				try:
					params = {'text':text}
					
					r = requests.get(self.geoserver_url, params=params)
					print r.url
					print json.dumps(r.json(),sort_keys=True,indent=4, separators=(',', ': '))
					
					res = r.json()
					if len(res["places"]) > 0:
						doc['geodata'] = res
						self.db_collection.save(doc)
				except requests.exceptions.RequestException as e:
					print "ERROR RequestException " + str(e)
			

def geoparseSingleText(text):
	try:
		params = {'text':text}
		
		r = requests.get(app.geoserver, params=params)
		print r.url
		print json.dumps(r.json(),sort_keys=True,indent=4, separators=(',', ': '))
		
		geodata = r.json()
		if len(geodata["places"]) > 0:
			return geodata
			
	except requests.exceptions.RequestException as e:
		print "ERROR RequestException " + str(e)
def lookupContinentAndRegion(geodata):
	
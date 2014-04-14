from boilerpipe.extract import Extractor
def extractSingleURL(doc):
	url = doc["url"]
	print doc
	try:
		extractor = Extractor(extractor='ArticleExtractor', url=url)
		extractedText = extractor.getText()
		if (len(extractedText) > 0):
			# make sure to include title in the extracted text object so it
			# gets geoparsed
			title = extractor.getTitle()
			
			if title is not None:
				extractedText = title + " " + extractedText
				doc["title"] = title
			print 'EXTRACTED - ' + url
			doc["extractedText"] = extractedText
			return doc
	except IOError, err:
		print "IOError with url " + url
		print str(err)
	except (LookupError):
		print "LookupError - Maybe not text or weird encoding " + url
	except (UnicodeDecodeError, UnicodeEncodeError):
		print "UnicodeDecodeError or UnicodeEncodeError- " + url
	except Exception, err:
		print "Unknown Exception: " + url
		print str(err)
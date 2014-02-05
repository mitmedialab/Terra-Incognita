from boilerpipe.extract import Extractor
def extractSingleURL(url):
	try:
		extractor = Extractor(extractor='ArticleExtractor', url=url)
		extractedText = extractor.getText()
		print (extractor.getHTML())
		if (len(extractedText) > 0):
			# make sure to include title in the extracted text object so it
			# gets geoparsed
			title = extractor.getTitle()
			
			if title is not None:
				extractedText = title + " " + extractedText
			print 'EXTRACTED -' + url
			return extractedText
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
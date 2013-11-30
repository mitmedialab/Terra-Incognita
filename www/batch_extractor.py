from boilerpipe.extract import Extractor
import httplib

#	BatchExtractor takes a cursor of MongoDB docs,
# 	grabs the URLS, extracts the content, and saves the content back to the DB in the 'extracted_text' field
# 	Use urls_to_ignore.txt to tell it what to ignore

class BatchExtractor():
	def __init__(self, doc_cursor, db_collection):
		self.doc_cursor = doc_cursor
		self.db_collection = db_collection
		text_file = open("urls_to_ignore.txt", "r")
		lines = text_file.readlines()
		self.blacklisted_domains = [line.strip() for line in lines]
		
	def run(self):
		for doc in self.doc_cursor:
			url = doc['url']
			print url
			if (self.keepText(url)):
				try:
					extractor = Extractor(extractor='ArticleExtractor', url=url)
					extracted_text = extractor.getText()
					print extracted_text
					if (len(extracted_text)) > 0):
						doc['extracted_text'] = extracted_text
						self.db_collection.save(doc)
				except (IOError, httplib.HTTPException):
					print "HTTPException with url " + url
				except (LookupError):
					print "LookupError - Maybe not text or weird encoding " + url
	def keepText(self, url):
		for domain in self.blacklisted_domains:
			if domain in url:
				print 'discarding url because its in the urls_to_ignore.txt file'
				return False
		return True


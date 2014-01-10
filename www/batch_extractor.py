from boilerpipe.extract import Extractor
import httplib


#	BatchExtractor takes a cursor of MongoDB docs,
# 	grabs the URLS, extracts the content, and saves the content back to the DB in the 'extracted_text' field
# 	Use urls_to_ignore.txt to tell it what to ignore like gmail, etc

class BatchExtractor():
	def __init__(self, doc_cursor, db_collection):
		self.doc_cursor = doc_cursor
		self.db_collection = db_collection
		
		text_file = open("urls_to_ignore.txt", "r")
		lines = text_file.readlines()
		self.blacklisted_domains = [line.strip() for line in lines]

		csv_file = open("media_sources_tld_whitelist.csv", "r")
		lines = csv_file.readlines()
		self.whitelisted_domains = [line.strip() for line in lines]

		
	def run(self):
		count = 0
		docCount = self.doc_cursor.count()
		for doc in self.doc_cursor:
			url = doc['url']
			if (self.keepText(url)):
				try:
					extractor = Extractor(extractor='ArticleExtractor', url=url)
					extracted_text = extractor.getText()
				
					if (len(extracted_text) > 0):
						title = extractor.getTitle()
						
						if title != None:
							doc['title'] = title
							doc['extracted_text'] = title + " " + extracted_text
						else:
							doc['extracted_text'] = extracted_text
						self.db_collection.save(doc)
						print 'OK -' + url
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
			count+=1
			print "Processed " + str(count) + "/" +  str(docCount)

	def keepText(self, url):
		#check domains to ignore FIRST because it's the shorter list
		for domain in self.blacklisted_domains:  
			if domain.lower() in url.lower():
				print "IGNORING FROM BLACKLIST: " + str(url)
				return False
		# then check mediacloud whitelist
		# if finds domain in url then check that the previous character in url is either . or / to 
		# prevent matches like ct.com being found in http://circuit.com 
		for domain in self.whitelisted_domains:  
			if domain.lower() in url.lower() and url[url.lower().find(domain.lower()) - 1] == '/' or url[url.lower().find(domain.lower()) - 1] == '.':
				print "INCLUDING FROM WHITELIST: " + domain + str(url)
				return True
		print "IGNORING BECAUSE NOT ON WHITELIST: " + str(url)
		return False


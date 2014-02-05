from boilerpipe.extract import Extractor
import httplib

def check(url):
  doc = {}
  #try: 
  extractor = Extractor(extractor='DefaultExtractor', url=url)
  extracted_text = extractor.getText()

  if (len(extracted_text) > 0):
    title = extractor.getTitle()
    '''print url
       print extractor.getTitle()
       print extracted_text'''
    if title != None:
      doc['title'] = title
      doc['extracted_text'] = title + " " + extracted_text
    else:  
      doc['extracted_text'] = extracted_text
      print 'OK -' + url
  return doc

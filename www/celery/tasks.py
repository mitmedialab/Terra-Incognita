from celery import Celery
from celery.utils.log import get_task_logger
from boilerpipe.extract import Extractor
import httplib

app = Celery('tasks', backend ="amqp", broker='amqp://guest@localhost//')

logger = get_task_logger(__name__)


## TO CALL THIS FROM ELSEWHERE IN PYTHON
## from tasks import extract
## extract.delay("http://natematias.com")
## remember to start the celery server at start.sh

@app.task
def extract(url):
  doc = {}
  logger.info("about to load URL")
  try: 
    extractor = Extractor(extractor='ArticleExtractor', url=url)
    logger.info("extractor successful")
    extracted_text = extractor.getText()
    logger.info("returning text")
  except:
    traceback.print_exc

  #geoparse.delay(extracted_text)
  #map_topics.delay(extracted_text) 

  return extracted_text

  #if (len(extracted_text) > 0):
  #  title = extractor.getTitle()
  #  '''print url
  #     print extractor.getTitle()
  #     print extracted_text'''
  #  if title != None:
  #    doc['title'] = title
  #    doc['extracted_text'] = title + " " + extracted_text
  #else:  
  #  doc['extracted_text'] = extracted_text
  #  print 'OK -' + url
  #return doc['extracted_text']
  #except (IOError, httplib.HTTPException):
  #  print "HTTPException with url " + url
  #except (LookupError):
  #  print "LookupError - Maybe not text or weird encoding " + url
  #except (UnicodeDecodeError, UnicodeEncodeError):
  #  print "UnicodeDecodeError or UnicodeEncodeError- " + url
  #except:
  #  print "Unknown Exception: " + url

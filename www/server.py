import os
import logging
import ConfigParser
import pymongo
from pymongo import MongoClient
from flask import Flask, render_template, json, jsonify, request
import pprint

# constants
CONFIG_FILENAME = 'app.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# read in app config
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

app = Flask(__name__,static_url_path='')
db_client = MongoClient()
db = db_client[config.get('db','name')]
db_collection = db[config.get('db','collection')]

# setup logging and pretty printing
pp = pprint.PrettyPrinter(indent=4)
handler = logging.FileHandler('server.log')
logging.basicConfig(filename='server.log',level=logging.DEBUG)
log = logging.getLogger('server')
log.info("---------------------------------------------------------------------------")


#Index test 
@app.route('/')
def hello():
	return "Hello Supposed Human. This server is running."

#Individual Map test 
@app.route('/individual_map.html')
def individual_map():
	return app.send_static_file('individual_map.html')

#DR Map test 
@app.route('/dr_map.html')
def dr():
	return app.send_static_file('dr_map.html')

#RB Map test 
@app.route('/rb_map.html')
def rb():
	return app.send_static_file('rb_map.html')

#EDP Map test 
@app.route('/edp_map.html')
def edp():
	return app.send_static_file('edp_map.html')

#EG Map test 
@app.route('/eg_map.html')
def eg():
	return app.send_static_file('eg_map.html')


#EG Whitelist Map test 
@app.route('/eg_whitelist_map.html')
def eg_whitelist():
	return app.send_static_file('eg_whitelist_map.html')

#CSD Map test 
@app.route('/csd_map.html')
def csd():
	return app.send_static_file('csd_map.html')

#Example sending JSON
@app.route('/map.json')
def map():
    return jsonify(userid=2, map='this is a json get test');

@app.route('/history/', methods=['POST'])
def processHistory():
	log.info("Processing browser history")
	historyItems = json.loads(request.form['history'])
	docIDs = db_collection.insert(historyItems)
	#batchExtractor = BatchExtractor(docIDs, db_collection)
	#batchExtractor.run()
	# TODO
	# batchExtractor = BatchExtractor(docIDs, db_collection)
	# check if this user already has history doc, if so, then ignore this request
	# save 30 days of history to mongoDB as single doc
	# mark that info as history (documentType = history) so can compare to after using extension
	# start the geoparsing, text processing queue for that info
	# send back status "Working on your map"
	return 'Got your message dude - inserted and extracted' + str(len(docIDs)) + ' history items'

# Receives a single URL object from user, geoparses and stores in DB
@app.route('/monitor/', methods=['POST'])
def processURL():
	log.info("Receiving new URL")
	historyObject = json.loads(request.form['logURL'])
	docID = db_collection.insert(historyObject)
	
	# TODO
	# save to mongoDB as single doc
	# mark as NOT history (documentType = something else)
	# start the geoparsing, text processing queue for that info
	# send back status "Updating your map" or something like that
	return 'Got your URL dude - ' + historyObject["url"]

if __name__ == '__main__':
	#running on 0.0.0.0 to be accessible to other machines on network
    app.run(debug=True,host= '0.0.0.0')
    log.info("Started Server")

'''
#Example calling a template
@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

#Example using a variable in the URL
@app.route('/user/<username>')
def show_user_profile(username):
    return 'User %s' % username
'''

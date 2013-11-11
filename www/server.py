
import logging
from flask import Flask, render_template, json, jsonify, request
import pprint

app = Flask(__name__)

# setup logging
pp = pprint.PrettyPrinter(indent=4)
handler = logging.FileHandler('server.log')
logging.basicConfig(filename='server.log',level=logging.DEBUG)
log = logging.getLogger('server')
log.info("---------------------------------------------------------------------------")

#Example sending JSON 
@app.route('/map.json')
def map():
    return jsonify(userid=2, map='this is a json get test');

@app.route('/history/', methods=['POST'])
def processHistory():
	log.info("Processing browser history")
	history30days = json.loads(request.form['history'])
	# check if this user already has history doc, if so, then ignore this request
	# save 30 days of history to mongoDB as single doc
	# mark that info as history (documentType = history) so can compare to after using extension
	# start the geoparsing, text processing queue for that info
	# send back status "Working on your map"
	return 'Got your message dude'

# Receives a single URL object from user, geoparses and stores in DB
@app.route('/monitor/', methods=['POST'])
def processURL():
	log.info("Receiving new URL")
	logURL = json.loads(request.form['logURL'])
	# save to mongoDB as single doc
	# mark as NOT history (documentType = something else)
	# start the geoparsing, text processing queue for that info
	# send back status "Updating your map" or something like that
	return 'Got your URL dude - ' + logURL["url"]

if __name__ == '__main__':
    app.run(debug=True)
    log.info("Started Server")

'''
#Home page example
@app.route('/')
def hello_world():
    return 'Hello asdWorld!'

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

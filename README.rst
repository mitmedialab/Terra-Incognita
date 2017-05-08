=================
Terra Incognita
=================

A personal media geography browser and recommendation system.

Configuration
=============

Dependencies:

- MongoDB - need 3.4.0 or higher

Through PIP or easy_install:

- tld (utility for extracting top level domain names)

- Python Flask 

- Flask Browser ID - https://pypi.python.org/pypi/Flask-BrowserID

- ~~Bitly Python API - https://github.com/bitly/bitly-api-python~~

- Reddit API - https://www.reddit.com/dev/api/

Services:

- An instance of CLIFF for geoparsing: https://github.com/c4fcm/CLAVIN-Server

- An instance of Boilerpipe-Server for content extraction - https://github.com/c4fcm/Boilerplate-Server


What needs to be running for Terra Incognita to do its work
=====
- Apache Server
- Flask Server
- MongoDB
- CLIFF CLAVIN - accessed over http
- Boilerpipe Server - accessed over http

MongoDB Configuration
=====
Create an index on the user history items collection like this:
db.user_history_items.createIndex( { "lastVisitTime": -1 } )



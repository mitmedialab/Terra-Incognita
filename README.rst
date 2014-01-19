=================
Terra Incognita
=================

A personal media geography browser and recommendation system.

Configuration
=============

Dependencies:

You will need an instance of the Clavin-Server to speak with over http: https://github.com/c4fcm/CLAVIN-Server

You need to install: 
- python-boilerpipe from my fork - https://github.com/kanarinka/python-boilerpipe -for content extraction. This is a python wrapper around boilerpipe - https://code.google.com/p/boilerpipe/.

- jpype (for using python-boilerpipe for content extraction). I used @originell's fork on github that makes it easier for installing on MacOSX: https://github.com/originell/jpype.

- MongoDB

Through PIP or easy_install:

- charade (for using python-boilerpipe for content extraction)

- tld (utility for extracting top level domain names)

- Python Flask 

- Flask Browser ID - https://pypi.python.org/pypi/Flask-BrowserID


Usage
=====
To run scripts for individual's data (temporary) -
- change db to their db name
- run test_batch_extraction.py, test_batch_geocoding.py, test_metadata_generator.py


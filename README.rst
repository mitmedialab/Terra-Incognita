=================
Terra Incognita
=================

A personal media geography browser and recommendation system.

Configuration
=============

Dependencies:

You will need an instance of the Clavin-Server to speak with over http: https://github.com/c4fcm/CLAVIN-Server

You need to install 
- python-boilerpipe from my fork - https://github.com/kanarinka/python-boilerpipe -for content extraction. This is a python wrapper around boilerpipe - https://code.google.com/p/boilerpipe/.

- jpype (for using python-boilerpipe for content extraction). I used @originell's fork on github that makes it easier for installing on MacOSX: https://github.com/originell/jpype.

- charade (for using python-boilerpipe for content extraction)

- tld (utility for extracting top level domain names)

- MongoDB



To test whether python-boilerpipe is working properly - try running test_content_extraction.py.

Usage
=====
To run scripts for individual's data (temporary) -
- change db to their db name
- run test_batch_extraction, test_batch_geocoding


=================
Terra Incognita
=================

A personal media geography browser and recommendation system.

Configuration
=============

Dependencies:
Includes python-boilerpipe - https://github.com/misja/python-boilerpipe/ -for content extraction. This is a python wrapper around boilerpipe - https://code.google.com/p/boilerpipe/.

You will need an instance of the Clavin-Server to speak with over http: https://github.com/c4fcm/CLAVIN-Server

You need to install 
- jpype (for using python-boilerpipe for content extraction)
- charade (for using python-boilerpipe for content extraction)
- tld (utility for extracting top level domain names)

For JPype, I used originell's fork on github that makes it easier for installing on MacOSX: https://github.com/originell/jpype.

To test whether python-boilerpipe is working properly - try running test_content_extraction.py.

Usage
=====



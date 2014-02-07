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

- Celery and RabbitMQ for queue management - http://www.celeryproject.org/

- Enable RabbitMQ's management plugin - "rabbitmq-plugins enable rabbitmq_management" (May have to tweak PATH variable to get this to work)

- Install Flower - http://docs.celeryproject.org/en/master/userguide/monitoring.html#flower-real-time-celery-web-monitor

- Use Celery along with Eventlet because Boilerpipe will break with Celery's default multiprocessing pools: https://github.com/celery/celery/tree/master/examples/eventlet

What needs to be running for Terra Incognita to do its work
=====
- Apache Server
- Flask Server
- MongoDB
- RabbitMQ
- Celery
- Celery Flower
- CLIFF CLAVIN (CLAVIN-Server) - accessed over http

Usage
=====
To run scripts for individual's data (temporary) -
- change db to their db name
- run test_batch_extraction.py, test_batch_geocoding.py, test_metadata_generator.py


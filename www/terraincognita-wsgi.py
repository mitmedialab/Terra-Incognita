import sys
import os
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
from server import app as application

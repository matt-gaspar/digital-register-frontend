import os, logging
from flask import Flask
import time
from time import strftime

import requests

app = Flask(__name__)

def format_datetime(value):
  return strftime("%d %b %Y at %H:%M:%S", time.strptime(value, "%Y-%m-%d %H:%M:%S"))

app.config.from_object(os.environ.get('SETTINGS'))
app.jinja_env.filters['datetime'] = format_datetime

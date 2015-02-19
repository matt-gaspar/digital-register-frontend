import os, logging
from flask import Flask
import dateutil
import dateutil.parser

import requests

app = Flask(__name__)

def format_datetime(value):
  return dateutil.parser.parse(value).strftime("%d %B %Y at %H:%M:%S")

app.config.from_object(os.environ.get('SETTINGS'))
app.jinja_env.filters['datetime'] = format_datetime

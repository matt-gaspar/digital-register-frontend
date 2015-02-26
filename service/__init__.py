import os, logging
from flask import Flask
import dateutil
import dateutil.parser
import requests

from config import CONFIG_DICT


app = Flask(__name__)
app.config.update(CONFIG_DICT)


def format_datetime(value):
    return dateutil.parser.parse(value).strftime("%d %B %Y at %H:%M:%S")


app.jinja_env.filters['datetime'] = format_datetime

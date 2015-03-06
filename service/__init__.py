import logging
from logging import config
from flask import Flask
import dateutil
import dateutil.parser
import json

from config import CONFIG_DICT


app = Flask(__name__)
app.config.update(CONFIG_DICT)


def format_datetime(value):
    return dateutil.parser.parse(value).strftime("%d %B %Y at %H:%M:%S")

def setup_logging(logging_config_file_path):
    try:
        with open(logging_config_file_path, 'rt') as file:
            config = json.load(file)
        logging.config.dictConfig(config)
    except IOError as e:
        raise(Exception('Failed to load logging configuration', e))


app.jinja_env.filters['datetime'] = format_datetime
setup_logging(app.config['LOGGING_CONFIG_FILE_PATH'])

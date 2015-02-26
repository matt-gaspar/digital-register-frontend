import os

CONFIG_DICT = {
    'DEBUG': False,
    'REGISTER_TITLE_API': 'http://landregistry.local:8004/',
}

settings = os.environ.get('SETTINGS')

if settings == 'dev':
    CONFIG_DICT['DEBUG'] = True
elif settings == 'test':
    CONFIG_DICT['DEBUG'] = True
    CONFIG_DICT['TESTING'] = True

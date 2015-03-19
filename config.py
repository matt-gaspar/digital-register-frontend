import os

register_title_api = os.environ['REGISTER_TITLE_API']
logging_config_file_path = os.environ['LOGGING_CONFIG_FILE_PATH']
google_analytics_api_key = os.environ['GOOGLE_ANALYTICS_API_KEY']

CONFIG_DICT = {
    'DEBUG': False,
    'REGISTER_TITLE_API': register_title_api,
    'LOGGING_CONFIG_FILE_PATH': logging_config_file_path,
    'GOOGLE_ANALYTICS_API_KEY': google_analytics_api_key,
}

settings = os.environ.get('SETTINGS')

if settings == 'dev':
    CONFIG_DICT['DEBUG'] = True
elif settings == 'test':
    CONFIG_DICT['DEBUG'] = True
    CONFIG_DICT['TESTING'] = True

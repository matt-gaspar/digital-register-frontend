import os

class Config(object):
    DEBUG = False
    REGISTER_TITLE_API='http://landregistry.local:8003/'

class DevelopmentConfig(Config):
    DEBUG = True

class TestConfig(DevelopmentConfig):
    TESTING = True

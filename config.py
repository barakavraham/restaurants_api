import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class DevConfig:
    CONFIG_NAME = 'dev'
    SQLALCHEMY_DATABASE_URI = (os.environ.get('SQLALCHEMY_DATABASE_URI')
                               or 'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS=False


class TestingConfig:
    CONFIG_NAME = 'testing'
    SQLALCHEMY_DATABASE_FILE = os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + SQLALCHEMY_DATABASE_FILE
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS=False


config = {
    'development': DevConfig,
    'testing': TestingConfig
}
# Production Configuration

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # POSTGRES = {
    #     'user': 'vidyut',
    #     'pw': 'vidyut2018*',
    #     'db': 'vidyut',
    #     # 'host': 'vidyut.c2ri3nat2mul.ap-south-1.rds.amazonaws.com',
    #     'port': '5432',
    # }
    # SQLALCHEMY_DATABASE_URI = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # MAIL_SERVER = 'smtp.office365.com'
    # MAIL_PORT = 587
    # MAIL_USE_TLS = True
    # MAIL_USERNAME = 'no-reply@vidyut.amrita.edu'
    # MAIL_PASSWORD = 'amma@123'
    # MAIL_DEFAULT_SENDER = 'no-reply@vidyut.amrita.edu'
    # MAIL_MAX_EMAILS = 3000
    HOST_LOC = 'production'
    DEVELOPMENT = True
    DEBUG = True
    MAINTENANCE = False

class TestingConfig(Config):
    TESTING = True

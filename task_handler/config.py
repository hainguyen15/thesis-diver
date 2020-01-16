import os

class Config(object):
    """Base config, uses staging database server."""
    DEBUG       = False
    TESTING     = False
    DB_SERVER   = 'localhost'
    
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT   = 587
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'kid.katou1@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'Asihdaiufs123')
    MAIL_DEFAULT_SENDER = 'Diver System'

    # @property
    # def DATABASE_URI(self):
    #     return 'mysql://user@{}/foo'.format(self.DB_SERVER)

class DevelopmentConfig(Config):
    SECRET_KEY = 'mtf83pg$z/L"@sRqKQ[zk6SNQe"}@,3ZD@u{t18Ka?Phig>+K}y[}@Mwkn(^4/e'
    DB_SERVER = 'localhost'
    DEBUG = True
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

class ProductionConfig(Config):
    """Uses production database server."""
    DB_SERVER = '192.168.19.32'

class TestingConfig(Config):
    DB_SERVER = 'localhost'
    DEBUG = True
    DATABASE_URI = 'sqlite:///:memory:'

class Config(object):
    """
    Base configuration. Other configs inherit from this class
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = False

    DB_NAME = "postgres"
    DB_PASSWORD = "postgres"
    DB_USER = "postgres"
    DB_HOST = "localhost"

    CACHE_TYPE = 'simple'


class ProductionConfig(Config):
    """
    Production configuration.
    """
    ENV = 'prod'
    DEBUG = False


class DevelopmentConfig(Config):
    """
    Development configuration
    """
    ENV = 'dev'
    DEBUG = True
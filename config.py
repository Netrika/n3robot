from os import environ, getenv


class Config(object):
    TELEGRAM_BOT_TOKEN = environ['TELEGRAM_BOT_TOKEN']
    PROJECT_URL = getenv('PROJECT_URL', 'http://127.0.0.1')
    WIKI_URL = getenv('WIKI_URL', '')

    MONGODB_DATABASE = getenv('MONGODB_DATABASE', 'n3robot')
    MONGODB_USER = getenv('MONGODB_USER', 'n3robot')
    MONGODB_PASSWORD = getenv('MONGODB_PASSWORD')
    MONGODB_HOST = getenv('MONGODB_HOST', '127.0.0.1')
    REDIS_HOST = getenv('REDIS_HOST', '127.0.0.1')

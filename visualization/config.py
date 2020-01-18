import os

class BaseConfig(object):
    SLIDE_CACHE_SIZE = 10
    DEEPZOOM_FORMAT = 'jpeg'
    DEEPZOOM_TILE_SIZE = 254
    DEEPZOOM_OVERLAP = 1
    DEEPZOOM_LIMIT_BOUNDS = False
    DEEPZOOM_TILE_QUALITY = 100
    PROJECT_BASE_DIR= os.environ.get('PROJECT_BASE_DIR', '/mnt/WORK/temp')


class DevelopmentConfig(BaseConfig):
    # MONGO_URI = 'mongodb://hainq:haideptrai123@ds263848.mlab.com:63848/diver-images'
    MONGO_URI = 'mongodb://localhost:27017/diver'


class ProductionConfig(BaseConfig):
    MONGO_URI = os.environ.get('IMAGE_DB', None)

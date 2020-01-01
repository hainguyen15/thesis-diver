import os

class BaseConfig(object):
    SLIDE_CACHE_SIZE = 10
    DEEPZOOM_FORMAT = 'jpeg'
    DEEPZOOM_TILE_SIZE = 254
    DEEPZOOM_OVERLAP = 1
    DEEPZOOM_LIMIT_BOUNDS = False
    DEEPZOOM_TILE_QUALITY = 75
    PROJECT_BASE_DIR= os.environ.get('PROJECT_BASE_DIR', '/mnt/WORK/Thesis/datasets/paip2019/')

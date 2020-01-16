from io import BytesIO
import json
from threading import Lock
from collections import OrderedDict
import datetime                       
from bson.objectid import ObjectId  

import openslide
from openslide import OpenSlide
from openslide.deepzoom import DeepZoomGenerator


class PILBytesIO(BytesIO):
    def fileno(self):
        raise AttributeError('Not supported')


class SlideCache(object):
    def __init__(self, cache_size, dz_opts):
        self.cache_size = cache_size
        self.dz_opts = dz_opts
        self._lock = Lock()
        self._cache = OrderedDict()

    def get(self, path):
        with self._lock:
            if path in self._cache:
                # Move to end of LRU
                slide_cache = self._cache.pop(path)
                self._cache[path] = slide_cache
                return slide_cache

        osr = OpenSlide(path)
        slide_dz = DeepZoomGenerator(osr, **self.dz_opts)
        try:
            mpp_x = osr.properties[openslide.PROPERTY_NAME_MPP_X]
            mpp_y = osr.properties[openslide.PROPERTY_NAME_MPP_Y]
            slide_dz.mpp = (float(mpp_x) + float(mpp_y)) / 2
        except (KeyError, ValueError):
            slide_dz.mpp = 0

        with self._lock:
            if path not in self._cache:
                if len(self._cache) == self.cache_size:
                    self._cache.popitem(last=False)
                self._cache[path] = slide_dz
        return slide_dz


class JSONEncoder(json.JSONEncoder):                           
    ''' extend json-encoder class'''
    def default(self, o):                               
        if isinstance(o, ObjectId):
            return str(o)                               
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)

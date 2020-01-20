import os
from io import BytesIO
import json
import zipfile
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


def process_zip(path, project_name, basedir):
    data = {
        'project_name': project_name,
        'images': []
    }
    if basedir is None or not os.path.exists(path):
        return False, None

    project_dir = os.path.join(basedir, project_name)
    save_dir = os.path.join(project_dir, 'wsi')
    thumbnails = os.path.join(project_dir, 'thumbnails')
    os.makedirs(save_dir)
    os.makedirs(thumbnails)
    
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(save_dir)

    for wsi in os.listdir(save_dir):
        slide = OpenSlide(os.path.join(save_dir, wsi))
        
        _save_thumbnails(slide, thumbnails, wsi)
        
        temp = {}
        temp['tiles'] = _extract_tiles(slide)
        temp['name'] = wsi
        temp['project_name'] = project_name
        temp['meta'] = {}
        temp['thumbnail'] = ''
        data['images'].append(temp)
                
        slide.close()
    return True, data


def _save_thumbnails(slide, thumb_dir, wsi_name):
    width, height = slide.dimensions
    thumb_size = (width // 256, height // 256)
    thumbnail = slide.get_thumbnail(thumb_size)
    thumbnail.save(os.path.join(thumb_dir, wsi_name.replace('.svs', '.png')))


def _extract_tiles(slide):
    dz = DeepZoomGenerator(slide)
    return {
        'levels': dz.level_count,
        'magnification': float(slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER]),
        'mm_x': float(slide.properties[openslide.PROPERTY_NAME_MPP_X]),
        'mm_y': float(slide.properties[openslide.PROPERTY_NAME_MPP_Y]),
        'sizeX': slide.level_dimensions[0][0],
        'sizeY': slide.level_dimensions[0][1],
        'tileHeight': 254,
        'tileWidth': 254,
        'image_type': 'H&E',
        'description': 'This is a description'
    }

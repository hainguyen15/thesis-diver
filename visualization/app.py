#!/home/hainq/anaconda3/envs/thesis/bin/python
import os
from io import BytesIO
from threading import Lock
from collections import OrderedDict
import re
from unicodedata import normalize

import openslide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator
from flask import (
    Flask, make_response, 
    render_template, url_for, jsonify
)
from flask_restful import abort
from werkzeug.utils import import_string


app = Flask(__name__)
cfg = import_string('config.BaseConfig')()
app.config.from_object(cfg)
app.config.from_envvar('DEEPZOOM_TILER_SETTINGS', silent=True)

class PILBytesIO(BytesIO):
    def fileno(self):
        raise AttributeError('Not supported')

class _SlideCache(object):
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


class _Directory(object):
    def __init__(self, basedir, relpath=''):
        self.name = os.path.basename(relpath)
        self.children = []
        for name in sorted(os.listdir(os.path.join(basedir, relpath))):
            if not os.path.isfile(name):
                continue
            cur_relpath = os.path.join(relpath, name)
            cur_path = os.path.join(basedir, cur_relpath)

            if OpenSlide.detect_format(cur_path):
                self.children.append(_SlideFile(cur_relpath))


class _SlideFile(object):
    def __init__(self, relpath):
        self.name = os.path.basename(relpath)
        self.url_path = relpath


@app.route('/')
def test():
    return  'Hello World'


@app.before_first_request
def setup():
    app.basedir = os.path.abspath(app.config['PROJECT_BASE_DIR'])
    config_map = {
        'DEEPZOOM_TILE_SIZE': 'tile_size',
        'DEEPZOOM_OVERLAP': 'overlap',
        'DEEPZOOM_LIMIT_BOUNDS': 'limit_bounds'
    }
    opts = dict((v, app.config[k]) for k, v in config_map.items())
    app.cache = _SlideCache(app.config['SLIDE_CACHE_SIZE'], opts)


@app.route('/<proj>')
def fetch_project(proj):
    proj_dir = os.path.join(app.basedir, proj)
    if not os.path.exists(proj_dir):
        abort(404, message='Project not found')
    imgs = os.listdir(proj_dir)
    if not imgs:
        abort(404, message='Data not found')
    children = []
    for name in sorted(imgs):
        cur_path = os.path.join(app.basedir, proj, name)
        if not os.path.isfile(cur_path) or not OpenSlide.detect_format(cur_path):
            continue
        children.append({
            'img_name': os.path.basename(cur_path),
            'url_path': url_for('slide', proj=proj, imname=name)
        })
    return make_response(jsonify(children), 200)


@app.route('/<proj>/<imname>')
def slide(proj, imname):
    path = os.path.join(proj, 'ws_images', imname)
    slide_obj = _get_slide(path)
    slide_url = url_for('dzi', path=path)
    return render_template('slide-fullpage.html', slide_url=slide_url,
            slide_filename=slide_obj.filename, slide_mpp=slide_obj.mpp)


@app.route('/<path:path>.dzi')
def dzi(path):
    _format = app.config['DEEPZOOM_FORMAT']
    slide_obj = _get_slide(path)
    resp = make_response(slide_obj.get_dzi(_format))
    resp.mimetype = 'application/xml'
    return resp

@app.route('/<path:path>_files/<int:level>/<int:col>_<int:row>.<imformat>')
def tile(path, level, col, row, imformat):
    slide_obj = _get_slide(path)
    imformat = imformat.lower()
    if imformat not in ['jpeg', 'png']:
        # Not supported by Deep Zoom
        abort(404)
    try:
        tile_obj = slide_obj.get_tile(level, (col, row))
    except ValueError:
        # Invalid level or coordinates
        abort(404)
    buf = PILBytesIO()
    tile_obj.save(buf, imformat, quality=app.config['DEEPZOOM_TILE_QUALITY'])
    resp = make_response(buf.getvalue())
    resp.mimetype = 'image/%s' % imformat
    return resp


def _get_slide(path):
    path = os.path.abspath(os.path.join(app.basedir, path))
    if not path.startswith(app.basedir + os.path.sep):
        # Directory traversal
        abort(404)
    if not os.path.exists(path):
        abort(404)
    try:
        slide_cache = app.cache.get(path)
        slide_cache.filename = os.path.basename(path)
        return slide_cache
    except OpenSlideError:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)

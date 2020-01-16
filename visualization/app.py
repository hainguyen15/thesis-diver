#!/home/hainq/anaconda3/envs/thesis/bin/python
import os
from io import BytesIO
from threading import Lock
from collections import OrderedDict

import openslide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator

from flask import ( 
    Flask, jsonify, url_for, 
    make_response, render_template
)
from flask_restful import abort
from flask_cors import CORS

from werkzeug.utils import import_string

app = Flask(__name__)
cfg = import_string('config.BaseConfig')()
app.config.from_object(cfg)
app.config.from_envvar('DEEPZOOM_TILER_SETTINGS', silent=True)
CORS(app=app)

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


@app.route('/')
def index(project_name='a'):
    return render_template('index.html', project_name=project_name)


@app.route('/<id>/tiles')
def slide_props(id):
    slide = OpenSlide(os.path.join(app.basedir, f'{id}.svs'))
    # slide = _get_slide(f'{id}.svs')
    dz = DeepZoomGenerator(slide)
    response = {
        'levels': dz.level_count,
        'magnification': slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER],
        'mm_x': slide.properties[openslide.PROPERTY_NAME_MPP_X],
        'mm_y': slide.properties[openslide.PROPERTY_NAME_MPP_Y],
        'sizeX': slide.level_dimensions[0][0],
        'sizeY': slide.level_dimensions[0][1],
        'tileHeight': app.config['DEEPZOOM_TILE_SIZE'],
        'tileWidth': app.config['DEEPZOOM_TILE_SIZE']
    }
    slide.close()
    return jsonify(response)


@app.route('/proj/<id>')
def slide_geometry(id):
    import json
    with open('template.json') as template:
        data = json.load(template)
    return jsonify(data)


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
    if not os.path.exists(path):
        abort(404)
    try:
        slide_cache = app.cache.get(path)
        slide_cache.filename = os.path.basename(path)
        return slide_cache
    except OpenSlideError:
        abort(404)


if __name__ == "__main__":
    app.run(debug=True)

#!/home/hainq/anaconda3/envs/thesis/bin/python
import os
import json
import openslide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator

from flask import ( 
    Flask, jsonify, 
    make_response, render_template,
    request
)
from flask_restful import abort
from flask_cors import CORS
from flask_pymongo import PyMongo

from werkzeug.utils import import_string
from utils import SlideCache, PILBytesIO, JSONEncoder

app = Flask(__name__)

if os.environ.get('FLASK_ENV', 'development') == 'production':
    cfg = import_string('config.ProductionConfig')()
else:
    cfg = import_string('config.DevelopmentConfig')()

app.config.from_object(cfg)
app.config.from_envvar('DEEPZOOM_TILER_SETTINGS', silent=True)
app.json_encoder = JSONEncoder

mongo = PyMongo(app)
CORS(app=app)


@app.before_first_request
def setup():
    app.basedir = os.path.abspath(app.config['PROJECT_BASE_DIR'])
    app.base_url = os.environ.get('BASE_URL', 'http://localhost:5000/')
    config_map = {
        'DEEPZOOM_TILE_SIZE': 'tile_size',
        'DEEPZOOM_OVERLAP': 'overlap',
        'DEEPZOOM_LIMIT_BOUNDS': 'limit_bounds'
    }
    opts = dict((v, app.config[k]) for k, v in config_map.items())
    app.cache = SlideCache(app.config['SLIDE_CACHE_SIZE'], opts)


@app.route('/<project_name>')
def index(project_name='default'):
    return render_template('index.html', project_name=project_name, base_url=app.base_url)


@app.route('/<project_name>/<fileid>/tiles')
def slide_props(project_name, fileid):
    slide = OpenSlide(os.path.join(app.basedir, project_name, 'wsi', f'{fileid}.svs'))
    dz = DeepZoomGenerator(slide)
    response = {
        'levels': dz.level_count,
        'name': fileid,
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


@app.route('/<project_name>/<fileid>/anno')
def slide_geometry(project_name, fileid):
    geojson = os.path.join(app.basedir, project_name, 'geojson', f'{fileid}.json')
    with open(geojson) as res:
        data = json.load(res)
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


@app.route('/<project_name>/images', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def proj_images(project_name):
    if request.method == 'GET':
        data = mongo.db.images.find({ 'project_name': project_name })
        return jsonify(data), 200

    data = request.get_json()
    # POST multiple images at the same time
    if request.method == 'POST':
        if data.get('project_name', None) is None or data.get('images', None) is None:
            abort(403, message='Requested data is invalid.')

        imgs = data['images']
        if not imgs:
            abort(403, message='Image list is empty!')
        
        mongo.db.images.insert_many(imgs)
        return jsonify({
            'status': True,
            'msg': 'Images added successfully'
        })
    else:
        raise NotImplementedError

if __name__ == "__main__":
    app.run(debug=True)

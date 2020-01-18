#!/home/hainq/anaconda3/envs/thesis/bin/python
import os
from bson.objectid import ObjectId  

from flask import ( 
    Flask, jsonify, 
    make_response, render_template,
    request, url_for
)
from flask_restful import abort
from flask_cors import CORS
from flask_pymongo import PyMongo

from werkzeug.utils import import_string
from openslide import OpenSlideError
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

@app.route('/')
@app.route('/<project_name>')
def index(project_name='default'):
    return render_template('index.html', project_name=project_name, base_url=app.base_url)


@app.route('/<project_name>/<_id>/tiles')
def slide_props(project_name, _id):
    data = mongo.db.images.find_one({ '_id': ObjectId(_id), "project_name": project_name }, { "tiles": 1, "name": 1 })
    if data is None:
        abort(404)
    return jsonify(data), 200


@app.route('/<project_name>/<_id>/anno', methods=['GET', 'POST'])
def slide_geometry(project_name, _id):
    if request.method == 'POST':
        data = request.get_json()
        if data.get('meta', None) is None:
            abort(403, message='Invalid meta')

        if data.get('geojslayer', None):
            abort(403, message='No geojslayer in meta')
        
        mongo.db.images.update_one({ "_id": ObjectId(_id) }, { "$set": { "meta": data['meta'] } })
        return url_for('slide_geometry', project_name=project_name, _id=_id)
    # GET method
    else:
        data = mongo.db.images.find_one(
            { '_id': ObjectId(_id), "project_name": project_name }, 
            { "meta": 1, 'name': 1 }
        )
        if data is None:
            abort(404)
        return jsonify(data), 200
        # import json
        # with open('template.json') as res:
        #     data = json.load(res)
        # return jsonify(data)


@app.route('/<project_name>/images', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def proj_images(project_name):
    if request.method == 'GET':
        data = mongo.db.images.find({ "project_name": project_name }, { 'meta': 0 })
        return jsonify(list(data)), 200

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


@app.route('/<project_name>/<path:path>_files/<int:level>/<int:col>_<int:row>.jpeg')
def tile(project_name, path, level, col, row):
    slide_obj = _get_slide(project_name, path)
    try:
        tile_obj = slide_obj.get_tile(level, (col, row))
    except ValueError:
        abort(404, message='Invalid level or coordinates')

    buf = PILBytesIO()
    tile_obj.save(buf, 'jpeg', quality=app.config['DEEPZOOM_TILE_QUALITY'])
    resp = make_response(buf.getvalue())
    resp.mimetype = 'image/%s' % 'jpeg'
    return resp


def _get_slide(project_name, path):
    path = os.path.abspath(os.path.join(app.basedir, project_name, 'wsi', path))
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

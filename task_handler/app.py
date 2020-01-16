import os
import tempfile
import random
import time

from skimage import io

from flask import (
    Flask, request,
    url_for, jsonify
)
# from flask_restful import abort
from flask_mail import Mail

from celery import Celery
from celery.result import AsyncResult
# import werkzeug
from werkzeug.utils import import_string
from werkzeug.datastructures import Headers

from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget

# from flask_celery import make_celery
from ai_modules.prediction import load_model, predict_wsi
from utils import process_zip, extract_info


app = Flask(__name__)
cfg = import_string('config.DevelopmentConfig')()
app.config.from_object(cfg)
# app.config['SECRET_KEY'] = 'mtf83pg$z/L"@sRqKQ[zk6SNQe"}@,3ZD@u{t18Ka?Phig>+K}y[}@Mwkn(^4/e'
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

mail = Mail(app)

# celery = make_celery(app)
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

model, global_fixed = None, None


@app.before_first_request
def init_model():
    model, global_fixed = load_model('./resource/wsi.pth')


# Celery tasks
@celery.task(bind=True)
def quick_predict(self, project_name):
    proj_base_dir = os.environ.get('PROJECT_BASE_DIR', '/mnt/WORK/temp/')
    img_dir = os.path.join(proj_base_dir, project_name, 'ws_images')
    out_scaled = os.path.join(img_dir, project_name, 'out_scaled')
    out_full = os.path.join(img_dir, project_name, 'out_full')

    imgs = [os.path.join(img_dir, f) for f in os.listdir(img_dir) if os.path.isfile(f)]
    total = len(imgs)
    for i, img in enumerate(imgs):
        out_scaled, large = predict_wsi(model, global_fixed, img)
        out_scaled.save(os.path.join(out_scaled, os.path.basename(img).replace('svs', 'png')))

        io.imsave(os.path.basename(img).replace('svs', 'tif'), large)
        self.update_state(state='PROGRESS',
                          meta={'progress': (i + 1) / total})

        # TODO: make simple request to update image info like 
        # tumor occupancy and tumor area. Of course it works in separate thread

    return jsonify({

    }), 200

@celery.task(bind=True)
def upload(self, project_name, headers):
    # def custom_stream_factory(total_content_length, filename, content_type, content_length=None):
    #     tmpfile = tempfile.NamedTemporaryFile('wb+', prefix='flaskapp')
    #     # app.logger.info("start receiving file ... filename => " + str(tmpfile.name))
    #     return tmpfile
    
    # _, _, files = werkzeug.formparser.parse_form_data(request.environ, stream_factory=custom_stream_factory)
    self.update_state(state='PROGRESS',
                      meta={'message': 'Uploading...'})
    temp = Headers()
    for k, v in headers:
        temp.add(k, v)
    with app.test_request_context():
        file_ = FileTarget(os.path.join(tempfile.gettempdir(), 'temp.zip'))
        parser = StreamingFormDataParser(headers=temp)
        parser.register('file', file_)

    self.update_state(state='PENDING',
                      meta={'message': 'Post processing...'})

    if not process_zip('/tmp/temp.zip', project_name):
        self.update_state(state='ERROR', meta={'message': 'Unexpected Error'})
        raise FileNotFoundError
    return {
        'status': True,
        'message': 'Upload successfully',
    }

@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

# routing
@app.route('/', methods=['GET'])
def test():
    return jsonify({'message': 'Hello World'})

# @app.route('/predict', methods=['GET'])
# def predict():
#     pass


@app.route('/upload/', defaults={'project_name': 'project'}, methods = ['POST'])
def upload_file(project_name):
    task = upload.apply_async(args=[project_name, request.headers.to_list()])
    response = {
        'task_id': task.id,
        'status_url': url_for('taskstatus', task_id=task.id)
    }
    return jsonify(response), 202


@app.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({
        'task_status': url_for('taskstatus', task_id=task.id)
    }), 202


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = AsyncResult(task_id, app=celery)
    if task.state == 'FAILURE':
        response = {
            'state': task.state,
            'message': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'message': task.info.get('message', None)
        }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port='5001')

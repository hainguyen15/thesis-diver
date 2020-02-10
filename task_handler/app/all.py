from flask import Blueprint, url_for, jsonify, request
from flask_restful import abort
from celery.result import AsyncResult
from app import celery
from .tasks import long_task, quick_predict
from .utils.processing import process_zip
from .utils.wsi import get_boundary

bp = Blueprint("all", __name__)


@bp.route('/')
def index():
    return jsonify({'message': 'Hello World'})


@bp.route('/status/<task_id>')
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
            'progress': task.info.get('progress', None),
            'message': task.info.get('message', None)
        }
    return jsonify(response)


@bp.route('/analyze', methods=['POST'])
def analyze_project():
    # task = quick_predict.apply_async(args=[project_name])
    data = request.get_json()
    project_name = data.get('project_name', None)
    if project_name is None:
        abort(400, message="Project name is invalid")
        
    # task = celery.tasks['diver_quick_predict']
    # task.run(project_name)
    task = quick_predict.apply_async(args=[project_name])
    return jsonify({
        'task_status': url_for('all.taskstatus', task_id=task.id)
    }), 202


@bp.route('/longtask', methods=['GET'])
def longtask():
    task = long_task.apply_async()
    return jsonify({
        'task_status': url_for('all.taskstatus', task_id=task.id)
    }), 202

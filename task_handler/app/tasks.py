import os
import time
import random
import requests as r
from PIL import Image
from app import celery
from .ai_modules.prediction import predict_wsi, load_model
from .utils.wsi import get_boundary


model, global_fixed = load_model(os.environ.get('MODEL_PATH', './resource/wsi.pth'))

@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = 20
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


@celery.task(bind=True)
def quick_predict(self, project_name):
    proj_base_dir = os.environ.get('PROJECT_BASE_DIR', '/mnt/WORK/temp/')
    img_dir = os.path.join(proj_base_dir, project_name, 'wsi')
    imgs = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
    total = len(imgs)
    self.update_state(state='PROGRESS',
                    meta={'message': 'Prediction started'})
    for i, img in enumerate(imgs):
        out = predict_wsi(model, global_fixed, img)
        up_res = _update_prediction(project_name, os.path.basename(img), out)
        if not up_res:
            raise Exception(f'Failed to update image {os.path.basename(img)}')
        self.update_state(state='PROGRESS',
                    meta={'message': '{0:.2f}%'.format(((i + 1) / total) * 100)})

    return {
        'status': True,
        'message': f'Project \"{project_name}\" ({total} images) processed successfully'
    }


def _update_prediction(project_name, img, out):
    vis_host = os.environ.get('VIS_HOST', None)
    if not vis_host:
        raise ModuleNotFoundError
    boundary = get_boundary(out)
    features = []
    for i, b in enumerate(boundary):
        feat = {
            "crs": {
                "properties": {
                    "name": "+proj=longlat +axis=esu",
                    "type": "proj4"
                },
                "type": "name"
            },
            "geometry": {
                "coordinates": b,
                "type": "LineString"
            },
            "properties": {
                "annotationId": i + 1,
                "annotationType": "rectangle",
                "fill": True,
                "fillColor": "#00ff00",
                "fillOpacity": 0.25,
                "name": f'Prediction {i + 1}',
                "stroke": True,
                "strokeColor": "#000000",
                "strokeOpacity": 1,
                "strokeWidth": 2
            },
            "type": "Feature"
        }
        features.append(feat)

    data = {
        'meta': {
            'geojslayer': {
                "features": features,
                "type": "FeatureCollection"
            },
            "tags": {}
        }
    }
    resp = r.post(url=f'http://{vis_host}/{project_name}/{img}/anno', json=data)
    return resp.status_code == 200

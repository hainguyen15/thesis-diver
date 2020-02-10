import os
import requests as r
# from threading import 
from PIL import Image
from celery import Task
from .ai_modules.prediction import predict_wsi, load_model
from .utils.wsi import get_boundary

class DiverTask(Task):
    def __init__(self):
        super().__init__()
        self.name = 'diver_quick_predict'
        self.model = None
        self.global_fixed = None
        model, global_fixed = load_model(os.environ.get('MODEL_PATH', './resource/wsi.pth'))
        self.model = model
        self.global_fixed = global_fixed

    # def init_model(self):
    def apply_async(self, args=None):
        if not args:
            return False

        project_name = args[0]
        proj_base_dir = os.environ.get('PROJECT_BASE_DIR', '/mnt/WORK/temp/')
        img_dir = os.path.join(proj_base_dir, project_name, 'wsi')
        imgs = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
        total = len(imgs)
        for i, img in enumerate(imgs):
            out = predict_wsi(self.model, self.global_fixed, img)
            
            imgout = Image.fromarray(out * 255)
            imgout.save(os.path.join(proj_base_dir, img.replace('.svs', '.png')))
            self.update_state(state='PROGRESS',
                        meta={'message': '{0:.2f}'.format(((i + 1) / total) * 100)})

        return {
            'status': True,
            'message': f'Project {project_name} ({total} images) processed successfully'
        }

    def run(self, project_name, *args, **kwargs):
        # if self.model is None or self.global_fixed is None:
        #     self.init_model()

        proj_base_dir = os.environ.get('PROJECT_BASE_DIR', '/mnt/WORK/temp/')
        img_dir = os.path.join(proj_base_dir, project_name, 'wsi')
        imgs = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
        total = len(imgs)
        for i, img in enumerate(imgs):
            out = predict_wsi(self.model, self.global_fixed, img)
            
            imgout = Image.fromarray(out * 255)
            imgout.save(os.path.join(proj_base_dir, img.replace('.svs', '.png')))
            self.update_state(state='PROGRESS',
                        meta={'message': '{0:.2f}'.format(((i + 1) / total) * 100)})

        return {
            'status': True,
            'message': f'Project {project_name} ({total} images) processed successfully'
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
    resp = r.post(url=f'{vis_host}/{project_name}/{img}/inno', json=data)
    return resp.status_code == 200

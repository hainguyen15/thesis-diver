import os
import zipfile
import openslide
from openslide import OpenSlide
from openslide.deepzoom import DeepZoomGenerator


def process_zip(path, project_name):
    proj_base_dir = os.environ.get('PROJECT_BASE_DIR', '/mnt/WORK/temp/')
    data = {
        'project_name': project_name,
        'images': []
    }
    if proj_base_dir is None or not os.path.exists(path):
        return False, None

    project_dir = os.path.join(proj_base_dir, project_name)
    save_dir = os.path.join(project_dir, 'wsi')
    thumbnails = os.path.join(project_dir, 'thumbnails')
    os.makedirs(save_dir)
    os.makedirs(thumbnails)
    
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(save_dir)

    for wsi in os.listdir(save_dir):
        slide = OpenSlide(os.path.join(save_dir, wsi))
        
        fname = _save_thumbnails(slide, thumbnails, wsi)
        
        temp = {}
        temp['tiles'] = _extract_tiles(slide)
        temp['name'] = wsi
        temp['project_name'] = project_name
        temp['meta'] = {}
        temp['thumbnail'] = fname
        data['images'].append(temp)

        slide.close()
    return True, data


def _save_thumbnails(slide, thumb_dir, wsi_name):
    width, height = slide.dimensions
    thumb_size = (width // 256, height // 256)
    thumbnail = slide.get_thumbnail(thumb_size)
    fname = wsi_name.replace('.svs', '.png')
    thumbnail.save(os.path.join(thumb_dir, fname))
    return fname


def _extract_tiles(slide):
    dz = DeepZoomGenerator(slide)
    return {
        'levels': dz.level_count,
        'magnification': slide.properties[openslide.PROPERTY_NAME_OBJECTIVE_POWER],
        'mm_x': slide.properties[openslide.PROPERTY_NAME_MPP_X],
        'mm_y': slide.properties[openslide.PROPERTY_NAME_MPP_Y],
        'sizeX': slide.level_dimensions[0][0],
        'sizeY': slide.level_dimensions[0][1],
        'tileHeight': 254,
        'tileWidth': 254,
        'image_type': 'H&E',
        'description': 'This is a description'
    }

import os
import zipfile

from openslide import OpenSlide

def process_zip(path, project_name):
    proj_base_dir = os.environ.get('PROJECT_BASE_DIR', '/mnt/WORK/temp/')
    if proj_base_dir is None or not os.path.exists(path):
        return False
    project_dir = os.path.join(proj_base_dir, project_name)
    save_dir = os.path.join(project_dir, 'ws_images')
    thumbnails = os.path.join(project_dir, 'thumbnails')
    # scaled_wsi = os.path.join((project_dir, 'scaled_wsi'))
    os.makedirs(save_dir)
    os.makedirs(thumbnails)
    os.makedirs(os.path.join(project_dir, 'out_scaled'))
    os.makedirs(os.path.join(project_dir, 'out_full'))
    # os.makedirs(scaled_wsi)
    
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(save_dir)

    for wsi in os.listdir(save_dir):
        slide = OpenSlide(os.path.join(save_dir, wsi))
        width, height = slide.level_dimensions[-1]
        thumb_size = (width // 4, height // 4)
        thumbnail = slide.get_thumbnail(thumb_size)
        thumbnail.save(os.path.join(thumbnails, wsi.replace('.svs', '.png')))
        
        # scaled_wsi = slide.read_region((0,0), slide.level_count[-1], slide.level_dimensions[-1])
        # scaled_wsi.save(scaled_wsi)
    
        slide.close()
    return True


def extract_info(slide, full_tumor_mask):
    percentage, area = 0, 0

    return percentage, area


def save_prediction():
    pass

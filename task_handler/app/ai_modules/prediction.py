import numpy as np
from openslide import OpenSlide, ImageSlide, deepzoom

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

from .GLNet.models import GLNet
from .GLNet.models.functional import crop_global
from .GLNet.utils.enums import PhaseMode
from .GLNet.utils.filters import apply_filters
from .GLNet.utils.processing import (
    images_transform,
    resize,
    global2patch,
    patch2global,
    add_extra_pixels,
    remove_mask_overlay_background
)
# from .GLNet.utils.visualization import apply_mask


def load_model(model_path):
    model = GLNet(2)
    model = nn.DataParallel(model)
    model.cuda()
    partial = torch.load(model_path)
    state = model.state_dict()
    pretrained_dict = {
        k: v for k, v in partial.items() if k in state
    }
    state.update(pretrained_dict)
    model.load_state_dict(state)
    model.eval()

    global_fixed = GLNet(2)
    global_fixed = nn.DataParallel(global_fixed)
    global_fixed.cuda()
    state = global_fixed.state_dict()
    pretrained_dict = {
        k: v for k, v in partial.items() if k in state and 'local' not in k
    }
    state.update(pretrained_dict)
    global_fixed.load_state_dict(state)
    global_fixed.eval()

    return model, global_fixed


def predict_wsi(model, global_fixed, slide_path):
    # size_g, size_p = (244, 244), (244, 244)
    # size_g, size_p = (1008, 1008), (1008, 1008)
    # n_class = 2
    # sub_batch_size = 1
    def predict(image_as_tensor, size_g=(244, 244), size_p=(244, 244), n_class=2):
        images_glb = resize(image_as_tensor, size_g)
        scores = [
            np.zeros((1, n_class, image_as_tensor[i].size[1], image_as_tensor[i].size[0]))
            for i in range(len(image_as_tensor))
        ]
        
        images_glb = images_transform(images_glb)
        
        patches, coordinates, templates, sizes, ratios = global2patch(
            image_as_tensor, size_p
        )

        predicted_ensembles = [
            np.zeros((len(coordinates[i]),n_class,size_p[0],size_p[1]))
            for i in range(len(image_as_tensor))
        ]
        
        for i in range(len(image_as_tensor)):
            j = 0
            while j < len(coordinates[i]):
                patches_var = images_transform(
                    patches[i][j : j + 1]
                )  # b, c, h, w

                fm_patches, _ = model.module.collect_local_fm(
                    images_glb[i : i + 1],
                    patches_var,
                    ratios[i],
                    coordinates[i],
                    [j, j + 1],
                    len(image_as_tensor),
                    global_model=global_fixed,
                    template=templates[i],
                    n_patch_all=len(coordinates[i]),
                )
                j += 1
        
        _, fm_global = model.forward(
            images_glb, None, None, None, mode=PhaseMode.GlobalFromLocal
        )
        
        for i in range(len(image_as_tensor)):
            j = 0
            # while j < n ** 2:
            while j < len(coordinates[i]):
                fl = fm_patches[i][j : j + 1].cuda()
                fg = crop_global(
                    fm_global[i : i + 1],
                    coordinates[i][j : j + 1],
                    ratios[i])[0]

                fg = F.interpolate(
                    fg, size=fl.size()[2:], mode="bilinear"
                )
                output_ensembles = model.module.ensemble(
                    fl, fg
                )  # include cordinates
                # output_ensembles = F.interpolate(model.module.ensemble(fl, fg), size_p, **model.module._up_kwargs)

                # ensemble predictions
                predicted_ensembles[i][j : j + output_ensembles.size()[0]] += (
                    F.interpolate(
                        output_ensembles,
                        size=size_p,
                        mode="nearest",
                    )
                    .data.cpu()
                    .numpy()
                )
                j += 1
            
            scores[i] += np.rot90(
                np.array(
                    patch2global(
                        predicted_ensembles[i : i + 1],
                        n_class,
                        sizes[i : i + 1],
                        coordinates[i : i + 1],
                        size_p,
                    )
                ),
                k=0,
                axes=(3, 2),
            )

        return [score.argmax(1)[0] for score in scores]

    slide = OpenSlide(slide_path)
    w, h = slide.level_dimensions[2]
    img = slide.read_region((0, 0), 2, (w, h))
    slide.close()
    img.convert('RGB').save('/tmp/temp.jpg')
    slide = ImageSlide('/tmp/temp.jpg')

    dz = deepzoom.DeepZoomGenerator(slide, tile_size=1024, overlap=0)

    cols, rows = dz.level_tiles[-1]
    out = np.zeros((rows * 1024, cols * 1024), dtype=np.uint8)

    for row in range(rows):
        for col in range(cols):
            tile = dz.get_tile(dz.level_count - 1, (col, row)) # col, row
            tile_coors = dz.get_tile_coordinates(dz.level_count - 1, (col, row))
            left, top = tile_coors[0]
            t_w, t_h = tile_coors[2]
            if tile.size != (1024, 1024):
                tile = add_extra_pixels(tile, expected_shape=(1024, 1024))
                
            tile = np.array(tile)
            processed = apply_filters(tile)

            pred = predict([Image.fromarray(processed)])
            pil_pred = pred[0].astype(np.uint8)
            
            newmask = remove_mask_overlay_background(processed, pil_pred)

            # applied_mask = apply_mask(tile, newmask)
            applied_mask = newmask
            out[top:top+t_h, left:left+t_w] = applied_mask[:t_h, :t_w]
    
    return out[:h, :w]

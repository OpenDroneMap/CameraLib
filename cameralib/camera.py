import json
import numpy as np
from cameralib.utils import rodrigues_vec_to_rotation_mat

def load_shots(shots_path):
    """Load camera shots"""
    with open(shots_path) as f:
        shots = json.loads(f.read())
    
    if not "features" in shots:
        raise IOError("Invalid shots.geojson file.")

    result = []
    for feat in shots["features"]:
        props = feat.get("properties")
        if props is None:
            continue

        focal = props.get('focal', props.get('focal_x'))
        if focal is None:
            continue

        cam_id = props.get('camera')
        filename = props.get('filename')
        translation = np.array(props['translation'])
        rotation = rodrigues_vec_to_rotation_mat(np.array(props['rotation']))
        width = props.get('width')
        height = props.get('height')
        if not width or not height:
            continue

        result.append({
            'cam_id': cam_id,
            'filename': filename,
            'focal': focal,
            'translation': translation,
            'rotation': rotation,
            'width': width,
            'height': height
        })
    
    return result

def load_cameras(cameras_file):
    with open(cameras_file) as f:
        return json.load(f)

def load_camera_mappings(mappings_file):
    with np.load(mappings_file, allow_pickle=False) as data:
        if not 'ids' in data:
            raise IOError("Invalid camera mappings file (ids missing)")
        
        result = {}
        idx = 0
        for cam_id in data['ids']:
            result[cam_id] = {
                'x': data['%s_x' % idx],
                'y': data['%s_y' % idx],
                'offset': data['%s_offset' % idx],
                'mul': data['%s_mul' % idx][0]
            }
            idx += 1

        return result
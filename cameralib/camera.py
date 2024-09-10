import json
import numpy as np
from cameralib.utils import rodrigues_vec_to_rotation_mat
from cameralib.exceptions import *
import cv2

def map_pixels(from_camera, to_camera, pixels):
    return to_camera.project_many(from_camera.pixel_bearing_many(pixels))


class Camera(object):
    def undistorted(self):
        return PerspectiveCamera(self.width, self.height, self.focal)

    def normalized_image_coordinates(self, pixel_coords):
        normalizer = max(self.width, self.height)
        p = np.empty((len(pixel_coords), 2))
        p[:, 0] = (pixel_coords[:, 0] + 0.5 - self.width / 2.0) / normalizer
        p[:, 1] = (pixel_coords[:, 1] + 0.5 - self.height / 2.0) / normalizer
        return p

    def denormalized_image_coordinates(self, norm_coords):
        unnormalizer = max(self.width, self.height)
        p = np.empty((len(norm_coords), 2))
        p[:, 0] = norm_coords[:, 0] * unnormalizer - 0.5 + self.width / 2.0
        p[:, 1] = norm_coords[:, 1] * unnormalizer - 0.5 + self.height / 2.0
        return p

    def get_K(self):
        return np.array([[self.focal, 0., self.cx],
                         [0., self.focal, self.cy],
                         [0., 0., 1.]])

    def pixel_bearing_many(self, pixels):
        uvs = self.normalized_image_coordinates(pixels)
        points = uvs.reshape((-1, 1, 2)).astype(np.float64)
        up = cv2.undistortPoints(points, self.get_K(), self.distortion)
        up = up.reshape((-1, 2))
        x = up[:, 0]
        y = up[:, 1]
        l = np.sqrt(x * x + y * y + 1.0)
        return np.column_stack((x / l, y / l, 1.0 / l))

    def project_many(self, points):
        K, R, t = self.get_K(), np.zeros(3), np.zeros(3)
        pixels, _ = cv2.projectPoints(points, R, t, K, self.distortion)
        return self.denormalized_image_coordinates(pixels.reshape((-1, 2)))


class PerspectiveCamera(Camera):
    def __init__(self, width, height, focal, k1=0.0, k2=0.0):
        self.width = width
        self.height = height
        self.focal = focal
        self.cx = 0
        self.cy = 0
        self.k1 = k1
        self.k2 = k2
        self.distortion = np.array([k1, k2, 0.0, 0.0, 0.0])


class BrownCamera(Camera):
    def __init__(self, width, height, focal, cx=0.0, cy=0.0, k1=0.0, k2=0.0, p1=0.0, p2=0.0, k3=0.0):
        self.width = width
        self.height = height
        self.focal = focal
        self.cx = cx
        self.cy = cy
        self.k1 = k1
        self.k2 = k2
        self.p1 = p1
        self.p2 = p2
        self.k3 = k3
        self.distortion = np.array([self.k1, self.k2, self.p1, self.p2, self.k3])


def load_shots(shots_path):
    """Load camera shots"""
    with open(shots_path) as f:
        shots = json.loads(f.read())
    
    if not "features" in shots:
        raise IOError("Invalid shots.geojson file.")

    result = []
    idx = 0
    shots_map = {}
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
        shots_map[filename] = idx
        idx += 1
    
    return result, shots_map

def load_cameras(cameras_file):
    with open(cameras_file) as f:
        cameras = json.load(f)

    result = {}
    for cam_id in cameras:
        camera = cameras[cam_id]

        if camera['projection_type'] == 'perspective':
            cam = PerspectiveCamera(camera['width'], camera['height'], camera.get('focal', camera.get('focal_x')),
                                    camera['k1'], camera['k2'])
        elif camera['projection_type'] == 'brown':
            cam = BrownCamera(camera['width'], camera['height'], camera.get('focal', camera.get('focal_x')), 
                                camera.get('c_x', 0), camera.get('c_y', 0),
                                camera['k1'], camera['k2'], camera['p1'], camera['p2'], camera['k3'])
        else:
            print(f"Warning: {camera['projection_type']} camera type is not supported")
            continue

        result[cam_id] = cam
    return result

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


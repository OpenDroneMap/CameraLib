import os
import json
import numpy as np
import rasterio
from cameralib.geo import get_utm_xyz 
from cameralib.camera import load_shots, load_cameras, map_pixels
from cameralib.exceptions import *

class Projector:
    def __init__(self, project_path, z_sample_window=1, z_sample_strategy='median', z_sample_target='dsm'):
        if not os.path.isdir(project_path):
            raise IOError(f"{project_path} is not a valid path to an ODM project")
        
        self.project_path = project_path
        self.z_sample_window = z_sample_window
        self.z_sample_strategy = z_sample_strategy

        self.dsm_path = os.path.abspath(os.path.join(project_path, "odm_dem", "dsm.tif"))
        self.dtm_path = os.path.abspath(os.path.join(project_path, "odm_dem", "dtm.tif"))
        if z_sample_target == 'dsm':
            self.dem_path = self.dsm_path
        elif z_sample_target == 'dtm':
            self.dem_path = self.dtm_path
        else:
            raise InvalidArgError(f"Invalid z_sample_target {z_sample_target}")

        self.shots_path = os.path.abspath(os.path.join(project_path, "odm_report", "shots.geojson"))
        self.cameras_path = os.path.abspath(os.path.join(project_path, "cameras.json"))

        self.shots, self.shots_map = load_shots(self.shots_path)
        self.cameras = load_cameras(self.cameras_path)


    def cam2world(self, image, coordinates):
        """Project 2D pixel coordinates in camera space to geographic coordinates
        
        Args:
            image (str): image filename
            coordinates (list of tuples): x,y pixel coordinates

        Returns:
            list of tuples: longitude,latitude,elevation for each coordinate pair
        """
        if not image in self.shots_map:
            raise InvalidArgError(f"Image {image} not found in {self.shots_path}")

        s = self.shots[self.shots_map[image]]
        cam_id = s['cam_id'].replace("v2 ", "")
        cam = self.cameras[cam_id]

        undistorted_uv = map_pixels(cam, cam.undistorted(), np.array(coordinates, dtype=np.float64))
        
        with rasterio.open(self.dem_path, 'r') as raster:
            min_z = 100 # TODO

            r = s['rotation']
            a1 = r[0][0]
            b1 = r[0][1]
            c1 = r[0][2]
            a2 = r[1][0]
            b2 = r[1][1]
            c2 = r[1][2]
            a3 = r[2][0]
            b3 = r[2][1]
            c3 = r[2][2]

            focal = s['focal']
            img_w = s['width']
            img_h = s['height']
            f = focal * max(img_h, img_w)
            Xs, Ys, Zs = s['translation']
            cam_grid_y, cam_grid_x = raster.index(Xs, Ys)

            print(cam_grid_x, cam_grid_y)

            # Get the grid coordinates of the ray projected from the camera via (u,v)
            # The Xa,Ya equations are just derived from the colinearity equations
            # solving for Xa and Ya instead of x,y
            Za = min_z
            u,v = undistorted_uv[0][0] - img_w / 2.0, undistorted_uv[0][1] - img_h / 2.0
            m = (a3*b1*v - a1*b3*v - (a3*b2 - a2*b3)*u - (a2*b1 - a1*b2)*f)
            Xa = (m*Xs + (b3*c1*v - b1*c3*v - (b3*c2 - b2*c3)*u - (b2*c1 - b1*c2)*f)*Za - (b3*c1*v - b1*c3*v - (b3*c2 - b2*c3)*u - (b2*c1 - b1*c2)*f)*Zs)/m
            Ya = (m*Ys - (a3*c1*v - a1*c3*v - (a3*c2 - a2*c3)*u - (a2*c1 - a1*c2)*f)*Za + (a3*c1*v - a1*c3*v - (a3*c2 - a2*c3)*u - (a2*c1 - a1*c2)*f)*Zs)/m

            y, x = raster.index(Xa, Ya)
            print(x, y)
            exit(1)

    # p.cam2world("image.JPG", [(x, y), ...]) --> ((x, y, z), ...) (geographic coordinates)

    def cam2geoJSON(self, image, coordinates):
        pass
    
    # geojson = p.cam2geoJSON("image.JPG", [(x, y), ...]) --> GeoJSON

    def world2cams(self, longitude, latitude, normalized=False):
        """Find which cameras in the reconstruction see a particular location.

        Args:
            longitude (float): Longitude
            latitude (float): Latitude
            normalized (bool): Whether to normalize pixel coordinates by the image dimension. By default pixel coordinates are in range [0..image width], [0..image height])

        Returns:
            list of dict: A list of dictionaries where each dictionary represents a camera with the following information:
            [
                {
                    'filename': str     # The filename of the image associated with the camera
                    'x': float          # The x-coordinate in camera space
                    'y': float          # The y-coordinate in camera space 
                },
                ...
            ]
        """
        Xa, Ya, Za = get_utm_xyz(self.dem_path, longitude, latitude, 
                                    z_sample_window=self.z_sample_window,
                                    z_sample_strategy=self.z_sample_strategy)
        images = []
        for s in self.shots:
            r = s['rotation']
            a1 = r[0][0]
            b1 = r[0][1]
            c1 = r[0][2]
            a2 = r[1][0]
            b2 = r[1][1]
            c2 = r[1][2]
            a3 = r[2][0]
            b3 = r[2][1]
            c3 = r[2][2]

            cam_id = s['cam_id'].replace("v2 ", "")
            focal = s['focal']
            img_w = s['width']
            img_h = s['height']
            Xs, Ys, Zs = s['translation']

            half_img_w = (img_w - 1) / 2.0
            half_img_h = (img_h - 1) / 2.0
            f = focal * max(img_w, img_h)

            dx = (Xa - Xs)
            dy = (Ya - Ys)
            dz = (Za - Zs)

            den = a3 * dx + b3 * dy + c3 * dz
            x = half_img_w - (f * (a1 * dx + b1 * dy + c1 * dz) / den)
            y = half_img_h - (f * (a2 * dx + b2 * dy + c2 * dz) / den)

            if x >= 0 and y >= 0 and x <= img_w - 1 and y <= img_h - 1:
                valid = True # assumed
                result = {
                    'filename': s['filename']
                }
                if cam_id is not None and cam_id in self.cameras:
                    cam = self.cameras[cam_id]

                    # Back-undistort to find exact UV coordinates

                    xi = img_w - 1 - int(round(x))
                    yi = img_h - 1 - int(round(y))
                    xu, yu = map_pixels(cam.undistorted(), cam, np.array([[xi, yi]])).ravel()

                    valid = xu >= 0 and xu <= img_w and yu >= 0 and yu <= img_h

                    result['x'] = float(xu)
                    result['y'] = float(yu)
                    if normalized:
                        result['x'] /= img_w
                        result['y'] /= img_h
                
                if valid:
                    images.append(result)

        return images
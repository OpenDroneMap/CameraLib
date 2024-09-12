import os
import json
import numpy as np
import rasterio
from cameralib.geo import get_utm_xyz, get_latlonz
from cameralib.camera import load_shots, load_cameras, map_pixels
from cameralib.exceptions import *

class Projector:
    def __init__(self, project_path, z_sample_window=1, z_sample_strategy='median', z_sample_target='dsm', raycast_threshold=1.0):
        if not os.path.isdir(project_path):
            raise IOError(f"{project_path} is not a valid path to an ODM project")
        
        self.project_path = project_path
        self.z_sample_window = z_sample_window
        self.z_sample_strategy = z_sample_strategy
        self.raycast_threshold = raycast_threshold

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

        self.raster = None
        self.dem_data = None
        self.min_z = None
    
    def _read_dem(self):
        if self.raster is None:
            self.raster = rasterio.open(self.dem_path, 'r')
            self.dem_data = self.raster.read(1)
            self.min_z = self.dem_data[self.dem_data!=self.raster.nodata].min()

    def __del__(self):
        if self.raster is not None:
            self.raster.close()
            self.raster = None

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

        self._read_dem()

        r = s['rotation']
        focal = s['focal']
        img_w = s['width']
        img_h = s['height']
        f = focal * max(img_h, img_w)
        t = s['translation'].reshape(3, 1)
        resolution_step = self.raster.transform[0] / np.sqrt(2) 

        rays_cam = cam.pixel_bearing_many(np.array(coordinates)).T
        rays_world = np.matmul(r, rays_cam).T
        results = []
        
        for ray_world in rays_world:
            ray_world = ray_world.reshape((3, 1))
            if float(ray_world[2]) > 0:
                print(f"Warning: Ray from {image} pointing up, cannot raycast")
                continue
        
            step = 0 # meters
            hit = None
            prev_x = None
            prev_y = None
            result = None

            while True:
                ray_pt = (ray_world * step + t).ravel()
                step += resolution_step

                # No hits
                if ray_pt[2] < self.min_z:
                    break

                y, x = self.raster.index(ray_pt[0], ray_pt[1])

                if x == prev_x and y == prev_y:
                    continue
                prev_x, prev_y = x, y

                if x >= 0 and x < self.dem_data.shape[1] and y >= 0 and y < self.dem_data.shape[0]:
                    pix_z = self.dem_data[y,x]

                    if pix_z == self.raster.nodata:
                        continue

                    # Above threshold? Skip more expensive cell intersection test
                    if abs(pix_z - ray_pt[2]) > self.raycast_threshold:
                        continue
                    
                    # Does our ray intersect the raster cell?
                    rast2world = self.raster.transform

                    # 0--1
                    # |  |
                    # 2--3
                    cell0 = np.append(np.array([rast2world * [x - 1.0, y - 1.0]]), pix_z)
                    cell1 = np.append(np.array([rast2world * [x + 1.0, y - 1.0]]), pix_z)
                    cell2 = np.append(np.array([rast2world * [x - 1.0, y + 1.0]]), pix_z)
                    
                    ds10 = cell1 - cell0
                    ds20 = cell2 - cell0
                    normal = np.cross(ds10, ds20)
                    delta = ray_pt - s['translation']
                    ndotdelta = np.dot(normal, delta)
                    if abs(ndotdelta) < 1e-6:
                        continue
                    
                    ts = -np.dot(normal, ray_pt - cell0) / ndotdelta
                    m = ray_pt + delta * ts
                    dms0 = m - cell0
                    u = np.dot(dms0, ds10)
                    v = np.dot(dms0, ds20)
                    if u >= 0 and u <= np.dot(ds10,ds10) and v >= 0 and v<= np.dot(ds20, ds20):
                        # Hit
                        easting, northing = m[0], m[1]
                        result = get_latlonz(self.raster, self.dem_data, y, x, easting, northing, z_sample_window=self.z_sample_window, z_sample_strategy=self.z_sample_strategy)
                        break
            
            results.append(result)
        return results
                        

    # p.cam2world("image.JPG", [(x, y), ...]) --> ((x, y, z), ...) (geographic coordinates)

    def cam2geoJSON(self, image, coordinates, properties={}):
        results = self.cam2world(image, coordinates)

        if 'image' not in properties:
            properties['image'] = image
        
        if len(results) == 1:
            geom = 'Point'
            lat,lon,z = results[0]
            coords = [lon,lat,z]
        elif len(results) == 2:
            geom = 'LineString'
            coords = list([lon,lat,z] for lat,lon,z in results)
        else:
            geom = 'Polygon'
            coords = [list([lon,lat,z] for lat,lon,z in results)]
            coords[0].append(coords[0][0])

        j = {
            'type': 'FeatureCollection',
            'features':[{
                'type': 'Feature',
                'properties': properties,
                'geometry': {
                    'coordinates': coords,
                    'type': geom
                }
            }]
        }
        
        return j

    
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
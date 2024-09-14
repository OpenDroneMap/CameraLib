import rasterio
import math
import numpy as np
from cameralib.exceptions import GeoError, OutOfBoundsError, InvalidArgError
from cameralib.kernels import circle_kernel
from rasterio.warp import transform
from rasterio.crs import CRS

def _get_sample_z(data, nodata, strategy):
    window = data.shape[0]

    if window == 1:
        z = float(data[0,0])
    else:
        valid_locs = data != nodata
        if np.count_nonzero(valid_locs) == 0:
            return nodata

        locs = (circle_kernel(window) == 1) & valid_locs
        if strategy == 'minimum':
            z = float(np.amin(data[locs]))
        elif strategy == 'maximum':
            z = float(np.amax(data[locs]))
        elif strategy == 'average':
            z = float(np.mean(data[locs]))
        elif strategy == 'median':
            z = float(np.median(data[locs]))
        else:
            raise InvalidArgError("Invalid strategy: %s" % strategy)
    
    return z

def raster_sample_z(rast_data, nodata, row, col, window=1, strategy='median'):
    half_win = window / 2.0
    h, w = rast_data.shape
    if row < 0 or col < 0 or row >= h or col >= w:
        return nodata
    
    try:
        data = rast_data[max(0, row-math.floor(half_win)):min(h, row+math.ceil(half_win)),
                         max(0, col-math.floor(half_win)):min(w, col+math.ceil(half_win))]
        return _get_sample_z(data, nodata, strategy)
    except Exception as e:
        raise OutOfBoundsError("Cannot read Z value: %s" % str(e))

def sample_z(rast_ds, x, y, window=1, strategy='median'):
    row, col = rast_ds.index(x, y, op=round)
    half_win = window / 2.0

    try:
        data = rast_ds.read(1, window=((row-math.floor(half_win), row+math.ceil(half_win)), 
                                       (col-math.floor(half_win), col+math.ceil(half_win))))
        return _get_sample_z(data, rast_ds.nodata, strategy)
    except Exception as e:
        raise OutOfBoundsError("Cannot read Z value: %s" % str(e))


def get_utm_xyz(raster_path, latitude, longitude, z_sample_window=1, z_sample_strategy='median'):
    with rasterio.open(raster_path) as d:
        if d.crs is None:
            raise GeoError(f"{raster_path} does not have a CRS")
            
        src_crs = CRS({'init':'EPSG:4326'})
        x, y = transform(src_crs, d.crs, [longitude], [latitude])
        x = x[0]
        y = y[0]

        z = sample_z(d, x, y, z_sample_window, z_sample_strategy)
    
    return x, y, z

def get_latlon(raster, easting, northing):
    if raster.crs is None:
        raise GeoError(f"{raster_path} does not have a CRS")
    
    dst = CRS({'init':'EPSG:4326'})
    longitude, latitude = transform(raster.crs, dst, [easting], [northing])

    return latitude[0], longitude[0]
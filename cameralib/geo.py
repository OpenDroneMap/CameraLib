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
        if z == nodata:
            raise OutOfBoundsError("Tried to sample nodata value")
    else:
        valid_locs = data != nodata
        if np.count_nonzero(valid_locs) == 0:
            raise OutOfBoundsError("Tried to sample nodata value")

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
    if window % 2 == 0 or window <= 0:
        raise InvalidArgError("window must be an odd number > 0")
    
    half_win = window / 2.0
    h, w = rast_data.shape
    try:
        data = rast_data[max(0, row-math.floor(half_win)):min(h, row+math.ceil(half_win)),
                         max(0, col-math.floor(half_win)):min(w, col+math.ceil(half_win))]
        return _get_sample_z(data, nodata, strategy)
    except Exception as e:
        raise OutOfBoundsError("Cannot read Z value: %s" % str(e))

def sample_z(rast_ds, x, y, window=1, strategy='median'):
    if window % 2 == 0 or window <= 0:
        raise InvalidArgError("window must be an odd number > 0")
    
    row, col = rast_ds.index(x, y)
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

def get_latlonz(raster, dem_data, row, col, z_sample_window=1, z_sample_strategy='median'):
    if raster.crs is None:
        raise GeoError(f"{raster_path} does not have a CRS")
    
    dst = CRS({'init':'EPSG:4326'})
    easting, northing = raster.xy(row, col)
    longitude, latitude = transform(raster.crs, dst, [easting], [northing])
    z = raster_sample_z(dem_data, raster.nodata, row, col, window=z_sample_window, strategy=z_sample_strategy)

    return latitude[0], longitude[0], z
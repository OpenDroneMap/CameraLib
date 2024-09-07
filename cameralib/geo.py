import rasterio
import math
import numpy as np
from cameralib.exceptions import GeoError, OutOfBoundsError, InvalidArgError
from cameralib.kernels import circle_kernel
from rasterio.warp import transform
from rasterio.crs import CRS

def sample_z(rast_ds, x, y, window=1, strategy='median'):
    if window % 2 == 0 or window <= 0:
        raise InvalidArgError("window must be an odd number > 0")
    
    row, col = rast_ds.index(x, y)
    half_win = window / 2.0

    try:
        data = rast_ds.read(1, window=((row-math.floor(half_win), row+math.ceil(half_win)), 
                                       (col-math.floor(half_win), col+math.ceil(half_win))))
        if window == 1:
            z = float(data[0,0])
        else:
            locs = (circle_kernel(window) == 1) & (data != rast_ds.nodata)
            if strategy == 'minimum':
                z = float(np.amin(data[locs]))
            elif strategy == 'maximum':
                z = float(np.amax(data[locs]))
            elif strategy == 'average':
                z = float(np.mean(data[locs]))
            elif strategy == 'median':
                z = float(np.median(data[locs]))
            else:
                InvalidArgError("Invalid strategy: %s" % strategy)

    except Exception as e:
        raise OutOfBoundsError("Cannot read Z value: %s" % str(e))

    if z == rast_ds.nodata:
        raise OutOfBoundsError("Nodata value found")
    
    return z


def get_utm_xyz(raster_path, latlng, z_sample_window=1, z_sample_strategy='median'):
    with rasterio.open(raster_path) as d:
        if d.crs is None:
            raise GeoError(f"{raster_path} does not have a CRS")
            
        src_crs = CRS({'init':'EPSG:4326'})
        x, y = transform(src_crs, d.crs, [latlng[1]], [latlng[0]])
        x = x[0]
        y = y[0]

        z = sample_z(d, x, y, z_sample_window, z_sample_strategy)
    
    return x, y, z
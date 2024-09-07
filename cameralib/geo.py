import rasterio
from cameralib.exceptions import GeoError, OutOfBoundsError
from rasterio.warp import transform
from rasterio.crs import CRS

def get_UTM_XYZ(raster_path, latlng):
    with rasterio.open(raster_path) as d:
        if d.crs is None:
            raise GeoError(f"{raster_path} does not have a CRS")
            
        src_crs = CRS({'init':'EPSG:4326'})
        Xa, Ya = transform(src_crs, d.crs, [latlng[1]], [latlng[0]])
        Xa = Xa[0]
        Ya = Ya[0]

        row, col = d.index(Xa, Ya)

        try:
            Za = float(d.read(1, window=((row, row+1), (col, col+1)))[0,0])
        except:
            raise OutOfBoundsError("Cannot read Z value")
        
        if Za == d.nodata:
            raise OutOfBoundsError("Nodata value found")

    
    return Xa, Ya, Za
import os

class Projector:
    def __init__(self, project_path):
        if not os.path.isdir(project_path):
            raise IOError(f"{project_path} is not a valid path to an ODM project")
        
        self.project_path = project_path

        self.dsm_path = os.path.abspath(os.path.join(project_path, "odm_dem", "dsm.tif"))
        self.dtm_path = os.path.abspath(os.path.join(project_path, "odm_dem", "dtm.tif"))

        #self.camera_mappings =
        
    

    def cam2world(self, image, coordinates):
        pass

    # p.cam2world("image.JPG", [(x, y), ...]) --> ((x, y, z), ...) (geographic coordinates)

    def cam2geoJSON(self, image, coordinates):
        pass
    
    # geojson = p.cam2geoJSON("image.JPG", [(x, y), ...]) --> GeoJSON

    def world2cams(x, y, z):
        pass
    
    # cams = p.world2cams(x, y, z) --> Array: [{filename, x, y}, ...]
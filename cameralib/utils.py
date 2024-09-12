import json
import os

def read_xanylabeling_annotations(annotation):
    """Read an annotation file generated with X-AnyLabeling (https://github.com/CVHub520/X-AnyLabeling)
    
    Args:
        annotation (str): Path to annotation JSON file
    
    Returns:
        list of dict: a list containing dictionaries with the following information
        [
            {
                'image': str            # Image filename
                'coordinates': list     # Coordinates of shape
                'properties': dict      # Properties of the shape
            }
        ]
    """
    with open(annotation, 'r') as f:
        j = json.load(f)
    
    return [{
            'image': os.path.basename(j['imagePath']),
            'coordinates': s['points'],
            'properties': {
                'label': s.get('label')
            }
        }for s in j['shapes']]


import os, json
from cameralib import Projector
from cameralib.tests import get_test_dataset
from cameralib.utils import read_xanylabeling_annotations

dataset = get_test_dataset()
p = Projector(dataset)

# Read annotations
annotations = read_xanylabeling_annotations(os.path.join(dataset, "images"))
print(annotations)

# Write them out as GeoJSON
for i in range(len(annotations)):
    out = os.path.join(dataset, f"label_{i}.geojson")
    with open(out, "w") as f:
        f.write(json.dumps(p.cam2geoJSON(**annotations[i])))
        print(out)
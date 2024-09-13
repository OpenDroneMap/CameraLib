import math
from cameralib import Projector
from cameralib.tests import get_test_dataset


p = Projector(get_test_dataset())
coords = [46.8423725961765, -91.99395518749954]
print(f"Input: {coords}")

cams = p.world2cams(*coords)
for cam in cams:
    if cam['filename'] == 'DJI_0028.JPG':
        print(f"X: {cam['x']} Y: {cam['y']}")
        output = p.cam2world('DJI_0028.JPG', [(cam['x'], cam['y'])])
        print(f"Output: {output[0]}")
        rms = math.sqrt((coords[0] - output[0][0]) ** 2 + (coords[1] - output[0][1]) ** 2)
        print(f"Reprojection error: ~{rms / 7.87e-6} meters")


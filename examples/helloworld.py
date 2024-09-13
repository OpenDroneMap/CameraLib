from cameralib import Projector
from cameralib.tests import get_test_dataset


p = Projector(get_test_dataset())
print(p.world2cams(46.8423725961765, -91.99395518749954))
print(p.cam2world("DJI_0028.JPG", [(3576.52, 898.97)]))
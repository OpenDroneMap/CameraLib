"""
CameraLib is a library for performing forward and backward projection of 2D coordinates in camera space to geographic coordinates on ODM projects. It's an official `OpenDroneMap`_ project.

Installation:
-------------

``pip install -U https://github.com/OpenDroneMap/CameraLib/archive/main.zip``

Quickstart:
-----------

Make sure that your ODM project has an elevation model available (pass the ``--dsm`` option when processing a dataset), then:

   >>> from cameralib import Projector
   >>> p = Projector("/dataset/brighton")
   >>> p.world2cams(46.8423725961765, -91.99395518749954)
   [{'filename': 'DJI_0028.JPG', 'x': 3576.5223779005346, 'y': 898.9714056819935}, {'filename': 'DJI_0027.JPG', 'x': 3640.8434954842614, 'y': 1670.683552000412}, {'filename': 'DJI_0031.JPG', 'x': 2066.0067963232805, 'y': 1252.4355627370903}, {'filename': 'DJI_0030.JPG', 'x': 2065.2268758465634, 'y': 255.93742225443987}, {'filename': 'DJI_0032.JPG', 'x': 1979.1241736591578, 'y': 2153.9211152055022}]
   >>> p.cam2world("DJI_0028.JPG", [(3576.52, 898.97)])
   [(46.84237264716458, -91.9939552609622, 165.27200317382812)]

Samples:
--------
 * `Hello World`_
 * `Get Node Info`_

Getting Help / Reporting Issues:
--------------------------------

If you find an issue please `report it`_. We welcome contributions, see the `GitHub`_ page for more information.

For all development questions, please reach out on the `Community Forum`_.

License: AGPLv3, see LICENSE for more details.

API
---

.. _OpenDroneMap:
    https://www.opendronemap.org
.. _Create Task:
   https://github.com/OpenDroneMap/CameraLib/blob/main/examples/hello_world.py
.. _Get Node Info:
   https://github.com/OpenDroneMap/CameraLib/blob/main/examples/get_node_info.py
.. _report it:
    https://github.com/OpenDroneMap/CameraLib/issues
.. _`GitHub`:
    https://github.com/OpenDroneMap/CameraLib
.. _`Community Forum`:
    https://community.opendronemap.org
"""

name = "cameralib"
from .projector import Projector

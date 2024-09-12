"""
CameraLib is a library for performing forward and backward projection of 2D coordinates in camera space to geographic coordinates on ODM projects. It's an official `OpenDroneMap`_ project.

Installation:
-------------

``pip install -U https://github.com/OpenDroneMap/CameraLib/archive/main.zip``

Simple usage:
-------------

   >>> import os
   >>> from pyodm import Node
   >>> n = Node('localhost', 3000)
   >>> task = n.create_task(['examples/images/image_1.jpg', 'examples/images/image_2.jpg'], {'dsm': True})
   >>> task.wait_for_completion()
   >>> os.listdir(task.download_assets("results"))[0:2]
   ['odm_orthophoto', 'odm_dem']

To test these examples you need to start a NodeODM node via:

``docker run -ti -p 3000:3000 opendronemap/nodeodm``

Code Samples:
-------------
 * `Create Task`_
 * `Get Node Info`_

Getting Help / Reporting Issues:
--------------------------------

If you find an issue please `report it`_. We welcome contributions, see the `GitHub`_ page for more information.

For all development questions, please reach out on the `Community Forum`_.

License: AGPLv3, see LICENSE for more details.

.. _OpenDroneMap:
    https://www.opendronemap.org
.. _Create Task:
   https://github.com/OpenDroneMap/PyODM/blob/master/examples/create_task.py
.. _Get Node Info:
   https://github.com/OpenDroneMap/PyODM/blob/master/examples/get_node_info.py
.. _report it:
    https://github.com/OpenDroneMap/PyODM/issues
.. _`GitHub`:
    https://github.com/OpenDroneMap/PyODM
.. _`Community Forum`:
    https://community.opendronemap.org
"""

name = "cameralib"
from .projector import Projector

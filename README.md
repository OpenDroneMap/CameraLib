# CameraLib

A Python library to perform forward and backward projection of 2D coordinates in camera space to geographic coordinates on [ODM](https://github.com/OpenDroneMap/ODM) projects. In simple terms, with an ODM project at hand you can use this library to ask:

 * Given a pixel coordinate in an image, where does it correspond on the map?
 * And it's inverse: given a location on the map, which images and pixels correspond to it?

![image](https://github.com/user-attachments/assets/00d14b1f-16fe-4123-a171-6ef3b774aeb9)

## Install

```bash
pip install -U https://github.com/OpenDroneMap/CameraLib/archive/main.zip
```

Note we developed the library using Python 3.12. If you're having issues with other versions of Python, you might need to relax the versions in `requirements.txt`.

## Usage

Check the [documentation](https://cameralib.readthedocs.io/) and [examples](https://github.com/OpenDroneMap/CameraLib/tree/main/examples).

Along with functions for doing coordinates projection, in the `cameralib.utils` package we also offer utilities to read certain annotations file formats. A use case for this is to use a software such as [X-AnyLabeling](https://github.com/CVHub520/X-AnyLabeling/releases) to annotate an image and then use this library to project the polygon/bounding boxes to geographic coordinates.

## Required Files in ODM project

CameraLib requires the following files from an ODM project. It's important that you process a dataset with the `--dsm` or `--dtm` option.

 * `odm_dem/dsm.tif` or `odm_dem/dtm.tif`
 * `odm_report/shots.geojson`
 * `cameras.json`

## Running the Examples

After [installing](#install) `cameralib` you can download any of the [examples](https://github.com/OpenDroneMap/CameraLib/tree/main/examples) into a folder of your choice and run:

```bash
python helloworld.py
```

## Contributing

We welcome contributions! Pull requests are welcome.

## Support the Project

There are many ways to contribute to the project:

 - ⭐️ us on GitHub.
 - Help us test the application.
 - Spread the word about OpenDroneMap on social media.
 - Help answer questions on the community [forum](https://community.opendronemap.org)
 - Become a contributor!

 ## License

The code in this repository is licensed under the AGPLv3.
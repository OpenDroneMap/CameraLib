import setuptools
import sys
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="cameralib",
    version="1.0.0",
    author="OpenDroneMap Contributors",
    author_email="pt@uav4geo.com",
    description="Camera library for ODM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenDroneMap/CameraLib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: AGPL-3.0-or-later License",
        "Operating System :: OS Independent",
    ],
    install_requires=required
)
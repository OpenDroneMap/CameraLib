import os
import urllib.request
from zipfile import ZipFile 

def get_test_dataset():
    dataset_path = os.path.join("test_datasets", "brighton")
    dataset_zip = os.path.join(dataset_path, "brighton.zip")
    dataset_url = "https://github.com/OpenDroneMap/CameraLib/releases/download/v0.0.1/brighton.zip"

    if not os.path.isfile(dataset_zip):
        os.makedirs(dataset_path, exist_ok=True)
        print(f"Downloading {dataset_url}")
        urllib.request.urlretrieve(dataset_url, dataset_zip)
    
    if not os.path.isdir(os.path.join(dataset_path, "images")):
        with ZipFile(dataset_zip, 'r') as z:
            print(f"Extracting {dataset_zip}")
            z.extractall(dataset_path)
    
    return os.path.abspath(dataset_path)
    

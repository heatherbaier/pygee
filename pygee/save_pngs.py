import rasterio as rio
from PIL import Image
import numpy as np
import zipfile
import imageio
import shutil
import cv2
import os

# from .utils import *

def save_pngs(shapeID, iso, base_dir, export_dir = None, v = True, l = 8):
    
    FULL_DIR = os.path.join(base_dir, iso, shapeID)
    TEMP_DIR = os.path.join(base_dir, iso, shapeID, "temp")
    
    if export_dir is None:
        SAVE_DIR = os.path.join(base_dir, iso, shapeID)
    else:
        SAVE_DIR = export_dir
    
    dir_length = len(os.listdir(FULL_DIR))
    num = 0

    os.makedirs(SAVE_DIR, exist_ok = True)

    for zipfolder in os.listdir(FULL_DIR):
    
        try:
            
            if v:
                print("Image ", str(num), " of ", str(dir_length), "---- Month: May")

            num += 1

            image_name = zipfolder.split(".zip")[0]

            # Extract the RGB TIFF files into the temporary directory
            with zipfile.ZipFile(os.path.join(FULL_DIR, zipfolder), 'r') as zip_ref:
                zip_ref.extractall(TEMP_DIR)

            tiff_files = os.listdir(TEMP_DIR)

            if l == 8:
                b1 = os.path.join(TEMP_DIR, [i for i in tiff_files if i.endswith("B2.tif")][0])
                b2 = os.path.join(TEMP_DIR, [i for i in tiff_files if i.endswith("B3.tif")][0])
                b3 = os.path.join(TEMP_DIR, [i for i in tiff_files if i.endswith("B4.tif")][0])

            elif l == 5:
                b1 = os.path.join(TEMP_DIR, [i for i in tiff_files if i.endswith("B1.tif")][0])
                b2 = os.path.join(TEMP_DIR, [i for i in tiff_files if i.endswith("B2.tif")][0])
                b3 = os.path.join(TEMP_DIR, [i for i in tiff_files if i.endswith("B3.tif")][0])    

            if l == 8:

                b1, b2, b3 = rio.open(b1).read(1), rio.open(b2).read(1), rio.open(b3).read(1)
                b1, b2, b3 = Image.fromarray(np.uint16(b1) / 255), Image.fromarray(np.uint16(b2) / 255), Image.fromarray(np.uint16(b3) / 255)
                stack = np.dstack([np.array(i) for i in [b3, b2, b1]])
                PIL_image = Image.fromarray(np.uint8(stack))#.convert('RGB')

                PIL_image.save(os.path.join(SAVE_DIR, (image_name + ".png")))

            elif l == 5:

                b1, b2, b3 = rio.open(b1).read(1), rio.open(b2).read(1), rio.open(b3).read(1)
                stack = np.dstack([np.array(i) for i in [b3, b2, b1]])
                imageio.imwrite(os.path.join(SAVE_DIR, (image_name + ".png")), stack)    

            [os.remove(os.path.join(TEMP_DIR, i)) for i in os.listdir(TEMP_DIR)]
            
        except Exception as e:
            
            print("Failure with message: ", e)

    shutil.rmtree(TEMP_DIR, ignore_errors = True)

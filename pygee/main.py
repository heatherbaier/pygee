import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import argparse
import shapely
import pyproj

from .utils import *
from .save_boxes import create_imagery_boxes, create_single_imagery_boxes
from .download_imagery import download_imagery
from .save_pngs import save_pngs, clip_image
from .downloadGB import downloadGB

GB_PATH = "./data/MEX/MEX_ADM2_fixedInternalTopology.shp"
ISO = "MEX"
ADM_ID = "MEX-ADM2-1590546715-B7"
IC = "LANDSAT/LT05/C01/T1"


downloadGB(ISO, "2")


create_single_imagery_boxes(gb_path = GB_PATH, 
                            iso = ISO, 
                            adm_id = ADM_ID)


download_imagery(shapeID = ADM_ID, 
                 year = "2010", 
                 ic = IC, 
                 month = "1", 
                 iso = ISO)

save_pngs(shapeID = ADM_ID)


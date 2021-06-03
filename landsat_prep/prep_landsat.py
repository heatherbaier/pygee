import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import argparse
import shapely
import pyproj

from .helpers import *
from .save_boxes import create_imagery_boxes, create_single_imagery_boxes
from .download_imagery import download_imagery
from .save_pngs import save_pngs, clip_image


# GB_PATH = "/Users/heatherbaier/Desktop/CAOE/data/MEX/MEX_ADM2_fixedInternalTopology.shp"
# ISO = "MEX"
# ADM_ID = "MEX-ADM2-1590546715-B8"
# IC = "LANDSAT/LT05/C01/T1"


def prep_landsat(gb_path, iso, shapeID, year, month, ic):

    create_single_imagery_boxes(gb_path = gb_path, iso = iso, adm_id = shapeID)

    download_imagery(shapeID = shapeID, year = year, ic = ic, month = month, iso = iso)

    save_pngs(shapeID = shapeID)


# prep_landsat(GB_PATH, ISO, ADM_ID, "2010", "1", IC)
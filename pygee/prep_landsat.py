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


def prep_landsat(gb_path, iso, shapeID, year, month, ic, v = True):

    """
    ARGS:
        - gb_path: Path to shapefile that contains 1) a column entitle 'shapeID' and 2) a row in that column with a polygon matching shapeID input
        - iso: ISO3C shapefile (used to locate directory and name files)
        - shapeID: Name of target polgyon to download Landsat imagery for
        - year: Year of Landsat imagery
        - month: Month of Landsat imagery
        - ic: GEE Imagery Collection (needs to be raw images i.e. NOT TOA)
        - v: Verbose (If True, print out messages, if False, don't)

    EXAMPLE USAGE:
        GB_PATH = "/Users/heatherbaier/Desktop/CAOE/data/MEX/MEX_ADM2_fixedInternalTopology.shp"
        ISO = "MEX"
        ADM_ID = "MEX-ADM2-1590546715-B8"
        IC = "LANDSAT/LT05/C01/T1"
        V = True

        prep_landsat(GB_PATH, 
                     iso = ISO, 
                     shapeID = ADM_ID, 
                     year = "2010", 
                     month = "1", 
                     ic = IC, 
                     v = V)
    """

    create_single_imagery_boxes(gb_path = gb_path, iso = iso, adm_id = shapeID, v = v)
    download_imagery(shapeID = shapeID, year = year, ic = ic, month = month, iso = iso, v = v)
    save_pngs(shapeID = shapeID, iso = iso, v = v)

    if v:
        print("Done prepping Landsat imagery for ", str(shapeID))
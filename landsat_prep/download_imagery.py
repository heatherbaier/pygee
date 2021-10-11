from datetime import date, timedelta
from joblib import Parallel, delayed
from functools import partial
import geopandas as gpd
import multiprocessing
import pandas as pd
import numpy as np
import argparse
import calendar
import datetime
import requests
import shapely
import pyproj
import shutil
import ee
import os

from .helpers import *



    # if type(month) != list:
    #     # Get the start and end dates of each month in the year to filter the imagery
    #     dates = GetDays(year, month)
    # elif type(month) == list:
    #     dates = month



def download_imagery(geom, shapeID, ic, dates, imagery_dir, bands, cloud_free = False, im = False, v = True):

    """
    ARGS:
        - shp: shapefile with unique ID column named shapeID
        - shapeID: Name of target polgyon to download imagery for
        - year: Year of Landsat imagery
        - ic: GEE Imagery Collection (needs to be raw images i.e. NOT TOA)
        - month: Month of Landsat imagery
        - iso: ISO3C shapefile (used to locate directory and name files)
        - v: Verbose (If True, print out messages, if False, don't)

    EXAMPLE USAGE:
        ADM_ID = "MEX-ADM2-1590546715-B8"
        YEAR = "2010"
        IC = "LANDSAT/LT05/C01/T1"
        MONTH = "8"
        ISO = "MEX"
        V = True
        
        download_imagery(shapeID = ADM_ID, 
                         year = YEAR, 
                         ic = IC, 
                         month = MONTH, 
                         iso = ISO, 
                         v = V)
    """

    ee.Initialize()

    # Set up imagery directories
    cur_directory = os.path.join(base_dir, shapeID)
    os.makedirs(cur_directory, exist_ok = True)

    cur_directory = os.path.join(base_dir, shapeID, "imagery")
    os.makedirs(cur_directory, exist_ok = True)

    try:

        cur_shp = convert_to_ee_feature(geom)


        if im:
            imagery = ee.Image(ic)
        elif not im:
            imagery = ee.ImageCollection(ic).filterDate(dates[0], dates[1]).filterBounds(cur_shp)
            if v:
                print(shapeID, " has ", imagery.size().getInfo(), " images available in ", year)
            if cloud_free:
                m = ee.Algorithms.Landsat.simpleComposite(imagery).select(bands)
            elif not cloud_free:
                m = imagery.select(bands).median()               

        m = m.clip(cur_shp)

        # Get the 4 point bounding box of the ADM2 to limit the export region
        region = ee.Geometry.Rectangle(list(geom.bounds))

        fname = cur_directory + "/" + shapeID + "_" + str(year) + "_" + str(month) + ".zip"

        # Get the URL download link
        link = m.getDownloadURL({
                'name': shapeID + "_" + str(year) + "_" + str(month),
                'crs': 'EPSG:4326',
                'fileFormat': 'GeoTIFF',
                'region': region,
                'scale':30,
                'maxPixels': 1e9
        })

        r = requests.get(link, allow_redirects = True)

        open(fname, 'wb').write(r.content)

    except Exception as e:

        print(e)




if __name__ == "__main__":

    # Trigger the authentication flow.
    # ee.Authenticate()

    # Parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("ic", help="GEE Imagery Collection ID")
    # parser.add_argument("ISO", help="Country ISO3")
    parser.add_argument("iso", help="you know what it is")
    parser.add_argument("--year_list", nargs="+")
    parser.add_argument("--month_list", nargs="+")
    args = parser.parse_args()# python3 DownloadImagery.py

    print(args.year_list)
    print(args.month_list)

    

    # Intitialize connection to GEE
    ee.Initialize()

    # Read in the shapefile to clip from
    SHP_PATH = os.path.join("./data/", args.iso, (args.iso + "imagery_bboxes.shp"))
    SHP_PATH  = "./tmp/484001001.shp"
    shp = gpd.read_file(SHP_PATH)

    # Parallelization
    num_cores = multiprocessing.cpu_count()
    output = Parallel(n_jobs=num_cores)(delayed(main)(year=y, ic=args.ic, shp=shp, month=j, iso = args.iso) for y in args.year_list for j in args.month_list)

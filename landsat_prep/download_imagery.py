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


def main(year, ic, shp, month, iso):

    ee.Initialize()

    # Get the start and end dates of each month in the year to filter the imagery
    dates = GetDays(year, month)

    # Set up imagery directories
    SetUp(year, month, iso)

    # Make a new directory to organize the imagery
    cur_directory = os.path.join(("./" + iso + "imagery"), str(year), str(month))
    os.mkdir(cur_directory)

    boxes_dict = {}

    # For the bounding box of every Mexico ADM2...
    for col, row in shp.iterrows():

        try:

            # Convert the ADM2 shape to a GEE feature
            cur_shp = ConvertToFeature(row.geometry)

            # Dictionary stuff
            if row.shapeID in boxes_dict.keys():
                boxes_dict[row.shapeID] += 1
            else:
                boxes_dict[row.shapeID] = 1

            # Grab Landsat 5 Bands 1, 2 and 3 for the current month, year and ADM2
            l5 = ee.ImageCollection(ic).filterDate(dates[0], dates[1]).filterBounds(cur_shp)

            print(row.shapeID, " has ", l5.size().getInfo(), " images available in ", year)

            # Mosaic the images together using the min (using min to avoid the high values of clouds)
            m = ee.Algorithms.Landsat.simpleComposite(l5).select(['B3', 'B2', 'B1'])

            m = m.clip(cur_shp)

            # Get the 4 point bounding box of the ADM2 to limit the export region
            geometry = ee.Geometry.Rectangle(list(row.geometry.bounds))

            fname = cur_directory + "/" + row.shapeID + "_" + str(year) + "_" + str(month) + "_box" + str(boxes_dict[row.shapeID]) + ".zip"

            # Get the URL download link
            link = m.getDownloadURL({
                    'name': row.shapeID + "_" + str(year) + "_" + str(month),
                    'crs': 'EPSG:4326',
                    'fileFormat': 'GeoTIFF',
                    'region': geometry,
                    'scale':30
            })

            r = requests.get(link, allow_redirects = True)

            open(fname, 'wb').write(r.content)

        # except:

        #     print("Imagery not available for ", row.shapeID, " during month ", str(month), " of ", str(year))


        except Exception as e:
            print(e)



def download_imagery(shapeID, year, ic, month, iso):

    SHP_PATH = os.path.join("./data/", shapeID, (shapeID + ".shp"))
    shp = gpd.read_file(SHP_PATH)

    ee.Initialize()

    # Get the start and end dates of each month in the year to filter the imagery
    dates = GetDays(year, month)

    # Set up imagery directories
    # SetUp(year, month, iso)

    # Make a new directory to organize the imagery
    cur_directory = os.path.join("./data/", shapeID, "imagery")
    os.mkdir(cur_directory)

    boxes_dict = {}

    # For the bounding box of every Mexico ADM2...
    for col, row in shp.iterrows():

        try:

            # Convert the ADM2 shape to a GEE feature
            cur_shp = ConvertToFeature(row.geometry)

            # Dictionary stuff
            if row.shapeID in boxes_dict.keys():
                boxes_dict[row.shapeID] += 1
            else:
                boxes_dict[row.shapeID] = 1

            # Grab Landsat 5 Bands 1, 2 and 3 for the current month, year and ADM2
            l5 = ee.ImageCollection(ic).filterDate(dates[0], dates[1]).filterBounds(cur_shp)

            print(row.shapeID, " has ", l5.size().getInfo(), " images available in ", year)

            # Mosaic the images together using the min (using min to avoid the high values of clouds)
            m = ee.Algorithms.Landsat.simpleComposite(l5).select(['B3', 'B2', 'B1'])

            m = m.clip(cur_shp)

            # Get the 4 point bounding box of the ADM2 to limit the export region
            geometry = ee.Geometry.Rectangle(list(row.geometry.bounds))

            fname = cur_directory + "/" + shapeID + "_" + str(year) + "_" + str(month) + "_box" + str(row.shapeID) + ".zip"

            # Get the URL download link
            link = m.getDownloadURL({
                    'name': shapeID + "_" + str(year) + "_" + str(month) + "_box" + str(row.shapeID),
                    'crs': 'EPSG:4326',
                    'fileFormat': 'GeoTIFF',
                    'region': geometry,
                    'scale':30
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
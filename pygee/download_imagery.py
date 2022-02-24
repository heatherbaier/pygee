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

from .utils import *

from .tiler import *


def download_large_imagery(shapeID,
                           geom,
                           IC,
                           dates,
                           imagery_dir,
                           bands,
                           scale,
                           max_pixels,
                           is_temp_dir = False):
        
        # If it is testing a new size, there will already be a _box in the shapeID name, so remove that 
        shapeID = shapeID.split("_")[0]
                
        imagery_dir = imagery_dir.strip(shapeID)

        tiles = Tiler(geom = geom,
                      max_pixels = max_pixels,
                      scale = scale).int_grid         

        temp_dir = os.path.join(imagery_dir, str(shapeID))
                
        max_pixels -= int(max_pixels * .10)

        for tile_col, tile_row in tiles.iterrows():
            
            download_imagery(geom = tile_row.geometry,
                                   shapeID = shapeID + "_box" + str(tile_row.shapeID),
                                   ic = IC, 
                                   dates = dates, 
                                   imagery_dir = temp_dir, 
                                   bands = bands,
                                   scale = scale,
                                   max_pixels = max_pixels)



def download_imagery(geom, shapeID, ic, dates, imagery_dir, bands, scale = 30, cloud_free = False, im = False, v = True, max_pixels = 1000):
    
    ee.Initialize()

    cur_directory = os.path.join(imagery_dir, shapeID)
    
    if not os.path.isdir(cur_directory):
        os.makedirs(cur_directory)

    try:

        cur_shp = pygee.convert_to_ee_feature(geom)

        if im:
#             if bands == None:
            m = ee.Image(ic)
            if bands is not None:
                m = m.select(bands)
        elif not im:
            if dates is not None:
                imagery = ee.ImageCollection(ic).filterDate(dates[0], dates[1]).filterBounds(cur_shp)
            else:
                imagery = ee.ImageCollection(ic).filterBounds(cur_shp)
            if v:
                print(shapeID, " has ", imagery.size().getInfo(), " images available between ", " and ".join(dates))
            if cloud_free:
                m = ee.Algorithms.Landsat.simpleComposite(imagery).select(bands)
            elif not cloud_free:
                m = imagery.select(bands).median()               

        m = m.clip(cur_shp)

        region = ee.Geometry.Rectangle(list(geom.bounds))
        
        if dates is not None:
            fname = cur_directory + "/" + shapeID + "_" + "_".join(dates) + ".zip"
            lname = shapeID + "_" + "_".join(dates)
        else:
            fname = cur_directory + "/" + shapeID + ".zip"
            lname = shapeID
            
            
        # Get the URL download link
        link = m.getDownloadURL({
                'name': lname,
                'crs': 'EPSG:4326',
                'fileFormat': 'GeoTIFF',
                'region': region,
                'scale': scale,
                'maxPixels': 1e9
        })
                

        r = requests.get(link, allow_redirects = True)
        open(fname, 'wb').write(r.content)
        
 
    except Exception as e:
        
        print("E: ", e)
                
        if "must be less than or equal to" in str(e):
            
            download_large_imagery(shapeID,
                                   geom,
                                   ic,
                                   dates,
                                   imagery_dir,
                                   bands,
                                   scale = scale,
                                   max_pixels = max_pixels)
            
        else:
            
            print(e)
            
            

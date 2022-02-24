from shapely.geometry import shape
from math import sqrt, floor
import geopandas as gpd
import pandas as pd
import numpy as np
import shapely
import pygee
import math
import os

from .utils import *

import utm
import pyproj
from shapely.geometry import Point
from shapely.ops import transform

def convert_to_meters(geom):    
    
    centroid = geom.centroid
    utm_zone = utm.from_latlon(centroid.y, centroid.x)[2]
    proj4 = "+proj=utm +zone=" + str(utm_zone) + " +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
    
    wgs84 = pyproj.CRS('EPSG:4326')
    proj4 = pyproj.CRS.from_proj4(proj4)
        
    project = pyproj.Transformer.from_crs(wgs84, proj4, always_xy=True).transform

    utm_poly = transform(project, geom)    
    
    return utm_poly, proj4.to_epsg()


class Tiler():
    
    def __init__(self, geom, max_pixels = 1000, scale = 30, to_gdf = True):
        
        """        
        Arguments:
            - geom = shapely polygon you want to tile
            - max_pixels = maximum number of pixels (for both width & height) 
              in tile (e.g. if 1000, each tile will be 1000x1000 pixels)
            - scale = pixel size
            - to_gdf = if False, output tiles as a list of polygons; if True, output 
              tiles as a GeoDataframe with shapeID (0, n-1) and geometry columns
        """

        self.scale = scale
        self.max_pixels = max_pixels
            
        self.geom = geom
        self.utm_geom, self.utm_crs = convert_to_meters(self.geom)
        
        self.to_gdf = to_gdf
        self.grid = self.__partition()
        self.int_grid = self.__get_intersection()
        
    def __partition(self):

        bounds = self.utm_geom.bounds
                
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        num_pixels = (width * height) / self.scale**2
        num_partiitons = num_pixels / (self.max_pixels ** 2)
        num_partitions = getClosestPerfectSquare(int(num_partiitons))
        
        if num_partitions == 0:
            num_partitions = 4
        num_breaks = int(math.sqrt(num_partitions))
        

        x_increment, y_increment = width / num_breaks, height / num_breaks

        polys = []
        for yi in range(0, num_breaks + 1):
            for xi in range(0, num_breaks + 1):
                minx = bounds[0] + (x_increment * xi)
                miny = bounds[1] + (y_increment * yi)
                maxx = bounds[0] + (x_increment * (xi + 1))
                maxy = bounds[1] + (y_increment * (yi + 1))

                if maxx > bounds[2]:
                    maxx = bounds[2]
                if maxy > bounds[3]:
                    maxy = bounds[3]            

                poly = (minx, miny, maxx, maxy)
                polys.append(shapely.geometry.box(*poly, ccw=True))

        if self.to_gdf:
            gdf = gpd.GeoDataFrame(geometry = polys)
            gdf['shapeID'] = [i for i in range(0, len(gdf))]
            gdf['area'] = gdf.geometry.area
            gdf = gdf[gdf['area'] != 0].drop(['area'], axis = 1)
            gdf = gdf.set_crs(self.utm_crs)
            gdf = gdf.to_crs("EPSG:4326")        
            return gdf
        else:
            return polys
        

    def __get_intersection(self):
        fc_intersect = []
        for c, featB in enumerate(self.grid.geometry):
            if shape(self.geom).intersects(shape(featB)):
                fc_intersect.append(featB)
        tiles = gpd.GeoDataFrame(geometry = fc_intersect)
        tiles['shapeID'] = [i for i in range(0, len(tiles))]
        return tiles

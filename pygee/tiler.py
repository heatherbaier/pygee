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


class Tiler():
    
    def __init__(self, shapeID, shp, bbox_shp, crs, to_gdf = True):
        
        self.shapeID = shapeID
        
        self.shp = shp[shp["GEOLEVEL2"] == self.shapeID]
        
        self.bbox_geom = bbox_shp[bbox_shp["shapeID"] == self.shapeID]
        self.bbox_geom = self.bbox_geom.set_crs("EPSG:4326")
        self.bbox_geom = self.bbox_geom.to_crs("EPSG:6362")
        self.bbox_geom = self.bbox_geom.geometry.to_list()[0]
        
        self.to_gdf = to_gdf
        self.og_crs = crs
        self.grid = self.__partition()
        self.int_grid = self.__get_intersection()
        
    def __partition(self):

        bounds = self.bbox_geom.bounds

        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        num_pixels = (width * height) / 30**2
        num_partiitons = num_pixels / (1000 ** 2)
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
            gdf = gdf.set_crs(self.og_crs)
            gdf = gdf.to_crs("EPSG:4326")        
            return gdf
        else:
            return polys
        

    def __get_intersection(self):
        fc_intersect = []
        for c, featB in enumerate(self.grid.geometry):
            if shape(self.shp['geometry'].to_list()[0]).intersects(shape(featB)):
                fc_intersect.append(featB)
        tiles = gpd.GeoDataFrame(geometry = fc_intersect)
        tiles['shapeID'] = [i for i in range(0, len(tiles))]
        return tiles
    
    
    def plot(self, intersected = True):
        if intersected:
            base = self.int_grid.plot(color='white', edgecolor='black')
        else:
            base = self.grid.plot(color='white', edgecolor='black')            
        self.shp.plot(ax=base, marker='o', color='red', markersize=5);

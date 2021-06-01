import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import argparse
import shapely
import pyproj

from helpers import *


def main(gb_path, iso):

    bbox = gpd.read_file(gb_path)

    # Project the box into the meters projection
    wgs84 = pyproj.CRS('EPSG:4326')
    utm_proj_string = "+proj=utm +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0"
    utm_proj = pyproj.CRS.from_proj4(utm_proj_string)
    projection = pyproj.Transformer.from_crs(wgs84, utm_proj, always_xy = True).transform
    projection_back = pyproj.Transformer.from_crs(utm_proj, wgs84, always_xy=True).transform

    BOXES_DIR = os.path.join("./data/", args.iso, "imagery_bboxes")

    print(BOXES_DIR)

    # If the folder already exists, delete it
    if os.path.isdir(BOXES_DIR):
        shutil.rmtree(BOXES_DIR)

    os.mkdir(BOXES_DIR)

    print("Creating imagery bounding boxes shapefile in ", BOXES_DIR)

    for col, row in bbox.iterrows():
        make_points(row, projection, projection_back, BOXES_DIR, utm_proj, wgs84)

    all_boxes = gpd.GeoDataFrame()

    box_shps = [i for i in os.listdir(BOXES_DIR) if i.endswith(".shp")]


    for i in box_shps:
        cur_file = os.path.join(BOXES_DIR, i)
        cur_boxes = gpd.read_file(cur_file)
        all_boxes = all_boxes.append(cur_boxes)

    SHP_PATH = os.path.join("./data/", args.iso, (args.iso + "imagery_bboxes.shp"))
    all_boxes.to_file(SHP_PATH)

    print("Done creating imagery bounding boxes.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("iso", help="Country ISO")
    args = parser.parse_args()

    gB_dir = os.path.join("./data/", args.iso)
    gb_path = os.path.join(gB_dir, [f for f in os.listdir(gB_dir) if f.endswith(".shp")][0])

    print(gb_path)
    
    main(gb_path, args.iso)
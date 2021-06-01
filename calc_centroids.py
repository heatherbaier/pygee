import geopandas as gpd
import argparse

def get_centroid(x):
    return x.centroid

def main(gdf):



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("iso", help="Country ISO")
    args = parser.parse_args()

    shp_path = os.path.join("./data/", args.iso, (args.iso + "imagery_bboxes.shp"))
    gdf = gpd.read_file(shp_path)

    main(gdf)
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import shapely
import pyproj
import os



def make_boxes(intersected_points, box, utm_proj):
  
    # For each of the points that intersected with the bounding box, create a 224x224px square around it
    polys = []
    for p in range(0, len(intersected_points)):
        m1, m2 = intersected_points[p].x + 3360, intersected_points[p].y + 3360
        m3, m4 = intersected_points[p].x - 3360, intersected_points[p].y + 3360
        m5, m6 = intersected_points[p].x - 3360, intersected_points[p].y - 3360
        m7, m8 = intersected_points[p].x + 3360, intersected_points[p].y - 3360
        polygon = shapely.geometry.Polygon([[m1, m2], [m3, m4], [m5, m6], [m7, m8]])
        polys.append(polygon)

    # Convert that list of 224x224px squares to a geodataframe
    polys_gdf = gpd.GeoDataFrame(geometry = polys, crs = utm_proj)
    intersected_gdf = gpd.GeoDataFrame(geometry = [i for i in polys_gdf.geometry if box.contains(i)], crs = utm_proj)

    return intersected_gdf



def find_intersecting_points(intersected, top_left_point, bottom_left_point, inital_point, test_point, bounding_box, box):

    points = []

    while intersected == True:

        # Append the latest point to the list
        points.append(test_point)

        # Move the test point to the right a bit and test if it intersects with the bounding box
        test_point = shapely.geometry.Point(test_point.x + 6720, test_point.y)
        intersected = test_point.within(bounding_box)

        # If the point moving to the right no longer intersects AND the point can still move down...
        if (test_point.y  > bottom_left_point.y) and (not intersected):

            # Move the point point back to the initial left position and scooch it down, then test if it intersects
            test_point = shapely.geometry.Point(inital_point.x, test_point.y - 6720)
            intersected = test_point.within(bounding_box)

    intersected_points = [i for i in points if i.within(box)]

    return intersected_points




def make_points(box, projection, projection_back, boxes_dir, utm_proj, wgs84):

  try:

    shapeID = str(box.CNTRY_CODE) + str(box.IPUM2010)
    print(shapeID)
    box = box.geometry

    # Project the box into meters
    # municipality = shapely.ops.transform(projection, shape)
    box = shapely.ops.transform(projection, box)
    
    # Get the min and max bounding coords and make them into a shapely Polygon
    bounds = box.bounds
    min_x, min_y, max_x, max_y = bounds[0], bounds[1], bounds[2], bounds[3]
    bounding_box = shapely.geometry.box(bounds[0], bounds[1], bounds[2], bounds[3])

    # Make the initial top left point of the bounding box
    top_left_point    = shapely.geometry.Point(min_x, max_y)
    bottom_left_point = shapely.geometry.Point(min_x, min_y)
    inital_point      = shapely.geometry.Point(top_left_point.x + 6720.0, top_left_point.y - 6720.0)
    test_point        = shapely.geometry.Point(top_left_point.x + 6720.0, top_left_point.y - 6720.0)

    # Double check that it intersects with our overall bounding box
    intersected = inital_point.within(bounding_box)

    # Get the points that intersect with the municipality
    intersected_points = find_intersecting_points(intersected, top_left_point, bottom_left_point, inital_point, test_point, bounding_box, box)

    # Make a 224x224px box around each point and convert those boxes into a geodataframe
    intersected_gdf = make_boxes(intersected_points, box, utm_proj)

    # Save that geodataframe
    gdf_name = os.path.join(boxes_dir, shapeID + ".shp")
    ref = pd.DataFrame([shapeID for i in range(0, len(intersected_gdf))])
    to_save = gpd.GeoDataFrame(ref, geometry = [shapely.ops.transform(projection_back, i) for i in intersected_gdf.geometry], crs = wgs84)
    to_save = to_save.rename(columns = {0: 'shapeID'})
    to_save.to_file(gdf_name)

  except Exception as e:

    print(e)



def makeGBdir(iso):
  
    # If the folder already exists, delete it
    if os.path.isdir(os.path.join("./data", iso)):
        shutil.rmtree(os.path.join("./data", iso))
    else:
        "Couldn't delete old folder"
    
    # Create new folder
    try:
        os.mkdir(os.path.join("./data", iso))
    except:
        os.mkdir("./data")
        os.mkdir(os.path.join("./data", iso))

    # ...and return the path
    return os.path.join("./data", iso)





def SetUp(year, month, iso):

  """TODO: Make this make the imagery folder!"""

  if not os.path.isdir("./" + iso + "imagery"):
    os.mkdir("./" + iso + "imagery")

  if not os.path.isdir(os.path.join(("./" + iso + "imagery"), year)):
    os.mkdir(os.path.join(("./" + iso + "imagery"), year))















from datetime import date, timedelta
import geopandas as gpd
import pandas as pd
import numpy as np
import calendar
import datetime
import shapely
import random
import pyproj
import ee
import os
import pyproj



def CalcBbox(x):
    """
        Calculate bounding box of a polgyon and return as a shapely polygon
    """
    bounds = list(x.bounds)
    box = shapely.geometry.box(bounds[0], bounds[1], bounds[2], bounds[3])
    return box.wkt


def GetMonths(year):
    flist = []
    for i in range(1, 13):
        r = list(calendar.monthrange(year, i))[1]
#         sdate = datetime.date(year, i, 1)
#         edate = datetime.date(year, i, r)
        sdate = "-".join([str(year), str(i), str(1)])
        edate = "-".join([str(year), str(i), str(r)])
        
        flist.append([sdate, edate])
        
    return flist


def GetInfo(im):
    pid = im.get('LANDSAT_PRODUCT_ID')
    cloudiness = im.get('CLOUD_COVER')
    return [str(pid.getInfo()), str(cloudiness.getInfo())]



def GetDates(start, end, d):
    """
    Inputs:
        - start: Start date (formatted as: '2010-01-01')
        - end:   End date (formatted as: '2010-01-01')
        - d:     Time delta (number of dates between each date in outputted list) 
        
    Example Usage:
        GetDates('2008-08-01', '2008-09-01', 1)
    """
    final_dates = []
    sdate, edate = start.split("-"), end.split("-")
    sdate = date(int(sdate[0]), int(sdate[1]), int(sdate[2]))   # start date
    edate = date(int(edate[0]), int(edate[1]), int(edate[2]))   # end date
    
    delta = edate - sdate       # as timedelta
    
    day = sdate
    final_dates.append(sdate)
    while day < edate:
        day = final_dates[-1] + timedelta(days = d)
        if day < edate:
            final_dates.append(day)
            
    return final_dates



def ConvertToFeature(shp):
    """
    Function to convert shapely polygons/geopandas DF to GEE Feature Collection
    
    Input:
        - shp: geopandas dataframe
    Output:
        - GEE FeatureCollection
    """

    features=[]
    
    x,y = shp.exterior.coords.xy
    print(x,y)
    cords = np.dstack((x,y)).tolist()

    g = ee.Geometry.Polygon(cords)
    feature = ee.Feature(g)
    features.append(feature)

    ee_object = ee.FeatureCollection(features)
        
    return ee_object



def MultiToPoly(x):
    
    """
    Function to convert the MultiPolygons to Polygons
    
    Input:
        - x: row.geometry
    Output:
        - Polygon of the MultiPolygon with the max area
    """
    
    if x.geom_type != 'Polygon':
        # Get the area of all mutipolygon parts
        areas = [i.area for i in x]

        # Get the area of the largest part
        max_area = areas.index(max(areas))    

        # Return the index of the largest area
        return x[max_area]
    
    else:
        return x



def GetImageCounts(start, end, d):
    
    """
    Function to get the number of images found between sets of dates
    Inputs:
        - start: Start date (formatted as: '2010-01-01')
        - end:   End date (formatted as: '2010-01-01')
        - d:     Time delta (number of dates between each date in outputted list) 
    Output:
        - Pandas DataFrame with the start date and counts of images in each row
    """
    
# gdf = gpd.read_file("./data/MexicoPRs.shp")
# gdf = gdf[['shapeName', 'shapeID', 'PATH', 'ROW', 'PR', 'geometry']]
# gdf.head()
    # Intitialize variables and get all of the dates in a user given range
    df, counts, all_dates= pd.DataFrame(), [], []
    dates = GetDates(start, end, d)
    
    # Get Mexico's border
    mex = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017').filterMetadata('country_na', 'equals', 'Mexico')
    
    # For every date...
    while len(dates) >= 2:
        
        # Filter the iamge collection to days that are d days apart
        ic = ee.ImageCollection('LANDSAT/LT05/C01/T1_TOA').filterDate(str(dates[0]), str(dates[1])).filterBounds(mex)
        print(ic.size().getInfo())
        
        # Append the Date and count of images to lists
        counts.append(ic.size().getInfo())
        all_dates.append(dates[0])
        del dates[0]
        
    # Make a dataframe to export with the dates and count of images on that date/before the next
    df['Date'], df['Count'] = all_dates, counts
    
    return df







# def makeGBdir(iso):
  
#     # If the folder already exists, delete it
#     if os.path.isdir(os.path.join("./data", iso)):
#         shutil.rmtree(os.path.join("./data", iso))
#     else:
#         "Couldn't delete old folder"
    
#     # Create new folder
#     os.mkdir(os.path.join("./data", iso))

#     # ...and return the path
#     return os.path.join("./data", iso)



def GetDays(year, month):
  r = list(calendar.monthrange(int(year), int(month)))[1]
  sdate = "-".join([str(year), str(month), str(1)])
  edate = "-".join([str(year), str(month), str(r)])

  return [sdate, edate]


def makeBboxDir(iso):
    path = os.path.join("./data/", iso, (iso + "_bbox"))
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.mkdir(path)
    

    
def generate_random(x):
  number = 4
  points = []
  minx, miny, maxx, maxy = x.bounds
  while len(points) < number:
    pnt = shapely.geometry.Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
    if x.contains(pnt):
      points.append(pnt)
  return points





def CalcDist(pixelSize, resolution):
    return (pixelSize * resolution) / 2    




def CreatePoly(row):
    
    final_polys = []
    
    m1, m2 = row['bbox_ur_lat'], row['bbox_ur_long']
    m3, m4 = row['bbox_lr_lat'], row['bbox_lr_long']
    m5, m6 = row['bbox_ll_lat'], row['bbox_ll_long']
    m7, m8 = row['bbox_ul_lat'], row['bbox_ul_long']
    
    polygon = shapely.geometry.Polygon([[m1, m2], [m3, m4], [m5, m6], [m7, m8]])
    
    return polygon


def ListifyPoints(x, index):
    x = np.array(x)
    return x[index]


def CreateBoxes(shp, zone, dist):
    
    # Reproject to UTM
    utm_string = "+proj=utm +zone=" + str(zone) + " +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0"
    utm_proj = pyproj.CRS.from_proj4(utm_string)
    shp.geometry = shp.geometry.to_crs(utm_proj)
    
    # Create UTM Box Coords
#    geom = pd.DataFrame(shp.geometry)

    shp['utm_latitude'] = shp.geometry.apply(lambda x: ListifyPoints(x, 0)) 
    shp['utm_longitude'] = shp.geometry.apply(lambda x: ListifyPoints(x, 1)) 
    
    shp['bbox_ur_lat'] = shp['utm_latitude'] + dist
    shp['bbox_ur_long'] = shp['utm_longitude'] + dist
    
    shp['bbox_lr_lat'] = shp['utm_latitude'] + dist
    shp['bbox_lr_long'] = shp['utm_longitude'] - dist

    shp['bbox_ll_lat'] = shp['utm_latitude'] - dist
    shp['bbox_ll_long'] = shp['utm_longitude'] - dist

    shp['bbox_ul_lat'] = shp['utm_latitude'] - dist
    shp['bbox_ul_long'] = shp['utm_longitude'] + dist
    
    # Create Box Polygons from each row in the dataframe
    final_polys = []
    for col, row in shp.iterrows():
        cur_poly = CreatePoly(row)
        final_polys.append(cur_poly)
    shp['box'] = final_polys
    
    # Create gpd and assign CRS then reproject
    geom = gpd.GeoDataFrame(shp, geometry=shp.box, crs = utm_proj)
    geom.geometry.crs = utm_string
    geom = geom.to_crs(epsg=4326)
#     geom = geom.drop(['box'], axis = 1)
    
    return geom
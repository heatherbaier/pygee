

    # if type(month) != list:
    #     # Get the start and end dates of each month in the year to filter the imagery
    #     dates = GetDays(year, month)
    # elif type(month) == list:
    #     dates = month






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



def download_imagery(shapeID, year, ic, month, iso, base_dir, v = True, cloud_free = False):

    """
    ARGS:
        - shapeID: Name of target polgyon to download Landsat imagery for
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

    SHP_PATH = os.path.join(base_dir, iso, shapeID, (shapeID + ".shp"))
    shp = gpd.read_file(SHP_PATH)

    ee.Initialize()

    # Get the start and end dates of each month in the year to filter the imagery
    dates = GetDays(year, month)

    # Set up imagery directories
    # SetUp(year, month, iso)

    # Make a new directory to organize the imagery
    cur_directory = os.path.join(base_dir, iso, shapeID, "imagery")
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

            if v:
                print(row.shapeID, " has ", l5.size().getInfo(), " images available in ", year)

            # Mosaic the images together using the min (using min to avoid the high values of clouds)
            if cloud_free:
                m = ee.Algorithms.Landsat.simpleComposite(l5).select(['B3', 'B2', 'B1'])
            else:
                m = l5.min()

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


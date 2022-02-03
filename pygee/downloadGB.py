from pandas.io.json import json_normalize
import pandas as pd
import requests
import argparse
import zipfile
import shutil
import json
import os

from .utils import *



def downloadGB(iso, adm, base_dir):

    # Create the request URL
    url = "https://www.geoboundaries.org/gbRequest.html?ISO=" + iso + "&ADM=ADM" + adm
    print("Making request to: ", url)

    # Make the request to the URL
    r = requests.get(url)
    dlPath = r.json()[0]['downloadURL']
    print("Downloading data from: ", dlPath)
    
    # Get the download URL
    r = requests.get(r.json()[0]['downloadURL'], allow_redirects=True)

    # Make directory for downloaded zipfolder
    tmp_dir = makeGBdir(iso, base_dir)
    print("Downloading data into: ", tmp_dir)
    
    # Open the request and download the zipfolder
    open(os.path.join(tmp_dir, "temp.zip"), 'wb').write(r.content)

    # Open the downloaded zipfolder
    with zipfile.ZipFile(os.path.join(tmp_dir, "temp.zip"), 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)

    # Grab the name of the second zipfolder
    to_open = [i for i in os.listdir(tmp_dir) if i.endswith(".zip") and i.startswith('geo')]

    # Extract the files from the second zipfolder
    with zipfile.ZipFile(os.path.join(tmp_dir, to_open[0]), 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)
    
    # Clean up directory
    to_delete = [i for i in os.listdir(tmp_dir) if i.endswith(".zip") or i.startswith('geo')]
    for i in to_delete:
      os.remove(os.path.join(tmp_dir, i))
    
    print("Done downloading boundary data.")
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("iso", help="Country ISO")
    parser.add_argument("adm", help="ADM level")
    parser.add_argument("base_dir", help="Directory to download data into")
    args = parser.parse_args()

    downloadGB(args.iso, args.adm, args.base_dir)
from threading import Thread
import tkinter
from PIL import Image, ImageTk, ImageFont, ImageDraw
import time
from queue import Queue
from glob import glob
import os
import re
import math
from pathlib import Path

# TODO: change source of var.
DUMP_DIR = 'testing/dump/'
MAP_FILE = 'USMap.png'
MAPS_DIR = 'maps/'


# Obtains area maps in the US to overlay radar images on.
class AreaMap:
    # Max latitude of US map in a linear form.
    LAT_MAX = 1.0799224683069641
    # Reference latitude in linear form.
    REF_LAT = 0.7380009964270406

    def __init__(self):
        # Coordinates of area.
        self.lat1 = None
        self.lon1 = None
        self.lat2 = None
        self.lon2 = None
        # Area ID.
        self.area_id = None
        # The area map.
        self.map = None

    # Get map configuration information.
    def get_config(self):
        """

        :return: True if successful, False if not
        """
        # Look for any radar map config files.
        files = glob(os.path.abspath(DUMP_DIR) + '/DWRI_*')
        if not files:
            return False
        # Extract info from first file.
        file = open(files[0], 'r')
        for line in file:
            if 'DWR_Area_ID' in line:
                self.area_id = re.findall(r'\"(.+?)\"', line)[0]
            elif 'Coordinates' in line:
                coords = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                self.lat1, self.lon1, self.lat2, self.lon2 = (float(x) for x in coords)
        return True

    # Render an area map from the US map.
    def render(self):
        # Open US map.
        us_map = Image.open(MAP_FILE)
        # Convert latitudes to a linear form.
        self.lat1 = AreaMap.LAT_MAX - math.asinh(math.tan(math.radians(self.lat1)))
        self.lat2 = AreaMap.LAT_MAX - math.asinh(math.tan(math.radians(self.lat2)))
        # Calculate x-coords using a ratio of a known location on the map.
        x1 = (self.lon1 + 130.781250) * 7162 / 39.34135
        x2 = (self.lon2 + 130.781250) * 7162 / 39.34135
        # Use another ratio of a known location to find the latitudes.
        den = AreaMap.LAT_MAX - AreaMap.REF_LAT
        y1 = self.lat1 * 3565 / den
        y2 = self.lat2 * 3565 / den
        # Crop the map.
        cropped = us_map.crop((
            int(x1),
            int(y1),
            int(x2),
            int(y2)
        ))
        # Resize to 900x900, convert to right format, and save.
        self.map = cropped.resize((900, 900))
        self.map = self.map.convert('RGBA')
        self.map.save(MAPS_DIR + self.area_id + '.png')

    # Get an area map for the predefined area.
    def get_map(self):
        # If already in memory, just return it.
        if self.map is not None:
            return self.map
        # Check if an area map has already been rendered.
        file = Path(MAPS_DIR + self.area_id + '.png')
        if file.is_file():
            # Open and return image.
            self.map = Image.open(file.absolute()).convert('RGBA')
            return self.map
        else:
            # Else, render it and return.
            self.render()
            return self.map

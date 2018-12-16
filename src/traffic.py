from threading import Thread
import tkinter
from PIL import Image, ImageTk, ImageFont, ImageDraw
import time
from queue import Queue
from glob import glob
import os
import os.path
from src.us_map import AreaMap
from datetime import datetime
import re
from . import DUMP, SAVES


# For processing traffic tiles.
class TrafficTile:
    def __init__(self, filename):
        self.filename = filename
        # x and y coordinates of tile in map.
        self.x = None
        self.y = None
        # The tile image.
        self.img = None
        # Load everything.
        self.load()

    # Get x and y coordinates (0 indexed).
    def get_xy(self):
        match = re.search('_([123])_([123])_', self.filename)
        self.x = int(match.group(2)) - 1
        self.y = int(match.group(1)) - 1

    # Get the tile image.
    def get_tile(self):
        self.img = Image.open(self.filename).convert('RGBA')

    # Load coordinates and tile image.
    def load(self):
        self.get_xy()
        self.get_tile()


# For processing traffic images.
class Traffic:
    def __init__(self, do_save=False, save_dir=SAVES):
        # The complete traffic map.
        self.map = Image.new('RGBA', (600, 600))
        # Keeps track of when all tiles are updated.
        self.tiles = [False] * 9
        # Whether or not maps should be saved.
        self.do_save = do_save
        # Save directory.
        self.save_dir = save_dir

    # Get a timestamp for right now.
    @staticmethod
    def timestamp():
        return datetime.now().strftime('%m-%d-%Y_%I-%M-%S_%p')

    # Save the map.
    def save(self):
        name = 'traffic_{0}.png'.format(self.timestamp())
        self.map.save(self.save_dir + name)
        # Reset update-tracking tiles.
        self.tiles = [False] * 9

    # Paste a tile on the map.
    def paste(self, tile):
        self.map.paste(tile.img, (tile.x * 200, tile.y * 200))
        # Show that tile was updated.
        self.tiles[tile.x + tile.y * 3] = True
        # Delete tile file.
        os.remove(tile.filename)

    # Load and paste any new tiles on the map.
    def update_tiles(self):
        # Get traffic tiles.
        files = glob(os.path.abspath(DUMP) + '/TMT_*')
        tiles = [TrafficTile(x) for x in files]
        # If no new tiles, nothing to be updated.
        if not tiles:
            return False
        # Paste tiles on the map.
        for tile in tiles:
            self.paste(tile)
        # Save if specified and all tiles are updated.
        if self.do_save and False not in self.tiles:
            self.save()
        return True

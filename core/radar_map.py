from threading import Thread
import tkinter
from PIL import Image, ImageTk, ImageFont, ImageDraw
import time
from queue import Queue
from glob import glob
import os
import os.path
from core.us_map import AreaMap
from datetime import datetime

# TODO: change.
DUMP_DIR = 'testing/dump/'
FONT = 'font/GlacialIndifference-Regular.otf'
RADAR_DIR = 'saves/'


# For managing received radar overlays.
class RadarMap:
    us_map: AreaMap

    def __init__(self, us_map, do_save=False):
        # File name of current overlay.
        self.filename = ''
        self.overlay = None
        self.us_map = us_map
        # Map with overlay.
        self.radar = None
        # Whether radar images should be saved.
        self.do_save = do_save

    # Get a timestamp for right now.
    @staticmethod
    def timestamp():
        return datetime.now().strftime('%m-%d-%Y_%I-%M-%S_%p')

    # Put timestamp on radar image.
    def stamp(self):
        # Write timestamp in bottom right corner.
        font = ImageFont.truetype(FONT, 25)
        draw = ImageDraw.Draw(self.radar)
        draw.text((550, 835), self.timestamp(), font=font, fill='black')

    # Save radar image.
    def save(self):
        name = 'radar_{0}.png'.format(self.timestamp())
        self.radar.save(RADAR_DIR + name)

    # Update the current map overlay.
    def update_overlay(self):
        """

        :return: True if updated, False if not
        """
        # Get any overlays new overlays.
        files = glob(os.path.abspath(DUMP_DIR) + '/DWRO_*')
        new_files = [x for x in files if os.path.basename(x) != self.filename]
        # If there are none, exit.
        if not new_files:
            return False
        # Update using the first new overlay.
        self.overlay = Image.open(new_files[0]).convert('RGBA')
        self.overlay = self.overlay.resize((900, 900))
        # Combine map and overlay.
        self.radar = Image.alpha_composite(
            self.us_map.get_map(),
            self.overlay
        )
        # Timestamp the radar.
        self.timestamp()
        # Update overlay filename.
        self.filename = os.path.basename(new_files[0])
        # Save file if necessary.
        if self.do_save:
            self.save()
        # Delete all overlays.
        for file in files:
            os.remove(file)
        return True

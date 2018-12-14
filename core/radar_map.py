from threading import Thread
import tkinter
from PIL import Image, ImageTk, ImageFont, ImageDraw
import time
from queue import Queue
from glob import glob
import os

# TODO: change.
DUMP_DIR = 'testing/dump/'


# For managing received radar overlays.
class RadarMap:
    def __init__(self):
        self.overlay = None

    # Update the current map overlay.
    def update_overlay(self):
        """

        :return: True if updated, False if not
        """
        # Get any overlays.
        files = glob(os.path.abspath(DUMP_DIR) + '/DWRO_*')
        # If there are none, exit.
        if not files:
            return False
        # If there are no new files, exit.
        if len((x for x in files if )):
        # TODO: finish.

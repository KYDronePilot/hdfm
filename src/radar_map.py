import os
import os.path
from datetime import datetime
from glob import glob

from PIL import Image, ImageFont, ImageDraw

from src.us_map import AreaMap
from . import DUMP, FONT, SAVES


# For managing received radar overlays.
class RadarMap:
    def __init__(self, area_map, do_save=False, save_dir=SAVES):
        # File name of current overlay.
        self.filename = ''
        self.overlay = None
        self.area_map = area_map
        # Map with overlay.
        self.img = None
        # Whether radar images should be saved.
        self.do_save = do_save
        # Save directory.
        self.save_dir = save_dir

    # Get a timestamp for right now.
    @staticmethod
    def timestamp():
        return datetime.now().strftime('%m-%d-%Y_%I-%M-%S_%p')

    # Put timestamp on radar image.
    def stamp(self):
        # Write timestamp in bottom right corner.
        font = ImageFont.truetype(FONT, 25)
        draw = ImageDraw.Draw(self.img)
        draw.text((550, 835), self.timestamp(), font=font, fill='black')

    # Save radar image.
    def save(self):
        name = 'radar_{0}.png'.format(self.timestamp())
        self.img.save(os.path.join(self.save_dir, name))

    # Update the current map overlay.
    def update_overlay(self):
        """

        :return: True if updated, False if not
        """
        # If no config has been received, try to get one.
        if not self.area_map.has_config():
            rc = self.area_map.get_config()
            # If still no config, wait till later.
            if not rc:
                return False
        # Get any overlays new overlays.
        files = glob(os.path.join(DUMP, 'DWRO_*'))
        new_files = [x for x in files if os.path.basename(x) != self.filename]
        # If there are none, delete old ones and exit.
        if not new_files:
            for file in files:
                os.remove(file)
            return False
        # Update using the first new overlay.
        self.overlay = Image.open(new_files[0]).convert('RGBA')
        self.overlay = self.overlay.resize((900, 900))
        # Combine map and overlay.
        self.img = Image.alpha_composite(
            self.area_map.get_map(),
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

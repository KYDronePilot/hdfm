import os
import os.path
from datetime import datetime
from glob import glob

from PIL import Image

from . import DUMP, SAVES


# For managing album/station
class Artwork:
    def __init__(self, do_save=False, save_dir=SAVES):
        # Artwork saving information.
        self.do_save = do_save
        self.save_dir = save_dir
        # Current artwork image.
        self.img = None

    # Get a timestamp for right now.
    @staticmethod
    def timestamp():
        return datetime.now().strftime('%m-%d-%Y_%I-%M-%S_%p')

    # Save artwork.
    def save(self):
        name = 'artwork_{0}.png'.format(self.timestamp())
        self.img.save(self.save_dir + name)

    # Delete artwork files.
    @staticmethod
    def delete_artwork():
        files = glob(DUMP + '*')
        art_files = [x for x in files if x.endswith('.jpg')]
        for art_file in art_files:
            os.remove(art_file)

    # Update artwork.
    def update(self):
        # Get any artwork files.
        files = glob(DUMP + '*')
        art_files = [x for x in files if x.endswith('.jpg')]
        # If no new art, exit.
        if not art_files:
            return False
        # Update to last file.
        self.img = Image.open(art_files[0]).convert('RGBA')
        # If set, save artwork.
        if self.do_save:
            self.save()
        # Delete all other artwork.
        for file in art_files:
            os.remove(file)
        return True

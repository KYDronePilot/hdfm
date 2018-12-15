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
import re
import subprocess

# TODO: change.
DUMP_DIR = 'testing/dump/'
FONT = 'font/GlacialIndifference-Regular.otf'
SAVES = 'saves/'
# Help message.
HELP = """\
Usage:  [OPTIONS]  frequency

Option        Meaning
 -h, --help    Show this message
 -c <channel>  HDFM channel, for stations with subchannels (default = 1)
 -p <ppm>      PPM error correction (default = 0)
 -s <dir>      Directory to do_save weather and traffic images to (default = none)
 -l <1-3>      Log level output from nrsc5 (default = 3, only debug info)
 -a <null>     Display album/station art
"""


# NRSC5 management.
class NRSC5(Thread):
    def __init__(self):
        super().__init__()
        self.channel = 0
        self.ppm = 0
        self.log = 3
        self.freq = 100.0
        self.dump_dir = DUMP_DIR
        # Command/arg list.
        self.cmd_args = None

    # Format command/argument list.
    def format_cmd(self):
        return [
            'nrsc5',
            '-l',
            self.log,
            '-p',
            self.ppm,
            '--dump-aas-files',
            self.dump_dir,
            self.freq,
            self.channel
        ]

    # Run the command.
    def run(self):
        subprocess.call(self.cmd_args)


# User interface management (CLI).
class UserInterface:
    nrsc5: NRSC5

    def __init__(self, nrsc5):
        # NRSC5 management object.
        self.nrsc5 = nrsc5
        # Operations for each command line option.
        option_map = {
            '-c': self.channel,
            '-p': self.ppm,
            '-l': self.log,
            '-a': self.art_set,
            '-s': self.save_dir_set
        }
        # Whether album art should be displayed.
        self.art = False
        # Directory where weather/traffic maps should be saved.
        self.save_dir = SAVES

    # Print help.
    @staticmethod
    def help():
        print(HELP)

    # Add channel argument to NRSC5 args.
    def channel(self, arg):
        # Validate channel.
        channel = int(arg)
        if channel < 0 or channel > 3:
            print('Error: Invalid channel (0 - 3)')
            return False
        # Set NRSC5 arg.
        self.nrsc5.channel = channel
        return True

    # Handle ppm argument.
    def ppm(self, arg):
        self.nrsc5.ppm = int(arg)
        return True

    # Handle log level arg.
    def log(self, arg):
        # Validate input.
        level = int(arg)
        if level < 1 or level > 3:
            print('Error: Invalid log level (1 - 3)')
            return False
        self.nrsc5.log = level
        return True

    # Set save directory.
    def save_dir_set(self, arg):
        # Validate directory.
        if not os.path.isdir(arg):
            print('Error: Invalid directory')
            return False
        self.save_dir = arg
        return True

    # Set whether or not album art should be saved.
    def art_set(self, arg):
        # Validate input.
        arg = arg.lower()
        if arg != 'y' and arg != 'n':
            print('Error: -a argument invalid (y|n)')
            return False
        # Handle the arg.
        self.art = True if arg == 'y' else False
        return True

    # Process arguments inputted to the main script.
    def process(self, args):
        pass



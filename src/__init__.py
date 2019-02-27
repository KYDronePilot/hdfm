import os.path
from os.path import dirname, abspath


# Directory of module.
DIR = dirname(dirname(abspath(__file__)))
# Paths to files in this project.
FONT = os.path.join(DIR, 'font', 'GlacialIndifference-Regular.otf')
SAVES = os.path.join(DIR, 'saves')
DUMP = os.path.join(DIR, 'dump')
MAPS = os.path.join(DIR, 'maps')
MAP_FILE = os.path.join(MAPS, 'us_map.png')

# Debug: FIXME.
print('Project dir: ', DIR)
print('Font file: ', FONT)
print('Saves dir: ', SAVES)
print('Dump dir: ', DUMP)
print('Maps dir: ', MAPS)
print('Map file: ', MAP_FILE)

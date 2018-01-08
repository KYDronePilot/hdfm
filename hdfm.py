# This program uses nrsc5 (developed by Theori, http://www.theori.io/) to
# display weather and traffic maps recieved from HDFM stations.
# See README for more info.

from PIL import Image, ImageTk, ImageFont, ImageDraw  # For image manipulation.
try: # For opening a weather and traffic gui/display.
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import os  # For multiple system operations.
import glob  # For finding files in a directory.
import re  # For getting coordinates from weather config file.
import math  # For converting earth coordinates to pixel coordinates.
import subprocess  # For calling nrsc5.
import threading  # For running nrsc5 as a thread in the backround.
import sys  # For args and exiting the program.
import time  # For delays.
import datetime  # For timestamps.

# Included font for weather map timestamp.
font_dir = "./GlacialIndifference-Regular.otf"
# Included OSM map of the US.
usmap_dir = "./USMap.png"

# Set the dump directory to "Dump" in the same directory as this script.
dump_dir = "./Dump"

# Create a dump directory if one does not exist in the same directory as this
# script.
if not os.path.exists(dump_dir):
    os.makedirs(dump_dir)

# For checking if a recieved weather overlay is updated or just a repeat.
prev_weather_file = ""

# Prevents the traffic display from updating unless a new tile has been
# recieved.
traffic_id = 1

# Ensures the getUSMap function will run only once.
map_onetime = 1


# Returns a string with the help info below when called.
def printHelp():
    return("""Usage:  [OPTIONS]  frequency

Option        Meaning
 -h, --help    Show this message
 -c <channel>  HDFM channel, for stations with subchannels (default = 1)
 -p <ppm>      PPM error correction (default = 0)
 -s <dir>      Directory to save weather and traffic images to (default = none)
 -l <1-3>      Log level output from nrsc5 (default = 3, only debug info)
 -a <null>     Display album/station art\n""")


# Starts nrsc5, the core behind nrscdec program. Takes variables for the dump
# directory, frequency, HDFM channel, ppm correction, and log level.
def startNRSC5(dump_dir, freq, channel, ppm, log_level):
    subprocess.call(["nrsc5", "-l", log_level, "-p", ppm,
                     "--dump-aas-files", dump_dir, freq, channel])


# Takes coordinates from the weather config and returns a map of the area
# between those coordinate bounds.
def getUSMap(lat1, lon1, lat2, lon2):
    # Open HiRes openstreetmap of the US.
    US_map = Image.open(usmap_dir)

    # Convert top latitude bound of HiRes US map to a linear form, since
    # latitudinal lines on a mercator map increase exponentially.
    y_top_coord = math.asinh(math.tan(math.radians(52.482780)))

    # Convert top and bottom bound of weather map to the same linear form
    # described above.
    lat1 = y_top_coord - math.asinh(math.tan(math.radians(lat1)))
    lat2 = y_top_coord - math.asinh(math.tan(math.radians(lat2)))

    # Zero out longitudes by adding the leftmost longitude of the HiRes map and
    # use a ratio of a know longitude and pixel x-value the get the pixel
    # coordinates of the left and right map bounds. Since longitude is linear
    # on a mercator map, the above process is unnecessary.
    pixel_x1 = (lon1 + 130.781250) * 7162 / 39.34135
    pixel_x2 = (lon2 + 130.781250) * 7162 / 39.34135

    # Use ratio of a known latitude and pixel y-value to calculate the top and
    # bottom pixel coordinates.
    pixel_y1 = lat1 * 3565 / (y_top_coord -
                              math.asinh(math.tan(math.radians(38.898))))
    pixel_y2 = lat2 * 3565 / (y_top_coord -
                              math.asinh(math.tan(math.radians(38.898))))

    # Crop the HiRes US map to the converted map coordinate bounds.
    cropped_map = US_map.crop((int(pixel_x1), int(pixel_y1),
                               int(pixel_x2), int(pixel_y2)))

    # Resize the cropped map to a resonable 900x900 image.
    cropped_map.resize((900, 900))

    # Return the cropped map.
    return cropped_map


# Checks the weather configuration file sent by the radio station and extracts
# coordinate bounds.
def checkWeatherConf():
    # Initialize list to hold all four coordinate bounds.
    coords = []
    # Search through every file in the dump directory and find any that start
    # with the config file prefix "DWRI".
    for file in glob.glob(os.path.abspath(dump_dir) + '/DWRI_*'):
        file = open(file, 'r')
        for line in file:
            # Once we find the line of text with the coordinates, use regex to
            # extract coordinate bounds.
            if 'Coordinates=' in line:
                coords = re.findall(r"[-+]?\d*\.\d+|\d+", line)
    # Return coordinate bounds as a list. If none found, return empty list "[]"
    return coords


# Returns a cropped area map using the checkWeatherConf and getUSMap functions.
def getCroppedMap():
    # Crop an area map from the HiRes map only once and then store it to a
    # variable that can be used multiple times without opening the HiRes image
    # over and over again.
    global map_onetime
    if map_onetime == 1:
        # Retrieve coordinate bounds using checkWeatherConf funtion.
        coords = checkWeatherConf()
        # If no coordinates can be retrieved, set the map image to a blank
        # white backround
        if coords == []:
            cropped_map = Image.new("RGBA", (900, 900))
        else:
            # Get a map of the area specified in the recieved weather config
            # file.
            cropped_map = getUSMap(float(coords[0]), float(coords[1]),
                                   float(coords[2]), float(coords[3]))
            # Make sure the above code is only run once.
            map_onetime = 0

        # Set area_map to the local map backround and return the said image.
        global area_map
        area_map = cropped_map.convert("RGBA")

    return area_map

# Initialize variables to hold command line arguments to be passed to nrsc5.
channel = "0"
ppm = "0"
save = ""
log_level = "3"
art_boo = False

# If no arguments are entered, print the help page.
if len(sys.argv) == 1:
    sys.exit(printHelp())

# Iterate through each entered argument, assigning any option values to their
# respective variables.
for arg in range(len(sys.argv)):
    if sys.argv[arg] == "-c":
        channel = sys.argv[arg + 1]
    elif sys.argv[arg] == "-p":
        ppm = sys.argv[arg + 1]
    elif sys.argv[arg] == "-s":
        save = sys.argv[arg + 1]
    elif sys.argv[arg] == "-l":
        log_level = sys.argv[arg + 1]
    elif sys.argv[arg] == "-h" or sys.argv[arg] == "--help":
        sys.exit(printHelp())
    elif sys.argv[arg] == "-a":
        art_boo = True

# Assign last arg to the frequency of the HDFM station.
freq = sys.argv[len(sys.argv) - 1]

# Ensure the last arg is actually a float.
try:
    float(freq)
except ValueError:
    sys.exit("Please enter a frequency")

# Ensure frequency is within the US FM spectrum limits.
if float(freq) < 88 or float(freq) > 108:
    sys.exit("Frequency is out of range!")

# Initialize weather gui/display.
weather = tk.Tk()
weather.title("HDFM Weather Map")
weather_final = Image.new("RGBA", (900, 900))
weather_display = ImageTk.PhotoImage(weather_final)
weather_label = tk.Label(weather, image=weather_display)
weather_label.pack()
weather.update()

# Initialize traffic gui/display.
traffic = tk.Toplevel()
traffic.title("HDFM Traffic Map")
traffic_final = Image.new("RGBA", (600, 600))
traffic_display = ImageTk.PhotoImage(traffic_final)
traffic_label = tk.Label(traffic, image=traffic_display)
traffic_label.pack()
traffic.update()

# Initialize album/station art window if specified.
if art_boo == True:
    art = tk.Toplevel()
    art.title("HDFM Art")
    art_image = Image.new("RGBA", (200, 200))
    art_display = ImageTk.PhotoImage(art_image)
    art_label = tk.Label(art, image=art_display)
    art_label.pack()
    art.update()

# Start a thread for nrsc5, so that when this script is stopped, nrsc5 is
# stopped as well.
nrsc_thread = threading.Thread(target=startNRSC5,
                               args=(dump_dir, freq, channel, ppm, log_level))
nrsc_thread.start()

# Used to keep track of when all the traffic tiles are updated.
traffic_save_check = [0] * 9

while True:
    # Looks for new weather overlays and updates the weather display when
    # necessary.
    for file in glob.glob(os.path.abspath(dump_dir) + '/DWRO_*'):
        # Since the radio sends repeat overlays, only update when the overlay
        # name is different, and thus new.
        if file != prev_weather_file:
            # Update the name of the last recieved overlay to the current one.
            prev_weather_file = file
            # Retrieve a map to paste the overlay on.
            US_map = getCroppedMap()
            # Open the overlay.
            radar_overlay = Image.open(file).convert("RGBA")
            # Combine the overlay and map.
            weather_final = Image.alpha_composite(
                US_map.resize((900, 900)),
                radar_overlay.resize((900, 900))
            )
            # Get the current time (for a timestamp).
            t = datetime.datetime.now().strftime("%m-%d-%Y %I-%M-%S %p")
            # Add timestamp to the map with overlay.
            font = ImageFont.truetype(font_dir, 25)
            draw = ImageDraw.Draw(weather_final)
            draw.text((550, 835), t, font=font, fill='black')
            # Update the weather display.
            weather_display = ImageTk.PhotoImage(weather_final)
            weather_label.configure(image=weather_display)
            weather.update()
            # If the save option was used, save the weather image.
            if save != "":
                weather_final.save(os.path.abspath(save) +
                                   "/Weather Map " + t + ".png")
        # Remove the already processed overlay.
        os.remove(file)

    # Finds the recieved traffic tiles and pastes them in their proper position
    # on a final traffic image.
    for tile_path in glob.glob(os.path.abspath(dump_dir) + '/TMT_*'):
        # Based on each tile's name, paste them in the right spot on the final
        # image and update the list that checks if all tiles have been updated.
        match = re.search('_([123])_([123])_', tile_path)
        if match:
            # Retrieve zero indexed tile coordinates from file name.
            x = int(match.group(2)) - 1
            y = int(match.group(1)) - 1
            # Open traffic tile.
            tile_image = Image.open(tile_path).convert("RGBA")
            # Paste tile on main traffic image at coordinates obtained above
            # times dimensions of tiles (200x200).
            traffic_final.paste(tile_image, (x * 200, y * 200))
            # Update save check list to 1 for address of identifying number of
            # tile just pasted (0-8).
            traffic_save_check[x + y*3] = 1
        # Prevents the display from updating unless a tile has been updated.
        traffic_id = 1
        # Remove tile after it has been processed.
        os.remove(tile_path)

    # If a save directory has been selected and all tiles have been updated,
    # save a composite traffic image.
    if save != "":
        if traffic_save_check == [1] * 9:
            t = datetime.datetime.now().strftime("%m-%d-%Y %I-%M-%S %p")
            traffic_final.save(os.path.abspath(save) +
                               "/Traffic Map " + t + ".png")
            # Reset the tile update tracker.
            traffic_save_check = [0] * 9

    # Update traffic display only if tile has been updated.
    if traffic_id == 1:
        traffic_id = 0
        traffic_display = ImageTk.PhotoImage(traffic_final)
        traffic_label.configure(image=traffic_display)
        traffic.update()
    
    # If art option specified, check for new files and update art display.
    if art_boo == True:
        for art_path in glob.glob(os.path.abspath(dump_dir) + "/*"):
            # In case save dir is same as dump dir.
            if not art_path.endswith("M.png"):
                # Only acknowledge files with .png and .jpg extensions.
                if art_path.endswith(".png") or art_path.endswith(".jpg"):
                    # Open art image file and update display.
                    art_image = Image.open(art_path).convert("RGBA")
                    art_display = ImageTk.PhotoImage(art_image)
                    art_label.configure(image=art_display)
                    art.update()
                    # Remove art file after updating.
                    os.remove(art_path)

    # Delay for 0.5 seconds before looking for new traffic and weather data.
    time.sleep(0.5)

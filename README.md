**hdfm** displays weather and traffic maps received from iHeartRadio HD radio stations. It relies on nrsc5 to decode and dump the radio station data for it to process and display.

This is my first major python project and I only have about 3 months of experience so forgive me if I made any mistakes. This program is designed for rtl-sdr enthusiasts or possibly people who want to put a navigation system in their vehicle. There are lots of things that need to be improved, namely audio. When run on a mac, the audio seems to work fine, but this will likely be different on a linux os. So far, I've successfully tested it with 2 different iHeartRadio stations, but you may run across some that it won't work with. Keep in mind, this will NOT work anything other than iHeartRadio HD stations. If you have any issues, please post them and I'll get back as soon as possible.

### Packages

The only required package other than python is nrsc5, developed by Theori http://www.theori.io

 * Installation instructions can be found at https://github.com/theori-io/nrsc5

### Libraries

The following python libraries are required and will need to be installed (pip install 'library'):

 * Tkinter
 * ImageTk
 * Pillow (PIL, Python Imaging Library)

The following python libraries are required, but most likely already installed.

 * os
 * glob
 * re
 * math
 * subprocess
 * threading
 * sys
 * time
 * datetime

## Requirements

An RTL-SDR dongle must be plugged in for this program to function properly.

### Usage:

	Usage:  [OPTIONS]  frequency
	
     Option              Meaning
     -h, --help          Show this message
     -c <channel>        HDFM channel, for stations with subchannels (default = 0)
     -p <ppm>            PPM error correction (default = 0)
     -s <dir>            Directory to save weather and traffic images to (default = none)
     -l <1-3>            Log level output from nrsc5 (default = 3, only debug info)
### Examples:

Tune to 104.5 MHz:

     $ python ./hdfm.py 104.5

Tune to 104.5 MHz and save all recieved maps to ./Recieved Maps/:

     $ python ./hdfm.py -s ./Recieved\ Maps/ 104.5

Tune to 104.5 MHz, set the ppm correction to 48, and decode HD channel 2 (HD2)

     $ python ./hdfm.py -p 48 -c 1 104.5

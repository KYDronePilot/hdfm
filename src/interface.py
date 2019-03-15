import os
import os.path

from . import SAVES

# Help message.
HELP = """\
Usage:  [OPTIONS]  frequency

Option        Meaning
 -h, --help    Show this message
 -c <program>  HD Radio program, for stations with subchannels (default = 0)
 -p <ppm>      PPM error correction (default = 0)
 -s <dir>      Directory to do_save weather and traffic images to (default = none)
 -l <null>     Show logging information
 -a <null>     Display album/station art
"""


# User interface management (CLI).
class UserInterface:
    # Halt program status code.
    HALT = 1
    # Success code.
    SUCCESS = 0

    def __init__(self, nrsc5):
        # NRSC5 management object.
        self.nrsc5 = nrsc5
        # Operations for each command line option.
        self.option_map = {
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
        self.do_save = False

    # Print help.
    @staticmethod
    def help():
        print(HELP)

    # Determine whether a string represents an integer.
    @staticmethod
    def repr_int(val):
        try:
            int(val)
            return True
        except ValueError:
            return False

    # Determine whether a string represents a float.
    @staticmethod
    def repr_float(val):
        try:
            float(val)
            return True
        except ValueError:
            return False

    # Add channel argument to NRSC5 args.
    def channel(self, arg):
        # Validate channel.
        if not UserInterface.repr_int(arg):
            print('Error: Invalid channel (0 - 3)')
            return False
        channel = int(arg)
        if channel < 0 or channel > 3:
            print('Error: Invalid channel (0 - 3)')
            return False
        # Set NRSC5 arg.
        self.nrsc5.channel = channel
        return True

    # Process frequency.
    def frequency(self, arg):
        # Validate.
        if not UserInterface.repr_float(arg):
            print('Error: Invalid frequency')
            return False
        freq = float(arg)
        if freq < 88 or freq > 108:
            print('Error: Frequency out of range (88.0 - 108.0)')
            return False
        self.nrsc5.freq = freq
        return True

    # Handle ppm argument.
    def ppm(self, arg):
        # Validate.
        if not UserInterface.repr_int(arg):
            print('Error: Invalid PPM argument')
            return False
        self.nrsc5.ppm = int(arg)
        return True

    # Set whether or not logging should be displayed.
    def log(self, arg):
        # Handle the arg.
        self.nrsc5.logging = True
        return True

    # Set save directory.
    def save_dir_set(self, arg):
        # Validate directory.
        if not os.path.isdir(arg):
            print('Error: Invalid directory')
            return False
        self.save_dir = os.path.join(os.path.abspath(arg), '/')
        self.do_save = True
        return True

    # Set whether or not album art should be saved.
    def art_set(self, arg):
        # Handle the arg.
        self.art = True
        return True

    # Process arguments inputted to the main script.
    def process(self, args):
        # Print help and exit if in args.
        if '-h' in args or '--help' in args:
            self.help()
            return self.HALT
        # Handle no args.
        if len(args) == 1:
            print('Error: No frequency specified')
            return self.HALT
        # Process last argument, which should be the frequency, exiting if there is an error.
        rc = self.frequency(args[-1])
        if not rc:
            return self.HALT
        # Process all args other.
        length = len(args)
        for i in range(length):
            # Handle empty flag.
            if args[i] == '-':
                print('Error: empty flag "-"')
                return self.HALT
            if args[i][0] != '-':
                continue
            # Do not process a flag at the end (should be frequency).
            if i < length - 1:
                rc = self.option_map[args[i]](args[i + 1])
                if not rc:
                    return self.HALT
        return self.SUCCESS

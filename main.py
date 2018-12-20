import sys

import src.gui
from src import interface
from src.artwork import Artwork
from src.gui import ArtworkDisplay
from src.gui import RadarDisplay
from src.gui import TrafficDisplay
from src.radar_map import RadarMap
from src.traffic import Traffic
from src.us_map import AreaMap


# Main class.
class Main:
    def __init__(self):
        # Management objects for NRSC5 and this program.
        self.nrsc5 = src.gui.NRSC5(self.stop)
        self.ui = interface.UserInterface(self.nrsc5)
        # Process arguments.
        rc = self.ui.process(sys.argv)
        # If argument error, exit.
        if rc:
            sys.exit()
        # Management objects for key components.
        self.area_map = AreaMap()
        self.radar = RadarMap(
            self.area_map,
            do_save=self.ui.do_save,
            save_dir=self.ui.save_dir
        )
        self.traffic = Traffic(
            do_save=self.ui.do_save,
            save_dir=self.ui.save_dir
        )
        # Display management objects.
        self.radar_disp = RadarDisplay(self.radar, self.stop)
        self.traffic_disp = TrafficDisplay(self.traffic, self.stop)
        # Handle artwork feature.
        self.artwork = None
        self.artwork_display = None
        # Set up if specified.
        if self.ui.art:
            self.setup_artwork()
        # Else, make NRSC5 instance delete artwork.
        else:
            self.nrsc5.artwork_del = Artwork.delete_artwork

    # Setup artwork feature.
    def setup_artwork(self):
        self.artwork = Artwork(
            do_save=self.ui.do_save,
            save_dir=self.ui.save_dir
        )
        self.artwork_display = ArtworkDisplay(self.artwork, self.stop)

    # Exit program.
    def stop(self):
        # Stop NBSR, NRSC5, and exit.
        self.nrsc5.nbsr.terminate()
        self.nrsc5.proc.terminate()
        self.nrsc5.quit()
        print('Exiting')

    # Run program.
    def run(self):
        # Start NRSC5.
        self.nrsc5.run()
        # Start display loop, handling exit.
        try:
            self.nrsc5.mainloop()
        except KeyboardInterrupt:
            # Stop important components.
            self.stop()


if __name__ == '__main__':
    # Start program.
    main = Main()
    main.run()

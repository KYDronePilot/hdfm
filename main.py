import sys

from src.us_map import AreaMap
from src.radar_map import RadarMap
from src.traffic import Traffic
from src import interface
from src.gui import RadarDisplay
from src.gui import TrafficDisplay


if __name__ == '__main__':
    # Management objects for NRSC5 and this program.
    nrsc5 = interface.NRSC5()
    ui = interface.UserInterface(nrsc5)
    # Process arguments.
    ui.process(sys.argv)
    # Management objects for key components.
    area_map = AreaMap()
    radar = RadarMap(area_map, do_save=ui.do_save, save_dir=ui.save_dir)
    traffic = Traffic(do_save=ui.do_save, save_dir=ui.save_dir)
    # Display management objects.
    radar_disp = RadarDisplay(radar)
    traffic_disp = TrafficDisplay(traffic)
    # Start NRSC5 thread.
    nrsc5.start()
    # Begin displaying.
    radar_disp.mainloop()
    pass



"""
Temporary module for designing new UI.
"""

import tkinter
from glob import glob
from pathlib import Path
from tkinter import ttk
from typing import Any, Optional, ClassVar, List, Callable

from PIL import Image, ImageTk
from PIL.Image import Image as ImageType

from artwork import ArtworkManager
from consts import FM_FREQUENCIES
from radar_map import DopplerRadarManager
from traffic import TrafficMapManager, TrafficTile
from config import static_config, user_config
from map_manager import MapManager
from nrsc5 import NRSC5Program, LogParserQueue

# from map_manager import MapManager
from utils import get_all_gain_levels


class ImagePanel(tkinter.Label):
    """
    Panel for displaying images.

    Attributes:
        _original_image: The original image currently being displayed (no resizing)
        _current_image: The current image being displayed, with potential resizing
        _tk_image: Tkinter photo image instance currently being displayed
        prev_event_w: Width from the previous size change event
        prev_event_h: Height from the previous size change event
    """

    _original_image: ImageType
    _current_image: ImageType
    _tk_image: ImageTk.PhotoImage
    prev_event_w: int
    prev_event_h: int

    def __init__(self, master, dimensions: (int, int)):
        super().__init__(master)
        self._current_image = Image.new('RGBA', dimensions)
        self.image = Image.new('RGBA', dimensions)
        self.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        # Reload image now that panel is packed
        self.reload_image()
        # Resize event handler.
        self.bind('<Configure>', self._resize_image)
        self.prev_event_w = 0
        self.prev_event_h = 0

    @property
    def image(self) -> ImageType:
        """
        Original image getter.

        Returns:
            Original version of image being displayed
        """
        return self._original_image

    @image.setter
    def image(self, image: ImageType):
        """
        Displayed image setter.
        Sets up the new image to display and reloads the panel.

        Args:
            image: New image to set
        """
        self._original_image = image.copy()
        self._current_image = self._original_image.resize(
            self._current_image.size, Image.ANTIALIAS
        )
        # Reload image on display
        self.reload_image()

    def reload_image(self):
        """
        Reload image that is displayed on the screen.
        """
        self._tk_image = ImageTk.PhotoImage(self._current_image)
        self.configure(image=self._tk_image)

    def _resize_image(self, event):
        """
        Image resize event handler.

        TODO: Resizing is not perfect by any means, but there are very few resources on how to do it properly.

        Args:
            event: Information about resize event
        """
        new_w = event.width
        new_h = event.height
        # Don't resize if dimensions haven't changed
        if new_w == self.prev_event_w and new_h == self.prev_event_h:
            return
        self.prev_event_w = new_w
        self.prev_event_h = new_h
        old_w, old_h = self._current_image.size
        # If dimensions match, nothing needs to be resized.
        if old_w == new_w or old_h == new_h:
            return
        # Difference in new and old dimensions.
        h_diff = abs(new_h - old_h)
        w_diff = abs(new_w - old_w)
        # Adjust either the new height or width to maintain image constraints.
        if h_diff > w_diff:
            new_w = (old_w * new_h) // old_h
        else:
            new_h = (old_h * new_w) // old_w
        # Resize
        self._current_image = self._original_image.resize(
            (new_w, new_h), Image.ANTIALIAS
        )
        self.reload_image()

    @property
    def screen_width(self) -> int:
        return self.winfo_screenwidth()

    @property
    def screen_height(self) -> int:
        return self.winfo_screenheight()

    @property
    def width(self) -> int:
        return self.winfo_width()

    @property
    def height(self) -> int:
        return self.winfo_height()


class State:
    """
    GUI state variables.
    """

    artist: tkinter.StringVar
    title: tkinter.StringVar
    slogan: tkinter.StringVar
    station_name: tkinter.StringVar
    audio_bit_rate: tkinter.StringVar
    # Settings
    frequency: tkinter.StringVar
    program: tkinter.StringVar
    gain: tkinter.StringVar
    ppm_error: tkinter.StringVar
    device: tkinter.StringVar

    def __init__(self):
        self.artist = tkinter.StringVar()
        self.title = tkinter.StringVar()
        self.slogan = tkinter.StringVar()
        self.station_name = tkinter.StringVar()
        self.audio_bit_rate = tkinter.StringVar()
        self.frequency = tkinter.StringVar()
        self.program = tkinter.StringVar()
        self.gain = tkinter.StringVar()
        self.gain = tkinter.StringVar(value=user_config.gain.get())
        self.ppm_error = tkinter.StringVar(value=user_config.ppm.get())
        self.device = tkinter.StringVar(value=user_config.device.get())

    def reset_info_vars(self):
        """
        Reset variables containing live station information.
        """
        self.artist.set('')
        self.title.set('')
        self.slogan.set('')
        self.station_name.set('')
        self.audio_bit_rate.set('')


class Controller:
    """
    Central manager of backend operations.

    Attributes:
        state_vars: UI state variables
        nrsc5: NRSC5 program execution manager
    """

    state_vars: State
    nrsc5: Optional[NRSC5Program]

    def __init__(self, state_vars: State):
        self.state_vars = state_vars
        self.nrsc5 = None


class Root(tkinter.Tk):
    """
    Root window, on which everything is built.

    Attributes:
        controller: Controller instance for managing operations
    """

    # Delay between event updates
    EVENT_UPDATE_INTERVAL: ClassVar[int] = 1000

    controller: Controller
    toolbar: Any
    tab_container: Any
    info_widget: Any
    station_settings_widget: 'StationSettingWidget'
    state_vars: State
    nrsc5: Optional[NRSC5Program]

    def __init__(self, title: str, width: int, height: int):
        super().__init__()
        self.title(title)
        self.aspect(220, 333, 220, 333)
        self.minsize(width=446, height=675)
        # TODO: Get rid of window positioning
        self.geometry(f'{width}x{height}+1000+300')
        self.state_vars = State()
        self.controller = Controller(self.state_vars)
        self.setup_components()
        self.nrsc5 = None
        # Schedule timed event handler
        self.after(str(self.EVENT_UPDATE_INTERVAL), self.update_event_handler)
        # Delete event handler
        self.protocol('WM_DELETE_WINDOW', self.stop)

    def stop(self):
        """
        Stop everything and close window.
        """
        if self.nrsc5 is not None:
            self.nrsc5.stop()
        self.destroy()

    def update_event_handler(self):
        """
        Event handler triggered at regular intervals to perform update tasks.
        """
        self.update_nrsc5_info()
        self.after(str(self.EVENT_UPDATE_INTERVAL), self.update_event_handler)

    def setup_components(self):
        """
        Setup components in root window.
        """
        self.toolbar = Toolbar(
            self, self.state_vars, self.handle_play_click, self.stop_nrsc5
        )
        self.tab_container = MainTabContainer(self, self.state_vars)
        self.station_settings_widget = StationSettingWidget(self, self.state_vars)
        self.station_settings_widget.pack(
            side=tkinter.TOP, padx=5, pady=5, fill=tkinter.X
        )
        self.info_widget = InfoWidget(self, self.state_vars)
        self.info_widget.pack(side=tkinter.TOP, padx=5, pady=5, fill=tkinter.X)

    @staticmethod
    def _update_var_from_parser_queue(q: LogParserQueue, var: tkinter.Variable):
        """
        Update tkinter variable from NRSC5 log parser queue.

        Args:
            q: Parser queue to get value from
            var: Variable to store information in
        """
        val = q.get_newest()
        if val is not None:
            var.set(val)

    def update_nrsc5_info(self):
        """
        Update info generated by NRSC5 program (station/track info, etc.).
        """
        # Exit if not running
        if self.nrsc5 is None:
            return
        self._update_var_from_parser_queue(
            self.nrsc5.log_parser.artist, self.state_vars.artist
        )
        self._update_var_from_parser_queue(
            self.nrsc5.log_parser.title, self.state_vars.title
        )
        self._update_var_from_parser_queue(
            self.nrsc5.log_parser.slogan, self.state_vars.slogan
        )
        self._update_var_from_parser_queue(
            self.nrsc5.log_parser.station_name, self.state_vars.station_name
        )
        self._update_var_from_parser_queue(
            self.nrsc5.log_parser.bit_rate, self.state_vars.audio_bit_rate
        )

    def start_nrsc5(self):
        """
        Event handler to start NRSC5 program.
        """
        self.nrsc5.config_dump_dir(static_config.dump_directory)
        self.nrsc5.start()

    def stop_nrsc5(self):
        """
        Stop NRSC5 program
        """
        # Do nothing if not already running
        if self.nrsc5 is None:
            return
        # Enable tuning fields
        self.station_settings_widget.set_visibility(True)
        self.nrsc5.stop()
        self.nrsc5 = None
        self.state_vars.reset_info_vars()

    def handle_play_click(self):
        """
        Handle click on play button.
        """
        # Ensure frequency and program are set
        if self.state_vars.frequency.get() == '' or self.state_vars.program.get() == '':
            return
        # Ensure settings are set
        if (
            self.state_vars.ppm_error.get() == ''
            or self.state_vars.device.get() == ''
            or self.state_vars.gain.get() == ''
        ):
            return
        # Disable tuning fields
        self.station_settings_widget.set_visibility(False)
        self.start_nrsc5()


class Toolbar(tkinter.Frame):
    """
    Toolbar in UI.
    """

    state_vars: State
    play_image: Any
    play_image_elem: Any
    play_button: Any
    stop_image: Any
    stop_image_elem: Any
    stop_button: Any
    sep1: Any
    gear_image: Any
    gear_image_elem: Any
    gear_button: Any

    def __init__(
        self, master: Root, state: State, play_handler: Callable, stop_handler: Callable
    ):
        super().__init__(master, bd=1, relief=tkinter.RAISED)
        self.pack(side=tkinter.TOP, fill=tkinter.X)
        self.state_vars = state
        # Play button
        self.play_image = Image.open('icons/play.png')
        self.play_image_elem = ImageTk.PhotoImage(self.play_image)
        self.play_button = tkinter.Button(
            self, image=self.play_image_elem, relief=tkinter.FLAT, command=play_handler
        )
        self.play_button.pack(side=tkinter.LEFT, padx=2, pady=2)
        # Stop button
        self.stop_image = Image.open('icons/stop.png')
        self.stop_image_elem = ImageTk.PhotoImage(self.stop_image)
        self.stop_button = tkinter.Button(
            self, image=self.stop_image_elem, relief=tkinter.FLAT, command=stop_handler
        )
        self.stop_button.pack(side=tkinter.LEFT, padx=2, pady=2)
        # Separator
        self.sep1 = ttk.Separator(self, orient=tkinter.VERTICAL)
        self.sep1.pack(side=tkinter.LEFT, padx=4, pady=3, fill=tkinter.Y)
        # Gear button
        self.gear_image = Image.open('icons/gear.png')
        self.gear_image_elem = ImageTk.PhotoImage(self.gear_image)
        self.gear_button = tkinter.Button(
            self, image=self.gear_image_elem, relief=tkinter.FLAT
        )
        self.gear_button.pack(side=tkinter.LEFT, padx=2, pady=2)


class MainTabContainer(ttk.Notebook):
    """
    Container for tabbed pages.
    """

    state_vars: State
    art_tab: 'AlbumArtFrame'
    info_tab: 'InfoFrame'
    settings_tab: 'SettingsFrame'
    radar_tab: 'RadarFrame'
    traffic_tab: 'TrafficFrame'

    def __init__(self, master: Root, state: State):
        super().__init__(master)
        self.pack(side=tkinter.TOP, padx=5, pady=5, fill=tkinter.X)
        self.state_vars = state
        # Art tab
        self.art_tab = AlbumArtFrame(self, self.state_vars)
        self.add(self.art_tab, text='Album Art')
        # Info tab
        self.info_tab = InfoFrame(self, self.state_vars)
        self.add(self.info_tab, text='Info')
        # Settings tab
        self.settings_tab = SettingsFrame(self, self.state_vars)
        self.add(self.settings_tab, text='Settings')
        # Radar tab
        self.radar_tab = RadarFrame(self, self.state_vars)
        self.add(self.radar_tab, text='Radar')
        # Traffic tab
        self.traffic_tab = TrafficFrame(self, self.state_vars)
        self.add(self.traffic_tab, text='Traffic')


class AlbumArtFrame(ttk.Frame):
    """
    Frame for displaying album art.
    """

    state_vars: State

    def __init__(self, master: MainTabContainer, state: State):
        super().__init__(master)
        self.state_vars = state


class InfoFrame(ttk.LabelFrame):
    """
    Frame for displaying Station info.
    """

    state_vars: State
    station_name: Any
    station_slogan: Any
    audio_bit_rate: Any
    sep1: Any

    def __init__(self, master: MainTabContainer, state: State):
        super().__init__(master, text='Station Info')
        self.state_vars = state
        self.pack()
        # Station name
        self.station_name = KeyValuePanel(self, 'Name', self.state_vars.station_name)
        self.station_name.pack(side=tkinter.TOP, fill=tkinter.X, pady=10, padx=10)
        # Station slogan
        self.station_slogan = KeyValuePanel(self, 'Slogan', self.state_vars.slogan)
        self.station_slogan.pack(side=tkinter.TOP, fill=tkinter.X, pady=10, padx=10)
        # Audio bit rate
        self.audio_bit_rate = KeyValuePanel(
            self, 'Bit Rate', self.state_vars.audio_bit_rate
        )
        self.audio_bit_rate.pack(side=tkinter.TOP, fill=tkinter.X, pady=10, padx=10)
        # Divider
        self.sep1 = ttk.Separator(self, orient=tkinter.HORIZONTAL)
        self.sep1.pack(side=tkinter.TOP, padx=4, pady=10, fill=tkinter.X)


class SettingsFrame(ttk.LabelFrame):
    """
    Frame for displaying settings.
    """

    state_vars: State
    gain: 'DropdownInput'
    ppm_error: 'DropdownInput'
    device: 'DropdownInput'
    submit_button: Any

    def __init__(self, master: MainTabContainer, state: State):
        super().__init__(master, text='Settings')
        self.state_vars = state
        # Gain input
        self.gain = DropdownInput(
            self,
            options=['auto'] + [str(gain) for gain in get_all_gain_levels()],
            label='Gain',
            input_var=self.state_vars.gain,
        )
        self.gain.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # PPM error input
        self.ppm_error = DropdownInput(
            self,
            options=[str(i) for i in range(-1000, 1001)],
            label='PPM Error Correction',
            input_var=self.state_vars.ppm_error,
        )
        self.ppm_error.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # Device input
        self.device = DropdownInput(
            self,
            options=[str(i) for i in range(0, 256)],
            label='Device Index',
            input_var=self.state_vars.device,
        )
        self.device.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # Submit button
        self.submit_button = ttk.Button(self, text='Save', command=self.save)
        self.submit_button.pack(padx=4, pady=10, anchor='w')

    def save(self):
        """
        Handle form save.
        """
        # Set config values
        user_config.gain.set(self.state_vars.gain.get())
        user_config.ppm.set(self.state_vars.ppm_error.get())
        user_config.device.set(self.state_vars.device.get())
        # Save it
        user_config.save()


class RadarFrame(ttk.LabelFrame):
    """
    Frame for displaying radar map.
    """

    state_vars: State

    def __init__(self, master, state: State):
        super().__init__(master, text='Radar Map')
        self.state_vars = state
        self.after(str(Root.EVENT_UPDATE_INTERVAL), self.update_event_handler)
        self.weather_panel = ImagePanel(self, (20, 20))
        self.map_manager = MapManager()
        self.radar_map_manager = DopplerRadarManager(self.map_manager)

    def update_event_handler(self):
        """
        Event handler triggered at regular intervals to perform update tasks.
        """
        # Reload map config
        self.map_manager.find_and_reload_config()
        # If it has a config, reload the radar
        if self.map_manager.has_config:
            self.radar_map_manager.update_radar_map()
            # If the radar map has an overlay, update the image displayed
            if self.radar_map_manager.has_overlay:
                self.weather_panel.image = self.radar_map_manager.radar_map
        self.after(str(Root.EVENT_UPDATE_INTERVAL), self.update_event_handler)


class TrafficFrame(ttk.LabelFrame):
    """
    Frame for displaying traffic map.
    """

    state_vars: State

    def __init__(self, master, state: State):
        super().__init__(master, text='Traffic Map')
        self.state_vars = state
        self.after(str(Root.EVENT_UPDATE_INTERVAL), self.update_event_handler)
        self.traffic_panel = ImagePanel(self, (50, 50))
        self.traffic_map_manager = TrafficMapManager()
        # self.traffic_panel.image = Image.open('/tmp/hdfm_dump/748_TMT_03g65g_1_2_20191227_2144_02ec.png')

    def update_event_handler(self):
        """
        Event handler triggered at regular intervals to perform update tasks.
        """
        # If more tiles get added, update image displayed in panel
        if self.traffic_map_manager.find_and_add_tiles():
            self.traffic_panel.image = self.traffic_map_manager.traffic_map
        self.after(str(Root.EVENT_UPDATE_INTERVAL), self.update_event_handler)


class SettingsInput(ttk.Frame):
    """
    Settings input item with label.
    """

    label: Any
    input_elem: tkinter.Entry
    input_var: tkinter.StringVar

    def __init__(self, master: Any, label: str, input_var: tkinter.StringVar):
        super().__init__(master)
        self.input_var = input_var
        # Label
        self.label = ttk.Label(self, text=f'{label}:', justify=tkinter.LEFT)
        self.label.pack(side=tkinter.TOP, anchor='w')
        # Input
        self.input_elem = ttk.Entry(self, textvariable=self.input_var)
        self.input_elem.pack(side=tkinter.TOP, anchor='w')

    def set_visibility(self, visible: bool):
        """
        Set visibility of field.

        Args:
            visible: Whether field is visible
        """
        self.input_elem.configure(state=tkinter.NORMAL if visible else tkinter.DISABLED)


class DropdownInput(ttk.Frame):
    """
    Dropdown input.
    """

    label: ttk.Label
    input_elem: tkinter.OptionMenu
    input_var: tkinter.StringVar
    options: List[str]

    def __init__(
        self,
        master: Any,
        options: List[str],
        label: str,
        input_var: tkinter.StringVar,
        default=None,
    ):
        super().__init__(master)
        self.input_var = input_var
        self.options = options
        # Label
        self.label = ttk.Label(self, text=f'{label}:', justify=tkinter.LEFT)
        self.label.pack(side=tkinter.TOP, anchor='w')
        # Input
        self.input_elem = ttk.OptionMenu(self, self.input_var, default, *self.options)
        self.input_elem.pack(side=tkinter.TOP, anchor='w')

    def set_visibility(self, visible: bool):
        """
        Set visibility of field.

        Args:
            visible: Whether field is visible
        """
        self.input_elem.configure(state=tkinter.NORMAL if visible else tkinter.DISABLED)


class KeyValuePanel(ttk.Frame):
    """
    Panel for displaying "key: value" information.
    """

    label: Any
    value: Any
    value_var: tkinter.StringVar

    def __init__(self, master: Any, label: str, value: tkinter.StringVar):
        super().__init__(master)
        self.value_var = value
        # Label
        self.label = ttk.Label(self, text=f'{label}:', justify=tkinter.LEFT)
        self.label.pack(side=tkinter.LEFT)
        # Value
        self.value = ttk.Label(self, textvariable=value, justify=tkinter.LEFT)
        self.value.pack(side=tkinter.LEFT)


class StationSettingWidget(ttk.LabelFrame):
    """
    Widget for setting the current radio station to tune to.
    """

    state_vars: State
    frequency: DropdownInput
    program: DropdownInput

    def __init__(self, master: Root, state: State):
        super().__init__(master, text='Tune Station')
        self.state_vars = state
        # Frequency input
        self.frequency = DropdownInput(
            self,
            options=[str(freq) for freq in FM_FREQUENCIES],
            label='Frequency',
            input_var=self.state_vars.frequency,
        )
        self.frequency.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # Program input
        self.program = DropdownInput(
            self,
            options=[str(i) for i in range(1, 5)],
            label='Program',
            input_var=self.state_vars.program,
        )
        self.program.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')

    def set_visibility(self, visible: bool):
        """
        Set visibility of fields.

        Args:
            visible: Whether the fields are visible
        """
        self.frequency.set_visibility(visible)
        self.program.set_visibility(visible)


class InfoWidget(ttk.LabelFrame):
    """
    Live info always displayed at bottom of window.
    """

    state_vars: State
    title: Any
    artist: Any
    station_name: Any

    def __init__(self, master: Root, state: State):
        super().__init__(master, text='Info')
        self.state_vars = state
        # Title
        self.title = KeyValuePanel(self, 'Title', self.state_vars.title)
        self.title.pack(side=tkinter.TOP, fill=tkinter.X, pady=10, padx=10)
        # Artist
        self.artist = KeyValuePanel(self, 'Artist', self.state_vars.artist)
        self.artist.pack(side=tkinter.TOP, fill=tkinter.X, pady=10, padx=10)
        # Station name
        self.station_name = KeyValuePanel(self, 'Station', self.state_vars.station_name)
        self.station_name.pack(side=tkinter.TOP, fill=tkinter.X, pady=10, padx=10)


if __name__ == '__main__':
    root = Root('HDFM - NRSC-5 GUI', 500, 1000)
    root.mainloop()

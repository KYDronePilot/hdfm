"""
Temporary module for designing new UI.
"""

import tkinter
from typing import Any
from PIL import Image, ImageTk
from tkinter import ttk


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
        self.ppm_error = tkinter.StringVar()
        self.device = tkinter.StringVar()


class Root(tkinter.Tk):
    """
    Root window, on which everything is built.
    """
    toolbar: Any
    tab_container: Any
    info_widget: Any
    state_vars: Any

    def __init__(self, title: str, width: int, height: int):
        super().__init__()
        self.title(title)
        # TODO: Get rid of window positioning
        self.geometry(f'{width}x{height}+1000+300')
        self.state_vars = State()
        self.setup_components()

    def setup_components(self):
        """
        Setup components in root window.
        """
        self.toolbar = Toolbar(self, self.state_vars)
        self.tab_container = MainTabContainer(self, self.state_vars)
        self.info_widget = InfoWidget(self, self.state_vars)
        self.info_widget.pack(side=tkinter.TOP, padx=5, pady=5, fill=tkinter.X)


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

    def __init__(self, master: Root, state: State):
        super().__init__(master, bd=1, relief=tkinter.RAISED)
        self.pack(side=tkinter.TOP, fill=tkinter.X)
        self.state_vars = state
        # Play button
        self.play_image = Image.open('icons/play.png')
        self.play_image_elem = ImageTk.PhotoImage(self.play_image)
        self.play_button = tkinter.Button(self, image=self.play_image_elem, relief=tkinter.FLAT)
        self.play_button.pack(side=tkinter.LEFT, padx=2, pady=2)
        # Stop button
        self.stop_image = Image.open('icons/stop.png')
        self.stop_image_elem = ImageTk.PhotoImage(self.stop_image)
        self.stop_button = tkinter.Button(self, image=self.stop_image_elem, relief=tkinter.FLAT)
        self.stop_button.pack(side=tkinter.LEFT, padx=2, pady=2)
        # Separator
        self.sep1 = ttk.Separator(self, orient=tkinter.VERTICAL)
        self.sep1.pack(side=tkinter.LEFT, padx=4, pady=3, fill=tkinter.Y)
        # Gear button
        self.gear_image = Image.open('icons/gear.png')
        self.gear_image_elem = ImageTk.PhotoImage(self.gear_image)
        self.gear_button = tkinter.Button(self, image=self.gear_image_elem, relief=tkinter.FLAT)
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
        self.audio_bit_rate = KeyValuePanel(self, 'Bit Rate', self.state_vars.audio_bit_rate)
        self.audio_bit_rate.pack(side=tkinter.TOP, fill=tkinter.X, pady=10, padx=10)
        # Divider
        self.sep1 = ttk.Separator(self, orient=tkinter.HORIZONTAL)
        self.sep1.pack(side=tkinter.TOP, padx=4, pady=10, fill=tkinter.X)


class SettingsFrame(ttk.LabelFrame):
    """
    Frame for displaying settings.
    """
    state_vars: State
    frequency: Any
    program: Any
    gain: Any
    ppm_error: Any
    device: Any
    submit_button: Any

    def __init__(self, master: MainTabContainer, state: State):
        super().__init__(master, text='Settings')
        self.state_vars = state
        # Frequency input
        self.frequency = SettingsInput(self, 'Frequency', self.state_vars.frequency)
        self.frequency.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # Program input
        self.program = SettingsInput(self, 'Program', self.state_vars.program)
        self.program.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # Gain input
        self.gain = SettingsInput(self, 'Gain', self.state_vars.gain)
        self.gain.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # PPM error input
        self.ppm_error = SettingsInput(self, 'PPM Error', self.state_vars.ppm_error)
        self.ppm_error.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # Device input
        self.device = SettingsInput(self, 'Device', self.state_vars.device)
        self.device.pack(padx=4, pady=10, fill=tkinter.X, anchor='w')
        # Submit button
        self.submit_button = ttk.Button(self, text='Save')
        self.submit_button.pack(padx=4, pady=10, anchor='w')


class RadarFrame(ttk.LabelFrame):
    """
    Frame for displaying radar map.
    """

    state_vars: State

    def __init__(self, master, state: State):
        super().__init__(master, text='Radar Map')
        self.state_vars = state


class TrafficFrame(ttk.LabelFrame):
    """
    Frame for displaying traffic map.
    """

    state_vars: State

    def __init__(self, master, state: State):
        super().__init__(master, text='Traffic Map')
        self.state_vars = state


class SettingsInput(ttk.Frame):
    """
    Settings input item with label.
    """
    label: Any
    input_elem: Any
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

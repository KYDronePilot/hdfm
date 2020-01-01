"""
Temporary module for designing new UI.
"""

import tkinter
from typing import Any
from PIL import Image, ImageTk
from tkinter import ttk


class Root(tkinter.Tk):
    """
    Root window, on which everything is built.
    """
    toolbar: Any
    tab_container: Any

    def __init__(self, title: str, width: int, height: int):
        super().__init__()
        self.title(title)
        # TODO: Get rid of window positioning
        self.geometry(f'{width}x{height}+1000+300')
        self.setup_components()

    def setup_components(self):
        """
        Setup components in root window.
        """
        self.toolbar = Toolbar(self)
        self.tab_container = MainTabContainer(self)


class Toolbar(tkinter.Frame):
    """
    Toolbar in UI.
    """
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

    def __init__(self, master: Root):
        super().__init__(master, bd=1, relief=tkinter.RAISED)
        self.pack(side=tkinter.TOP, fill=tkinter.X)
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

    art_tab: 'AlbumArtFrame'
    info_tab: 'InfoFrame'

    def __init__(self, master: Root):
        super().__init__(master)
        self.pack(side=tkinter.TOP, padx=5, pady=5, fill=tkinter.X)
        # Art tab
        self.art_tab = AlbumArtFrame(self)
        self.add(self.art_tab, text='Album Art')
        # Info tab
        self.info_tab = InfoFrame(self)
        self.add(self.info_tab, text='Info')


class AlbumArtFrame(ttk.Frame):
    """
    Frame for displaying album art.
    """

    def __init__(self, master: MainTabContainer):
        super().__init__(master)


class InfoFrame(ttk.Frame):
    """
    Frame for displaying Station info.
    """
    station_name: Any

    def __init__(self, master: MainTabContainer):
        super().__init__(master)
        self.pack()
        self.station_name = StationNameInfo(self)


class StationNameInfo(ttk.LabelFrame):
    """
    Entry in InfoFrame containing radio station name.
    """

    label: Any
    value: Any

    def __init__(self, master: InfoFrame):
        super().__init__(master, text='Station Info')
        self.pack(side=tkinter.LEFT, fill=tkinter.X)
        # Label
        self.label = ttk.Label(self, text='Name:', justify=tkinter.LEFT)
        self.label.pack(side=tkinter.LEFT)
        # Value
        self.value = ttk.Label(self, text='KZOK-FM', justify=tkinter.LEFT)
        self.value.pack(side=tkinter.LEFT)


if __name__ == '__main__':
    root = Root('HDFM - NRSC-5 GUI', 500, 1000)
    root.mainloop()

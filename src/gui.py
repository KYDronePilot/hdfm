import multiprocessing
import subprocess
import tkinter
from queue import Queue

from PIL import Image, ImageTk

from src import DUMP


# Generic image display window.
class GenericDisplay(tkinter.Toplevel, tkinter.Tk):
    def __init__(self, title, dim, delete_eh):
        """

        :param title: title of the window
        :param dim: window default image dimensions
        """
        # Init display object.
        self.init()
        # Image that will be displayed on this window.
        self.image = None
        self.image_cpy = None
        self.p_image = None
        # Init image to a blank image.
        new_img = self.blank_image(dim)
        self.image = new_img
        self.set_image(new_img)
        # Set up display.
        self.title(title)
        # Set up image display panel.
        self.panel = tkinter.Label(self)
        self.panel.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.update_image()
        self.panel.bind('<Configure>', self.resize_image)
        # A callback function to check for and make updates.
        self.after('2000', self.update_window)
        # Register window delete event handler.
        self.protocol('WM_DELETE_WINDOW', delete_eh)

    # Determines what tkinter display is inherited.
    def init(self):
        raise NotImplementedError('This should be implemented by inheritors.')

    # Create blank Tkinter PhotoImage.
    @staticmethod
    def blank_image(dim):
        """

        :param dim: dimensions of this image
        :type dim: tuple
        :return: blank PhotoImage
        """
        return Image.new('RGBA', dim)

    # Callback function to apply any display updates.
    def update_window(self):
        raise NotImplementedError('This function should be subclassed.')

    # Update the image currently on the display.
    def update_image(self):
        self.p_image = ImageTk.PhotoImage(self.image)
        self.panel.configure(image=self.p_image)
        # Set aspect ratio.
        width, height = self.image_cpy.size
        self.aspect(width, height, width, height)

    # Resize an image upon window size change.
    def resize_image(self, event):
        # Ensure the image dimensions are constrained so the image is not distorted.
        old_w, old_h = self.image_cpy.size
        new_w = event.width - 4
        new_h = event.height - 4
        # If dimensions match, nothing needs to be resized.
        if old_w == new_w and old_h == new_h:
            return
        # Difference in new and old dimensions.
        h_diff = abs(new_h - old_h)
        w_diff = abs(new_w - old_w)
        # Adjust either the new height or width to maintain image constraints.
        if h_diff > w_diff:
            new_w = (old_w * new_h) // old_h
        else:
            new_h = (old_h * new_w) // old_w
        # Resize to new dimensions.
        self.image = self.image_cpy.resize((new_w, new_h))
        # Display new image.
        self.update_image()

    # Set an image to the display
    def set_image(self, image):
        """

        :param image: the image to be set
        :type image: Image.Image
        :return:
        """
        # Get dimensions of current image.
        width, height = self.image.size
        # Update images.
        self.image = image
        self.image_cpy = image.copy()
        # Resize new main image to the old dimensions.
        self.image = self.image_cpy.resize((width, height))


# Subclass for the weather display.
class RadarDisplay(GenericDisplay):
    def __init__(self, radar, delete_eh, dim=(900, 900)):
        super().__init__('HDFM - Radar Map', dim, delete_eh)
        # Radar management object.
        self.radar = radar

    # Make TopLevel window.
    def init(self):
        tkinter.Toplevel.__init__(self)

    # For updating the image on the radar display.
    def update_window(self):
        # Try to update the radar image.
        rc = self.radar.update_overlay()
        # If updated, update the display's image.
        if rc:
            self.set_image(self.radar.img)
            self.update_image()
        # Re-register updater hook.
        self.after('2000', self.update_window)


# Subclass for traffic display.
class TrafficDisplay(GenericDisplay):
    def __init__(self, traffic, delete_eh, dim=(600, 600)):
        super().__init__('HDFM - Traffic Display', dim, delete_eh)
        # Traffic management object.
        self.traffic = traffic

    # Make TopLevel window.
    def init(self):
        tkinter.Toplevel.__init__(self)

    # Update traffic tiles on display.
    def update_window(self):
        # Try to update any new tiles.
        rc = self.traffic.update_tiles()
        # If updated, update display's image.
        if rc:
            self.set_image(self.traffic.map)
            self.update_image()
        # Re-register updater hook.
        self.after('2000', self.update_window)


# Subclass for artwork display.
class ArtworkDisplay(GenericDisplay):
    def __init__(self, artwork, delete_eh, dim=(200, 200)):
        super().__init__('HDFM - Artwork Display', dim, delete_eh)
        # Artwork management object.
        self.artwork = artwork

    # Make TopLevel window.
    def init(self):
        tkinter.Toplevel.__init__(self)

    # Update artwork.
    def update_window(self):
        # Try to update artwork.
        rc = self.artwork.update()
        # If updated, update display's image.
        if rc:
            self.set_image(self.artwork.img)
            self.update_image()
        # Re-register updater hook.
        self.after('2000', self.update_window)


# NRSC5 info display frames.
class InfoFrame(tkinter.Frame):
    def __init__(self, root, label, row, col):
        tkinter.Frame.__init__(self, root, bg='#cecece')
        # Set non-zero weight.
        root.columnconfigure(col, weight=1)
        root.rowconfigure(row, weight=1)
        # Information being displayed.
        self.label_text = label
        self.info = ''
        # Set up label.
        text = '{0}: {1}'.format(self.label_text, self.info)
        self.label = tkinter.Label(
            self,
            text=text,
            bg='#cecece'
        )
        self.label.place(relx=0.5, rely=0.5, anchor='c')
        # Position frame.
        self.grid(
            row=row,
            column=col,
            sticky=tkinter.N + tkinter.S + tkinter.E + tkinter.W
        )

    # Update info.
    def update_info(self):
        text = '{0}: {1}'.format(
            self.label_text,
            self.info
        )
        self.label.config(text=text)
        self.update()


# Non-blocking stream reader.
class NBSR(multiprocessing.Process):
    q: Queue

    def __init__(self, proc):
        multiprocessing.Process.__init__(self)
        # Queue for lines.
        self.q = multiprocessing.Queue()
        # Subprocess.
        self.proc = proc

    # Read lines from process.
    def read_lines(self):
        # Continuously get output.
        line = self.proc.stderr.readline()
        while line:
            self.q.put(line)
            line = self.proc.stderr.readline()

    # Run, exiting on termination.
    def run(self):
        try:
            self.read_lines()
        except KeyboardInterrupt:
            pass


# NRSC5 display and process manager.
class NRSC5(tkinter.Tk):
    def __init__(self, delete_eh):
        # Set up window.
        tkinter.Tk.__init__(self)
        self.title('HDFM - Information')
        self.geometry('730x160')
        # NRSC5 arguments.
        self.channel = 0
        self.ppm = 0
        self.log = 3
        self.freq = None
        self.dump_dir = DUMP
        # Command/arg list.
        self.cmd_args = None
        # The command object.
        self.proc = None
        # Non-blocking stream reader for NRSC5 text
        self.nbsr = None
        # Artwork delete function.
        self.artwork_del = None
        # Labels for the display.
        self.artist = InfoFrame(self, 'Artist', row=0, col=0)
        self.track_title = InfoFrame(self, 'Track', row=0, col=1)
        self.slogan = InfoFrame(self, 'Slogan', row=1, col=0)
        self.station_name = InfoFrame(self, 'Station', row=1, col=1)
        self.bit_rate = InfoFrame(self, 'Bit Rate', row=2, col=0)
        # A callback function to check for and make updates.
        self.after('2000', self.update_window)
        # Register window delete event handler.
        self.protocol('WM_DELETE_WINDOW', delete_eh)

    # Format command/argument list.
    def format_cmd(self):
        self.cmd_args = [
            'nrsc5',
            '-l',
            str(self.log),
            '-p',
            str(self.ppm),
            '--dump-aas-files',
            self.dump_dir,
            str(self.freq),
            str(self.channel)
        ]

    # Set the title of the window.
    def set_title(self):
        text = 'HDFM - {0} - Information'.format(
            self.freq
        )
        self.title(text)

    # Run NRSC5.
    def run(self):
        # Set title of info display.
        self.set_title()
        self.format_cmd()
        # Run command, piping output.
        self.proc = subprocess.Popen(
            self.cmd_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Start stream reader.
        self.nbsr = NBSR(self.proc)
        self.nbsr.start()

    # Process STDERR line.
    def process_line(self, line):
        # If line matches information being tracked, update information.
        if 'Artist' in line:
            self.artist.info = line.split('Artist: ')[1][:-1]
            self.artist.update_info()
        elif 'Title' in line:
            self.track_title.info = line.split('Title: ')[1][:-1]
            self.track_title.update_info()
        elif 'Slogan' in line:
            self.slogan.info = line.split('Slogan: ')[1][:-1]
            self.slogan.update_info()
        elif 'Station Name' in line:
            self.station_name.info = line.split('Station Name: ')[1][:-1]
            self.station_name.update_info()
        elif 'Audio bit rate' in line:
            self.bit_rate.info = line.split('Audio bit rate: ')[1][:-1]
            self.bit_rate.update_info()

    # Update the display.
    def update_window(self):
        # Delete artwork if feature not enabled.
        if self.artwork_del is not None:
            self.artwork_del()
        # Get lines from stream.
        while not self.nbsr.q.empty():
            line = self.nbsr.q.get()
            line = line.decode()
            # Process line.
            self.process_line(line)
        # Re-register updater hook.
        self.after('2000', self.update_window)

import tkinter
from queue import Queue

from PIL import Image, ImageTk


# Generic image display window.
class GenericDisplay(tkinter.Toplevel):
    def __init__(self, title, dim):
        """

        :param title: title of the window
        :param dim: window default image dimensions
        """
        super().__init__()
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
        # A queue for receiving update information.
        self.updates = Queue(maxsize=10)

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
    def __init__(self, radar, dim=(900, 900)):
        super().__init__('HDFM - Radar Map', dim)
        # Radar management object.
        self.radar = radar

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
    def __init__(self, traffic, dim=(600, 600)):
        super().__init__('HDFM - Traffic Display', dim)
        # Traffic management object.
        self.traffic = traffic

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

# if __name__ == '__main__':
#     root = GenericDisplay('Test')
#     img = Image.open('../saves/radar_12-14-2018 08-08-38 PM.png').convert('RGBA')
#     root.set_image(img)
#     root.update_image()
#     root.mainloop()
#     print('test')

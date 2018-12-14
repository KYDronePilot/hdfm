from threading import Thread
import tkinter
from PIL import Image, ImageTk, ImageFont, ImageDraw
import time
from queue import Queue

# Font location.
# TODO: may be unnecessary.
FONT = 'font/GlacialIndifference-Regular.otf'


# Generic image display window.
class RootDisplay(Thread):
    def __init__(self, title, dim=(900, 900)):
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
        self.set_image(self.blank_image(dim))
        # Set up display.
        self.disp = self.init_window()
        self.disp.title(title)
        # Set up image display panel.
        self.panel = tkinter.Label(self.disp)
        self.panel.pack(fill=tkinter.BOTH, expand=tkinter.YES)
        self.update_image()
        self.panel.bind('<Configure>', self.resize_image)
        # A callback function to check for and make updates.
        self.disp.after('1000', self.update)
        # A queue for receiving update information.
        self.updates = Queue(maxsize=10)

    # Defines the Tkinter window type (can be overrided).
    @staticmethod
    def init_window():
        return tkinter.Tk()

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
    def update(self):
        raise NotImplementedError('This function should be subclassed.')

    # Update the image currently on the display.
    def update_image(self):
        self.p_image = ImageTk.PhotoImage(self.image)
        self.panel.configure(image=self.p_image)
        # Set aspect ratio.
        width, height = self.image_cpy.size
        self.disp.aspect(width, height, width, height)

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
        # TODO only resize based on dimension constraints.

    # Set an image to the display
    def set_image(self, image):
        """

        :param image: the image to be set
        :type image: Image.Image
        :return:
        """
        self.image = image
        self.image_cpy = image.copy()

    # Main loop.
    def run(self):
        self.disp.mainloop()


if __name__ == '__main__':
    root = RootDisplay('Test')
    img = Image.open('Weather Map 10-28-2017 09-29-42 PM.png').convert('RGBA')
    root.set_image(img)
    root.update_image()
    root.run()

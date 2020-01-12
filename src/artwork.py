from typing import Optional

from PIL import Image
from PIL.Image import Image as ImageType

from config import static_config


class ArtworkManager:
    """
    Management of album/station artwork.

    Attributes:
        _image: The artwork image
    """

    _image: Optional[ImageType]

    def __init__(self, image: Optional[ImageType] = None):
        self._image = image

    def update_artwork(self) -> bool:
        """
        Search for new artwork image and update if available.

        Returns:
            Whether artwork was updated
        """
        files = list(static_config.dump_directory.glob('*.jpg'))
        # Ensure one exists
        if len(files) == 0:
            return False
        # Update with first artwork file, ignoring others
        with files[0].open('rb') as fp:
            self.image = Image.open(fp).convert('RGBA')
        # Delete other files
        for file in files:
            file.unlink()
        return True

    @property
    def image(self) -> ImageType:
        return self._image

    @image.setter
    def image(self, value: ImageType):
        self._image = value

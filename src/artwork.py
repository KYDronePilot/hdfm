from typing import BinaryIO

from PIL import Image
from PIL.Image import Image as ImageType


class ArtworkManager:
    """
    Management of album/station artwork.

    Attributes:
        _image: The artwork image
        filename: Name of artwork image file
    """

    _image: ImageType
    filename: str

    def __init__(self, image: ImageType, filename: str):
        self._image = image
        self.filename = filename

    @classmethod
    def load_image(cls, fp: BinaryIO, filename: str) -> 'ArtworkManager':
        """
        Load an artwork image from a file handle.

        Args:
            fp: File handle
            filename: Name of file

        Returns:
            New artwork instance
        """
        image = Image.open(fp).convert('RGBA')
        return cls(image, filename)

    @property
    def image(self) -> ImageType:
        return self._image

    @image.setter
    def image(self, value: ImageType):
        self._image = value

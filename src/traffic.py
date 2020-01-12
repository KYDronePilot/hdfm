import re
import time
from pathlib import Path
from typing import List, Optional, BinaryIO

from PIL import Image
from PIL.Image import Image as ImageType
from config import static_config


class TrafficTile:
    """
    Single received traffic tile.

    Attributes:
        filename: Name of file
        _image: The actual image
    """

    filename: str
    _image: ImageType

    def __init__(self, filename: str, image: ImageType):
        self.filename = filename
        self._image = image

    @classmethod
    def load_file(cls, fp: BinaryIO, filename: str) -> 'TrafficTile':
        """
        Load traffic tile from file handle.

        Args:
            fp: Traffic tile file handle
            filename: Name of file

        Returns:
            Traffic tile instance
        """
        image = Image.open(fp).convert('RGBA')
        return cls(filename, image)

    @property
    def xy_coordinates(self) -> (int, int):
        """
        Coordinates of tile in final image.

        Returns:
            Coordinates in (x, y) form (zero indexed)
        """
        match = re.search('_([123])_([123])_', self.filename)
        if match is None:
            raise Exception(
                f'Traffic tile coordinates are not in filename: "{self.filename}"'
            )
        return int(match.group(2)) - 1, int(match.group(1)) - 1

    @property
    def image(self) -> ImageType:
        return self._image

    @image.setter
    def image(self, value: ImageType):
        self._image = value


class TrafficMapManager:
    """
    Traffic map management class. Processes traffic tiles received from iHeartRadio.

    Attributes:
        _traffic_map: Traffic map tile pasteboard, where traffic tiles are pasted as they are received.
        _tiles: Received traffic tiles
    """

    _traffic_map: ImageType
    _tiles: List[Optional[TrafficTile]]

    def __init__(self):
        self._traffic_map = Image.new('RGBA', (600, 600))
        self._tiles = [None] * 9

    def add_tile(self, tile: TrafficTile):
        """
        Add a new traffic tile to the map.

        Args:
            tile: Tile to add
        """
        x, y = tile.xy_coordinates
        self._tiles[x + y * 3] = tile
        self._paste_tile(tile)

    def find_and_add_tiles(self) -> bool:
        """
        Find any new traffic tiles and add them to the map.

        Returns:
            Whether any new traffic tiles were found/added
        """
        files = list(static_config.dump_directory.glob('*TMT*'))
        # Need at least 1 files to continue
        if len(files) == 0:
            return False
        for file in files:
            with file.open('rb') as fp:
                self.add_tile(TrafficTile.load_file(fp, file.name))
            file.unlink()
        return True

    def _paste_tile(self, tile: TrafficTile):
        """
        Paste tile on full map.

        Args:
            tile: Tile to paste
        """
        x, y = tile.xy_coordinates
        self._traffic_map.paste(tile.image, (x * 200, y * 200))

    @property
    def traffic_map(self) -> ImageType:
        return self._traffic_map

    @traffic_map.setter
    def traffic_map(self, value: ImageType):
        self._traffic_map = value

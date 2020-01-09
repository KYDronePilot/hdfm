from pathlib import Path
from typing import Optional

from PIL import Image, ImageFont, ImageDraw
from PIL.Image import Image as ImageType

from config import static_config
from src.map_manager import MapManager
from utils import timestamp


class DopplerRadarManager:
    """
    Doppler radar manager. Radar is composed of a cropped street map and radar overlay received from iHearRadio
    stations.

    Attributes:
        map_manager: Street map manager
        overlay: Radar overlay image
        _radar_map: Actual doppler radar map
    """

    map_manager: MapManager
    overlay: Optional[ImageType]
    _radar_map: Optional[ImageType]

    def __init__(self, map_manager: MapManager, overlay: Optional[ImageType] = None):
        self.map_manager = map_manager
        self.overlay = overlay
        self._radar_map = None

    @property
    def has_overlay(self) -> bool:
        """
        Whether instance has a radar overlay.
        """
        return self.overlay is not None

    @classmethod
    def init_from_overlay_file(
        cls, map_manager: MapManager, overlay_file: Path
    ) -> 'DopplerRadarManager':
        """
        Create radar instance from an overlay file.

        Args:
            map_manager: Street map manager
            overlay_file: Path to radar overlay file

        Returns:
            New radar instance
        """
        image = Image.open(overlay_file)
        return cls(map_manager, image)

    @classmethod
    def init_from_overlay_and_config_files(
        cls, config_file: Path, overlay_file: Path
    ) -> 'DopplerRadarManager':
        """
        Create radar instance from config and overlay files.

        Args:
            config_file: Path to radar config file
            overlay_file: Path to radar overlay file

        Returns:
            New radar instance
        """
        with config_file.open() as fp:
            map_manager = MapManager.init_from_config(fp)
        return cls.init_from_overlay_file(map_manager, overlay_file)

    def update_overlay(self, overlay: ImageType):
        """
        Update the overlay of the radar map.

        Args:
            New overlay image
        """
        self.overlay = overlay

    def update_radar_map(self) -> bool:
        """
        Attempt to update the radar map image, searching for a new overlay.

        Returns:
            Whether the map was updated or not
        """
        files = list(static_config.dump_directory.glob('*DWRO*'))
        # Ensure at least one to continue
        if len(files) == 0:
            return False
        # Update overlay with first overlay file, regardless if there are more than one
        with files[0].open('rb') as fp:
            self.update_overlay(Image.open(fp).convert('RGBA'))
        # Delete all overlay files
        for file in files:
            file.unlink()
        return True

    @staticmethod
    def timestamp_image(image: ImageType):
        """
        Timestamp an image.
            Writes to bottom right corner

        Args:
            image: Image to timestamp

        Returns:
            Timestamped image
        """
        font = ImageFont.truetype(str(static_config.font_file), 25)
        draw = ImageDraw.Draw(image)
        draw.text((550, 835), timestamp(), font=font, fill='black')

    @staticmethod
    def overlay_image(radar_overlay: ImageType, map_image: ImageType) -> ImageType:
        """
        Overlay the radar on the map image.

        Args:
            radar_overlay: Radar overlay image
            map_image: Map image to overlay the radar onto

        Returns:
            Overlayed radar map
        """
        radar_overlay = radar_overlay.resize((900, 900))
        return Image.alpha_composite(map_image, radar_overlay.convert('RGBA'))

    @property
    def radar_map(self) -> ImageType:
        """
        Get doppler radar map from cache (if possible), or generate one.

        Returns:
            Doppler radar map
        """
        if self._radar_map is not None:
            return self._radar_map
        # Generate image and timestamp it
        radar_map = self.overlay_image(self.overlay, self.map_manager.map)
        self.timestamp_image(radar_map)
        # Cache and return
        self.radar_map = radar_map
        return radar_map

    @radar_map.setter
    def radar_map(self, value: ImageType):
        self._radar_map = value

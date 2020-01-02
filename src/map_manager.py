import math
import re
from pathlib import Path
from typing import ClassVar, List, Union, Dict, TextIO, Any, Tuple, Optional

from PIL import Image
from PIL.Image import Image as ImageType

from config import static_config

IHeartRadioConfigType = Dict[str, Union[str, List[str]]]


class IHeartRadioConfig:
    """
    iHeartRadio config manager.
    """

    @staticmethod
    def strip_quotes(s: str) -> str:
        """
        Strip beginning/trailing quotes from string.

        Args:
            s: String to strip from

        Returns:
            Quote-stripped string
        """
        if s[0] == s[-1] == '"' or s[0] == s[-1] == "'":
            return s[1:-1]

    @staticmethod
    def _parse_value(value: str) -> Union[List[str], str]:
        """
        Parse value part of config entry.

        Args:
            value: Entry value

        Returns:
            Parsed value
        """
        # Split into list if broken up by semicolons
        if ';' in value:
            return [IHeartRadioConfig.strip_quotes(part) for part in value.split(';')]
        return IHeartRadioConfig.strip_quotes(value)

    @staticmethod
    def load(text: str) -> IHeartRadioConfigType:
        """
        Parse an iHeartRadio config file.

        Args:
            text: Text to parse

        Returns:
            Parsed data
        """
        result = {}
        lines = text.splitlines()
        for line in lines:
            key_val_re = re.search(r'(\w+)=(.*?)$', line)
            # Skip if line has no matching config entry
            if key_val_re is None:
                continue
            key, val = key_val_re.groups()
            result[key] = IHeartRadioConfig._parse_value(val)
        return result


class IHeartRadioConfigEntry:
    """
    Config entry in iHearRadio config.

    Attributes:
        key: Key for config entry
        value: Value of config entry
    """

    key: ClassVar[str]
    value: Any

    def __init__(self, value: str):
        self.value = self.parse(value)

    def parse(self, value: str) -> Any:
        """
        Parse entry value.

        Args:
            value: Value to parse
        """
        return value


class AreaId(IHeartRadioConfigEntry):
    key = 'DWR_Area_ID'


class Coordinates(IHeartRadioConfigEntry):
    key = 'Coordinates'
    value: Tuple[Tuple[float, float], Tuple[float, float]]

    def parse(self, value: List[str]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        if len(value) != 2:
            raise Exception(f'Coordinates "{value}" in config are malformed.')
        lat_top, lon_left = value[0][1:-1].split(',')
        lat_bottom, lon_right = value[1][1:-1].split(',')
        return (float(lat_top), float(lon_left)), (float(lat_bottom), float(lon_right))


class MapManager:
    """
    Map to overlay the weather radar on.

    Attributes:
        lat_top: Latitude of top edge
        lat_bottom: Latitude of bottom edge
        lon_left: Longitude of left edge
        lon_right: Longitude of right edge
        area_id: Area ID of map
        coordinates: Coordinates of map's edges
        _map: Cached map instance for area specified by coordinates
    """

    # Max latitude of US map in a linear form.
    LAT_MAX: ClassVar[float] = 1.0799224683069641
    # Reference latitude in linear form.
    REF_LAT: ClassVar[float] = 0.7380009964270406

    lat_top = float
    lat_bottom = float
    lon_left = float
    lon_right = float
    area_id = AreaId
    coordinates: Coordinates
    _map: Optional[ImageType]

    def __init__(self, area_id: AreaId, coordinates: Coordinates):
        self.area_id = area_id
        self.coordinates = coordinates
        self.lat_top = coordinates.value[0][0]
        self.lat_bottom = coordinates.value[1][0]
        self.lon_left = coordinates.value[0][1]
        self.lon_right = coordinates.value[1][1]
        self._map = None

    @property
    def map_cache_file(self) -> Path:
        """
        Name of the map cache file.
        """
        return static_config.cache_directory / Path(f'map_{self.area_id.value}.png')

    @classmethod
    def init_from_config(cls, fp: TextIO) -> 'MapManager':
        """
        Create instance from config.

        Args:
            fp: File handle

        Returns:
            New map instance
        """
        config_text = fp.read()
        config = IHeartRadioConfig.load(config_text)
        area_id = AreaId(config[AreaId.key])
        coords = Coordinates(config[Coordinates.key])
        return cls(area_id, coords)

    @staticmethod
    def _load_main_map() -> ImageType:
        """
        Load main map to use for cropping.

        Returns:
            Loaded map
        """
        return Image.open(static_config.main_map_file)

    def create_map(self) -> ImageType:
        """
        Create map for area specified by coordinates.

        Returns:
            Map for area
        """
        main_map = self._load_main_map()

        # Make latitudes linear
        def make_linear(val: float):
            return MapManager.LAT_MAX - math.asinh(math.tan(math.radians(val)))

        lin_lat_top = make_linear(self.lat_top)
        lin_lat_bottom = make_linear(self.lat_bottom)
        # Calculate x-coords using a ratio of a known location on the map
        x1 = (self.lon_left + 130.781250) * 7162 / 39.34135
        x2 = (self.lon_right + 130.781250) * 7162 / 39.34135
        # Use another ratio of a known location to find the latitudes
        den = MapManager.LAT_MAX - MapManager.REF_LAT
        y1 = lin_lat_top * 3565 / den
        y2 = lin_lat_bottom * 3565 / den
        # Crop the map.
        cropped = main_map.crop((
            int(x1),
            int(y1),
            int(x2),
            int(y2)
        ))
        # Crop and resize the map
        return cropped.resize((900, 900)).convert('RGBA')

    @property
    def map(self) -> ImageType:
        """
        Obtain map in the following order of attempts:
            - Check cache attribute
            - Check cache file
            - Generate and cache new file

        Returns:
            Map specified by coordinates
        """
        if self._map is not None:
            return self._map
        if self.map_cache_file.exists():
            map_image = Image.open(self.map_cache_file)
            self.map = map_image
            return map_image.convert('RGBA')
        map_image = self.create_map()
        self.map = map_image
        return map_image

    @map.setter
    def map(self, value: ImageType):
        """
        Write to cache file and attribute, overwriting if already exists.

        Args:
            value: Map image
        """
        self._map = value
        # Delete cache if already exists
        if self.map_cache_file.exists():
            self.map_cache_file.unlink()
        value.save(self.map_cache_file)

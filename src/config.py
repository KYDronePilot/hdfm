"""
Configuration management.
"""
import json
from pathlib import Path
from typing import List, Any, ClassVar
import tempfile


class ConfigEntry:
    """
    Entry in config.
    """

    key: str
    value: Any

    def __init__(self, key: str, value: Any):
        self.key = key
        self.value = value

    def get(self) -> Any:
        return self.value

    def set(self, value: Any):
        self.value = value


class Config:
    """
    Generic config representation.

    Attributes:
        file: Where config file is located
        all_items: All config items
    """

    file: Path
    all_items: List[ConfigEntry]

    def __init__(self, file: Path):
        self.file = file
        self.all_items = []

    def save(self):
        """
        Save config changes to file.
        """
        config_map = {item.key: item.value for item in self.all_items}
        with self.file.open('w') as fp:
            json.dump(config_map, fp)

    def load_config(self):
        """
        Load the config into memory.
        """
        if not self.file.exists():
            raise Exception(f'Config file "{self.file}" does not exist.')
        with self.file.open() as fp:
            config_map = json.load(fp)

        for item in self.all_items:
            # Ensure item is in config
            if item.key not in config_map:
                raise Exception(f'Config key "{item.key}" not in config file "{self.file}".')
            item.set(config_map[item.key])
            del config_map[item.key]
        # Ensure no extra config items
        if len(config_map) != 0:
            raise Exception(f'Extra keys in config file "{self.file}": {config_map}.')


class StaticConfig:
    """
    Static configuration (not editable by user; values dynamically generated or stored in source code).

    Attributes:
        project_root: Root of project
        font_file: Path to font file
        main_map_file: Main US map file
        dump_directory: Directory to dump NRSC5 output to
        cache_directory: Directory to save cache files to
    """

    project_root: ClassVar[Path] = Path(__file__).parent.parent
    font_file: ClassVar[Path] = project_root / Path('font') / Path('GlacialIndifference-Regular.otf')
    main_map_file: ClassVar[Path] = project_root / Path('maps') / Path('us_map.png')
    dump_directory: ClassVar[Path] = Path(tempfile.gettempdir()) / Path('nrsc5_dump')
    cache_directory: ClassVar[Path] = Path(tempfile.gettempdir()) / Path('nrsc5_cache')

    @classmethod
    def setup(cls):
        """
        Perform any setup tasks for static config.
        """
        # Clean dump directory
        if cls.dump_directory.exists():
            cls.dump_directory.rmdir()
        cls.dump_directory.mkdir()
        # Ensure cache directory exists
        if not cls.cache_directory.exists():
            cls.cache_directory.mkdir()


class UserConfig(Config):
    """
    User-changeable config items.
    """

    def __init__(self):
        super().__init__(Path(__file__).parent.parent / Path('hdfm_config.json'))


static_config = StaticConfig()
static_config.setup()

"""
Configuration management.
"""
import json
import shutil
from pathlib import Path
from typing import List, Any, ClassVar
import tempfile
from appdirs import AppDirs


class ApplicationDirectories(AppDirs):
    """
    AppDirs wrapper.
    """

    @property
    def user_data_dir(self) -> Path:
        return Path(super().user_data_dir)

    @property
    def site_data_dir(self) -> Path:
        return Path(super().site_data_dir)

    @property
    def user_config_dir(self) -> Path:
        return Path(super().user_config_dir)

    @property
    def site_config_dir(self) -> Path:
        return Path(super().site_config_dir)

    @property
    def user_cache_dir(self) -> Path:
        return Path(super().user_cache_dir)

    @property
    def user_state_dir(self) -> Path:
        return Path(super().user_state_dir)

    @property
    def user_log_dir(self) -> Path:
        return Path(super().user_log_dir)


class ConfigEntry:
    """
    Entry in config.
    """

    key: str
    value: Any

    def __init__(self, key: str, value: Any = None):
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
            raise FileNotFoundError(f'Config file "{self.file}" does not exist.')
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
            shutil.rmtree(cls.dump_directory)
        cls.dump_directory.mkdir()
        # Ensure cache directory exists
        if not cls.cache_directory.exists():
            cls.cache_directory.mkdir()


class UserConfig(Config):
    """
    User-changeable config items.
    """

    gain: ConfigEntry
    ppm: ConfigEntry
    device: ConfigEntry

    def __init__(self, config_file: Path):
        super().__init__(config_file)
        self.gain = ConfigEntry(key='gain', value='auto')
        self.ppm = ConfigEntry(key='ppm', value='0')
        self.device = ConfigEntry(key='device', value='0')

        self.all_items = [
            self.gain,
            self.ppm,
            self.device
        ]


# Setup config dirs
dirs = ApplicationDirectories(appname='hdfm', appauthor='kydronepilot', version='0.0.1')
config_dir = dirs.user_config_dir
# Create if not exists
if not config_dir.exists():
    config_dir.mkdir(parents=True)


static_config = StaticConfig()
static_config.setup()

user_config = UserConfig(config_dir / Path('config.json'))
# Try to load config, leaving defaults if doesn't exist
try:
    user_config.load_config()
except FileNotFoundError:
    pass

"""
Module for managing NRSC-5 application.
"""
import asyncio
import queue
import re
import subprocess
import threading
import time
from itertools import chain
from pathlib import Path
from typing import List, Any, Optional, Union, IO, Tuple


class Arg:
    """
    Generic command line argument.

    Attributes:
        name: Name of argument
        description: Description of argument
    """

    name: str
    description: str

    def __init__(self, name: str, description: str = ''):
        self.name = name
        self.description = description

    @staticmethod
    def format_multiple_args(args: List['Arg']) -> List[str]:
        """
        Format list of args into bigger list.

        Args:
            args: Args to format

        Returns:
            Formatted args
        """
        return list(chain(*(arg.format_arg() for arg in args)))

    def format_arg(self) -> List[str]:
        """
        Format argument to pass into subprocess call.

        Returns:
            Formatted argument
        """
        raise NotImplementedError

    def set_arg(self, value: Any):
        """
        Set argument value.

        Args:
            value: Value to set argument to
        """
        raise NotImplementedError


class BooleanArg(Arg):
    """
    Represents a boolean argument.

    Attributes:
        _value: Boolean value (defaults to False)
        _flag: Argument flag when executing (including hyphens)
    """

    _value: bool
    _flag: str

    def __init__(
        self, name: str, flag: str, description: str = '', default: bool = False
    ):
        super().__init__(name, description)
        self._value = default
        self._flag = flag

    def format_arg(self) -> List[str]:
        if self._value:
            return [self._flag]
        return []

    def set_arg(self, value: bool):
        self._value = value


class KeyValArg(Arg):
    """
    Key/value argument.

    Attributes:
        _flag: Argument key/flag (including hyphens)
        _value: Value part of argument
        _is_required: Whether the argument is required (value must be provided)
    """

    _flag: str
    value: Optional[str]
    _is_required: bool

    def __init__(
        self, name: str, flag: str, description: str = '', is_required: bool = False
    ):
        super().__init__(name, description)
        self._flag = flag
        self.value = None
        self._is_required = is_required

    def format_arg(self) -> List[str]:
        # Ensure value provided if required
        if self.value is None:
            if self._is_required:
                raise Exception(
                    f'Value for "{self._flag}" not provided, but is required.'
                )
            return []
        return [self._flag, self.value]

    def set_arg(self, value: Optional[str]):
        self.value = value

    def clear(self):
        """
        Clear argument value, if any.
        """
        self.value = None


class PositionalArg(Arg):
    """
    Positional argument.

    Attributes:
        _value: Argument value
        _is_required: Whether the argument is required
    """

    _value: Optional[str]
    _is_required: bool

    def __init__(self, name: str, description: str = '', is_required: bool = True):
        super().__init__(name, description)
        self._value = None
        self._is_required = is_required

    def format_arg(self) -> List[str]:
        # Ensure value provided if required
        if self._value is None:
            if self._is_required:
                raise Exception(
                    f'Value for "{self.name}" positional argument not provided'
                )
            return []
        return [self._value]

    def set_arg(self, value: str):
        self._value = value


class SubprocessStreamReader(threading.Thread):
    """
    Stream reader for stdout/stderr of a subprocess.

    Attributes:
        line_q: Queue to store lines in
        stream: IO stream to read from
        _stop_event: Event to stop thread
    """

    line_q: queue.Queue
    stream: IO[Union[str, bytes]]
    _stop_event: threading.Event

    def __init__(self, stream: IO[Union[str, bytes]]):
        super().__init__()
        self.line_q = queue.Queue()
        self.stream = stream
        self._stop_event = threading.Event()

    async def read_lines(self):
        """
        Read and queue lines from stream.
        """
        line = self.stream.readline()
        while line:
            if isinstance(line, bytes):
                line = line.decode()
            self.line_q.put(line)
            line = self.stream.readline()

    def run(self):
        # Start reader
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.read_lines())
        # Wait for stop command
        while not self._stop_event.is_set():
            time.sleep(0.1)
        # Kill reader
        loop.stop()

    def join(self, *args, **kwargs) -> None:
        self._stop_event.set()
        super().join(*args, **kwargs)


class LogParserQueue(queue.Queue):
    """
    Modified queue for parsing and storing log information.
    """

    def handle_line(self, line: str) -> bool:
        """
        Check if log line has the information needed by the queue and queue it if so.

        Args:
            line: Line to check

        Returns:
            Whether the line could be processed or not
        """
        parsed = self.parse(line)
        if parsed is None:
            return False
        # Handle the line
        self.put(parsed)
        return True

    def parse(self, line: str) -> Optional[str]:
        """
        Parse a log line, returning parsed value if possible, else None.

        Args:
            line: Line to parse

        Returns:
            Parsed information or None if unable to parse
        """
        raise NotImplementedError()

    def get_newest(self) -> str:
        """
        Get the newest item parsed, discarding older ones.

        Returns:
            Newest item parsed or None if none
        """
        item = None
        while not self.empty():
            item = self.get()
        return item


class ArtistParserQueue(LogParserQueue):
    def parse(self, line: str) -> Optional[str]:
        res = re.search(r'Artist: (.*?)$', line)
        if res is not None:
            return res.group(1)


class TitleParserQueue(LogParserQueue):
    def parse(self, line: str) -> Optional[str]:
        res = re.search(r'Title: (.*?)$', line)
        if res is not None:
            return res.group(1)


class SloganParserQueue(LogParserQueue):
    def parse(self, line: str) -> Optional[str]:
        res = re.search(r'Slogan: (.*?)$', line)
        if res is not None:
            return res.group(1)


class StationNameParserQueue(LogParserQueue):
    def parse(self, line: str) -> Optional[str]:
        res = re.search(r'Station name: (.*?)$', line)
        if res is not None:
            return res.group(1)


class BitRateParserQueue(LogParserQueue):
    def parse(self, line: str) -> Optional[str]:
        res = re.search(r'Audio bit rate: (.*?)$', line)
        if res is not None:
            return res.group(1)


class NRSC5LogParser(threading.Thread):
    """
    For parsing and extracting information from NRSC5 logs.

    Attributes:
        stderr_reader: Log stream reader
        artist: Artist information
        title: Track title (used for ADs sometimes)
        slogan: Station slogan
        station_name: Station name
        bit_rate: Bit rate of the audio
        queues: All log parser queues
    """

    stderr_reader: Optional[SubprocessStreamReader]
    # Queues for information extracted from logs
    artist: ArtistParserQueue
    title: TitleParserQueue
    slogan: SloganParserQueue
    station_name: StationNameParserQueue
    bit_rate: BitRateParserQueue
    queues: Tuple[
        ArtistParserQueue,
        TitleParserQueue,
        SloganParserQueue,
        StationNameParserQueue,
        BitRateParserQueue,
    ]
    _stop_event: threading.Event

    def __init__(self, stream: IO[Union[str, bytes]]):
        super().__init__()
        self.stderr_reader = SubprocessStreamReader(stream)
        self.artist = ArtistParserQueue()
        self.title = TitleParserQueue()
        self.slogan = SloganParserQueue()
        self.station_name = StationNameParserQueue()
        self.bit_rate = BitRateParserQueue()
        self.queues = (
            self.artist,
            self.title,
            self.slogan,
            self.station_name,
            self.bit_rate,
        )
        self._stop_event = threading.Event()

    def handle_line(self, line: str):
        """
        Handle single log line.

        Args:
            line: Log line
        """
        # Try each queue
        for q in self.queues:
            if q.handle_line(line):
                break

    def handle_lines(self):
        """
        Handle available lines from the stream reader.
        """
        while not self.stderr_reader.line_q.empty():
            self.handle_line(self.stderr_reader.line_q.get())

    def run(self):
        self.stderr_reader.start()
        while not self._stop_event.is_set():
            self.handle_lines()
            time.sleep(0.1)

    def join(self, *args, **kwargs) -> None:
        self.stderr_reader.join()
        self._stop_event.set()
        super().join(*args, **kwargs)


class NRSC5Program:
    """
    Representation of NRSC-5 command line application.

    Attributes:
        exec_path: Path to executable
        process: NRSC5 program subprocess
        log_parser: Log parser
        (Args omitted)
    """

    exec_path: Path
    process: Optional[subprocess.Popen]
    log_parser: Optional[NRSC5LogParser]

    # Boolean args
    version: BooleanArg
    q: BooleanArg
    # Key/value args
    log_level: KeyValArg
    device_index: KeyValArg
    ppm_error: KeyValArg
    gain: KeyValArg
    iq_input: KeyValArg
    iq_output: KeyValArg
    wav_output: KeyValArg
    hdc_output: KeyValArg
    aas_output: KeyValArg
    # Positional args
    frequency: PositionalArg
    program: PositionalArg

    def __init__(self, exec_path: Path):
        self.exec_path = exec_path
        self.process = None
        self.log_parser = None

        self.version = BooleanArg(
            name='Version', flag='-v', description='print the version number and exit'
        )
        self.q = BooleanArg(
            name='Logout output', flag='-q', description='disable log output'
        )
        self.log_level = KeyValArg(
            name='Log Level',
            flag='-l',
            description='set log level (1 = DEBUG, 2 = INFO, 3 = WARN)',
        )
        self.device_index = KeyValArg(
            name='Device Index', flag='-d', description='rtl-sdr device'
        )
        self.ppm_error = KeyValArg(
            name='PPM Error', flag='-p', description='rtl-sdr ppm error'
        )
        self.gain = KeyValArg(
            name='Gain',
            flag='-g',
            description='gain (example: 49.6) (automatic gain selection if not specified)',
        )
        self.iq_input = KeyValArg(
            name='IQ Input', flag='-r', description='read IQ samples from input file'
        )
        self.iq_output = KeyValArg(
            name='IQ Output', flag='-w', description='write IQ samples to output file'
        )
        self.wav_output = KeyValArg(
            name='WAV Output', flag='-o', description='write audio to output WAV file'
        )
        self.hdc_output = KeyValArg(
            name='Dump HDC', flag='--dump-hdc', description='dump HDC packets'
        )
        self.aas_output = KeyValArg(
            name='Dump AAS Files',
            flag='--dump-aas-files',
            description='dump AAS files (WARNING: insecure)',
        )
        self.frequency = PositionalArg(
            name='Frequency',
            description='center frequency in MHz or Hz (do not provide frequency when reading from file)',
        )
        self.program = PositionalArg(
            name='Program', description='audio program to decode (0, 1, 2, or 3)'
        )

    @staticmethod
    def string_if_not_none(v: Any) -> Optional[str]:
        """
        Cast var to str if not None.

        Args:
            v: Var to cast

        Returns:
            String cast if not None
        """
        if v is not None:
            return str(v)
        return v

    def _get_args_list(self) -> List[str]:
        """
        Format/combine command line args.

        Returns:
            Command line args to execute program with
        """
        boolean_args = Arg.format_multiple_args([self.version, self.q])
        # Exclude gain if set to auto
        if self.gain.value == '-1.0':
            gain_arg = [self.gain]
        else:
            gain_arg = []
        key_val_args = Arg.format_multiple_args(
            [
                self.log_level,
                self.device_index,
                self.ppm_error,
                *gain_arg,
                self.iq_input,
                self.iq_output,
                self.wav_output,
                self.hdc_output,
                self.aas_output,
            ]
        )
        positional_args = Arg.format_multiple_args([self.frequency, self.program])
        return list(
            chain(
                [str(self.exec_path.absolute())],
                boolean_args,
                key_val_args,
                positional_args,
            )
        )

    def config_iq_read(self, iq_file: Path, program: int):
        """
        Configure NRSC5 to read data from IQ file (not using an rtl-sdr).

        Good for testing when you don't have an antenna setup.
        Note: Mutually exclusive with `config_channel_tune`

        Args:
            iq_file: Input IQ file
            program: Audio program to decode
        """
        self.iq_input.set_arg(str(iq_file.absolute()))
        self.frequency._is_required = False
        self.program.set_arg(str(program))

    def config_channel_tune(
        self,
        freq: float,
        program: int,
        device_index: Optional[int] = None,
        ppm_error: Optional[int] = None,
        gain: Optional[float] = None,
    ):
        """
        Configure NRSC5 to tune rtl-sdr to a particular frequency.

        Note: Mutually exclusive with `config_iq_read`

        Args:
            freq: Frequency to tune to
            program: Program to decode
            device_index: rtl-sdr device number
            ppm_error: rtl-sdr ppm error
            gain: rtl-sdr gain
        """
        self.frequency.set_arg(str(freq))
        self.program.set_arg(str(program))
        self.device_index.set_arg(self.string_if_not_none(device_index))
        self.ppm_error.set_arg(self.string_if_not_none(ppm_error))
        self.gain.set_arg(self.string_if_not_none(gain))

    def config_dump_dir(self, directory: Path):
        """
        Configure path to dump AAS files to.

        Args:
            directory: Directory to dump files to
        """
        self.aas_output.set_arg(str(directory.absolute()))

    def start(self):
        """
        Start NRSC5 program.
        """
        args = self._get_args_list()
        self.process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.log_parser = NRSC5LogParser(self.process.stderr)
        self.log_parser.start()

    def stop(self):
        """
        Stop NRSC5 program.
        """
        self.process.terminate()
        self.log_parser.join()

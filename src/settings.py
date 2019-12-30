import os
import tkinter
from typing import Any, Callable, Dict
from tkinter import messagebox

from cerberus import Validator


class Settings:
    """
    For holding runtime settings of the application.

    Attributes:
        program: HD Radio program, for stations with subchannels
        ppm: PPM error correction
        save_dir: Directory to save weather and traffic images to
        show_log: Whether to show logging information
        show_art: Whether to display album/station art
        nrsc5_path: Path to NRSC5 executable
    """
    nrsc5_path: str
    program: int
    ppm: int
    save_dir: str
    show_log: bool
    show_art: bool

    def __init__(self, nrsc5_path: str, program: int, ppm: int, save_dir: str, show_log: bool, show_art: bool):
        self.nrsc5_path = nrsc5_path
        self.program = program
        self.ppm = ppm
        self.save_dir = save_dir
        self.show_log = show_log
        self.show_art = show_art

    @classmethod
    def init_raw(cls, nrsc5_path: str, program: str, ppm: str, save_dir: str, show_log: bool, show_art: bool):
        """
        Create instance from raw settings values (all values assumed valid).
        """
        return cls(
            nrsc5_path,
            int(program),
            int(ppm),
            save_dir,
            show_log,
            show_art
        )

    @classmethod
    def validate_all_fields(cls, nrsc5_path: str, program: str, ppm: str, save_dir: str, show_log: bool,
                            show_art: bool):
        """
        Validate all settings fields.

        Returns:
            Whether all fields are valid
        """
        return (
            cls.validate_nrsc5_path(nrsc5_path) == ''
            and cls.validate_program(program) == ''
            and cls.validate_ppm(ppm) == ''
            and cls.validate_save_dir(save_dir) == ''
        )

    @staticmethod
    def validate_nrsc5_path(value: str):
        if value == '':
            return 'Please enter path to NRSC-5 executable'
        if not os.path.isfile(value):
            return 'Path not valid'
        return ''

    @staticmethod
    def validate_program(value: str):
        if value == '':
            return 'Please enter HD Radio program'
        try:
            value = int(value)
        except ValueError:
            pass
        if not validate(value, {'type': 'integer', 'min': 0}):
            return 'Program must be a number greater than 0'
        return ''

    @staticmethod
    def validate_ppm(value: str):
        if value == '':
            return 'Please enter PPM error correction'
        try:
            int(value)
        except ValueError:
            return 'Value must be an integer'
        return ''

    @staticmethod
    def validate_save_dir(value: str) -> str:
        if value == '':
            return ''
        if not os.path.isdir(value):
            return 'Not a valid directory'
        return ''


def validate(value: Any, constraints: Dict[str, str]) -> bool:
    """
    Validation wrapper for Cerberus.

    Args:
        value: Value to validate
        constraints: Validation constraints to pass to Cerberus

    Returns:
        Whether value is an int
    """
    val = Validator({'val': constraints})
    return val.validate({'val': value})


class TextInput(tkinter.Entry):
    """
    Text input GUI element.

    Attributes:
        value: String var containing input value
        feedback_var: Feedback variable to write invalid feedback to
        validator: Validator for input field
    """
    value: tkinter.StringVar
    feedback_var: tkinter.StringVar
    validator: Callable

    def __init__(self, root: 'InputGroup', validator: Callable, feedback_var: tkinter.StringVar,
                 default_value: str = ''):
        # Configure callback for input value changes
        self.value = tkinter.StringVar(value=default_value)
        self.value.trace('w', lambda name, i, mode, sv=self.value: self.on_change(sv))
        super().__init__(root.root, textvariable=self.value)
        self.feedback_var = feedback_var
        self.validator = validator

    def on_change(self, value_var: tkinter.StringVar):
        """
        Handle changes to the input.

        Args:
            value_var: Input value variable
        """
        self.feedback_var.set(self.validator(value_var.get()))


class InputGroup:
    """
    Label/input group for settings window.

    Attributes:
        label_elem: Label element for input
        feedback_elem: Element for displaying field feedback
        input_elem: GUI input element
        frame: GUI frame for input group
    """
    label_elem: Any
    feedback: tkinter.StringVar
    feedback_elem: Any
    input_elem: Any
    frame: tkinter.Frame

    def __init__(self, root: 'SettingsWindow', label: str):
        self.frame = tkinter.Frame(root)
        # Pack label element
        self.label_elem = tkinter.Label(self.frame, text=label, justify=tkinter.LEFT)
        self.label_elem.grid(row=0, column=0, sticky='w')
        self.label_elem.pack(anchor='w')
        # Pack feedback element
        self.feedback = tkinter.StringVar()
        self.feedback_elem = tkinter.Label(self.frame, textvariable=self.feedback, fg='red')
        self.feedback_elem.grid(row=1, column=0, sticky='w')
        self.feedback_elem.pack(anchor='w')

    @property
    def root(self) -> tkinter.Frame:
        """
        More intuitive access of input group frame.
        """
        return self.frame

    # def update_feedback(self, feedback: str):
    #     """
    #     Update feedback label.
    #
    #     Args:
    #         feedback: Feedback to update with (blank if no feedback)
    #     """
    #     # self.feedback_elem.

    def pack(self, input_elem: Any):
        """
        Pack the input group.
        """
        self.input_elem = input_elem
        self.input_elem.grid(row=2, column=0, sticky='we')
        self.input_elem.pack(anchor='nw', fill=tkinter.X, expand=False)

        self.frame.pack(anchor='nw', fill=tkinter.X, expand=False)


class SettingsWindow(tkinter.Tk):
    """
    Root settings window for GUI application.

    Attributes:
        _title: Title of window.
        width: Width of window
        height: Height of window
        nrsc5_path: Variable for path to NRSC5 executable
        program: Variable for HD Radio program
        ppm: Variable for PPM error correction
        save_dir: Variable for directory to save weather and traffic images to
        logging: Variable for whether to show logging information
        art: Variable for whether to display album/station art
    """
    _title: str
    width: int
    height: int
    nrsc5_path: tkinter.StringVar
    program: tkinter.StringVar
    ppm: tkinter.StringVar
    save_dir: tkinter.StringVar
    logging: tkinter.BooleanVar
    art: tkinter.BooleanVar

    def __init__(self, title: str, width: int, height: int):
        super().__init__()
        self.window_title = title
        self.grid_columnconfigure(0, weight=1)
        # Setup components

        # self.nrsc5_path__label = tkinter.Label(self, text='NRSC-5 Executable Path:')
        # self.nrsc5_path__label.grid(row=0, column=0, sticky='we')
        # self.nrsc5_path__input = tkinter.Entry(self)
        # self.nrsc5_path__input.grid(row=0, column=1, sticky='we')
        self.width = width
        self.height = height
        self.geometry(f'{self.width}x{self.height}')
        self.setup_components()

    def setup_components(self):
        """
        Setup the UI components.
        """
        nrsc5_input_group = InputGroup(self, 'NRSC-5 Executable Path')
        nrsc5_input = NRSC5PathInput(nrsc5_input_group)
        nrsc5_input_group.pack(nrsc5_input)
        self.nrsc5_path = nrsc5_input.value

        program_input_group = InputGroup(self, 'HD Radio program, for stations with subchannels')
        program_input = ProgramInput(program_input_group)
        program_input_group.pack(program_input)
        self.program = program_input.value

        ppm_input_group = InputGroup(self, 'PPM error correction')
        ppm_input = PPMInput(ppm_input_group)
        ppm_input_group.pack(ppm_input)
        self.ppm = ppm_input.value

        save_dir_input_group = InputGroup(
            self,
            'Directory to save weather and traffic images to (leave blank to not save)'
        )
        save_dir_input = SaveDirInput(save_dir_input_group)
        save_dir_input_group.pack(save_dir_input)
        self.save_dir = save_dir_input.value

        logging_checkbox = CheckboxInput(self, label='Show logging information')
        logging_checkbox.pack(anchor='w')
        self.logging = logging_checkbox.is_checked

        art_checkbox = CheckboxInput(self, label='Display album/station art')
        art_checkbox.pack(anchor='w')
        self.art = art_checkbox.is_checked

        submit_button = tkinter.Button(self, text='Submit', command=self.handle_submit)
        submit_button.pack(anchor='w')

    @property
    def window_title(self) -> str:
        return self._title

    @window_title.setter
    def window_title(self, value: str):
        """
        Set title for class and window.
        """
        self._title = value
        super().title(value)

    def handle_submit(self):
        """
        Handle form submit.
        """
        valid = Settings.validate_all_fields(
            self.nrsc5_path.get(),
            self.program.get(),
            self.ppm.get(),
            self.save_dir.get(),
            self.logging.get(),
            self.art.get()
        )
        if not valid:
            messagebox.showerror(
                title='Invalid Settings',
                message='At least one of the settings you entered is invalid. See form for more details.'
            )


class CheckboxInput(tkinter.Checkbutton):
    """
    Checkbox input.

    Attributes:
        is_checked: Whether the button is checked
    """
    is_checked: tkinter.BooleanVar

    def __init__(self, root: SettingsWindow, label: str, default: bool = False):
        self.is_checked = tkinter.BooleanVar(value=default)
        super().__init__(root, text=label, variable=self.is_checked, onvalue=True, offvalue=False, bg='black', pady=5)


class NRSC5PathInput(TextInput):
    """
    NRSC5 executable path input.
    """

    def __init__(self, input_group: InputGroup):
        super().__init__(
            input_group,
            self.validate,
            input_group.feedback,
            default_value='/usr/local/bin/nrsc5'
        )

    @staticmethod
    def validate(value: str):
        if value == '':
            return 'Please enter path to NRSC-5 executable'
        if not os.path.isfile(value):
            return 'Path not valid'
        return ''


class ProgramInput(TextInput):
    """
    HD Radio program number.
    """

    def __init__(self, input_group: InputGroup):
        super().__init__(
            input_group,
            self.validate,
            input_group.feedback,
            default_value='0'
        )

    @staticmethod
    def validate(value: str):
        if value == '':
            return 'Please enter HD Radio program'
        try:
            value = int(value)
        except ValueError:
            pass
        if not validate(value, {'type': 'integer', 'min': 0}):
            return 'Program must be a number greater than 0'
        return ''


class PPMInput(TextInput):
    """
    PPM error correction input.
    """

    def __init__(self, input_group: InputGroup):
        super().__init__(
            input_group,
            self.validate,
            input_group.feedback,
            default_value='0'
        )

    @staticmethod
    def validate(value: str):
        if value == '':
            return 'Please enter PPM error correction'
        try:
            int(value)
        except ValueError:
            return 'Value must be an integer'
        return ''


class SaveDirInput(TextInput):
    """
    Directory to save weather and traffic images to.
    """

    def __init__(self, input_group: InputGroup):
        super().__init__(
            input_group,
            self.validate,
            input_group.feedback,
            default_value=''
        )

    @staticmethod
    def validate(value: str) -> str:
        if value == '':
            return ''
        if not os.path.isdir(value):
            return 'Not a valid directory'
        return ''


if __name__ == '__main__':
    settings = SettingsWindow('Test Title', 400, 200)

    settings.mainloop()

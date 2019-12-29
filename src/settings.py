import tkinter
from typing import Any, Callable, List, Dict
from cerberus import Validator
import os


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

    def __init__(self, root: 'InputGroup', validator: Callable, feedback_var: tkinter.StringVar, default_value: str = ''):
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
    """
    _title: str
    width: int
    height: int

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


if __name__ == '__main__':
    settings = SettingsWindow('Test Title', 400, 200)

    nrsc5_input = InputGroup(settings, 'NRSC-5 Executable Path:')

    def validate_nrsc5_input(value: str):
        if value == '':
            return 'Please enter path to NRSC-5 executable'
        if not os.path.isfile(value):
            return 'Path not valid'
        return ''

    entry = TextInput(nrsc5_input, validate_nrsc5_input, nrsc5_input.feedback, default_value='/usr/local/bin/nrsc5')
    nrsc5_input.pack(entry)

    program_input = InputGroup(settings, 'HD Radio program, for stations with subchannels')

    def validate_program_input(value: str):
        if value == '':
            return 'Please enter HD Radio program'
        try:
            value = int(value)
        except ValueError:
            pass
        if not validate(value, {'type': 'integer', 'min': 0}):
            return 'Program must be a number greater than 0'
        return ''

    entry = TextInput(program_input, validate_program_input, program_input.feedback, default_value='0')
    program_input.pack(entry)

    settings.mainloop()

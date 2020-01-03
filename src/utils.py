"""
Utility functions.
"""

from datetime import datetime


def timestamp(time: datetime = datetime.now()) -> str:
    """
    Timestamp format used throughout project.

    Args:
        time: Time of the timestamp

    Returns:
        Formatted timestamp
    """
    return time.strftime('%m-%d-%Y_%I-%M-%S_%p')

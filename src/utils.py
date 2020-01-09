"""
Utility functions.
"""

from datetime import datetime
from typing import List


def timestamp(time: datetime = datetime.now()) -> str:
    """
    Timestamp format used throughout project.

    Args:
        time: Time of the timestamp

    Returns:
        Formatted timestamp
    """
    return time.strftime('%m-%d-%Y_%I-%M-%S_%p')


def get_all_gain_levels() -> List[float]:
    """
    Get all possible gain levels that can be set.

    Returns:
        All possible gain levels
    """
    gains = []
    current_gain = 0.0
    while current_gain <= 49.6:
        gains.append(current_gain)
        current_gain = round(current_gain + 0.1, 1)
    return gains

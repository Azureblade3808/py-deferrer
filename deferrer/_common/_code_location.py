from __future__ import annotations

from types import FrameType


def get_code_location(frame: FrameType, /) -> str:
    """
    Extract location of code currently being executed in a given frame.
    """

    filename = frame.f_code.co_filename
    line_number = frame.f_lineno
    code_location = f"file: {filename!r}, line: {line_number}"
    return code_location

from __future__ import annotations

__all__ = [
    "get_current_frame",
    "get_outer_frame",
    "is_class_frame",
    "is_global_frame",
]

import re
import sys
from types import FrameType

from ._opcode import Opcode, build_instruction_pattern


def get_current_frame() -> FrameType:
    """
    Returns the frame of the caller.

    Examples
    --------
    >>> def foo():  # L0
    ...     frame = get_current_frame()
    ...     print(
    ...         frame.f_code.co_name,
    ...         frame.f_lineno - frame.f_code.co_firstlineno,  # L4
    ...     )

    >>> foo()
    foo 4
    """

    return sys._getframe(1)  # pyright: ignore[reportPrivateUsage]


def get_outer_frame() -> FrameType:
    """
    Returns the frame of the caller of caller.

    Examples
    --------
    >>> def foo():  # L0
    ...     def inner():
    ...         frame = get_outer_frame()
    ...         print(
    ...             frame.f_code.co_name,
    ...             frame.f_lineno - frame.f_code.co_firstlineno,
    ...         )
    ...     inner()  # L7

    >>> foo()
    foo 7
    """

    return sys._getframe(2)  # pyright: ignore[reportPrivateUsage]


def is_global_frame(frame: FrameType, /) -> bool:
    """
    Detects if the given frame is a global frame.

    Examples
    --------
    >>> import sys

    >>> print(is_global_frame(sys._getframe()))
    True

    >>> class C:
    ...     print(is_global_frame(sys._getframe()))
    False

    >>> def f():
    ...     print(is_global_frame(sys._getframe()))

    >>> f()
    False
    """

    return frame.f_locals is frame.f_globals


def is_class_frame(frame: FrameType, /) -> bool:
    """
    Detects if the given frame is a class frame.

    Examples
    --------
    >>> import sys

    >>> print(is_class_frame(sys._getframe()))
    False

    >>> class C:
    ...     print(is_class_frame(sys._getframe()))
    True

    >>> def f():
    ...     print(is_class_frame(sys._getframe()))

    >>> f()
    False

    >>> def fake_class():
    ...     global __name__, __module__, __qualname__
    ...     if False: __name__, __module__, __qualname__
    ...     print(is_class_frame(sys._getframe()))

    >>> fake_class()
    False
    """

    # Typical class code will begin like:
    #
    #   RESUME
    #   LOAD_NAME "__name__"
    #   STORE "__module__"
    #   LOAD_CONST {qualname}
    #   STORE "__qualname__"
    #   ...

    code = frame.f_code

    names = code.co_names
    if (
        len(names) < 3
        or names[0] != "__name__"
        or names[1] != "__module__"
        or names[2] != "__qualname__"
    ):
        return False

    code_bytes = code.co_code
    if re.match(_PATTERN, code_bytes) is None:
        return False

    return True


_PATTERN = re.compile(
    pattern=(
        "".join(
            [
                # "COPY_FREE_VARS ?". Optional.
                "(?:%s)?" % build_instruction_pattern(Opcode.COPY_FREE_VARS),
                # "RESUME". Optional.
                "(?:%s)?" % build_instruction_pattern(Opcode.RESUME),
                # "LOAD_NAME 0 (__name__)".
                build_instruction_pattern(Opcode.LOAD_NAME, 0),
                # "STORE_NAME 1 (__module__)".
                build_instruction_pattern(Opcode.STORE_NAME, 1),
                # "LOAD_CONST 0 {qualname}".
                build_instruction_pattern(Opcode.LOAD_CONST, 0),
                # "STORE_NAME 2 (__qualname__)"
                build_instruction_pattern(Opcode.STORE_NAME, 2),
            ]
        ).encode("iso8859-1")
    ),
    flags=re.DOTALL,
)

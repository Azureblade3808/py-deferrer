from __future__ import annotations

__all__ = [
    "get_outer_frame",
    "is_class_frame",
    "is_global_frame",
]

import sys
from collections.abc import Sequence
from types import FrameType

from ._opcode import Opcode


def get_outer_frame() -> FrameType:
    """
    Returns the frame of the caller of caller.

    Examples
    --------
    >>> def foo():  # L0
    ...     def inner():
    ...         frame = get_outer_frame()
    ...         print (
    ...             frame.f_code.co_name,
    ...             frame.f_lineno - frame.f_code.co_firstlineno,
    ...         )
    ...     inner()  # L7

    >>> foo()
    foo 7
    """

    frame = sys._getframe(2)  # pyright: ignore[reportPrivateUsage]
    return frame


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
    if not _sequence_has_prefix(names, ("__name__", "__module__", "__qualname__")):
        return False

    code_bytes = code.co_code
    # In some cases (e.g. embedded class), there may be a COPY_FREE_VARS instruction.
    if _sequence_has_prefix(code_bytes, (Opcode.COPY_FREE_VARS,)):
        code_bytes = code_bytes[2:]
    if not _sequence_has_prefix(
        code_bytes,
        (
            Opcode.RESUME,
            0,
            Opcode.LOAD_NAME,
            0,  # __name__
            Opcode.STORE_NAME,
            1,  # __module__
            Opcode.LOAD_CONST,
            0,
            Opcode.STORE_NAME,
            2,  # __qualname__
        ),
    ):
        return False

    return True


def _sequence_has_prefix(
    sequence: Sequence[object], prefix: Sequence[object], /
) -> bool:
    return tuple(sequence[: len(prefix)]) == tuple(prefix)

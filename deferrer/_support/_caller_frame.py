from __future__ import annotations

__all__ = ["get_caller_frame"]

import sys
from collections.abc import Sequence
from types import FrameType
from typing import override

from ._opcode import Opcode


def get_caller_frame() -> FrameType:
    """
    Returns the frame of the caller of caller.

    Raises
    ------
    If the pending result is a global frame or a class frame, a
    `RuntimeError` will be raised.

    Examples
    --------
    >>> def foo():  # L0
    ...     def mocked_defer():
    ...         frame = get_caller_frame()
    ...         return (
    ...             frame.f_code.co_name,
    ...             frame.f_lineno - frame.f_code.co_firstlineno,
    ...         )
    ...     print(*mocked_defer())  # L7

    >>> foo()
    foo 7
    """

    frame = sys._getframe(2)  # pyright: ignore[reportPrivateUsage]
    frame.f_code.co_firstlineno

    if _is_global_frame(frame):
        raise RuntimeError("cannot be used in global scope")

    if _is_class_frame(frame):
        raise RuntimeError("cannot be used in class scope")

    return frame


def _is_global_frame(frame: FrameType, /) -> bool:
    """
    Detects if the given frame is a global frame.
    """

    return frame.f_locals is frame.f_globals


def _is_class_frame(frame: FrameType, /) -> bool:
    """
    Detects if the given frame is a class frame.
    """

    if (
        True
        and _sequence_has_prefix(frame.f_code.co_consts, _CLASS_CODE_PREFIX_CONSTS)
        and _sequence_has_prefix(frame.f_code.co_names, _CLASS_CODE_PREFIX_NAMES)
        and _sequence_has_prefix(frame.f_code.co_code, _CLASS_CODE_PREFIX_BYTES)
    ):
        return True

    return False


def _sequence_has_prefix(
    sequence: Sequence[object], prefix: Sequence[object], /
) -> bool:
    return tuple(sequence[: len(prefix)]) == tuple(prefix)


class _AnyStr:
    """
    An object that equals any `str`.
    """

    @override
    def __eq__(self, other: object, /) -> bool:
        return isinstance(other, str)


_CLASS_CODE_PREFIX_CONSTS = (_AnyStr(),)
_CLASS_CODE_PREFIX_NAMES = ("__name__", "__module__", "__qualname__")
_CLASS_CODE_PREFIX_BYTES = bytes(
    [
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
    ]
)

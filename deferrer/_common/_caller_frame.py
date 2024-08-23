from __future__ import annotations

__all__ = ["get_caller_frame"]

import sys
from collections.abc import Sequence
from types import FrameType
from typing import override

from ._opcode import Opcode


def get_caller_frame() -> FrameType:
    frame = sys._getframe(2)  # pyright: ignore[reportPrivateUsage]

    if _is_global_frame(frame):
        raise RuntimeError("cannot be used in global scope")

    if _is_class_frame(frame):
        raise RuntimeError("cannot be used in class scope")

    return frame


def _is_global_frame(frame: FrameType, /) -> bool:
    return frame.f_locals is frame.f_globals


def _is_class_frame(frame: FrameType, /) -> bool:
    code = frame.f_code

    code_consts = code.co_consts
    if not _sequence_has_prefix(code_consts, _CLASS_CODE_PREFIX_CONSTS):
        return False

    code_names = code.co_names
    if not _sequence_has_prefix(code_names, _CLASS_CODE_PREFIX_NAMES):
        return False

    code_bytes = code.co_code
    if not _sequence_has_prefix(code_bytes, _CLASS_CODE_PREFIX_BYTES):
        return False

    return True


def _sequence_has_prefix(
    sequence: Sequence[object], prefix: Sequence[object], /
) -> bool:
    return tuple(sequence[: len(prefix)]) == tuple(prefix)


class _AnyStr:
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

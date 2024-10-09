from __future__ import annotations

__all__ = [
    "Opcode",
    "build_code_byte_sequence",
    "build_code_bytes",
]

import sys
from collections.abc import Sequence
from enum import IntEnum
from types import MappingProxyType
from typing import cast

from opcode import _cache_format  # pyright: ignore[reportAttributeAccessIssue]
from opcode import opmap


class Opcode(IntEnum):
    """
    All op-code values used in this project.
    """

    COPY_FREE_VARS = opmap["COPY_FREE_VARS"]
    JUMP_BACKWARD = opmap["JUMP_BACKWARD"]
    LOAD_CONST = opmap["LOAD_CONST"]
    LOAD_NAME = opmap["LOAD_NAME"]
    MAKE_CELL = opmap["MAKE_CELL"]
    POP_TOP = opmap["POP_TOP"]
    RESUME = opmap["RESUME"]
    RETURN_VALUE = opmap["RETURN_VALUE"]
    STORE_FAST = opmap["STORE_FAST"]
    STORE_NAME = opmap["STORE_NAME"]
    STORE_DEREF = opmap["STORE_DEREF"]

    if sys.version_info >= (3, 13):
        TO_BOOL = opmap["TO_BOOL"]

    if sys.version_info >= (3, 12):
        POP_JUMP_IF_FALSE = opmap["POP_JUMP_IF_FALSE"]

    if sys.version_info >= (3, 11) and sys.version_info < (3, 12):
        JUMP_IF_FALSE_OR_POP = opmap["JUMP_IF_FALSE_OR_POP"]


_n_caches_map = MappingProxyType(
    {
        cast("Opcode", opcode): (
            0 if (d := _cache_format.get(name)) is None else sum(d.values())
        )
        for name, opcode in Opcode._member_map_.items()
    }
)


def build_code_bytes(opcode: Opcode, arg: int = 0) -> bytes:
    return bytes(build_code_byte_sequence(opcode, arg))


def build_code_byte_sequence(
    opcode: Opcode, arg: int = 0, *, cache_value: int = 0
) -> Sequence[int]:
    return [opcode, arg] + [cache_value] * (_n_caches_map[opcode] * 2)

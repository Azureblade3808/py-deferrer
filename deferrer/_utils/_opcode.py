from __future__ import annotations

__all__ = [
    "Opcode",
    "build_instruction_code_bytes",
    "build_instruction_pattern",
    "extract_argument_from_instruction",
]

import sys
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
    EXTENDED_ARG = opmap["EXTENDED_ARG"]
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


def build_instruction_code_bytes(opcode: Opcode, argument: int = 0) -> bytes:
    assert 0 <= opcode <= ((1 << 8) - 1)
    assert 0 <= argument <= ((1 << 32) - 1)

    argument_bytes = _get_bytes(argument)

    code_byte_list: list[int] = []
    for argument_byte in argument_bytes[:-1]:
        code_byte_list.append(Opcode.EXTENDED_ARG)
        code_byte_list.append(argument_byte)
    else:
        code_byte_list.append(opcode)
        code_byte_list.append(argument_bytes[-1])
    code_byte_list.extend([0] * (_n_caches_map[opcode] * 2))

    code_bytes = bytes(code_byte_list)
    return code_bytes


def build_instruction_pattern(opcode: Opcode, argument: int | None = None) -> str:
    if argument is None:
        argument_bytes = None
    else:
        argument_bytes = _get_bytes(argument)

    pattern = ""

    if argument_bytes is None:
        pattern += r"(?:\x%02x.){0,3}" % Opcode.EXTENDED_ARG
    else:
        pattern += "".join(
            r"\x%02x\x%02x" % (Opcode.EXTENDED_ARG, argument_byte)
            for argument_byte in argument_bytes[:-1]
        )

    pattern += r"\x%02x" % opcode

    if argument_bytes is None:
        pattern += "."
    else:
        pattern += r"\x%02x" % argument_bytes[-1]

    n_caches = _n_caches_map[opcode]
    if n_caches > 0:
        pattern += ".{%d}" % (n_caches * 2)

    return pattern


def extract_argument_from_instruction(code_bytes: bytes, /) -> int:
    argument = 0

    for i in range(0, len(code_bytes), 2):
        argument <<= 8
        argument |= code_bytes[i + 1]

        if code_bytes[i] != Opcode.EXTENDED_ARG:
            break

    return argument


def _get_bytes(value: int, /) -> bytes:
    assert value >= 0
    n_bytes = 1 if value == 0 else (value.bit_length() + 7) // 8
    bytes_ = value.to_bytes(n_bytes, "big", signed=False)
    return bytes_

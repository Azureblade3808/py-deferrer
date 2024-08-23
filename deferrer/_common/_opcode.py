from __future__ import annotations

__all__ = ["Opcode"]

from dis import opmap
from enum import IntEnum


class Opcode(IntEnum):
    COPY_FREE_VARS = opmap["COPY_FREE_VARS"]
    LOAD_CONST = opmap["LOAD_CONST"]
    LOAD_NAME = opmap["LOAD_NAME"]
    POP_JUMP_IF_FALSE = opmap["POP_JUMP_IF_FALSE"]
    POP_TOP = opmap["POP_TOP"]
    RESUME = opmap["RESUME"]
    RETURN_VALUE = opmap["RETURN_VALUE"]
    STORE_FAST = opmap["STORE_FAST"]
    STORE_NAME = opmap["STORE_NAME"]

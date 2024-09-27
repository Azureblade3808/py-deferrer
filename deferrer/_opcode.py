from __future__ import annotations

__all__ = ["Opcode"]

import sys
from dis import opmap
from enum import IntEnum


class Opcode(IntEnum):
    """
    All op-code values used in this project.
    """

    COPY_FREE_VARS = opmap["COPY_FREE_VARS"]
    LOAD_CONST = opmap["LOAD_CONST"]
    LOAD_NAME = opmap["LOAD_NAME"]
    MAKE_CELL = opmap["MAKE_CELL"]
    POP_TOP = opmap["POP_TOP"]
    RESUME = opmap["RESUME"]
    RETURN_VALUE = opmap["RETURN_VALUE"]
    STORE_FAST = opmap["STORE_FAST"]
    STORE_NAME = opmap["STORE_NAME"]
    STORE_DEREF = opmap["STORE_DEREF"]

    if (3, 12) <= sys.version_info < (3, 13):
        POP_JUMP_IF_FALSE = opmap["POP_JUMP_IF_FALSE"]

    if (3, 11) <= sys.version_info < (3, 12):
        JUMP_IF_FALSE_OR_POP = opmap["JUMP_IF_FALSE_OR_POP"]

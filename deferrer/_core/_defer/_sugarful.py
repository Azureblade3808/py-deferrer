from __future__ import annotations

__all__ = ["Defer"]

import sys
from collections.abc import Callable
from types import CellType, FunctionType
from typing import Any, Final, Literal, cast, final
from warnings import warn

from .._deferred_actions import DeferredAction, ensure_deferred_actions
from ..._utils import (
    WILDCARD,
    Opcode,
    build_code_byte_sequence,
    build_code_bytes,
    get_code_location,
    get_outer_frame,
    sequence_has_prefix,
    sequence_has_suffix,
)

_MISSING = cast("Any", object())


class Defer:
    @staticmethod
    def __bool__() -> Literal[False]:
        """
        **DO NOT INVOKE**

        This method is only meant to be used during `defer and ...`.

        If used in other ways, the return value will always be `False`
        and a warning will be emitted.
        """

        frame = get_outer_frame()

        code = frame.f_code
        code_bytes = code.co_code
        i_code_byte = frame.f_lasti

        if not sequence_has_prefix(
            code_bytes[i_code_byte:], _expected_code_bytes_prefix
        ):
            code_location = get_code_location(frame)
            message = (
                ""
                + (
                    ""
                    + "Method `defer.__bool__()` is called in an unsupported way ("
                    + code_location
                    + ")."
                )
                + " "
                + "It is only designed to be invoked during `defer and ...`."
            )
            warn(message)
            return False

        global_scope = frame.f_globals
        local_scope = frame.f_locals

        dummy_code_bytes = bytes()
        dummy_closure = ()
        dummy_consts = code.co_consts

        # If the original function has local variables, pass their current values by
        # appending these values to constants and using some instruction pairs of
        # "LOAD_CONST" and "STORE_FAST".
        local_var_names = code.co_varnames
        for i_local_var, name in enumerate(local_var_names):
            if (value := local_scope.get(name, _MISSING)) is _MISSING:
                # The value does not exist, so there is nothing to store.
                continue

            dummy_code_bytes += build_code_bytes(Opcode.LOAD_CONST, len(dummy_consts))
            dummy_code_bytes += build_code_bytes(Opcode.STORE_FAST, i_local_var)
            dummy_consts += (value,)

        # If the original function has cell variables, add some instructions of
        # "MAKE_CELL".
        # For non-local cell variables, pass their current values by appending these
        # values to constants and using some instruction pairs of "LOAD_CONST" and
        # "STORE_DEREF".
        cell_var_names = code.co_cellvars
        next_i_nonlocal_cell_var = len(local_var_names)
        for name in cell_var_names:
            try:
                i_local_var = local_var_names.index(name)
            except ValueError:
                i_local_var = None

            if i_local_var is not None:
                dummy_code_bytes += build_code_bytes(Opcode.MAKE_CELL, i_local_var)
            else:
                i_nonlocal_cell_var = next_i_nonlocal_cell_var
                next_i_nonlocal_cell_var += 1

                dummy_code_bytes += build_code_bytes(
                    Opcode.MAKE_CELL, i_nonlocal_cell_var
                )

                if (value := local_scope.get(name, _MISSING)) is _MISSING:
                    # The value does not exist, so there is nothing to store.
                    continue

                dummy_code_bytes += build_code_bytes(
                    Opcode.LOAD_CONST, len(dummy_consts)
                )
                dummy_code_bytes += build_code_bytes(
                    Opcode.STORE_DEREF, i_nonlocal_cell_var
                )
                dummy_consts += (value,)

        # If the original function has free variables, create a closure based on their
        # current values, and add a "COPY_FREE_VARS" instruction.
        free_var_names = code.co_freevars
        n_free_vars = len(free_var_names)
        if n_free_vars != 0:
            dummy_closure += tuple(
                (
                    CellType()
                    if (value := frame.f_locals.get(name, _MISSING)) is _MISSING
                    else CellType(value)
                )
                for name in free_var_names
            )
            dummy_code_bytes += build_code_bytes(Opcode.COPY_FREE_VARS, n_free_vars)

        # Copy the bytecode of the RHS part in `defer and ...` into the dummy function.
        n_skipped_instructions = code_bytes[i_code_byte + _jumping_start_offset + 1]
        n_skipped_bytes = n_skipped_instructions * 2
        dummy_code_bytes += code_bytes[
            (i_code_byte + _rhs_offset) : (
                i_code_byte + _jumping_stop_offset + n_skipped_bytes
            )
        ]

        # For Python 3.13, if the current expression is the last expression in a loop,
        # there will be a duplicated `POP_TOP + JUMP_BACKWARD` instruction pair.
        # Cut it off before it can cause any trouble.
        if sequence_has_suffix(dummy_code_bytes, _unneeded_code_bytes_suffix):
            dummy_code_bytes = dummy_code_bytes[: -len(_unneeded_code_bytes_suffix)]

        # The dummy function should return something. The simplest way is to return
        # whatever value is currently active.
        dummy_code_bytes += build_code_bytes(Opcode.RETURN_VALUE)

        # The dummy function will be called with no argument.
        dummy_code = code.replace(
            co_argcount=0,
            co_posonlyargcount=0,
            co_kwonlyargcount=0,
            co_code=dummy_code_bytes,
            co_consts=dummy_consts,
            co_linetable=bytes(),
            co_exceptiontable=bytes(),
        )

        new_function = FunctionType(
            code=dummy_code, globals=global_scope, closure=dummy_closure
        )
        deferred_call = _DeferredCall(new_function)

        deferred_actions = ensure_deferred_actions(frame)
        deferred_actions.append(deferred_call)

        return False


_expected_code_bytes_prefix: list[int]
"""
Code bytes pattern when `defer.__bool__()` is invoked upon `defer and ...`.
"""

_jumping_start_offset: int
"""
Distance in bytes between the current instruction and the jumping instruction.
"""

_jumping_stop_offset: int
"""
Distance in bytes between the current instruction and the next instruction to the
jumping instruction.
"""

_rhs_offset: int
"""
Distance in bytes between the current instruction and the instructions of RHS in
`defer and ...`.
"""


if sys.version_info >= (3, 13) and sys.version_info < (3, 14):
    # ```
    #     LOAD_GLOBAL ? (defer)
    #     COPY
    # --> TO_BOOL
    #     POP_JUMP_IF_FALSE ?
    #     CACHE
    #     POP_TOP
    #     <???>
    # ```

    _expected_code_bytes_prefix = []

    _expected_code_bytes_prefix.extend(
        build_code_byte_sequence(Opcode.TO_BOOL, cache_value=WILDCARD)
    )
    _jumping_start_offset = len(_expected_code_bytes_prefix)

    _expected_code_bytes_prefix.extend(
        build_code_byte_sequence(
            Opcode.POP_JUMP_IF_FALSE, WILDCARD, cache_value=WILDCARD
        )
    )
    _jumping_stop_offset = len(_expected_code_bytes_prefix)

    _expected_code_bytes_prefix.extend(
        build_code_byte_sequence(Opcode.POP_TOP, cache_value=WILDCARD)
    )
    _rhs_offset = len(_expected_code_bytes_prefix)

if sys.version_info >= (3, 12) and sys.version_info < (3, 13):
    # ```
    #     LOAD_GLOBAL ? (defer)
    #     COPY
    # --> POP_JUMP_IF_FALSE ?
    #     POP_TOP
    #     <???>
    # ```

    _expected_code_bytes_prefix = []
    _jumping_start_offset = 0

    _expected_code_bytes_prefix.extend(
        build_code_byte_sequence(
            Opcode.POP_JUMP_IF_FALSE, WILDCARD, cache_value=WILDCARD
        )
    )
    _jumping_stop_offset = len(_expected_code_bytes_prefix)

    _expected_code_bytes_prefix.extend(
        build_code_byte_sequence(Opcode.POP_TOP, cache_value=WILDCARD)
    )
    _rhs_offset = len(_expected_code_bytes_prefix)

if sys.version_info >= (3, 11) and sys.version_info < (3, 12):
    # ```
    #     LOAD_GLOBAL ? (defer)
    # --> JUMP_IF_FALSE_OR_POP ?
    #     <???>
    # ```

    _expected_code_bytes_prefix = []
    _jumping_start_offset = 0

    _expected_code_bytes_prefix.extend(
        build_code_byte_sequence(
            Opcode.JUMP_IF_FALSE_OR_POP, WILDCARD, cache_value=WILDCARD
        )
    )
    _jumping_stop_offset = len(_expected_code_bytes_prefix)
    _rhs_offset = _jumping_stop_offset


_unneeded_code_bytes_suffix = (
    *build_code_byte_sequence(Opcode.POP_TOP, cache_value=WILDCARD),
    *build_code_byte_sequence(Opcode.JUMP_BACKWARD, WILDCARD, cache_value=WILDCARD),
)


@final
class _DeferredCall(DeferredAction):
    def __init__(self, body: Callable[[], Any], /) -> None:
        self._body: Final = body

    def perform(self, /) -> None:
        self._body()

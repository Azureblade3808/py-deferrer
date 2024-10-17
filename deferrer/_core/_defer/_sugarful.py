from __future__ import annotations

__all__ = ["Defer"]

import re
import sys
from collections.abc import Callable
from types import CellType, FunctionType
from typing import Any, Final, Literal, cast, final
from warnings import warn

from .._deferred_actions import DeferredAction, ensure_deferred_actions
from ..._utils import (
    Opcode,
    build_instruction_code_bytes,
    build_instruction_pattern,
    extract_argument_from_instruction,
    get_code_location,
    get_outer_frame,
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
        for _ in range(3):
            temp_i_code_byte = i_code_byte - 2
            if (
                temp_i_code_byte < 0
                or code_bytes[temp_i_code_byte] != Opcode.EXTENDED_ARG
            ):
                break
            i_code_byte = temp_i_code_byte
        code_bytes_0 = code_bytes[i_code_byte:]

        match_0 = re.match(_pattern_0, code_bytes_0)
        if match_0 is None:
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

        n_skipped_bytes = extract_argument_from_instruction(match_0.group(1)) * 2
        code_bytes_1 = match_0.group(2)[:n_skipped_bytes]

        match_1 = re.fullmatch(_pattern_1, code_bytes_1)
        assert match_1 is not None
        code_bytes_2 = match_1.group(1)

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

            dummy_code_bytes += build_instruction_code_bytes(
                Opcode.LOAD_CONST, len(dummy_consts)
            )
            dummy_code_bytes += build_instruction_code_bytes(
                Opcode.STORE_FAST, i_local_var
            )
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
                dummy_code_bytes += build_instruction_code_bytes(
                    Opcode.MAKE_CELL, i_local_var
                )
            else:
                i_nonlocal_cell_var = next_i_nonlocal_cell_var
                next_i_nonlocal_cell_var += 1

                dummy_code_bytes += build_instruction_code_bytes(
                    Opcode.MAKE_CELL, i_nonlocal_cell_var
                )

                if (value := local_scope.get(name, _MISSING)) is _MISSING:
                    # The value does not exist, so there is nothing to store.
                    continue

                dummy_code_bytes += build_instruction_code_bytes(
                    Opcode.LOAD_CONST, len(dummy_consts)
                )
                dummy_code_bytes += build_instruction_code_bytes(
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
            dummy_code_bytes += build_instruction_code_bytes(
                Opcode.COPY_FREE_VARS, n_free_vars
            )

        # Copy the bytecode of the RHS part in `defer and ...` into the dummy function.
        dummy_code_bytes += code_bytes_2

        # The dummy function should return something. The simplest way is to return
        # whatever value is currently active.
        dummy_code_bytes += build_instruction_code_bytes(Opcode.RETURN_VALUE)

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


if sys.version_info >= (3, 13) and sys.version_info < (3, 14):
    # ```
    #     LOAD_GLOBAL ? (defer)
    #     COPY
    # --> TO_BOOL
    #     POP_JUMP_IF_FALSE ?
    #     POP_TOP
    #     <???>
    # ```

    _pattern_0 = re.compile(
        pattern=(
            (
                "%(TO_BOOL)s(%(POP_JUMP_IF_FALSE)s)(%(POP_TOP)s.*)"
                % {
                    "TO_BOOL": build_instruction_pattern(Opcode.TO_BOOL),
                    "POP_JUMP_IF_FALSE": build_instruction_pattern(
                        Opcode.POP_JUMP_IF_FALSE
                    ),
                    "POP_TOP": build_instruction_pattern(Opcode.POP_TOP),
                }
            ).encode("iso8859-1")
        ),
        flags=re.DOTALL,
    )
    _pattern_1 = re.compile(
        pattern=(
            (
                "%(POP_TOP)s(.*?)(?:%(POP_TOP)s%(JUMP_BACKWARD)s)?"
                % {
                    "POP_TOP": build_instruction_pattern(Opcode.POP_TOP),
                    "JUMP_BACKWARD": build_instruction_pattern(Opcode.JUMP_BACKWARD),
                }
            ).encode("iso8859-1")
        ),
        flags=re.DOTALL,
    )

if sys.version_info >= (3, 12) and sys.version_info < (3, 13):
    # ```
    #     LOAD_GLOBAL ? (defer)
    #     COPY
    # --> POP_JUMP_IF_FALSE ?
    #     POP_TOP
    #     <???>
    # ```

    _pattern_0 = re.compile(
        pattern=(
            (
                "(%(POP_JUMP_IF_FALSE)s)(%(POP_TOP)s.*)"
                % {
                    "POP_JUMP_IF_FALSE": build_instruction_pattern(
                        Opcode.POP_JUMP_IF_FALSE
                    ),
                    "POP_TOP": build_instruction_pattern(Opcode.POP_TOP),
                }
            ).encode("iso8859-1")
        ),
        flags=re.DOTALL,
    )
    _pattern_1 = re.compile(
        pattern=(
            (
                "%(POP_TOP)s(.*)"
                % {
                    "POP_TOP": build_instruction_pattern(Opcode.POP_TOP),
                }
            ).encode("iso8859-1")
        ),
        flags=re.DOTALL,
    )

if sys.version_info >= (3, 11) and sys.version_info < (3, 12):
    # ```
    #     LOAD_GLOBAL ? (defer)
    # --> JUMP_IF_FALSE_OR_POP ?
    #     <???>
    # ```

    _pattern_0 = re.compile(
        pattern=(
            (
                "(%(JUMP_IF_FALSE_OR_POP)s)(.*)"
                % {
                    "JUMP_IF_FALSE_OR_POP": build_instruction_pattern(
                        Opcode.JUMP_IF_FALSE_OR_POP
                    ),
                }
            ).encode("iso8859-1")
        ),
        flags=re.DOTALL,
    )
    _pattern_1 = re.compile(
        pattern="(.*)".encode("iso8859-1"),
        flags=re.DOTALL,
    )


@final
class _DeferredCall(DeferredAction):
    def __init__(self, body: Callable[[], Any], /) -> None:
        self._body: Final = body

    def perform(self, /) -> None:
        self._body()

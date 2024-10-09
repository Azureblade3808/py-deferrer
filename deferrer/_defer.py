from __future__ import annotations

__all__ = ["defer"]

import sys
from collections.abc import Callable
from types import CellType, FunctionType
from typing import Any, Final, Generic, Literal, ParamSpec, cast, final
from warnings import warn

from ._code_location import get_code_location
from ._defer_scope import ensure_deferred_actions
from ._deferred_actions import DeferredAction
from ._frame import get_outer_frame
from ._opcode import Opcode, build_code_byte_sequence, build_code_bytes
from ._sequence_matching import WILDCARD, sequence_has_prefix, sequence_has_suffix

_P = ParamSpec("_P")

_MISSING = cast("Any", object())


@final
class Defer:
    """
    Provides `defer` functionality in both sugarful and sugarless ways.

    Examples
    --------
    >>> import sys
    >>> from deferrer import defer_scope

    >>> def f_0():
    ...     defer and print(0)
    ...     defer and print(1)
    ...     print(2)
    ...     defer and print(3)
    ...     defer and print(4)

    >>> if sys.version_info < (3, 12):
    ...     f_0 = defer_scope(f_0)

    >>> f_0()
    2
    4
    3
    1
    0

    >>> def f_1():
    ...     defer(print)(0)
    ...     defer(print)(1)
    ...     print(2)
    ...     defer(print)(3)
    ...     defer(print)(4)

    >>> if sys.version_info < (3, 12):
    ...     f_1 = defer_scope(f_1)

    >>> f_1()
    2
    4
    3
    1
    0
    """

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

    @staticmethod
    def __call__(callable: Callable[_P, Any], /) -> Callable[_P, None]:
        """
        Converts a callable into a deferred callable.

        Return value of the given callable will always be ignored.
        """

        frame = get_outer_frame()
        code_location = get_code_location(frame)

        deferred_callable = _DeferredCallable(callable, code_location)

        deferred_actions = ensure_deferred_actions(frame)
        deferred_actions.append(deferred_callable)

        return deferred_callable


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


defer = Defer()


@final
class _DeferredCall(DeferredAction):
    def __init__(self, body: Callable[[], Any], /) -> None:
        self._body: Final = body

    def perform(self, /) -> None:
        self._body()


@final
class _DeferredCallable(DeferredAction, Generic[_P]):
    _body: Final[Callable[..., Any]]
    _code_location: Final[str]

    _args_and_kwargs: tuple[tuple[Any, ...], dict[str, Any]] | None

    def __init__(self, body: Callable[_P, Any], /, code_location: str) -> None:
        self._body = body
        self._code_location = code_location

        self._args_and_kwargs = None

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> None:
        if self._args_and_kwargs is not None:
            raise RuntimeError("`defer(...)` gets further called more than once.")

        self._args_and_kwargs = (args, kwargs)

    def perform(self, /) -> None:
        body = self._body
        args_and_kwargs = self._args_and_kwargs

        if args_and_kwargs is not None:
            args, kwargs = args_and_kwargs
            body(*args, **kwargs)
            return

        try:
            body()
        except Exception as e:
            if isinstance(e, TypeError):
                traceback = e.__traceback__
                assert traceback is not None

                if traceback.tb_next is None:
                    # This `TypeError` was raised on function call, which means that
                    # there was a signature error.
                    # It is typically because a deferred callable with at least one
                    # required argument doesn't ever get further called with appropriate
                    # arguments.
                    code_location = self._code_location
                    message = (
                        f"`defer(...)` has never got further called ({code_location})."
                    )
                    warn(message)
                    return

            raise e

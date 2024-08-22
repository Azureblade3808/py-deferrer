from __future__ import annotations

__all__ = ["defer"]

import sys
from collections.abc import Callable
from dis import opmap
from types import CellType, FrameType, FunctionType
from typing import Any, Final, cast
from warnings import warn

type _DeferredCall = Callable[[], Any]

_MISSING = cast("Any", object())

_BYTE__COPY_FREE_VARS = opmap["COPY_FREE_VARS"]
_BYTE__LOAD_CONST = opmap["LOAD_CONST"]
_BYTE__STORE_FAST = opmap["STORE_FAST"]
_BYTE__POP_TOP = opmap["POP_TOP"]
_BYTE__POP_JUMP_IF_FALSE = opmap["POP_JUMP_IF_FALSE"]
_BYTE__RETURN_VALUE = opmap["RETURN_VALUE"]


class _Defer:
    @staticmethod
    def __call__[**P](callable: Callable[P, Any], /) -> _DeferredCallable[P]:
        code_location = _get_code_location(_get_caller_frame())
        deferred_callable = _DeferredCallable(callable, code_location)
        return deferred_callable

    def __bool__(self, /) -> bool:
        frame = _get_caller_frame()

        # The usage is `defer and ...` and the corresponding instructions should be:
        # ```
        #     LOAD_GLOBAL ? (defer)
        #     COPY
        # --> POP_JUMP_IF_FALSE ?
        #     POP_TOP
        #     <???>
        # ```
        # The current instruction is at the line prefixed by "-->", and the "<???>"
        # part stands for the `...` part in `defer and ...`.
        code = frame.f_code
        code_bytes = code.co_code
        i_code_byte = frame.f_lasti
        if not (
            len(code_bytes) - i_code_byte >= 4
            and code_bytes[i_code_byte + 0] == _BYTE__POP_JUMP_IF_FALSE
            and code_bytes[i_code_byte + 2] == _BYTE__POP_TOP
            and code_bytes[i_code_byte + 3] == 0
        ):
            code_location = _get_code_location(frame)
            message = (
                ""
                + (
                    ""
                    + "Method `defer.__bool__()` is called in an unsupported way("
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

        # If the original function has free variables, create a closure based on their
        # current values, and add a "COPY_FREE_VARS" instruction at the head of the
        # dummy function.
        free_var_names = code.co_freevars
        n_free_vars = len(free_var_names)
        if n_free_vars == 0:
            dummy_closure = ()
        else:
            dummy_closure = tuple(
                (
                    CellType()
                    if (value := frame.f_locals.get(name, _MISSING)) is _MISSING
                    else CellType(value)
                )
                for name in free_var_names
            )
            dummy_code_bytes += bytes([_BYTE__COPY_FREE_VARS, n_free_vars])

        # If the original function has local variables, pass their current values by
        # appending these values to constants and using some instruction pairs of
        # "LOAD_CONST" and "STORE_FAST".
        dummy_consts = code.co_consts
        local_var_names = code.co_varnames
        for i_local_var, name in enumerate(local_var_names):
            if (value := local_scope.get(name, _MISSING)) is _MISSING:
                continue

            dummy_code_bytes += bytes(
                [_BYTE__LOAD_CONST, len(dummy_consts), _BYTE__STORE_FAST, i_local_var]
            )
            dummy_consts += (value,)

        # Copy the bytecode of the `...` part in `defer and ...` into the dummy
        # function.
        n_skipped_bytes = code_bytes[i_code_byte + 1] * 2
        dummy_code_bytes += code_bytes[
            (i_code_byte + 4) : (i_code_byte + 2 + n_skipped_bytes)
        ]

        # The dummy function should return something. The simplest way is to return
        # whatever value is currently active.
        dummy_code_bytes += bytes([_BYTE__RETURN_VALUE, 0])

        # The dummy function will be called with no argument.
        dummy_code = code.replace(
            co_argcount=0,
            co_posonlyargcount=0,
            co_kwonlyargcount=0,
            co_code=dummy_code_bytes,
            co_consts=dummy_consts,
        )

        new_function = FunctionType(
            code=dummy_code, globals=global_scope, closure=dummy_closure
        )

        if __debug__:

            # This function exists to provide a place for breakpoints in case that
            # `new_function` should fail to work.
            def deferred_call() -> Any:
                return new_function()

        else:
            deferred_call = new_function

        deferred_calls = _ensure_deferred_calls(frame)
        deferred_calls.append(deferred_call)

        return False


defer = _Defer()


class _DeferredCallable[**P]:
    def __init__(self, body: Callable[P, Any], /, code_location: str) -> None:
        self._body: Final = body
        self._code_location = code_location

    __called: bool = False

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        body = self._body

        def deferred_call() -> Any:
            return body(*args, **kwargs)

        frame = _get_caller_frame()
        deferred_calls = _ensure_deferred_calls(frame)
        deferred_calls.append(deferred_call)

        self.__called = True

    def __del__(self, /) -> None:
        if not self.__called:
            code_location = self._code_location
            message = f"`defer(...)` has never got called({code_location})."
            warn(message)


def _get_caller_frame() -> FrameType:
    frame = sys._getframe(2)  # pyright: ignore[reportPrivateUsage]

    if frame.f_locals is frame.f_globals:
        raise RuntimeError("cannot be used in global scope")

    if frame.f_code.co_names[:3] == ("__name__", "__module__", "__qualname__"):
        raise RuntimeError("cannot be used in class scope")

    return frame


def _get_code_location(frame: FrameType, /) -> str:
    filename = frame.f_code.co_filename
    line_number = frame.f_lineno
    code_location = f"{filename}:{line_number}"
    return code_location


# The type of this key is `object` instead of `str`, so it will never conflict with
# anything in a local scope.
_DEFERRED_CALLS_KEY = cast("Any", object())


def _ensure_deferred_calls(frame: FrameType, /) -> _DeferredCalls:
    f_locals = frame.f_locals

    deferred_calls = cast(
        "_DeferredCalls | None", f_locals.get(_DEFERRED_CALLS_KEY, None)
    )
    if deferred_calls is None:
        deferred_calls = _DeferredCalls()
        f_locals[_DEFERRED_CALLS_KEY] = deferred_calls

    return deferred_calls


class _DeferredCalls:
    __internal_list: list[_DeferredCall]

    def __init__(self, /) -> None:
        self.__internal_list = []

    def append(self, deferred_call: _DeferredCall, /) -> None:
        self.__internal_list.append(deferred_call)

    def __del__(self, /) -> None:
        # When this object is being disposed, call everything in the list in a reversed
        # order, and translate all exceptions into warnings.
        internal_list = self.__internal_list
        while len(internal_list) > 0:
            call = internal_list.pop()

            try:
                call()
            except Exception as e:
                # Treat the exception as a warning.
                warn(Warning(e))

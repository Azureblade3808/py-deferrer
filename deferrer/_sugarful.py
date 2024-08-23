from __future__ import annotations

__all__ = [
    "Defer",
    "defer",
]

from types import CellType, FunctionType
from typing import Any, cast
from warnings import warn

from ._common import Opcode, ensure_deferred_calls, get_caller_frame, get_code_location

_MISSING = cast("Any", object())


class Defer:
    """
    Provides `defer` functionality in a sugarful way.

    Examples
    --------
    >>> def f():
    ...     defer and print(0)
    ...     defer and print(1)
    ...     print(2)
    ...     defer and print(3)
    ...     defer and print(4)

    >>> f()
    2
    4
    3
    1
    0
    """

    @staticmethod
    def __bool__() -> bool:
        """
        **DO NOT INVOKE**

        This method is only meant to be called during `defer and ...`.

        If called in other ways, the return value will always be `False`
        and a warning will be emitted.
        """

        frame = get_caller_frame()

        # The usage is `defer and ...` and the corresponding instructions should be:
        # ```
        #     LOAD_GLOBAL ? (defer)
        #     COPY
        # --> POP_JUMP_IF_FALSE ?
        #     POP_TOP
        #     <???>
        # ```
        # The current instruction is at the line prefixed by "-->", and the "<???>" part
        # stands for the `...` part in `defer and ...`.
        code = frame.f_code
        code_bytes = code.co_code
        i_code_byte = frame.f_lasti
        if not (
            True
            and len(code_bytes) - i_code_byte >= 4
            and code_bytes[i_code_byte + 0] == Opcode.POP_JUMP_IF_FALSE
            and code_bytes[i_code_byte + 2] == Opcode.POP_TOP
            and code_bytes[i_code_byte + 3] == 0
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
            dummy_code_bytes += bytes([Opcode.COPY_FREE_VARS, n_free_vars])

        # If the original function has local variables, pass their current values by
        # appending these values to constants and using some instruction pairs of
        # "LOAD_CONST" and "STORE_FAST".
        dummy_consts = code.co_consts
        local_var_names = code.co_varnames
        for i_local_var, name in enumerate(local_var_names):
            if (value := local_scope.get(name, _MISSING)) is _MISSING:
                continue

            dummy_code_bytes += bytes(
                [Opcode.LOAD_CONST, len(dummy_consts), Opcode.STORE_FAST, i_local_var]
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
        dummy_code_bytes += bytes([Opcode.RETURN_VALUE, 0])

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

        deferred_calls = ensure_deferred_calls(frame)
        deferred_calls.append(deferred_call)

        return False


defer = Defer()

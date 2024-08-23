from __future__ import annotations

__all__ = [
    "DeferredCall",
    "DeferredCalls",
    "ensure_deferred_calls",
]

from collections.abc import Callable
from types import FrameType
from typing import Any, cast
from warnings import warn

type DeferredCall = Callable[[], Any]


class DeferredCalls:
    """
    A list-like object that holds deferred calls and automatically runs
    them in a reversed order when it is being disposed.
    """

    __internal_list: list[DeferredCall]

    def __init__(self, /) -> None:
        self.__internal_list = []

    def append(self, deferred_call: DeferredCall, /) -> None:
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


def ensure_deferred_calls(
    frame: FrameType,
    /,
    *,
    # The type of this key is `object` instead of `str`, so it will never conflict with
    # anything in a local scope.
    __key: Any = object(),  # pyright: ignore[reportCallInDefaultInitializer]
) -> DeferredCalls:
    """
    Always returns a `DeferredCalls` object for the given frame. Reuses
    the same object whenever possible.
    """

    f_locals = frame.f_locals

    deferred_calls = cast("DeferredCalls | None", f_locals.get(__key, None))
    if deferred_calls is None:
        deferred_calls = DeferredCalls()
        f_locals[__key] = deferred_calls

    return deferred_calls

from __future__ import annotations

__all__ = [
    "AnyDeferredCall",
    "DeferredCall",
    "DeferredCalls",
    "ensure_deferred_calls",
]

from collections.abc import Callable
from types import FrameType
from typing import Any, Final, Protocol, cast, override
from warnings import warn


class DeferredCall(Protocol):
    def invoke(self, /) -> None: ...


class AnyDeferredCall(DeferredCall):
    """
    A type-erasing implementation of `DeferredCall`.
    """

    __slots__ = "_body"

    _body: Final[Callable[[], Any]]

    def __init__(self, body: Callable[[], Any]) -> None:
        self._body = body

    @override
    def invoke(self) -> None:
        self._body()


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
            deferred_call = internal_list.pop()

            try:
                deferred_call.invoke()
            except Exception as e:
                # Exceptions that occur in `__del__` cannot be raised. So we wrap them
                # as warnings.
                warn(repr(e))


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

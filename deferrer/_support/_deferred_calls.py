from __future__ import annotations

__all__ = [
    "AnyDeferredCall",
    "DeferredCall",
    "DeferredCalls",
]

from abc import ABC, abstractmethod
from collections.abc import Callable
from types import FrameType
from typing import Any, Final, cast, override
from warnings import warn

from ._frame import is_class_frame, is_global_frame


class DeferredCall(ABC):
    __slots__ = ()

    @abstractmethod
    def invoke(self, /) -> None: ...


class AnyDeferredCall(DeferredCall):
    """
    A type-erasing implementation of `DeferredCall`.
    """

    __slots__ = ("_body",)

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

    # The type of this key is `object` instead of `str`, so it will never conflict with
    # anything in a local scope.
    _key: Final[Any] = object()

    @staticmethod
    def ensure_in_frame(frame: FrameType, /) -> DeferredCalls:
        if is_global_frame(frame):
            raise RuntimeError("cannot be used in global scope")

        if is_class_frame(frame):
            raise RuntimeError("cannot be used in class scope")

        key = DeferredCalls._key

        local_scope = frame.f_locals

        instance = cast("DeferredCalls | None", local_scope.get(key))
        if instance is None:
            instance = DeferredCalls()
            local_scope[key] = instance

        return instance

    __slots__ = ("_internal_list",)

    _internal_list: list[DeferredCall]

    def __init__(self, /) -> None:
        self._internal_list = []

    def append(self, deferred_call: DeferredCall, /) -> None:
        self._internal_list.append(deferred_call)

    def drain(self, /) -> None:
        internal_list = self._internal_list
        while len(internal_list) > 0:
            deferred_call = internal_list.pop()

            try:
                deferred_call.invoke()
            except Exception as e:
                warn(repr(e))

    def __del__(self, /) -> None:
        self.drain()

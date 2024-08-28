from __future__ import annotations

__all__ = ["DeferScopeIterable"]

import operator
from collections.abc import Iterable, Iterator
from types import FrameType
from typing import Any, Final, Generic, TypeVar, cast, override

from ._context import DeferScope
from .._support import get_caller_frame

_E_co = TypeVar("_E_co", covariant=True)

_MISSING = cast("Any", object())


class DeferScopeIterable(Iterable[_E_co], Generic[_E_co]):
    __slots__ = ("_wrapped", "_frame")

    _wrapped: Final[Iterable[_E_co]]
    _frame: Final[FrameType]

    def __init__(
        self, wrapped: Iterable[_E_co], /, frame: FrameType = _MISSING
    ) -> None:
        if frame is _MISSING:
            frame = get_caller_frame()

        self._wrapped = wrapped
        self._frame = frame

    @override
    def __iter__(self, /) -> Iterator[_E_co]:
        frame = self._frame
        wrapped = self._wrapped

        @iter
        @operator.call
        def _() -> Iterable[_E_co]:
            for e in iter(wrapped):
                with DeferScope(frame):
                    yield e

        iterator = _
        return iterator

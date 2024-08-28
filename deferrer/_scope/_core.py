from __future__ import annotations

__all__ = [
    "DeferScope",
    "DeferScopeIterable",
    "defer_scope",
]

from collections.abc import Iterable
from contextlib import AbstractContextManager
from typing import Any, cast, overload

from ._context import DeferScope
from ._iterable import DeferScopeIterable
from .._support import get_caller_frame

_MISSING = cast("Any", object())


@overload
def defer_scope() -> AbstractContextManager: ...


@overload
def defer_scope[E](iterable: Iterable[E], /) -> Iterable[E]: ...


def defer_scope(
    wrapped: Iterable[Any] = _MISSING, /
) -> AbstractContextManager | Iterable[Any]:
    frame = get_caller_frame()

    if wrapped is _MISSING:
        return DeferScope(frame=frame)

    if isinstance(wrapped, Iterable):
        return DeferScopeIterable(wrapped, frame=frame)

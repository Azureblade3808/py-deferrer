from __future__ import annotations

__all__ = [
    "Defer",
    "defer",
]

from collections.abc import Callable
from typing import Any, Final
from warnings import warn

from ._common import ensure_deferred_calls, get_caller_frame, get_code_location


class Defer:
    @staticmethod
    def __call__[**P](callable: Callable[P, Any], /) -> _DeferredCallable[P]:
        code_location = get_code_location(get_caller_frame())
        deferred_callable = _DeferredCallable(callable, code_location)
        return deferred_callable


defer = Defer()


class _DeferredCallable[**P]:
    __slots__ = ("_body", "_code_location", "_has_been_called")

    def __init__(self, body: Callable[P, Any], /, code_location: str) -> None:
        self._body: Final = body
        self._code_location: Final = code_location
        self._has_been_called = False

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        if self._has_been_called:
            raise RuntimeError("`defer(...)` gets further called more than once.")

        body = self._body

        def deferred_call() -> Any:
            return body(*args, **kwargs)

        frame = get_caller_frame()
        deferred_calls = ensure_deferred_calls(frame)
        deferred_calls.append(deferred_call)

        self._has_been_called = True

    def __del__(self, /) -> None:
        if not self._has_been_called:
            code_location = self._code_location
            message = f"`defer(...)` has never got further called({code_location})."
            warn(message)

from __future__ import annotations

__all__ = ["defer_scope"]

import operator
from collections.abc import Callable, Iterable, Iterator
from contextlib import AbstractContextManager
from functools import update_wrapper
from types import FrameType, TracebackType
from typing import Any, Final, Generic, ParamSpec, TypeVar, final, overload

from ._deferred_actions import (
    DeferredActions,
    callable_deferred_actions_recorder,
    context_deferred_actions_recorder,
)
from .._utils import get_current_frame, get_outer_frame

_Wrapped_t = TypeVar("_Wrapped_t")

_P = ParamSpec("_P")
_R = TypeVar("_R")

_E = TypeVar("_E")


@overload
def defer_scope() -> AbstractContextManager: ...
@overload
def defer_scope(wrapped: Callable[_P, _R], /) -> Callable[_P, _R]: ...
@overload
def defer_scope(wrapped: Iterable[_E], /) -> Iterable[_E]: ...


def defer_scope(wrapped: Any = None, /) -> Any:
    if wrapped is None:
        return _DeferScopeContextManager()

    return update_wrapper(_DeferScopeWrapper(wrapped), wrapped)


@final
class _DeferScopeContextManager(AbstractContextManager):
    _frame: FrameType | None = None
    _deferred_actions: DeferredActions | None = None

    def __enter__(self, /) -> Any:
        frame = get_outer_frame()
        assert self._frame is None
        self._frame = frame

        deferred_actions = context_deferred_actions_recorder.setup(frame)
        assert self._deferred_actions is None
        self._deferred_actions = deferred_actions

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        frame = self._frame
        assert frame is not None
        del self._frame

        deferred_actions = context_deferred_actions_recorder.teardown(frame)
        assert self._deferred_actions is deferred_actions
        del self._deferred_actions


@final
class _DeferScopeWrapper(Generic[_Wrapped_t]):
    def __init__(self, wrapped: _Wrapped_t, /) -> None:
        self._wrapped: Final = wrapped

    def __call__(
        self: _DeferScopeWrapper[Callable[_P, _R]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R:
        frame = get_current_frame()

        deferred_actions = callable_deferred_actions_recorder.setup(frame)
        try:
            result = self._wrapped(*args, **kwargs)
        finally:
            __ = callable_deferred_actions_recorder.teardown(frame)
            assert __ is deferred_actions
            deferred_actions.drain()

        return result

    def __iter__(self: _DeferScopeWrapper[Iterable[_E]], /) -> Iterator[_E]:
        frame = get_outer_frame()

        @iter
        @operator.call
        def _() -> Iterable[_E]:
            for element in self._wrapped:
                deferred_actions = context_deferred_actions_recorder.setup(frame)
                try:
                    yield element
                finally:
                    __ = context_deferred_actions_recorder.teardown(frame)
                    assert __ is deferred_actions
                    deferred_actions.drain()

        iterator = _
        return iterator

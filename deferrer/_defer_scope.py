from __future__ import annotations

from types import TracebackType

__all__ = [
    "_DeferScopeContextManager",
    "defer_scope",
    "ensure_deferred_actions",
]

import operator
import sys
from collections.abc import Callable, Iterable, Iterator
from contextlib import AbstractContextManager
from functools import update_wrapper
from types import FrameType
from typing import Any, Final, Generic, ParamSpec, TypeVar, cast, final, overload

from ._deferred_actions import DeferredActions
from ._frame import get_current_frame, get_outer_frame, is_class_frame, is_global_frame

_Wrapped_t = TypeVar("_Wrapped_t")

_P = ParamSpec("_P")
_R = TypeVar("_R")

_E = TypeVar("_E")

_LOCAL_KEY = cast("Any", object())


@overload
def defer_scope() -> AbstractContextManager: ...
@overload
def defer_scope(wrapped: Callable[_P, _R], /) -> Callable[_P, _R]: ...
@overload
def defer_scope(wrapped: Iterable[_E], /) -> Iterable[_E]: ...


def defer_scope(wrapped: Any = None, /) -> Any:
    if wrapped is None:
        return _DeferScopeContextManager()
    else:
        wrapper = _DeferScopeWrapper(wrapped)
        wrapper = update_wrapper(wrapper, wrapped)
        return wrapper


def ensure_deferred_actions(frame: FrameType) -> DeferredActions:
    for recorder in (
        _context_deferred_actions_recorder,
        _callable_deferred_actions_recorder,
    ):
        deferred_actions = recorder.find(frame)
        if deferred_actions is not None:
            return deferred_actions

    if sys.version_info < (3, 12):
        raise RuntimeError(
            "cannot inject deferred actions into local scope"
            + " with Python older than 3.12"
        )

    local_scope = frame.f_locals

    deferred_actions = local_scope.get(_LOCAL_KEY)
    if deferred_actions is not None:
        return deferred_actions

    if is_global_frame(frame):
        raise RuntimeError("cannot inject deferred actions into global scope")

    if is_class_frame(frame):
        raise RuntimeError("cannot inject deferred actions into class scope")

    deferred_actions = DeferredActions()
    local_scope[_LOCAL_KEY] = deferred_actions

    return deferred_actions


@final
class _DeferScopeContextManager(AbstractContextManager):
    _frame: FrameType | None = None
    _deferred_actions: DeferredActions | None = None

    def __enter__(self, /) -> Any:
        frame = get_outer_frame()
        assert self._frame is None
        self._frame = frame

        deferred_actions = DeferredActions()
        assert self._deferred_actions is None
        self._deferred_actions = deferred_actions

        _context_deferred_actions_recorder.add(frame, deferred_actions)

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

        deferred_actions = self._deferred_actions
        assert deferred_actions is not None
        del self._deferred_actions

        _context_deferred_actions_recorder.remove(frame, deferred_actions)

        return None


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
        wrapped = self._wrapped

        frame = get_current_frame()
        deferred_actions = DeferredActions()

        _callable_deferred_actions_recorder.add(frame, deferred_actions)
        try:
            result = wrapped(*args, **kwargs)
        finally:
            _callable_deferred_actions_recorder.remove(frame, deferred_actions)

        return result

    def __iter__(self: _DeferScopeWrapper[Iterable[_E]], /) -> Iterator[_E]:
        frame = get_outer_frame()
        wrapped = self._wrapped

        @iter
        @operator.call
        def _() -> Iterable[_E]:
            for element in wrapped:
                deferred_actions = DeferredActions()

                _context_deferred_actions_recorder.add(frame, deferred_actions)
                try:
                    yield element
                finally:
                    _context_deferred_actions_recorder.remove(frame, deferred_actions)

        iterator = _
        return iterator


class _CallableDeferredActionsRecorder:
    _internal_dict: Final[dict[FrameType, DeferredActions]]

    def __init__(self, /) -> None:
        self._internal_dict = {}

    def add(self, outer_frame: FrameType, deferred_actions: DeferredActions, /) -> None:
        __ = self._internal_dict.setdefault(outer_frame, deferred_actions)
        assert __ is deferred_actions

    def remove(
        self, outer_frame: FrameType, deferred_actions: DeferredActions, /
    ) -> None:
        __ = self._internal_dict.pop(outer_frame)
        assert __ is deferred_actions

        deferred_actions.drain()

    def find(self, frame: FrameType, /) -> DeferredActions | None:
        outer_frame = frame.f_back
        assert outer_frame is not None
        deferred_actions = self._internal_dict.get(outer_frame)
        return deferred_actions


_callable_deferred_actions_recorder = _CallableDeferredActionsRecorder()


class _ContextDeferredActionsRecorder:
    _internal_dict: Final[dict[FrameType, list[DeferredActions]]]

    def __init__(self, /) -> None:
        self._internal_dict = {}

    def add(self, frame: FrameType, deferred_actions: DeferredActions, /) -> None:
        internal_dict = self._internal_dict

        deferred_actions_list = internal_dict.get(frame)
        if deferred_actions_list is None:
            deferred_actions_list = []
            internal_dict[frame] = deferred_actions_list

        deferred_actions_list.append(deferred_actions)

    def remove(self, frame: FrameType, deferred_actions: DeferredActions, /) -> None:
        internal_dict = self._internal_dict

        deferred_actions_list = internal_dict[frame]
        __ = deferred_actions_list.pop()
        assert __ is deferred_actions

        if len(deferred_actions_list) == 0:
            del internal_dict[frame]

        deferred_actions.drain()

    def find(self, frame: FrameType, /) -> DeferredActions | None:
        deferred_actions_list = self._internal_dict.get(frame)
        if deferred_actions_list is None:
            return None

        deferred_actions = deferred_actions_list[-1]
        return deferred_actions


_context_deferred_actions_recorder = _ContextDeferredActionsRecorder()

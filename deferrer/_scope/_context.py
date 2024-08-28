from __future__ import annotations

__all__ = ["DeferScope"]

from contextlib import AbstractContextManager
from types import FrameType, TracebackType
from typing import Any, Final, cast, override

from .._support import DeferredCalls, get_caller_frame

_MISSING = cast("Any", object)


class DeferScope(AbstractContextManager):
    _internal_dict: Final[dict[FrameType, list[DeferredCalls]]] = {}

    @staticmethod
    def get_deferred_calls(frame: FrameType, /) -> DeferredCalls:
        internal_dict = DeferScope._internal_dict

        deferred_calls_list = internal_dict.get(frame)
        if deferred_calls_list is None:
            deferred_calls = DeferredCalls.ensure_in_frame(frame)
            return deferred_calls

        deferred_calls = deferred_calls_list[-1]
        return deferred_calls

    _frame: Final[FrameType]

    def __init__(self, /, frame: FrameType = _MISSING) -> None:
        if frame is _MISSING:
            frame = get_caller_frame()

        self._frame = frame

    _deferred_calls: DeferredCalls | None = None

    @override
    def __enter__(self, /) -> None:
        assert self._deferred_calls is None

        deferred_calls = DeferredCalls()
        self._deferred_calls = deferred_calls

        internal_dict = self._internal_dict
        frame = self._frame

        deferred_calls_list = internal_dict.get(frame)
        if deferred_calls_list is None:
            deferred_calls_list = []
            internal_dict[frame] = deferred_calls_list

        deferred_calls_list.append(deferred_calls)

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        internal_dict = DeferScope._internal_dict
        frame = self._frame

        deferred_calls_list = internal_dict[frame]

        deferred_calls = deferred_calls_list.pop()
        deferred_calls.drain()

        if len(deferred_calls_list) == 0:
            del internal_dict[frame]

        assert deferred_calls is self._deferred_calls
        self._deferred_calls = None

from __future__ import annotations

__all__ = [
    "CallableDeferredActionsRecorder",
    "ContextDeferredActionsRecorder",
    "DeferredAction",
    "DeferredActions",
    "callable_deferred_actions_recorder",
    "context_deferred_actions_recorder",
    "ensure_deferred_actions",
]

import sys
from abc import ABC, abstractmethod
from types import FrameType
from typing import Any, Final, Never, cast, final

from .._utils import is_class_frame, is_global_frame


class DeferredAction(ABC):
    """
    An object that stands for an action that is meant to be performed
    later.
    """

    @abstractmethod
    def perform(self, /) -> None: ...


@final
class DeferredActions:
    """
    A list-like object that holds `DeferredAction` objects.

    When a `DeferredActions` object is being disposed, all
    `DeferredAction` objects it holds will get performed in a FILO
    order.
    """

    _internal_list: Final[list[DeferredAction]]

    def __init__(self, /) -> None:
        self._internal_list = []

    def append(self, deferred_call: DeferredAction, /) -> None:
        self._internal_list.append(deferred_call)

    def drain(self, /) -> None:
        exceptions: list[Exception] = []

        internal_list = self._internal_list
        while len(internal_list) > 0:
            deferred_call = internal_list.pop()

            try:
                deferred_call.perform()
            except Exception as e:
                exceptions.append(e)

        n_exceptions = len(exceptions)
        if n_exceptions == 0:
            return

        exception_group = ExceptionGroup("deferred exception(s)", exceptions)
        raise exception_group

    def __del__(self, /) -> None:
        self.drain()


@final
class CallableDeferredActionsRecorder:
    """
    A recorder that records `DeferredActions` objects associated with
    callables.
    """

    _internal_dict: Final[dict[FrameType, DeferredActions]]

    def __init__(self, /) -> None:
        self._internal_dict = {}

    def setup(self, /, outer_frame: FrameType) -> DeferredActions:
        internal_dict = self._internal_dict
        assert outer_frame not in internal_dict
        deferred_actions = DeferredActions()
        internal_dict[outer_frame] = deferred_actions
        return deferred_actions

    def teardown(self, /, outer_frame: FrameType) -> DeferredActions:
        return self._internal_dict.pop(outer_frame)

    def get(self, /, frame: FrameType) -> DeferredActions | None:
        outer_frame = frame.f_back
        assert outer_frame is not None
        deferred_actions = self._internal_dict.get(outer_frame)
        return deferred_actions


callable_deferred_actions_recorder = CallableDeferredActionsRecorder()
"""
The singleton instance of `CallableDeferredActionsRecorder`.
"""


@final
class ContextDeferredActionsRecorder:
    """
    A recorder that records `DeferredActions` objects associated with
    context managers.
    """

    _internal_dict: Final[dict[FrameType, list[DeferredActions]]]

    def __init__(self, /) -> None:
        self._internal_dict = {}

    def setup(self, /, frame: FrameType) -> DeferredActions:
        internal_dict = self._internal_dict
        deferred_actions_list = internal_dict.setdefault(frame, [])
        deferred_actions = DeferredActions()
        deferred_actions_list.append(deferred_actions)
        return deferred_actions

    def teardown(self, /, frame: FrameType) -> DeferredActions:
        internal_dict = self._internal_dict
        deferred_actions_list = internal_dict[frame]
        deferred_actions = deferred_actions_list.pop()
        if len(deferred_actions_list) == 0:
            del internal_dict[frame]
        return deferred_actions

    def get(self, /, frame: FrameType) -> DeferredActions | None:
        deferred_actions_list = self._internal_dict.get(frame)
        if deferred_actions_list is None:
            return None
        deferred_actions = deferred_actions_list[-1]
        return deferred_actions


context_deferred_actions_recorder = ContextDeferredActionsRecorder()
"""
The singleton instance of `ContextDeferredActionsRecorder`.
"""


def ensure_deferred_actions(
    frame: FrameType,
    *,
    # We are using a newly created `object` instance as a secret key in local scopes
    # so that it will never conflict with any existing key.
    # It is intentially typed as `Never` so that it will never be assigned another value
    # when the function is getting called.
    __KEY__: Never = cast(
        "Any",
        object(),  # pyright: ignore[reportCallInDefaultInitializer]
    ),
) -> DeferredActions:
    """
    Returns the most active `DeferredActions` object for the given
    frame.
    """

    # Try to find one in `context_deferred_actions_recorder` and then
    # `callable_deferred_actions_recorder`.
    for recorder in (
        context_deferred_actions_recorder,
        callable_deferred_actions_recorder,
    ):
        deferred_actions = recorder.get(frame)
        if deferred_actions is not None:
            return deferred_actions

    # No match. We shall check local scope soon.

    # There is no way to inject an object into a local scope in Python 3.11.
    if sys.version_info < (3, 12):
        raise RuntimeError(
            (
                "cannot inject deferred actions into local scope with"
                " Python older than 3.12"
            )
        )

    # If we injected an object into a global scope or a class scope, it would not get
    # released in time.
    if is_global_frame(frame):
        raise RuntimeError("cannot inject deferred actions into global scope")
    if is_class_frame(frame):
        raise RuntimeError("cannot inject deferred actions into class scope")

    local_scope = frame.f_locals

    # If one existing instance is already in the local scope, just reuse it.
    deferred_actions = local_scope.get(__KEY__)
    if deferred_actions is not None:
        return deferred_actions

    # We are now forced to deploy a new instance.
    deferred_actions = DeferredActions()
    local_scope[__KEY__] = deferred_actions
    return deferred_actions

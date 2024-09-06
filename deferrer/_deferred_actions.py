from __future__ import annotations

__all__ = [
    "DeferredAction",
    "DeferredActions",
]

from abc import ABC, abstractmethod
from typing import Final, final


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

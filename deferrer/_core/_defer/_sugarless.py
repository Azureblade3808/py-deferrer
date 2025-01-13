from __future__ import annotations

__all__ = ["Defer"]

from collections.abc import Callable
from typing import Any, Final, Generic, ParamSpec, final
from warnings import warn

from .._deferred_actions import DeferredAction, ensure_deferred_actions
from ..._utils import get_code_location, get_outer_frame

_P = ParamSpec("_P")


class Defer:
    @staticmethod
    def __call__(callable: Callable[_P, Any], /) -> Callable[_P, None]:
        """
        Converts a callable into a deferred callable.

        Return value of the given callable will always be ignored.
        """

        frame = get_outer_frame()
        code_location = get_code_location(frame)
        deferred_actions = ensure_deferred_actions(frame)

        deferred_callable = _DeferredCallable(callable, code_location)
        deferred_actions.append(deferred_callable)

        return deferred_callable


@final
class _DeferredCallable(DeferredAction, Generic[_P]):
    _body: Final[Callable[..., Any]]
    _code_location: Final[str]

    _args_and_kwargs: tuple[tuple[Any, ...], dict[str, Any]] | None

    def __init__(self, body: Callable[_P, Any], /, code_location: str) -> None:
        self._body = body
        self._code_location = code_location

        self._args_and_kwargs = None

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> None:
        if self._args_and_kwargs is not None:
            raise RuntimeError("`defer(...)` gets further called more than once.")

        self._args_and_kwargs = (args, kwargs)

    def perform(self, /) -> None:
        body = self._body
        args_and_kwargs = self._args_and_kwargs

        if args_and_kwargs is not None:
            args, kwargs = args_and_kwargs
            body(*args, **kwargs)
            return

        try:
            body()
        except TypeError as e:
            traceback = e.__traceback__
            assert traceback is not None

            if traceback.tb_next is not None:
                # This `TypeError` was raised by user. We should not do anthing special.
                raise

            # This `TypeError` was raised on function call, which means that there was a signature error.
            # It is typically because a deferred callable with at least one required argument doesn't ever get further
            # called with appropriate arguments.
            code_location = self._code_location
            message = f"`defer(...)` has never got further called ({code_location})."
            warn(message)

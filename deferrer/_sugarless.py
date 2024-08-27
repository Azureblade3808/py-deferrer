from __future__ import annotations

__all__ = [
    "Defer",
    "defer",
]

from collections.abc import Callable
from typing import Any, Final, override
from warnings import warn

from ._common import (
    DeferredCall,
    ensure_deferred_calls,
    get_caller_frame,
    get_code_location,
)


class Defer:
    """
    Provides `defer` functionality in a sugarless way.

    Examples
    --------
    >>> def f():
    ...     defer(print)(0)
    ...     defer(print)(1)
    ...     print(2)
    ...     defer(print)(3)
    ...     defer(print)(4)

    >>> f()
    2
    4
    3
    1
    0
    """

    @staticmethod
    def __call__[**P](callable: Callable[P, Any], /) -> Callable[P, None]:
        """
        Converts a callable into a deferred callable.

        Return value of the given callable will always be ignored.
        """

        frame = get_caller_frame()
        code_location = get_code_location(frame)

        deferred_callable = _DeferredCallable(callable, code_location)

        deferred_calls = ensure_deferred_calls(frame)
        deferred_calls.append(deferred_callable)

        return deferred_callable


defer = Defer()


class _DeferredCallable[**P](DeferredCall):
    __slots__ = ("_body", "_code_location", "_args_and_kwargs")

    _body: Final[Callable[[], Any]]
    _code_location: Final[str]

    _args_and_kwargs: tuple[tuple[Any, ...], dict[str, Any]] | None

    def __init__(self, body: Callable[P, Any], /, code_location: str) -> None:
        self._body = body
        self._code_location = code_location

        self._args_and_kwargs = None

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        if self._args_and_kwargs is not None:
            raise RuntimeError("`defer(...)` gets further called more than once.")

        self._args_and_kwargs = (args, kwargs)

    @override
    def invoke(self, /) -> None:
        body = self._body
        args_and_kwargs = self._args_and_kwargs

        if args_and_kwargs is not None:
            args, kwargs = args_and_kwargs
            body(*args, **kwargs)
            return

        try:
            body()
        except Exception as e:
            if isinstance(e, TypeError):
                traceback = e.__traceback__
                assert traceback is not None

                if traceback.tb_next is None:
                    # This `TypeError` was raised on function call, which means that
                    # there was a signature error.
                    # It is typically because a deferred callable with at least one
                    # required argument doesn't ever get further called with appropriate
                    # arguments.
                    code_location = self._code_location
                    message = (
                        f"`defer(...)` has never got further called ({code_location})."
                    )
                    warn(message)
                    return

            raise e

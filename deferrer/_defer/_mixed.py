from __future__ import annotations

__all__ = [
    "Defer",
    "defer",
]

from . import _sugarful, _sugarless


class Defer(_sugarful.Defer, _sugarless.Defer):
    """
    Provides `defer` functionality in both sugarful and sugarless ways.

    Examples
    --------
    >>> def f_0():
    ...     defer and print(0)
    ...     defer and print(1)
    ...     print(2)
    ...     defer and print(3)
    ...     defer and print(4)

    >>> f_0()
    2
    4
    3
    1
    0

    >>> def f_1():
    ...     defer(print)(0)
    ...     defer(print)(1)
    ...     print(2)
    ...     defer(print)(3)
    ...     defer(print)(4)

    >>> f_1()
    2
    4
    3
    1
    0
    """

    __slots__ = ()


defer = Defer()

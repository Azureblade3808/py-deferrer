from __future__ import annotations

__all__ = [
    "Defer",
    "defer",
]

from . import _sugarful, _sugarless


class Defer(_sugarful.Defer, _sugarless.Defer):
    pass


defer = Defer()

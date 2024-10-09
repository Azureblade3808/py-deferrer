from __future__ import annotations

__all__ = [
    "WILDCARD",
    "sequence_has_prefix",
    "sequence_has_suffix",
]

from collections.abc import Sequence
from typing import Any


class _Wildcard(Any):
    """
    An object that equals any object.
    """

    def __eq__(self, other: object, /) -> bool:
        return True


WILDCARD = _Wildcard()


def sequence_has_prefix(sequence: Sequence[Any], prefix: Sequence[Any], /) -> bool:
    return tuple(sequence[: len(prefix)]) == tuple(prefix)


def sequence_has_suffix(sequence: Sequence[Any], suffix: Sequence[Any], /) -> bool:
    return tuple(sequence[-len(suffix) :]) == tuple(suffix)

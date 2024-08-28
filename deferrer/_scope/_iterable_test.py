from __future__ import annotations

__all__ = []

import pytest

from ._iterable import *
from .._defer import defer


class FuntionalityTests:
    @staticmethod
    def test_0() -> None:
        def f() -> None:
            for _ in DeferScopeIterable(range(10)):
                raise ValueError("xxx")

        with pytest.raises(ValueError, match="xxx"):
            f()

    @staticmethod
    def test_1() -> None:
        nums: list[int] = []

        for i in DeferScopeIterable([0, 5, 10]):
            defer(nums.append)(i)
            defer and nums.append(i + 1)
            nums.append(i + 2)
            defer(nums.append)(i + 3)
            defer and nums.append(i + 4)

        assert nums == [2, 4, 3, 1, 0, 7, 9, 8, 6, 5, 12, 14, 13, 11, 10]

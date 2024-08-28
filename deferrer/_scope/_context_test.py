from __future__ import annotations

__all__ = []

import pytest

from ._context import *
from .._defer import defer


class FunctionalityTests:
    @staticmethod
    def test_0() -> None:
        def f() -> None:
            with DeferScope():
                raise ValueError("xxx")

        with pytest.raises(ValueError, match="xxx"):
            f()

    @staticmethod
    def test_1() -> None:
        nums: list[int] = []

        with DeferScope():
            defer(nums.append)(0)
            defer and nums.append(1)

            with DeferScope():
                defer(nums.append)(2)
                defer and nums.append(3)

                nums.append(4)

                defer(nums.append)(5)
                defer and nums.append(6)

            defer(nums.append)(7)
            defer and nums.append(8)

        assert nums == [4, 6, 5, 3, 2, 8, 7, 1, 0]

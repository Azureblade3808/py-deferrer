from __future__ import annotations

__all__ = []

from ._core import *
from .._defer import defer


class FunctionalityTests:
    @staticmethod
    def test_0() -> None:
        nums: list[int] = []

        with defer_scope():
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

    @staticmethod
    def test_1() -> None:
        nums: list[int] = []

        for i in defer_scope([0, 5, 10]):
            defer(nums.append)(i)
            defer and nums.append(i + 1)
            nums.append(i + 2)
            defer(nums.append)(i + 3)
            defer and nums.append(i + 4)

        assert nums == [2, 4, 3, 1, 0, 7, 9, 8, 6, 5, 12, 14, 13, 11, 10]

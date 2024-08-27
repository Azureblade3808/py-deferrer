from __future__ import annotations

from typing import Any, cast

import pytest

from ._mixed import *

_MISSING = cast("Any", object())


class FunctionalityTests:
    @staticmethod
    def test_0() -> None:
        x: int = _MISSING
        nums: list[int] = _MISSING

        def f() -> None:
            nonlocal nums

            nums = []
            assert nums == []

            defer and nums.append(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            assert nums == [x]

            defer and nums.append(3)
            defer(nums.append)(4)
            assert nums == [x]

        x = 0
        f()
        assert nums == [0, 4, 3, 2, 1]

        x = -1
        f()
        assert nums == [-1, 4, 3, 2, 1]

    @staticmethod
    def test_1() -> None:
        nums: list[int] = _MISSING

        def f(x: int) -> None:
            nonlocal nums

            nums = []
            assert nums == []

            defer and nums.append(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            assert nums == [x]

            defer and nums.append(3)
            defer(nums.append)(4)
            assert nums == [x]

        f(0)
        assert nums == [0, 4, 3, 2, 1]

        f(-1)
        assert nums == [-1, 4, 3, 2, 1]

    @staticmethod
    def test_2() -> None:
        nums: list[int] = _MISSING

        def f(x: int = 0) -> None:
            nonlocal nums

            nums = []
            assert nums == []

            defer and nums.append(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            assert nums == [x]

            defer and nums.append(3)
            defer(nums.append)(4)
            assert nums == [x]

        f()
        assert nums == [0, 4, 3, 2, 1]

        f(0)
        assert nums == [0, 4, 3, 2, 1]

        f(-1)
        assert nums == [-1, 4, 3, 2, 1]

    @staticmethod
    def test_3() -> None:
        x: int = _MISSING
        nums: list[int] = _MISSING

        def f() -> None:
            nonlocal nums

            nums = []
            assert nums == []

            defer and nums.append(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            raise

            defer and nums.append(3)
            defer(nums.append)(4)

        x = 0
        with pytest.raises(Exception):
            f()
        assert nums == [0, 2, 1]

        x = -1
        with pytest.raises(Exception):
            f()
        assert nums == [-1, 2, 1]

    @staticmethod
    def test_4() -> None:
        x: int = _MISSING

        def f() -> list[int]:
            nums: list[int] = []
            assert nums == []

            defer and nums.append(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            assert nums == [x]

            defer and nums.append(3)
            defer(nums.append)(4)
            assert nums == [x]

            return nums

        x = 0
        nums = f()
        assert nums == [0, 4, 3, 2, 1]

        x = -1
        nums = f()
        assert nums == [-1, 4, 3, 2, 1]

    @staticmethod
    def test_5() -> None:
        result: int = _MISSING

        def f() -> None:
            x = 0

            def f_0() -> None:
                nonlocal result
                result = x

            defer and f_0()

            def f_1() -> None:
                nonlocal x
                x = 1

            defer and f_1()

            def f_2() -> None:
                nonlocal x
                x = 2

            defer and f_2()

        f()
        assert result == 1

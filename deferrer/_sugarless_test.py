from __future__ import annotations

__all__ = []

import pytest

from ._sugarless import *


class Tests:
    @staticmethod
    def test__should_raise__in_global_scope() -> None:
        with pytest.raises(RuntimeError):
            from . import _sugarless_test__defer_in_global_scope as _

    @staticmethod
    def test__should_raise__in_class_scope() -> None:
        with pytest.raises(RuntimeError):

            class _:
                defer(print)()

    @staticmethod
    def test__should_warn__not_called() -> None:
        def f() -> None:
            defer(print)  # pyright: ignore[reportUnusedCallResult]

        with pytest.warns():
            f()

    @staticmethod
    def test__should_raise__called_more_than_once() -> None:
        def f() -> None:
            stub = defer(print)
            stub()
            stub()

        with pytest.raises(RuntimeError):
            f()

    @staticmethod
    def test__should_warn__deferred_exceptions() -> None:
        def f() -> None:
            def do_raise() -> None:
                raise

            defer(do_raise)()

        with pytest.warns():
            f()

    @staticmethod
    def test__should_work__case_0() -> None:
        nums: list[int] = []

        def f() -> None:
            nonlocal nums
            nums = []
            defer(nums.append)(1)
            defer(nums.append)(2)
            defer(nums.append)(3)
            assert nums == []
            nums.append(0)
            assert nums == [0]
            defer(nums.append)(4)
            defer(nums.append)(5)
            defer(nums.append)(6)
            assert nums == [0]

        f()
        assert nums == [0, 6, 5, 4, 3, 2, 1]

        f()
        assert nums == [0, 6, 5, 4, 3, 2, 1]

    @staticmethod
    def test__should_work__case_1() -> None:
        nums: list[int] = []

        def f(x: int) -> None:
            nonlocal nums
            nums = []
            defer(nums.append)(1)
            defer(nums.append)(2)
            defer(nums.append)(3)
            assert nums == []
            nums.append(x)
            assert nums == [x]
            defer(nums.append)(4)
            defer(nums.append)(5)
            defer(nums.append)(6)
            assert nums == [x]

        f(0)
        assert nums == [0, 6, 5, 4, 3, 2, 1]

        f(-1)
        assert nums == [-1, 6, 5, 4, 3, 2, 1]

    @staticmethod
    def test__should_work__case_2() -> None:
        nums: list[int] = []

        def f(x: int = 0) -> None:
            nonlocal nums
            nums = []
            defer(nums.append)(1)
            defer(nums.append)(2)
            defer(nums.append)(3)
            assert nums == []
            nums.append(x)
            assert nums == [x]
            defer(nums.append)(4)
            defer(nums.append)(5)
            defer(nums.append)(6)
            assert nums == [x]

        f()
        assert nums == [0, 6, 5, 4, 3, 2, 1]

        f(0)
        assert nums == [0, 6, 5, 4, 3, 2, 1]

        f(-1)
        assert nums == [-1, 6, 5, 4, 3, 2, 1]

    @staticmethod
    def test__should_work__case_3() -> None:
        nums: list[int] = []

        def f() -> None:
            nonlocal nums
            nums = []
            defer(nums.append)(1)
            defer(nums.append)(2)
            defer(nums.append)(3)
            assert nums == []
            nums.append(0)
            raise
            nums.append(-1)
            assert nums == [0]
            defer(nums.append)(4)
            defer(nums.append)(5)
            defer(nums.append)(6)
            assert nums == [0]

        with pytest.raises(Exception):
            f()
        assert nums == [0, 3, 2, 1]

        with pytest.raises(Exception):
            f()
        assert nums == [0, 3, 2, 1]

    @staticmethod
    def test__should_work__case_4() -> None:
        def f() -> list[int]:
            nums: list[int] = []
            defer(nums.append)(1)
            defer(nums.append)(2)
            defer(nums.append)(3)
            assert nums == []
            nums.append(0)
            assert nums == [0]
            defer(nums.append)(4)
            defer(nums.append)(5)
            defer(nums.append)(6)
            assert nums == [0]
            return nums

        nums = f()
        assert nums == [0, 6, 5, 4, 3, 2, 1]

        nums = f()
        assert nums == [0, 6, 5, 4, 3, 2, 1]

    @staticmethod
    def test__should_work__case_5() -> None:
        result: int | None = None

        def f() -> None:
            x = 0

            def f_0() -> None:
                nonlocal result
                result = x

            defer(f_0)()

            def f_1() -> None:
                nonlocal x
                x = 1

            defer(f_1)()

            def f_2() -> None:
                nonlocal x
                x = 2

            defer(f_2)()

        f()
        assert result == 1

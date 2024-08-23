from __future__ import annotations

__all__ = []

import pytest

from ._sugarful import *


class Tests:
    @staticmethod
    def test__should_raise__in_global_scope() -> None:
        with pytest.raises(RuntimeError):
            from unimportable import _sugarful_test__defer_in_global_scope as _

    @staticmethod
    def test__should_raise__in_class_scope() -> None:
        with pytest.raises(RuntimeError):

            class _:
                defer and print()

    @staticmethod
    def test__should_warn__unsupported_usage() -> None:
        def f_0() -> None:
            defer or print()

        with pytest.warns():
            f_0()

        def f_1() -> None:
            __ = bool(defer)

        with pytest.warns():
            f_1()

    @staticmethod
    def test__should_warn__deferred_exceptions() -> None:
        def f() -> None:
            def do_raise() -> None:
                raise

            defer and do_raise()

        with pytest.warns():
            f()

    @staticmethod
    def test__should_work__case_0() -> None:
        nums: list[int] = []

        def f() -> None:
            nonlocal nums
            nums = []
            defer and nums.append(1)
            defer and nums.append(2)
            defer and nums.append(3)
            assert nums == []
            nums.append(0)
            assert nums == [0]
            defer and nums.append(4)
            defer and nums.append(5)
            defer and nums.append(6)
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
            defer and nums.append(1)
            defer and nums.append(2)
            defer and nums.append(3)
            assert nums == []
            nums.append(x)
            assert nums == [x]
            defer and nums.append(4)
            defer and nums.append(5)
            defer and nums.append(6)
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
            defer and nums.append(1)
            defer and nums.append(2)
            defer and nums.append(3)
            assert nums == []
            nums.append(x)
            assert nums == [x]
            defer and nums.append(4)
            defer and nums.append(5)
            defer and nums.append(6)
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
            defer and nums.append(1)
            defer and nums.append(2)
            defer and nums.append(3)
            assert nums == []
            nums.append(0)
            raise
            nums.append(-1)
            assert nums == [0]
            defer and nums.append(4)
            defer and nums.append(5)
            defer and nums.append(6)
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
            defer and nums.append(1)
            defer and nums.append(2)
            defer and nums.append(3)
            assert nums == []
            nums.append(0)
            assert nums == [0]
            defer and nums.append(4)
            defer and nums.append(5)
            defer and nums.append(6)
            assert nums == [0]
            return nums

        nums = f()
        assert nums == [0, 6, 5, 4, 3, 2, 1]

        nums = f()
        assert nums == [0, 6, 5, 4, 3, 2, 1]

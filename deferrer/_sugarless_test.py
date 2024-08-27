from __future__ import annotations

__all__ = []

from typing import Any, cast

import pytest

from ._sugarless import *

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

            defer(nums.append)(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            assert nums == [x]

            defer(nums.append)(3)
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

            defer(nums.append)(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            assert nums == [x]

            defer(nums.append)(3)
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

            defer(nums.append)(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            assert nums == [x]

            defer(nums.append)(3)
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

            defer(nums.append)(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            raise

            defer(nums.append)(3)
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

            defer(nums.append)(1)
            defer(nums.append)(2)
            assert nums == []

            nums.append(x)
            assert nums == [x]

            defer(nums.append)(3)
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


class UsageTests:
    @staticmethod
    def test__should_raise__used_in_global_scope() -> None:
        with pytest.raises(RuntimeError):
            from . import _sugarless_test__used_in_global_scope as _

    @staticmethod
    def test__should_raise__used_in_class_scope() -> None:
        with pytest.raises(RuntimeError):

            class _:
                defer(print)()

    @staticmethod
    def test__should_warn__not_further_called() -> None:
        def f_0() -> None:
            def inner() -> None:
                pass

            defer(inner)  # pyright: ignore[reportUnusedCallResult]

        # This should work because `f_0.inner` can be called with no argument.
        f_0()

        def f_1() -> None:
            def inner(x: int) -> None: ...

            defer(inner)  # pyright: ignore[reportUnusedCallResult]

        # This should not work because `f_1.inner` cannot be called with no argument.
        with pytest.warns(UserWarning, match="has never got further called"):
            f_1()

    @staticmethod
    def test__should_raise__called_more_than_once() -> None:
        def f() -> None:
            stub = defer(lambda: None)
            stub()
            stub()

        with pytest.raises(RuntimeError):
            f()

    @staticmethod
    def test__should_warn__type_error_created_by_user() -> None:
        def f() -> None:
            @defer
            def _() -> None:
                raise TypeError()

        # The `TypeError` should be raised as a warning because it is created by user.
        with pytest.warns(match="TypeError"):
            f()

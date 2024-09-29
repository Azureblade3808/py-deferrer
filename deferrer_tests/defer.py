from __future__ import annotations

import sys
from typing import Never

import pytest

from deferrer import defer


class Test__defer:
    @staticmethod
    def test__is_forbidden_at_module_level() -> None:
        """
        For `defer` to work, the local scope where `defer` gets used
        need to eventually get disposed with everything in it released
        at the same time.

        If `defer` is used at module level, the local scope is the
        global scope and will never get disposed in time.

        Therefore, an exception is raised to prevent such usages.
        """

        with pytest.raises(Exception) as exc_info:
            from deferrer_tests.samples import sugarful_without_defer_scope as _
        assert not exc_info.errisinstance(ImportError)

        with pytest.raises(Exception):
            from deferrer_tests.samples import sugarless_without_defer_scope as _
        assert not exc_info.errisinstance(ImportError)

    @staticmethod
    def test__is_forbidden_at_class_level() -> None:
        """
        For `defer` to work, the local scope where `defer` gets used
        need to eventually get disposed with everything in it released
        at the same time.

        If `defer` is used at class level, everything in the local scope
        will get copied into the class and will never get released in
        time.

        Therefore, an exception is raised to prevent such usages.
        """

        with pytest.raises(Exception):

            class _:
                defer and print()

        with pytest.raises(Exception):

            class _:
                defer(print)()

        with pytest.raises(Exception):

            def _(x: int = 0):
                # This class will have "COPY_FREE_VARS" at the head of its code.
                class _:
                    defer and print(x)

            _()

        with pytest.raises(Exception):

            def _(x: int = 0):
                # This class will have "COPY_FREE_VARS" at the head of its code.
                class _:
                    defer(print)(x)

            _()

    @staticmethod
    @pytest.mark.skipif(sys.version_info >= (3, 12), reason="supported on new python")
    def test__is_forbidden_at_function_level_in_old_python() -> None:
        """
        `defer_scope` must be used for `defer` to work in Python older
        than 3.12.
        """

        def f():
            defer and print()

        with pytest.raises(Exception):
            f()

    @staticmethod
    def test__works_in_sugarful_form() -> None:
        """
        `defer` can be used like `defer and {expression}`.
        """

        nums = []

        def f() -> None:
            nums.clear()
            assert nums == []

            defer and nums.append(0)
            assert nums == []

            nums.append(1)
            assert nums == [1]

            defer and nums.append(2)
            assert nums == [1]

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert nums == [1, 2, 0]

    @staticmethod
    def test__works_in_sugarless_form() -> None:
        """
        `defer` can be used like `defer(function)(*args, **kwargs)`.
        """

        nums = []

        def f() -> None:
            nums.clear()
            assert nums == []

            defer(nums.append)(0)
            assert nums == []

            nums.append(1)
            assert nums == [1]

            defer(nums.append)(2)
            assert nums == [1]

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert nums == [1, 2, 0]

    @staticmethod
    def test__works_in_mixed_forms() -> None:
        """
        Both forms can work together.
        """

        nums = []

        def f() -> None:
            nums.clear()
            assert nums == []

            defer and nums.append(0)
            assert nums == []

            defer(nums.append)(1)
            assert nums == []

            nums.append(2)
            assert nums == [2]

            defer(nums.append)(3)
            assert nums == [2]

            defer and nums.append(4)
            assert nums == [2]

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert nums == [2, 4, 3, 1, 0]

    @staticmethod
    def test__works_with_free_and_cell_variables() -> None:
        nums = []

        def f() -> None:
            # This is a cell variable with no value
            n0: Never
            # This is a cell variable with value
            i0 = 1

            def f1() -> None:
                # This is a free variable with no value.
                nonlocal n0
                # This is a free variable with value.
                nonlocal i0

                # This is a cell variable with no value
                n1: Never
                # This is a cell variable with value
                i1 = 2

                def f2() -> None:
                    nonlocal n1
                    nonlocal i1

                    i2 = 3

                    defer and nums.append(i2)
                    nums.append(i1)
                    defer and nums.append(-i2)

                    i1 = -i1

                if sys.version_info < (3, 12):
                    from deferrer import defer_scope

                    f2 = defer_scope(f2)

                defer and nums.append(i1)
                f2()
                nums.append(i0)
                f2()
                defer and nums.append(-i1)

                i0 = i0

            if sys.version_info < (3, 12):
                from deferrer import defer_scope

                f1 = defer_scope(f1)

            defer and nums.append(i0)
            f1()
            f1()
            defer and nums.append(-i0)

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert nums == [
            2,
            -3,
            3,
            1,
            -2,
            -3,
            3,
            -2,
            2,
            2,
            -3,
            3,
            1,
            -2,
            -3,
            3,
            -2,
            2,
            -1,
            1,
        ]

    @staticmethod
    def test__emits_warning_for_unsupported_bool_conversion() -> None:
        """
        `defer.__bool__()` is only meant to be indirectly called during
        `defer and ...`.

        If used in another situation, a warning will be emitted.
        """

        with pytest.warns():
            __ = bool(defer)

        with pytest.warns():
            defer or print()

    @staticmethod
    def test__works_as_function_decorator() -> None:
        """
        The typical usage is -

        ```
        @defer
        def _():
            ...
        ```
        """

        nums = []

        def f() -> None:
            nums.clear()
            assert nums == []

            @defer
            def _() -> None:
                nums.append(0)

            assert nums == []

            nums.append(1)
            assert nums == [1]

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert nums == [1, 0]

    @staticmethod
    def test__variables_are_evaluated_beforehand() -> None:
        nums = []

        def f() -> None:
            nums.clear()
            assert nums == []

            i = 0

            # Equivalent to `defer and nums.append(0)`.
            defer and nums.append(i)
            assert nums == []

            i = 1
            nums.append(i)
            assert nums == [1]

            i = 2
            # Equivalent to `defer and nums.append(2)`.
            defer and nums.append(i)
            assert nums == [1]

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert nums == [1, 2, 0]


class Test__deferred_call:
    @staticmethod
    def test__emits_warning_if_left_out() -> None:
        """
        `defer(function)` need to be further called with arguments of
        `function` to work correctly.

        If it doesn't get further called, a warning will be emitted.

        Note
        ----
        If `function` can be called with no argument, the deferred call
        is allowed not to be further called.
        """

        def f() -> None:
            __ = defer(lambda __: None)

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        with pytest.warns():
            f()

    @staticmethod
    def test__cannot_be_further_called_more_than_once() -> None:
        """
        If a deferred call is accidentally further called more than
        once, an exception will be raised. The previous deferred calls,
        including the first further call of this deferred call, will all
        take effect.
        """

        nums = []

        def f() -> None:
            nums.clear()
            assert nums == []

            # This will take effect later.
            defer(nums.append)(0)
            assert nums == []

            nums.append(1)
            assert nums == [1]

            deferred = defer(nums.append)
            # This will also take effect later.
            deferred(2)
            assert nums == [1]
            # This will cause an exception.
            deferred(3)

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        with pytest.raises(Exception):
            f()
        assert nums == [1, 2, 0]

    @staticmethod
    def test__is_allowed_not_to_be_further_called_if_no_argument_is_needed() -> None:
        """
        If a function can be called with no argument, its deferred
        version is allowed not to be further called.

        Such usage is not recommended though.
        """

        nums = []

        def f() -> None:
            nums.clear()
            assert nums == []

            __ = defer(lambda *args: nums.append(0))
            assert nums == []

            nums.append(1)
            assert nums == [1]

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert nums == [1, 0]

    @staticmethod
    def test__user_typeerror_should_not_be_silenced() -> None:
        """
        If a deferred call doesn't get further called, we will try to
        invoke it with no argument. When it is not callable with no
        argument, a `TypeError` will be raised at that point. We will
        catch that `TypeError` and won't re-raise it.

        It is important that `TypeError`s raised by user should not get
        silenced with the same reason.
        """

        def f() -> None:
            def raise_type_error() -> None:
                raise TypeError

            __ = defer(raise_type_error)

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        with pytest.raises(Exception):
            e = None

            def unraisablehook(args: sys.UnraisableHookArgs, /) -> None:
                nonlocal e
                e = args.exc_value

            old_unraisablehook = sys.unraisablehook
            sys.unraisablehook = unraisablehook
            try:
                f()
            finally:
                sys.unraisablehook = old_unraisablehook

            if e is not None:
                raise e

    @staticmethod
    def test__can_write_nonlocal_variables() -> None:
        a = int()
        b = int()
        c = int()

        def f() -> None:
            nonlocal a, b, c

            a = 0
            b = 0
            c = 0

            def b_to_a() -> None:
                nonlocal a
                a = b

            defer and b_to_a()
            assert a == 0
            assert b == 0
            assert c == 0

            def c_to_b() -> None:
                nonlocal b
                b = c

            defer and c_to_b()
            assert a == 0
            assert b == 0
            assert c == 0

            c = 1
            assert a == 0
            assert b == 0
            assert c == 1

            # deferred: b = c
            # deferred: a = b

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert a == 1
        assert b == 1
        assert c == 1


class Test__deferred_exceptions:
    @staticmethod
    def test__are_grouped_and_may_be_unraisable() -> None:
        """
        If any exceptions are raised in deferred actions, they are
        grouped as an `ExceptionGroup`.

        Due to the fact that the deferred actions are performed during
        disposal of local scope, the `ExceptionGroup` may be unraisable.
        """

        def f() -> None:
            def do_raise():
                raise RuntimeError

            defer and do_raise()
            defer and do_raise()

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        with pytest.raises(Exception) as exc_info:
            e = None

            def unraisablehook(args: sys.UnraisableHookArgs, /) -> None:
                nonlocal e
                e = args.exc_value

            old_unraisablehook = sys.unraisablehook
            sys.unraisablehook = unraisablehook
            try:
                f()
            finally:
                sys.unraisablehook = old_unraisablehook

            if e is not None:
                raise e

        e = exc_info.value
        assert isinstance(e, ExceptionGroup)
        e_0, e_1 = e.exceptions
        assert isinstance(e_0, RuntimeError)
        assert isinstance(e_1, RuntimeError)

    @staticmethod
    def test__work_in_generator_function() -> None:
        """ """

        def f():
            # Makes the function a generator function.
            yield

            # Should cause a `ZeroDivisionError` in deferred actions.
            defer and 0 / 0

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        with pytest.raises(Exception) as exc_info:
            e = None

            def unraisablehook(args: sys.UnraisableHookArgs, /) -> None:
                nonlocal e
                e = args.exc_value

            old_unraisablehook = sys.unraisablehook
            sys.unraisablehook = unraisablehook
            try:
                __ = list(f())
            finally:
                sys.unraisablehook = old_unraisablehook

            if e is not None:
                raise e

        e = exc_info.value
        assert isinstance(e, ExceptionGroup)
        (e_0,) = e.exceptions
        assert isinstance(e_0, ZeroDivisionError)

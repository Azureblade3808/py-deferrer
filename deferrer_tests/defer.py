from __future__ import annotations


def defer_is_not_allowed_in_module_level() -> None:
    """
    For `defer` to work, the local scope where `defer` gets used need to
    eventually get disposed with everything in it released at the same
    time.

    If `defer` is used in module level, the local scope is the global
    scope and will never get disposed in time.

    Therefore, an exception is raised to prevent such usages.
    """

    import pytest

    with pytest.raises(Exception) as exc_info:
        from deferrer_tests.samples import sugarful_without_defer_scope as _
    assert not exc_info.errisinstance(ImportError)

    with pytest.raises(Exception):
        from deferrer_tests.samples import sugarless_without_defer_scope as _
    assert not exc_info.errisinstance(ImportError)


def defer_is_not_allowed_in_class_level() -> None:
    """
    For `defer` to work, the local scope where `defer` gets used need to
    eventually get disposed with everything in it released at the same
    time.

    If `defer` is used in class level, everything in the local scope
    will get copied into the class and will never get released in time.

    Therefore, an exception is raised to prevent such usages.
    """

    import pytest

    from deferrer import defer

    with pytest.raises(Exception):

        class _:
            defer and print()

    with pytest.raises(Exception):

        class _:
            defer(print)()


def defer_can_be_used_in_sugarful_form() -> None:
    """
    `defer` can be used like `defer and {expression}`.
    """

    from deferrer import defer

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

    f()
    assert nums == [1, 2, 0]


def defer_can_be_used_in_sugarless_form() -> None:
    """
    `defer` can be used like `defer(function)(*args, **kwargs)`.
    """

    from deferrer import defer

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

    f()
    assert nums == [1, 2, 0]


def defer_can_be_used_in_mixed_forms() -> None:
    """
    Both forms can work together.
    """

    from deferrer import defer

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

    f()
    assert nums == [2, 4, 3, 1, 0]


def there_will_be_warnings_for_unsupported_bool_conversions() -> None:
    """
    `defer.__bool__()` is only meant to be indirectly called during
    `defer and ...`.

    If used in another situation, a warning will be emitted.
    """

    import pytest

    from deferrer import defer

    with pytest.warns():
        __ = bool(defer)

    with pytest.warns():
        defer or print()


def there_will_be_warnings_for_left_out_deferred_calls() -> None:
    """
    `defer(function)` need to be further called with arguments of
    `function` to work correctly.

    If it doesn't get further called, a warning will be emitted.

    Note
    ----
    If `function` can be called with no argument, the deferred call is
    allowed not to be further called.
    """

    import pytest

    from deferrer import defer

    def f() -> None:
        __ = defer(lambda __: None)

    with pytest.warns():
        f()


def deferred_call_cannot_be_further_called_more_than_once() -> None:
    """
    If a deferred call is accidentally further called more than once,
    an exception will be raised. The previous deferred calls, including
    the first further call of this deferred call, will all take effect.
    """

    import pytest

    from deferrer import defer

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

    with pytest.raises(Exception):
        f()
    assert nums == [1, 2, 0]


def deferred_call_with_no_argument_is_allowed_not_to_be_further_called() -> None:
    """
    If a function can be called with no argument, its deferred version
    is allowed not to be further called.

    Such usage is not recommended though.
    """

    from deferrer import defer

    nums = []

    def f() -> None:
        nums.clear()
        assert nums == []

        __ = defer(lambda *args: nums.append(0))
        assert nums == []

        nums.append(1)
        assert nums == [1]

    f()
    assert nums == [1, 0]


def user_typeerror_during_deferred_call_should_not_be_silenced() -> None:
    """
    If a deferred call doesn't get further called, we will try to invoke
    it with no argument. When it is not callable with no argument, a
    `TypeError` will be raised at that point. We will catch that
    `TypeError` and won't re-raise it.

    It is important that `TypeError`s raised by user should not get
    silenced with the same reason.
    """

    import sys
    from typing import cast

    import pytest

    from deferrer import defer

    def f() -> None:
        def raise_type_error() -> None:
            raise TypeError

        __ = defer(raise_type_error)

    with pytest.raises(Exception):
        e = cast("BaseException | None", None)

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


def defer_can_be_used_as_function_decorator() -> None:
    """
    The typical usage is -

    ```
    @defer
    def _():
        ...
    ```
    """

    from deferrer import defer

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

    f()
    assert nums == [1, 0]


def deferred_exceptions_are_grouped_and_unraisable() -> None:
    """
    If any exceptions are raised in deferred actions, they are grouped
    as an `ExceptionGroup`.

    Due to the fact that the deferred actions are performed during
    disposal of local scope, the `ExceptionGroup` will be unraisable.
    """

    import sys
    from typing import cast

    from deferrer import defer

    def f() -> None:
        def do_raise():
            raise RuntimeError

        defer and do_raise()
        defer and do_raise()

    e = cast("BaseException | None", None)

    def unraisablehook(args: sys.UnraisableHookArgs, /) -> None:
        nonlocal e
        e = args.exc_value

    old_unraisablehook = sys.unraisablehook
    sys.unraisablehook = unraisablehook
    f()
    sys.unraisablehook = old_unraisablehook

    assert isinstance(e, ExceptionGroup)
    e_0, e_1 = e.exceptions
    assert isinstance(e_0, RuntimeError)
    assert isinstance(e_1, RuntimeError)


def variables_are_evaluated_when_defer_expression_is_evaluated() -> None:
    from deferrer import defer

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

    f()
    assert nums == [1, 2, 0]


def deferred_function_can_write_nonlocal_variables() -> None:
    from deferrer import defer

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

    f()
    assert a == 1
    assert b == 1
    assert c == 1

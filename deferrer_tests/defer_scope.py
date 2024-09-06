from __future__ import annotations


def defer_scope_can_be_used_to_provide_context_manager() -> None:
    """
    If `defer_scope` is called with no argument, it provides a context
    manager that holds all deferred actions. When the context manager
    exists, the deferred actions it holds get performed.
    """

    from deferrer import defer, defer_scope

    nums = []

    with defer_scope() as _scope_0:
        defer and nums.append(0)
        assert nums == []

        # `defer_scope` can be nested.
        with defer_scope() as _scope_1:
            defer and nums.append(1)
            assert nums == []

            nums.append(2)
            assert nums == [2]

            defer and nums.append(3)
            assert nums == [2]

        # Exits `_scope_1`.
        assert nums == [2, 3, 1]

        defer and nums.append(4)
        assert nums == [2, 3, 1]

    # Exits `_scope_0`.
    assert nums == [2, 3, 1, 4, 0]


def defer_is_allowed_to_be_used_in_module_level_with_defer_scope() -> None:
    """
    Inside a `defer_scope()` context, `defer` is allowed to be used in
    module level.
    """

    from deferrer_tests.samples import sugarless_with_defer_scope as _


def defer_is_allowed_to_be_used_in_class_level_with_defer_scope() -> None:
    """
    Inside a `defer_scope()` context, `defer` is allowed to be used in
    class level.
    """

    from deferrer import defer, defer_scope

    class _:
        with defer_scope():

            @defer
            def _() -> None:
                pass


def defer_scope_can_be_used_to_wrap_functions() -> None:
    """
    When called with a function as the argument, `defer_scope(...)`
    ensures that `defer` should be usable in the function (even in
    Python prior to 3.12).
    """

    from deferrer import defer, defer_scope

    nums = []

    @defer_scope
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


def defer_scope_can_be_used_to_wrap_iterables() -> None:
    """
    When called with an iterable as the argument, `defer_scope(...)`
    returns a similar iterable with one distinct `defer_scope` context
    for each iteration.
    """

    from deferrer import defer, defer_scope

    nums = []

    for i in defer_scope([1, 2, 3]):
        defer and nums.append(-1)
        nums.append(i)
        defer and nums.append(0)

    assert nums == [1, 0, -1, 2, 0, -1, 3, 0, -1]

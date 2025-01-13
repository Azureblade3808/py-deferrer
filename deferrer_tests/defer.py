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
    def test__works_in_sugarful_form_with_very_large_rhs() -> None:
        """
        When RHS part is very large, there will be "EXTENDED_ARG" in RHS
        instructions.
        """

        nums = []

        def f() -> None:
            defer and (
                nums.append(
                    1
                    # There are 512 `int()`s in following lines.
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                    | int()  # type: ignore
                )
            )
            nums.append(0)

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        f()
        assert nums == [0, 1]

    @staticmethod
    def test__works_in_sugarful_form_with_very_huge_amount_of_variables() -> None:
        """
        When there is a lot of variables in current function,
        "EXTENDED_ARG" may be required to specify a certain variable.
        """

        nums = []

        def f(
            # There are 500 arguments here.
            _000 = None,  # type: ignore
            _001 = None,  # type: ignore
            _002 = None,  # type: ignore
            _003 = None,  # type: ignore
            _004 = None,  # type: ignore
            _005 = None,  # type: ignore
            _006 = None,  # type: ignore
            _007 = None,  # type: ignore
            _008 = None,  # type: ignore
            _009 = None,  # type: ignore
            _010 = None,  # type: ignore
            _011 = None,  # type: ignore
            _012 = None,  # type: ignore
            _013 = None,  # type: ignore
            _014 = None,  # type: ignore
            _015 = None,  # type: ignore
            _016 = None,  # type: ignore
            _017 = None,  # type: ignore
            _018 = None,  # type: ignore
            _019 = None,  # type: ignore
            _020 = None,  # type: ignore
            _021 = None,  # type: ignore
            _022 = None,  # type: ignore
            _023 = None,  # type: ignore
            _024 = None,  # type: ignore
            _025 = None,  # type: ignore
            _026 = None,  # type: ignore
            _027 = None,  # type: ignore
            _028 = None,  # type: ignore
            _029 = None,  # type: ignore
            _030 = None,  # type: ignore
            _031 = None,  # type: ignore
            _032 = None,  # type: ignore
            _033 = None,  # type: ignore
            _034 = None,  # type: ignore
            _035 = None,  # type: ignore
            _036 = None,  # type: ignore
            _037 = None,  # type: ignore
            _038 = None,  # type: ignore
            _039 = None,  # type: ignore
            _040 = None,  # type: ignore
            _041 = None,  # type: ignore
            _042 = None,  # type: ignore
            _043 = None,  # type: ignore
            _044 = None,  # type: ignore
            _045 = None,  # type: ignore
            _046 = None,  # type: ignore
            _047 = None,  # type: ignore
            _048 = None,  # type: ignore
            _049 = None,  # type: ignore
            _050 = None,  # type: ignore
            _051 = None,  # type: ignore
            _052 = None,  # type: ignore
            _053 = None,  # type: ignore
            _054 = None,  # type: ignore
            _055 = None,  # type: ignore
            _056 = None,  # type: ignore
            _057 = None,  # type: ignore
            _058 = None,  # type: ignore
            _059 = None,  # type: ignore
            _060 = None,  # type: ignore
            _061 = None,  # type: ignore
            _062 = None,  # type: ignore
            _063 = None,  # type: ignore
            _064 = None,  # type: ignore
            _065 = None,  # type: ignore
            _066 = None,  # type: ignore
            _067 = None,  # type: ignore
            _068 = None,  # type: ignore
            _069 = None,  # type: ignore
            _070 = None,  # type: ignore
            _071 = None,  # type: ignore
            _072 = None,  # type: ignore
            _073 = None,  # type: ignore
            _074 = None,  # type: ignore
            _075 = None,  # type: ignore
            _076 = None,  # type: ignore
            _077 = None,  # type: ignore
            _078 = None,  # type: ignore
            _079 = None,  # type: ignore
            _080 = None,  # type: ignore
            _081 = None,  # type: ignore
            _082 = None,  # type: ignore
            _083 = None,  # type: ignore
            _084 = None,  # type: ignore
            _085 = None,  # type: ignore
            _086 = None,  # type: ignore
            _087 = None,  # type: ignore
            _088 = None,  # type: ignore
            _089 = None,  # type: ignore
            _090 = None,  # type: ignore
            _091 = None,  # type: ignore
            _092 = None,  # type: ignore
            _093 = None,  # type: ignore
            _094 = None,  # type: ignore
            _095 = None,  # type: ignore
            _096 = None,  # type: ignore
            _097 = None,  # type: ignore
            _098 = None,  # type: ignore
            _099 = None,  # type: ignore
            _100 = None,  # type: ignore
            _101 = None,  # type: ignore
            _102 = None,  # type: ignore
            _103 = None,  # type: ignore
            _104 = None,  # type: ignore
            _105 = None,  # type: ignore
            _106 = None,  # type: ignore
            _107 = None,  # type: ignore
            _108 = None,  # type: ignore
            _109 = None,  # type: ignore
            _110 = None,  # type: ignore
            _111 = None,  # type: ignore
            _112 = None,  # type: ignore
            _113 = None,  # type: ignore
            _114 = None,  # type: ignore
            _115 = None,  # type: ignore
            _116 = None,  # type: ignore
            _117 = None,  # type: ignore
            _118 = None,  # type: ignore
            _119 = None,  # type: ignore
            _120 = None,  # type: ignore
            _121 = None,  # type: ignore
            _122 = None,  # type: ignore
            _123 = None,  # type: ignore
            _124 = None,  # type: ignore
            _125 = None,  # type: ignore
            _126 = None,  # type: ignore
            _127 = None,  # type: ignore
            _128 = None,  # type: ignore
            _129 = None,  # type: ignore
            _130 = None,  # type: ignore
            _131 = None,  # type: ignore
            _132 = None,  # type: ignore
            _133 = None,  # type: ignore
            _134 = None,  # type: ignore
            _135 = None,  # type: ignore
            _136 = None,  # type: ignore
            _137 = None,  # type: ignore
            _138 = None,  # type: ignore
            _139 = None,  # type: ignore
            _140 = None,  # type: ignore
            _141 = None,  # type: ignore
            _142 = None,  # type: ignore
            _143 = None,  # type: ignore
            _144 = None,  # type: ignore
            _145 = None,  # type: ignore
            _146 = None,  # type: ignore
            _147 = None,  # type: ignore
            _148 = None,  # type: ignore
            _149 = None,  # type: ignore
            _150 = None,  # type: ignore
            _151 = None,  # type: ignore
            _152 = None,  # type: ignore
            _153 = None,  # type: ignore
            _154 = None,  # type: ignore
            _155 = None,  # type: ignore
            _156 = None,  # type: ignore
            _157 = None,  # type: ignore
            _158 = None,  # type: ignore
            _159 = None,  # type: ignore
            _160 = None,  # type: ignore
            _161 = None,  # type: ignore
            _162 = None,  # type: ignore
            _163 = None,  # type: ignore
            _164 = None,  # type: ignore
            _165 = None,  # type: ignore
            _166 = None,  # type: ignore
            _167 = None,  # type: ignore
            _168 = None,  # type: ignore
            _169 = None,  # type: ignore
            _170 = None,  # type: ignore
            _171 = None,  # type: ignore
            _172 = None,  # type: ignore
            _173 = None,  # type: ignore
            _174 = None,  # type: ignore
            _175 = None,  # type: ignore
            _176 = None,  # type: ignore
            _177 = None,  # type: ignore
            _178 = None,  # type: ignore
            _179 = None,  # type: ignore
            _180 = None,  # type: ignore
            _181 = None,  # type: ignore
            _182 = None,  # type: ignore
            _183 = None,  # type: ignore
            _184 = None,  # type: ignore
            _185 = None,  # type: ignore
            _186 = None,  # type: ignore
            _187 = None,  # type: ignore
            _188 = None,  # type: ignore
            _189 = None,  # type: ignore
            _190 = None,  # type: ignore
            _191 = None,  # type: ignore
            _192 = None,  # type: ignore
            _193 = None,  # type: ignore
            _194 = None,  # type: ignore
            _195 = None,  # type: ignore
            _196 = None,  # type: ignore
            _197 = None,  # type: ignore
            _198 = None,  # type: ignore
            _199 = None,  # type: ignore
            _200 = None,  # type: ignore
            _201 = None,  # type: ignore
            _202 = None,  # type: ignore
            _203 = None,  # type: ignore
            _204 = None,  # type: ignore
            _205 = None,  # type: ignore
            _206 = None,  # type: ignore
            _207 = None,  # type: ignore
            _208 = None,  # type: ignore
            _209 = None,  # type: ignore
            _210 = None,  # type: ignore
            _211 = None,  # type: ignore
            _212 = None,  # type: ignore
            _213 = None,  # type: ignore
            _214 = None,  # type: ignore
            _215 = None,  # type: ignore
            _216 = None,  # type: ignore
            _217 = None,  # type: ignore
            _218 = None,  # type: ignore
            _219 = None,  # type: ignore
            _220 = None,  # type: ignore
            _221 = None,  # type: ignore
            _222 = None,  # type: ignore
            _223 = None,  # type: ignore
            _224 = None,  # type: ignore
            _225 = None,  # type: ignore
            _226 = None,  # type: ignore
            _227 = None,  # type: ignore
            _228 = None,  # type: ignore
            _229 = None,  # type: ignore
            _230 = None,  # type: ignore
            _231 = None,  # type: ignore
            _232 = None,  # type: ignore
            _233 = None,  # type: ignore
            _234 = None,  # type: ignore
            _235 = None,  # type: ignore
            _236 = None,  # type: ignore
            _237 = None,  # type: ignore
            _238 = None,  # type: ignore
            _239 = None,  # type: ignore
            _240 = None,  # type: ignore
            _241 = None,  # type: ignore
            _242 = None,  # type: ignore
            _243 = None,  # type: ignore
            _244 = None,  # type: ignore
            _245 = None,  # type: ignore
            _246 = None,  # type: ignore
            _247 = None,  # type: ignore
            _248 = None,  # type: ignore
            _249 = None,  # type: ignore
            _250 = None,  # type: ignore
            _251 = None,  # type: ignore
            _252 = None,  # type: ignore
            _253 = None,  # type: ignore
            _254 = None,  # type: ignore
            _255 = None,  # type: ignore
            _256 = None,  # type: ignore
            _257 = None,  # type: ignore
            _258 = None,  # type: ignore
            _259 = None,  # type: ignore
            _260 = None,  # type: ignore
            _261 = None,  # type: ignore
            _262 = None,  # type: ignore
            _263 = None,  # type: ignore
            _264 = None,  # type: ignore
            _265 = None,  # type: ignore
            _266 = None,  # type: ignore
            _267 = None,  # type: ignore
            _268 = None,  # type: ignore
            _269 = None,  # type: ignore
            _270 = None,  # type: ignore
            _271 = None,  # type: ignore
            _272 = None,  # type: ignore
            _273 = None,  # type: ignore
            _274 = None,  # type: ignore
            _275 = None,  # type: ignore
            _276 = None,  # type: ignore
            _277 = None,  # type: ignore
            _278 = None,  # type: ignore
            _279 = None,  # type: ignore
            _280 = None,  # type: ignore
            _281 = None,  # type: ignore
            _282 = None,  # type: ignore
            _283 = None,  # type: ignore
            _284 = None,  # type: ignore
            _285 = None,  # type: ignore
            _286 = None,  # type: ignore
            _287 = None,  # type: ignore
            _288 = None,  # type: ignore
            _289 = None,  # type: ignore
            _290 = None,  # type: ignore
            _291 = None,  # type: ignore
            _292 = None,  # type: ignore
            _293 = None,  # type: ignore
            _294 = None,  # type: ignore
            _295 = None,  # type: ignore
            _296 = None,  # type: ignore
            _297 = None,  # type: ignore
            _298 = None,  # type: ignore
            _299 = None,  # type: ignore
            _300 = None,  # type: ignore
            _301 = None,  # type: ignore
            _302 = None,  # type: ignore
            _303 = None,  # type: ignore
            _304 = None,  # type: ignore
            _305 = None,  # type: ignore
            _306 = None,  # type: ignore
            _307 = None,  # type: ignore
            _308 = None,  # type: ignore
            _309 = None,  # type: ignore
            _310 = None,  # type: ignore
            _311 = None,  # type: ignore
            _312 = None,  # type: ignore
            _313 = None,  # type: ignore
            _314 = None,  # type: ignore
            _315 = None,  # type: ignore
            _316 = None,  # type: ignore
            _317 = None,  # type: ignore
            _318 = None,  # type: ignore
            _319 = None,  # type: ignore
            _320 = None,  # type: ignore
            _321 = None,  # type: ignore
            _322 = None,  # type: ignore
            _323 = None,  # type: ignore
            _324 = None,  # type: ignore
            _325 = None,  # type: ignore
            _326 = None,  # type: ignore
            _327 = None,  # type: ignore
            _328 = None,  # type: ignore
            _329 = None,  # type: ignore
            _330 = None,  # type: ignore
            _331 = None,  # type: ignore
            _332 = None,  # type: ignore
            _333 = None,  # type: ignore
            _334 = None,  # type: ignore
            _335 = None,  # type: ignore
            _336 = None,  # type: ignore
            _337 = None,  # type: ignore
            _338 = None,  # type: ignore
            _339 = None,  # type: ignore
            _340 = None,  # type: ignore
            _341 = None,  # type: ignore
            _342 = None,  # type: ignore
            _343 = None,  # type: ignore
            _344 = None,  # type: ignore
            _345 = None,  # type: ignore
            _346 = None,  # type: ignore
            _347 = None,  # type: ignore
            _348 = None,  # type: ignore
            _349 = None,  # type: ignore
            _350 = None,  # type: ignore
            _351 = None,  # type: ignore
            _352 = None,  # type: ignore
            _353 = None,  # type: ignore
            _354 = None,  # type: ignore
            _355 = None,  # type: ignore
            _356 = None,  # type: ignore
            _357 = None,  # type: ignore
            _358 = None,  # type: ignore
            _359 = None,  # type: ignore
            _360 = None,  # type: ignore
            _361 = None,  # type: ignore
            _362 = None,  # type: ignore
            _363 = None,  # type: ignore
            _364 = None,  # type: ignore
            _365 = None,  # type: ignore
            _366 = None,  # type: ignore
            _367 = None,  # type: ignore
            _368 = None,  # type: ignore
            _369 = None,  # type: ignore
            _370 = None,  # type: ignore
            _371 = None,  # type: ignore
            _372 = None,  # type: ignore
            _373 = None,  # type: ignore
            _374 = None,  # type: ignore
            _375 = None,  # type: ignore
            _376 = None,  # type: ignore
            _377 = None,  # type: ignore
            _378 = None,  # type: ignore
            _379 = None,  # type: ignore
            _380 = None,  # type: ignore
            _381 = None,  # type: ignore
            _382 = None,  # type: ignore
            _383 = None,  # type: ignore
            _384 = None,  # type: ignore
            _385 = None,  # type: ignore
            _386 = None,  # type: ignore
            _387 = None,  # type: ignore
            _388 = None,  # type: ignore
            _389 = None,  # type: ignore
            _390 = None,  # type: ignore
            _391 = None,  # type: ignore
            _392 = None,  # type: ignore
            _393 = None,  # type: ignore
            _394 = None,  # type: ignore
            _395 = None,  # type: ignore
            _396 = None,  # type: ignore
            _397 = None,  # type: ignore
            _398 = None,  # type: ignore
            _399 = None,  # type: ignore
            _400 = None,  # type: ignore
            _401 = None,  # type: ignore
            _402 = None,  # type: ignore
            _403 = None,  # type: ignore
            _404 = None,  # type: ignore
            _405 = None,  # type: ignore
            _406 = None,  # type: ignore
            _407 = None,  # type: ignore
            _408 = None,  # type: ignore
            _409 = None,  # type: ignore
            _410 = None,  # type: ignore
            _411 = None,  # type: ignore
            _412 = None,  # type: ignore
            _413 = None,  # type: ignore
            _414 = None,  # type: ignore
            _415 = None,  # type: ignore
            _416 = None,  # type: ignore
            _417 = None,  # type: ignore
            _418 = None,  # type: ignore
            _419 = None,  # type: ignore
            _420 = None,  # type: ignore
            _421 = None,  # type: ignore
            _422 = None,  # type: ignore
            _423 = None,  # type: ignore
            _424 = None,  # type: ignore
            _425 = None,  # type: ignore
            _426 = None,  # type: ignore
            _427 = None,  # type: ignore
            _428 = None,  # type: ignore
            _429 = None,  # type: ignore
            _430 = None,  # type: ignore
            _431 = None,  # type: ignore
            _432 = None,  # type: ignore
            _433 = None,  # type: ignore
            _434 = None,  # type: ignore
            _435 = None,  # type: ignore
            _436 = None,  # type: ignore
            _437 = None,  # type: ignore
            _438 = None,  # type: ignore
            _439 = None,  # type: ignore
            _440 = None,  # type: ignore
            _441 = None,  # type: ignore
            _442 = None,  # type: ignore
            _443 = None,  # type: ignore
            _444 = None,  # type: ignore
            _445 = None,  # type: ignore
            _446 = None,  # type: ignore
            _447 = None,  # type: ignore
            _448 = None,  # type: ignore
            _449 = None,  # type: ignore
            _450 = None,  # type: ignore
            _451 = None,  # type: ignore
            _452 = None,  # type: ignore
            _453 = None,  # type: ignore
            _454 = None,  # type: ignore
            _455 = None,  # type: ignore
            _456 = None,  # type: ignore
            _457 = None,  # type: ignore
            _458 = None,  # type: ignore
            _459 = None,  # type: ignore
            _460 = None,  # type: ignore
            _461 = None,  # type: ignore
            _462 = None,  # type: ignore
            _463 = None,  # type: ignore
            _464 = None,  # type: ignore
            _465 = None,  # type: ignore
            _466 = None,  # type: ignore
            _467 = None,  # type: ignore
            _468 = None,  # type: ignore
            _469 = None,  # type: ignore
            _470 = None,  # type: ignore
            _471 = None,  # type: ignore
            _472 = None,  # type: ignore
            _473 = None,  # type: ignore
            _474 = None,  # type: ignore
            _475 = None,  # type: ignore
            _476 = None,  # type: ignore
            _477 = None,  # type: ignore
            _478 = None,  # type: ignore
            _479 = None,  # type: ignore
            _480 = None,  # type: ignore
            _481 = None,  # type: ignore
            _482 = None,  # type: ignore
            _483 = None,  # type: ignore
            _484 = None,  # type: ignore
            _485 = None,  # type: ignore
            _486 = None,  # type: ignore
            _487 = None,  # type: ignore
            _488 = None,  # type: ignore
            _489 = None,  # type: ignore
            _490 = None,  # type: ignore
            _491 = None,  # type: ignore
            _492 = None,  # type: ignore
            _493 = None,  # type: ignore
            _494 = None,  # type: ignore
            _495 = None,  # type: ignore
            _496 = None,  # type: ignore
            _497 = None,  # type: ignore
            _498 = None,  # type: ignore
            _499 = None,  # type: ignore
        ) -> None:
            defer and nums.append(0)
            nums.append(1)
            defer and nums.append(2)

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
        assert nums == [2, -3, 3, 1, -2, -3, 3, -2, 2, 2, -3, 3, 1, -2, -3, 3, -2, 2, -1, 1]

    @staticmethod
    def test__works_with_unbound_variables() -> None:
        v1 = 1
        v2 = 2
        v3 = 3
        del v2
        v4 = 4
        v5 = 5
        v6 = 6
        del v5

        def f(v7=7, v8=8, v9=9, v10=10, v11=11, v12=12):
            nonlocal v4, v5, v6
            v4 = v4
            v6 = v6
            del v8
            del v11
            v13 = 13
            v14 = 14
            v15 = 15
            del v14

            def _():
                # This function is not called and it exists only to make sure that the
                # following variables get transformed into cell variables in the outer
                # function.
                v4, v5, v6, v10, v11, v12, v13, v14, v15  # type: ignore

            defer and nums.append(v1)
            defer and nums.append(v3)
            defer and nums.append(v4)
            defer and nums.append(v6)
            defer and nums.append(v7)
            defer and nums.append(v9)
            defer and nums.append(v10)
            defer and nums.append(v12)
            defer and nums.append(v13)
            defer and nums.append(v15)

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        nums = []
        f()
        assert nums == [15, 13, 12, 10, 9, 7, 6, 4, 3, 1]

    @staticmethod
    def test__works_with_arguments() -> None:
        def f(x=0) -> None:
            defer and nums.append(x)
            nums.append(0)
            defer and nums.append(-x)

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        nums = []
        f()
        assert nums == [0, 0, 0]

        nums = []
        f(0)
        assert nums == [0, 0, 0]

        nums = []
        f(1)
        assert nums == [0, -1, 1]

    @staticmethod
    def test__works_with_arguments_as_cell_variables() -> None:
        def f(x=0) -> None:
            defer and nums.append(x)
            nums.append(0)
            defer and nums.append(-x)

            # Makes `x` a cell variable.
            def _():
                x

        if sys.version_info < (3, 12):
            from deferrer import defer_scope

            f = defer_scope(f)

        nums = []
        f()
        assert nums == [0, 0, 0]

        nums = []
        f(0)
        assert nums == [0, 0, 0]

        nums = []
        f(1)
        assert nums == [0, -1, 1]

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

        if sys.version_info >= (3, 12):

            def f():
                # Makes the function a generator function.
                yield

                # Should cause a `ZeroDivisionError` in deferred actions.
                defer and 0 / 0

        else:

            from deferrer import defer_scope

            def f():
                with defer_scope():
                    # Makes the function a generator function.
                    yield

                    # Should cause a `ZeroDivisionError` in deferred actions.
                    defer and 0 / 0

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

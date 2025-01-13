# Fancy `defer` for Python >= 3.12 (partially supported in Python 3.11)

[![Python package](https://github.com/Azureblade3808/py-deferrer/actions/workflows/python-package.yml/badge.svg)](https://github.com/Azureblade3808/py-deferrer/actions/workflows/python-package.yml)
[![Coverage Status](https://coveralls.io/repos/github/Azureblade3808/py-deferrer/badge.svg)](https://coveralls.io/github/Azureblade3808/py-deferrer)

## Installation

You may install `deferrer` by running `pip install deferrer`.

## Usage

### `defer`

There are two designed ways to use `defer`. You may use either of them, or mix them up.

One is to use `defer` as a syntactic sugar in the form of `defer and ...`. Example:

```python
>>> from deferrer import defer

>>> def f():
...     defer and print("deferred")
...     print("normal")

>>> import sys
>>> if sys.version_info < (3, 12):
...     from deferrer import defer_scope
...     f = defer_scope(f)

>>> f()
normal
deferred

```

The other is to use `defer` as a function wrapper. Example:

```python
>>> from deferrer import defer

>>> def f():
...     defer(print)("deferred")
...     print("normal")

>>> import sys
>>> if sys.version_info < (3, 12):
...     from deferrer import defer_scope
...     f = defer_scope(f)

>>> f()
normal
deferred

```

Note that when the deferred function can be invoke with no arguments, an empty call is not required, which means `defer` can be used as a decorator. Example:

```python
>>> from deferrer import defer

>>> def f():
...     @defer
...     def _():
...         print("deferred")
...
...     print("normal")

>>> import sys
>>> if sys.version_info < (3, 12):
...     from deferrer import defer_scope
...     f = defer_scope(f)

>>> f()
normal
deferred

```

### `defer_scope`

You can use `defer_scope` to declare a code range that deferred actions should be gathered in and executed after.

It's not rare that you may want to defer some actions in a loop and get them executed at the end of each cycle. But unlike some other languages, loops in Python don't create new scopes, which makes it inconvenient to use `defer` in them. `defer_scope` can be used to wrap an iterable to gather deferred actions in each iteration and execute them at the end of the iteration. Example:

```python
>>> from deferrer import defer, defer_scope

>>> def f():
...     for i in defer_scope(range(3)):
...         defer and print("deferred", i)
...         print("normal", i)

>>> f()
normal 0
deferred 0
normal 1
deferred 1
normal 2
deferred 2

```

Sometimes, you may want to use `defer` outside of a function. `defer_scope` can be used as a context manager to gather deferred actions when it's entered and execute them when it's exited. Example:

```python
>>> from deferrer import defer, defer_scope

>>> with defer_scope():
...     # Note that `defer and ...` itself is an expression, and
...     # its value (i.e. the `defer` object) may get printed by
...     # some interpretters.
...     # Use an assignment to suppress the printing behavior.
...     _ = defer and print("deferred")
...     print("normal")
normal
deferred

```

Also, `defer_scope` can be used to wrap a function to help `defer` to work properly in Python 3.11. Note that `locals()` in Python 3.11 returns a copy of the local scope, which makes it impossible for `defer` to inject deferred actions into the real local scope. Without a function level `defer_scope`, deferred actions would be executed immediately after they are evaluated.

## Known Limitations

-   `deferrer` has only been tested on CPython. It may not work on other Python implementations.
-   `defer` must not be used together with `await`. Code like `defer and await ...` is syntactically acceptable but will cause segmentetation fault without being detected beforehand.

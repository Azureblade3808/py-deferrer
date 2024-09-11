# Fancy `defer` in Python 3.12

[![Python package](https://github.com/Azureblade3808/py-deferrer/actions/workflows/python-package.yml/badge.svg)](https://github.com/Azureblade3808/py-deferrer/actions/workflows/python-package.yml)
[![Coverage Status](https://coveralls.io/repos/github/Azureblade3808/py-deferrer/badge.svg)](https://coveralls.io/github/Azureblade3808/py-deferrer)

## Installation and usage

### Installation

You may install `deferrer` by running `pip install deferrer`.

### Usage

There are two designed ways to use `defer`. You may use either of them, or mix them up.

#### Sugarful

```python
>>> from deferrer import defer

>>> def f():
...     defer and print(0)
...     defer and print(1)
...     print(2)
...     defer and print(3)
...     defer and print(4)

>>> import sys
>>> if sys.version_info < (3, 12):
...     from deferrer import defer_scope
...     f = defer_scope(f)

>>> f()
2
4
3
1
0

```

#### Sugarless

```python
>>> from deferrer import defer

>>> def f():
...     defer(print)(0)
...     defer(print)(1)
...     print(2)
...     defer(print)(3)
...     defer(print)(4)

>>> import sys
>>> if sys.version_info < (3, 12):
...     from deferrer import defer_scope
...     f = defer_scope(f)

>>> f()
2
4
3
1
0

```

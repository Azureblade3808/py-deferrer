# Specifications

## `defer` can be used in two forms

There are two ways to use `defer`. One is called _sugarful_ and the other is called _sugarless_.

A typical _sugarful_ usage is like

```python
>>> from deferrer import defer

>>> def f():
...     defer and print(0)
...     print(1)

>>> f()
1
0

```

A typical _sugarless_ usage is like

```python
>>> from deferrer import defer

>>> def f():
...     defer(print)(0)
...     print(1)

>>> f()
1
0

```

You may use either of them, or mix them up.

```python
>>> from deferrer import defer

>>> def f():
...     defer and print(0)
...     defer(print)(1)
...     print(2)

>>> f()
2
1
0

```

## `defer` can only be used in functions

The implementation of `defer` relies on the fact that the local scope, along with some temporary objects we put in it, will eventually be released when the function ends.

It is never the same case for a global scope or a class scope, whereas a global scope will nearly never get disposed and objects in a class scope are copied into the class and therefore retained.

As a prevention, when `defer` is (incorrectly) used in a global scope or a class scope, a `RuntimeError` is raised.

```python
>>> from deferrer import defer

>>> defer and print()
Traceback (most recent call last):
    ...
RuntimeError: ...

>>> defer(print)()
Traceback (most recent call last):
    ...
RuntimeError: ...

>>> class C:
...     defer and print()
Traceback (most recent call last):
    ...
RuntimeError: ...

>>> class C:
...     defer(print)()
Traceback (most recent call last):
    ...
RuntimeError: ...

```

## A deferred function’s arguments are evaluated when the defer statement is evaluated

(Paragraph title is borrowed from [The Go Blog](https://go.dev/blog/defer-panic-and-recover))

```python
>>> from deferrer import defer

>>> def f():
...     x = 0
...     defer and print(x)
...     x = 1
...     defer and print(x)
...     x = 2
...     print(x)

>>> f()
2
1
0

```

```python
>>> from deferrer import defer

>>> def f():
...     x = 0
...     defer(print)(x)
...     x = 1
...     defer(print)(x)
...     x = 2
...     print(x)

>>> f()
2
1
0

```

If you don't want this behavior, you may try embedded functions with non-local variables.

```python
>>> from deferrer import defer

>>> def f():
...     x = 0
...
...     @defer
...     def _():
...         print(x)
...
...     x = 1
...
...     @defer
...     def _():
...         print(x)
...
...     x = 2
...     print(x)

>>> f()
2
2
2

```

## `defer_scope` can be used to explicitly declare where the deferred actions should be drained

```python
>>> from deferrer import defer, defer_scope

>>> with defer_scope():
...     __ = defer and print(0)  # If the result is not used, it will be printed.
...     print(1)
1
0

```

## `defer_scope` can be used to wrap an iterable and drain deferred actions when each loop ends

```python
>>> from deferrer import defer, defer_scope

>>> for i in defer_scope(range(3)):
...     __ = defer and print(-i)  # If the result is not used, it will be printed.
...     print(i)
0
0
1
-1
2
-2

```

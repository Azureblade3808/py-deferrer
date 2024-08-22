# Usages

## Sugarless 

```python
>>> from deferrer import defer

>>> def f():
...     defer(print)(0)
...     defer(print)(1)
...     print(2)

>>> f0()
2
1
0
```

## Sugarful

```python
>>> from deferrer import defer

>>> def f():
...     defer and print(0)
...     defer and print(1)
...     print(2)

>>> f()
2
1
0
```

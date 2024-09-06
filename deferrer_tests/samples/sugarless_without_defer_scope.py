from deferrer import defer

# The following line will cause a `RuntimeError`.
defer(lambda: None)()

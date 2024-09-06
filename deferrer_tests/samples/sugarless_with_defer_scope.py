from deferrer import defer, defer_scope

# `defer` is allowed in a `defer_scope()` context.
with defer_scope():

    @defer
    def _() -> None:
        pass

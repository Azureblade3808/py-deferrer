from __future__ import annotations

__all__ = []

from ._sugarless import defer

# The following line should cause a `RuntimeError`.
defer(print)()

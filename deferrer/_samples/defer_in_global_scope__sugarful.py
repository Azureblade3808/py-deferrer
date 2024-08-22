from __future__ import annotations

__all__ = []

from .. import defer

# The following line should cause a `RuntimeError`.
defer and print()

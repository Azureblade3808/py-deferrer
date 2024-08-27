from __future__ import annotations

__all__ = []

from deferrer._sugarful import defer

# The following line should cause a `RuntimeError`.
defer and print()

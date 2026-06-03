"""Readiness facade for non-executing action eligibility diagnostics.

The current v0.3 implementation exposes click readiness through
`click_policy.py`; this module gives callers a neutral readiness import path
without changing execution policy or enabling desktop input.
"""

from __future__ import annotations

from .click_policy import (
    click_readiness_metadata,
    click_readiness_not_applicable,
    evaluate_click_readiness,
)


__all__ = [
    "click_readiness_metadata",
    "click_readiness_not_applicable",
    "evaluate_click_readiness",
]

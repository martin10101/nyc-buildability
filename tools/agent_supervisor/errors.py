#!/usr/bin/env python3
"""The loop's error taxonomy, in one place (D-007).

`LoopError` lives here rather than in `loop.py` so the modules that make up the
loop - `owner_touch.py`, `loop_breakers.py` - can raise the SAME error the loop
raises without importing the loop itself. Every refusal in this package carries a
CODE as well as a message: an operator, a wrapper script, and
`refusals.outcome_for_loop_refusal` all key off the code, never off prose.
"""
from __future__ import annotations


class LoopError(Exception):
    """The loop refused to do something. Always carries a code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message

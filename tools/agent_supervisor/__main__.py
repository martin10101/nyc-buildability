#!/usr/bin/env python3
"""Entry point for `python -m tools.agent_supervisor` (D-007 S12.1).

Also supports being run as `python tools/agent_supervisor/__main__.py` by adding
the repository root to `sys.path` when the package context is missing, so an
operator does not have to be in exactly the right directory to run `doctor`.
"""
from __future__ import annotations

import sys

if __package__ in (None, ""):  # pragma: no cover - direct-script invocation
    import pathlib

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    from tools.agent_supervisor.cli import main
else:
    from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())

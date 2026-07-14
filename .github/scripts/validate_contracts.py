#!/usr/bin/env python3
"""Validate that every contract schema parses as JSON and declares $schema/$id.

Used by the `contracts` CI job (task M0-T004). Standard library only, so it
runs on any GitHub-hosted runner without installing dependencies.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCHEMA_ROOT = Path("packages/contracts/schemas")
REQUIRED_KEYS = ("$schema", "$id", "title", "description")


def main() -> int:
    if not SCHEMA_ROOT.is_dir():
        print(f"ERROR: schema root not found: {SCHEMA_ROOT}", file=sys.stderr)
        return 1

    schema_files = sorted(SCHEMA_ROOT.rglob("*.json"))
    if not schema_files:
        print(f"ERROR: no schema files found under {SCHEMA_ROOT}", file=sys.stderr)
        return 1

    failures = 0
    for schema_file in schema_files:
        try:
            with schema_file.open(encoding="utf-8") as handle:
                document = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"FAIL {schema_file}: does not parse as JSON: {exc}", file=sys.stderr)
            failures += 1
            continue

        missing = [key for key in REQUIRED_KEYS if key not in document]
        if missing:
            print(f"FAIL {schema_file}: missing keys {missing}", file=sys.stderr)
            failures += 1
            continue

        print(f"OK   {schema_file} ({document['title']})")

    print(f"Checked {len(schema_files)} schema file(s); {failures} failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

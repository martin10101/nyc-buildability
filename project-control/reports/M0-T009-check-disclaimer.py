#!/usr/bin/env python3
"""M0-T009 self-check (defect D4): apps/web/src/lib/disclaimer.ts must equal
the PRD section 29 disclaimer byte-for-byte, including the U+2019 typographic
apostrophe in "platform's". Read-only; exits nonzero on mismatch."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRD = REPO_ROOT / "PRD.md"
TS = REPO_ROOT / "apps" / "web" / "src" / "lib" / "disclaimer.ts"


def main() -> int:
    prd_text = PRD.read_text(encoding="utf-8")
    match = re.search(r"^> (This platform provides preliminary.*?construction\.)\s*$",
                      prd_text, re.MULTILINE | re.DOTALL)
    if not match:
        print("FAIL: PRD s29 blockquote not found", file=sys.stderr)
        return 1
    prd_disclaimer = " ".join(line.lstrip("> ").rstrip() for line in match.group(1).splitlines())

    ts_source = TS.read_text(encoding="utf-8")
    segments = re.findall(r'"((?:[^"\\]|\\.)*)"', ts_source)
    ts_disclaimer = "".join(seg.encode().decode("unicode_escape") if "\\" in seg else seg
                            for seg in segments)

    print(f"PRD  bytes: {len(prd_disclaimer.encode('utf-8'))}")
    print(f"TS   bytes: {len(ts_disclaimer.encode('utf-8'))}")
    apostrophe = "’"
    print(f"PRD uses U+2019 ({unicodedata.name(apostrophe)}): {apostrophe in prd_disclaimer}")
    print(f"TS  uses U+2019: {apostrophe in ts_disclaimer}")

    if prd_disclaimer == ts_disclaimer:
        print("PASS: disclaimer.ts matches PRD s29 byte-for-byte")
        return 0

    for i, (a, b) in enumerate(zip(prd_disclaimer, ts_disclaimer)):
        if a != b:
            print(f"FAIL: first difference at index {i}: PRD={a!r} (U+{ord(a):04X}) "
                  f"TS={b!r} (U+{ord(b):04X})", file=sys.stderr)
            print(f"context: ...{prd_disclaimer[max(0, i-30):i+30]!r}...", file=sys.stderr)
            return 1
    print(f"FAIL: length mismatch: PRD={len(prd_disclaimer)} TS={len(ts_disclaimer)}",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

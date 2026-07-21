#!/usr/bin/env python3
"""Context-budget guard for the automatic project-instruction load.

Before 2026-07-21 every session (and every subagent) eagerly loaded ~93 KB / ~23k tokens of
project instructions — root `CLAUDE.md` plus nine `@`-imported documents plus two unconditional
`.claude/rules/` files — before any task work began. This check fails CI if that automatic budget
regrows, if an unconditional rule accumulates retired/superseded history that belongs in
`docs/archive/`, if a known stale status board loses its HISTORICAL label, or if a new duplicate
current-status task board appears.

What counts as "eager" (auto-loaded, no user action):
  - root `CLAUDE.md`
  - every file it `@`-imports, recursively (resolved only if the path exists in the repo)
  - every `.claude/rules/*.md` WITHOUT `paths:` frontmatter (unconditional rules load every session)

Path-scoped rules (with `paths:`) and documents referenced in backticks are NOT eager and are not
counted. Tokens are estimated as ceil(chars / 4).

Stdlib only. No network, no writes. Exit 0 if all checks pass, 1 otherwise.
Usage: python tools/context_budget_check.py [--config tools/context_budget.json]
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMPORT_RE = re.compile(r"(?:^|\s)@([^\s]+)")


def tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def is_unconditional_rule(path: pathlib.Path) -> bool:
    """A rule is eager (unconditional) unless it has a `paths:` key in front-matter."""
    text = read(path)
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return True
    return "paths:" not in m.group(1)


def resolve_imports(path: pathlib.Path, visited: set[pathlib.Path]) -> list[pathlib.Path]:
    """Recursively resolve @-imports that point at real repo files."""
    out: list[pathlib.Path] = []
    if path in visited or not path.exists():
        return out
    visited.add(path)
    for token in IMPORT_RE.findall(read(path)):
        target = (ROOT / token).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            continue  # outside repo
        if target.exists() and target.is_file() and target not in visited:
            out.append(target)
            out.extend(resolve_imports(target, visited))
    return out


def eager_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    claude = ROOT / "CLAUDE.md"
    if claude.exists():
        files.append(claude)
        # Pass an empty visited set: resolve_imports adds `claude` itself, then follows its
        # @-imports recursively. (Seeding it with {claude} would short-circuit and count nothing.)
        files.extend(resolve_imports(claude, set()))
    for rule in sorted((ROOT / ".claude" / "rules").glob("*.md")):
        if is_unconditional_rule(rule):
            files.append(rule)
    # de-dupe preserving order
    seen: set[pathlib.Path] = set()
    uniq = []
    for f in files:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return uniq


def split_sections(text: str) -> list[str]:
    sections: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        if line.startswith("#") and cur:
            sections.append("\n".join(cur))
            cur = [line]
        else:
            cur.append(line)
    if cur:
        sections.append("\n".join(cur))
    return sections


def main(argv: list[str]) -> int:
    cfg_path = ROOT / "tools" / "context_budget.json"
    if "--config" in argv:
        cfg_path = pathlib.Path(argv[argv.index("--config") + 1])
    cfg = json.loads(read(cfg_path))

    failures: list[str] = []
    print("# Context-budget check\n")

    # 1) Eager project-instruction budget --------------------------------------
    files = eager_files()
    total_tok = 0
    total_bytes = 0
    print("## Eager (auto-loaded) project instructions")
    for f in files:
        text = read(f)
        b = len(f.read_bytes())
        t = tokens(text)
        total_tok += t
        total_bytes += b
        rel = f.relative_to(ROOT).as_posix()
        print(f"  {b:>7}B  ~{t:>5} tok  {rel}")
    budget = cfg["eager_token_budget"]
    print(f"  ---- eager total: {total_bytes}B  ~{total_tok} tok  (budget {budget} tok)")
    if total_tok > budget:
        failures.append(
            f"eager project-instruction budget exceeded: ~{total_tok} tok > {budget} tok "
            f"(the @-import / unconditional-rule load regrew — move detail to on-demand docs or path-scoped rules)"
        )

    # 2) Session-handoff cap ---------------------------------------------------
    handoff = ROOT / cfg["handoff_file"]
    if handoff.exists():
        h = tokens(read(handoff))
        hb = cfg["handoff_token_budget"]
        print(f"\n## Session handoff\n  ~{h} tok  {cfg['handoff_file']}  (budget {hb} tok)")
        if h > hb:
            failures.append(
                f"session handoff too large: ~{h} tok > {hb} tok "
                f"(keep it current-only; move old sessions to docs/archive/session-handoffs/)"
            )

    # 3) Known stale boards must carry a HISTORICAL marker near the top --------
    print("\n## Historical markers on known stale status docs")
    marker = re.compile(cfg["historical_marker_regex"], re.I)
    nlines = cfg["historical_marker_scan_lines"]
    for rel in cfg["historical_required"]:
        p = ROOT / rel
        if not p.exists():
            print(f"  SKIP (absent): {rel}")
            continue
        head = "\n".join(read(p).splitlines()[:nlines])
        ok = bool(marker.search(head))
        print(f"  {'OK ' if ok else 'MISSING'}  {rel}")
        if not ok:
            failures.append(
                f"stale status doc missing a HISTORICAL marker in its first {nlines} lines: {rel}"
            )

    # 4) Unconditional rules must not hoard retired/superseded narrative -------
    print("\n## Retired/superseded sections in unconditional rules")
    retired = re.compile(r"(?i)\b(" + "|".join(map(re.escape, cfg["retired_markers"])) + r")\b")
    min_chars = cfg["retired_section_min_chars"]
    exempt = cfg["archive_exempt_substring"]
    flagged = False
    for rule in sorted((ROOT / ".claude" / "rules").glob("*.md")):
        if not is_unconditional_rule(rule):
            continue
        for sec in split_sections(read(rule)):
            if retired.search(sec) and len(sec) > min_chars and exempt not in sec:
                flagged = True
                rel = rule.relative_to(ROOT).as_posix()
                head = sec.splitlines()[0][:70]
                failures.append(
                    f"unconditional rule {rel} holds a retired/superseded section "
                    f'("{head}") > {min_chars} chars with no {exempt} link — move it to docs/archive/'
                )
    if not flagged:
        print("  OK - none (retired history is archived or absent)")

    # 5) No new duplicate current-status task board ---------------------------
    print("\n## Duplicate current-status task boards")
    status_hdr = re.compile(cfg["board_status_header_regex"], re.I)
    task_id = re.compile(cfg["board_task_id_regex"])
    allow = set(cfg["board_allowlist"]) | set(cfg["historical_required"])
    boards = []
    seen_paths: set[str] = set()
    for glob in cfg["board_scan_globs"]:
        for p in sorted(ROOT.glob(glob)):
            rel = p.relative_to(ROOT).as_posix()
            if rel in seen_paths or rel.startswith("docs/archive/"):
                continue
            seen_paths.add(rel)
            text = read(p)
            if status_hdr.search(text) and len(task_id.findall(text)) >= cfg["board_min_task_rows"]:
                boards.append(rel)
    for rel in boards:
        labelled = rel in cfg["historical_required"]
        allowed = rel in allow
        status = "HISTORICAL-labelled" if labelled else ("allowlisted" if allowed else "UNACCOUNTED")
        print(f"  {rel}: {status}")
        if not allowed:
            failures.append(
                f"possible duplicate current-status task board: {rel} — label it HISTORICAL "
                f"(and add to historical_required) or, if it is a legitimate plan, add it to board_allowlist"
            )

    # Verdict ------------------------------------------------------------------
    print("\n## Result")
    if failures:
        print(f"FAIL — {len(failures)} issue(s):")
        for i, f in enumerate(failures, 1):
            print(f"  {i}. {f}")
        return 1
    print("PASS - automatic context budget within limits; no stale/duplicate/retired regressions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

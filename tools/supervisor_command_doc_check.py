#!/usr/bin/env python3
"""CI tooth: validate every presented supervisor command against the live contract.

D-024 Amendment 22 defects D1/D14/D15/D17 (M0-T125 register), wired into CI. The
living operator docs present ``start`` (and other) commands; this entry extracts
each presented supervisor command and dry-runs it against ``cli.build_parser()``,
``start_gate.dispatch_inputs_missing`` and the pinned-flag set (via
``tools.agent_supervisor.command_docs``), failing CLOSED (exit 1) on ANY drift in
either direction. It launches nothing, contacts no provider, and never opens the
live journal (R374/R375 intact).

Removal-sensitive: delete ``--worktree`` (or any pinned flag) from a presented
start command, or delete this check from CI, and the guard is gone — which is
exactly the gap the live exit-11 refusal fell through (register D17: the defect
escaped 2,889 tests and five certifications because no test parsed the presented
documents).

Docs scanned are the LIVING operator docs this task owns; point-in-time
certification reports under ``project-control/reports/`` are historical
snapshots, not living command sources, and are not scanned here.

Usage:
    python tools/supervisor_command_doc_check.py [--doc PATH ...]

Exit codes: 0 = every presented command matches the live contract; 1 = drift.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

# Bootstrap the repo root onto sys.path so the package imports whether invoked as
# a bare script (CI: `python tools/supervisor_command_doc_check.py`) or otherwise.
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.agent_supervisor import command_docs  # noqa: E402
from tools.agent_supervisor.cli import build_parser  # noqa: E402

#: The living operator RUNBOOK whose presented supervisor commands an operator
#: literally runs, and which the register names (§1/§5/§11). Relative to the repo
#: root. The package README presents pedagogical ``<placeholder>`` templates
#: rather than concrete operator commands (the extractor skips templates), so it
#: is not a strict command source and is not scanned by default.
DEFAULT_DOCS: tuple[str, ...] = (
    "docs/CONTROLLER_UPDATE_RUNBOOK.md",
)


def check_docs(doc_paths: list[pathlib.Path]) -> tuple[int, list[str]]:
    """Validate every presented supervisor command in ``doc_paths``.

    Returns ``(failure_count, lines)`` where ``lines`` is the human-readable
    report. A doc with no presented supervisor command is reported and is not a
    failure (it simply carries none).
    """
    parser = build_parser()
    lines: list[str] = []
    failures = 0
    total = 0
    for path in doc_paths:
        if not path.exists():
            failures += 1
            lines.append(f"FAIL  {path}: document not found")
            continue
        text = path.read_text(encoding="utf-8")
        verdicts = command_docs.validate_document(text, parser, source=str(path))
        if not verdicts:
            lines.append(f"ok    {path}: no presented supervisor command")
            continue
        for verdict in verdicts:
            total += 1
            loc = f"{path}:{verdict.command.line_number}"
            if verdict.ok:
                lines.append(f"ok    {loc} [{verdict.verb}] {verdict.message}")
            else:
                failures += 1
                lines.append(
                    f"FAIL  {loc} [{verdict.verb or '?'}] {verdict.code}: "
                    f"{verdict.message}")
                lines.append(f"        command: {verdict.command.raw}")
    lines.append("")
    lines.append(
        f"summary: {total} presented supervisor command(s) checked; "
        f"{failures} failure(s)")
    return failures, lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--doc", action="append", default=None,
        help="a document to scan (repeatable); defaults to the living operator docs")
    args = ap.parse_args(argv)
    rels = args.doc if args.doc else list(DEFAULT_DOCS)
    doc_paths = [(_REPO_ROOT / rel) if not pathlib.Path(rel).is_absolute()
                 else pathlib.Path(rel) for rel in rels]
    failures, lines = check_docs(doc_paths)
    print("\n".join(lines))
    if failures:
        print(
            "\ncommand-document validation FAILED: a presented supervisor "
            "command drifted from the live parser/seam contract "
            "(D-024-R372; M0-T125 D1/D14/D15/D17).",
            file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Deterministic repository modularity checker (M0-T073, D-017-R110).

Enforces the permanent modularity policy (docs/CODE_MODULARITY_POLICY.md) over
HANDWRITTEN PRODUCTION source only. Line count is a review signal, never by
itself proof that architecture is bad - and a passing line count never excuses
responsibility mixing or excessive coupling; those are judged by the review
checklist against the actual diff, not by this tool.

What FAILS (--check, exit 1):
  * a NEW handwritten production file (absent from the reviewed baseline) above
    the HARD threshold without a valid exception;
  * a baseline (grandfathered) file that has grown MATERIALLY beyond its
    recorded size without a valid exception;
  * a malformed, expired, broadened (non-exact path), or incorrectly targeted
    exception - exceptions fail closed;
  * a baseline whose recorded digest does not match its own content (an edited
    baseline), or a baseline regeneration without a matching unexpired
    baseline-regeneration approval.

What is REPORTED but never fails:
  * files between the WARNING and HARD thresholds that are not yet baseline
    debt (review signal);
  * top-level symbol counts above the symbol ceiling (approximate for
    TypeScript; reliable for Python).

Determinism: selection comes from `git ls-files` (tracked files only), all
output is sorted, and expiry comparison uses --today when supplied (CI passes
the commit date; interactive runs default to the current UTC date, which is the
one intentional time input).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

WARN_SLOC = 600      # normally stay below this (policy s3)
JUSTIFY_SLOC = 750   # explicit cohesion justification required (policy s3)
HARD_SLOC = 1000     # mandatory architecture review; CI-enforced for new files
SYMBOL_CEILING = 40  # top-level symbols; report-only signal

GROWTH_ABSOLUTE = 50    # material growth = max(GROWTH_ABSOLUTE, 10%) over baseline
GROWTH_FRACTION = 0.10

#: Handwritten production roots -> extensions. Everything else is out of scope.
INCLUDE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("services/", (".py",)),
    ("tools/", (".py",)),
    ("packages/", (".py",)),
    ("apps/web/src/", (".ts", ".tsx")),
)

#: Any of these path segments excludes a file (generated, vendored, data-driven).
EXCLUDED_SEGMENTS = frozenset({
    "node_modules", ".next", "dist", "build", "coverage", "__pycache__",
    ".venv", "venv", "migrations", "fixtures", "generated", "vendor",
    "vendored", "_quarantine", "tests", "replay_corpus", "schemas", "prompts",
})

BASELINE_PATH = REPO_ROOT / "tools" / "modularity_baseline.json"
EXCEPTIONS_PATH = REPO_ROOT / "tools" / "modularity_exceptions.json"

PY_SYMBOL = re.compile(r"^(?:def |class |async def )\w+")
TS_SYMBOL = re.compile(
    r"^export\s+(?:default\s+)?(?:abstract\s+)?(?:async\s+)?"
    r"(?:function|class|const|let|var|interface|type|enum)\b")


class CheckError(Exception):
    """A fail-closed policy violation."""


def _is_test_file(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    return (name.startswith("test_") or name.endswith("_test.py")
            or ".test." in name or ".spec." in name)


def selected_files(repo: pathlib.Path) -> list[str]:
    """Tracked handwritten production files, sorted, POSIX-relative."""
    out = subprocess.run(["git", "ls-files"], cwd=str(repo), capture_output=True,
                         text=True, check=True)
    chosen: list[str] = []
    for line in out.stdout.splitlines():
        path = line.strip()
        if not path:
            continue
        segments = path.split("/")
        if any(seg in EXCLUDED_SEGMENTS for seg in segments):
            continue
        if _is_test_file(path):
            continue
        for prefix, extensions in INCLUDE_RULES:
            if path.startswith(prefix) and path.endswith(extensions):
                chosen.append(path)
                break
    return sorted(chosen)


def source_lines(path: pathlib.Path) -> int:
    """Non-blank, non-comment-only physical lines (policy s10 definition)."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise CheckError(f"unreadable selected file {path}: {exc}") from exc
    suffix = path.suffix
    count = 0
    in_block_comment = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if suffix in (".ts", ".tsx"):
            if in_block_comment:
                if "*/" in line:
                    in_block_comment = False
                continue
            if line.startswith("/*"):
                if "*/" not in line:
                    in_block_comment = True
                continue
            if line.startswith("//"):
                continue
        else:  # .py
            if line.startswith("#"):
                continue
        count += 1
    return count


def top_level_symbols(path: pathlib.Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = TS_SYMBOL if path.suffix in (".ts", ".tsx") else PY_SYMBOL
    return sum(1 for line in text.splitlines() if pattern.match(line))


def census(repo: pathlib.Path) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for rel in selected_files(repo):
        p = repo / rel
        result[rel] = {"sloc": source_lines(p), "symbols": top_level_symbols(p)}
    return result


def baseline_digest(entries: dict[str, int], version: int) -> str:
    canonical = json.dumps({"version": version,
                            "files": dict(sorted(entries.items()))},
                           sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_baseline(path: pathlib.Path) -> tuple[int, dict[str, int]]:
    """Load and integrity-check the reviewed baseline. Fail closed on tamper."""
    if not path.is_file():
        raise CheckError(f"baseline missing: {path} (the baseline is reviewed "
                         f"repository state; run --regenerate-baseline only with "
                         f"a recorded approval)")
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version")
    entries = data.get("files")
    recorded = data.get("baseline_digest")
    if not isinstance(version, int) or not isinstance(entries, dict):
        raise CheckError("baseline malformed: needs int `version` and object `files`")
    entries = {str(k): int(v) for k, v in entries.items()}
    if recorded != baseline_digest(entries, version):
        raise CheckError(
            "baseline_digest mismatch: tools/modularity_baseline.json was edited "
            "without regeneration approval; debt cannot be erased by editing the "
            "baseline (D-017-R110)")
    return version, entries


def load_exceptions(path: pathlib.Path, today: datetime.date,
                    known_files: set[str]) -> tuple[dict[str, dict], list[dict]]:
    """Validate exceptions; return (per-file exceptions, regeneration approvals).

    Every malformed, expired, broadened, or incorrectly targeted entry raises -
    exceptions fail closed rather than silently widening.
    """
    if not path.is_file():
        return {}, []
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = data.get("exceptions", [])
    if not isinstance(entries, list):
        raise CheckError("exceptions malformed: `exceptions` must be a list")
    per_file: dict[str, dict] = {}
    regenerations: list[dict] = []
    for i, e in enumerate(entries):
        where = f"exceptions[{i}]"
        for field in ("owner", "reason", "review_evidence", "expires"):
            if not isinstance(e.get(field), str) or not e.get(field).strip():
                raise CheckError(f"{where}: missing required field {field!r}")
        try:
            expires = datetime.date.fromisoformat(e["expires"])
        except ValueError as exc:
            raise CheckError(f"{where}: bad expires date {e['expires']!r}") from exc
        kind = e.get("kind", "file")
        if kind == "baseline-regeneration":
            if not isinstance(e.get("approval_id"), str) or not e["approval_id"].strip():
                raise CheckError(f"{where}: baseline-regeneration needs approval_id")
            # A consumed approval goes inert when it expires (it is only
            # load-bearing for --regenerate-baseline, which refuses it then);
            # it must not poison later --check runs.
            e = dict(e)
            e["_expired"] = expires < today
            regenerations.append(e)
            continue
        if expires < today:
            raise CheckError(f"{where}: EXPIRED on {expires.isoformat()} - remove or "
                             f"renew it through review; expired exceptions fail closed")
        if kind != "file":
            raise CheckError(f"{where}: unknown kind {kind!r}")
        target = e.get("path")
        if not isinstance(target, str) or not target:
            raise CheckError(f"{where}: file exception needs `path`")
        if any(ch in target for ch in "*?[]") or target.endswith("/"):
            raise CheckError(f"{where}: path {target!r} is broadened (glob or "
                             f"directory); exceptions must target exactly one file")
        if target not in known_files:
            raise CheckError(f"{where}: path {target!r} is not a selected handwritten "
                             f"production file - incorrectly targeted exceptions fail "
                             f"closed")
        if not isinstance(e.get("max_lines"), int) or e["max_lines"] <= 0:
            raise CheckError(f"{where}: file exception needs positive int max_lines")
        if target in per_file:
            raise CheckError(f"{where}: duplicate exception for {target!r}")
        per_file[target] = e
    return per_file, regenerations


def material_growth_limit(recorded: int) -> int:
    return recorded + max(GROWTH_ABSOLUTE, int(recorded * GROWTH_FRACTION))


def run_check(repo: pathlib.Path, today: datetime.date,
              baseline_path: pathlib.Path,
              exceptions_path: pathlib.Path) -> dict:
    counts = census(repo)
    _, baseline = load_baseline(baseline_path)
    per_file_exceptions, _ = load_exceptions(exceptions_path, today, set(counts))

    failures: list[dict] = []
    warnings: list[dict] = []

    for stale in sorted(set(baseline) - set(counts)):
        warnings.append({"kind": "baseline_entry_gone", "path": stale,
                         "note": "file deleted or no longer selected; drop the entry "
                                 "at the next approved regeneration"})

    for path in sorted(counts):
        sloc = counts[path]["sloc"]
        symbols = counts[path]["symbols"]
        exception = per_file_exceptions.get(path)
        if exception is not None and sloc > exception["max_lines"]:
            failures.append({
                "kind": "exception_exceeded", "path": path, "sloc": sloc,
                "limit": exception["max_lines"],
                "detail": f"grew past its reviewed exception ceiling "
                          f"({exception['max_lines']}); renew through review"})
            continue
        if path in baseline:
            limit = material_growth_limit(baseline[path])
            if sloc > limit and exception is None:
                failures.append({
                    "kind": "baseline_growth", "path": path, "sloc": sloc,
                    "recorded": baseline[path], "limit": limit,
                    "detail": "grandfathered oversized file grew materially "
                              "without a reviewed exception"})
        else:
            if sloc > HARD_SLOC and exception is None:
                failures.append({
                    "kind": "new_oversized", "path": path, "sloc": sloc,
                    "limit": HARD_SLOC,
                    "detail": "new handwritten production file above the hard "
                              "threshold without a reviewed exception"})
            elif sloc > WARN_SLOC:
                warnings.append({
                    "kind": "review_signal", "path": path, "sloc": sloc,
                    "note": ("above the justification threshold; record a cohesion "
                             "justification in review" if sloc > JUSTIFY_SLOC else
                             "above the warning threshold; consider the module "
                             "boundary before growing it further")})
        if symbols > SYMBOL_CEILING:
            approx = " (approximate count)" if path.endswith((".ts", ".tsx")) else ""
            warnings.append({"kind": "symbol_ceiling", "path": path,
                             "symbols": symbols,
                             "note": f"many top-level symbols{approx}; a signal, "
                                     f"not a verdict"})

    return {
        "command": "modularity-check",
        "today": today.isoformat(),
        "selected_files": len(counts),
        "thresholds": {"warn": WARN_SLOC, "justify": JUSTIFY_SLOC,
                       "hard": HARD_SLOC, "symbol_ceiling": SYMBOL_CEILING},
        "failures": failures,
        "warnings": warnings,
        "ok": not failures,
        "note": ("line count is a review signal, never by itself proof that "
                 "architecture is bad; a passing count never excuses "
                 "responsibility mixing or excessive coupling (policy s1)"),
    }


def regenerate_baseline(repo: pathlib.Path, today: datetime.date,
                        baseline_path: pathlib.Path,
                        exceptions_path: pathlib.Path,
                        approval_id: str) -> dict:
    """Regenerate the baseline - ONLY with a matching unexpired approval.

    Debt is never erased: an entry for a file that still exists and is still at
    or above the WARNING threshold is carried forward (count updated to the
    smaller of recorded and current - shrinking is progress, growing is not
    laundered in). Entries are dropped only for files that were deleted, are no
    longer selected, or now sit below the warning threshold.
    """
    counts = census(repo)
    _, regenerations = load_exceptions(exceptions_path, today, set(counts))
    approved = [r for r in regenerations
                if r.get("approval_id") == approval_id and not r.get("_expired")]
    if not approved:
        raise CheckError(
            f"no unexpired baseline-regeneration approval with approval_id "
            f"{approval_id!r} in {exceptions_path.name}; the baseline cannot be "
            f"casually regenerated (D-017-R110)")
    old_entries: dict[str, int] = {}
    if baseline_path.is_file():
        _, old_entries = load_baseline(baseline_path)
    entries: dict[str, int] = {}
    for path, data in counts.items():
        sloc = data["sloc"]
        if path in old_entries:
            if sloc >= WARN_SLOC:
                entries[path] = min(old_entries[path], sloc)
        elif sloc >= WARN_SLOC:
            entries[path] = sloc
    version = 1
    if baseline_path.is_file():
        version = json.loads(baseline_path.read_text(encoding="utf-8"))["version"] + 1
    doc = {
        "version": version,
        "generated_with_approval_id": approval_id,
        "thresholds": {"warn": WARN_SLOC, "justify": JUSTIFY_SLOC, "hard": HARD_SLOC},
        "files": dict(sorted(entries.items())),
        "baseline_digest": baseline_digest(entries, version),
        "note": ("reviewed legacy-debt register; entries persist while their file "
                 "remains at or above the warning threshold - regeneration never "
                 "erases live debt"),
    }
    baseline_path.write_text(json.dumps(doc, indent=1) + "\n",
                             encoding="utf-8", newline="\n")
    return {"command": "regenerate-baseline", "version": version,
            "entries": len(entries), "ok": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="fail-closed policy check (the CI mode)")
    parser.add_argument("--report", action="store_true",
                        help="census + warnings, never fails")
    parser.add_argument("--regenerate-baseline", action="store_true")
    parser.add_argument("--approval-id", default=None,
                        help="approval_id of the baseline-regeneration exception")
    parser.add_argument("--repo", default=str(REPO_ROOT))
    parser.add_argument("--baseline", default=str(BASELINE_PATH))
    parser.add_argument("--exceptions", default=str(EXCEPTIONS_PATH))
    parser.add_argument("--today", default=None,
                        help="ISO date for expiry checks (default: current UTC date)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo = pathlib.Path(args.repo).resolve()
    today = (datetime.date.fromisoformat(args.today) if args.today
             else datetime.datetime.now(datetime.timezone.utc).date())
    try:
        if args.regenerate_baseline:
            if not args.approval_id:
                raise CheckError("--regenerate-baseline requires --approval-id")
            payload = regenerate_baseline(repo, today, pathlib.Path(args.baseline),
                                          pathlib.Path(args.exceptions),
                                          args.approval_id)
        elif args.check or args.report:
            payload = run_check(repo, today, pathlib.Path(args.baseline),
                                pathlib.Path(args.exceptions))
            if args.report:
                payload["ok"] = True  # report mode never fails on findings
        else:
            parser.error("choose one of --check, --report, --regenerate-baseline")
    except CheckError as exc:
        message = {"command": "modularity-check", "ok": False,
                   "error": str(exc)}
        print(json.dumps(message, indent=1) if args.json else f"FAIL: {exc}",
              file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=1))
    else:
        print(f"selected {payload.get('selected_files', payload.get('entries'))} files; "
              f"failures {len(payload.get('failures', []))}; "
              f"warnings {len(payload.get('warnings', []))}")
        for f in payload.get("failures", []):
            print(f"  FAIL {f['kind']}: {f['path']} ({f.get('sloc')}) - {f['detail']}")
        for w in payload.get("warnings", [])[:20]:
            print(f"  warn {w['kind']}: {w.get('path')} - {w['note']}")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())

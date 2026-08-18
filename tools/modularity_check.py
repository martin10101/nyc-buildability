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
output is sorted, and expiry comparison uses --today when supplied (tests pin
it; CI and interactive runs default to the current UTC date - the one
intentional time input, so an expired exception turns a rerun red on purpose).
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
EXCEPTION_HORIZON_DAYS = 90  # exceptions are temporary; never standing waivers

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
    try:
        out = subprocess.run(["git", "ls-files"], cwd=str(repo),
                             capture_output=True, text=True, check=True)
    except (subprocess.CalledProcessError, OSError) as exc:
        raise CheckError(f"git ls-files failed in {repo}: {exc}") from exc
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


def _ts_line_has_code(line: str, in_block: bool,
                      in_template: bool = False) -> tuple[bool, bool, bool]:
    """Quote- and comment-aware: does non-comment code remain on this line?

    A char scanner that tracks three cross-line-relevant states so a comment
    marker inside a string literal is never mistaken for a real comment
    (G3-R1 / G4-D1): block-comment spans (`/* */`, multi-line), template-literal
    spans (backtick, multi-line), and single-line '' / "" strings (reset each
    line). `//` and `/*` inside any string are ignored; `*/` inside a string
    does not close a block. Returns (has_code, in_block, in_template).
    Remaining bound (documented, policy s10): a raw `${...}` nesting a backtick
    is not tracked, and escaped quotes inside single-line strings are handled
    but exotic nesting is not - both conspicuous in review.
    """
    remainder: list[str] = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if in_block:
            end = line.find("*/", i)
            if end == -1:
                return bool("".join(remainder).strip()), True, in_template
            i = end + 2
            in_block = False
            continue
        if in_template:
            end = line.find("`", i)
            if end == -1:
                # whole line is template-literal body: non-blank string content
                return True, False, True
            remainder.append("t")  # template body counts as code content
            i = end + 1
            in_template = False
            continue
        two = line[i:i + 2]
        if two == "//":
            break  # rest of line is a comment
        if two == "/*":
            i += 2
            in_block = True
            continue
        if ch == "`":
            remainder.append("t")
            i += 1
            in_template = True
            continue
        if ch in ("'", '"'):
            remainder.append("s")  # a string literal is code content
            i += 1
            while i < n:
                if line[i] == "\\":
                    i += 2
                    continue
                if line[i] == ch:
                    i += 1
                    break
                i += 1
            continue
        remainder.append(ch)
        i += 1
    return bool("".join(remainder).strip()), in_block, in_template


def source_lines(path: pathlib.Path) -> tuple[int, bool]:
    """Non-blank, non-comment-only physical lines (policy s10 definition).

    Returns (sloc, scan_uncertain). scan_uncertain is True for a TS/TSX file
    whose scan ends inside an open block comment - almost always a `/*` inside a
    string literal (e.g. `import.meta.glob('./x/*.ts')`), which the span scanner
    cannot distinguish from a real comment and which would zero out the tail of
    the file. It is surfaced as a warning so an undercount cannot hide silently
    (G3-R1).
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise CheckError(f"unreadable selected file {path}: {exc}") from exc
    suffix = path.suffix
    count = 0
    in_block_comment = False
    in_template = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if suffix in (".ts", ".tsx"):
            has_code, in_block_comment, in_template = _ts_line_has_code(
                line, in_block_comment, in_template)
            if not has_code:
                continue
        else:  # .py: comment-only lines; `#` inside docstrings/strings is a
            # documented heuristic bound (policy s10)
            if line.startswith("#"):
                continue
        count += 1
    # A scan ending inside an open block comment is genuinely ambiguous; an open
    # template literal at EOF is a syntax error in real code, so treat it the
    # same - surface uncertainty rather than trust a possibly-truncated count.
    return count, (suffix in (".ts", ".tsx") and (in_block_comment or in_template))


def top_level_symbols(path: pathlib.Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    pattern = TS_SYMBOL if path.suffix in (".ts", ".tsx") else PY_SYMBOL
    return sum(1 for line in text.splitlines() if pattern.match(line))


def census(repo: pathlib.Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for rel in selected_files(repo):
        p = repo / rel
        sloc, uncertain = source_lines(p)
        result[rel] = {"sloc": sloc, "symbols": top_level_symbols(p),
                       "scan_uncertain": uncertain}
    return result


def baseline_digest(entries: dict[str, int], version: int,
                    approval_id: str = "") -> str:
    canonical = json.dumps({"version": version,
                            "approval_id": approval_id,
                            "files": dict(sorted(entries.items()))},
                           sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_baseline(path: pathlib.Path) -> tuple[int, dict[str, int]]:
    """Load and integrity-check the reviewed baseline. Fail closed on drift."""
    if not path.is_file():
        raise CheckError(f"baseline missing: {path} (the baseline is reviewed "
                         f"repository state; run --regenerate-baseline only with "
                         f"a recorded approval)")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckError(f"baseline unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise CheckError("baseline malformed: top level must be an object")
    version = data.get("version")
    entries = data.get("files")
    recorded = data.get("baseline_digest")
    approval_id = str(data.get("generated_with_approval_id", ""))
    if not isinstance(version, int) or not isinstance(entries, dict):
        raise CheckError("baseline malformed: needs int `version` and object `files`")
    entries = {str(k): int(v) for k, v in entries.items()}
    if recorded != baseline_digest(entries, version, approval_id):
        # A self-consistency check over version+approval+entries: it catches
        # accidental or unrecomputed edits and forces any deliberate change
        # through a visible diff carrying a recomputed digest - where review,
        # not cryptography, is the actual authenticity control (G5 SEC-MINOR-1).
        raise CheckError(
            "baseline_digest mismatch: tools/modularity_baseline.json was edited "
            "outside the approved regeneration path; recompute via "
            "--regenerate-baseline with a reviewed approval (D-017-R110)")
    return version, entries


def load_exceptions(path: pathlib.Path, today: datetime.date,
                    known_files: set[str]) -> tuple[dict[str, dict], list[dict]]:
    """Validate exceptions; return (per-file exceptions, regeneration approvals).

    Every malformed, expired, broadened, or incorrectly targeted entry raises -
    exceptions fail closed rather than silently widening.
    """
    if not path.is_file():
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckError(f"exceptions unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise CheckError("exceptions malformed: top level must be an object")
    entries = data.get("exceptions", [])
    if not isinstance(entries, list):
        raise CheckError("exceptions malformed: `exceptions` must be a list")
    per_file: dict[str, dict] = {}
    regenerations: list[dict] = []
    for i, e in enumerate(entries):
        where = f"exceptions[{i}]"
        if not isinstance(e, dict):
            raise CheckError(f"{where}: entry must be an object")
        for field in ("owner", "reason", "review_evidence", "expires"):
            if not isinstance(e.get(field), str) or not e.get(field).strip():
                raise CheckError(f"{where}: missing required field {field!r}")
        try:
            expires = datetime.date.fromisoformat(e["expires"])
        except ValueError as exc:
            raise CheckError(f"{where}: bad expires date {e['expires']!r}") from exc
        if expires > today + datetime.timedelta(days=EXCEPTION_HORIZON_DAYS):
            raise CheckError(
                f"{where}: expires {expires.isoformat()} exceeds the "
                f"{EXCEPTION_HORIZON_DAYS}-day temporary horizon; exceptions are "
                f"temporary by policy s8, never standing waivers")
        kind = e.get("kind", "file")
        if kind == "baseline-regeneration":
            if not isinstance(e.get("approval_id"), str) or not e["approval_id"].strip():
                raise CheckError(f"{where}: baseline-regeneration needs approval_id")
            if not isinstance(e.get("for_version"), int) or e["for_version"] <= 0:
                raise CheckError(f"{where}: baseline-regeneration needs int "
                                 f"for_version - each approval is single-use, "
                                 f"bound to the one baseline version it produces")
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
        if "baseline_sloc" in e and (not isinstance(e["baseline_sloc"], int)
                                     or e["baseline_sloc"] <= 0):
            raise CheckError(f"{where}: baseline_sloc, when present, must be a "
                             f"positive int (the file's SLOC at review time)")
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
        if counts[path].get("scan_uncertain"):
            warnings.append({
                "kind": "sloc_scan_uncertain", "path": path,
                "note": "the SLOC scan ended inside an open block comment "
                        "(likely a /* inside a string literal); this file's count "
                        "may be undercounted - inspect it (G3-R1)"})
        if symbols > SYMBOL_CEILING:
            # Report-only signal, emitted BEFORE any failure short-circuit so an
            # already-failing file keeps its signal (G3-F11).
            approx = " (approximate count)" if path.endswith((".ts", ".tsx")) else ""
            warnings.append({"kind": "symbol_ceiling", "path": path,
                             "symbols": symbols,
                             "note": f"many top-level symbols{approx}; a signal, "
                                     f"not a verdict"})
        if exception is not None:
            # G5 SEC-MINOR-4 / G3-R2 / G4-D2: an exception permits at most one
            # growth step above the size recorded WHEN IT WAS REVIEWED
            # (exception.baseline_sloc, default current). A ceiling above that is
            # over-broad and FAILS. But if the FILE has since shrunk comfortably
            # below its own ceiling, the exception is merely STALE (the file is
            # small - benign); that is a warning, and a hard failure is reserved
            # for a ceiling that outruns the review size while the file is still
            # near it.
            reviewed_sloc = exception.get("baseline_sloc", sloc)
            over_broad = exception["max_lines"] > material_growth_limit(reviewed_sloc)
            shrunk_clear = sloc <= material_growth_limit(WARN_SLOC)
            if over_broad and shrunk_clear:
                warnings.append({
                    "kind": "stale_exception", "path": path, "sloc": sloc,
                    "note": f"file is {sloc} SLOC, well under its exception ceiling "
                            f"({exception['max_lines']}) - the exception is stale; "
                            f"DELETE it (the refactor policy s6 asked for succeeded)"})
            elif over_broad:
                failures.append({
                    "kind": "exception_too_broad", "path": path, "sloc": sloc,
                    "limit": material_growth_limit(reviewed_sloc),
                    "detail": f"the reviewed ceiling ({exception['max_lines']}) "
                              f"exceeds one growth step above the recorded review size "
                              f"({reviewed_sloc}); narrow it, or if the file was "
                              f"refactored below threshold, DELETE the exception "
                              f"(G5 SEC-MINOR-4)"})
                continue
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
    version = 1
    old_entries: dict[str, int] = {}
    if baseline_path.is_file():
        prior_version, old_entries = load_baseline(baseline_path)  # G3-R3: guarded read
        version = prior_version + 1
    approved = [r for r in regenerations
                if r.get("approval_id") == approval_id and not r.get("_expired")
                and r.get("for_version") == version]
    if not approved:
        raise CheckError(
            f"no unexpired baseline-regeneration approval with approval_id "
            f"{approval_id!r} bound to version {version} in {exceptions_path.name}; "
            f"an approval is bound to the one version it produces (while the "
            f"predecessor baseline exists) - the baseline cannot be casually "
            f"regenerated (D-017-R110, G5 SEC-MINOR-2). Deleting the baseline to "
            f"reset the counter is a conspicuous whole-file diff that review "
            f"catches (G4-D3, policy s7)")
    entries: dict[str, int] = {}
    for path, data in counts.items():
        sloc = data["sloc"]
        if path in old_entries:
            if sloc >= WARN_SLOC:
                entries[path] = min(old_entries[path], sloc)
        elif sloc >= WARN_SLOC:
            entries[path] = sloc
    doc = {
        "version": version,
        "generated_with_approval_id": approval_id,
        "thresholds": {"warn": WARN_SLOC, "justify": JUSTIFY_SLOC, "hard": HARD_SLOC},
        "files": dict(sorted(entries.items())),
        "baseline_digest": baseline_digest(entries, version, approval_id),
        "note": ("reviewed legacy-debt register; entries persist while their file "
                 "remains at or above the warning threshold - regeneration never "
                 "erases live debt (a currently-failing NEW file absorbed here is "
                 "the reviewed absorption path, visible in this file's diff)"),
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

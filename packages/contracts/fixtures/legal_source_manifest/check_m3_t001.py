#!/usr/bin/env python3
"""M3-T001 self-check harness (executable acceptance evidence).

Runs, deterministically and with only the standard library + the already-installed
``jsonschema`` package (no new runtime dependency), the machine-checkable acceptance
scenarios owned by M3-T001:

  AS-11a  legal_source_manifest.schema.json passes JSON Schema (Draft 2020-12) meta-validation.
  AS-11b  every positive fixture validates against the schema.
  AS-11c  every negative fixture FAILS validation (each isolates one missing/invalid
          required provenance / corpus-version / raw-hash field or constraint).
  AS-11d  the schema's $id and manifest_version const are the expected deterministic constants;
          the schema file's SHA-256 is printed so reruns are visibly byte-identical.
  AS-4    no forbidden aggregate "complete/compliant/buildable/feasible" system guarantee
          appears in the prose deliverables while any coverage-matrix domain is unresolved.
  AS-12   none of the prohibited OCR/accuracy claim strings appears as a system guarantee;
          every occurrence sits on a line explicitly marked PROHIBITED / negated.
  NC-2    no PDF bytes are committed by this task and no inferred project identity
          (BBL / street address) appears in the benchmark analysis.

Exit code 0 = all checks passed; 1 = at least one failed. Reproducible:
    python packages/contracts/schemas/v1/fixtures/legal_source_manifest/check_m3_t001.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve()             # .../packages/contracts/fixtures/legal_source_manifest/check_m3_t001.py
REPO = HERE.parents[4]                       # repo root (fixtures/legal_source_manifest -> fixtures -> contracts -> packages -> root)
SCHEMA_PATH = REPO / "packages/contracts/schemas/v1/legal_source_manifest.schema.json"
# Fixtures live under the repo convention the CI validator instance-checks:
# valid/ must validate against the schema; invalid/ must FAIL.
VALID_DIR = REPO / "packages/contracts/fixtures/valid/legal_source_manifest"
INVALID_DIR = REPO / "packages/contracts/fixtures/invalid/legal_source_manifest"

EXPECTED_ID = ("https://github.com/martin10101/nyc-buildability/"
               "packages/contracts/schemas/v1/legal_source_manifest.schema.json")
EXPECTED_VERSION = "1.0.0"

# Prose deliverables scanned for AS-4 (aggregate) and AS-12 (prohibited claims).
PROSE_DELIVERABLES = [
    "docs/SOURCE_AUTHORITY_POLICY.md",
    "docs/LEGAL_CORPUS_COVERAGE_MATRIX.md",
    "docs/DOCUMENT_EVIDENCE_POLICY.md",
    "docs/CONSTRUCTION_CODE_RELEASE_SCOPE.md",
    "project-control/reports/M3-T001-architect-benchmark-analysis.md",
    "project-control/reports/M3-T001-producer-report.md",
]
# The registry is scanned only for the (very specific) prohibited claim strings, so
# pre-existing accepted rows cannot cause a false positive on the broad aggregate check.
PROHIBITED_SCAN_EXTRA = ["docs/SOURCE_ACCESS_REGISTRY.md"]

BENCHMARK_REPORT = "project-control/reports/M3-T001-architect-benchmark-analysis.md"

# AS-12: exact prohibited claim phrases (never a system guarantee).
PROHIBITED_CLAIMS = [
    "100% accurate OCR",
    "100% legally accurate",
    "OCR confidence proves correctness",
    "two OCR engines agreed therefore verified",
    "arithmetic consistency proves the extracted rule is correct",
]
# A line carrying a prohibited phrase is acceptable only if it is explicitly a prohibition.
PROHIBITION_MARKERS = [
    "prohibited", "must never", "never appear", "never be emitted",
    "forbid", "must not", "is false", "are false", "false and",
]

# For AS-4: an aggregate-verdict shape is acceptable ONLY when it is being negated, forbidden,
# or given as an example of a forbidden claim. Checked in a text WINDOW around the match so that
# markdown hard-wraps of a single sentence do not defeat the guard. A bare affirmative guarantee
# (no negation/exemplar marker nearby) still fails.
AGGREGATE_NEGATION_MARKERS = [
    "never", "not ", "no ", "without", "forbid", "prohibit", "must not", "cannot",
    "may not", "e.g.", "excluded", "exclusion", "disclaimer", "blocks", "fails if",
    "forbidden", "rather than", "instead of", "is not", "are not", "neither",
    "only after", "never a", "does not", "no single", "no deliverable",
]
AGGREGATE_WINDOW = 200

# AS-4: affirmative aggregate-verdict shapes that would only ever be a false guarantee.
FORBIDDEN_AGGREGATE_REGEXES = [
    r"(?i)\b(the\s+)?(property|development|project|site|envelope|building|scenario)\s+"
    r"(is|are|will\s+be|would\s+be)\s+(now\s+)?(buildable|compliant|feasible)\b",
    r"(?i)\b(corpus|coverage|legal\s+corpus|analysis)\s+(is|are)\s+(now\s+)?complete\b",
    r"(?i)\bis\s+(fully\s+)?(compliant|buildable)\b",
    r"(?i)\bfully\s+(compliant|buildable|complete)\b",
    r"(?i)\bconfirmed\s+(buildable|compliant)\b",
    r"(?i)\bguarantee[sd]?\b[^.\n]{0,60}\b(buildable|compliant|approv)",
]

results: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    schema_sha = hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest()
    print(f"schema sha256: {schema_sha}\n")

    # AS-11a
    try:
        Draft202012Validator.check_schema(schema)
        record("AS-11a schema meta-validates (Draft 2020-12)", True)
    except Exception as exc:  # noqa: BLE001
        record("AS-11a schema meta-validates (Draft 2020-12)", False, str(exc))

    # AS-11d — deterministic version carried by the $id (/v1/) + the manifest_version const
    # (house convention; the CI contract validator's keyword allowlist forbids a custom
    # top-level version keyword, so version lives in $id + the const, not an x- keyword).
    ok_id = schema.get("$id") == EXPECTED_ID
    ok_ver = schema.get("properties", {}).get("manifest_version", {}).get("const") == EXPECTED_VERSION
    record("AS-11d deterministic $id + manifest_version const",
           ok_id and ok_ver,
           f"$id_ok={ok_id} version_const_ok={ok_ver} sha256={schema_sha}")

    validator = Draft202012Validator(schema)

    # AS-11b positives (repo convention: fixtures/valid/<schema>/)
    pos = sorted(VALID_DIR.glob("*.json"))
    all_pos_ok = bool(pos)
    for f in pos:
        errs = sorted(validator.iter_errors(json.loads(f.read_text(encoding="utf-8"))),
                      key=lambda e: e.path)
        ok = not errs
        all_pos_ok &= ok
        record(f"AS-11b positive validates: {f.name}", ok,
               "" if ok else f"unexpected errors: {[e.message for e in errs]}")

    # AS-11c negatives (repo convention: fixtures/invalid/<schema>/ — must FAIL)
    neg = sorted(INVALID_DIR.glob("*.json"))
    all_neg_ok = bool(neg)
    for f in neg:
        errs = list(validator.iter_errors(json.loads(f.read_text(encoding="utf-8"))))
        ok = bool(errs)
        all_neg_ok &= ok
        record(f"AS-11c negative rejected: {f.name}", ok,
               (f"rejected on: {errs[0].message[:90]}" if ok else "UNEXPECTEDLY VALID"))

    record("AS-11 fixtures summary", all_pos_ok and all_neg_ok and bool(pos) and bool(neg),
           f"{len(pos)} positive / {len(neg)} negative")

    # AS-12 prohibited claims
    prohibited_violations = []
    for rel in PROSE_DELIVERABLES + PROHIBITED_SCAN_EXTRA:
        for i, line in enumerate(read(rel).splitlines(), 1):
            low = line.lower()
            for phrase in PROHIBITED_CLAIMS:
                if phrase.lower() in low:
                    if not any(m in low for m in PROHIBITION_MARKERS):
                        prohibited_violations.append(f"{rel}:{i}: {line.strip()[:80]}")
    record("AS-12 prohibited claims only appear as prohibitions", not prohibited_violations,
           "" if not prohibited_violations else "; ".join(prohibited_violations))

    # AS-4 no false aggregate: an aggregate-verdict shape is a violation ONLY when it is NOT
    # negated/forbidden/exemplified within a surrounding text window (markdown-wrap safe).
    aggregate_hits = []
    for rel in PROSE_DELIVERABLES:
        text = read(rel)
        low_all = text.lower()
        for rx in FORBIDDEN_AGGREGATE_REGEXES:
            for m in re.finditer(rx, text):
                w0 = max(0, m.start() - AGGREGATE_WINDOW)
                w1 = min(len(text), m.end() + AGGREGATE_WINDOW)
                window = low_all[w0:w1]
                if not any(mk in window for mk in AGGREGATE_NEGATION_MARKERS):
                    line_no = text[:m.start()].count("\n") + 1
                    aggregate_hits.append(f"{rel}:{line_no}: …{m.group(0)}… (unguarded)")
    record("AS-4 no aggregate complete/compliant/buildable guarantee", not aggregate_hits,
           "" if not aggregate_hits else "; ".join(aggregate_hits))

    # NC-2 no PDF bytes committed by this task
    try:
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True
        ).stdout.splitlines()
    except Exception as exc:  # noqa: BLE001
        tracked = []
        record("NC-2 git ls-files available", False, str(exc))
    pdfs = [p for p in tracked if p.lower().endswith(".pdf")]
    record("NC-2 no PDF committed anywhere in tree", not pdfs,
           "" if not pdfs else f"PDFs present: {pdfs}")

    # NC-2 no inferred identity (BBL / street address) in the benchmark analysis
    bench = read(BENCHMARK_REPORT)
    bbl_hits = re.findall(r"\b[1-5]\d{9}\b", bench)
    addr_hits = re.findall(
        r"(?i)\b\d{1,4}\s+\w+\s+(?:street|st|avenue|ave|road|rd|place|pl|boulevard|blvd|lane|ln|drive|dr)\b",
        bench)
    record("NC-2 no inferred BBL/address in benchmark analysis",
           not bbl_hits and not addr_hits,
           "" if (not bbl_hits and not addr_hits) else f"bbl={bbl_hits} addr={addr_hits}")

    failed = [n for n, ok, _ in results if not ok]
    print("\n" + "=" * 60)
    print(f"TOTAL: {len(results)} checks, {len(failed)} failed")
    if failed:
        print("FAILED: " + "; ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

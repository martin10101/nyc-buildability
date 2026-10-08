# M0-T188 look-back: accepted and in-flight tasks whose allowed_paths carry a glob/pattern entry

Backlog DB-181; owner directive D-090-R557; serves D-001-R146 / D-001-R110.
Read-only look-back run at the M0-T188 claim-seam head
`b416cf0d154400ebf1dcaaabc199da4f4e25bc40`. **This report rewrites no task, gate,
verification or directive record** (every `project-control/tasks/**`, `gates/**` and
`directives/**` path is in M0-T188's `forbidden_paths`). It is the evidence that produced the
frozen `PATTERN_ALLOWED_PATHS_GRANDFATHERED` allowlist in `tools/directive_registry.py`.

## Counts

- TOTAL pattern-carrying tasks: **88**
- ACCEPTED: **77**
- IN-FLIGHT (not accepted): **11** — 1 `awaiting_gate` carrying no pattern test aside (M0-T021),
  5 `awaiting_gate` (M4-T001, M4-T002, M4-T004, M4-T005, M4-T006, M5-T001 — see list), 4 `backlog`
  (M3-T002..M3-T005). (Exact per-task statuses are in the output below.)

A **pattern** entry contains `*` or `?`, or begins with `:` (pathspec magic). A literal path —
including one that does not yet exist, and the one tracked Next.js bracket route
`apps/web/src/app/survey/review/[documentId]/page.tsx` — is NOT a pattern.

## What this means for the recorded identities (plain statement)

Under `GIT_LITERAL_PATHSPECS=1` every `allowed_paths` entry is matched literally, so each pattern
entry above resolved to **0 tracked files** (column `-> resolves 0 tracked files`). Therefore the
frozen content-identity hash that submission, the gates and acceptance compared for these tasks
**did not bind the files the pattern entries declared**; it covered only whatever *literal*
entries bound. For the tasks marked `other-literal-entries-bind-files=False` — **M1-T001**
(accepted) and the in-flight **M3-T002, M3-T003, M3-T004, M3-T005, M4-T006** — no literal entry
bound a tracked file either, so the identity bound only a literal report placeholder where one was
listed (the insidious patterns-plus-literal-report case), or nothing (the empty-identity guard,
added later in M0-T057, catches the nothing case for tasks that pass through it now).

This is a statement about the **content-identity hash only**. It does not assert the underlying
work was unreviewed: per DB-181 itself, waves 4 and 5 compared those files' blobs with a
pattern-aware acceptance check of their own and the pre-merge checks compared them with `git diff`,
so those merges were covered by other means; earlier tasks were not examined. M0-T188 does not
re-open, re-accept, re-validate or rewrite any of these records (forbidden); it only prevents NEW
packets from repeating the defect and freezes these 88 ids as grandfathered so
`validate_directive_compliance.py --check` stays exit 0.

## The look-back script (verbatim)

The `ROOT` constant is set to the checkout being measured; otherwise the script is run from the
repository root. It uses the same literal-pathspec git mechanics as the registry's identity path.

```python
#!/usr/bin/env python3
"""M0-T188 look-back (read-only): every task whose allowed_paths carry a glob/pattern entry.
Run from the repository root at the claim-seam head. A PATTERN entry contains '*' or '?' or
begins with ':' (pathspec magic); a literal bracket path is NOT a pattern. For each task it
records id, status, the pattern entries (with how many tracked files each resolves to under
GIT_LITERAL_PATHSPECS=1), and whether any NON-pattern entry binds at least one tracked file."""
import json
import subprocess
from pathlib import Path

ROOT = Path("<repository root / worktree root>")
TASKS = ROOT / "project-control" / "tasks"


def is_pattern(entry) -> bool:
    if not isinstance(entry, str):
        return True
    s = entry.strip()
    if not s:
        return False
    return s.startswith(":") or "*" in s or "?" in s


def resolve_count(path: str) -> int:
    pp = str(path).strip().rstrip("/")
    if not pp:
        return 0
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-tree", "-r", "-z", "--full-tree", "HEAD", "--", pp],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={"GIT_LITERAL_PATHSPECS": "1", "PATH": "/usr/bin:/bin"})
    return len([r for r in out.stdout.split(b"\x00") if r])


rows = []
for p in sorted(TASKS.glob("*.json")):
    try:
        t = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        continue
    ap = list(t.get("allowed_paths") or [])
    pats = [e for e in ap if is_pattern(e)]
    if not pats:
        continue
    literal_bound = any(resolve_count(e) > 0 for e in ap if not is_pattern(e))
    rows.append((t.get("task_id") or p.stem, t.get("status"), pats, literal_bound))

accepted = sorted(r for r in rows if r[1] == "accepted")
inflight = sorted(r for r in rows if r[1] != "accepted")
print(f"TOTAL pattern-carrying tasks: {len(rows)}")
print(f"ACCEPTED: {len(accepted)}    IN-FLIGHT: {len(inflight)}")
for label, group in (("ACCEPTED", accepted), ("IN-FLIGHT", inflight)):
    print(f"\n=== {label} ({len(group)}) ===")
    for tid, status, pats, lb in group:
        print(f"{tid} [{status}] other-literal-entries-bind-files={lb}")
        for e in pats:
            print(f"    {e}  -> resolves {resolve_count(e)} tracked files")
print("\nFROZEN ID LIST (accepted + in-flight), sorted:")
print(sorted(r[0] for r in rows))
```

## The script's output (verbatim, at the claim-seam head)

```text
TOTAL pattern-carrying tasks: 88
ACCEPTED: 77    IN-FLIGHT: 11

=== ACCEPTED (77) ===
M0-T004 [accepted] other-literal-entries-bind-files=True
    apps/**  -> resolves 0 tracked files
    services/**  -> resolves 0 tracked files
    packages/**  -> resolves 0 tracked files
    .github/**  -> resolves 0 tracked files
    project-control/reports/M0-T004-*  -> resolves 0 tracked files
M0-T005 [accepted] other-literal-entries-bind-files=True
    project-control/reports/M0-T005-*  -> resolves 0 tracked files
M0-T005-R1 [accepted] other-literal-entries-bind-files=True
    project-control/reports/M0-T005-R1-*  -> resolves 0 tracked files
M0-T006 [accepted] other-literal-entries-bind-files=True
    docs/adr/**  -> resolves 0 tracked files
    project-control/reports/M0-T006-*  -> resolves 0 tracked files
M0-T009 [accepted] other-literal-entries-bind-files=True
    packages/contracts/**  -> resolves 0 tracked files
    project-control/reports/M0-T009-*  -> resolves 0 tracked files
M0-T010 [accepted] other-literal-entries-bind-files=True
    project-control/reports/M0-T010-*  -> resolves 0 tracked files
M0-T011 [accepted] other-literal-entries-bind-files=True
    docs/adr/**  -> resolves 0 tracked files
    project-control/reports/M0-T011-*  -> resolves 0 tracked files
M0-T015 [accepted] other-literal-entries-bind-files=True
    services/api/tests/** (new middleware tests only)  -> resolves 0 tracked files
M0-T018 [accepted] other-literal-entries-bind-files=True
    services/api/requirements.txt (and any generated services/api/requirements*.lock / requirements-prod.txt the chosen lock format needs)  -> resolves 0 tracked files
    .github/workflows/** (new exact-production-install job + scheduled audit workflow; existing jobs stay green)  -> resolves 0 tracked files
    services/api/scripts/** (lock-generation / audit helper scripts if needed)  -> resolves 0 tracked files
M0-T019 [accepted] other-literal-entries-bind-files=True
    .github/workflows/** (npm tooling pin, blocking audit step, scheduled audit; existing jobs stay green)  -> resolves 0 tracked files
    apps/web/scripts/tests/** - the age-gate's deterministic positive / boundary (604800 pass, 604799 fail) / fail-closed unit tests  -> resolves 0 tracked files
M0-T020 [accepted] other-literal-entries-bind-files=True
    services/api/pyproject.toml - STRICTLY LIMITED to the [project.optional-dependencies].dev pytest specifier ('pytest>=8,<9' -> 'pytest>=9.0.3,<10') plus an adjacent explanatory comment if useful; NO other dependency, version cap, or [tool.*] configuration may change (owner bounded amendment 2026-07-20).  -> resolves 0 tracked files
    services/api/scripts/** (lock_requirements.sh update; the ONE documented tooling-lock generation script; the dependency-policy release-age checker and its deterministic tests)  -> resolves 0 tracked files
    .gitignore (the repository ignore rule covering services/api/**/*.egg-info/)  -> resolves 0 tracked files
M0-T022 [accepted] other-literal-entries-bind-files=True
    apps/web/src/app/dashboard/**  -> resolves 0 tracked files
    apps/web/src/lib/dashboard/**  -> resolves 0 tracked files
    apps/web/src/components/dashboard/**  -> resolves 0 tracked files
    apps/web/src/test-support/dashboard/**  -> resolves 0 tracked files
    apps/web/e2e/fixtures/control-plane/**  -> resolves 0 tracked files
M0-T036 [accepted] other-literal-entries-bind-files=True
    tools/agent_supervisor/** (create; per D-007 Section 6 layout, adjusted to repository conventions)  -> resolves 0 tracked files
    tools/test_agent_supervisor_*.py (create)  -> resolves 0 tracked files
M0-T041 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T042 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T044 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T045 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T046 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T048 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T049 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T050 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T051 [accepted] other-literal-entries-bind-files=True
    tools/test_agent_supervisor_*.py  -> resolves 0 tracked files
M0-T181 [accepted] other-literal-entries-bind-files=True
    project-control/reports/M0-T181-ci-evidence/**  -> resolves 0 tracked files
M0-T184 [accepted] other-literal-entries-bind-files=True
    project-control/reports/M0-T184-ci-evidence/**  -> resolves 0 tracked files
M0-T186 [accepted] other-literal-entries-bind-files=True
    project-control/reports/M0-T186-ci-evidence/**  -> resolves 0 tracked files
M1-T001 [accepted] other-literal-entries-bind-files=False
    docs/research/pluto-mappluto-*  -> resolves 0 tracked files
    docs/research/source-registry-drafts/pluto-mappluto*  -> resolves 0 tracked files
    project-control/reports/M1-T001-*  -> resolves 0 tracked files
M1-T002 [accepted] other-literal-entries-bind-files=True
    services/api/app/connectors/**  -> resolves 0 tracked files
    services/api/tests/connectors/**  -> resolves 0 tracked files
    services/api/tests/fixtures/pluto/**  -> resolves 0 tracked files
    project-control/reports/M1-T002-*  -> resolves 0 tracked files
M1-T003 [accepted] other-literal-entries-bind-files=True
    docs/research/zoning-features-ztldb-*  -> resolves 0 tracked files
    project-control/reports/M1-T003-*  -> resolves 0 tracked files
M1-T004 [accepted] other-literal-entries-bind-files=True
    docs/research/zoning-resolution-*  -> resolves 0 tracked files
    project-control/reports/M1-T004-*  -> resolves 0 tracked files
M1-T005 [accepted] other-literal-entries-bind-files=True
    services/api/app/api/**  -> resolves 0 tracked files
    services/api/app/profile/**  -> resolves 0 tracked files
    services/api/tests/**  -> resolves 0 tracked files
    project-control/reports/M1-T005-*  -> resolves 0 tracked files
M1-T006 [accepted] other-literal-entries-bind-files=True
    packages/contracts/**  -> resolves 0 tracked files
    .github/scripts/tests/**  -> resolves 0 tracked files
M1-T007 [accepted] other-literal-entries-bind-files=True
    docs/research/fixtures/m1-t007/**  -> resolves 0 tracked files
M1-T008 [accepted] other-literal-entries-bind-files=True
    services/api/tests/fixtures/** (KB-scale representative fixtures only, if needed)  -> resolves 0 tracked files
M1-T009 [accepted] other-literal-entries-bind-files=True
    services/api/**  -> resolves 0 tracked files
M2-T001 [accepted] other-literal-entries-bind-files=True
    apps/web/**  -> resolves 0 tracked files
M2-T002 [accepted] other-literal-entries-bind-files=True
    apps/web/**  -> resolves 0 tracked files
M2-T003 [accepted] other-literal-entries-bind-files=True
    services/api/**  -> resolves 0 tracked files
    packages/contracts/**  -> resolves 0 tracked files
M2-T004 [accepted] other-literal-entries-bind-files=True
    services/api/** (EXCEPT services/api/requirements.txt and services/api/app/main.py - reserved for M0-T015 during Wave 1)  -> resolves 0 tracked files
    packages/contracts/**  -> resolves 0 tracked files
M2-T005 [accepted] other-literal-entries-bind-files=True
    apps/web/**  -> resolves 0 tracked files
M2-T006 [accepted] other-literal-entries-bind-files=True
    packages/contracts/**  -> resolves 0 tracked files
    services/api/**  -> resolves 0 tracked files
M2-T007 [accepted] other-literal-entries-bind-files=True
    services/api/app/connectors/** (new zoning-features module(s) only; pluto_soda.py and bbl.py may not be modified)  -> resolves 0 tracked files
    services/api/tests/connectors/** (new zoning-features test module(s) only; existing test files may not be modified)  -> resolves 0 tracked files
    services/api/tests/fixtures/zoning_features/**  -> resolves 0 tracked files
M2-T008 [accepted] other-literal-entries-bind-files=True
    services/api/app/connectors/** (new ZTLDB module(s) only; existing connector files may not be modified)  -> resolves 0 tracked files
    services/api/app/profile/** (cross-check/conflict integration ONLY, within contract 1.3.0; no contract-shape changes)  -> resolves 0 tracked files
    services/api/tests/connectors/** (new ZTLDB test module(s); existing test files only where the cross-check integration genuinely requires an additive assertion, disclosed in the report)  -> resolves 0 tracked files
    services/api/tests/profile/** (cross-check integration tests)  -> resolves 0 tracked files
    services/api/tests/fixtures/ztldb/**  -> resolves 0 tracked files
M2-T009 [accepted] other-literal-entries-bind-files=True
    services/api/app/connectors/** (new geometry module(s) only; existing connector files may not be modified)  -> resolves 0 tracked files
    services/api/tests/connectors/** (new geometry test module(s) only)  -> resolves 0 tracked files
    services/api/tests/fixtures/mappluto_geometry/**  -> resolves 0 tracked files
    services/api/requirements*.txt / pyproject dependency pin for Shapely ONLY if not already present (disclosed in report; version pinned exactly; CI green required)  -> resolves 0 tracked files
M2-T010 [accepted] other-literal-entries-bind-files=True
    packages/contracts/** (generation tooling only; NO version additions, NO semantic schema changes)  -> resolves 0 tracked files
    apps/web/src/lib/__tests__/** (regression tests)  -> resolves 0 tracked files
    services/api/tests/api/** ONLY (docstring/packaging-related test touch only if genuinely required, disclosed; NARROWED 2026-07-20 for disjointness with the parallel M2-T011 task - services/api/tests/{connectors,resilience}/** are M2-T011 territory)  -> resolves 0 tracked files
    .github/workflows/** ONLY if the derivation requires a pipeline step change - disclose in report; existing jobs must stay green  -> resolves 0 tracked files
M2-T011 [accepted] other-literal-entries-bind-files=True
    services/api/app/connectors/** (transport-loop extraction only; connector semantics preserved)  -> resolves 0 tracked files
    services/api/app/resilience/** (shared module home if placed here)  -> resolves 0 tracked files
    services/api/tests/connectors/**, services/api/tests/resilience/** (import updates and new consolidation tests)  -> resolves 0 tracked files
    docs/research/source-registry-drafts/** (additive corrections only, disclosed)  -> resolves 0 tracked files
M2-T012 [accepted] other-literal-entries-bind-files=True
    services/api/app/profile/**  -> resolves 0 tracked files
    services/api/app/_contract_schemas/** (via the sync tooling only)  -> resolves 0 tracked files
    packages/contracts/** (1.4.0 publication through M2-T010 tooling)  -> resolves 0 tracked files
    apps/web/src/lib/** (derived declarations + validation consumption)  -> resolves 0 tracked files
    services/api/app/connectors/** and services/api/app/resilience/** ONLY for the enumerated carried defects (each touch disclosed per-defect)  -> resolves 0 tracked files
    services/api/tests/**, apps/web/src/lib/__tests__/**  -> resolves 0 tracked files
    services/api/app/api/v1/** (typed error surface only if the new keys require it, disclosed)  -> resolves 0 tracked files
M2-T013 [accepted] other-literal-entries-bind-files=True
    services/api/app/spatial/** (new module)  -> resolves 0 tracked files
    services/api/tests/spatial/** (new tests + fixtures reusing committed connector fixture packs by reference)  -> resolves 0 tracked files
    docs/research/** (V1/V2 accuracy-evidence extracts, small, retrieval-dated)  -> resolves 0 tracked files
M2-T014 [accepted] other-literal-entries-bind-files=True
    docs/research/source-registry-drafts/** (additive rows)  -> resolves 0 tracked files
    docs/research/fixtures/m2-t014/** (small representative response/metadata extracts only, low-storage policy)  -> resolves 0 tracked files
M2-T015 [accepted] other-literal-entries-bind-files=True
    services/api/app/documents/**  -> resolves 0 tracked files
    services/api/tests/documents/**  -> resolves 0 tracked files
    packages/contracts/fixtures/valid/survey_evidence/**  -> resolves 0 tracked files
    packages/contracts/fixtures/invalid/survey_evidence/**  -> resolves 0 tracked files
M2-T021 [accepted] other-literal-entries-bind-files=True
    services/api/app/connectors/**  -> resolves 0 tracked files
    services/api/tests/connectors/**  -> resolves 0 tracked files
    services/api/tests/fixtures/geoclient/**  -> resolves 0 tracked files
M4-T009 [accepted] other-literal-entries-bind-files=True
    services/api/app/rules/rulesets/**  -> resolves 0 tracked files
    services/api/tests/rules/**  -> resolves 0 tracked files
M4-T023 [accepted] other-literal-entries-bind-files=True
    services/api/app/rules/review_register/**  -> resolves 0 tracked files
    docs/zoning-rule-review/**  -> resolves 0 tracked files
M4-T024 [accepted] other-literal-entries-bind-files=True
    docs/reference-cases/R6B/**  -> resolves 0 tracked files
    services/api/tests/rules/reference_cases/**  -> resolves 0 tracked files
M4-T025 [accepted] other-literal-entries-bind-files=True
    docs/research/zr-snapshots/v1/**  -> resolves 0 tracked files
    services/api/app/_zr_snapshots/v1/**  -> resolves 0 tracked files
M4-T026 [accepted] other-literal-entries-bind-files=True
    docs/research/zr-snapshots/v1/**  -> resolves 0 tracked files
    services/api/app/_zr_snapshots/v1/**  -> resolves 0 tracked files
M4-T027 [accepted] other-literal-entries-bind-files=True
    docs/reference-cases/R6B/**  -> resolves 0 tracked files
    services/api/tests/rules/reference_cases/**  -> resolves 0 tracked files
M4-T028 [accepted] other-literal-entries-bind-files=True
    docs/reference-cases/R6B/**  -> resolves 0 tracked files
    services/api/tests/rules/reference_cases/**  -> resolves 0 tracked files
M4-T029 [accepted] other-literal-entries-bind-files=True
    docs/research/zr-snapshots/v1/**  -> resolves 0 tracked files
    services/api/app/_zr_snapshots/v1/**  -> resolves 0 tracked files
M4-T030 [accepted] other-literal-entries-bind-files=True
    docs/reference-cases/R6B/**  -> resolves 0 tracked files
    services/api/tests/rules/reference_cases/**  -> resolves 0 tracked files
M4-T031 [accepted] other-literal-entries-bind-files=True
    docs/research/zr-snapshots/v1/**  -> resolves 0 tracked files
    services/api/app/_zr_snapshots/v1/**  -> resolves 0 tracked files
M4-T032 [accepted] other-literal-entries-bind-files=True
    docs/reference-cases/R6B/**  -> resolves 0 tracked files
    services/api/tests/rules/reference_cases/**  -> resolves 0 tracked files
M4-T033 [accepted] other-literal-entries-bind-files=True
    docs/research/zr-snapshots/v1/**  -> resolves 0 tracked files
    services/api/app/_zr_snapshots/v1/**  -> resolves 0 tracked files
M4-T034 [accepted] other-literal-entries-bind-files=True
    docs/research/zr-snapshots/v1/**  -> resolves 0 tracked files
    services/api/app/_zr_snapshots/v1/**  -> resolves 0 tracked files
M5-T004 [accepted] other-literal-entries-bind-files=True
    apps/web/src/app/property/compare/**  -> resolves 0 tracked files
    apps/web/src/components/compare/**  -> resolves 0 tracked files
    apps/web/src/lib/scenario-*  -> resolves 0 tracked files
M5-T018 [accepted] other-literal-entries-bind-files=True
    apps/web/src/components/compare/**  -> resolves 0 tracked files
M5-T048 [accepted] other-literal-entries-bind-files=True
    packages/contracts/fixtures/valid/scenario/**  -> resolves 0 tracked files
    packages/contracts/fixtures/invalid/scenario/**  -> resolves 0 tracked files
    packages/contracts/fixtures/semantically_invalid/scenario/**  -> resolves 0 tracked files
M5-T051 [accepted] other-literal-entries-bind-files=True
    services/api/tests/scenario/fixtures/derivation/**  -> resolves 0 tracked files
M5-T054 [accepted] other-literal-entries-bind-files=True
    services/api/tests/rules/fixtures/proposal_checks/**  -> resolves 0 tracked files
M5-T066 [accepted] other-literal-entries-bind-files=True
    apps/web/src/components/architect/ProposalOutlineMap*.tsx  -> resolves 0 tracked files
    apps/web/src/components/architect/__tests__/proposal-outline-map*.test.tsx  -> resolves 0 tracked files
M5-T073 [accepted] other-literal-entries-bind-files=True
    services/api/tests/connectors/fixtures/bridge_ring_pairs/**  -> resolves 0 tracked files
M5-T089 [accepted] other-literal-entries-bind-files=True
    services/api/tests/fixtures/building_footprints/**  -> resolves 0 tracked files
M5-T096 [accepted] other-literal-entries-bind-files=True
    docs/samples/cad/**  -> resolves 0 tracked files
M5-T126 [accepted] other-literal-entries-bind-files=True
    docs/measurement-basis/**  -> resolves 0 tracked files
    services/api/tests/scenario/measurement_basis/**  -> resolves 0 tracked files
M5-T129 [accepted] other-literal-entries-bind-files=True
    services/api/app/scenario/three_answers/result_way_*.py  -> resolves 0 tracked files
    services/api/tests/scenario/three_answers/test_result_ways_*.py  -> resolves 0 tracked files
M5-T130 [accepted] other-literal-entries-bind-files=True
    services/api/app/scenario/three_answers/result_way_bridge_*.py  -> resolves 0 tracked files
    services/api/tests/scenario/three_answers/test_result_way_bridge_*.py  -> resolves 0 tracked files
M5-T132 [accepted] other-literal-entries-bind-files=True
    services/api/app/scenario/three_answers/result_way_*.py  -> resolves 0 tracked files
    services/api/tests/scenario/three_answers/test_result_ways_*.py  -> resolves 0 tracked files
    services/api/tests/scenario/three_answers/test_result_way_*.py  -> resolves 0 tracked files
M5-T133 [accepted] other-literal-entries-bind-files=True
    docs/measurement-basis/**  -> resolves 0 tracked files
    services/api/tests/scenario/measurement_basis/**  -> resolves 0 tracked files

=== IN-FLIGHT (11) ===
M0-T021 [awaiting_gate] other-literal-entries-bind-files=True
    services/api/scripts/tests/**  -> resolves 0 tracked files
M3-T002 [backlog] other-literal-entries-bind-files=False
    services/api/app/corpus/ingest/** (OWNED by M3-T002)  -> resolves 0 tracked files
    services/api/app/corpus/storage/** (OWNED by M3-T002)  -> resolves 0 tracked files
    services/api/app/corpus/versioning/** (OWNED by M3-T002)  -> resolves 0 tracked files
    services/api/tests/corpus/ingest/**, services/api/tests/corpus/storage/**, services/api/tests/corpus/versioning/**  -> resolves 0 tracked files
    services/api/tests/fixtures/corpus/capture/**  -> resolves 0 tracked files
    infra/ingestion/**  -> resolves 0 tracked files
M3-T003 [backlog] other-literal-entries-bind-files=False
    services/api/app/corpus/extractors/** (OWNED)  -> resolves 0 tracked files
    services/api/app/corpus/document_validation/** (OWNED)  -> resolves 0 tracked files
    services/api/app/corpus/evidence/** (OWNED)  -> resolves 0 tracked files
    packages/contracts/schemas/v1/fixtures/{document_classification,extraction_run,evidence_span,cross_source_comparison,human_review_decision}/**  -> resolves 0 tracked files
    services/api/tests/corpus/evidence/**  -> resolves 0 tracked files
    services/api/tests/fixtures/corpus/evidence/**  -> resolves 0 tracked files
M3-T004 [backlog] other-literal-entries-bind-files=False
    services/api/app/corpus/closure/** (OWNED by M3-T004; exclusive)  -> resolves 0 tracked files
    packages/contracts/schemas/v1/fixtures/closure_manifest/**  -> resolves 0 tracked files
    services/api/tests/corpus/closure/**  -> resolves 0 tracked files
    services/api/tests/fixtures/corpus/closure/**  -> resolves 0 tracked files
M3-T005 [backlog] other-literal-entries-bind-files=False
    services/api/app/corpus/construction_code/** (OWNED by M3-T005; exclusive)  -> resolves 0 tracked files
    services/api/app/corpus/overlay/** (OWNED by M3-T005; exclusive)  -> resolves 0 tracked files
    services/api/tests/corpus/construction_code/**, services/api/tests/corpus/overlay/**  -> resolves 0 tracked files
    services/api/tests/fixtures/corpus/construction_code/**  -> resolves 0 tracked files
M4-T001 [awaiting_gate] other-literal-entries-bind-files=True
    services/api/app/rules/** (new module)  -> resolves 0 tracked files
    services/api/tests/rules/**  -> resolves 0 tracked files
    packages/contracts/schemas/v1/** rule-definition/evaluation-trace schemas via M2-T010 tooling (additive only, disclosed)  -> resolves 0 tracked files
M4-T002 [awaiting_gate] other-literal-entries-bind-files=True
    services/api/app/rules/** (new integration module; consume profile/spatial via read-only imports only)  -> resolves 0 tracked files
    services/api/tests/rules/**  -> resolves 0 tracked files
M4-T004 [awaiting_gate] other-literal-entries-bind-files=True
    services/api/tests/rules/**  -> resolves 0 tracked files
M4-T005 [awaiting_gate] other-literal-entries-bind-files=True
    packages/contracts/scripts/tests/**  -> resolves 0 tracked files
    packages/contracts/fixtures/valid/rule_evaluation/**  -> resolves 0 tracked files
    packages/contracts/fixtures/invalid/rule_evaluation/**  -> resolves 0 tracked files
    services/api/app/_zr_snapshots/**  -> resolves 0 tracked files
    services/api/tests/api/**  -> resolves 0 tracked files
    services/api/tests/rules/**  -> resolves 0 tracked files
    services/api/tests/contracts/**  -> resolves 0 tracked files
    apps/web/src/app/property/**  -> resolves 0 tracked files
    apps/web/src/components/property/**  -> resolves 0 tracked files
    apps/web/src/components/rule-evaluation/**  -> resolves 0 tracked files
    apps/web/src/test-support/**  -> resolves 0 tracked files
    apps/web/e2e/**  -> resolves 0 tracked files
M4-T006 [awaiting_gate] other-literal-entries-bind-files=False
    services/api/app/rules/rulesets/*.rule.json (NEW R5 height/setback ruleset file(s); do NOT edit r5_residential_far.rule.json)  -> resolves 0 tracked files
    services/api/app/rules/schemas/v1/*.schema.json (ONLY if an additive min/max height-setback DSL field is required; extend additively, never redefine)  -> resolves 0 tracked files
    services/api/app/_zr_snapshots/v1/*.snapshot.json + the sync_zr_snapshots source dir (NEW official ZR snapshots, byte-identical + hash-guarded, package-data per M4-T005)  -> resolves 0 tracked files
    services/api/tests/rules/** (deterministic, fail-closed, effective-date, provenance, rule-conflict, negative-control NC-1..NC-7, installed-wheel deployability tests)  -> resolves 0 tracked files
M5-T001 [awaiting_gate] other-literal-entries-bind-files=True
    services/api/app/scenario/** (new deterministic foundation module + typed constraint/completeness model; consume profile/rule-evaluation via read-only imports only)  -> resolves 0 tracked files
    services/api/tests/scenario/** (acceptance pack AS-1..AS-12)  -> resolves 0 tracked files

FROZEN ID LIST (accepted + in-flight), sorted:
['M0-T004', 'M0-T005', 'M0-T005-R1', 'M0-T006', 'M0-T009', 'M0-T010', 'M0-T011', 'M0-T015', 'M0-T018', 'M0-T019', 'M0-T020', 'M0-T021', 'M0-T022', 'M0-T036', 'M0-T041', 'M0-T042', 'M0-T044', 'M0-T045', 'M0-T046', 'M0-T048', 'M0-T049', 'M0-T050', 'M0-T051', 'M0-T181', 'M0-T184', 'M0-T186', 'M1-T001', 'M1-T002', 'M1-T003', 'M1-T004', 'M1-T005', 'M1-T006', 'M1-T007', 'M1-T008', 'M1-T009', 'M2-T001', 'M2-T002', 'M2-T003', 'M2-T004', 'M2-T005', 'M2-T006', 'M2-T007', 'M2-T008', 'M2-T009', 'M2-T010', 'M2-T011', 'M2-T012', 'M2-T013', 'M2-T014', 'M2-T015', 'M2-T021', 'M3-T002', 'M3-T003', 'M3-T004', 'M3-T005', 'M4-T001', 'M4-T002', 'M4-T004', 'M4-T005', 'M4-T006', 'M4-T009', 'M4-T023', 'M4-T024', 'M4-T025', 'M4-T026', 'M4-T027', 'M4-T028', 'M4-T029', 'M4-T030', 'M4-T031', 'M4-T032', 'M4-T033', 'M4-T034', 'M5-T001', 'M5-T004', 'M5-T018', 'M5-T048', 'M5-T051', 'M5-T054', 'M5-T066', 'M5-T073', 'M5-T089', 'M5-T096', 'M5-T126', 'M5-T129', 'M5-T130', 'M5-T132', 'M5-T133']
```

## Freezing and regeneration

`PATTERN_ALLOWED_PATHS_GRANDFATHERED` in `tools/directive_registry.py` is this exact 88-id set.
It **never grows by hand** — it is regenerated by this script. Because M0-T188's tool commits are
integrated onto the wave branch LAST (after the two wave peers submit and gate with the unchanged
tools), the orchestrator regenerates the list at the integration head; a task that drained its
pattern entries to literal paths before then simply resolves non-empty and no longer needs the
exemption. M0-T188's own `allowed_paths` are all literal, so it is correctly NOT in the list.

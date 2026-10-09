# M5-T010 — Directive-Compliance Verification (DCV) vs D-038 (verbatim reviewer return)

Verifier: **directive-compliance-verifier** (independent ≠ producer scenario-optimization-engineer, ≠ orchestrator). Reviewed SHA `ea08f504ea4b52cc93062a74a9c125e5133c4b7b`. Transport entity-decoding applied; content otherwise verbatim.

---

# Independent Directive-Compliance Verification — M5-T010 vs D-038

**Reviewed SHA (frozen head):** `ea08f504ea4b52cc93062a74a9c125e5133c4b7b` — confirmed via `git rev-parse HEAD` == the expected head. Branch `candidate/D-024-mrl-option-b`. Parent = `c62bb93077c57cdc62e422271deb66e9d9ca63d9` (matches the producer report's declared base `c62bb930`).

**Role:** independent verifier (≠ producer scenario-optimization-engineer, ≠ orchestrator). Read-only. Producer report treated as claims and reproduced against primary evidence.

## VERDICT: PASS

Applicable requirement set for M5-T010 = **{D-038-R003, D-038-R004}**, both **PASS**. No VIOLATED / UNVERIFIABLE / BLOCKED rows.

## Applicability sweep (how the set was derived)

`python tools/project_control.py evaluate_task_refs --task-id M5-T010` — **verb does not exist** in this CLI build (subcommands are `init, new-task, claim, progress, submit, gate, accept, checkpoint, status`). Per instruction I reasoned from the registry directly:

- R001, R002, R005, R006, R007 — each `applicability.task_ids == ["D-038-BOOTSTRAP"]` only (sentinel; no `task_types`/`milestones`/`paths`). **Not applicable** to ledger task M5-T010.
- R003 — `applicability.task_ids` includes `"M5-T010"` (requirements.json line 88). **Applicable.**
- R004 — `applicability.task_ids` includes `"M5-T010"` (requirements.json line 129). **Applicable.**
- Task `directive_refs = [{D-038: ALL}]` (M5-T010.json lines 69-74), so cited ⊇ applicable → selective-citation guard satisfied.

## Integrity

- `python tools/validate_directive_compliance.py --check` → **EXIT 0**.
- `sha256(requirements.json)` = `2e904ad643a07b59cc1acb3f6d6ab12c91a60f88698dc20e0e27289b6bd84bdf` == `manifest.requirements_content_digest_sha256`. **MATCH.**
- `sha256(source-001.md)` = `a237dd50672e4745aff5dc5b19cf79506252a0ff0742184576f99b29f7962212` == `manifest.sources[0].content_digest_sha256`. **MATCH (source unchanged).**
- `locked_requirement_ids` = R001..R007, all 7 present/unchanged.
- `audit_log` has the M5-T010 entry: `applicability_appended` @ `2026-09-09T04:30:00`, resync `84ab4118 → 2e904ad6`, "No requirement id added/removed/renumbered". **Present.**

## Diff scope (no forbidden path)

`git show HEAD --name-only` = exactly the 4 allowed paths: `comparison.py`, `__init__.py`, `test_scenario_comparison.py`, `M5-T010-producer-report.md`. Grep for forbidden paths (derive/builder/models/constants/contract/ranking/sensitivity/_json_safety/packages/contracts/apps/web/tools) → **NONE**. `__init__.py` diff is additive-only.

## Per-requirement rows

### D-038-R003 — positive product deliverable — **PASS**
- Genuine product, not M0 self-infra: `M5-T010.json` `task_type="backend"`, `milestone_id="M5"`; deliverable `services/api/app/scenario/comparison.py` (601 SLOC) — optimization/comparison engine. `allowed_paths` all product scenario-engine files.
- Contracted G0 packet: `project-control/gates/M5-T010-G0.json` → `result="PASS"`, `role="administrative"`.
- Executable AS-1..AS-7 mapped to real passing tests in `test_scenario_comparison.py` (`test_as1_*`…`test_as7_*` + rework tests). `pytest test_scenario_comparison.py` → **71 passed**; full suite → **323 passed** (323 − 71 = 252 pre-existing, 0 regression).
- Read-only echo, never Verified, cap verbatim (reproduced): for cap 12345.0, `derive.canonical_cap_sq_ft` == comparison `baseline_metrics.canonical_cap_sq_ft`; `assert_scenario_not_verified(compared_doc)` PASS; incoming `verified` → `conditional`, `needs_review=True`.
- Modularity: `modularity_check --check` → **EXIT 0** (comparison.py not flagged).

### D-038-R004 — no Supabase / no live Geoclient / offline — **PASS**
- Import inspection: comparison.py imports only `json`, `math`, `typing` + `._json_safety` + `.constants` + `.derive`. No network/persistence/env/subprocess.
- Negative grep over comparison.py for `supabase|geoclient|requests|httpx|socket|urllib|os.environ|getenv|subprocess|import os|open(|aiohttp|psycopg|sqlalchemy` → No matches. Transitive grep over all `services/api/app/scenario/*.py` → No files match.
- Socket-blocked run reproduced: with `socket.socket`/`socket.create_connection` patched to raise, `compare_scenario_assumption_sets` runs to completion; `json.dumps(result, allow_nan=False)` OK (len 11308); `" at 0x"` leak = False.
- Determinism/degenerate reproduced: 3 input orders → byte-identical JSON; <2 sets → `invalid_comparison_request`; no-cap doc → `empty_no_comparable_cap`; non-list → `invalid_comparison_request`.
- Packet declares no Supabase/Geoclient dependency: `dependencies=["M5-T009"]` only; fixture/pure-Python tests.

## Content-identity / drift check
Producer report cited line ranges resolve exactly against the committed file (`_base_lineage` 193-208, `_base_lineage_identity` 211-226, `_compared_metrics_doc` 229-232, `_parse_entry` 238-287). Verbatim excerpts byte-for-byte the committed bytes. No report↔code drift.

## Transparency notes (not defects)
1. `evaluate_task_refs` is not a subcommand in this CLI build; applicable set derived from requirements.json applicability blocks per fallback instruction.
2. The producer report's self-reported working-tree digest `f79bfafb…` (raw-bytes sha256 of its uncommitted tree) was not reproduced — a producer CLAIM about a pre-commit tree; I verify at committed HEAD ea08f504. Immaterial: verified committed bytes directly.
3. Prohibited-action check: producer worktree-commit on the candidate branch only — nothing merged/accepted/pushed/deployed. `final_reviewed_sha` null; M5-T010 verification rows not yet written (orchestrator's step). PR #241 untouched.

## Rows for verification.json

| Requirement | State | Reviewed SHA | Primary evidence |
|---|---|---|---|
| D-038-R003 | **PASS** | ea08f504 | M5 backend product engine comparison.py; G0 PASS; AS-1..AS-7 → 71 tests + full suite 323 passed; cap verbatim (12345.0 identical) + assert_scenario_not_verified PASS; modularity_check EXIT 0 |
| D-038-R004 | **PASS** | ea08f504 | comparison.py imports stdlib+.derive+.constants+._json_safety only; negative grep (module + transitive) no network/persistence; socket-blocked run completes, json allow_nan=False OK, no address leak; deps=[M5-T009] only; offline fixture tests pass |

**Overall: PASS.** Both applicable requirements (D-038-R003, D-038-R004) independently verified SATISFIED at frozen head `ea08f504ea4b52cc93062a74a9c125e5133c4b7b`.

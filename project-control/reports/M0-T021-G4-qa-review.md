# M0-T021 — G4 (QA / regression) verbatim return

_Verbatim independent qa-engineer return (transport decoding only). Orchestrator-recorded._

**Task:** M0-T021 — Repair lock-verifier reproducibility check (blank-temp → seeded committed lock)
**Frozen code SHA:** `bd80e72` (worktree tip `eded402` is ledger/reports-only; code == `bd80e72`)
**Reviewer:** qa-engineer (independent, read-only). **Verdict: PASS** (one non-blocking orchestrator confirmation item N1).

## Scope verified (f5ab631 → bd80e72)
Service-code changes = exactly three files: `lock_tools.sh` (+11), `lock_requirements.sh` (+11 mirror), new `tests/test_lock_verify_reproducibility.py` (405). Byte-identical to f5ab631 (via `git diff --quiet`): `dependency_age_gate.py`, both `.in`, both locks. Remaining delta = ledger/control artifacts.

## Required commands — independently run
| Command (from services/api) | Expected | Actual |
|---|---|---|
| `pytest scripts/tests/test_lock_verify_reproducibility.py -v` | 11 | **11 passed** |
| `pytest scripts/tests -q` | 28 | **28 passed** |
| `pytest scripts/tests/test_dependency_age_gate.py -q` | 17 | **17 passed** |
| `bash -n scripts/lock_tools.sh` / `lock_requirements.sh` | OK | **OK** |

`--upgrade` only in comments + the AS-6 negative assertion; never in executable code. Suite mutated no committed service files.

## Acceptance scenarios — verified genuine and regression-meaningful
- **AS-1** consistent lock → PASSES (both mirrors). HOLDS.
- **AS-2 (core)** newer upstream but seeded pin satisfies inputs → PASSES; sub-assertion resolves a blank output and asserts it pulls `2.0.0`. Genuinely exercises seeding. HOLDS.
- **AS-3** genuine input drift → FAILS rc 1 with diff. HOLDS.
- **AS-4** tampered hash → FAILS rc 1. HOLDS.
- **AS-5** age gate boundary via the real unmodified `dependency_age_gate.py` (604800 PASS / 604799 FAIL). HOLDS.
- **AS-6** both scripts seed before compile; no `--upgrade` in code. HOLDS.

**Independent differential proof (my own fake resolver):** copied `lock_tools.sh`, produced a pre-fix variant by stripping the `cp` seed, ran both under a newer-upstream fake uv — fixed script rc **0**, pre-fix (blank) rc **1** (the deadlock). Confirms the seed line is load-bearing and a revert would be caught.

## Fake-uv stub fairness
Faithful model of the preference/hash behavior; deterministic/offline; fake uv reports `0.11.28` so the script's version guard passes. Limitation: the stub resolves only packages in the `.in`, not transitive-only deps (the real deadlock, certifi, was transitive) — so the offline suite proves the script plumbing + the preference mechanism on direct deps; real-uv transitive proof is the committed CI (N1).

## Findings
- **N1 (non-blocking, orchestrator confirmation):** real-uv proof is the committed CI — `api-tooling-lock-verify` + `api-lock-verify` green at `bd80e72` while certifi 2026.7.22 was upstream (RED pre-fix). Orchestrator should record the 12/12 green with the gate (captured in `M0-T021-ci-evidence.md`).
- **N2 (info):** AS-6 anchors on `text.index('MODE')` — functions correctly; stylistic fragility only.
- No blocking defects; no missing/failing claimed scenario; no mutation of real locks; no `--upgrade` in code.

## VERDICT: PASS

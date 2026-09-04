# M0-T109 — G4 independent review (test/QA + integration/regression)

> Orchestrator note: reviewer return saved verbatim (transport entity-decoding only). Reviewer: independent qa-engineer agent (read-only), returned 2026-09-04 (UTC).

**Reviewer:** qa-engineer (roster G4 gate). **Read-only.** **Task:** M0-T109 readonly-guard follow-up hardening (D-024, in-regime).
**Reviewed content:** candidate commit `7f075e37` (adoption), blob-identical to task tip `67b5b4dc`. **ctl24 HEAD:** `f993bafc2faed19ffbbcbc71385d87379c6f73bc` (candidate/D-024-mrl-option-b).

## 1. Required suites (run from ctl24, which is at the reviewed content)
- `python tools/test_readonly_agent_guard_powershell.py` → **ALL CHECKS PASSED**, `EXIT=0`. Includes Round-5 (ADV-R4-1 5 deny + 2 no-FP; ADV-4 3 deny + 1 no-FP; ADV-R4-2 2 residual-doc) and 17 RED-on-mutant proofs.
- `python tools/test_readonly_agent_guard.py` → **ALL CHECKS PASSED**, `EXIT=0` (shell-agnostic suite; all M0-T108 denials preserved).

## 2. Mutant proofs genuine (independently verified)
Framework (lines 478-489): each mutant written to a temp guard; passes only if `mutant→ALLOW AND real→DENY`. Any no-op (`mutated_src == SRC`) is force-failed at lines 480-481 (`check_static("[mutation applied]", False)`). All passed ⇒ no dead replace. I confirmed each search literal exists in the guard, so the replace is non-trivial:
- **(c) CreateInstance-only** (test 434-439): drops `\[(?:System\.)?Activator\]::CreateInstance\b` (guard line **258**); payload `[activator]::CreateInstance($t)` carries no ProgID ⇒ only this tooth denies. Genuine.
- **(b) GetTypeFromProgID-only** (test 441-446): drops `\[(?:System\.)?Type\]::GetTypeFromProgID\b` (guard line **259**, self-anchored); payload has no CreateInstance ⇒ only this tooth denies. Genuine; also proves the tooth is now *reachable* (was dead behind the `:`-excluding leading class).
- **(a) chained-assignment-loop-revert** (test 447-454): replaces the `while prev != head` loop (guard lines **613-615**) with a single strip; payload `$a=$b=powershell -enc …` ⇒ single strip leaves `$b=powershell` (ALLOW), loop reduces to `powershell` (DENY). Genuine.

## 3. Coverage — no-FP rows pass and are meaningful
- `$a=$b=Get-Content README.md` and spaced form → **ALLOW** (loop strips all layers to `Get-Content`, a read). Guards against an over-broad "deny all chained assignment" fix.
- `Get-Content -Encoding UTF8 GetTypeFromProgID-notes.md` → **ALLOW** (self-anchored tooth needs the `[Type]::` prefix, so the name as data/filename does not match). Guards against a substring-match false positive.

## 4. Regression
- Prior M0-T108 denials preserved: Round-1..4 + C1-C3/D1-D4/A1-A3/F1-F2/NF1-NF2 sections all PASS in both suites.
- **Bash pack byte-unchanged:** `git diff 1c069571 67b5b4dc` touches only the 3 deliverable paths; the guard diff changes only the PS `_PS_MUTATING` reflection tooth (line 259), the `_ASSIGN_LAYER` loop, and docstrings — no `_unquoted_redirect`/`_launches_nested_shell`/bash denial line; the shell-agnostic test file is not in the changeset.
- `-Encoding` / powershell-as-data reads still **ALLOW** (C3, D-R3-1, ADV-4 no-FP rows PASS).

## 5. Integration
- `python tools/modularity_check.py --check` → **failures 0**, warnings 12, `EXIT=0`. `readonly_agent_guard.py` is not in the warn or failure list ⇒ warn-only, not a ceiling failure (contrast M0-T133).
- `python -m ruff check` (ruff **0.13.0**, matches CI) on both changed files → **All checks passed!** `EXIT=0`.
- **Blob-identity:** guard `ad009d4f…`, ps-test `0fd81db3…`, report `c27862fe…` are identical across task tip `67b5b4dc`, adoption `7f075e37`, candidate HEAD `f993bafc`, and ctl24's working-tree files (`git hash-object`).
- **No forbidden path touched:** adoption commit changes exactly `.claude/hooks/readonly_agent_guard.py`, `tools/test_readonly_agent_guard_powershell.py`, `project-control/reports/M0-T109-guard-hardening.md` — all within allowed_paths; none of the forbidden_paths (`.claude/settings.json`, `apps`, `services`, `tools/project_control.py`, …) changed.

## 6. Bounded footprint
`7f075e37..f993bafc` = three orchestrator control-plane commits only (`M0-T109-evidence-map.json`, `M0-T109.json`, `state.json`, `M0-T109-G2.json`, `reports/M0-T109.json`) — M0-T109 ledger records, explicitly allowed. The adoption commit touches only the 3 deliverable paths.

## Notes / scope boundary
- In-regime (`directive_refs: D-024 ALL`). Per-requirement directive verification (incl. the evidence-map's honestly-PENDING R754 owner-gated live run and R760 terminal path) is the separate `directive-compliance-verifier`'s pass into `verification.json`; it is outside this G4 test/QA gate and is not a test-quality defect. The code deliverable and its tests are complete and green.

All G4 scope items (1-6) verified with reproduced command output. No defects found.

VERDICT: PASS
ctl24 HEAD reviewed: f993bafc2faed19ffbbcbc71385d87379c6f73bc

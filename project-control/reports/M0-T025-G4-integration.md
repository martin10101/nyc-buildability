# G4 Independent Review — M0-T025 "path containment for manifest requirements_file/verification_file references (LOW-1)"

**Task:** M0-T025 (governance / control-plane hardening; in-regime, cites D-002 ALL)
**Gate:** G4 (integration / regression, whole-control-plane level)
**Reviewer:** control-plane-verifier (read-only, independent; producer = `supervised-loop-fable-worker`; I am not the producer and not the orchestrator)
**Reviewed identity:** frozen producer candidate `20f7651c`, merged at `56db6a17`, present unchanged at current branch HEAD `2194cf5a` (`candidate/D-024-mrl-option-b`).

## 1. Captured full-suite evidence — CONFIRMED

- **wt-m0t025 HEAD == 20f7651c:** CONFIRMED. `git rev-parse HEAD` in `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t025` = `20f7651c24461655cbee7514c398eed4a2efa71f`, branch `task/M0-T025-path-containment`, working tree clean (`git status --porcelain` empty).
- **Three tool files byte-identical to ctl24 HEAD blobs:** CONFIRMED. Blob SHAs are identical at wt HEAD (20f7651c), ctl24 HEAD (2194cf5a), and merge 56db6a17:
  - `tools/directive_registry.py` = `e1168304`
  - `tools/validate_directive_compliance.py` = `d649b6fe`
  - `tools/test_directive_compliance.py` = `940ad7dd`
  - (`project-control/reports/M0-T025-producer-report.md` = `805ddc84`, also identical.)
  So the captured run at wt-m0t025 @ 20f7651c executed the exact content merged to HEAD.
- **Log shape is genuine `pytest -q` output:** CONFIRMED. `M0-T025-full-suite-20f7651c.txt` = two progress-dot lines (`72` dots `[ 57%]`, then `54` dots `[100%]`), the summary `126 passed in 4697.02s (1:18:17)`, then an appended `PYTEST EXIT: 0`. 72 dots at the wrap = 72/126 = 57.1% → `[57%]`; 126/126 → `[100%]`. 4697 s = 78.3 min, consistent with the ~78-min suite. No skips/xfails/errors/warnings in the summary.
- **Test count consistent with the file's inventory (counted independently):** CONFIRMED. I counted `def test_` methods in `tools/test_directive_compliance.py` two ways (git grep -c and Grep count) = **126**, and the progress dots total **72 + 54 = 126**. Exact match to "126 passed", with no parametrization inflation and no skips.

## 2. Regression at the control-plane level — CONFIRMED

- `python tools/validate_directive_compliance.py --check` → **exit 0** (ran it myself at ctl24 HEAD 2194cf5a; the real 30-directive registry validates clean through the new containment guard).
- Control-CLI machinery end-to-end: `python -m pytest tools/test_project_control.py -q` → **23 passed in 154.53 s, exit 0** (ran it myself). The directive-compliance loader/`evaluate_task_refs` consumed by the control plane still works end to end.
- Note: my local re-run of the heavy containment subset (`-k "PathContainment or guard_*"`) was SIGKILLed by the sandbox resource cap (exit 137) — these tests each copy the 7.7 MB / 265-file registry (the documented slow characteristic), not a test failure. Passing evidence for that subset comes from the captured full-suite log (126 passed) and the two prior independent gates that ran it green: G3 (7 passed / 707 s) and G5 (6 passed / 421 s).

## 3. Additive narrowing only; no behavior change for well-formed registries — CONFIRMED

From `git show 20f7651c`:
- New shared guard `resolve_contained_ref(base_dir, ref)` is a **pure addition** (returns `(path, None)` for contained refs; `(None, reason)` otherwise).
- Loader (`directive_registry.py`): refactored to call the guard, but the valid-reference accept path is preserved — contained + exists → `_load_json` (as before); missing → same `"… missing"` error; invalid JSON → same `"… invalid"` error. The **only** new branch is containment rejection (`fpath is None`), routed to the same `d.errors` fail-closed sink.
- Validator c14 (`validate_directive_compliance.py`): adds `if rfile_path is None: errors.append(... containment ...)` and guards the digest branch with `elif rfile_path is not None and rfile_path.exists()`. For a well-formed ref the digest computation is unchanged.
- `_hash_manifest_entries` change is **E702 lint-only** (semicolon-joined statements split onto separate lines) — same statements, same order, byte-identical hashing.
- **No product/runtime code touched:** the diff is exactly 4 files — 3 under `tools/`, 1 under `project-control/reports/`. No `services/**`, `apps/**`, or `packages/**`. `git show --stat 20f7651c` = 4 files, 339 insertions, 33 deletions.

## 4. Task-outputs completeness (M2-T015 lesson) — CONFIRMED

Each named deliverable in the packet `outputs` exists at merged HEAD:
- `tools/directive_registry.py` — present, modified (guard + loader). ✔
- `tools/validate_directive_compliance.py` — present, modified (c14 guarded resolution). ✔
- `tools/test_directive_compliance.py` — present, modified (PathContainmentTests + lint rider). ✔
- `project-control/reports/M0-T025-producer-report.md` — present (blob 805ddc84). ✔

## Independence / process

Producer `supervised-loop-fable-worker` ≠ this G4 reviewer (`control-plane-verifier`) ≠ prior gate reviewers (G3 `code-reviewer`, G5 `security-reviewer`, DCV `directive-compliance-verifier`). All prior gates PASS; task is `awaiting_gate` (not accepted). No writes, git mutations, or control-CLI performed.

## Reviewed identity and commands

Reviewed identity: frozen candidate `20f7651c` (byte-identical at HEAD `2194cf5a`; four blobs `e1168304 / d649b6fe / 940ad7dd / 805ddc84`). Commands I ran:
- `git rev-parse HEAD` (ctl24) → `2194cf5a…`; (wt-m0t025) → `20f7651c…`, clean tree
- `git ls-tree` at 20f7651c / HEAD / 56db6a17 / wt HEAD → four blobs identical (as above)
- `git show --stat 20f7651c` → 4 files (3 tools + report); `git show 20f7651c -- tools/*.py` → additive-narrowing diff confirmed
- `python tools/validate_directive_compliance.py --check` → **exit 0**
- `python -m pytest tools/test_project_control.py -q` → **23 passed, exit 0**
- Independent `def test_` count in `tools/test_directive_compliance.py` → **126**; full-suite log dots 72+54 = **126** vs summary "126 passed", `PYTEST EXIT: 0`

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the control-plane-verifier agent-return channel (2026-09-07 gate wave, task notification a3b57d05db0b83e7f; leading corroboration sentence and trailing absolute-path routing note removed as transport framing, content unaltered). The reviewer ran against HEAD `2194cf5a`; the four reviewed blobs are byte-identical at the recording-time HEAD (verified by the orchestrator via `git ls-tree` before recording the gate).*

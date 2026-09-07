# G3 Independent Review — M0-T025 "path containment for manifest requirements_file/verification_file references (LOW-1)"

**Task:** M0-T025 (governance / control-plane hardening, in-regime, cites D-002 ALL)
**Reviewer:** code-reviewer (read-only, independent; producer = supervised-loop-fable-worker)
**Reviewed identity:** frozen producer candidate `20f7651c` (merged at `56db6a17`). I confirmed the branch working tree (`candidate/D-024-mrl-option-b`) is byte-identical to `20f7651c` for the three tool files (`git diff --stat 20f7651c -- …` returned empty), so my runtime checks execute the exact reviewed content.

## Scope of change (diff verified)
- `tools/directive_registry.py` — new shared guard `resolve_contained_ref(base_dir, ref)` (lines 401-422); loader loop (lines 543-556) resolves both manifest references through it.
- `tools/validate_directive_compliance.py` — c14 body-digest path resolves `requirements_file` via `dr.resolve_contained_ref` (lines 487-490, 495).
- `tools/test_directive_compliance.py` — new `PathContainmentTests` + lint rider.
- `project-control/reports/M0-T025-producer-report.md` — evidence only.
Forbidden paths (product/runtime, `.claude/**`, other directives, D-002 sources) untouched. Scope honored.

## Findings against the review checklist

**1. LOW-1 disposition implemented exactly — CONFIRMED.** `project-control/reports/M0-T024-LOW-1.md` requires (a) `requirements_file`/`verification_file` must resolve inside the directive's own directory, rejecting `..` and absolute paths with a clear error; (b) fail-closed behavior preserved (narrow only); (c) positive + negative tests. All three present. The change adds rejection only; the existing missing/invalid-file error paths are retained verbatim.

**2. Single containment authority — CONFIRMED.** `resolve_contained_ref` is defined once in `directive_registry.py:401` and consumed by the loader (`directive_registry.py:547`) and the validator (`validate_directive_compliance.py:487`, via `dr.`). Grep of `tools/**` for `requirements_file|verification_file` shows only these two resolution sites; all other hits are manifest-key lists or test fixtures. `project_control.py` reads verification through the guarded loader (`evaluate_task_refs`), not a private opener. No divergent second implementation.

**3. Rejection classes on Windows AND POSIX — CONFIRMED, no bypass found.** I exercised the guard directly on this Windows host (`python -c … resolve_contained_ref`):
- ACCEPT: `requirements.json`, `sub/requirements.json` (legit nested relative — no false rejection).
- REJECT: `../other/x.json`, `a/../../x.json` (traversal); `/rooted/x.json`, `C:/abs/x.json`, `C:\abs\x.json` (absolute); `C:file.json` (drive-relative, caught by `p.drive`); `\\server\share\x.json` (UNC); `\x.json` (bare root); `..\other\x.json` (backslash traversal, parts-split on Windows); `''`, `None`, `42` (non-string/empty).
Cross-platform reasoning holds: Windows-only forms (`C:file.json`, UNC, `\x.json`, `..\…`) that are literal filenames on POSIX stay inside `base_dir` and are contained there, so they cannot escape on either platform; the final `_within()` resolve() check (`directive_registry.py:390`) catches residual symlink / redundant-separator escapes because `resolve()` follows symlinks before `relative_to`. Exact-component `".." in p.parts` (not prefix match) means a legitimate dir like `..data/` is not falsely rejected.

**4. Fail-closed equivalence — CONFIRMED.** A rejected ref appends to `d.errors` (loader `directive_registry.py:549`), the identical sink used for a missing file (`:551`). Consequences chain: `is_active` → False (`:447`, errors present); `validate()` surfaces it as `c2 [D-xxx] … containment` (`:368-369` and `:490`); `evaluate_task_refs` returns an invalid ref "cited directive … has integrity errors … fail closed" (`:685-688`) → `ok: False`, which `accept()` refuses; validator exits non-zero. No new partial-trust path — the digest is never computed over an out-of-directory file (`validate_directive_compliance.py:495` guards on `rfile_path is not None`).

**5. AS-1 / AS-2 tests — CONFIRMED sound.** The AS-1 negatives copy the real `requirements.json`/`verification.json` to the escaping target as a byte-identical file, so absent the guard the file would be found and pass the content-digest check unchanged; therefore the observed rejection can only be the containment guard — the isolation the producer claims is real. `test_as1_registry_fails_closed_on_escaping_ref` proves the full chain (`requirements == {}`, `is_active False`, `evaluate_task_refs` invalid). AS-2 (`test_as2_in_directory_refs_still_pass`, `test_real_registry_valid`) plus my own `validate --check` (exit 0) prove no regression on the real 30-directive registry.

**6. Lint rider — CONFIRMED behavior-neutral except the one intended strengthening, which is sound.** 11 findings = E702×7 (statement-per-line splits in `_hash_manifest_entries` and `_git` calls — same calls, same order, byte-identical hashing/side-effects), E741×2 (`l`→`line` rename), F841 `reg` (unused local dropped; the `self._reg(...)` side-effecting call is kept). The single strengthening, `assertEqual(m2, m1)` in `test_manifest_is_order_independent_and_content_based`, is sound by construction: `content_manifest` (`directive_registry.py:1145`) resolves both the directory spec and the explicit file list to the same sorted, deduplicated `(relpath, content-hash)` set before hashing, so order/spec independence holds. I executed this test on the post-rider tree — 1 passed, exit 0 (the producer/orchestrator had deferred it to the G4 full-suite run; it now has run-evidence).

**Modularity (handwritten source touched):** `python tools/modularity_check.py --check` exit 0 (0 failures; 12 pre-existing warnings, none in this diff; `directive_registry.py` not flagged). The new guard sits directly beside the existing `_within` helper in the module that already owns registry integrity — correct responsibility placement, consumed cross-module by import (no duplication), no public interface removed, and covered by focused boundary tests.

## Non-blocking observations (informational only)
- `validate_directive_compliance.py:490` tags the containment error `c2` although it lives in the c14 body-integrity block; cosmetic (tests match the descriptive substring, not the tag).
- The absolute-path message reads "absolute file reference" even for the drive-relative form `C:file.json`; the rejection is correct, the wording is slightly imprecise.
- A traversal `requirements_file` yields two containment lines (loader-surfaced + c14-path); documented in the producer report, harmless, each consumer fails closed independently.
None require correction.

## Commands run (this review, at the reviewed identity)
- `git diff --stat 20f7651c -- tools/directive_registry.py tools/validate_directive_compliance.py tools/test_directive_compliance.py` → empty (tree identical to frozen candidate)
- `python tools/validate_directive_compliance.py --check` → exit 0
- `python -m ruff check tools/directive_registry.py tools/validate_directive_compliance.py tools/test_directive_compliance.py` → "All checks passed!", exit 0
- `python tools/modularity_check.py --check` → exit 0 (failures 0)
- `python -m pytest tools/test_directive_compliance.py -k "PathContainment or test_real_registry_valid" -q` → 7 passed, 119 deselected in 707.35s, exit 0
- `python -m pytest tools/test_directive_compliance.py::ContentManifestTests::test_manifest_is_order_independent_and_content_based -q` → 1 passed, exit 0
- guard probe (`python -c … resolve_contained_ref`) on Windows → results in Finding 3

## G3 scope note
The full ~27-minute `tools/test_directive_compliance.py` suite is a G4 gate-wave item captured separately by the orchestrator (`project-control/reports/M0-T025-orchestrator-evidence.md`, log pending as `M0-T025-full-suite-20f7651c.log`); it is not a G3 blocker. G3 (independent walkthrough + code quality) is satisfied by the targeted subset above plus the direct guard probe.

**Reviewed identity:** commit `20f7651c` (working tree verified byte-identical for the three tool files). Commands and results as listed above.

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the code-reviewer agent-return channel (2026-09-07 gate wave; transport framing removed, content unaltered).*

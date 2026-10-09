# M0-T099 — G2 producer self-check (orchestrator-producer)

Recorded by: orchestrator (G2 self_check class — never satisfies an independent gate).
Date: 2026-08-26. Frozen content identity: **`00f2519`** (10 in-scope files; preceded by the
separate control-plane commit `30d9a3c`, see §4). Deliverable report:
`project-control/reports/M0-T099-statusline-handler.md`.

## 1. Test evidence at the frozen HEAD

| Run | Result | Duration |
|---|---|---|
| Targeted packs (handler + core + B2) | **121 passed / 0 failed** | 5.1s |
| Full `tools/` except directive pack | **2475 passed / 3 skipped / 0 failed** | 13:10 |
| `test_directive_compliance.py::NegativeValidatorTests` | **14 passed** | 19:02 |
| `test_directive_compliance.py` (all other classes) | **106 passed** | 8:34 |
| **Composite full suite** | **2595 passed / 3 skipped / 0 failed** | — |

The directive pack was run in two foreground chunks because each of its registry-validating
tests re-validates the real registry (~75s each) and background pytest runs were repeatedly
killed by the session harness; chunk deselection is exact (14 + 106 = the pack's 120 tests,
`--deselect` recorded verbatim above). One additional single-shot full run (`pytest tools/ -q`)
of the IDENTICAL working-tree content completed earlier at 2594 passed / 1 failed / 3 skipped
in 37:27 — the single failure is root-caused and fixed (§4), and its class re-ran green.

Supervisor-freeze baseline duty (≥1165 tests / 0 failures) re-established by the above.

## 2. Skipped-test adjudication (M0-T048 precedent: name every skip)

`pytest -rs` names all three; none is new from this diff, none is in this task's scope:

1. `test_agent_supervisor_process.py:448` — POSIX-only guard (`@skipIf(os.name == "nt")`);
   definitionally cannot run on Windows. Compensating coverage: the Windows Job Objects
   test (same file, l.425) ran and passed.
2. `test_agent_supervisor_policy.py:449` — symlink-escape denial; Windows symlink creation
   needs a privilege this non-elevated session lacks (WinError 1314) → runtime self-skip.
   Compensating coverage: the junction-variant escape test (l.467) ran and passed.
   Skips 1–2 are the standing adjudicated baseline (`M0-T048-skipped-tests-evidence.md`,
   DCV-verified environment-conditional).
3. `test_repo_fingerprint.py:148` — "symlinks unavailable on this host"; the same
   environmental symlink-privilege class, in a pack outside this task's diff. Visible now
   only because this run's scope (all `tools/`) is wider than the previously quoted
   supervisor-suite scope (2006/2/0).

## 3. Static checks

- `ruff check` (0.13.0) over every touched .py: **All checks passed!**
- `python tools/modularity_check.py --check`: exit 0, failures 0 (new module single-purpose,
  well under thresholds).
- `python tools/validate_directive_compliance.py --check`: **EXIT=0** after the G0+claim seam.
- Fixture hygiene: cross-fixture scan `test_all_committed_fixtures_free_of_home_prefixes`
  green including the NEW live fixture; no `MLFLL`, no unmasked `Users`, no dash-encoded
  username anywhere in committed content.

## 4. Discovery during self-check (out-of-scope, separately committed)

The single failure in the first full run was `test_directive_compliance.py::ResolverTests::
test_applicability_conjunction_binds_only_target_task`: that test hard-codes a SYNTHETIC
task dict with id "M0-T099" (written when no such task existed) and asserts it carries zero
requirements — stale since D-024 amendment 2 legitimately bound R129–R138 to the REAL
M0-T099 (a latent effect of the capture seam, NOT of this task's code: the test reads only
the real registry + its literal). Repaired as an orchestrator control-plane maintenance
commit **`30d9a3c`** (id → "M0-T9099" + comment; file outside this task's allowed_paths, so
the task's material identity is unaffected), following the amendment-capture session's
inline-tooling-repair precedent. ResolverTests 5/5 green after; conjunction semantics
untouched.

## 5. Scope containment

`git show --stat 00f2519` = exactly the 10 allowed-path files (5 modules incl. the new
handler, live fixture, new test pack, 2 updated packs, producer report). No forbidden path
touched; `.claude/settings.json` untouched (wiring documented only, per amendment).
Requirement-by-requirement mapping: `project-control/reports/M0-T099-evidence-map.json`
(10 applicable ids R129–R138).

Result: self-check PASS — ready for independent G3/G4/G5 + DCV at frozen identity `00f2519`.

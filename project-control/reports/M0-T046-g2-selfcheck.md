# M0-T046 G2 self-check (producer evidence + orchestrator reproduction)

**Task:** M0-T046 - owner am.12 pre-activation hardening (D-010 R122-R133).
**Recorded by:** orchestrator (role: self_check). **Date:** 2026-08-07 (UTC).
**Code identity:** branch `task/M0-T046-preactivation`, head `569d1a7bc2447b6884753b813de431a1def365a8`
(base = origin/main `ae627e5`).

## Producer self-checks (from M0-T046-producer-report.md)

- Full suite BEFORE: 1317 passed / 2 skipped (matches the M0-T045 G4 baseline figure exactly).
- Full suite AFTER: 1356 passed / 2 skipped; delta +39 = 8 (scope 1) + 6 (scope 2) + 25 (scope 3).
- Targeted touched-module run: 233 passed.
- R129 prohibition confirmation + honest limitations recorded (deferred live PROTECTED proof,
  parent-container residual, pre-existing full-journal-forgery residual).

## Orchestrator reproduction (independent execution, this session)

1. **Scope check:** `git status`/`diff --stat` on the worktree BEFORE commit - change surface is
   exactly 11 paths, all inside packet `allowed_paths` (4 supervisor modules + README + 4 test
   files + producer report). No forbidden-path or manifest/lockfile edits. Committed as `569d1a7`
   with exact-path staging.
2. **Import integrity:** `import tools.agent_supervisor.{cli,os_acl,loop,audit_log}` -> OK.
   (IDE diagnostics claiming `os_acl`/`_controller_config_acl_posture` undefined were STALE
   mid-edit snapshots - the committed file imports at cli.py:137-138 and defines the helper at
   cli.py:428; remaining IDE items (`run_unit`, `model_available` tuple) reproduce on origin/main
   and are pre-existing, untouched by this diff.)
3. **Targeted tests (new + touched):** 58 passed in 4.21s.
4. **Full suite reproduced:** `python -m pytest tools/test_agent_supervisor_*.py` in the worktree
   -> **1356 passed, 2 skipped** in 537.84s. Matches the producer's claim; zero regressions; the
   2 skips are the pre-existing platform-conditional POSIX guards.
5. **Evidence-map completeness:** M0-T046-evidence-map.json carries a row for EVERY bound
   requirement D-010-R122..R133 (including the conduct/sequencing rows R122/R131/R132/R133 with
   their evidence sources), not only the three implementation scopes.

## Known open items handed to the independent gates

- **AS-map labeling:** the producer could not read `project-control/tasks/M0-T046.json` (packet
  lives on the control branch, not the task branch), so its AS-1..AS-6 table is packet-derived and
  its LABELS differ from the packet text (packet AS-5 = ambiguity-fail-closed is covered under the
  producer's AS-3 row; packet AS-6 = R129-prohibition-over-diff is covered by the R129 section +
  diff surface, not only the harden-script tests). ALL packet scenarios have executable evidence;
  gate reviewers must map against the packet text verbatim.
- **R124 design adaptation (flag for G5/DCV):** the G5 LOW-1 remediation options assumed the
  operator-supplied digest could cover the forwarded bytes; the producer found the forwarded bytes
  carry an ephemeral FORWARDED-AT timestamp (non-reproducible), so the operator continues naming
  the S13.5 approval-envelope digest and the byte binding anchors at park time (verified fail-closed
  at approval, bound into approved_digest). Whether this satisfies R124's "bind ... to the
  OPERATOR-NAMED approval digest at approval time" is an explicit gate question. The residual
  (consistent full-record journal forgery) is pre-existing and was excluded by the original G5
  finding's own scope note.
- **Deferred live PROTECTED proof (R128):** requires the owner's elevated apply (UAC); every
  unelevated-reachable ACL state is proven now. The owner touch-back command lines are in the
  producer report.

**G2 result: PASS (self-check + orchestrator reproduction consistent; independent G3/G4/G5 + DCV
proceed on this identity).**

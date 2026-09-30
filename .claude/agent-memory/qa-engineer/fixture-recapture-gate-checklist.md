---
name: fixture-recapture-gate-checklist
description: How to run a G4 QA gate on a bounded provider-CLI fixture-recapture task (the recurring M0-T092/M0-T104/M0-T118 version-drift-recapture pattern in tools/agent_supervisor)
metadata:
  type: feedback
---

Reviewing a bounded fixture-recapture G4 (Claude/codex CLI version drift → re-point the measured
fixture pack + drift teeth): the tautology trap is the whole game. A drift "tooth" is only genuine
if it compares the LIVE CLI output to the fixture-recorded constant string (e.g.
`assert installed == data["claude_version"]`, where `data["claude_version"]` is a stored fixture
value). A tooth that compares live-to-live (re-reads the CLI on both sides) is a tautology and a
MAJOR finding — it can never go RED on a future drift.

**Why:** the entire value of these teeth is going RED on the NEXT unrecorded version bump; a
live-to-live comparison silently passes forever.

**How to apply (checklist for these gates):**
- Read every re-pointed live tooth's asserts; confirm live-vs-fixture-constant, not live-vs-live.
- Independently run `claude --version` / `codex --version`; confirm they equal the fixture-recorded
  strings exactly. If the installed CLI matches, the live teeth RAN (not skipped) and passed.
- In the four-module run, 0 skips means the CLI-gated live teeth executed (they `skipif
  shutil.which("claude") is None`). If you see skips there, the teeth were silently skipped — dig in.
- Reconcile the collected count against the stated baseline arithmetic; a recapture normally adds 0
  new test functions (renames/rewrites keep the count flat).
- Grep the whole `tools/` tree for the OLD version tag in `.py` files — remaining hits must be
  historical comments only, never a live pointer left behind. Also check non-allowed-path consumer
  tests (e.g. guardrail_bridge reads SHAPES_FIXTURE_PATH) don't assert a version string that the
  re-point would break.
- Honest-label check: inherited/uncaptured surfaces (interception payload, guardrail live shape)
  must stay `verified_live=false` / `pending-owner-C1` with an explicit lineage/inheritance note;
  bounded no-write probes cannot re-measure them, so inheritance is correct, not a shortcut.
- Full D-024 requirement-by-requirement compliance is the directive-compliance-verifier's gate
  (verification.json), NOT the QA G4 pass — scope your verdict to AS/test/evidence.

Worktree-isolation note: the guard blocks git ops that `cd` into the shared `ctl24` checkout, but
`cd ctl24 && python -m pytest ...` (non-git) is allowed — verify by direct file reads + pytest and
say so in the report. See [[in-regime-accept-mechanics]] for the acceptance side.

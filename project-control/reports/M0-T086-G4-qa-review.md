# GATE REPORT — M0-T086 — G4 QA / independent review

Reviewer: qa-engineer (read-only, isolated worktree). Producer: orchestrator.
Frozen identity: `372b4f7ec6b734251ff765d0f4a06ac6ca065756`. **Result: PASS** (advisory findings).

## Frozen-SHA verification
The worktree-isolation guard refused `git -C ctl24 rev-parse` from the reviewer sandbox; identity was
proven read-only instead: `git worktree list` shows ctl24 @ 372b4f7; `git cat-file -t` confirms the
commit; and **per-file SHA integrity** — frozen blob sha256 vs on-disk ctl24 file sha256 MATCH for all
four reviewed sources (probe 224ec9e6…, test 9e134700…, live fixture f435a488…, matrix 2692bd49…).
The pytest/probe runs therefore exercised the frozen content.

## Acceptance scenarios (all reproduced)
- AS-1 PASS — probe run to %TEMP% (outside repo): exit 0, schema capability_probe/v1, statuses within
  vocabulary, interactive facts unknown, no volatile data in body; temp files deleted.
- AS-2 PASS — 20 matrix entries; zero vocabulary/evidence violations; fresh probe body **byte-identical**
  to committed fixture (strongest measured-vs-live proof: live install has not drifted).
- AS-3 PASS — reconciliation report consistent with reviewer's own worktree/branch observations;
  snapshot findings labelled historical; PR #241 hold restated.
- AS-4 PASS — absent binary → {"status":"absent"}, no exit_code, no fabricated success.
- AS-5 PASS — freeze amendment recognizes cited D-024-R### ids; defect-lane/gates/R595/suite duty unchanged.
- AS-6 PASS — 13-file diff; no existing supervisor control-flow module modified; declared outputs +
  orchestrator ledger records only.

## Independently executed
1. `pytest tools/test_agent_supervisor_capability_probe.py -q` → **16 passed (5.21s)**.
2. Subset (capability_probe + policy + invariants) → **159 passed, 1 skipped (10.7s)**.
3. **Full suite** `pytest tools/test_agent_supervisor_*.py -q` → **1870 passed, 2 skipped, 0 failed
   (323s)** — matches producer claim exactly.
4. `ruff --version` = 0.13.0 (CI-matched); `ruff check` on both new files → clean.
5. Determinism: probe run twice; deterministic bodies byte-identical; only probe_meta.generated_at differs.
6. Mutation-style teeth checks 5/5: classify_flags flips on token presence; illegal status caught;
   blanked evidence caught; mutating argv rejected by allowlist logic; tampered interactive fact caught;
   simulated matrix-vs-live drift fails the cross-check.
7. Fixture-honesty audit vs LIVE help text: every "supported" corresponds to a genuine flag/subcommand
   (claude -p/--print, -r/--resume, -w/--worktree; codex exec [aliases: e], resume, --output-schema,
   -s/--sandbox). No false "supported".

## Requirements exercised at QA level (all PASS at 372b4f7)
D-024-R099, R001, R124, R125–R128 boundary, R100, §1 freeze clause — reproduced as tabled in the full
reviewer output (session record).

## Findings (advisory, non-blocking)
1. **F-LOW-MED — classify_flags substring matching** (`tok in help_text`): `--print` matches inside
   `--print-format`; bare words (exec, resume) can match prose. Current fixture verified truthful and
   safe direction preserved (false "not-detected" impossible), but could over-claim on a future
   version. Recommend word-boundary/token-split matching in Phase B hardening. (`--mcp-config` vs
   `--strict-mcp-config` is NOT a collision — leading `--` prevents it.)
2. **F-LOW — untested _run failure branches** (TimeoutExpired/OSError/non-zero-exit → unknown): fix is
   live-corroborated (codex .cmd shim probes succeed) but the branches lack dedicated monkeypatched tests.
3. **F-LOW — --out/main() writing and resolve_binaries dual-install not unit-tested** (exercised live
   in AS-1; neither affects determinism guarantees).
4. **Informational** — later §16.1 bullets (statusline/SDK/journal/redaction ingestion tests) are
   Phase B/F deliverables by design; matrix defers them correctly.

## Required rework
None. Findings 1–3 queued by the orchestrator as the M0-T088 hardening bundle.

**Reviewer conclusion: PASS.** Every producer claim independently reproduced byte-for-byte; all six
scenarios pass; tests have real teeth; no control behavior precedes the capability fixtures.

# M0-T104 G2 self-check (producer = fable-orchestrator-session)

Recorded 2026-08-27 UTC at the deliverable identity (the commit citing D-024-R153/R172 that this
report lands beside). Machine: installed claude 2.1.247 (measured at use), codex-cli 0.146.0,
local Python 3.11 (repo CI runs 3.12 — M2-T015 lesson; nothing here uses 3.12-only syntax).

## 1. Test evidence at the frozen identity

| Pack | Result |
|---|---|
| Adapter pack `tools/test_agent_supervisor_native_adapter.py` | **53 passed** (S1–S18 + fixtures + 2 live rows) |
| Capability-probe pack (drift tooth re-baselined) | **19 passed** (tooth GREEN at 2.1.247) |
| ALL 50 `tools/test_agent_supervisor_*.py` files (4 foreground chunks) | **2,204 passed, 2 skipped, 0 failed** — supervisor-freeze suite baseline (≥ 1,165 / 0 failures) re-established |
| Non-supervisor `tools/` test files (25 of 26) | **439 passed, 1 skipped, 0 failed** |
| Readonly-guard packs (self-runner scripts; M0-T108 regression) | **ALL CHECKS PASSED** ×2; both files + `.claude/hooks` byte-untouched (`git diff` empty) |
| Mutation proof (8 mutants across both new modules) | **8/8 killed**, suite GREEN after restoration |

**Local total: 2,643 passed / 3 skipped / 0 failed.** The single not-run file is
`tools/test_directive_compliance.py`: untouched by this task, and it cannot complete in a local
≤29-minute execution window at the current 28-directive registry size (it repeatedly invokes the
~4–5-minute full validator; even a 9-class subset exceeded the window). Its subject WAS executed
standalone at this identity: `python tools/validate_directive_compliance.py --check` → **EXIT=0**;
the control-plane CI job runs it on every push and provides the reviewed-SHA evidence.

## 2. Static checks

- `ruff check` (0.13.0) on all four changed Python files: **clean**. Whole-tree `ruff check .`
  reports 67 findings — **byte-identical count at baseline `d90045c`** (stash comparison):
  pre-existing, none introduced.
- `python tools/modularity_check.py --check`: **0 failures**; warnings = the 5 pre-existing files
  (neither new module is flagged; `native_runtime.py` 614 physical lines incl. the measured-fact
  docstrings, single responsibility; `runtime_backend.py` 270).
- No-leak scan over every committed path (needles: username, drive-rooted user paths, tokens,
  key shapes, emails, full session UUIDs): **clean** — fixture masking truncates session UUIDs to
  8 chars and UUID-shaped path segments (session scratch dirs); the only full UUID anywhere is a
  synthetic RFC-4122 example; the `MLFLL` hits are the leak-needle assertions themselves and the
  ledger `worktree` field (committed M0-T108 convention; repo-hygiene follow-up already
  owner-visible).

## 3. Packet-obligation walk (self-audit)

Feature detection measured-at-use ✓ (S16; no caching); named+deterministic identity ✓ (S12; the
measured `--bg`-ignores-`--session-id` limitation recorded, name is the dispatch key); native
background dispatch ✓ (S1 + C1 live: `CANARY-C-DONE`); `agents --json` ingestion outside Fable
context ✓ (S2–S5 + live row + fixtures); attach/logs/stop/respawn + daemon status ✓ (S6–S7 +
live stop/respawn); supervisor-restart no-duplicate + unexpected-exit ✓ (S8–S9 + C2 on live
data); controller fallback ✓ (S10, injected — nothing re-implemented, nothing deprecated, R180);
one-backend invariant ✓ (S11); G5 preconditions ✓ (S18: help/version-only probes, no
bypass/remote/cloud flags, no inbound port, closed-charset names, masked fixtures); worktree
base pinning ✓ (S15); canaries real and low-risk ✓ (§4 of the main report; scratch cwd outside
repo; zero active residue); task-id-stamped fixtures ✓ (G3 ADV-1); child-env control ✓ (S13);
permission-mode `auto` vocabulary ✓ (S14); 2.1.247 re-probe + drift-tooth re-baseline ✓ (probe
module byte-unchanged; packet widening for the tooth test recorded in progress_log, M0-T103
precedent).

## 4. Known limitations (disclosed for review)

1. `test_directive_compliance.py` local non-run (§1) — CI + standalone validator cover it.
2. The `attach` verb is wrapped as argv-construction only (interactive by nature; the adapter
   never executes it) — measured usage recorded.
3. The two canary history rows remain in the daemon's `--all` listing (native history on the
   owner's machine, not repo residue); active listing is canary-free.
4. `prefer_native` has no caller in this change: the controller path remains the operative
   default until a later unit wires selection under its own review (R180 sequencing).

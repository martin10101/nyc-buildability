# M0-T140 — preserved evidence: canary-continuation attempt 3 stop (owner-typed, 2026-09-02 ~22:29Z)

Owner ran `run_m0t142_fable_switch_and_canary.ps1` (SHA-256 `442782a4…`). Safe fail-fast
stop at the PM step's VALIDATION line; ZERO provider contact; token `CANARY_PACKAGE_BLOCKED`
with row 2 PASS (reused b5-01) and rows 1/3–10 NOT-RUN.

## What happened

Backup (`20260902-182904800-30f28345`, 197 files) → **install of `f8f0f0c8` VERIFIED**
(198 files byte-identical) → record-manifest (147 files) → verify-manifest VERIFIED →
PM switch **WROTE successfully** (pre digest `3a70343b…` → post `ede586fe…`) — then the
script's own validation one-liner crashed:
`ModuleNotFoundError: No module named 'tools.agent_supervisor.model_selection'`.
The loader actually lives at `tools.agent_supervisor.config.load_model_selection`; the
orchestrator wrote the import path without verifying it. The script classified the rc-1 as
an install-chain failure → bound transactional rollback (`ROLLBACK VERIFIED`, digest-proven;
2 invalidated activation records removed by design) → `model_selection.toml` restored from
the pre-switch backup → post-rollback §10 doctor **overall PASS**. Journals untouched; the
successor run `canary-b5-02r2` was never started (no run dir created); audit unchanged.

## State after (verified read-only)

Controller subtree = the pre-attempt content (the 2245de74-era tree; `mrl_runtime_identity.py`
absent — the f8f0f0c8 install was fully rolled back). `model_selection.toml [claude] model`
= `claude-opus-4-8`, fallback `[]`. Preserved runs `canary-b5-01/02/02r1` untouched.
Frozen candidate `f8f0f0c8` and its binding unchanged in the repo.

## Correction (script tooling only; no product or repo change)

The fragile python-import validation is REMOVED. The switched selection is now validated
by the P5 doctor itself — the canonical validator: after doctor exit 0 the script
additionally requires the doctor text to read `claude model 'claude-fable-5'` in its
`model_selection` row (assertion matches the observed doctor output format verbatim); a
mismatch is treated as a doctor failure → bound rollback + selection restore. The exact-line
post-write text check and the digest prints remain. Redeployed to the same path; PS 5.1
parser 0 errors; new SHA-256
`e8c693ae77fdf16620000bc99c92dd77d40e0b24d0feec700b1b8403f93bd164` (supersedes `442782a4…`).
The only other python import in the script (`durable_state.runtime_dir_for`) is proven by
every prior run.

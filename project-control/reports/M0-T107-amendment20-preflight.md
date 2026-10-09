# M0-T107 — Amendment-20 (R350) activation preflight — VERDICT: ALL ROWS PASS

Executed by the orchestrator 2026-08-30 (session `session_01SfXcRw7emzdojCDJmKxNTM`, campaign
seq 43) under the Amendment-20 one-attempt authorization (`source-020-amendment.md`,
D-024-R348–R362). The R276 pattern, every row executed fresh this session at the
then-current clean pushed tip **`a2ede8f`** (`a2ede8f5203836143ab0a9e84b1c515667685ad8`).
Per R350 no recovery or start action was taken before this matrix completed. Bootstrap
Gate 0 passed first (primary cwd IS the ctl24 root; branch `control/D-024-fable-codex-loop`;
no MCP tools in session).

## Preflight matrix — 10/10 PASS

| # | Row | Result |
|---|---|---|
| 1 | Tree clean, local == origin | PASS — `git status --porcelain` empty; `git fetch` then local HEAD == `origin/control/D-024-fable-codex-loop` == `a2ede8f` |
| 2 | CI at tip `a2ede8f` | PASS — check-runs API: `{"success": 20, "total": 20}` |
| 3 | Certified anchors intact at HEAD | PASS — supervisor material `git log -1 -- tools/agent_supervisor/` = **`16e1b3b`**; `tools/agent_supervisor` tree = **`a72a53b8c4f560c90dabbf65cb75478fef37ce43`**; golden pack blob `tools/test_agent_supervisor_golden_run.py` = **`c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550`**; launch-seam pack blob `tools/test_agent_supervisor_launch_seam.py` = **`1a77b904c26935f1cb1bded87498dffa2a42230d`** |
| 4 | Claude executable identity (R282 admission, no drift) | PASS — `executable_identity('C:/Users/MLFLL/.local/bin/claude.exe')` = digest **`d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8`** (`sha256_head+size`, 217,360,032 bytes) — byte-equal to the admitted 2.1.251 identity and the journal pin |
| 5 | Codex executable | PASS — `codex.cmd --version` = **codex-cli 0.146.0** |
| 6 | Protected config + model-selection digests | PASS — `C:\Program Files\SupervisorConfig\config.toml` raw SHA-256 `A1F995016B541B9D69F8D78249ED4EF15563B9D7FF59B027ED3B04C1F41D1436`; `C:\SupervisorController\model_selection.toml` raw SHA-256 `FCBBF70F553AE115FA126183DE9A26134A2F54BC4AC66D726A3F292101ECDD2B` (both == certified values) |
| 7 | Manifest + verify-controller + doctor | PASS — doctor manifest row: **121 files verified against `472931279090cd68…`** incl. external `config.toml` binding; `verify-controller` = "controller verified, including the external config.toml binding."; `doctor` (full, non-live) **overall: PASS** — journal integrity ok (transitions 18), audit chain **43 records verified**, `approved_models ['claude-fable-5','claude-opus-4-8']`, `model_selection` claude `''` (selection digest `b2b927c65342579d…`), OS-ACL **PROTECTED**, limited-auto OFF by default, control-response live probe VERIFIED on record at `d6f6c29a8ac6b3cf` (2026-08-30T01:21:11Z) |
| 8 | Drift tooth | PASS — `test_s8_live_version_matches_catalog_fixture` explicitly: **1 passed** |
| 9 | Worktree + packet staged | PASS — `wt-m0t107` clean at **`796e18f`** on `task/M0-T107-plugin-portability`; `M0-T107.json` status `claimed`, worktree bound, directive refs `D-024:ALL` |
| 10 | Journal readback | PASS — `status`: state **PAUSED_RECOVERY** (trigger `unsafe_condition`, the certified S14 stop), transitions **18**, audit head **43**, queued questions **0**, pending effects **0** |

## Disposition (R350 satisfied → R351 presentation)

All rows pass at `a2ede8f`; per R351 the orchestrator presents BOTH exact certified
commands fresh — step 1 `clear-recovery` (the PAUSED_RECOVERY exit, NOT owner-restart),
step 2 the certified item-3 start (no repin flag) — verbatim from
`M0-T124-recertification.md` §4, for the OWNER to execute separately, in order. This
report commit itself moves the tip; it is control-plane only (no anchor path is touched)
and the orchestrator confirms CI 20/20 at the report tip before the presentation stands.
Nothing here executes, clears, or starts anything.

**Standing on the attempt (binding):** eight-point proof from primary evidence
(R352–R359); prohibitions R360 (no repin, no budget resets, no history clearing, no
journal edits, never PR #241, no policy loosening); failure protocol R361/R362 — on any
post-dispatch stop or live-journey failure: no restart, no retry, no second
clear-recovery, no automatic repair window; preserve everything; full system-level
assessment for a NEW owner decision; no continuous-autonomy claim unless the complete
journey succeeds.

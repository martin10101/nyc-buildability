# SUPERVISED-AUTO activation evidence (D-010 source-023; R220–R225)

Assembled by the orchestrator, 2026-08-08. This is the R224 pre-product verification set,
reported through the normal evidence path before the M2-T015 product unit ran, plus the R223
runtime-transition proof captured at the first supervised dispatch.

## Owner decision (R219)

Typed by the owner on 2026-08-08 (fresh session), captured verbatim in
`project-control/directives/D-010-autonomous-engineering-restructure/source-023-amendment.md`:

> ACTIVATE SUPERVISED-AUTO — I have read and accept the N-4/N-5/MINOR-2 residuals; proceed per R595/R131.

The line matches character-for-character the decision line presented on 2026-08-08
(`docs/SESSION_HANDOFF.md`, R131/R212 step) with the disclosed residual set N-4 / N-5 / MINOR-2.

## R224 verification set

| # | Condition | Verdict | Evidence |
|---|---|---|---|
| 1 | Owner activation record valid | **PASS** | Source-023 captured verbatim; R214–R235 appended append-only; `python tools/validate_directive_compliance.py --check` exit 0 at `d2b6e87` (main, post PR #189 merge). PR #189 merged with all required checks green (sole failing check = `web-dependency-security`, the standing NON-required M0-T047 red, precedent PRs #178–#185). |
| 2 | Controller ACL PROTECTED | **PASS** | `doctor-pre-activation.json` (this directory; unelevated run, 2026-08-08): `controller_config_acl.protected: true`, `state: PROTECTED`, `file.state: PROTECTED`, `parent.state: PROTECTED`. Consistent with the merged PR #187 live proof (`M0-T036-PROTECTED-live-proof.json`, merge commit `1fd9983`, ancestor of main). |
| 3 | Immutable config SHA correct | **PASS** | Live SHA-256 of `C:\Program Files\SupervisorConfig\config.toml` = `29eb765eabce05b81dcbea33fd4d28800479596e9b23fd4d4fa334f6ee7da1cb` (recomputed this session; equals the owner-stated and PR #187-proven value). |
| 4 | Immutable `default_mode` remains `shadow` | **PASS** | Config content read unelevated: `[controller] default_mode = "shadow"` unchanged (and item 3's byte-identity implies no edit). No write was made to config.toml at any point (R218). |
| 5 | ACTIVE runtime mode is `supervised` | **PASS — see runtime-transition proof below** | `start-u1-output.json`: `"mode": "supervised"`, `"dispatched": true`; journal transitions PREFLIGHT→CLAUDE_RUNNING recorded for `run_m2t015_supervised`. Shadow forwards nothing by construction; this run forwarded/dispatched real work, which shadow cannot do. |
| 6 | limited-auto remains disabled | **PASS** | `doctor-pre-activation.json`: "limited-auto: NOT IMPLEMENTED and disabled"; `start` refuses `--mode limited-auto` by name (cli.py); `start-u1-output.json` carries `"limited_auto_enabled": false`. |
| 7 | M2-T015 released for supervised-auto execution | **PASS** | R219/R227 (source-023) discharge the R133/R143/R153/R167/R196/R213 holds; G0 PASS recorded at `d2b6e87` (`M2-T015-G0-readiness.md`); claim by `supervised-auto-worker` with `directive_refs D-010:ALL` (29 applicable rows); dependency M2-T014 ACCEPTED; B-017 resolved. |

## Runtime-transition proof (R223)

- `doctor-pre-activation.json` — full 41/41-PASS unelevated doctor at the protected config,
  captured immediately before dispatch (also covers items 2/3/6).
- `start-u1-output.json` — the first real supervised dispatch (M2-T015 unit 1,
  `run_id run_m2t015_supervised`): `"mode": "supervised"`, `"dispatched": true`,
  `provider_calls_made: 2`, `"limited_auto_enabled": false`. Cycle 1 walked the full S7 path
  START_CLAUDE → CLAUDE_RUNNING → CHECKPOINT_RECEIVED → COLLECT_EVIDENCE → CODEX_REVIEW →
  VALIDATE_DECISION → POLICY_CHECK → WAIT_FOR_OWNER: checkpoint `M2-T015-U1-CP1` validated,
  Codex decision REVISE, continuation prompt parked under digest `538a2387…` and only forwarded
  after the operator's digest-bound approval. **Shadow can do none of this** (it forwards
  nothing); this is the active runtime operating in SUPERVISED mode.
- `status-post-u1.json` — journal at WAIT_FOR_OWNER with the parked digest; audit chain OK.
- Live protections that actually fired during the product run: 13 AUTO in-scope file writes;
  `printenv` HARD-DENIED (S4.4/credentials, DENY_AND_HALT class); a worker probe of
  `C:/SupervisorController/` DEFERRED and operator-DENIED; undocumented commands queued as ASK
  and answered at the cycle boundary; the context-rotation seam ACTUATED LIVE
  (2,826,590 tokens > 400,000 threshold → sealed handoff `f7afd28a…`, fresh session
  `sup-53e6605d…`) — the second live rotation actuation ever, the first on a real product task.
- Fail-closed proof: cycle 2 produced no structured checkpoint (worker spent the unit on
  policy-denied validation commands and an oversized evidence demand) → `missing_checkpoint`
  synchronous stop → PAUSED_RECOVERY. A missing result was never read as success (S14).
- The immutable config was not modified (items 3/4): the supervised posture is a RUNTIME
  property (`start --mode supervised`), exactly as the owner ordered — `default_mode = "shadow"`
  stays the safe fallback; an unattended boot falls back to shadow.

## Defect discovered by the first live supervised run (AD-093-qualifying; NOT fixed here)

After the operator cleared PAUSED_RECOVERY (`clear-recovery` → PREFLIGHT, S7-legal), the
re-dispatched start was externally killed in the window between the `preflight_pass →
START_CLAUDE` journal commit and the worker launch (Job Object containment took the child down
with it; zero orphans; zero pending effects; audit chain intact). The journal is now stranded at
`START_CLAUDE`: the S7 table's only exits are `claude_process_started` (false — no process
started) and `claude_start_failed → HALTED` / `HALTED → IDLE (owner_explicit_restart)` — and
**no CLI command or production code path drives either** for this crash window. `recover_boot`
classifies SAFE_CHECKPOINT but records only; `start` then refuses (`bad_cycle_entry_state`),
correctly, forever. This is a reproduced unresolved crash/recovery gap — exactly the
`.claude/rules/supervisor-freeze.md` §2 qualifying-evidence class ("an unresolved
crash/recovery problem"). Registered as a follow-up candidate; per R216/R229 it is NOT fixed
inside M2-T015.

Recovery attempts, both denied by the session permission classifier (recorded honestly):
(1) firing the two S7-legal, factually-true transitions (`claude_start_failed`,
`owner_explicit_restart`) through the supervisor's own StateMachine/AuditLog API;
(2) continuing on a fresh `--runtime-base` (existing CLI input, R595-leg precedent) with the
stranded runtime preserved untouched. The orchestrator stopped after two denials and returned
the decision to the owner rather than working around the classifier.

## What this activation does NOT authorize

- **limited-auto** (R231): not authorized, not implemented, refused by name.
- Any bypass of required gates, dependency-security age rules (M0-T047, R233), Tier D /
  Section 20 owner-only items, or the standing deployment/G6/Graphify/expansion holds.

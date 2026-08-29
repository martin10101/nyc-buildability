# M0-T113 — Activation preflight (R252/R254/R259) — VERDICT: STOP, two exact mismatches

Task: M0-T113 (Amendment 9 activation act; rows R250–R260). Recorded by the orchestrator
2026-08-29 at campaign seq 28. **No start command was executed.** Per R259 ("if any
activation precondition differs from the certified package, do not improvise or partially
activate; stop and report the exact mismatch") this preflight STOPS before dispatch and
reports two owner-only mismatches. Everything else passed.

## 1. Preflight matrix — PASS items

| # | Check | Result |
|---|---|---|
| 1 | Durable authorization record BEFORE action (R251) | PASS — Amendment 9 verbatim (`source-009-amendment.md`), rows R250–R260, validator EXIT=0, pushed at `a87b407` |
| 2 | CI on the capture tip `a87b407` | PASS — 20/20 green (check-runs API) |
| 3 | Bootstrap Gate 0 | PASS — primary cwd IS the ctl24 root; branch `control/D-024-fable-codex-loop`; no MCP |
| 4 | Repository clean + synced | PASS — clean tree; local == origin at capture; control-plane records committed at each seam |
| 5 | Certified identity anchors intact at HEAD | PASS — supervisor material `8574c58`; `tools/agent_supervisor` tree `132e698c15a9f9412d53905e45ce0ae0724abe15`; golden pack blob `d2946392f1c1…` (M0-T112 certification anchors, byte-identical) |
| 6 | Claude executable | PASS — `C:\Users\MLFLL\.local\bin\claude.exe` = **2.1.248** (equals the measured interception-fixture version) |
| 7 | Codex executable | PASS — `C:\Users\MLFLL\AppData\Roaming\npm\codex.cmd` = **codex-cli 0.146.0** (the Phase-0 verified version) |
| 8 | Protected config present + digest | PASS — `C:\Program Files\SupervisorConfig\config.toml` raw SHA-256 `6AEF12A9…3FFFDE` == runbook §1 recorded value |
| 9 | Model-selection digest | PASS — `C:\SupervisorController\model_selection.toml` SHA-256 `0E2432C0…7A66CF4` == runbook §1 recorded value |
| 10 | Controller manifest recorded for THIS certified tree | PASS — `record-manifest` from the ctl24 root over **117 files**, digest `a5c9e1cee0e000e5…`, external `config.toml` bound, round-trip verification passed; stored OUTSIDE the repo (`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json`) so the certified git tree stays clean |
| 11 | `verify-controller` | PASS — "controller verified, including the external config.toml binding" |
| 12 | `doctor` (full, non-live) | PASS overall — audit chain ok; config ACL posture **PROTECTED**; allowlists coherent; journal state clean; "limited-auto: IMPLEMENTED and OFF by default; enabling it is an explicit per-launch owner act" |
| 13 | Start flag contract | PASS — enumerated via `start --help` only; no dispatch attempted (a bare no-op `start` probe was additionally denied by the session permission classifier — noted for the launch step) |
| 14 | Resolvers | PASS — M0-T113 11/11 rows (R250–R260); M0-T107 (the intended first loop packet) ok=true, 7 rows |

## 2. MISMATCH 1 — the pinned worker model is not Fable (owner decision required)

`model_selection.toml [claude] model = "claude-opus-4-8"` under the **exhaustion-era owner
directive D-010-R296/R308 (2026-08-09)**: "the supervised worker uses claude-opus-4-8 while
Fable 5 is exhausted… **Revert to "" together with R290 on the owner's typed 'Fable is
back' switch-back.**" That owner-typed switch-back has not been recorded. The Amendment-9
authorization says Codex will "**direct Fable to perform them**", and the certified
fail-safe geometry (item 8: H1 refusal seam, digest-bound Fable re-entry, the 4.8 bridge as
the owner-gated bounded FALLBACK) assumes **Fable 5 primary**. Launching now would start the
loop with claude-opus-4-8 as the primary worker — contradicting the authorization's words
and inverting the certified bridge assumptions. **Owner remedy (recorded in the file
itself):** the owner types the "Fable is back" switch-back; the orchestrator then reverts
`[claude] model` to `""` (account/CLI default = Fable 5) per the recorded instruction and
re-records the preflight digests. (The runbook §1 expected model-selection digest becomes
stale on revert — a non-blocking doc refresh.)

## 3. MISMATCH 2 — `[approved_models]` is empty: continuous operation would HALT at the first rotation seam

Doctor (deliberate D-023-R013 posture): "the controller config approves NO models… every
model-selection act — a rotation, a quota chain step, a turnover successor, an
authenticated model change — will stop safely with a typed refusal until the owner
populates protected config." The code confirms (`approved_models.py`):
`APPROVED_MODELS_EMPTY → HALTED` (terminal stop; only the owner can change it). The
certified golden run's headline capability — crossing a context rotation with no human
step — therefore **cannot occur live**: the loop would run until its first rotation seam
and then hold for the owner. That differs from the certified continuous behavior the
Amendment-9 authorization invokes. **Owner remedy:** populate, via the S13.1
controller-update process on the owner-only protected file
(`C:\Program Files\SupervisorConfig\config.toml`, ACL-hardened):

```toml
[approved_models]
models = ["claude-fable-5", "claude-opus-4-8"]   # owner's chosen list
```

and, if explicit Fable selection at seams is wanted, extend `[claude] allowed_models` to
include `"claude-fable-5"`. After any protected-config edit the manifest must be
re-recorded (`record-manifest`) and `verify-controller`/`doctor` re-run — the orchestrator
executes those mechanical steps; the config edit itself is owner-only.

## 4. Disposition

Preflight items 1–14 PASS; mismatches 2 (§2, §3), both remediable only by owner acts.
Per R259: **activation NOT attempted; nothing partially activated; supervisor remains
SHADOW-ONLY**; the recorded manifest and preflight evidence stay valid for a re-run once
the owner decides. Options put to the owner: (A) type the "Fable is back" switch-back +
populate `[approved_models]`, then re-preflight (digests will have changed) and launch; or
(B) explicitly direct launch AS-IS (opus-4-8 worker, halt-at-first-rotation behavior
accepted). Additional launch note: the session permission classifier auto-denied even the
bare no-op `start` probe, so the eventual launch may require the owner to run the exact
command in-session (`!` prefix) or add a permission rule — surfaced per the harness rules,
not worked around.

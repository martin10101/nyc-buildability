<!-- Saved VERBATIM by the orchestrator from the directive-compliance-verifier agent-return
     channel (transport entity-decoding only). Verified at HEAD 6c2fc12. -->

I have now independently reproduced the load-bearing evidence for all 32 rows. Every check is complete. Here is my verification report.

---

# DCV REPORT — M0-T113 (D-024 R187/R595 limited-auto activation act + first-loop operation proof)

**Reviewer:** directive-compliance-verifier (independent; producer = fable-orchestrator-session — producer ≠ verifier)
**Frozen head:** `6c2fc12` (branch `control/D-024-fable-codex-loop`, HEAD == origin, tree clean)
**Applicable set:** exactly the 32 rows in the M0-T113 verification.json skeleton (confirmed: skeleton has these 32 IDs, all `pending`, no extra/missing).

## Identity / integrity preconditions (reproduced)
- **Deliverable identity stable at HEAD:** activation-preflight.md (`55f15759`), activation-evidence.md (`44f4d413`), fable-probe.md (`58381fa6`), evidence-map.json (`9190e76d`), requirements.json (`81a6a999`) are all byte-identical between the reviewed gate SHA `702c64c` and HEAD `6c2fc12`. `6c2fc12` only adds the gate records + task-status update.
- **Validator:** `python tools/validate_directive_compliance.py --check` → **EXIT=0** (source digests + locked_requirement_ids intact).
- **Gates:** G0 PASS, G2 PASS (orchestrator), **G3/G4/G5 PASS** by independent reviewers at reviewed_sha `fb25f4d` (content = `702c64c`).
- **Audit chain (R273 primary):** I independently recomputed the 31-record hash chain from scratch (SHA-256 over canonical JSON minus `digest`, prev_digest linkage) WITHOUT importing shipped code → **all 31 records valid, head digest `53db08f2…` matches the sidecar anchor** (seq 31).
- **Control-plane harnesses:** `test_directive_compliance.py` / `test_project_control.py` are subprocess-heavy and time out in this Windows sandbox; every subtest observed before the cutoff passed (`... ok`), and the deterministic `--check` validator is EXIT=0. Not an M0-T113 deliverable; not a compliance gap.

## Intake review (source ↔ matrix)
Read all seven verbatim captures `source-009…015-amendment.md`. Each carries a `VERBATIM-BEGIN/END` owner block + forward-trace. The 32 applicable requirement rows faithfully render the source obligations with no **missing**, **weakened**, **combined**, or **invented** row: Amendment 9 → R250-R260 (11/11), Amendment 10 → R261-R267 (7/7), Amendment 11 → R268-R271 (4/4), Amendment 12 slice → R273+R276, Amendment 13 slice → R277+R280+R284+R285, Amendment 15 → R298-R301. Amendments' non-M0-T113 rows (R272/R274/R275, R278-R283/R286-R288, R289-R297) correctly bind to other tasks and are excluded from this set. Digests match (validator EXIT=0).

## Per-requirement verdicts (each judged on primary evidence I reproduced)

### Amendment 9 (R250-R260)
- **R250 — PASS.** source-009 verbatim authorization present; audit chain confirms activation executed (`state_transition` IDLE→PREFLIGHT `mode:limited-auto operator_initiated:true`, seq 2, 2026-08-29T05:05:19Z) and the loop stopped at protected decisions twice (owner_touch seq 11 `no_valid_checkpoint`; seq 31 `halt_unsafe`) — nothing auto-approved.
- **R251 — PASS.** Capture commit `a87b407` is a git ancestor of both the first launch tip `cfc6b16` and the seq-33 dispatch tip `c88c2b9` (recorded before acting).
- **R252 — PASS.** Preflight before every start: preflight §1-4 (seq-28 STOP), §5 re-preflight (PASS→first launch), §6 (seq-30 R276 STOP), seq-33 rerun preflight (progress_log 96%).
- **R253 — PASS.** Audit seq 2 detail `mode:limited-auto`; start JSON (evidence item 1) `--mode limited-auto --owner-enable-bounded-auto`, 11/11 probes; only extra flag ever = the owner-authorized one-time `--repin-cli-identity` (R277/R285). No other launch shape.
- **R254 — PASS.** First dispatch `cfc6b16` CI **20/20 success** (re-queried); seq-33 dispatch `c88c2b9` CI **20/20 success** + supervisor tree anchor `c88c2b9:tools/agent_supervisor = 8d34ea53…` matches the M0-T119 certified anchor. Non-matching states never dispatched (seq-28/30/attempt-1 all `dispatched:false`).
- **R255 — PASS.** Full select/direct/review/advance chain exercised live: transitions START_CLAUDE→CLAUDE_RUNNING→CHECKPOINT_RECEIVED→COLLECT_EVIDENCE→CODEX_REVIEW→VALIDATE_DECISION→POLICY_CHECK→HALTED with `codex_review_decision` seq 27. Advancement correctly gated by the review, which held.
- **R256 — PASS.** Fail-closed at every seam in primary data: 3 `approval_deferred DEFER_TO_OWNER` (ASK never AUTO, seq 5-7); `missing_checkpoint`→PAUSED_RECOVERY (seq 8-10); `UNSAFE_OR_DRIFTED` restart refusal (seq 16); `HALT_UNSAFE` (seq 27); `rotation_pending_flagged` deferred to seam (seq 24, state_kv `rotation_pending:true`).
- **R257 — PASS (prohibition honored).** PR #241 **OPEN / not merged** (`gh pr view 241`: state OPEN, closed false; title "DO NOT MERGE"). No autostart (`recover_boot` `resume_permitted:false`, `safe_no_auto_resume`). Telegram `configured:no`, queued 0. `pending_live_observation_register` shows 4.8-bridge live actuation + natural-event graduation still gated (shadow-only).
- **R258 — PASS.** All M0-T113 activation commits (`f44a6c6/8d47fb8/0c7b7d8/cfc6b16/bbb932a`) touched only `project-control/reports/**` — no `tools/agent_supervisor/**`. Activation ran at the M0-T112 certified identity; residuals carried as M0-T114 (accepted separately).
- **R259 — PASS (prohibition honored).** Stop-and-report-exact-mismatch, never partial: seq-28 (worker-pin + empty approved_models), seq-30 (CLI drift), attempt-1 (bash-mangled paths refused), Amendment-11 restart (`UNSAFE_OR_DRIFTED`, seq 16) — every one `dispatched:false`/fail-closed exit.
- **R260 — PASS.** 7-item report in activation-evidence.md; each item corroborated by primary state: mode, run `run_M0_T107_unitJ` + runtime dir + budget digest `c1a51d3a…`, selected task M0-T107, dispatch evidence (3 ASK cmds), operator commands, Telegram state, awaiting-owner.

### Amendment 10 (R261-R267)
- **R261 — PASS.** source-010 verbatim; owner fact (Fable available) independently consistent — the fable_probe init event and the seq-33 worker both report `claude-fable-5`.
- **R262 — PASS.** `model_selection.toml [claude] model = ""` (re-hashed live, below); seq-33 dispatch `observed_models:["claude-fable-5"]` (journal `provider_session_continuity` session `02b014ee`).
- **R263 — PASS.** Probe-before-change: `doctor --live` VERIFIED `sha256_head 8a9c9c9018460062` (= the then-current 2.1.248 pin, later the `replaced_digest`); supplemental probe init_model `claude-fable-5` (fable-probe.md).
- **R264 — PASS.** source-010 capture `c5ca81a` + committed `M0-T113-fable-probe.md` (`bbb932a`).
- **R265 — PASS.** Exactly one setting changed; I re-hashed `C:\SupervisorController\model_selection.toml` → **`FCBBF70F553AE115…DD2B`** (matches), `[claude] model = ""`.
- **R266 — PASS.** I re-hashed `C:\Program Files\SupervisorConfig\config.toml` → **`A1F995016B541B9D…D1436`** (matches); contains exactly `[approved_models] models=["claude-fable-5","claude-opus-4-8"]` and `[claude] allowed_models=["claude-fable-5","claude-opus-4-8"]` — the two instructed changes.
- **R267 — PASS.** Manifest re-recorded (`b07818fa`, preflight A3), full §5 re-preflight PASS, then launch at `cfc6b16` — hold honored.

### Amendment 11 (R268-R271)
- **R268 — PASS.** Audit seq 12-14 `approval_owner_denied DENY`; approval records digests `5637335f…/56cbd282…/ae36645d…` match the echoed evidence; seq 15 `owner_cleared_pause` PAUSED_RECOVERY→PREFLIGHT; seq 16 identical certified restart (refused pre-dispatch — exposing the seam).
- **R269 — PASS.** Amendment-11 attempt: no new identity, 0 provider calls (evidence addendum 1). Completed at seq-33: `run_budget_resumed` (seq 19, resumes=1), live Fable 5 (session `02b014ee`), checkpoint `M0-T107-ready-2026-08-29-01` validated (seq 21-25).
- **R270 — PASS (prohibition honored).** After the seq-16 refusal, **zero** further restarts (audit gap seq 16→17 spans the full recert, next day); `restart_attempts` counter = 0; separate correction proposed as M0-T115.
- **R271 — PASS.** Recert-before-resume: M0-T116 (post M0-T115) **accepted**; M0-T119 (post Amendments 13/14) **accepted** — both before the seq-33 resume.

### Amendment 12 slice (R273, R276)
- **R273 — PASS (prohibition honored).** Chain cryptographically intact (independent recompute, above). Decisive: the raw `queued_asks` rows STILL show `answered_at_utc = ""` while their `approval/*` records are DENIED — the journal was **never hand-edited**; truthfulness comes only from read-time reconciliation (each ask digest maps to a DENIED approval → reconciled open asks = 0).
- **R276 — PASS.** seq-30 attempt STOPPED on drift (no bypass); seq-33 resume ran only after M0-T119 accepted + CI 20/20 at `c88c2b9` + full preflight green.

### Amendment 13 slice (R277, R280, R284, R285)
- **R277 — PASS.** Option A slice executed: one-time `--repin-cli-identity` on the next certified start after recert — `cli_identity_repinned` (seq 17, `owner_repin`, `repinned:["claude"]`).
- **R280 — PASS (prohibition honored).** `DISABLE_UPDATES` set nowhere (registry HKCU/HKLM clean; only `DISABLE_AUTOUPDATER=1` in HKLM — the authorized R278/R286/R288 control; code comment in process.py deliberately declines DISABLE_UPDATES). Installed `claude --version` = **2.1.251** (= admitted; not downgraded).
- **R284 — PASS.** R276 rerun from the beginning in order: record-manifest `774f9198` (119 files) → verify-controller → doctor 43/43 → doctor --live VERIFIED → full preflight (CI 20/20 @ c88c2b9) → certified start (progress_log 96-98% + audit resume seq 17-31).
- **R285 — PASS.** Exactly **one** `cli_identity_repinned` audit event (seq 17). I re-hashed the installed `claude.exe` with the shipped head-1MB+size algorithm → **`d6f6c29a8ac6b3cf…`, size 217360032**, exactly equal to the journal's pinned identity; resumed in already-authorized limited-auto (`run_budget_resumed`, dispatched). No new activation authority.

### Amendment 15 (R298-R301)
- **R298 — PASS.** Sequencing intact: all five gates recorded PASS; acceptance has NOT happened (`status: awaiting_gate` — correctly, this DCV precedes it); cycle-2 not started (journal HALTED at rest, M0-T107 still `claimed`, owner holds the command). Nothing jumped the sequence; acceptance is the pending orchestrator step this verdict enables.
- **R299 — PASS.** Clean pushed tip (HEAD `6c2fc12` == origin, tree clean) + journal at rest verified live: `current_state = "HALTED"`, `effects`=0, `outbox`=0, `inbox`=0, `launched_child_processes=[]`, reconciled open asks = 0. Report obligation satisfiable; underlying facts independently true now.
- **R300 — PASS (recording obligation).** Conditional cycle-2 stop protocol (no restart + preserve all evidence) durably captured verbatim in source-015 + row present (validator EXIT=0) + campaign seq-33 NEXT. The condition (a cycle-2 counted stop) has not fired; the binding record — the row's actual demand at this point — exists.
- **R301 — PASS (recording obligation).** Conditional AD-093 defect-diagnosis obligation durably recorded (source-015 + row, cites this row as qualifying evidence on future creation). Packet allocated only if the condition fires; the recording is present and binding.

## Prohibited-action check
Nothing merged/accepted/dispatched-out-of-regime/deployed/installed/purchased/closed: M0-T113 not yet accepted (correct); PR #241 OPEN/unmerged; 2.1.251 admitted only through the accepted M0-T117/T118/T119 chain; repin owner-authorized. No violations.

---

## Relevant file paths (absolute)
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/tasks/M0-T113.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T113-activation-preflight.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T113-activation-evidence.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T113-fable-probe.md`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/reports/M0-T113-evidence-map.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/directives/D-024-fable-codex-loop/source-009…015-amendment.md`, `requirements.json`, `verification.json`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/project-control/gates/M0-T113-G0..G5.json`
- Runtime (read-only): `%LOCALAPPDATA%/NYCBuildabilitySupervisor/33dfa57d…7a7ed/audit.jsonl` (+ `.head.json`) and `supervisor_journal.sqlite3`
- `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24/tools/agent_supervisor/audit_log.py`, `process.py` (algorithms reproduced)

All 32 applicable requirement IDs are individually **SATISFIED** on primary evidence I personally reproduced. No VIOLATED / BLOCKED / UNVERIFIABLE rows.

**DCV VERDICT: PASS at 6c2fc12**

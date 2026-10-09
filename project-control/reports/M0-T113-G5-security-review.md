<!-- Saved VERBATIM by the orchestrator from the G5 security-reviewer agent-return channel
     (transport entity-decoding only). Review head 702c64c. -->

All verification is complete. Here is my G5 security review report to return to the orchestrator.

---

# Gate Report

- **Gate ID:** G5 (independent security review)
- **Task ID:** M0-T113 (D-024 Amendment 9 unit N — R187/R595 limited-auto activation act + first-loop operation proof)
- **Reviewer:** security-reviewer (read-only)
- **Producer:** fable-orchestrator-session
- **Result:** PASS
- **Clean environment/worktree used:** Yes — reviewed at frozen control head `702c64c` (`git rev-parse HEAD` = `702c64c8131a17570e2b9f8815734816b2aa0776`, branch `control/D-024-fable-codex-loop`); live machine-local runtime state read read-only for the R299 at-rest confirmation.

## Scope note

This is a governance/activation-act packet. Its `allowed_paths` are two report files under `project-control/reports/`; it binds NO production source (R258 prohibits modifying certified supervisor code; `forbidden_paths` include `.claude`, `apps`, `packages`, `services`, `supabase`, `tools`). The security review is therefore about AUTHORITY and CONTAINMENT, not code. Modularity review N/A (no handwritten production source changed).

## Directive/requirement verification (security-relevant subset, re-derived at `702c64c`)

The full 32-row directive re-derivation is the `directive-compliance-verifier`'s pass (still `pending` in `verification.json` at this head — see SEC-INFO-1). Below are the security-load-bearing requirements I re-derived from source and reproduced live.

| Requirement ID | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024-R250/R253 (activation enable + exact command) | `702c64c` / source-009 | PASS | source-009 VERBATIM owner authorization present; audit `mode limited-auto`, transitions PREFLIGHT→START_CLAUDE→CLAUDE_RUNNING |
| D-024-R256 (fail-closed continues) | `702c64c` / source-009 | PASS | 6 distinct live fail-closed refusals (inventory below), none leaked an effect |
| D-024-R257 (exclusions untouched) | `702c64c` / source-009 | PASS | PR #241 no merge commit; no supervisor autostart task; 4.8 bridge shadow-only (attested) |
| D-024-R259 (stop-report on mismatch) | `702c64c` | PASS | 3 documented stops (seq-28 model/approved-models, seq-30 CLI drift, bash-mangled paths), no partial activation |
| D-024-R261..R267 (config edits) | `702c64c` / source-010 | PASS | owner authorization present; single model_selection edit; admin `[approved_models]` edit owner-executed |
| D-024-R268 (deny/clear/restart) | `702c64c` / source-011 | PASS | audit seq 12–14 "denied by the owner at the CLI" (digests 5637335f/56cbd282/ae36645d) |
| D-024-R273 (no journal hand-edit) | `702c64c` / source-012 | PASS | `verify_chain()` ok=True over 31 records; head file digest == recomputation |
| D-024-R277/R285 (one-time repin) | `702c64c` / source-013 | PASS | exactly ONE `cli_identity_repinned` (seq 17, policy_result `owner_repin`, `["claude"]`); binary re-hash == admitted digest |
| D-024-R280 (no DISABLE_UPDATES / no downgrade) | `702c64c` / source-013 | PASS | registry: DISABLE_UPDATES NOT SET (HKCU/HKLM/proc); Claude 2.1.251 not downgraded |
| D-024-R298/R299/R300 (cycle-2 protocol) | `702c64c` / source-015 | PASS | at-rest readback: HALTED, 0 asks, 0 effects, audit intact; cycle-2 command omits repin flag |

Every privileged act cited in the evidence map maps to a captured amendment source (source-009..015); no privileged act lacks a source row. R288 (machine env var) is not an M0-T113 row — it is M0-T117's owner-executed act, referenced only contextually and confirmed independently (below).

## Steps independently executed (read-only commands)

1. `git rev-parse HEAD` / `git rev-parse --abbrev-ref HEAD` → `702c64c…`, `control/D-024-fable-codex-loop` (frozen head confirmed).
2. Read: task packet `M0-T113.json`; deliverables `M0-T113-activation-preflight.md`, `M0-T113-activation-evidence.md`; `M0-T113-evidence-map.json`; amendment sources `source-009..015`; `verification.json` (M0-T113 section, line 7430); `campaigns/D-024-fable-codex-loop.json`; `M0-T117-autoupdater-evidence.md`; `M0-T119-recertification.md`; `shell_routing_2026-08-29_m0t120_2_1_251.json`.
3. `python -c "executable_identity('C:\\Users\\MLFLL\\.local\\bin\\claude.exe')"` → digest `d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8` (sha256_head+size, 217360032 bytes); head16 `d6f6c29a8ac6b3cf` MATCHES admitted digest.
4. `claude.exe --version` → `2.1.251 (Claude Code)`.
5. `python -m tools.agent_supervisor status --json --checkout …ctl24` → `current_state HALTED`, `pending_effects []`, `open_asks []`, 3 `resolved_asks` all `approval_status DENIED / actionable false`, `unsent_outbound 0`, `audit_chain_ok true`, `audit_head_sequence 31`, `mode none`, `limited_auto_enabled false`, no children recorded.
6. `reg query "HKCU\Environment"` and `HKLM\…\Session Manager\Environment` filtered for DISABLE_UPDATES / DISABLE_AUTOUPDATER; `env |` filter.
7. `schtasks /query /fo LIST` filtered for supervisor/loop/codex/fable/NYCBuild.
8. Parsed runtime `audit.jsonl` (31 events) + ran `AuditLog(...).verify_chain()` and independent `compute_record_digest` on the last record.
9. `git worktree list`; `git log --oneline --all | grep #241`.

## Findings

**SEC-INFO-1 — DCV directive rows still `pending` at the reviewed head (process, not security defect).**
`verification.json` M0-T113 section lists all 32 `applicable_requirement_ids` in `state: pending` (no `verified_by`, no `reviewed_sha`). That is the separate `directive-compliance-verifier` pass in this same gate wave (producer ≠ verifier). It is acceptance-blocking and must be recorded PASS by that reviewer before the orchestrator accepts. Out of my gate's scope; flagged for the orchestrator.

**SEC-INFO-2 — Authority chain is complete; every privileged act traces to a captured owner source, and the audit corroborates owner-initiation.**
Activation enable (source-009 R250/R253, VERBATIM), model-selection + approved-models edits (source-010 R261–R267), deny/clear/restart (source-011 R268), same-window repair + gated resume (source-012 R272–R276), Option-A repin (source-013 R277/R285), shell-routing (source-014), cycle-2 protocol (source-015 R298–R301). Runtime audit shows owner-initiated acts explicitly: denials recorded "denied by the owner at the CLI" (seq 12–14); repin `policy_result: owner_repin` / "an operator explicitly accepted a changed provider CLI identity" (seq 17); two `owner_touch_recorded` (seq 11, 31). The orchestrator's own start was denied by the session classifier and the owner typed it via `!` prefix (documented in progress_log/campaign; not a durable audit field, but consistent with the operator-initiated acts the audit does record).

**SEC-INFO-3 — Containment and effects: external_writes 0, no orphaned effects, corroborated live.**
Live status at rest: `pending_effects []`, `unsent_outbound 0`, no child processes, `mode none`. Audit scan of all 31 events found NO push/commit/send/external-write/outbound/autostart events. Job-object (kill-on-close) containment is attested in the committed start-command JSON (activation-evidence item 1) and corroborated by "no children recorded" at rest and the clean producer worktree `wt-m0t107 @ 796e18f`. No refusal path leaked an effect.

**SEC-INFO-4 — Fail-closed inventory (6 live refusals, each stopped without forwarding/writing).**
(1) S14 missing-checkpoint → PAUSED_RECOVERY (audit seq 10); zero writes. (2) Unclassified commands → ASK never AUTO: 3 `approval_deferred` → owner-denied (seq 12–14); nothing forwarded. (3) Pre-dispatch seam refusal (Amendment 11 restart) → `UNSAFE_OR_DRIFTED`, dispatched=false, 0 provider calls, exit 11. (4) `provider_cli_drift` (seq-30) → preflight stop; start not attempted. (5) Corrupt-path (bash-mangled) → `UNSAFE_OR_DRIFTED`, dispatched=false, 0 provider calls, journal stayed PREFLIGHT. (6) `HALT_UNSAFE` independent Codex review (seq 27, returncode 0) → POLICY_CHECK→HALTED (seq 30), exit 10, nothing forwarded. The security value of the unit is exactly this inventory, and it holds.

**SEC-INFO-5 — Prohibition integrity verified.**
R257: PR #241 has NO merge commit (all git-log references say "stays unmerged"); GitHub-side confirmation is a `gh` fact for the orchestrator, but nothing in this packet could merge it. No supervisor/loop autostart scheduled task exists (`schtasks` empty). R273: audit hash-chain cryptographically intact — `verify_chain()` returned ok=True over all 31 records (sequence contiguity + prev_digest linkage + per-record digest recomputation + head-anchor match), the `.head.json` digest `53db08f2…` equals the last-record digest, and an independent `compute_record_digest` of the last record matched; a hand-edit would have tripped `digest_mismatch`. R280: DISABLE_UPDATES NOT SET anywhere (HKCU/HKLM/process env); Claude not downgraded. The one `DISABLE_AUTOUPDATER=1` at HKLM is the authorized R288 control, matching M0-T117's owner-side pack `[Environment]::SetEnvironmentVariable('DISABLE_AUTOUPDATER','1','Machine')` marked "OWNER-EXECUTED — NOT run by this producer"; it requires admin elevation the agent session lacks (HKCU carried neither key) and is a related, in-scope control, not the prohibited key.

**SEC-INFO-6 — Repin scope: exactly the admitted digest, consumed exactly once.**
Independent re-hash of the installed `claude.exe` via `tools.agent_supervisor.process.executable_identity` = `d6f6c29a8ac6b3cf…889ed8`, byte-for-byte the R282-admitted 2.1.251 identity recorded in `M0-T119-recertification.md` ("ADMITTED … digest d6f6c29a8ac6b3cf…") and the `shell_routing…2_1_251.json` fixture (`cli_identity` full string). The audit contains exactly ONE `cli_identity_repinned` event (seq 17, scoped to `["claude"]`). The campaign seq-33 `next_action` specifies the cycle-2 continuation as "the same certified start WITHOUT `--repin-cli-identity` (one-time repin consumed)". Repin scope and single-consumption confirmed.

**SEC-INFO-7 — No secrets/PII in the two deliverables beyond established convention.**
`M0-T113-activation-preflight.md` and `M0-T113-activation-evidence.md` contain only digests, run/session IDs, and Windows paths carrying username `MLFLL` (an established repo-wide convention present in CLAUDE.md). Telegram is presence-only ("values never read"); no token, chat ID, API key, password, or credential appears. No redaction defect.

**SEC-INFO-8 — Carried follow-up (out of scope here, tracked).**
The campaign seq-33 text carries `F2 wrapper-evasion SEC-MINOR` and other candidates as supervisor-code follow-ups from prior gates. These are not M0-T113 findings (governance packet, no production code) and are correctly tracked as separate follow-up candidates.

## Expected versus actual

Every security-load-bearing claim in the deliverables and evidence map reproduced exactly against source and live state: authority sources present and verbatim; containment 0-effect at rest; 6 fail-closed refusals with no leaked effect; hash-chain cryptographically intact; DISABLE_UPDATES not set; repin = admitted digest, once. No discrepancy found.

## Evidence paths (absolute)

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T113-activation-preflight.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T113-activation-evidence.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T113-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T113.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\source-009-amendment.md` … `source-015-amendment.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\verification.json` (M0-T113 section)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\campaigns\D-024-fable-codex-loop.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T117-autoupdater-evidence.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T119-recertification.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\process.py` (`executable_identity`, line 265); `audit_log.py` (`verify_chain`, line 256)
- Runtime (machine-local, read-only): `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\33dfa57d…\audit.jsonl` (+ `.head.json`), `supervisor_journal.sqlite3`

## Human-style walkthrough findings

The operator experience is a fail-closed loop: it dispatched a live Fable 5 worker, reached a structured checkpoint with zero brokered command requests, then the independent Codex reviewer refused CONTINUE (HALT_UNSAFE) and the controller HALTED rather than trusting the worker's self-report. At rest the operator sees HALTED with zero open asks and zero pending effects — a clean, resumable, human-touchpoint state. This is the review-independence principle exercised live.

## Regression/security/provenance findings

No SEC-BLOCKER, SEC-MAJOR, or SEC-MINOR findings against M0-T113. All items are SEC-INFO (above). Provenance is intact and cryptographically verifiable (audit chain), and every privileged act is authorized by a captured, verbatim owner source.

## Defects

None.

## Required rework

None for the G5 security gate. For overall acceptance (not this gate): the `directive-compliance-verifier` must record its 32-row pass (SEC-INFO-1), and the orchestrator should confirm PR #241 unmerged via `gh` at accept time.

## Reviewer conclusion

The activation act's security posture is sound. Every privileged act (limited-auto enable, config edits, restart, one-time repin, machine env var) traces to a captured, verbatim owner authorization, and the runtime audit corroborates owner-initiation. Containment held (external_writes 0, no orphaned effects, no autostart). Six distinct fail-closed refusals were exercised live and none leaked an effect. The audit hash-chain is cryptographically intact (no journal hand-edit). DISABLE_UPDATES is not set and Claude was not downgraded. The repin pinned exactly the R282-admitted digest `d6f6c29a…` and was consumed once, with the cycle-2 command correctly omitting the flag. No secrets/PII beyond repo convention appear in the deliverables.

**G5 VERDICT: PASS**

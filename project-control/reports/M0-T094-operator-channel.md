# M0-T094 — Unit G: operator channel (one-command start, status, /loop-* commands, ask-Codex) — D-024 Phase F

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R104** (Phase F; packet-named). Status: **STAGED (claim + G0 + scenario pack)** — the
seq-17 session accepted unit F, claimed this unit, and authored this pack at a clean seam under
the D-010 R113/R114 rotate-at-seam ceiling; the successor implements from this frozen pack with a
fresh context budget (the same pattern that staged unit F at seq 16 and delivered it at seq 17).
No implementation code is written at this staging seam.

## 0. Reuse boundary (R018: prove existing architecture, extend — never duplicate)

| Existing surface (REUSE, do not duplicate) | What it already provides | Unit-G extension |
|---|---|---|
| `cli.py` verbs: `start`, `status`, `stop`, `resume`, `doctor`, `watchdog`, `pending-approvals`, answer-verbs, `autostart-plan/install/uninstall` | the canonical operator command surface (R034 "no parallel CLI") with typed refusals (`refusals.py`, stable exit codes) and idempotent start (`locking.SingleInstanceLock`; `start_gate.bounded_mode_gate`) | prove each section-14 operation maps to an existing verb; add ONLY: a documented "Start the agent loop" alias note (R035, likely help-text/docs not code), any missing concise-status fields (R034 list: current task+why, checkpoints, model/session+fallback, subagents+contracts, token health+confidence), and the NEW `ask` operation |
| `stop`/`resume` + `resume_scheduler` durable flags; `recovery.set_manual_pause`/`set_emergency_stop`; unit-F `stop_intent.set_graceful_stop` | durable pause/emergency-stop acknowledged only after the journal write (R036/R086); unit F added the graceful-stop intent + precedence | wire `graceful-stop` as a CLI verb over `stop_intent` (accepted unit-F module); emergency-stop semantics already cancel wake + require explicit resume |
| `notifications.py NotificationSink` | the R096 notification-sink boundary with terminal implementation | route new operator events through it; NO email/credentials (owner-gated forever) |
| `codex_reviewer.py` (read-only argv, `FORBIDDEN_REVIEWER_FLAGS`, bounded packets, timeouts) + `review_packet.py` | the read-only Codex invocation contract (R085 "grants no mutation tools") | NEW `ask` operation: bounded owner question → read-only Codex call with a bounded current-state packet → concise answer, or a durable request ID on timeout (journal-backed; no background duplicate after timeout, R087) |
| unit-F `epoch_lease`/`outage_policy`/`bootstrap_gate` + `campaign_continuity --status` | durable status facts (lease/epoch owner, retry/idle holds, campaign NEXT) answerable without waking Fable (R094) | the concise `status` renders these; verbose/JSON via existing `--json` conventions (R095) |
| `.claude/hooks/` (4 existing: both guard packs — DO NOT TOUCH — plus `supervisor_event_recorder.py`, `directive_reminder.py`) + `.claude/settings.json` hook wiring; `.claude/skills/*` (incl. `session-handoff`) | the proven hook + skills surface and its settings wiring pattern | NEW thin skills `/loop-start /loop-status /loop-tasks /loop-ask /loop-pause /loop-resume /loop-stop /loop-emergency-stop` with `disable-model-invocation: true` (R083/R158) calling the supervisor CLI directly; NEW feature-detected pre-model interception hook (R084: UserPromptExpansion preferred; UserPromptSubmit exact-match/block/display/erase otherwise); MUST NOT collide with built-in `/loop` (R159) — names are `/loop-*` exactly |
| unit-C fixtures + `capability_probe` (2.1.248 current) | installed-version feature detection discipline (R149) | detect the hook capability on 2.1.248 and record a fixture; the zero-context PROOF (R088) is measured, or the second-terminal fallback is documented truthfully |

## 1. Acceptance-scenario pack (pre-implementation; section-16.5 matrix — R111)

| ID | Scenario (Given / When / Then) | Kind | Key reqs |
|---|---|---|---|
| S1 canonical idempotent start | Given a running campaign, when `start` (or the documented "Start the agent loop" alias) runs again, then the active campaign is REPORTED, never duplicated; no duration parameter exists. | deterministic | R027/R034/R035/R036 |
| S2 section-14 status set | Given durable state, when `status` renders, then it names: current task + why selected, recent checkpoints, active model/session + fallback state, active subagents + bounded contracts, token/context health WITH confidence labels; concise by default, verbose/JSON on demand; no invented numbers (unknown never zero). | deterministic | R034/R042/R094/R095 |
| S3 durable-before-ack controls | Given pause/resume/graceful-stop/emergency-stop, when each verb runs, then the journal is updated BEFORE the acknowledgment prints; graceful-stop uses unit-F `stop_intent`; emergency stop cancels dispatch, blocks lease renewal, marks ambiguous effects, requires explicit resume. | deterministic | R036/R086 |
| S4 ask — bounded synchronous window | Given an owner question, when `ask` runs, then the question goes to read-only Codex with a bounded state packet (no mutation tools), and a concise answer prints within the configured window. | deterministic (fake transport) | R085/R104 |
| S5 ask — durable async fallback | Given the window elapses, when `ask` times out, then a durable request ID is returned, retrievable later; NO background duplicate request survives the timeout. | deterministic | R085/R087 |
| S6 bridge security matrix | Given hostile inputs (shell metacharacters, quotes, multiline, Unicode, oversized, empty, terminal escapes, secret-looking strings), when they flow through ask/hook paths, then: no shell interpolation (argv arrays only), bounded I/O, redaction before display/persist, exact command matching (never substring), repo-root + campaign identity validated. | deterministic | R087/R111 |
| S7 skills are user-only and thin | Given the 8 `/loop-*` skills, when inspected, then each carries `disable-model-invocation: true` (or the locally supported equivalent), calls the supervisor CLI directly, and is NOT an ordinary prompt-based command; `/btw` is not used; no collision with built-in `/loop`. | deterministic | R083/R158/R159 |
| S8 feature-detected interception | Given the installed 2.1.248, when the hook path is chosen, then the choice is feature-DETECTED (UserPromptExpansion preferred; else UserPromptSubmit with exact-match + block + user-visible output + prompt erasure), recorded in a fixture; unsupported → the documented second-terminal fallback, never a fake. | deterministic + fixture | R084/R088/R149 |
| S9 zero-context proof | Given an intercepted `/loop-status`, when measured on the installed version, then the command and its output are ABSENT from the Fable transcript and context usage is unchanged within measurable noise — or the honest fallback is documented with the version requirement. | measured (live, low-risk) | R088/R111/R159 |
| S10 similar text not intercepted | Given ordinary prompts resembling the commands ("tell me about /loop-status", "loop-status", "/loop-statuses"), when submitted, then they are NOT intercepted (exact-match only). | deterministic | R084/R111 |
| S11 idle vs active-response behavior | Given Claude idle and Claude mid-response, when `/loop-*` runs in each state, then active work is never cancelled/corrupted; if input queues until the response ends, that fact is documented and second-terminal controls are the advertised real-time path. | measured + doc | R089 |
| S12 hook fail-closed | Given a hook error/timeout/malformed payload, when interception fails, then it fails CLOSED for the control action (no zombie duplicate process, no half-executed control) and the prompt is not silently swallowed without a user-visible reason. | deterministic | R087/R111 |
| S13 no worker pollution | Given any operator text/status output, when composed, then no token quotas/countdowns reach worker-facing assignments (`assert_worker_text_clean`) and operator traffic never inserts polling messages into the Fable context. | deterministic | R045/R184 |
| S14 Gate-0 + identity | Given the operator commands, when run outside the campaign worktree/repo root, then repo-root + campaign identity validation refuses (reuse unit-F `bootstrap_gate` + `campaign_continuity` identity). | deterministic | R087/R125–R128 |
| C1 live interception canary (OWNER-GATED) | Given the installed terminal, when an owner-approved exact-command canary submits `/loop-status` live, then interception + zero-context proof are captured as a fixture (the R088 measurement). | live canary (owner exact-command, R192/R197) | R088/R183 |

## 2. Owner-gated items (flagged, not blocking the deterministic core)

- **C1 live interception canary** (R088 zero-context measurement on the live terminal): needs an
  owner-approved exact command, like every prior C1. The deterministic matrix + fixtures are
  built WITHOUT it; if the proof cannot be captured, the truthful second-terminal fallback is
  the documented path (R088 explicitly permits this).
- Email/remote notification remains owner-gated (R096); terminal sink only.

## 3. Implementation guidance for the successor (not yet done)

- **Prove-first (R018):** for S1–S3 cite the existing CLI verbs before adding any; the likely
  genuine gaps are ONLY: the `ask` operation, the graceful-stop verb over unit-F `stop_intent`,
  any missing section-14 status fields, the 8 thin skills, the interception hook, and the R035
  alias documentation. Inspect `cli.py`'s grouped verb loops (lines ~3364/3414/3430) before
  assuming a verb is missing — pause/resume/answer verbs already exist in groups.
- **Modularity:** `cli.py` is already ~179KB and symbol-ceiling-warned — put the `ask`
  operation and status-composition logic in NEW focused modules (`operator_ask.py`,
  `operator_status.py`?) with thin `cli.py` wiring; the hook is a standalone script under
  `.claude/hooks/`; skills are markdown/frontmatter under `.claude/skills/loop-*/`.
- **Guards:** `.claude/hooks/agent_dispatch_guard.py` + `readonly_agent_guard.py` are
  UNTOUCHABLE without a G5-reviewed reason (expansion-hold rule §1); this unit only ADDS files.
- **Settings wiring** (`.claude/settings.json`): additive hook registration only; the G5 gate
  of THIS unit is the review for that wiring.
- **Zero-context proof method:** compare transcript JSONL + `/context`-style occupancy before
  and after an intercepted command (unit-D/E fixtures show the measuring pattern); record as a
  masked fixture like the 2_1_248 captures.
- **Test file:** `tools/test_agent_supervisor_operator_channel.py` (the §1 matrix; R111 names
  the required cases incl. metacharacter/Unicode safety, timeout single-request, hook
  fail-closed).
- **DCV scale:** 54 applicable requirements — build the evidence map per behavior cluster as
  unit F did (`M0-T092-evidence-map.json` is the worked template).

## 4. Evidence (populated during implementation — successor)

(pending — staging seam only)

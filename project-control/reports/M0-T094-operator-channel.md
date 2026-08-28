# M0-T094 — Unit G: operator channel (one-command start, status, /loop-* commands, ask-Codex) — D-024 Phase F

Producer: fable-orchestrator-session (orchestrator). Supervisor-freeze qualifying evidence:
**D-024-R104** (Phase F; packet-named). Status: **IMPLEMENTED (deterministic core; §4 evidence)**
— the seq-17 session staged this pack at a clean seam; the seq-18 successor session implemented
from it unchanged (§0 reuse boundary held; §1 matrix delivered as
`tools/test_agent_supervisor_operator_channel.py`, 51/51 PASS). The owner-gated C1 interception
canary (§2) remains pending; the honest second-terminal fallback is documented (§4.2/§4.4).

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

## 4. Evidence (implementation session, 2026-08-27/28)

### 4.1 Prove-first result (R018) — the §0 boundary held exactly

Every section-14 operation except the named gaps mapped to an EXISTING verb:
`start` (idempotent via `SingleInstanceLock`, no duration, `--run-wall-clock-seconds`
optional-unlimited), `status`, `pause`/`resume`/`stop --clear`/`emergency-stop`
(durable-before-ack, existing), `pending-approvals`/answer verbs, `export-handoff`.
The genuine gaps were ONLY the §3 list — nothing else was added:

| Gap | Delivered as |
|---|---|
| `ask` operation | NEW `operator_ask.py` (400 ln): bounded question sanitation (size/control-seq/redaction), identity validation, bounded state packet, ONE read-only Codex window via the REUSED `codex_reviewer.build_argv` contract (S2.2 flags, forbidden-flag refusal, `--sandbox read-only`), `process.run` containment (timeout kills the tree — R087 no-background-duplicate), durable `queued_asks` fallback (`oper_*` ids; `--show`, `--resubmit` re-poses the SAME row); + `operator_ask_answer.schema.json` |
| graceful-stop verb | `graceful-stop [--reason] [--clear]` over accepted unit-F `stop_intent` (durable BEFORE ack; emergency>graceful>pause) |
| section-14 status fields | NEW `operator_status.py` (279 ln): labeled facts (value+source+R042 confidence; absent = `unknown`, never zero; persisted measurements keep their own label) composed read-only from journal + campaign records; additive `status` payload key `section14` + concise lines; `--json` = verbose |
| 8 thin skills | `.claude/skills/loop-{start,status,tasks,ask,pause,resume,stop,emergency-stop}/SKILL.md`, each `disable-model-invocation: true`, thin CLI-calling bodies, no `/loop` collision, no `/btw` |
| interception hook | NEW `.claude/hooks/loop_command_interceptor.py` (232 ln) + additive `settings.json` UserPromptSubmit registration; guard hooks untouched |
| R035 alias doc | cli.py module docstring + `start` help: "'Start the agent loop' IS the `start` command" |

CLI wiring stayed thin per the modularity policy: the two new handlers + parser
registration + the shared `_open_runtime`/`_emit` helpers live in NEW
`operator_channel_cli.py` (244 ln); cli.py net diff is +34 lines and
`modularity_check --check` = failures 0 (cli.py had tripped `baseline_growth`
mid-session; the split resolved it — no exception record needed).
`durable_state.py` gained one additive read-only method (`ask_by_id`, for
`--show` over answered rows).

### 4.2 Feature detection + honest measurement state (R084/R088/R089/R149)

`fixtures/loop_interception_detection_2_1_248.json`: **selected_event =
UserPromptSubmit** (payload measured-live per `hook_event_payloads_v1.json`;
block/display/erasure contract official-docs; the exit-0+stdout context path
measured every session by `directive_reminder.py` on the same event).
UserPromptExpansion is catalog-present but its RESPONSE contract is UNPROVEN
on 2.1.248 → the hook passes a matching prompt through unchanged on that
event, never a fake (R088); flipping requires a measured capture. The hook
reads the fixture at runtime (fail-closed default = the measured path).
**zero_context_proof = pending-owner-C1** and **queued_input_behavior =
pending-owner-C1**: until the owner-gated C1 canary (R192/R197) runs, the
SECOND TERMINAL (`status`/`ask`/`pause`/`graceful-stop`/`stop`/`emergency-stop`)
is the advertised zero-context real-time path — R088's truthful fallback,
asserted by tests S9/S11.

Identity-validation scope (deliberate, for reviewers): the ask/hook paths
validate repo-root markers + machine-validated campaign records
(`campaign_continuity.load`, fail-closed on tamper); the unit-F
`bootstrap_gate` module remains the SESSION-write gate — operator reads/
controls do not re-run the MCP-clean probe.

### 4.3 Test + check evidence

* `tools/test_agent_supervisor_operator_channel.py`: **51/51 PASS** — the full
  §1 matrix S1–S14 incl. R111's named cases (metacharacter/Unicode/quoted/
  multiline/empty/oversized questions, terminal-escape stripping both
  directions, runtime-built secret redaction, timeout single-request +
  same-row resubmit, hook fail-closed on malformed payload / broken supervisor
  / hung supervisor with kill, exact-match-only interception incl.
  `/loop-statuses`/`loop-status`/mention forms, pass-through emits NOTHING,
  block emits ONLY decision+reason, worker-text-clean ask instruction,
  identity refusals at module/CLI/hook levels with typed exits 11/13).
* Regression over the touched surfaces: operator_channel + command_authority +
  controller_succession + phase1 + reviewer + start_reentry = **332 PASS**.
* Whole-suite baseline (freeze rule): `python -m pytest tools/ -q` run this
  session — result recorded in the checkpoint/progress entry; CI
  supervisor-bridge job is the confirming whole-suite run on the pushed SHA.
* `ruff check` on every new/changed file: clean (the 9 cli.py F401s are
  PRE-EXISTING at the accepted HEAD and untouched under the defect-only lane).
* `python tools/modularity_check.py --check`: failures 0.
* Live smoke (read-only + scratch runtime): `status` renders the section-14
  concise block; `graceful-stop` set→status→clear round-trip durable;
  hook end-to-end `/loop-status` and `/loop-tasks` block-with-output.

### 4.4 Exact owner commands (task output)

From the repository root (`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`):

* **Start the agent loop** (R035 alias): `python -m tools.agent_supervisor start`
  (idempotent; add the explicit executables/config/packet inputs to dispatch,
  per `--help`; no duration exists — omit `--run-wall-clock-seconds` for unlimited)
* **Status** (section 14, no model call): `python -m tools.agent_supervisor status`
  (verbose/JSON: `--json`) · campaign NEXT: `python -m tools.agent_supervisor.campaign_continuity --status`
* **Pause / resume:** `python -m tools.agent_supervisor pause` / `resume`
* **Graceful stop (land the unit, then stop):** `python -m tools.agent_supervisor graceful-stop --reason "<why>"` · clear: `graceful-stop --clear`
* **Hard stop / emergency:** `python -m tools.agent_supervisor stop` ·
  `emergency-stop` · clear flags: `stop --clear`
* **Ask Codex (read-only):** `python -m tools.agent_supervisor ask "<question>"
  --codex-executable <path> --config <path> --model-selection <path>
  [--window 90]` · after a timeout: `ask --show <request-id>` /
  `ask --resubmit <request-id> --codex-executable ... --config ... --model-selection ...`
* **In the Claude Code terminal:** `/loop-start /loop-status /loop-tasks
  /loop-ask <q> /loop-pause /loop-resume /loop-stop [reason]
  /loop-emergency-stop` — intercepted pre-model where supported; until the C1
  zero-context proof lands, treat the second terminal as the authoritative
  real-time path. `/loop-ask` in-terminal additionally needs
  `SUPERVISOR_CODEX_EXECUTABLE`/`SUPERVISOR_CONFIG`/`SUPERVISOR_MODEL_SELECTION`
  set, else it prints the exact second-terminal command.

# M0-T110 — unit K: `/loop-codex` persistent same-terminal Codex-only discussion channel

D-024 Amendment 8, applicable rows **R231–R240, R246, R248, R249** (13).
Supervisor-freeze qualifying evidence: **D-024-R232/R234** (packet + commits).
Producer: fable-orchestrator-session (campaign seq 23). Claim seam: G0 PASS at `8fc8a5b`,
claimed at `a5ac4dd`.

## 0. Reuse boundary (R237 — reuse, never re-implement)

| Reused surface | Where | What unit K takes from it |
|---|---|---|
| Pre-model interception | `.claude/hooks/loop_command_interceptor.py` (unit G, M0-T094) | exact-token anchored matching (never substring), identity-validated repo root, detection-fixture-selected `UserPromptSubmit` block/erase/display contract, argv arrays only, hard timeout with kill, fail-closed blocks naming the exact second-terminal command. Unit K EXTENDS the alternation with `loop-codex` + a subverb map; no second hook. |
| Measured installed-version fixture | `tools/agent_supervisor/fixtures/loop_interception_detection_2_1_248.json` | the ONLY basis for interception claims (R233/R235); `UserPromptExpansion` stays pass-through-unfaked. |
| User-only skill pattern | `.claude/skills/loop-ask/SKILL.md` | `disable-model-invocation: true`, interception note, one-command fallback, honest context-cost statement, no `/btw` claim (R233). |
| Read-only Codex invocation | `codex_reviewer.build_argv` (+ `FORBIDDEN_REVIEWER_FLAGS`, `assert_argv_safe`, `provider_failure_reason`) | `--sandbox read-only` + `--ephemeral --ignore-user-config --strict-config --json --output-schema --output-last-message`; a discussion turn can never gain mutation tools. The read-only sandbox over `-C <repo>` IS the R236 "read-only access for deeper inspection". |
| Question hygiene + display bounds | `operator_ask.sanitize_question`, `bound_answer`, `validate_identity`, `_read_answer_file` rule | control-sequence strip + redaction BOTH directions, typed refusals (empty/oversized/non-text), campaign-record validation, `turn.failed`-never-mistaken-for-an-answer. |
| Process containment | `process.run`, `minimal_env` | argv arrays, shell=False, kill-on-close Job Object; timeout terminates the WHOLE tree — no background duplicate turn. |
| Model resolution | `policy.resolve_model` | explicit allowlisted model; the provider never chooses. |
| Fresh state (R236 item 3) | `operator_status.compose_status` + `campaign_continuity.load` | labeled durable facts (value/source/confidence; absent = `unknown`, never zero), active-campaign summaries. |
| Thread persistence (R236 items 1–2) | `durable_state.DurableJournal` `state_kv` + `compare_and_swap_state` | namespaced register rows (`codex_channel/...`), CAS single-winner create/update — the exact convention `live_observation.py` (unit I) re-proved. No new database. |
| Redaction on every transmission | `redaction.redact_text/redact_structure`, `operator_channel_cli.emit_payload` | stdout is a transmission (C2); audit rows carry digests + sizes, never raw text. |
| CLI registration seam | `operator_channel_cli.register_operator_verbs` pattern; `cli.py:3423` | unit K adds `register_codex_channel_verbs(sub, add_common)` from a NEW focused module — `cli.py` (grandfathered-oversized) grows by an import + one registration call only. |
| Packet size discipline | `operator_ask.build_ask_packet` byte-ceiling pattern (0A.4 lineage) | hard byte ceiling, visible trimming order, fail-closed refusal — never an unbounded payload. |

**Prove-first executions (settled tree `a5ac4dd`, before any unit-K change):**
`tools/test_agent_supervisor_operator_channel.py` **54/54 passed** (S1–S14: interception
exact-match, fixture-selected event, fail-closed hook, ask bounds/redaction/identity,
durable fallback, skills discipline, queued-input honesty) and
`tools/test_agent_supervisor_reviewer.py` **81/81 passed** (read-only argv contract,
forbidden flags, schema-validated output). The golden pack (M0-T096, accepted at `9f93587`)
re-proved the `state_kv` CAS conventions this unit persists threads with.

## 1. Command surface (R234) and interception map (R235)

CLI: `python -m tools.agent_supervisor codex <subverb> ...` (registered on the EXISTING
surface — no parallel CLI, R034 precedent). Interceptor: `/loop-codex <subverb> ...`
matched as one exact anchored token; the subverb is parsed by the hook, unknown/missing
subverbs BLOCK with usage (fail closed, visible; never half-executed, never to the model).

| Owner types | Hook argv (provider inputs from the session env, as `/loop-ask`) | Provider call? |
|---|---|---|
| `/loop-codex new <question>` | `codex new --codex-executable … --config … --model-selection … -- <question>` | yes (one bounded window) |
| `/loop-codex continue <thread-id> <message>` | `codex continue <thread-id> --codex-executable … -- <message>` | yes (one bounded window) |
| `/loop-codex show <thread-id>` | `codex show <thread-id>` | no |
| `/loop-codex promote <message-id>` | `codex promote <message-id>` | no |
| `/loop-codex close <thread-id>` | `codex close <thread-id>` | no |

The question/message rides behind an explicit `--` end-of-options separator as ONE argv
element (unit-G G5 ADVISORY-2 hardening): leading `-`, metacharacters, quotes, Unicode,
newlines are data, never options, never shell.

**Honest limits (R233 — stated, never worked around):** `/loop-codex` is an ordinary custom
command. Official installed behavior queues ordinary commands submitted while Claude is
responding until the turn ends; only built-in `/btw` surfaces mid-turn. `/loop-codex` is
therefore NOT `/btw`-equivalent and is never represented as such; the honest real-time path
while a producer is responding remains the second terminal
(`python -m tools.agent_supervisor codex …`). Zero-context erasure rests on the measured
2.1.248 `UserPromptSubmit` payload + the documented `decision:"block"` contract (the same
basis unit G shipped with); the live owner-typed zero-context canary remains
**pending-owner-C1**, and the skill documents the truthful fallback (if the model reads the
skill, interception did NOT fire; the fallback consumes context and says so).

## 2. Per-turn bounded context (R236/R237/R238)

Every provider turn receives EXACTLY one `codex_discussion_turn` packet:

1. **Bounded durable thread summary** — maintained by the provider itself (`updated_summary`
   in each validated reply, bounded chars, stored on the thread row; empty ⇒ prior kept).
2. **Bounded recent exchanges** — the last ≤ 6 stored exchanges (each display-bounded).
3. **Fresh current state** — `compose_status` labeled facts + active-campaign summaries
   (sequence, next task), redacted; never history, never the transcript.
4. **Evidence references** — reference guidance + the campaign frozen identity; the packet
   instruction requires commit SHAs, content digests, changed paths, symbols, and test names
   over bare line numbers (R238), both in what we send and what Codex returns.
5. **Read-only deeper inspection** — the reviewer sandbox itself (`-C <repo>` +
   `--sandbox read-only`): Codex reads the repository directly when it needs more; nothing
   is bulk-shipped.

Prohibited content (R237): no full Claude transcript, no full repository, no all-source
dumps, no full logs, no unrelated history — structurally absent (the packet builder has no
input that could carry them) AND size-enforced: hard byte ceiling with a visible trimming
order (state bulk first, then oldest exchanges, recorded in `omitted_for_size`), then a
typed fail-closed refusal. Threads are bounded: a full thread refuses `continue` with
"start a new thread — the summary carries context" rather than silently dropping messages.

## 3. Closed dispositions (R239) and promotion (R240) — decision record

The reply schema (`schemas/codex_discussion_reply.schema.json`) REQUIRES
`disposition` ∈ {ADVICE_ONLY, QUEUE_NEXT_BOUNDARY, REVISE_CURRENT_TASK, PROPOSE_NEW_TASK,
URGENT_PAUSE, STOP_FOR_OWNER}; supervisor-side validation refuses any other value with a
typed error — never a defaulted disposition, never a partial record.

**Nothing in this channel automatically alters Fable's instructions (R239).** Decided
handling, per disposition:

- **ADVICE_ONLY** — displayed; recorded on the thread. No other effect.
- **QUEUE_NEXT_BOUNDARY** — one bounded row appended to the durable boundary queue
  (`codex_channel/boundary_queue`, CAS, bounded depth with visible refusal when full).
  Honest bound (G5 INFO-2): in THIS unit the queue is deliberately write-only and inert —
  no code reads it, nothing is injected into any model context; reading it at a safe
  boundary is orchestrator/later-unit behavior, not unit-K machinery.
- **REVISE_CURRENT_TASK** — displayed with the standing rule: a finding enters the current
  task ONLY through the existing authorized repair route (unit-H2 `repair_gate`, R076–R078);
  the channel records it and changes nothing itself.
- **PROPOSE_NEW_TASK** — parked on the thread, promotable ONLY by the owner-typed
  `/loop-codex promote <message-id>`.
- **URGENT_PAUSE / STOP_FOR_OWNER** — a durable attention row (`codex_channel/attention/…`,
  CAS-idempotent) + audit event; the display names the exact existing owner command
  (`python -m tools.agent_supervisor pause` / the owner action). Deliberately NO automatic
  actuation in this unit: the channel is owner-interactive in the same terminal — the owner
  reading the reply is the actuation path; a provider reply actuating a control would be a
  provider-driven instruction change, which R239 forbids. (The supervisor's own safety
  machinery — breakers, guardrail bridge, stop intents — is unchanged and remains the
  autonomous-safety authority.)

**Promotion is owner-gated by construction (R240):** `promote` is reachable only from the
user-typed command (the skill is `disable-model-invocation: true`; the model cannot invoke
it, and the hook intercepts it pre-model). Promoting writes ONE durable promotion row
(CAS-idempotent; a second promote reports the existing row) recording message id/digest,
thread, disposition, and `status: recorded_awaiting_capture`. A promotion row AUTHORIZES
NOTHING by itself: new features / changed priorities / expanded scope still require durable
directive/task capture through `/directive-compliance` + the ledger before any work — the
row is the owner's explicit approval evidence feeding that existing route, never a bypass.
Only REVISE_CURRENT_TASK and PROPOSE_NEW_TASK messages are promotable (advice and queue
rows have their own lanes; URGENT/STOP are attention, not scope).

## 4. Scenario matrix (executable pack: `tools/test_agent_supervisor_codex_channel.py`)

| # | Class | Scenario | Kind |
|---|---|---|---|
| K1.1 | surface | all five subverbs registered on the existing CLI; no parallel CLI | primary |
| K1.2 | surface | `new` creates a thread + returns reply/disposition/thread-id | primary |
| K1.3 | surface | `continue` appends to the SAME thread; summary + recents ride the next packet | primary |
| K1.4 | surface | `show` prints the durable record verbatim-bounded, NO provider call | primary |
| K1.5 | surface | `close` closes durably; `continue` on closed → typed refusal | boundary |
| K2.1 | interception | exact `/loop-codex …` intercepted (block+erase contract on the fixture-selected event) | primary |
| K2.2 | interception | similar text (`loop-codex`, `/loop-codexes`, "tell me about /loop-codex") passes through untouched | boundary |
| K2.3 | interception | missing/unknown subverb → visible BLOCK with usage; nothing executed, nothing to the model | failure |
| K2.4 | interception | `new`/`continue` without the three provider env inputs → fail-closed block naming the exact second-terminal command | failure |
| K2.5 | interception | `show`/`promote`/`close` run WITHOUT provider inputs (no provider call) | primary |
| K2.6 | interception | unproven event (`UserPromptExpansion`) passes through unfaked; hook consults the fixture | boundary |
| K2.7 | honesty | no `/btw` equivalence claim anywhere in skill/hook/module; queued-input limitation documented verbatim | primary (R233) |
| K3.1 | context | packet = summary + ≤N recents + fresh labeled state + campaigns + guidance — and NOTHING else | primary (R236/R237) |
| K3.2 | context | byte ceiling: visible trimming order, `omitted_for_size`, then typed fail-closed refusal | failure |
| K3.3 | context | recents bound + summary bound enforced; oversized provider summary bounded on store | boundary |
| K3.4 | context | full thread → `continue` refuses with "new thread" guidance; no silent drop | boundary |
| K3.5 | context | stable-reference guidance present in packet instruction + schema description (R238) | primary |
| K4.1 | disposition | schema + validator enforce the closed set; unknown/missing disposition → typed failure, never defaulted | failure (R239) |
| K4.2 | disposition | each of the six values produces exactly its decided effect (§3) and no other durable write | primary |
| K4.3 | disposition | URGENT_PAUSE/STOP_FOR_OWNER: attention row CAS-idempotent + exact command named; NO stop/pause intent written by the channel (module writes no `stop_intent`) | primary (R239) |
| K4.4 | disposition | QUEUE_NEXT_BOUNDARY: bounded queue; full queue → visible refusal | boundary |
| K5.1 | promotion | promote records ONE durable row; second promote reports the existing row (CAS) | primary (R240) |
| K5.2 | promotion | unknown message id / non-promotable disposition → typed refusal | failure |
| K5.3 | promotion | a promotion row changes NO task/ledger/campaign state (no such imports; no file writes) | primary (R240) |
| K6.1 | security | empty/oversized/non-text messages → typed refusals (reused sanitize) | failure |
| K6.2 | security | control sequences stripped + secrets redacted BOTH directions; emitted payloads redacted | primary |
| K6.3 | security | identity refusal outside the campaign root; tampered campaign record refuses | failure |
| K6.4 | security | the turn argv IS the hardened read-only builder (sandbox read-only, forbidden flags absent) | primary |
| K6.5 | security | timeout: tree terminated, owner message durably on the thread, no background duplicate; re-`continue` re-poses | failure |
| K6.6 | security | audit rows carry digests + sizes, never raw question/reply text | primary |
| K7.1 | skill | `.claude/skills/loop-codex/SKILL.md` exists, user-only, thin, documents interception + context cost + fallback | primary |
| K8 | register | executable requirement register: one row per applicable req R231–R240/R246/R248/R249 → proving test(s) | primary (R249 pattern) |

## 5. Module plan (modularity answers, `.claude/rules/code-architecture.md`)

1. Owning responsibility: the operator discussion channel — a NEW responsibility (thread
   persistence + turn orchestration + disposition policy), distinct from single-shot `ask`.
2. Modules: `tools/agent_supervisor/codex_channel.py` (domain: threads/packets/replies/
   dispositions/promotion; target < 600 SLOC) + `tools/agent_supervisor/codex_channel_cli.py`
   (argparse wiring + display, mirroring `operator_channel_cli.py`; target < 300 SLOC) +
   `schemas/codex_discussion_reply.schema.json`. `cli.py` grows by one import + one
   registration line (grandfathered file, minimal delta). The hook grows by the subverb map
   (same file — one interception authority, no second hook).
3. Threshold check: all new files start far below warn (600); `modularity_check` runs after
   `git add`, before submit.
4. No behavior is moved; nothing to extract.
5. Stable public interface: `register_codex_channel_verbs(sub, add_common)` +
   `codex_channel` module functions; existing surfaces untouched.
6. Boundary tests: the K-pack above; existing packs must stay green (operator channel 54,
   reviewer 81, golden 40).
7. CI modularity check must pass before submission.

## 6. Evidence (implementation; settled tree, foreground-chunked)

**Deliverable files:** `tools/agent_supervisor/codex_channel.py` (domain, 632 physical lines
incl. docs — count corrected per DCV note 1; below the 600-SLOC warn band, modularity exit 0) + `codex_channel_cli.py` (wiring) + `schemas/codex_discussion_reply.schema.json`
+ `cli.py` (one import + one registration line) + `operator_ask.py`
(`_read_answer_file` → public `read_answer_file`, one call site) +
`.claude/hooks/loop_command_interceptor.py` (regex alternation + `_codex_argv` subverb map)
+ `.claude/skills/loop-codex/SKILL.md` + `tools/test_agent_supervisor_codex_channel.py`
(K-pack, reusing the unit-G harness by import — one harness authority).

- **K-pack: 52/52 passed** (K1 surface 6, K2 interception 8 — real hook subprocess,
  K3 bounded context 8, K4 dispositions 5, K5 promotion 4, K6 security 7, K7 skill 1,
  K8 executable requirement register 13 — one row per applicable req).
- **Affected packs re-run green:** operator-channel 54/54, golden-run 40/40,
  reviewer 81/81.
- **Whole supervisor suite (freeze-rule baseline re-established):** 3 chunks =
  895 + 895 (2 skipped) + 864 → **2,654 passed, 2 skipped, 0 failed** (was 2,584+2 at
  M0-T096; the growth is this unit's 52 + the K-pack-imported harness collection).
- **Non-supervisor tools suite:** 3 chunks = 279 + 160 (1 skipped) + 120 →
  **559 passed, 1 skipped** — exactly the accepted M0-T096 baseline.
- **Mutation pass: 14/14 KILLED** (accept-any-disposition; drop-STOP_FOR_OWNER;
  summary-erasure; recents-keep-oldest; ceiling-fails-open; CAS→blind-overwrite;
  continue-ignores-closed; thread-full-removed; queue-unbounded; promote-anything;
  promotion-overwrite; hook-executes-unknown-subverbs; attention-row-skipped;
  timeout-drops-owner-message). Honest note: the CAS→blind-overwrite mutation SURVIVED
  the first pass — no test exercised a real concurrent-writer conflict — so
  `test_a_concurrent_thread_write_loses_cleanly_via_cas` was added (red under the
  mutation, green under the real code) and the mutation now dies.
- **ruff 0.13.0 (the CI version): all changed files clean.** (CI's ruff job runs with
  `working-directory: services/api` — untouched by this unit; the repo-root tree carries
  58 pre-existing hits in files this unit never touched.)
- **`modularity_check --check` exit 0** after `git add` (all new files far below warn).
- **CI on the pushed deliverable SHA:** recorded in the progress log at the submit seam.

## 7. Consolidated correction round (gate wave at `eacbb43`; all four verdicts PASS)

Reviewer returns: **G3 PASS** (MINOR-1 blocking-for-acceptance + INFO-1..4), **G4 PASS**
(MINOR-1..4 + INFO-1..4), **G5 PASS** (ADVISORY-1 + INFO-1..3), **DCV PASS 13/13** (notes
1–4). Verbatim reports: `M0-T110-{G3-code-review,G4-qa,G5-security,DCV}.md`. ONE
consolidated round applied every actionable item:

| Finding | Disposition |
|---|---|
| G3 MINOR-1 / G5 ADVISORY-1 (id tokens not protected as data) | **FIXED** — `_codex_argv` validates ids against `^(?:cxt_|cxm_)[A-Za-z0-9]+$` BEFORE argv construction; option-shaped ids are a visible hook refusal ("ids are data, never options; nothing was executed"). New test `test_an_option_shaped_id_is_refused_before_any_execution` (3 shapes); new mutant M16 (validation removed) KILLED. |
| G4 MINOR-1 (`--` hardening untested/unmutated on the codex path) | **FIXED** — `test_free_text_rides_behind_the_end_of_options_separator` imports the hook module directly (provider env patched) and asserts `argv[-2:] == ["--", <hostile dash/metachar/newline message>]` for `new` AND `continue`; new mutant M15 (drop `--`) KILLED. |
| G4 MINOR-2 (non-text refusal untested) | **FIXED** — K6.1 now covers `12345` and `None` → typed `question_not_text`. |
| G4 MINOR-3 (inbound reply redaction untested) | **FIXED** — `test_a_secret_inside_the_reply_is_redacted_before_store_and_display`: a fake `ghp_` token in reply + updated_summary is absent from `outcome.reply` and the entire stored thread record. |
| G4 MINOR-4 (`close` no-provider path untested) | **FIXED** — `test_close_executes_without_provider_inputs` (real hook subprocess → executed → `unknown_thread`). |
| G3 INFO-1 (45 s effective hook window undocumented in the skill) | **FIXED** — SKILL.md now states the ~45 s interception-path bound and that `--window` 90 s applies only off-hook. |
| G3 INFO-4 / G4 INFO-2 (`new` refusal says "message" not "question") | **FIXED** — per-verb noun in `_codex_argv`. |
| G4 INFO-3 (promote-on-closed-thread undocumented) | **FIXED** — documented as deliberate in the `promote_message` docstring (closing a discussion never voids the approval path). |
| G5 INFO-2 (queue "surfaced at next boundary" aspirational) | **FIXED** — §3 wording corrected: the queue is write-only and inert in this unit. |
| DCV note 1 (line-count imprecision) | **FIXED** — §6 corrected to 632 lines. |
| G3 INFO-2 / G5 (pending-owner-C1 canary) | **NO CHANGE NEEDED** — already stated honestly; remains owner-gated. |
| G3 INFO-3 (resolution-unusable branch / attention-CAS return untested), G4 INFO-1 (transitive assertions), G5 INFO-1 (45s/90s nesting — inherited unit-G structure), G5 INFO-3 (fail-open-to-pass-through posture) | **ACCEPTED AS-IS** — low-value additions / inherited accepted structure / deliberate documented posture; carried as non-blocking notes. |

**Corrected-identity evidence:** K-pack **56/56** (52 + 4 new); operator-channel 54/54
(110 combined); mutation now **16/16 KILLED** (M15/M16 added); ruff clean; secret scan
PASS (the new fake inbound token carries its own justification pragma); modularity exit 0;
CI on the resubmitted SHA recorded in the progress log.

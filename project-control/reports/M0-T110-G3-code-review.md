VERDICT: PASS

# M0-T110 — G3 independent code review (unit K: `/loop-codex` Codex discussion channel)

**Reviewed SHA:** `eacbb43bd7dc0df4584476a2c0ba9ab01b1006c6` (verified `git rev-parse HEAD` == expected).
Deliverable content identity `ba25516` (impl `e632da2` + CI-red `secretscan:allow` pragma); the
`b063a18`/`eacbb43` submission-bundle commits touch only `project-control/`.
**Reviewer:** independent G3 (read-only). **Verdict:** PASS — no blocking or major defects; one MINOR
hardening correction listed as blocking-for-acceptance, plus INFO notes.

## Scope reviewed
`git diff 1b5513f..HEAD` over the 8 named files: `+1868 / -6`.
- `tools/agent_supervisor/codex_channel.py` (632 lines, new) — domain
- `tools/agent_supervisor/codex_channel_cli.py` (222, new) — wiring/display
- `tools/agent_supervisor/schemas/codex_discussion_reply.schema.json` (48, new)
- `tools/agent_supervisor/cli.py` (+2: one import + one registration call)
- `tools/agent_supervisor/operator_ask.py` (+7/-6: `_read_answer_file` → public `read_answer_file`, one call site)
- `.claude/hooks/loop_command_interceptor.py` (+82: regex alternation + `_codex_argv`)
- `.claude/skills/loop-codex/SKILL.md` (new, 36 lines)
- `tools/test_agent_supervisor_codex_channel.py` (846, new)

## Commands run (all read-only) and results
| Command | Result |
|---|---|
| `git rev-parse HEAD` | `eacbb43…` (== expected reviewed head) |
| `git diff 1b5513f..HEAD --stat -- <8 files>` | 8 files, +1868/-6 (matches packet) |
| `python --version` | Python 3.11.9 (workstation interpreter class) |
| `pytest tools/test_agent_supervisor_codex_channel.py -q` | **52 passed** in 5.14s |
| `pytest tools/test_agent_supervisor_operator_channel.py -q` | **54 passed** in 15.65s |
| `pytest tools/test_agent_supervisor_reviewer.py -q` | **81 passed** in 12.66s (reused `build_argv` contract, no regression) |
| `python tools/modularity_check.py --check` | selected 325 files; **failures 0**; `codex_channel*` not flagged (below warn) |
| `ls project-control/tasks/M0-T11*.json` | T110/T111/T112 present (R246 durable sequence) |
| `grep -rn _read_answer_file` | 0 hits (rename clean); `read_answer_file` used in operator_ask (self) + codex_channel |
| CLI smoke: `build_parser()` + `codex --help` | parser builds; subverbs `{new,continue,show,promote,close}` registered; rc 0 |

## Correctness — verified
- **Thread CAS single-winner (create-vs-update expected value).** `durable_state.compare_and_swap_state`
  runs read+compare+write inside one `BEGIN IMMEDIATE`; `expected is None` means "must not exist" and a
  stored JSON `null` does **not** match it. `_store_thread` passes `expected = None if create else dict(before)`.
  Create (`new`) requires absence; update (`continue`/`close`/timeout) requires byte-equality with the
  pre-turn record → a concurrent write loses cleanly with typed `thread_conflict`, never a silent overwrite.
  Reproduced by `test_a_concurrent_thread_write_loses_cleanly_via_cas` (interloping runner mutates the row
  mid-turn; asserts `thread_conflict` and that the concurrent write survives).
- **Timeout persistence path.** On `result.timed_out`, the contained tree is already terminated (Job Object
  kill-on-close via `process.run`); only the owner message is persisted with the same `create` flag, so
  `show` stays honest and re-`continue` re-poses. Reproduced by `test_a_timeout_terminates_the_tree_and_keeps_the_owner_message`.
- **Disposition effects = durable rows only, never actuation (R239).** `_apply_disposition_effects` writes
  a bounded boundary-queue row (QUEUE_NEXT_BOUNDARY) or a CAS attention row (URGENT_PAUSE/STOP_FOR_OWNER,
  `actuated: False`); ADVICE/REVISE/PROPOSE write no side rows. `test_each_disposition_produces_exactly_its_decided_effect`
  asserts exactly 1 queue row, 2 attention rows, 0 promotion rows across all six; `test_the_module_imports_no_actuation_surface`
  and reading the module confirm no `stop_intent`/`repair_gate`/`project_control`/`github_flow` import.
- **Promotion idempotency (R240).** `promote_message` CAS-writes with `expected=None`; a second promote
  reads and returns the existing row (`already_promoted: True`); only PROMOTABLE_DISPOSITIONS are eligible;
  the row carries `authorizes_nothing: True` + a `/directive-compliance` `required_next`. Reproduced by
  `test_promote_records_one_idempotent_durable_row`, `…_non_promotable_messages_refuse`, `…_touches_only_channel_state`.
- **Boundary-queue CAS retry loop.** Bounded (`MAX_BOUNDARY_QUEUE=32`) with a visible `queue_full` result
  (reply still recorded), a 3-try CAS loop, and a `queue_contended` fallback surfaced in the CLI. Reproduced
  by `test_a_full_boundary_queue_is_a_visible_refusal_not_a_drop`.
- **Bounded packet (R236/R237/R238).** Exactly the R236 key set; recents capped at 6; visible trim order
  (state bulk → oldest exchanges → `omitted_for_size`) then typed `packet_too_large` fail-closed; summary
  bounded on store; empty summary keeps prior; full thread refuses `continue` with "new thread" guidance.
  All reproduced in `K3BoundedContext`.

## Contracts — verified
- Reuse of `operator_ask.sanitize_question` / `bound_answer` / `validate_identity` / `read_answer_file`
  confirmed by source: control-sequence strip + redaction both directions, typed refusals
  (`empty_question`/`question_too_large`/`question_not_text`, `identity_mismatch`/`campaign_record_invalid`),
  and the `turn.failed`-never-an-answer rule. The channel maps every `AskError` to `ChannelError` with the
  **same code** (one error type).
- `codex_reviewer.build_argv` read-only invariant holds: `--sandbox read-only` is mandatory (any other value
  raises), `FORBIDDEN_REVIEWER_FLAGS` refused, `--ephemeral --ignore-user-config --strict-config --json`,
  output-schema = `codex_discussion_reply.schema.json`. Reproduced by `test_the_turn_rides_the_hardened_read_only_argv`.
- `emit_payload` redacts stdout via `redact_structure` (both `--json` and line paths). Audit rows carry
  `reply_digest` + sizes, never raw text — reproduced by `test_the_audit_trail_is_privacy_bounded`.
- Refusal-code mapping: `_UNSAFE_CODES = {identity_mismatch, campaign_record_invalid}` → `refusals.UNSAFE`;
  everything else → `STALE_STATE`. `resolve_model(role="primary")` does not invoke `assert_advisory_allowed`,
  so `purpose="codex_discussion"` is fine; `ModelResolution.usable`/`model`/`reason_code`/`reason` all exist.

## Error paths / fail-closed — verified
- `validate_reply` rejects non-object, empty reply, and any disposition outside the closed set (missing key
  → `None` → typed `disposition_invalid`), never defaulted; failed turns persist **no** thread row
  (`test_an_unknown_or_missing_disposition_is_a_typed_failure` asserts no `THREAD_KEY_PREFIX` rows).
- `read_answer_file` returning `None` → typed `no_reply`; malformed reply → typed, never echoed.

## Hook safety — verified
- Exact-match anchored regex `^/(loop-(?:…|codex))(?:\s+([\s\S]*))?$`: `/loop-codexes`, `/loop-codex-new`,
  `loop-codex …`, and "tell me about /loop-codex …" all pass through untouched (`test_similar_text_passes_through_untouched`).
- `_codex_argv` fail-closed on every malformed shape (missing/unknown subverb, missing id, missing message,
  extra text after an id-only subverb, missing provider env) — all BLOCK visibly, nothing executed, nothing
  to the model; real-subprocess `K2Interception` covers each branch, and `UserPromptExpansion` passes through
  unfaked. Free text rides one argv element behind an explicit `--` end-of-options separator.
- `_codex_argv` shape map validated; the 45s subprocess timeout (`SUBPROCESS_TIMEOUT_SECONDS`, env-overridable)
  is inherited by `/loop-codex new|continue` exactly as `/loop-ask` — `subprocess.run` kills the child on
  timeout and the CLI's own Job Object kills the codex grandchild (no orphan).
- **Python 3.11/3.12 compat:** the hook carries `from __future__ import annotations`, so `list[str] | None`,
  `dict[str, tuple[bool,int,bool]]`, etc. are never evaluated at runtime; stdlib-only imports. The K2 tests
  executed the hook as a real subprocess under Python 3.11.9 and passed.

## Maintainability / modularity — verified
- `cli.py` grew by exactly one import + one `register_codex_channel_verbs(sub, add_common)` call (diff
  confirmed). New domain (`codex_channel`) vs wiring (`codex_channel_cli`) vs schema separated cleanly; no
  actuation/ledger coupling; no dumping ground. `modularity_check --check` reports 0 failures and does not
  flag either new file (both below the 600-SLOC warn). No import cycle (CLI smoke + K-pack import succeed).

## Findings

### BLOCKING — none.
### MAJOR — none.

### MINOR-1 (blocking-for-acceptance) — hook: id tokens are not protected as data
`.claude/hooks/loop_command_interceptor.py`, `_codex_argv`. The free-text tail rides behind `--` (good), but
the id argument (`thread_id`/`message_id`) is appended **before** `--` via `tail += ids`. An id beginning with
`-` (e.g. `/loop-codex show --checkout=/x`, `promote --help`) is therefore handed to argparse as an option, not
data — contrary to the unit-G G5 ADVISORY-2 hardening intent this module cites ("leading `-` … are data, never
options"). **Not exploitable** (owner-only, model-uninvocable surface; a single token is either the positional
or an option, so consuming it as an option leaves the required positional missing → argparse exit 2 → fail
closed; ids are prefix-validated downstream), so this is defense-in-depth/consistency, not a vulnerability.
**Smallest fix:** in `_codex_argv`, after extracting `id_parts[0]`, reject any id that `startswith("-")` with a
visible block reason (mirrors the existing fail-closed pattern), or place ids behind their own `--`.

### INFO-1 — interception-path effective window is 45s, not the CLI's 90s default
`DEFAULT_TURN_WINDOW_SECONDS = 90.0` is unreachable via interception because the hook kills the subprocess at
`SUBPROCESS_TIMEOUT_SECONDS = 45`. This is documented (self-check §5), precedent-consistent with `/loop-ask`,
and fail-closed (no partial state; visible timeout message; second-terminal fallback with no cap). Optional:
state the 45s effective cap in `SKILL.md` so the `--window` help isn't read as promising 90s on the hook path.

### INFO-2 — R235 live zero-context canary honestly deferred
The code emits the correct `{decision:"block", reason}` UserPromptSubmit contract (real-subprocess K2 tests
assert the exact key set on the measured 2.1.248 fixture). The live owner-typed zero-context proof on the
installed Claude Code version remains pending-owner-C1, consistent with the accepted unit-G posture and the
R233 honesty prohibition (no `/btw` equivalence anywhere — verified in hook/skill/module). This is a
directive-completeness item for the DCV/G4 pass, not a code defect; no false claim is made.

### INFO-3 — minor K-pack coverage gaps
The `resolution.usable == False` branch in `_run_turn` and the ignored return of the attention-row CAS are not
directly exercised by the K-pack (the model-resolution path is mirrored by `operator_ask` coverage; the
attention CAS always succeeds for a fresh per-turn `message_id`). Behavior is straightforward; non-blocking.

### INFO-4 — cosmetic
`/loop-codex new` with no text blocks with "new needs a message" while the usage line reads "new <question>".
Wording only.

## Verified vs taken on faith
**Verified (reproduced this session):** reviewed SHA; diff scope; K-pack 52/52; operator-channel 54/54;
reviewer 81/81; modularity 0 failures; CLI parser + subverb registration; clean `read_answer_file` rename;
CAS create/update semantics (source); `build_argv` read-only invariants (source); redaction in
`sanitize/bound/emit_payload` (source); hook regex exact-match, fail-closed branches, and Py3.11/3.12 hint
compatibility (ran under 3.11.9); T110/T111/T112 task files (R246).
**Taken on faith (not reproduced):** the 14/14 mutation kill (scratchpad driver — assessed by inspecting that
the CAS-conflict, disposition-effect, promotion-idempotency, redaction, and timeout tests genuinely exercise
behavior rather than source strings); the full supervisor suite 2,654 passed and non-supervisor 559 (I ran 3
representative packs green + modularity, not the whole suites); CI 20/20 at `ba25516`; the live installed-version
zero-context canary (R235, honestly deferred — not reproducible without the platform + owner input).

**Verdict: PASS.** Blocking-for-acceptance correction: **MINOR-1** (reject `-`-leading ids / place ids behind `--` in `_codex_argv`). INFO-1..4 are advisory.

*(Saved verbatim from the reviewer's return by the orchestrator; transport entity-decoding only — `&lt;`/`&gt;` decoded.)*

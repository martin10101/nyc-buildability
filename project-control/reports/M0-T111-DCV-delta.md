DELTA VERDICT: PASS

# M0-T111 DCV — Delta Re-attestation

**Corrected deliverable identity:** `8574c58b3425137aa41457c6d7ba3c3923b8605e`; **branch tip:** `6cbac33e270758cda0e49c5e9e87bb55e92804de` (confirmed via `git rev-parse HEAD`). `git diff --stat 8574c58..HEAD -- tools/` is empty → the production source under review at HEAD is byte-identical to the deliverable identity; `8574c58..HEAD` is control-plane only (task/state/report JSON). Read-only pass; no live send performed.

**Delta production surface** (`git diff 4ce8131..8574c58 -- tools/`): `telegram_sink.py`, `telegram_sink_cli.py`, and the test pack only. `.redaction` is an existing in-package module (`tools/agent_supervisor/redaction.py::redact_text`) — no new dependency. **L-pack: 35 passed** (was 31; +4 new tests) — reproduced. `validate_directive_compliance.py --check` EXIT=0; `modularity_check.py --check` EXIT=0. Module sizes 375 / 124 lines (focused; +34 / +3).

## Delta-relevant rows re-verified

| Req | Verdict (stands) | Delta evidence I reproduced |
|---|---|---|
| **R242** one-way | SATISFIED | No new receive surface: grep of both modules for `getupdates\|webhook\|long_poll\|offset\|receive\|inbound\|recv\|getme\|listen` → only the honest docstring. `_already_queued` only READS the local durable `QUEUE_KEY` (not a Telegram receive). The one-way scan was genuinely hardened, not weakened: `functional_text` now folds `ast.Import`/`ast.ImportFrom` module+alias names into the blob (catches `from subprocess import run`) and matches `exec/eval/subprocess/socket/http.client/asyncio` as EXACT identifier tokens. `L4OneWay::test_no_receive_or_command_surface_exists` reproduced green. |
| **R243** secrets | SATISFIED (strengthened) | Full delta secret scan (`git diff 4ce8131..8574c58`, token/`ghp_`/`xox`/`AKIA` patterns): only the two new fake sentinels `ghp_FAKEsummaryLeakSentinel…` / `ghp_FAKEtaskidLeakSentinel…` — both obviously fake, both carry `# gitleaks:allow secretscan:allow` pragmas (pragma count = 2), and both are leak-absence-asserted (`assertNotIn(secret, …)`). No real credential value anywhere. `compose_text` now additionally routes `task_id`/`run_id` through `redact_text` (identifier fields previously rode the builder unredacted) — a strict strengthening of the secrecy posture. |
| **R244** retries/dedup/isolation | SATISFIED (strengthened) | `_already_queued` suppression bounds queue growth under a sustained outage while keeping at-least-once (the one queued item is untouched) — `test_a_failing_identical_condition_does_not_grow_the_queue` proves queue depth stays 1 across 4 repeats. New `MAX_OUTBOUND_CHARS=3500` hard cap with visible `...[truncated]` marker bounds outbound size (test reproduced). `deliver` still carries `except Exception … never raise`; `queue.deliver(…, unit_can_proceed=True)` unchanged; **no `unit_can_proceed=False` anywhere** → `run_must_pause` stays structurally False. |
| **R245** owner-gated live send | HOLD-IN-FORCE-AND-HONORED | New `test_cli_canary_with_flag_but_no_env_queues_without_a_send` clears `SUPERVISOR_TELEGRAM_BOT_TOKEN`/`CHAT_ID` via `mock.patch.dict(clear=True)` then runs `telegram canary --live-canary-authorized-by-owner`; `resolve_credentials` raises `telegram_not_configured` inside `deliver` BEFORE any transport call → `attempts=0`, `delivered=False`, `still_queued=True`. The default-opener transport closure is constructed but never invoked; no socket. Live send still NOT fired by this unit. |
| **R248** no prohibited surface | SATISFIED | Full-delta forbidden-path scan (`4ce8131..HEAD`): no `.claude/hooks`, no `settings.json`, no dependency manifest/lockfile, no `apps/services/supabase`, no control tooling. No new external/third-party import in the delta (only `QUEUE_KEY`, `redact_text` in-package; `NotificationQueue` moved to a hygiene import; `unittest.mock`/`CODEX_HOLD_KEY` in tests). Stdlib + in-package only. |

## Unchanged rows (delta does not touch their primary evidence)

R231, R232, R246, R249 — evidence (verbatim capture / campaign hold / three task packets / owner-report §§1–5) unchanged; validator EXIT=0. **R241** — production `CONDITIONS`/`CONDITION_RISK` values unchanged; the delta only *tightened* its tests (exact `CONDITION_RISK` dict assertion; a second durable quota source in discovery) — still SATISFIED.

**All 10/10 verdicts stand at the corrected identity `8574c58` (tip `6cbac33`).** The correction items (G3 INFO-3 / G4 MINOR-1..5 / G5 MINOR-1,2 / G5 ADVISORY-1) are behavior-strengthening or test-hardening only; none weakens any obligation, and no new receive surface, secret value, or prohibited surface was introduced.

*(Saved verbatim from the reviewer's SendMessage return by the orchestrator.)*

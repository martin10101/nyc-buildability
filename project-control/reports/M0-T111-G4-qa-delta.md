DELTA VERDICT: PASS

# G4 QA Delta Re-Attestation — M0-T111 (consolidated correction round)

**Identity.** Branch tip `6cbac33e270758cda0e49c5e9e87bb55e92804de` (read from `refs/heads/control/D-024-fable-codex-loop`); deliverable-content identity `8574c58b` per coordinator. Reviewed the corrected files in the ctl24 checkout.

**Re-ran (this delta):**
- `pytest tools/test_agent_supervisor_telegram_sink.py -v` → **35 passed** (was 31; +4 new tests).
- `ruff check` (telegram_sink.py, telegram_sink_cli.py, L-pack) → **All checks passed** (0.13.0).
- Regression, full-CLI dispatch: `pytest operator_channel + codex_channel` → **110 passed** (54+56), no regression from the source changes.
- Two adversarial probes: hardened `functional_text` (exec/subprocess/socket incl. import-only caught as exact identifiers; honest "execution" display string is NOT a false positive), and direct read of `compose_text`, `_already_queued`, `notify_condition`, `NotifyOutcome`.

**Per-finding closure verdicts:**
- **MINOR-1 — CLOSED.** `test_cli_canary_with_flag_but_no_env_queues_without_a_send` drives the authorized CLI glue with `--live-canary-authorized-by-owner` under `mock.patch.dict(os.environ, ..., clear=True)` with both `SUPERVISOR_TELEGRAM_*` removed; asserts `delivered False`, `still_queued True`, `telegram_not_configured`, `attempts == 0`. Safe: env cleared inside the test, no network, flag never fired against a configured env. The previously-untested canary orchestration is now exercised.
- **MINOR-2 — CLOSED.** `test_the_same_condition_for_a_different_task_is_not_deduplicated` (approval_waiting, identical summary, M0-T111 vs M0-T112 → both delivered, `b.deduplicated False`, `delivered == 2`) pins `task_id` in the dedup key; mutant M14 (digest drops task_id) killed.
- **MINOR-3 — CLOSED.** L1.1 now asserts exact `CONDITION_RISK` dict equality for all eight mappings; a within-`RISK_CLASSES` swap (M15) now fails.
- **MINOR-4 — CLOSED.** `functional_text` folds `ast.Import`/`ast.ImportFrom` module+alias names into the blob, and exec/eval/subprocess/socket/http.client/asyncio are matched as exact whole-line identifiers (dead `"exec("`/`"eval("` paren-needles removed). Probe confirms `from subprocess import run`, `import socket`, and a bare `exec()` are all caught, and the honest "no … execution" string does not false-positive. The one-way backstop is now sound; direct read still confirms the actual code is one-way.
- **MINOR-5 — CLOSED.** L2.2 now injects a `ghp_`-prefixed fake token at the START of the summary (survives the 400-char bound) and asserts its absence from the sent text — genuinely proving compose-path redaction, not truncation.
- **INFO-1 — ADDRESSED.** `compose_text` redacts `task_id`/`run_id` via `redact_text` and applies a hard `MAX_OUTBOUND_CHARS` total cap with a visible `...[truncated]` marker (`test_identifier_fields_are_redacted_and_the_total_is_bounded`; mutants M17/M18).
- **INFO-2 — ADDRESSED.** L1.3 exercises both quota keys (`LIMIT_RECORD_KEY` + `CODEX_HOLD_KEY` → two `quota_refusal_hold` rows); L5.1 asserts `calls[0]["timeout"] == 5.0` (sink→transport timeout forwarding).
- **INFO-3 — ADDRESSED.** `_already_queued` + the `notify_condition` `already_queued` branch (new `NotifyOutcome.already_queued`) suppress re-enqueue of an identical pending item; the new test proves queue depth stays 1 across four outage repeats (mutant M16).

**One new non-blocking observation (INFO, optional):** `_already_queued` recomputes its comparison digest from the STORED queue item (whose `summary` is the redacted/400-char-bounded value), whereas the notify-time digest is over the RAW summary. For summaries that redaction or the length bound alters, the two digests differ, so the growth-suppression silently no-ops and the queue reverts to the prior enqueue-each-time behavior. No requirement is broken (R244 loop-never-stops holds; at-least-once preserved; no wrong suppression — a false match needs a negligible digest collision); it only weakens the best-effort growth bound for redacted/truncated summaries. Optional hardening: compare against the notify-time digest (e.g., stamp it on the queued item) or normalize both sides identically. Not required for this gate.

**Mutation (18/18, producer-reported).** Killing tests for the five new mutants (M14 task_id, M15 risk-swap, M16 re-enqueue, M17 identifier-redaction, M18 outbound-cap) all exist and assert the claimed behavior; I did not re-run the mutation harness (none committed) but verified the tests independently.

All five MINOR findings from the base gate are closed, all three INFO items addressed, no regression, ruff clean, L-pack 35/35. Delta accepted.

*(Saved verbatim from the reviewer's SendMessage return by the orchestrator.)*

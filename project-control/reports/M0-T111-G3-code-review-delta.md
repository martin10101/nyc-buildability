DELTA VERDICT: PASS

# M0-T111 G3 Code Review — Delta Re-Attestation

**Gate:** G3 (independent code review) — delta re-attestation of the consolidated correction round
**Deliverable content identity reviewed:** `8574c58b3425137aa41457c6d7ba3c3923b8605e`
**Branch tip:** `6cbac33e270758cda0e49c5e9e87bb55e92804de` (HEAD; control-plane only on top; CI reported 20/20 green at the tip)
**Delta base (prior review identity):** `4ce8131`
**Reviewer role:** read-only, independent
**Verdict:** **DELTA VERDICT: PASS** — MINOR-1 closed; INFO-3 closed; INFO-2 bounded for the common case with one honest residual (below); no regressions; no new correctness/safety defects.

## Commands re-run (read-only, at the delta)

| Command | Result |
|---|---|
| `git rev-parse HEAD` | `6cbac33…` (tip) |
| `git diff --stat 4ce8131..8574c58 -- . ':(exclude)project-control'` | only `telegram_sink.py` (+45/-…), `telegram_sink_cli.py` (+8/-…), test file (+129/-…); `cli.py` unchanged in the delta |
| `git diff --name-only 4ce8131..8574c58 -- notifications.py codex_channel.py resume_scheduler.py redaction.py models.py` | empty — **frozen S13.10 boundary still untouched** |
| `python -m pytest tools/test_agent_supervisor_telegram_sink.py -q` | **35 passed** (was 31; +4 new tests) |
| `python -m pytest .../adversarial.py .../endurance.py -q` | **187 passed** — no regression |
| `ruff check` (v0.13.0) on the 3 changed files | **All checks passed!** |

## Findings re-checked against my prior review

**MINOR-1 — CLOSED (verified).** `telegram_sink_cli.py` now imports `NotificationQueue` from `.notifications` inside the notifications import block, and it is removed from the `.telegram_sink` import block. The re-export coupling is gone; the CLI now sources all four notifications symbols (`DELIVERED_KEY`, `QUEUE_KEY`, `NotificationQueue`, `build_notification`) from their owning module. Import hygiene resolved.

**INFO-3 — CLOSED (verified).** `MAX_OUTBOUND_CHARS = 3_500` added; `compose_text` now truncates to `text[:MAX_OUTBOUND_CHARS-15].rstrip() + " ...[truncated]"`. The marker is exactly 15 chars, so the result is `<= 3500` (bounded; `rstrip` can only shorten). New test `test_identifier_fields_are_redacted_and_the_total_is_bounded` proves `len(compose_text(where_to_review="r"*5000)) <= MAX_OUTBOUND_CHARS` and that `"[truncated]"` is present. Safely under Telegram's 4096 limit.

**INFO-2 — BOUNDED for the common case (verified), one honest residual.** New `_already_queued(journal, digest)` scans the durable `QUEUE_KEY`; when an item with a matching `_dedup_digest` is already awaiting delivery, `notify_condition` returns a visible `already_queued=True, still_queued=True` outcome (with a `telegram_already_queued` audit line) instead of re-enqueueing. Precedence is correct — it runs after `_dedup_seen` (delivered) and before `build`/`enqueue`, so nothing new is built or queued on that path. At-least-once is preserved (the original queued item still delivers). Test `test_a_failing_identical_condition_does_not_grow_the_queue` proves depth stays 1 across 5 failing emissions. This is strictly better than before and non-regressive.
- *Residual (MINOR, non-blocking, no action required to pass):* `_already_queued` recomputes the digest from the **stored** queue item's `reason`/`task_id`/`summary`, whereas `notify_condition`'s digest uses the **raw** `summary` argument. For the eight condition names, `reason` is stored unchanged, and for short/clean summaries the stored summary equals the raw one, so the digests match (the tested path). But for a summary that `build_notification` alters — redacted content or > 400-char truncation — the recomputed digest diverges and `_already_queued` returns False, so that specific sub-case would still re-enqueue. This only affects queue-growth bounding (never correctness, secrecy, or at-least-once) for redaction/truncation-altered summaries under a sustained outage, in shadow-only unwired code. Worth a note for the M0-T112 seam-wiring unit; not a delta defect.

**INFO-1 / INFO-4 / INFO-5 — accepted-as-is, consistent.** The delta's CODEX_HOLD_KEY discovery test now asserts two `quota_refusal_hold` rows (one per durable source), confirming INFO-5 is intended source-level reporting. INFO-1's run_id/where_to_review-insensitive dedup semantics are now applied consistently by `_already_queued` (same documented design choice, no new surprise).

## Other round items (G4/G5) — spot-verified for correctness, no concern

- **Identifier redaction (G5 MINOR-2):** `compose_text` now passes `task_id`/`run_id` through `redact_text(...).value` before composing — closing the gap that these fields rode through the S13.10 builder unredacted. New test injects a fake `ghp_…` token into both and asserts its absence from the composed text. Discarding the redaction `.count` here is immaterial (identifiers aren't part of the notification's stored `redaction_count`). Sound.
- **Compose-path redaction test (G4 MINOR-5):** `test_the_summary_is_hard_bounded_and_text_redacted` now injects a fake token into the summary and asserts it is absent from the sent text. Sound.
- **One-way scan hardening (G5 MINOR-1 / G4 MINOR-4):** `functional_text` now folds `ast.Import`/`ast.ImportFrom` module + alias names into the blob, and `exec`/`eval`/`subprocess`/`socket`/`http.client`/`asyncio` are matched as exact whole-line identifiers (via a `set(splitlines())` membership) rather than substrings. This catches import-based evasion (`from subprocess import run`) while eliminating the false-positive risk on the honest "no ... execution" display strings (which appear as whole-sentence lines, not the bare token). AST extraction guarantees each Name/attr/import-name is its own line, so a real `exec(...)`/`subprocess.run(...)` still surfaces its identifier. Sound hardening, no hole introduced.
- **Exact `CONDITION_RISK` assertion (G4 MINOR-3):** L1.1 now asserts the full literal map, catching within-`RISK_CLASSES` swaps (mutant M15). Matches source exactly. Sound.
- **Timeout forwarding (G4 INFO-2):** L5.1 now asserts `calls[0]["timeout"] == 5.0`, pinning that the sink forwards its configured timeout to the transport. Sound.
- **Authorized-canary-no-env (G4 MINOR-1):** New test clears both env vars via `mock.patch.dict(..., clear=True)`, runs `telegram canary --live-canary-authorized-by-owner`, and asserts `delivered=False`, `still_queued=True`, `attempts=0`, detail `telegram_not_configured`. I traced it: the authorized path constructs the real transport but `sink.deliver` calls `resolve_credentials` first, which refuses before any `open_url` call — so the authorized glue is exercised with **zero** transport/socket invocation. This is a safe, valuable proof that R245's live send never fires when the env is absent even on the authorized path. Sound.

## What I re-checked vs. taken on faith

**Independently verified (this delta pass):** the full delta diff of all three changed deliverable files; MINOR-1 import relocation; the `MAX_OUTBOUND_CHARS` bound arithmetic and truncation marker; the `_already_queued` precedence, match logic, and its digest-source residual; identifier redaction in `compose_text`; the one-way scan hardening logic; the exact `CONDITION_RISK` assertion; frozen-boundary and forbidden-path exclusion; L-pack 35/35 and adversarial/endurance 187/187 reproduced green; ruff clean.

**Taken on faith:** the producer's "mutation 18/18 killed" and "CI 20/20 green at the tip" (I ran only the named packs). Neither affects the delta code-correctness verdict; the mutant classes named (M15–M18, M16) map to behaviors I confirmed present in source and covered by the reproduced tests. Full D-024 requirement-to-evidence remains the `directive-compliance-verifier`'s province (producer ≠ verifier).

**Conclusion:** The correction round faithfully closes MINOR-1 and INFO-3, materially bounds INFO-2 for the realistic case, and lands the additional G4/G5 hardening without regression or new defect. The one residual (queue-growth bound is best-effort for redaction/truncation-altered summaries) is non-blocking and non-regressive. **DELTA VERDICT: PASS.**

*(Saved verbatim from the reviewer's SendMessage return by the orchestrator; transport entity-decoding only — `&lt;`/`&gt;` decoded.)*

# M0-T114 — Residual fixes (the three pinned non-blocking certification residuals)

Task: M0-T114 (Amendment 9 R258 carry → Amendment 12 R272 execution; rows R258/R272/R273).
Producer: fable-orchestrator-session. Supervisor-freeze qualifying evidence:
**D-024-R258/R272**. Reliability standard sections applied: §1, §2, §3.1/§3.3/§3.4, §8.

## Residual 1 — `telegram_sink` queue-growth suppression digest mismatch — FIXED

**Defect (pinned by all three T111 delta reviewers):** `notify_condition` computed the
queue-comparison digest from the RAW caller summary, while queued items store the
POST-BUILDER summary (`build_notification` redacts and truncates to `MAX_SUMMARY_CHARS`).
Any summary the builder ALTERS therefore never matched, and an identical failing
notification re-enqueued on EVERY retry during an outage — unbounded growth for exactly
the altered-summary class the suppression existed to bound.

**Fix (smallest fitting change):** the `_already_queued` check moved AFTER
`build_notification` and compares `_dedup_digest(condition, task_id,
notification.summary)` — post-builder vs post-builder, like-for-like. The delivered-dedup
path (`_dedup_seen`/`_dedup_record`) already compared raw-vs-raw consistently and is
UNCHANGED. `_already_queued` itself is unchanged (it always digested stored items
correctly); only the caller's comparison operand was wrong. At-least-once is preserved
(the queued item still delivers; nothing is dropped); for unaltered summaries raw == built
so behavior is identical.

**Red → green → revert-proof:**
- RED (unchanged code): `python -m pytest tools/test_agent_supervisor_telegram_sink.py
  -k "builder_altered_summary" -q` → **FAILED** (queue grew to 2; `already_queued` False).
- GREEN: L-pack **36/36** (35 + this test).
- REVERT-PROOF: `git stash push telegram_sink.py live_observation.py` → both defect tests
  FAILED → `git stash pop` → both passed.

## Residual 2 — `live_observation.py` raw `source_record_key` — FIXED (one line)

**Defect (unit-I G-report one-liner):** the register row wrote the RAW
`str(source.get("source_record_key", ""))` even though the SANITIZED value was already
computed in the `sanitize_structure` input two lines above — the one copied scalar that
bypassed the boundary sanitizer.

**Fix:** the record now reads `sanitized.value["source_record_key"]`. One line; the
sanitizer input set is unchanged (the key was already being sanitized — the result was
simply never used).

**Red → green:** RED: `python -m pytest tools/test_agent_supervisor_golden_run.py
-k "source_record_key_is_sanitized" -q` → **FAILED** (a key-shaped token embedded in a
source record key reached the register raw). GREEN: golden pack **41/41** (40 + this
test); the test proves `[REDACTED` appears and the raw token does not. Revert-proof shared
with residual 1 (same stash pair).

## Residual 3 — unit-K boundary-queue write-only/inert notes — DISPOSITION ONLY (no code)

The unit-K reviewers noted the codex-channel boundary queue is write-only/inert (items are
recorded for the next safe boundary but no consumer drains them yet) plus a report
line-count nit. `codex_channel.py` is OUTSIDE this packet's allowed_paths, and the
reviewers classified the behavior as BY DESIGN for the accepted unit-K contract
(promotion/consumption is owner-gated future work, not a defect): recording is the
contracted behavior; draining belongs to the owner-gated promotion flow. DISPOSITION:
documented here as inert-by-design, carried as a note on the accepted unit-K record; any
code change there requires its own packet and would re-trigger R247 again. No code was
touched (R272 no-broadening honored).

## Evidence summary

- Affected sweep (telegram, golden, adversarial, endurance, phase1, operator-channel,
  codex-channel, reviewer): **535 passed, 0 failed**.
- `ruff check` on all four touched files: **All checks passed** (no new lint debt).
- `modularity_check --check`: EXIT=0.
- **R273:** zero runtime-journal writes — both fixes execute only inside future
  notify/observe calls; tests use temp journals; the live journal was not touched.
- **Scope:** exactly `telegram_sink.py`, `live_observation.py`, and their two test packs
  (all in allowed_paths); `test_agent_supervisor_golden_run.py` gained ONE register test —
  the golden-run certification scenarios themselves are untouched (M0-T116 re-runs the
  whole pack at the final frozen identity regardless).
- **R247 consequence:** supervisor material identity has moved; M0-T116 recertifies at the
  ONE frozen final identity covering both this unit and M0-T115.

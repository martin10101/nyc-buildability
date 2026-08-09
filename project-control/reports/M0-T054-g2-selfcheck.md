# M0-T054 — G2 self-check (orchestrator)

Recorded by the orchestrator 2026-08-09 at main `89c4e30`. Non-independent producer self-check preceding
the independent G3/G5/DCV gates (already PASS at reviewed code `3c36c42`).

## Reproduced self-check evidence
- **Tests:** 79 deterministic turnover tests green; full supervisor suite **1481 passed / 2 skipped, 0
  failures** — re-run independently by the orchestrator. Freeze baseline (M0-T039) preserved: 1471 + 10
  live-signal, every non-exhaustion path byte-for-byte unchanged.
- **Diff:** strictly additive — 14 files, +3500 / −0 (`git diff --stat origin/main...3c36c42`); worker seam
  is `loop.py` +37/−0, `cli.py` +10/−0, entered only when an integration is injected AND
  classify == FABLE_EXHAUSTED.
- **Detection correctness:** grounds on the exact `You have reached your Fable 5 limit` phrase / typed
  `seven_day` rate-limit; transient 429 excluded; contradiction/unattributed/bare-limit/network/unknown →
  AMBIGUOUS_FAIL_CLOSED; never raises.
- **Actuation correctness:** single-instance lock, duplicate-event suppression, exactly-once successor,
  Fable→Opus audit link, hard-pinned `claude-opus-4-8`/xhigh (non-opus echo → available=False),
  safe-stop-if-opus-unavailable.
- **Invariants:** doctor proof ALL-12 PASS re-run live; `default_mode=shadow`, supervised runtime,
  LIMITED-AUTO off, protected immutable config unchanged.
- **Live proof (R316):** real Fable exhaustion → classify → one real opus-4.8 worker launch (exit 0),
  isolated non-product runtime, no owner `/model` (`M0-T054-live-proof/LIVE-PROOF.md`).

## Honest limitation
Production auto-actuation is record-intent-only; live production activation (R595) is the owner-gated
follow-up M0-T056, not a defect. Self-check PASS; proceeds to independent gates.

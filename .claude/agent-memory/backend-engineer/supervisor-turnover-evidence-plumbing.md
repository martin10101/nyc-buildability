---
name: supervisor-turnover-evidence-plumbing
description: Where the REAL Fable weekly-exhaustion signal lives in a worker RunResult, and how model_turnover classifies it (M0-T054 turnover seam)
metadata:
  type: project
---

The agent-supervisor Fable->Opus turnover stack (`tools/agent_supervisor/`): detection is
`model_turnover.classify_exhaustion` (pure, fail-closed), the actuation policy is
`turnover_controller.TurnoverController`, and the loop seam is
`worker_turnover.WorkerTurnoverIntegration.evaluate`.

**Load-bearing fact (M0-T054 increment 5, live proof 2026-08-09):** on a REAL Fable weekly
hard-stop the exact phrase "You've reached your Fable 5 limit..." does NOT reach
`RunResult.stderr_tail` (empty) or `RunResult.checkpoint_error` (a generic
`missing_checkpoint: ...` string). It lives in the STREAM events: a `rate_limit_event` with
`rateLimitType == "seven_day_overage_included"` + `status == "rejected"`, an `assistant`
event flagged `is_api_error_message`, and a terminal `result` with `is_error` /
`terminal_reason == "api_error"` carrying the phrase. Captured fixtures:
`project-control/reports/M0-T054-live-proof/real-fable-exhaustion-streamjson.txt`.

**Why:** the first-built seam fed the classifier only `checkpoint_error + stderr_tail`, so it
saw no phrase and returned NOT_EXHAUSTED — turnover never fired on real exhaustion.
**How to apply:** the runner now distills two additive `RunResult` fields via
`claude_runner.detect_exhaustion_evidence(events)` — `result_text` (api-error result/assistant
text) and `rate_limit_rejection` (raw rejected `rate_limit_event` + attached `model_id`). The
seam folds `result_text` into stdout and passes `rate_limit_rejection` as
`structured_result`. `model_turnover._weekly_rate_limit_rejection` treats `seven_day`/`week`
markers + `rejected` as FABLE_EXHAUSTED; a bare/transient 429 (no weekly marker, no phrase)
stays AMBIGUOUS by design (`STRUCTURED_QUOTA_CODES` deliberately excludes 429). The runner
GATHERS; the classifier is the sole decider. This module is supervisor-freeze; edits must be
additive and cite the R289 incident + this live proof. See [[fable-exhaustion-fallback-test]].

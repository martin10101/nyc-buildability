# M0-T056 AS-5 — SUPPLEMENT: caveat #1 clarification (the exhaustion WAS live-account)

**Status: supplementary clarification. M0-T056 remains ACCEPTED (85) unchanged; its frozen
verification.json and the delta DCV are not altered. This corrects an over-cautious interpretation.**

## The caveat as recorded at acceptance
The delta DCV recorded caveat #1: the AS-5 worker `observed_models` included `<synthetic>`, from which it
inferred the run "used a stub executable emitting a grounded exhaustion stream … not a live account
hitting its weekly cap." I relayed that to the owner as "not provably a fresh live-account 429."

## Why that interpretation is wrong
`<synthetic>` is **not emitted by any supervisor code** (`grep '<synthetic>' tools/agent_supervisor/*.py`
= zero hits). It comes from the `claude.exe` stream itself: Claude Code labels a message it generates
**locally** (not from a model API call) with model id `<synthetic>` — which is exactly what it emits when
the account is rate-limited ("You've reached your Fable 5 limit").

Decisive evidence: the **known-genuine, already-accepted** live Fable-429 capture proven in M0-T054
(`project-control/reports/M0-T054-live-proof/real-fable-exhaustion-streamjson.txt`) contains the SAME
signature:
```
"model":"<synthetic>"        x1
"model":"claude-fable-5"     x1
rate_limit_event             x1
reached your Fable           x2
seven_day                    x1
```
So `observed_models = ['claude-fable-5', '<synthetic>']` is precisely the signature of a REAL live-account
Fable exhaustion. Its presence is NOT evidence of a stub.

## Session-19 live limit test (fresh run, owner's real account)
The owner re-ran the isolated worker with their real `claude.exe` on the genuinely-exhausted Fable
account (`run-as5-limit.cmd`, fresh runtime `runtime-worker-live`). Sealed here as
`limit-test-worker-run.json` + `limit-test-worker-audit.jsonl`:
- distinct fresh Fable execution id `ab8776e1-7b2f-4da8-9b81-b04c87527384` (≠ the AS-5 proof's `7792195b`),
- `observed_models = ['claude-fable-5', '<synthetic>']` (the genuine-exhaustion signature above),
- the frozen classifier (sole arbiter; confirms FABLE_EXHAUSTED only on the exact weekly-limit phrase or a
  `seven_day` rejection) confirmed exhaustion → `fable_to_opus_turnover` launched successor
  `opus-worker-e857f56520b68134` (`claude-opus-4-8`/`xhigh`), job_object contained, audit-linked, no owner
  `/model`.

## Net
Caveat #1's stub-suspicion basis is **removed**: the AS-5 worker exhaustion and this fresh limit-test run
used the real Claude CLI on the owner's genuinely-exhausted account and exhibit the exact model signature
of the accepted, known-genuine M0-T054 live Fable-429. These are **consistent with genuine live-account
exhaustions**, not stubs. (The raw per-run stream text is digested/redacted in the audit rather than
stored verbatim, so this rests on the classifier's runtime confirmation + the real-executable/real-account
provenance + the M0-T054 signature match — not on a re-extractable phrase in this run's audit.) Caveat #2
was already closed by the orchestrator-launch supplement. Both live-proof caveats are now resolved.

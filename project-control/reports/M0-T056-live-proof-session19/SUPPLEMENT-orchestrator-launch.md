# M0-T056 AS-5 — SUPPLEMENT: clean orchestrator-layer live launch (post-acceptance)

**Status: supplementary corroboration. M0-T056 is already ACCEPTED (85, commit 13ee59d) and is NOT changed by this file.**

At acceptance, the delta DCV recorded two honest, non-blocking caveats. Caveat #2 was that the
ORCHESTRATOR-layer watchdog *fail-closed* (`opus_unavailable_safe_stop`) rather than launching its
successor live, because the initial owner-run launcher prefix (`python -m tools.agent_supervisor start`)
had **no `--runtime-base`**: the watchdog runs the successor under `process.minimal_env` (which allowlists
`PATH`/`SYSTEMROOT`/`TEMP`/… but **not `%LOCALAPPDATA%`**), so the successor could not resolve its default
runtime dir and exited 1 — which the watchdog correctly treated as "successor not started" and fail-closed
(no fallback). R345's successful-launch path was already deterministically proven on `OrchestratorWatchdogTests`.

This supplement records the owner re-running the watchdog with the **corrected** launcher prefix
(`python -m tools.agent_supervisor start --runtime-base <isolated-successor-runtime>`), on the same
Windows/job_object host, against the same captured real Fable exhaustion signal
(`signal-fable-exhaustion.txt`), touching no account and no quota (the successor is a real supervisor
`start` relaunch that starts cleanly at pre-dispatch and contacts no provider).

## Result (files sealed alongside; sha256 in SHA256-MANIFEST-supplement.txt)

- **watchdog-fixed-run1.json** — `launched: true`, `actuated: true`,
  `successor_id: opus-orchestrator-0a870815d70d50df`, `successor_model_id: claude-opus-4-8`,
  `containment_kind: job_object`, `status: launched_successor`,
  `audit_record_id: c0d52f663397d85ffa67445091410addd2e55b932c574e07752649e3a583561c`.
  Reason: "launched exactly one claude-opus-4-8/xhigh successor 'opus-orchestrator-0a870815d70d50df'
  for the orchestrator layer from safe checkpoint 'as5-safe-cp'; audited Fable
  'orchestrator-exhaustion:a7d3ec00…' -> Opus 'opus-orchestrator-0a870815…'".
- **watchdog-fixed-run2.json** — same signal + runtime: `launched: false`, `status: suppressed_duplicate`
  ("exhaustion event … was already actioned; suppressing a repeat turnover") → **exactly-once** proven live.
- **watchdog-fixed-audit.jsonl** — `fable_to_opus_turnover` + `fable_turnover_event_actioned`
  (dedup digest `7749e7c2dcdf075d21b97aebdd0d97a9ed45d547252a0173dd5eb9c7c3389d5e`).

## Net

Both turnover layers now have a live, successful, job_object-contained, audit-linked, exactly-once
auto-launch on record (worker layer at acceptance; orchestrator layer here). Caveat #2 is closed.
Caveat #1 (the AS-5 worker exhaustion was a synthetic-but-grounded injected stream, not a fresh
live-account 429) stands as recorded; genuine-account Fable-429 detection remains separately
proven+accepted in M0-T054. This supplement does not alter M0-T056's acceptance or its frozen
verification.json; it is corroborating evidence for the R595 production-activation decision.

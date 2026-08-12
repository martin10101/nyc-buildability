# M0-T056 — DCV DELTA verification (R349 + R351) — VERBATIM independent reviewer return

Independent verifier: `directive-compliance-verifier` (read-only; verifier != producer backend-engineer). Returned via agent channel; saved verbatim (transport entity-decoding only). Reviewed at frozen HEAD `44f27999e0cd6aee4c42c0a4100578730a0608f5`, content identity `9306071de8fd2013dc15452581c8a4616725a0d545db8fffc531c56a94396d48`.

---

# DCV DELTA REPORT — M0-T056 (D-010) — R349 & R351

**Verifier:** directive-compliance-verifier (independent; producer = backend-engineer). **Read-only.**
**Frozen identity (verified):** HEAD = `44f27999e0cd6aee4c42c0a4100578730a0608f5`. The 6 M0-T056 allowed_paths files are byte-identical to `a90ac19` (`git diff --stat a90ac19 HEAD -- <6 files>` = empty, exit 0). All four gates + the M0-T056 `verification.json` block pin `reviewed_sha=44f27999…`. Task status = `awaiting_gate` (not accepted/merged — no prohibited action). `validate_directive_compliance.py --check` exit 0.

## (A) Prose ruling

### Integrity of the sealed evidence
- **SHA256-MANIFEST.txt** — recomputed `sha256sum` for all six files; every hash matches (`doctor.json`, `watchdog-audit.jsonl`, `watchdog-run1.json`, `watchdog-run2.json`, `worker-audit.jsonl`, `worker-run1.json`). `watchdog-run1.json` and `watchdog-run2.json` are byte-identical (same hash `329dfbb3…`) — the second watchdog run reproduced the identical safe-stop.
- **Audit hash-chains — cryptographically genuine.** Re-derived every record's digest with the actual `audit_log.compute_record_digest` (SHA-256 over canonical JSON minus `digest`) and confirmed `prev_digest` links from genesis (`000…0`): `worker-audit.jsonl` (9 records, seq 1→9): every digest_ok + prev_link_ok. CHAIN VALID. `watchdog-audit.jsonl` (2 records): both valid. CHAIN VALID.

### Isolation (no product / M2-T015)
`doctor.json`: `checkout = %TEMP%\as5\repo`, runtime under `%TEMP%\as5\runtime-worker\…`, config `%TEMP%\as5\config.toml` — isolated non-product scratch. `limited_auto: NOT IMPLEMENTED and disabled`; `push_policy … NO push is executed`. Touched no product/M2-T015. (Note: the orchestrator prompt's claim that the packet allowed_paths are "README/docs only" is inaccurate — the M0-T056 packet allowed_paths are the six supervisor files; isolation is instead established by the `%TEMP%\as5` runtime in doctor.json, which is correct.)

### What the code path proves (deterministic)
The `fable_to_opus_turnover` event (`reason_code=fable_exhaustion_worker_turnover`) is only emitted when `worker_turnover.evaluate` had all of: (1) `classify_exhaustion → FABLE_EXHAUSTED`; (2) the owner's `--authorize-turnover-actuation` predicate True; (3) a wired real controller (`_build_worker_actuation_channel`, built only under `--authorize-turnover-actuation` AND job_object containment, using production `make_subprocess_command_runner`); (4) `controller.execute → turned_over=True`. The frozen classifier confirms FABLE_EXHAUSTED only on the exact weekly-limit phrase or a `seven_day` rate-limit rejection — a bare 429 fails closed.

### R349 — ACCEPTANCE HARNESS / isolated live proof — PASS (SATISFIED)
Worker-layer evidence demonstrates the R349 phenomenon on an isolated job_object runtime: one continuous supervised run `run_a6b010b17760` (`START_CLAUDE → CLAUDE_RUNNING → PAUSED_RECOVERY`), a Fable unit (seq 4, session `7792195b`, expected_model claude-fable-5, returncode 1) → confirmed exhaustion → real automatic successor spawn (seq 6 `fable_to_opus_turnover`: `successor_id=opus-worker-eaa97b4657b19d6b`, `successor_model_id=claude-opus-4-8`, `successor_effort=xhigh`, layer=worker, via production `make_subprocess_command_runner`, not a faked Popen). Exactly-once: seq 7 `fable_turnover_event_actioned` dedup marker (`turnover_event_digest=70f64576…`); budget counted=1. No owner /model step; provider_calls_made=1. All required gates: G0/G2/G3/G5 PASS at reviewed_sha 44f27999, plus this independent DCV.

This replaces the single link accepted M0-T054 explicitly deferred to R595 (M0-T054-live-proof/LIVE-PROOF.md proved genuine-account Fable-429 detection + a real claude-opus-4-8 successor process; the only deferred piece was a single continuous automated supervised run where the final subprocess.Popen was faked). AS-5 session19 replaces that faked Popen with a real spawn in a live continuous run.

**Two caveats recorded honestly (neither defeats R349 as written):**
1. The AS-5 exhaustion signal was **synthetic-but-grounded, not a fresh live-account 429**: worker-audit seq 4 `observed_models=["claude-fable-5","<synthetic>","claude-haiku-4-5-20251001"]`; `<synthetic>` is never emitted by supervisor code, so the run used a stub `--claude-executable` emitting a grounded exhaustion stream (task_id SYNTH-AS5-PROOF), not a live account hitting its weekly cap. Appropriate: the frozen classifier confirmed FABLE_EXHAUSTED; genuine-account detection is separately proven+accepted in M0-T054. The verifier does NOT endorse the stronger phrase "a REAL Fable-5 weekly-cap exhaustion of a real worker session".
2. Only the WORKER layer launched live; the ORCHESTRATOR watchdog fail-closed (`launched:false`, `opus_unavailable_safe_stop`, relaunch returncode=1, no fallback). Its successful-launch path is deterministically proven under R345 (already PASS on code + OrchestratorWatchdogTests); the shared launcher succeeded live on the worker layer.

**On orchestrator-vs-worker:** R349's parenthetical is singular ("a real successor auto-launches"). The two-layer channel is decomposed into R345 (orchestrator) + R346 (worker), both already PASS on code+tests. R349 is satisfied by the worker-layer continuous auto-actuation. R349 does NOT require the orchestrator-layer successor to also launch live. A fixed-watchdog re-run showing one live orchestrator-layer launch would strengthen the record — optional, not required.

**Forward-looking (not an R349 blocker):** doctor.json reports `controller_config_acl: NOT_PROTECTED` on the scratch `%TEMP%\as5\config.toml` — a production-config hardening precondition for the eventual R350 production flip; immaterial to this isolated scratch proof (whose in-code gate is job_object containment, met).

### R351 — RETURN at the acceptance seam — PASS (SATISFIED)
Items 1/2/3/5 confirmed in the prior DCV at the frozen identity (R346/R347/R348 PASS; G0/G2/G3/G5 PASS). Item 4 (the isolated live-proof record) now satisfied by the sealed `project-control/reports/M0-T056-live-proof-session19/`: six files sha256-verified, both audit chains cryptographically genuine, payloads internally consistent.

## VERDICT: PASS
- D-010-R349 → PASS (two honestly-recorded, non-blocking caveats: synthetic-but-grounded signal; orchestrator layer fail-closed not launched).
- D-010-R351 → PASS (item 4 satisfied by the sealed, integrity-verified live-proof record).

All 14 M0-T056 requirements PASS. Frozen identity, gate wave, and audit-chain integrity intact; proof touched no product/M2-T015; no prohibited action (task awaiting_gate).

**Recommendation:** record the DELTA gate result as PASS and update the two verification.json rows to state PASS; carry the two caveats forward into the acceptance note; and before the R350 PRODUCTION flip, (a) harden the real controller-config ACL (doctor currently NOT_PROTECTED on the scratch config) and (b) optionally re-run a fixed orchestrator watchdog to capture one live orchestrator-layer successful launch. Neither is required to accept M0-T056 under R349/R351 as written.

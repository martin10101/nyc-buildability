<!-- Saved VERBATIM by the orchestrator from the G5 security-reviewer agent-return channel
     (transport entity-decoding only). Review head d4a529d, material identity d1b05bb. -->

All 9 deterministic tests I could run reproduce GREEN on Python 3.11.9. The live-CLI teeth (requiring an installed 2.1.251 claude) were verified by source inspection (exact `==` retained) plus the producer's verbatim red-before/green-after capture in M0-T118-recapture-evidence.md. I have everything needed for the report.

---

# G5 Security Review — Ledger task M0-T118

**Task:** M0-T118 — D-024 Amendment 13 unit R: bounded fixture recapture at Claude Code 2.1.251
**Reviewed at:** frozen control-branch head `d4a529d` (material identity `d1b05bb`), branch `control/D-024-fable-codex-loop`
**Reviewer:** security-reviewer (independent, read-only)
**Scope:** 13-file delta (`git show d1b05bb`): 5 new measured fixtures, 2 pointer re-points (event_drift.py, guardrail_refusal.py), 4 test packs, 2 reports. No implementation modified by this review.

## Read-only commands run
- `git log --oneline -8 d4a529d`; `git rev-parse HEAD`; `git branch --show-current` — confirmed frozen head, clean tree (`git status --porcelain` empty).
- `git show --stat d1b05bb`; `git show d1b05bb -- <each file>` — full delta inspection.
- `git show d4a529d:tools/agent_supervisor/telemetry_hooks.py | grep KNOWN_HOOK_EVENTS` — confirmed baseline unchanged (31 events).
- `git show d4a529d:tools/test_agent_supervisor_*.py | grep <tooth bodies>` — confirmed exact-match teeth.
- `git grep -n -i -E "MLFLL|C:\Users|/Users/|sk-ant|api_key|token|password|secret|bearer|PRIVATE" d1b05bb -- <5 fixtures>` — clean (exit 1).
- `git show d1b05bb | grep -i -E "DISABLE_UPDATE|downgrade|admitted"` — only negation/deferral statements.
- `git show d1b05bb --name-only` — all 13 files within packet `allowed_paths`.
- Confidence-label semantic diffs (python one-liners) between 2_1_248 and 2_1_251 fixtures.
- `git show d4a529d:tools/agent_supervisor/capability_probe.py` / `native_runtime.py` — probe-command inspection.
- `python -m pytest` on 9 deterministic tests — all PASS on Python 3.11.9.

## Findings

**No SEC-BLOCKER, SEC-MAJOR, or SEC-MINOR findings.** Three SEC-INFO notes below.

### 1. Drift-detection integrity as a security control — PASS
- All three live drift teeth retain exact `==` version comparison against the installed CLI, unweakened: `test_s8_live_version_matches_catalog_fixture` (test_agent_supervisor_event_bus.py:354), `test_live_reprobe_claude_version_matches_fixture` (test_agent_supervisor_capability_probe.py:191), `test_live_detection_matches_committed_fixture` (test_agent_supervisor_native_adapter.py:727). None skipped, none made tautological — only the fixture pointer and the recorded version string moved (248→251). Producer's captured RED-before (`3 failed`, `'2.1.251' == '2.1.248'`) / GREEN-after (`3 passed`) evidence in M0-T118-recapture-evidence.md:24-53 is consistent with the retained exact-match logic.
- The +2 event drift is bound deterministically in `test_s8_recorded_drift_matches_computed_drift` (test_agent_supervisor_event_bus.py:307-318): asserts `drift.added == ("PostModelSwitch", "PreModelSwitch")`, `drift.removed == ()`, `drift.has_drift`, and that the computed drift matches the fixture's recorded reconciliation. This cannot silently regress — and critically, it is itself the backstop against a silent KNOWN_HOOK_EVENTS widening: if the baseline were later widened to absorb the two events, `catalog_drift()` would compute `added=()` and line 315 would FAIL.
- `KNOWN_HOOK_EVENTS` at the frozen SHD is unchanged at 31 events (telemetry_hooks.py:29-38); PreModelSwitch/PostModelSwitch are absent; telemetry_hooks.py is not in the delta. Not widened — the drift is recorded as a reconciled fact, exactly as claimed.
- Independently reproduced 4 deterministic tests GREEN (drift reconciliation, catalog validity/masking, drift computation, detection-fixture shape) on Python 3.11.9.

### 2. Fixture content hygiene — PASS
- Secret/token/PII scan across all 5 new fixtures returned no matches: no `MLFLL`, no `myhappybook`, no absolute `C:\Users`/`/Users/` paths, no `sk-ant`/api-key/token/password/bearer/private-key shapes. All home paths are masked `[HOME]` (capability_probe fixture `probe_meta.claude_binaries`/`codex_binaries`; hook_event_catalog:47 documents the `[HOME]` masking convention).
- All 5 fixtures are data-only JSON. No executable content — the only `script` substring hits are inside `transcript`/`transcript_path` (loop_interception_detection_2_1_251.json:26-27, hook_event_catalog_2_1_251.json:47), which are descriptive notes, not code.
- No credential-shaped strings requiring gitleaks/secretscan pragmas exist, so no unannotated pragma gap.

### 3. Honest-confidence non-escalation — PASS
- **guardrail_refusal_shapes**: semantic-field diff (confidence, per-shape `verified_live`, `live_capture.status`) between 2_1_248 and 2_1_251 is byte-identical. The only change is the `cli_version` string, which stays `"UNCAPTURED ... base CLI 2.1.251"` (fixture line 26 of the delta). No label upgraded.
- **loop_interception_detection**: `selected_event` (UserPromptSubmit), `zero_context_proof.status`, and `queued_input_behavior.status` all remain `pending-owner-C1` — identical to the predecessor. The 2_1_251 fixture adds an honest `payload_lineage` block explicitly stating the UserPromptSubmit payload is INHERITED (not re-measured at 2.1.251); only event-set membership was re-checked. This is strictly more disclosed than the predecessor, not an escalation.
- **hook_event_catalog**: confidence stays `official-docs`; the only movement is the documented, intended +2 event drift.
- Only `capability_probe_live` and `native_runtime_detection` carry measured-live values, exactly matching the producer's stated method (capability probe + native runtime measured live; interception inherited; guardrail UNCAPTURED; zero_context pending-owner-C1). No UNCAPTURED/inherited label was upgraded to measured-live.

### 4. Probe boundedness — PASS
- `capability_probe.py` (re-run to produce the live fixture) documents "every probe is read-only — no login, no config mutation, no network calls" (line 17) and its `_PROBES` set is exactly `claude --version`, `claude --help`, `codex --version`, `codex --help`, `codex exec --help` (lines 51-55), run via `subprocess.run(..., check=False)` with no `shell=`.
- `native_runtime.py` documents "every detection probe is help/version-only (no login, no config mutation, no network beyond what the CLI does locally); the allowlist is closed" (lines 12-13); probes are `claude --version`/`--help`/`<verb> --help` only.
- No provider session, no prompt sent, no file writes outside the 5 named fixtures. The fixture provenance is honest: the docs re-fetch is attributed to the orchestrator, not the sandboxed producer (hook_event_catalog_2_1_251.json `source`: "docs re-fetched 2026-08-29 by the orchestrator … producer recorded the delivered set"; interception `payload_lineage` reinforces this).

### 5. R280/R282 compliance — PASS
- **R280**: No `DISABLE_UPDATES` applied anywhere — the only occurrences in the delta are negation statements in reports (M0-T118-recapture-evidence.md:6-7). No CLI downgrade/update: AS-4 version stamps are identical at capture start (19:49:31Z) and end (20:07:08Z), both `2.1.251 (Claude Code)`. No unrelated global config change — all 13 delta files are within the packet's `allowed_paths`; no `.claude/**`, no runtime journal, no protected config, no telemetry_hooks.py touched.
- **R282**: NO admission record is written by this unit. Every "admitted" string in the delta is an explicit non-admission/deferral (producer report line 32; evidence-map D-024-R282 row: "no admission line exists anywhere in this delta"). The admission is correctly deferred to M0-T119. Confirmed by scanning `git diff d1b05bb d4a529d` — the control-plane submit adds only gate/report/state/task files, no admission claim.

### 6. Supply-chain surface — PASS
- No new dependencies: the delta touches no lockfile, `package.json`, `requirements`, or manifest. No G5 provenance review is triggered.
- No executable content in fixtures (see finding 2).
- No changes to command-broker/policy/approval surfaces: process.py, claude_runner.py, preflight.py, cli.py, turnover_adapters.py are all untouched (confirmed by the delta file list).

## SEC-INFO notes (non-blocking)
- **SEC-INFO-1**: `capability_probe_live_..._2_1_251.json` stores `output_sha256` digests of the `--version`/`--help` output. These are integrity anchors over public CLI help text (data-only), not secrets — no pragma or redaction needed. Noted for completeness.
- **SEC-INFO-2**: The live drift teeth (`requires_claude`) could not be executed in the reviewer sandbox (no guaranteed 2.1.251 CLI present; CI runners skip these). Verified by source inspection (exact `==` retained) plus the producer/orchestrator captured red/green evidence, per the read-only-reviewer evidence-verification protocol — not returned as BLOCKED.
- **SEC-INFO-3**: `native_runtime_detection_2026-08-29_m0t118.json` and the capability probe carry `platform: "win32"` and a UTC `generated_at` — non-sensitive environment facts, no machine name or user identity leaked.

## Modularity
Production-source change is limited to two one-line constant re-points (event_drift.py:43-44 `CATALOG_FIXTURE_PATH`; guardrail_refusal.py:160-161 `SHAPES_FIXTURE_PATH`) plus explanatory comments. No responsibility mixing, no module growth of concern, no new coupling. No modularity concern from a security standpoint.

## Summary
The delta is a faithful, bounded fixture recapture at the deliberately-admitted-but-not-yet-recorded 2.1.251 CLI. The drift-detection security control is intact and strengthened (the +2 drift is now a deterministically-asserted fact that also backstops against silent KNOWN_HOOK_EVENTS widening). Fixtures are clean, data-only, and honestly labeled with no confidence escalation. Probes are bounded and read-only. R280/R282 prohibitions and the admission hold are honored — no DISABLE_UPDATES, no downgrade, no admission record, no protected-config touch, no new dependencies. Nothing in the suite moved beyond the intended pointer/label updates.

**G5 VERDICT: PASS**

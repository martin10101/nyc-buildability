# M0-T105 G5 security review — DELTA round 2 (VERBATIM reviewer return; transport entity-decoding only)

Saved by the orchestrator per the report-preservation rule. Reviewer: security-reviewer (same
agent resumed with round-1 context, 2026-08-27). Verdict returned: **PASS**.

---

# G5 Security Gate — DELTA Re-review — M0-T105 (D-024 Amendment 3 unit D)

**Reviewer:** security-reviewer (independent, read-only)
**Round:** 2 (delta) — round-1 verdict was PASS with LOW-1 + ADVISORY-1/2/3
**New frozen identity:** deliverable commit `bfdf4ef5e4682d64a7e1c8f0a330b86fc04d1963`; content_manifest_sha256 `4bd0e18256d538b254a24a931b341c4b57b2851db15879dbcb4f86e336fe15d3`; live HEAD `9f816477c1c78d45599d54637ccedcc88f401d80`
**Applicable requirements:** D-024-R154, D-024-R155, D-024-R173
**Repo visibility:** PUBLIC
**Verdict:** **PASS** — LOW-1 genuinely closed; no new blocking findings; ADVISORY-1/2/3 remain correctly-scoped non-blocking residuals.

---

## Delta scope covered (as requested)

### (1) LOW-1 genuinely closed — non-cosmetic — CONFIRMED
- The old top-level attribute loop is **gone**; `event_bus._store` now calls the new **recursive** `_mask_uuids(...)` on `dict(record.attributes)`, `record.session_id`, and `record.task_id` (event_bus.py lines 220-236). `_mask_uuids` (lines 69-82) recurses over dict **values**, dict **keys**, and list/tuple **elements**, digest-masking every full-UUID-shaped string at any depth.
- My exact round-1 reproduction now masks completely (re-run in-memory through `ingest_hook_event` → `_mask_uuids` → `sanitize_structure`):
  ```
  payload = {..., 'agent_id':{'x':REAL, REAL:'as-key'}, 'model':['p',REAL]}
  → RAW UUID anywhere in record : False
  → agent_id stored as : {'x':'[SESSION sha256=38e4e4acfa60]', '[SESSION sha256=38e4e4acfa60]':'as-key'}
  → model stored as    : ['p','[SESSION sha256=38e4e4acfa60]']
  ```
  The nested value, the **dict-key** UUID, and the **list element** are all masked. This is a structural fix (the guarantee now holds by construction of the recursive walk), not a targeted patch of one path.
- Committed regression test `test_s4_nested_uuid_masked_at_any_depth` asserts `SESSION_UUID not in stored` and `stored.count("[SESSION sha256=") >= 4` (value, nested, key, list). Independently reproduced: `python -m pytest tools/test_agent_supervisor_event_bus.py -q` → **38 passed in 2.53s** (was 32; +6, incl. the nested-mask, cp1252-fidelity, oversized-stdin, and C1-fixture tests).

### (2) F1 byte-cap math + decode posture — SOUND
- Recorder now reads **bytes**: `raw_bytes = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)` then `if len(raw_bytes) > MAX_STDIN_BYTES: return 0`. This is a true byte-level cap — it fixes my round-1 §2.2 note that the old `sys.stdin.read()` capped **characters** (a UTF-8 stream could reach ~4× the byte budget). New math: `read(MAX+1)` returns ≤ 1 MiB+1 bytes; `len > MAX` rejects the boundary; exactly-1 MiB passes. The oversized branch is now exercised for real by `test_s9_recorder_oversized_stdin_fails_closed` (asserts nothing recorded).
- Decode posture is correct: cap is checked **before** decode, so `.decode("utf-8-sig", "replace")` runs on ≤ 1 MiB of bytes (bounded). `sys.stdin.buffer` bypasses the Windows cp1252 locale (the G4 M1 defect); `utf-8-sig` tolerates a BOM; `"replace"` turns undefined bytes into U+FFFD instead of raising — so a damaged byte stays visible and never silently drops the whole event, while any resulting invalid JSON still fails closed (json.loads raises → caught → exit 0). `test_s9_recorder_non_ascii_payload_fidelity` round-trips an emoji + `Ísafjörður` path payload through the recorder subprocess.

### (3) C1 fixture + .gitleaksignore leak/abuse review — CLEAN
**C1 fixture** (`fixtures/hook_events_live_2026-08-27_m0t105_c1.json`, 9 records, owner-launched round 2):
- Independent leak scan over the committed bytes → **0 hits** (no username/`MLFLL`, no email, no drive-rooted or POSIX user path, no raw UUID, no token shapes, no prompt content).
- Masking verified per field: `session_id` = `[SESSION sha256=…]` (12-hex digest); `cwd` = `[HOME]\AppData\Local\Temp\evcap247` ([HOME]-masked scratch dir); `prompt_id` = `[PROMPT-WITHHELD sha256=… chars=29]` (withheld wholesale because the `prompt_id` key matches the prompt-like pattern — even better than storing the raw id); the raw `prompt` field is absent (not whitelisted). `agent_id` (`a662aee3f5d7f16ac`) is an opaque per-run subagent handle needed for attribution — not a UUID, not a credential. `model` = `claude-fable-5`.
- The fixture's honest disclosures (cross-process `bus_sequence` collision at seq 3; a second session's `SessionEnd` digest `f8304cf9a432` recorded, never guessed into the capture session; SubagentStart/Stop firing without TaskCreated/Completed on 2.1.247) are provenance-accurate ordering/observation notes, **not** security defects — no data loss, distinct dedup keys, digest-masked identities throughout.

**.gitleaksignore** (9 fingerprints):
- Confirmed **structural false positives, fingerprint-scoped, not rule-wide.** Each entry is `tools/…/hook_events_live_…json:generic-api-key:<line>` for lines **17-25** — verified those are exactly the 9 records carrying `idempotency_key`.
- Ground-truth via gitleaks 8.30.1: bypassing the ignore (`--gitleaks-ignore-path` at a nonexistent path) yields **exactly 9 `generic-api-key` findings on lines 17-25**, and the flagged "Secret" in each is the record's `idempotency_key` 64-hex value (hashes match the fixture bytes). Re-scanning **with** the repo `.gitleaksignore` applied → **"no leaks found."** So the ignore suppresses precisely these content-addressed sha256 dedup digests (hash of sanitized event identity + content — deterministic, non-credential) and the `generic-api-key` rule still fires everywhere else. Note gitleaks did **not** flag the session/prompt digests (12-hex, non-"key"-named fields), so the ignore surface is minimal and exact.
- Minor (informational, non-blocking): the fingerprints use the filesystem `file:rule:line` form, which I proved works for `gitleaks detect --no-git`. If the pre-commit hook runs gitleaks in git mode (fingerprints embed the commit SHA), these entries would not match — but the fixture is already committed (won't re-trigger the staged-scan hook) and the content is genuinely non-credential, so worst case is a re-flagged false positive, never an actual secret exposure.

### (4) ADVISORY-1/2/3 residuals + no new surface — CONFIRMED
- **ADVISORY-1** (`NYCB_EVENT_STORE_PATH` honored in production without validation): unchanged and correctly scoped. The C1 capture legitimately used it to redirect the store into the scratch dir — the intended mechanism. Still no validation, still within the accepted threat model (env is not payload/web-attacker-controlled; hooks run as the user; only sanitized JSONL is appended). Non-blocking residual.
- **ADVISORY-2** (O(n) per-event replay latency): still present, and now **disclosed in-code** (F3 comment in the recorder documenting the `warm_rotated=False` dedup-window trade — a duplicate after a rotation boundary is re-recorded, the safe direction, surfaced later by replay as `store_duplicates`). Correctly characterized; non-blocking.
- **ADVISORY-3** (recorder swallows all exceptions → silent telemetry loss on persistent write failure): unchanged; correct session-safety trade for a passive, non-tamper-evident journal (`audit_log.py` holds the hash chain). Non-blocking.
- **No new surface** across `git diff 50abb34..bfdf4ef`: no new imports in any of the four production modules; no `urllib/requests/socket/http/subprocess/eval/exec/os.system/__import__` added to production code (all such grep hits are report-markdown prose); no new dependency manifest; no MCP/SDK/bypass flags; repo `.claude/settings.json` untouched (empty diff) and both guard packs (`readonly_agent_guard.py`, `agent_dispatch_guard.py`) byte-untouched (empty diff). The scratch `settings.json` (sha `a26d3b9b95ba3cc6`) lives outside the repo and is not committed.

---

## Requirement coverage (security aspects) at the new identity
- **D-024-R154** (stream ingestion outside Fable context; statusLine sidecar primary; typed errors): PASS — unchanged; no sidecar/model surface; typed `StreamEventError`; R042/R043 labels intact.
- **D-024-R155** (hooks fast/deterministic/sanitized/bounded/fail-closed; external state only; never block/inject/message): PASS — recorder still stdout-silent, exit-0, fail-closed; F1 hardens the bounded/sanitized stdin path (true byte cap + UTF-8 fidelity); ADVISORY-2 (fast) now disclosed in-code.
- **D-024-R173** (unknown-event/version-drift honest handling): PASS — unchanged; `known:false`/`known_type:false`; the C1 capture even records honest live drift (Agent subagent fires no TaskCreated/Completed on 2.1.247) without guessing.

---

## Verdict
**PASS.** The round-1 LOW-1 nested-UUID gap is genuinely and structurally closed (recursive `_mask_uuids` wired into `_store`; exact reproduction now fully masked; committed regression test; 38/38 pass). F1's bytes-first read fixes the cp1252 hazard with sound cap math and a fail-closed decode. The owner-launched C1 fixture is leak-clean and its 9 `generic-api-key` gitleaks hits are proven structural false positives suppressed by a correctly fingerprint-scoped (not rule-wide) `.gitleaksignore`. Repo settings and guard packs remain untouched; no new imports, dependencies, network/exec/bypass surface, or hook registration appeared. ADVISORY-1/2/3 remain correctly-scoped, non-blocking residuals appropriate for a follow-up hardening task. No blocking corrections.

Relevant absolute paths:
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\event_bus.py` (F2 recursive `_mask_uuids` lines 69-82; `_store` wiring 220-236)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.claude\hooks\supervisor_event_recorder.py` (F1 bytes+decode lines 51-60; F3 disclosure 72-76)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\hook_events_live_2026-08-27_m0t105_c1.json` (C1 evidence)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.gitleaksignore` (9 fingerprint-scoped false positives)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_event_bus.py` (38 tests)

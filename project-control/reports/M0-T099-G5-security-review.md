# GATE REPORT — M0-T099 — G5 independent security review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only — the harness had neutralized angle brackets as HTML entities — per the
report-preservation rule). Reviewer: security-reviewer (independent, read-only). Producer:
orchestrator.

---

# GATE REPORT — M0-T099 — G5 Independent Security Review

**VERDICT: PASS** (no blocking findings; 1 minor + 2 nit advisory items, none gating)

**Reviewer:** security-reviewer (independent, read-only)
**Reviewed content identity (frozen):** `00f2519f2eb2cf0b1afb6789b6b0afe17b1aac05`
**Live HEAD:** `27c0ab7c14e0fb3b7d660265ed8c7b3dcb110ed6` — `git diff --name-status 00f2519 HEAD` returns only `project-control/**` records (gates/M0-T099-G2.json, reports/M0-T099-G2-self-check.md, reports/M0-T099-evidence-map.json, state.json, tasks/M0-T099.json). **The reviewed code identity is intact.**
**Environment:** Python 3.11.9. Reproduced: 3 telemetry test packs → **121 passed in 5.23s**; mask probes and fixture scans reproduced independently (below).
**Scope (frozen 10 files):** `telemetry_statusline.py` (new, 211 SLOC), `telemetry_redaction.py`, `telemetry_sdk.py`, `telemetry_transcript.py`, `telemetry_subagent.py`, `fixtures/statusline_live_2026-08-26.json` (new), 3 test files, the producer report. `.claude/settings.json` is **absent** from the diff (confirmed; it is also a forbidden path).

---

## Per-dimension verdicts

### 1. Data exposure (PUBLIC repo) — PASS (advisory MIN-1)
Required identity masking is **complete and independently reproduced**:
- `grep` over the committed fixture for `MLFLL | C--Users | C:\Users | /home/ | /Users/ | myhappybook` → **no matches**; bare `Users` token → none.
- Reproduced both home-prefix regexes over the fixture text: dash-form hits `[]`, slash-form hits `[]`.
- The dash-encoded projects-dir form is masked (e.g. `[HOME]-Downloads-nyc-zoning-ctl24`, `transcript_path` nested double-encoding both masked).
- Cross-fixture scan `test_all_committed_fixtures_free_of_home_prefixes` globs **all** `*.json` (covers the new fixture) and passed inside the 121.

Judgement of every remaining field: `session_id`/`prompt_id` are opaque UUIDs of a **discarded** scratch session (a Claude Code session_id is a local transcript identifier, not a credential — no exploitability); `session_name` ("Respond with exact acknowledgment") is the trivial capture-prompt title; `cost.total_cost_usd` (0.78) is intentionally documented spend; `added_dirs` tails reveal only folder structure with the username masked. The one real-telemetry residue worth owner awareness is the live **account-state**: `rate_limits.five_hour.used_percentage` (28.999…%), `seven_day` (33%) and `resets_at` epochs (1787721600 / 1787878800) — see MIN-1. Note: `ingest_status_line` does **not** capture `session_name`/`prompt_id` into any record, so those two fields live only in the fixture file, never in a runtime sidecar/journal.

### 2. New mask logic (separator symmetry + dash mask) — PASS (nits NIT-1, NIT-2)
`_HOME_PREFIXES` uses `[\\/]+` (one-or-more), so JSON-escaped `C:\\Users\\name` masks symmetrically with the leak-scan regex. Reproduced bypass probes:
- `C:/Users/someone/p` → `[HOME]/p`; lowercase/drive-case handled `(?i)`.
- Dash form `C--Users-someone-Downloads-proj` → `[HOME]-Downloads-proj` (n=1).
- Two occurrences `C--Users-a-x-C--Users-b-y` → `[HOME]-x-[HOME]-y` (**global** subn, n=2).
- Username-with-dashes `C--Users-multi-part-name-Downloads` → `[HOME]-part-name-Downloads` (first-segment-only, as documented). No mixed/URL-encoded/UNC bypass produced a leak that also survives the pipeline; the actual owner username (`MLFLL`, no dashes) masks fully and the slash-form mask consumes dashed usernames wholesale.

### 3. Predecessor G5 closures (M1/M2/N1/N2) — PASS (all four independently verified closed)
- **M1 (SdkTaskTracker cardinality bound) — CLOSED.** `setdefault` then `if len(self._tasks) > max: _evict(keep=task_id)`; `_evict` scans completed-first in insertion order, else oldest, and never evicts `keep`; `_evicted_tasks` counter is honest. `test_sdk_tracker_bounded_eviction_prefers_completed` proves completed-first-then-oldest and the evicted count. Keep-parameter sound; the just-added task always survives.
- **M2 (transcript accumulator bounds) — CLOSED.** `compaction_total` and `pre_tokens_sum`/`pre_tokens_seen` accumulate for **every** boundary *before* the 256-detail cap, so totals stay **exact**; `compactions` capped at 256 with `compactions_truncated`; `session_ids` capped at 64 with `session_id_overflow_events`; `unknown_types` capped at 64 distinct keys with a counted `<other>` bucket. Overflow is always counted, never silent. Three red/green tests confirm totals-exact-while-detail-capped.
- **N1 (dict-KEY sanitization) — CLOSED.** `clean_key` runs the full `sanitize_text` pipeline over string keys; SENSITIVE/PROMPT pattern checks run against the **original** key name; collisions append `#<digest8>` of the original key so no entry is dropped — verified order-independent (both orderings keep both entries). No route puts an unsanitized string key into a stored document (post-`json.loads` keys are strings; non-string keys pass through but cannot occur). Red/green ×2.
- **N2 (postTokens/trigger narrowing) — CLOSED.** `post_tokens = _narrow_count(...)` (bool/negative/non-numeric → None), `trigger` string-only. `test_transcript_post_tokens_and_trigger_narrowed` proves malformed shapes drop to None.

### 4. Injection / exfiltration surface of `telemetry_statusline.py` — PASS
Grep for `eval|exec|pickle|marshal|subprocess|popen|os.system|__import__|import_module|socket|urllib|requests|httpx|http.client|asyncio|additionalContext|hookSpecificOutput` → **none** (also clean across the four other changed modules). Imports are `argparse/json/sys/typing` + three telemetry modules only. **stdout is the sole emission** (`out_stream.write(row + "\n")`); the sidecar/journal are the only file writes and both sanitize-first (`update`→`_to_sanitized_dict`→`sanitize_structure` at journal:116; `append` at journal:184 — traced). The degraded error row is `f"telemetry ? (handler error: {type(exc).__name__})"` — exception **type only**, no message/args; `test_main_handler_error_prints_degraded_row_exit_zero` asserts `str(tmp_path) not in row`.

### 5. R135 (no model messages / no API tokens) — PASS
`test_statusline_module_no_network_or_process_imports` AST-walks imports and forbids `{socket,urllib,http,requests,httpx,subprocess,asyncio}`; `test_statusline_module_no_model_context_injection` forbids `additionalContext`/`hookSpecificOutput` in any non-docstring string constant. No code path composes a prompt or opens a connection; the transitive foundation (`telemetry_ingest/journal/records/redaction`) is stdlib-only and unchanged except the reviewed hardening edits. Structurally the handler cannot consume API tokens. `test_official_no_token_note_recorded_in_module_and_fixture` anchors the verbatim official note + doc URL.

### 6. Worker-facing leak (D-024-R045) + settings untouched — PASS
The human row surfaces model/effort, ctx %, session cost/duration, and rate-limit % (`_rate_limit_segment` shows `used_percentage` only, never `resets_at`). Because statusLine output renders in the **terminal status chrome and is never injected into any model/worker context** (the R135 property), those usage numbers cannot reach a worker prompt surface; the machine feed (sidecar) is controller-private, read only by the operator/monitor CLI `telemetry_status.read_only_status`. This handler emits the plain-text statusLine contract, not the `subagentStatusLine {"id","content"}` worker-adjacent contract (explicitly routed away to M0-T089). `.claude/settings.json` is not in the frozen diff. R045 holds structurally.

### 7. Secret scan over added lines — PASS
`git diff 00f2519~1 00f2519 -- tools/` added lines filtered for `sk-ant|AKIA|BEGIN|PRIVATE KEY|bearer|password|secret_key|api_key=|ghp_|xox…|AIza` (excluding LLM token-count identifiers) → **no matches**. Only `token/tokenCount/tokenSamples/total_tokens` LLM-usage identifiers appear.

---

## Findings

**Minor (non-blocking, advisory)**
- **MIN-1 — Real live-account telemetry committed to a PUBLIC repo.** `fixtures/statusline_live_2026-08-26.json` embeds the owner's point-in-time account state (`rate_limits.*.used_percentage` 29% / 33%, `resets_at` epochs) plus real `session_id`/`prompt_id` UUIDs, `session_name`, and `cost.total_cost_usd`. The **required** identity masking (home paths, `MLFLL`, dash-encoded `C--Users-MLFLL`) is complete and verified clean, and none of these residual fields are exploitable (scratch session discarded; session_id is a local identifier). They are also **not** load-bearing for the installed-version proof — the `version`, field shapes, and documented nullability carry R129/R131. Recommendation (owner-awareness, for any future real capture): neutralize account-usage numbers/epochs and session/prompt UUIDs to synthetic values so a public artifact never carries a live account-usage snapshot. Not gating — the owner directed a real capture and the report intentionally documents the trivial spend.

**Nit**
- **NIT-1 — Dash-form not in the class-wide fixture scan.** `test_all_committed_fixtures_free_of_home_prefixes` uses only the slash-form regex; the dash-encoded (`C--Users-<name>`) form is asserted clean only by the per-file `test_live_fixture_masked_no_home_or_username_leak`. The committed fixture is clean under both (reproduced), but the *class* guard for the dash form is fixture-specific. Consider adding `_HOME_DASH_PREFIXES` to the cross-fixture scan.
- **NIT-2 — Dash-username masking is first-segment-only.** `C--Users-multi-part-x` → `[HOME]-part-x`. Documented best-effort; not a live leak (owner username has no dashes; the slash-form mask fully consumes dashed usernames). Latent limitation only for a future capture from a machine whose username contains a hyphen. Acceptable as documented.

---

## Recommendation to orchestrator
**Record G5 = PASS.** The frozen code identity matches `00f2519` (live HEAD differs only in `project-control/**`). All four predecessor advisories (M1/M2/N1/N2) are independently verified closed with genuine red/green teeth; the new mask logic and the real-fixture masking are complete and reproduced; the handler is network-free, prompt-free, stdout-only, sanitize-first on persistence, and leaks only an exception type on failure; `.claude/settings.json` is untouched. MIN-1 is an owner-awareness advisory about the deliberately-real fixture (not a masking defect); NIT-1/NIT-2 are hardening suggestions. None block acceptance of this shadow-only, controller-private telemetry.

---

*Orchestrator disposition (recorded at gate time): MIN-1 is surfaced to the owner in the
acceptance summary (the real capture was owner-directed; the recommendation — neutralize
account-usage numbers and session/prompt UUIDs in FUTURE public captures — is adopted as
standing guidance for the Phase B/F live-canary task). NIT-1 (dash-form in the cross-fixture
class scan) and NIT-2 (first-segment dash-username limitation) join the carried hardening
inputs for the next task touching these modules. None blocking.*

# GATE REPORT — M0-T099 — G3 independent code review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only — the harness had neutralized angle brackets as HTML entities — per the
report-preservation rule). Reviewer: code-reviewer (independent, read-only). Producer:
orchestrator.

---

# GATE REPORT — M0-T099 — G3 Independent Code Review

## VERDICT: PASS (minor/nit findings; none blocking)

**Reviewer:** code-reviewer (independent, read-only). **Date:** 2026-08-26.
**Task:** M0-T099 — "D-024 B1-follow-up: project statusLine handler + real installed-version fixture (amendment 2)".
**Reviewed content identity (frozen):** `00f2519f2eb2cf0b1afb6789b6b0afe17b1aac05`.
**Live HEAD:** `27c0ab7c14e0fb3b7d660265ed8c7b3dcb110ed6` — `git diff --name-only 00f2519 HEAD` returns **only 5 `project-control/**` files** (`gates/M0-T099-G2.json`, `reports/M0-T099-G2-self-check.md`, `reports/M0-T099-evidence-map.json`, `state.json`, `tasks/M0-T099.json`). No production/test/fixture byte differs between the frozen SHA and HEAD; the reviewed code identity is intact.
**Environment:** Python 3.11.9, ruff 0.13.0. All commands reproduced locally.

---

## 1. Scope & identity

`git show --stat 00f2519` = exactly the **10** packet files: new `tools/agent_supervisor/telemetry_statusline.py`; new fixture `tools/agent_supervisor/fixtures/statusline_live_2026-08-26.json`; new `tools/test_agent_supervisor_statusline_handler.py`; hardening edits to `telemetry_redaction.py` / `telemetry_sdk.py` / `telemetry_transcript.py` / `telemetry_subagent.py`; updates to `test_agent_supervisor_telemetry_core.py` and `test_agent_supervisor_subagent_telemetry.py`; and the producer report. Every path is inside `allowed_paths`; no forbidden path touched (`.claude/settings.json`, `.claude/hooks`, `tools/project_control.py`, `apps`, `services`, … all absent from the diff). The reused M0-T088 surfaces `telemetry_ingest.py`, `telemetry_records.py`, `telemetry_journal.py`, `telemetry_status.py`, `telemetry_hooks.py` are **not in the diff** — confirming R130 (reuse, no rebuild).

## 2. Reproduction (frozen identity, Python 3.11.9)

| Check | Claim | Reproduced |
|---|---|---|
| Targeted packs (handler + core + B2) | 121 passed | **121 passed in 15.03s** ✓ |
| Full supervisor suite `tools/test_agent_supervisor_*.py` | (freeze baseline ≥1165/0) | **2041 passed, 2 skipped, 0 failed in 268.7s** ✓ (2006 M0-T089 + 35 new = 2041) |
| `ruff check` on all 8 touched .py | clean | **All checks passed!** ✓ |
| `modularity_check.py --check` | failures 0 | **292 files; failures 0; 5 pre-existing warnings, none in the new handler** ✓ |
| Handler pack test count | packet/report say "21" | **23 tests collected** ✗ (see Nit N1) |

## 3. Dimension 1 — Handler correctness & design

`telemetry_statusline.py` (211 SLOC) is a clean single-responsibility CLI/presentation layer over the accepted core: `parse_payload` → `ingest_status_line` (reused) → `TelemetrySidecar.update` (sanitize-first, reused) → optional `TelemetryJournal.append` → `format_status_row` over the **same** record. Verified behaviors:
- **Degrade-never-crash CLI:** `main()` wraps ingest+persist in `try/except Exception` and always writes a row + returns 0; on handler error it emits `telemetry ? (handler error: <ExcType>)` naming only the exception *type* (no message text → no path leak). Reproduced by `test_main_handler_error_prints_degraded_row_exit_zero`, `test_main_garbage_stdin_degrades_to_unknown_row`.
- **Row format** matches the live payload exactly — I traced the post-response payload to `"Fable 5 xhigh | ctx 4% of 1.0M | sess $0.78 1m | 5h 29% 7d 33% | v2.1.220"` (`test_row_from_live_post_payload`). `_fmt_pct`/`_fmt_tokens` handle None→`?` and unit scaling correctly.
- **No path/identity in the row:** `format_status_row` reads only model/effort/version + occupancy/cumulative/rate-limit numbers; `test_row_never_leaks_paths_or_session_identity` confirms no `[HOME]`, slash, `session_id`, or `transcript`.

## 4. Dimension 2 — Amendment-2 fit (R129–R138)

Confirmed at the code/test/design level (the formal per-requirement verdict is the directive-compliance-verifier's province; producer ≠ verifier):
- **R129** doc URL `https://code.claude.com/docs/en/statusline` in module docstring + fixture (`doc_url`) + tests. **R130** no-rebuild (reused surfaces absent from diff).
- **R131** REAL live-2.1.220 fixture: two raw payloads (pre-first-response documented-nulls; post-response real usage + both rate-limit windows), `installed_version_proof` cross-refs the capability probe; exercised by 8 tests.
- **R132** one feed: `handle_status_line` returns the row from the **same** record it persisted; `test_one_feed_read_back_by_shadow_status` proves `telemetry_status.read_only_status` reads back exactly `stored`.
- **R133** occupancy (`ctx`, `context_window.*`, category `occupancy`) vs cumulative (`sess`, `cost.*`, category `cumulative`) are structurally separate in row and record; `test_row_axes_never_borrow_each_other` gives distinctive numbers teeth.
- **R134** `rate_limits.*` kept a verbatim attribute rendered as its own `5h/7d` segment; `test_live_post_response_payload_real_values_and_axes` asserts no `rate_*` measurement exists (never a context measurement); wholly-absent block → `limits ?`, never 0.
- **R135** official note verbatim in docstring; two structural proofs — AST scan (no `additionalContext`/`hookSpecificOutput` outside docstrings) and import scan (no socket/http/urllib/requests/httpx/subprocess/asyncio). Handler output is one stdout row + sanitize-first file I/O only.
- **R136** proven against REAL startup data (`test_live_startup_payload_documented_nullability`): `current_usage`/percentages null → unknown; `total_*: 0` and `cost:0` → value 0 (zero stays zero); `context_window_size: 1000000` present. Backed by `_measure`/`_clean_count` where 0 is a value and null/absent/malformed is unknown.
- **R137** routing untouched — subagentStatusLine stays in `telemetry_subagent.py` (M0-T089 accepted); the only change there is the nit#4 detail string.
- **R138** doc URL + installed-version proof recorded in report + fixture.

## 5. Dimension 3 — Carried M0-T089 items (verified individually vs prior finding text)

| Item (prior finding) | Disposition | Evidence |
|---|---|---|
| **G5 M1** SdkTaskTracker bound + completed-first eviction | Code CORRECT; test teeth gap | `DEFAULT_MAX_TASKS=512`; `_evict` scans completed-first then oldest, `evicted_tasks` counter; setdefault-then-bound keeps len ≤ max. Test `test_sdk_tracker_bounded_eviction_prefers_completed` proves the bound + counting but does **not** isolate "completed-first" (see Minor M1). |
| **G5 M2** transcript bounds, exact totals | CLOSED | `MAX_COMPACTION_DETAILS=256` / `MAX_SESSION_IDS=64` / `MAX_UNKNOWN_TYPE_KEYS=64`; `compaction_total`+`pre_tokens_sum` accumulate BEFORE caps (stay exact); `<other>` overflow bucket + overflow counters. 3 red/green tests with real teeth. |
| **G5 N1** dict-KEY sanitization + collisions | CLOSED | `clean_key` runs the string pipeline over keys; sensitive/prompt pattern checks stay on the ORIGINAL key; colliding sanitized keys get an 8-hex digest suffix so no entry is dropped. Traced the "unchanged-key collides with sanitized-key" case both orderings — both survive. 2 tests. |
| **G5 N2** postTokens/trigger narrowing | CLOSED | `_narrow_count(postTokens)`; `trigger` stored only if `str`. `test_transcript_post_tokens_and_trigger_narrowed` (bad→None, good preserved). |
| **G3 minor#2** per-EVENT counters | CLOSED | `event_duplicate`/`event_regression` flags → counted once per event; test asserts a fully-repeated 3-field event = 1 duplicate (old per-field = 3). |
| **G3 nit#3** final_request detail | CLOSED | detail ends "select final-request scope by the `final_request_*` name, never by label"; test asserts `"never by label" in detail`. |
| **G3 nit#4** window detail | CLOSED | `contextWindowSize` detail = "denominator of the live view, not lifetime spend"; token detail keeps "documented pairing"; test asserts the two are distinct. |
| **G3 nit#5** dead assertion replaced | CLOSED — judged sound | The old `assert "lower bound" not in … or True` was dead AND inverted (the detail DOES contain "lower bound"). Replacement asserts `"conservative lower bound" in detail` and `"not a provider statement" in detail`, which matches the actual `telemetry_transcript.py` detail string (lines 149-150). The replacement is a genuine teeth assertion on the real contract. |
| **G4 A2** mask separator symmetry `[\\/]+` | CLOSED | `_HOME_PREFIXES` now uses `[\\/]+`; `test_home_prefix_json_escaped_double_separator_masked` (double-separator `C:\\Users\\…`). |
| **G4 A1** hermetic-subset (documented-only) | CONFIRMED documented | Report §5 records it as "DOCUMENTED (no code): the full `tools/` suite requires the full checkout … Guarding on artifact presence remains optional future work" — matches the G4 A1 note; no code claim. |

## 6. Dimension 5 — New production change beyond the carried list

`_HOME_DASH_PREFIXES = re.compile(r"(?i)\b[A-Z]--Users-[^-\\/\s\"',;:\]\[]+")` masks the dash-encoded projects-dir form (`C--Users-<name>-…`) that a live `transcript_path` leaks even after the slash-form mask. Judged **correct and low-risk**: the regex is a narrow, anchored, linear (no-backtracking) pattern applied after the slash mask inside `redact_user_paths`; `test_home_prefix_dash_encoded_projects_dir_masked` asserts the exact output (`[HOME]\.claude\projects\[HOME]-Downloads-proj\abc.jsonl`) and `n == 2`. Regression risk on existing masking tests is negligible — the full supervisor suite (2041/0, incl. all `telemetry_core` home-prefix tests) is green, and the committed fixture's `transcript_path` demonstrates the mask working end-to-end (`C--Users-MLFLL-…` → `[HOME]-…`, no username survives).

## 7. Dimension 4 — Test adequacy

23 handler tests (real teeth: exact row-string equality, axis-borrow negatives, independent-window absence, degrade/garbage/error CLI paths, one-feed read-back, sidecar masking, AST + import structural proofs). No tautologies. The two updated packs add 12 red/green tests, all reproduced GREEN; each targets a specific carried behavior with a distinguishing assertion. Modularity clean; strong reuse over duplication.

## 8. Findings

**Blocking:** none.

**Minor**
- **M1 — G5-M1 "completed-first" preference is not uniquely pinned by a test.** In `test_sdk_tracker_bounded_eviction_prefers_completed` the completed entry (`t1`) is also the *oldest*, so a hypothetical pure-oldest-first mutation of `_evict` would still pass the test. The code implements completed-first correctly and the bound + eviction-counting ARE teeth-tested; this is a test-adequacy gap on the eviction-order nuance only. Recommend a case where a *newer* task is completed while an older one stays active, asserting the newer-completed is evicted first. Non-blocking (bound is the material property; code is correct).

**Nit**
- **N1 — Report/commit test-count inaccuracy.** The report §1 and the commit message state a "21-test pack"; the handler pack actually collects **23** tests. The composite `121 passed` figure (the gate-relevant number) is correct and reproduced, so there is no arithmetic impact — report/commit accuracy only.
- **N2 — Home username in report prose (informational, not a redaction-policy breach).** The report §8 purge note commits `C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack`. This is consistent with **287** other already-committed tracked files (SESSION_HANDOFF, blockers, directives, agent-memory) and is outside the telemetry-artifact masking scope the redaction work governs. The governed artifact — the live fixture — **is** correctly masked (no `MLFLL`, no unmasked `Users`; verified by `test_live_fixture_masked_no_home_or_username_leak` and the cross-fixture scan). Noted for the record; not a G3 defect.

## 9. Notes for the orchestrator / other gates
- Supervisor-freeze: `D-024-R100` + `D-024-R131/R132` cited in packet objective, module docstrings, report, and commit message; suite baseline (≥1165/0) re-established at **2041/0**. Satisfied.
- The per-requirement D-024 (R129–R138) verification is the `directive-compliance-verifier`'s job at `project-control/directives/D-024-fable-codex-loop/verification.json`; this G3 adjudicates only code, tests, design, modularity, and report accuracy.

**Recommended gate result: PASS.** The two carried-item hardening surfaces, the new handler, and the dash-form mask extension are correct, well-tested, and regression-free; the minor/nit items are advisory and do not affect correctness, the amendment-2 requirements, or the shadow-only guarantee.

---

*Orchestrator disposition (recorded at gate time): G3-M1 (completed-first eviction-order test
isolation) joins the carried hardening inputs for the next task touching telemetry_sdk.py.
G3-N1 (21 vs 23 test-count undercount) is durably corrected in the M0-T099-DCV.md disposition
note — the producer report is deliberately not edited post-submit (identity preservation).
G3-N2 is informational (report prose matches 287 pre-existing committed path references;
the governed telemetry artifacts are masked). None blocking.*

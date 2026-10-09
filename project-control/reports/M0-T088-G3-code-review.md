# GATE REPORT — M0-T088 — G3 Independent Code Review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only, per the report-preservation rule). Reviewer: code-reviewer
(independent, read-only). Producer: orchestrator.

---

# G3 CODE REVIEW — M0-T088 (D-024 Phase B1: telemetry core + primary-session ingestion, shadow)

## VERDICT: PASS (with minor findings; none blocking)

**Reviewer:** code-reviewer (independent, read-only). **Reviewed identity:** frozen commit `23f0d80a1e6097e0e8f7616be3fde43de3a202cd`. **Live HEAD:** `74dc098` adds only control-plane records (G2 gate json + state + task fields; verified via `git show 74dc098 --stat`). **Producer:** orchestrator (governance task).

### Identity verification (done first)
- Frozen commit exists; all 6 reviewed source files on disk are blob-identical to `23f0d80` (`git hash-object` == `git rev-parse 23f0d80:<path>` for all four telemetry modules, `capability_probe.py`, and the test file — all YES).
- Frozen commit touched exactly the 14 declared files; no forbidden production path (`.claude/hooks`, `settings.json`, `project_control.py`, `validate_directive_compliance.py`, `directive_registry.py`, `apps`, `services`, `supabase`, `D-001`) was touched. The `project-control/{tasks,state,gates,reports}` edits are the orchestrator's own control-plane records (producer==orchestrator per ADR-005), not producer-scope violations.

### Evidence reproduced (my sandbox, Python 3.11.9)
- `pytest tools/test_agent_supervisor_telemetry_core.py tools/test_agent_supervisor_capability_probe.py -q` → **65 passed** (49 new + 16 existing probe, unmodified). Matches report.
- Full `pytest tools/test_agent_supervisor_*.py -q` → **1969 passed, 2 skipped, 0 failed** (332s). Matches report; re-establishes supervisor-freeze ≥1165/0 baseline duty.
- `python tools/modularity_check.py --check` → exit 0 (failures 0).
- `ruff 0.13.0` on all five touched modules + test file → "All checks passed!". Matches CI-matched claim.
- Fixture body byte-identity: `git show 23f0d80` diff on the fixture shows **only the `probe_meta` block changed** (paths → `[HOME]`, `generated_at` refreshed); the `body` is untouched. Committed fixture JSON dump contains zero `Users`/`/home/` occurrences.
- Matrix cross-check: 11 `measured-live` capability ids, all mapped in `_derive_live_status` (test asserts ≥10 and iterates every one).

---

## Per-dimension findings

### 1. Correctness of each module — PASS
Read every line of all four modules and the `capability_probe.py` diff.

- **telemetry_records.py** — `Measurement.__post_init__` enforces the full contract: label∈8-vocabulary, category∈3-set, `value is None ⇔ label=='unknown'`, bool rejected (`isinstance(bool)` guard precedes numeric), negatives rejected, numeric-may-not-claim-unknown. `MEASUREMENT_CATEGORY` registry + `_check_measurement_name` make occupancy↔cumulative cross-labelling a hard `TelemetryRecordError`. Round-trip `to_dict`/`from_dict` with schema guard is correct. No I/O, no prompt composition. Solid.
- **telemetry_redaction.py** — Pass order is exactly escapes → paths → secrets → bounding (`sanitize_text`, lines 102–118); the ordering rationale (secrets before bounding so truncation can't leak a secret head; secrets after escape-strip so a fragmented credential still matches) is correct and load-bearing. `bounded is not out` identity check (line 115) correctly detects truncation because `bound_text` returns the same object when under limit and a fresh object when truncated. `_HOME_PREFIXES` (line 55) consumes exactly the username segment and masks drive+Users/home; tail preserved; case-insensitive; both slash directions. Terminal-escape regex preserves tab/LF/CR and strips other C0+DEL+CSI+OSC. `sanitize_structure` masks sensitive keys wholesale *before* recursing (no leak via walk) and withholds prompt-like keys as sha256 digests.
- **telemetry_journal.py** — Atomic write: unique temp (pid+counter) + fsync + `os.replace` with bounded PermissionError retry; `finally` unlinks temp only on failure (post-success the temp is already renamed away). Sidecar bound-check happens *before* write (nothing written when oversized — test confirms `read()==None`). Journal rotation drops oldest→shifts→renames active; single record over bound refused up-front; `read_all` skips+counts torn/non-dict lines, never invents. `utf-8-sig` read tolerates BOM.
- **telemetry_ingest.py** — `_clean_count` rejects bool/non-numeric/negative → `None`; nullable fields become `unknown`, reported zeros stay zero (correct distinction, tested). `context_window.*`→occupancy, `cost.*`→cumulative — consistent with the records registry. `UsageAccumulator`: message-ID dedup via bounded LRU; unidentified/malformed steps counted not dropped; per-step (`provider-exact`) and reported (`sdk-cumulative`) kept in separate structures and name families; regression logic retains high-water and counts resets so a counter can never "look fresh". Import graph is acyclic (`capability_probe`→`telemetry_redaction`→`redaction`; no cycle back).

**minor** — `telemetry_ingest.py:221-231, 284-292`: the per-step record emits measurements literally named `cumulative_input_tokens` (etc.) holding a *single step's* value, with `detail="single step, not a running total"`. The category is correct (cumulative) and the detail disambiguates, and `snapshot()` supplies the true running sum, but reusing the `cumulative_*` name family for a per-step delta on a `provider_usage_step` record is a provenance-clarity wrinkle a downstream consumer could misread. Non-blocking (nothing consumes records yet; shadow mode).

### 2. Test adequacy / teeth — PASS
49 new test functions (confirmed `grep -c '^def test'` = 49). All carry real assertions — exact value/dict equality, `pytest.raises(TelemetryRecordError)` in both directions for unknown/zero and cross-labelling, `is_unknown` checks, and substring-absence checks on serialized output (`"sk-ant" not in json.dumps(...)`). No vacuous/never-failing tests found:
- `test_no_telemetry_module_injects_model_context` correctly excludes docstrings via AST (so `ingest.py`'s docstring naming `additionalContext` doesn't falsely pass) and iterates real code-string literals — not vacuous.
- `test_generic_matrix_equals_live_for_all_measured_entries` asserts `len(measured)>=10` before looping, so it cannot pass on an empty set; an unmapped id raises `AssertionError` with instructions.
- Atomicity tests exercise both before-rename (monkeypatched exploding `os.replace` → previous snapshot survives) and after-rename crash, plus 32-thread overlap. `_run` failure branches (Timeout/OSError/non-zero) monkeypatched. Word-boundary classify_flags asserts both positives and negatives.

**nit** — `_derive_live_status` (test helper) for `claude.print_mode_output_format` uses `statuses.pop()` on a mixed set (line 653), which is nondeterministic if the two flags ever disagree. Harmless today (both `supported`) and test-only, but a latent fragility.

### 3. Fixture truthfulness — PASS
- Body byte-identical: proven by the commit diff itself (only `probe_meta` hunks). No independent *fresh-probe* reproduction was possible in my sandbox (requires live `claude`/`codex` binaries), but the committed body is provably unchanged from the parent fixture, and the `classify_flags` hardening is strictly *stricter* (word-boundary), so it can only remove substring false-positives; every `supported` flag in the committed body (`--print`, `--mcp-config`, `--strict-mcp-config`, `exec`, `resume`, …) is a real standalone flag, so no committed classification is at risk. Consistent.
- `probe_meta` redaction verified: committed fixture dump has zero `Users`/`/home/` occurrences; all binary paths start `[HOME]`. Regression-tested by `test_committed_live_fixture_probe_meta_is_redacted` and `test_probe_meta_paths_are_home_redacted_live`.

### 4. Report accuracy — PASS with one minor inaccuracy
Spot-checked ≥6 claims against the live repo: 65-passed split, full-suite 1969/2/0, byte-identical body, zero Users/home in probe_meta, modularity failures 0, ruff 0.13.0 clean, 49 new tests, 11 measured-live cross-checked — **all VERIFIED**.

**minor** — `M0-T088-telemetry-core.md:119` and `M0-T088-G2-self-check.md:17` both state new-module SLOC "**219/171/216/292**". The modularity tool's own `source_lines()` reports **179/140/192/266** (219/180/235/313 are the *total* physical line counts). The reported SLOC figures match neither the tool nor total/non-blank/non-comment consistently, so they are not reproducible. Immaterial to the gate (all are far below the 600 warn threshold and `modularity_check` exits 0), but the numbers as written are wrong in two reports.

### 5. Modularity / architecture — PASS
Four focused modules with clean, single-responsibility boundaries: records = typing/validation (pure data), redaction = sanitization, journal = persistence (atomic/bounded/rotated), ingest = payload parsing. Correctly **reuses** rather than duplicates: `telemetry_redaction` composes the existing `redaction.py` secret pass; `telemetry_ingest` reuses `models.to_utc_iso`. The telemetry journal is explicitly and justifiably distinguished from `audit_log.py` (runtime bounded/rotated evidence vs tamper-evident hash chain) in the module docstring. `modularity_check --check` → 0 failures; no pre-existing file grew. No dumping-ground module.

### 6. No control-behavior change — PASS
No supervisor control-flow module (`cli.py`, `policy.py`, loop/rotation/session_continuity, `broker.py`, `codex_reviewer.py`) was touched — the frozen commit's file list is exactly the 4 new modules + `capability_probe.py` + fixture + test + control records. Nothing consumes the new records (shadow/actuation-off, confirmed: no import of the telemetry modules by any controller). The only behavioral change to existing code is `capability_probe.classify_flags` (stricter matching, output proven unchanged) and `build_record()` routing `probe_meta` through redaction (a hygiene wrap, body untouched). Supervisor-freeze qualifying evidence **D-024-R100** is cited in the task packet, commit message, and report per §3 duty.

**Note (not a finding):** Directive-requirement-by-requirement verification over the full 34-id applicable set (R002/R003/R004/R037/R038/R039/R042/R043/R044/R045/R100/R107/R120/R125-128, etc.) is the `directive-compliance-verifier`'s pass, not G3. From a code standpoint the technically-testable directive requirements (R037 no-injection, R038 category separation, R042 unknown-never-zero, R043 per-step≠reported, R044 compact-records-only, R107 test coverage, R120 bounds) are satisfied in source and tests as reproduced above.

---

## Summary
- **Blocking findings:** none.
- **Minor:** (a) per-step record reuses `cumulative_*` measurement names for single-step deltas (`telemetry_ingest.py:221-231`); (b) SLOC figures 219/171/216/292 in two reports are not reproducible (tool reports 179/140/192/266).
- **Nit:** `_derive_live_status` `statuses.pop()` nondeterminism on a mixed set (test-only, `:653`).

Recommend **PASS**. The minor items are documentation/clarity only and do not affect correctness, safety, directive compliance, or the shadow-mode guarantee.

---

*Orchestrator disposition (recorded at gate time): the frozen producer reports are not edited
post-submit (that would move the reviewed material identity); the authoritative SLOC figures are
the modularity tool's (179/140/192/266 source lines; 219/180/235/313 physical), as documented
here — G3 minor (b) is thereby corrected by reference. G3 minor (a) (per-step measurement
naming) and the test-helper nit join the G5-S2 item as the named cleanup bundle carried into
M0-T089 (Phase B2), matching the M0-T086→M0-T088 precedent. None blocking.*

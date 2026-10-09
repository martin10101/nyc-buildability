# GATE REPORT — M0-T088 — G4 QA / independent review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only, per the report-preservation rule). Reviewer: qa-engineer (independent,
read-only, isolated worktree). Producer: orchestrator.

---

# G4 QA Gate Report — M0-T088 (D-024 Phase B1: telemetry core + primary-session ingestion, shadow mode)

## VERDICT: PASS (with 2 advisory, non-blocking findings)

Reviewer: qa-engineer (independent, read-only). Reviewed content identity: **23f0d80a1e6097e0e8f7616be3fde43de3a202cd** (frozen). No blocking defects. All producer claims reproduced exactly.

---

## Content-identity proof (I exercised the frozen content)

- Frozen commit `23f0d80` `--stat` vs parent = the exact 14-file diff described in the packet (4 new modules, new 685-line test, `capability_probe.py` +22, fixture ±12, plus 5 control-plane records).
- `git diff --name-only 23f0d80 74dc098` (live HEAD) = **only 3 control-plane files** (`gates/M0-T088-G2.json`, `state.json`, `tasks/M0-T088.json`). None of the 7 implementation files differ between frozen and live.
- Per-file **sha256: all 7 implementation files in the ctl24 working tree are byte-identical to the frozen `23f0d80` blobs** — `telemetry_records.py` 387f8b05…, `telemetry_redaction.py` ac95cf33…, `telemetry_journal.py` 15636953…, `telemetry_ingest.py` 5adf50a3…, `capability_probe.py` 40bf1095…, `fixtures/capability_probe_live_2026-08-25.json` 8073c086…, `test_agent_supervisor_telemetry_core.py` 938a4450… (frozen blob hash == working-tree hash, all MATCH). Tests below therefore run against the frozen content.

---

## Reproduced commands (exact counts)

| # | Command | Producer claim | Reproduced | Verdict |
|---|---------|----------------|------------|---------|
| 1 | `pytest tools/test_agent_supervisor_telemetry_core.py -q` | 49 passed | **49 passed** (14.08s) | PASS |
| 2 | `pytest …_telemetry_core.py …_capability_probe.py -q` | 65 passed | **65 passed** (9.37s) | PASS |
| 3 | `pytest tools/test_agent_supervisor_*.py -q` | 1969 passed, 2 skipped, 0 failed | **1969 passed, 2 skipped, 0 failed** (214s; re-run 201s) | PASS |
| 4 | `ruff check` (0.13.0) on 4 new modules + `capability_probe.py` + test | clean | **All checks passed!** | PASS |
| 5 | determinism: `build_record()['body']` == committed fixture body; probe_meta `[HOME]`-masked | True; no home prefix | **BODY_IDENTICAL: True**; all probe_meta paths start `[HOME]`; zero `Users`//`/home/` | PASS |

Local: Python 3.11.9, pytest 8.4.2, ruff 0.13.0 (CI-matched). The 2 skips are pre-existing environmental guards unrelated to T088 and part of the 1920 baseline: `test_agent_supervisor_policy.py:449` (Windows symlink privilege, WinError 1314) and `test_agent_supervisor_process.py:448` (POSIX-only guard). Baseline 1920/2/0 + 49 new = 1969/2/0 → supervisor-freeze §4 duty (≥1165/0) re-established.

`python tools/modularity_check.py --check` → **failures 0**; the 5 warnings are all pre-existing files (`surveyReview/types.ts`, `mappluto_geometry_arcgis.py`, `agent_supervisor/cli.py`, `policy.py`, `context_benchmark.py`) — none are the new modules, and no pre-existing file grew. New module sizes are well under thresholds.

---

## Mutation-style teeth checks (7/7 red — tests are load-bearing)

Method: copied the whole `tools/agent_supervisor` package + the test file into OS temp (namespace package; repo untouched), confirmed baseline 49 passed, then applied one behavior-breaking string mutation per guard test and confirmed the node goes red.

| Mutation | Guard test | Result |
|---|---|---|
| Remove message-ID dedup (`return None` disabled) | `test_message_id_dedup_ignores_replayed_steps` | **RED** |
| Drop counter high-water (always overwrite) | `test_counter_regression_never_looks_fresh` | **RED** |
| Disable occupancy/cumulative cross-label guard | `test_occupancy_and_cumulative_never_cross_labelled` | **RED** |
| Make sidecar write non-atomic (direct `write_bytes`) | `test_sidecar_interrupted_before_rename_keeps_previous_snapshot` | **RED** |
| Coerce missing status field to `0` instead of unknown | `test_status_line_startup_nulls_become_unknown_not_zero` | **RED** |
| Skip torn-line counting | `test_journal_torn_final_line_skipped_never_invented` | **RED** |
| Matrix `status` drift in fixture | `test_generic_matrix_equals_live_for_all_measured_entries` | **RED** |

The occupancy/cumulative separation, dedup, regression-never-fresh, atomic write, unknown-not-zero, torn-line "never invented", and generic matrix==live checks are all proven to have teeth.

---

## Per-QA-dimension verdicts (D-024 §16.1 rows in B1 scope)

**Complete / null / malformed status payloads — PASS.** `test_status_line_complete_payload`, `…_occupancy_vs_cumulative_separation`, `…_startup_nulls_become_unknown_not_zero`, `…_post_compaction_current_usage_null`, `…_non_dict_payload_fails_to_unknown`, `…_malformed_values_become_unknown`. The **reported-zero vs absent** distinction is real and has teeth (mutation M5): `context_total_input_tokens.value == 0` (reported zero preserved) while `cumulative_api_duration_ms.is_unknown` (absent → unknown), and `current_usage=None` (startup and post-`/compact`) → `unknown`. Field names verified faithful to the documented `official-docs` schema captured in the matrix capability entries `claude.statusline.primary_payload` / `.nullable_fields` (context_window.* → occupancy "live, never lifetime spend"; cost.* → cumulative; current_usage/percentages nullable; total_* reported-zero).

**Atomicity (interrupted before/after rename), overlap, rotation+retention, torn-line — PASS.** Before-rename (monkeypatched `os.replace` raises → previous snapshot intact), after-rename (leftover temp never corrupts read), 32 overlapping writers (parseable final in valid set), oversized snapshot refused with nothing written, unreadable sidecar → `None` not zero. Journal rotation with bounded generations + byte ceiling, oldest-first read-back, torn final line skipped+counted, single over-bound record refused. All covered with real assertions.

**Redaction (credentials / prompts / secrets / escapes / user paths) — PASS (see Advisory 2).** ANSI CSI/OSC/control chars stripped (tab/LF/CR preserved); credential + `KEY=value` masking; Windows and POSIX home prefixes → `[HOME]`; prompt-like keys digest-withheld; 5000-char text bounded to excerpt+digest; status-record transcript path `[HOME]`-masked at journal write; `probe_meta` shape-preserving redaction. Order (escapes → paths → secrets → bounding) is correct so truncation cannot leak a secret head. No secret survives in the journal round-trip (`sk-ant` absent).

**Per-step vs cumulative distinct; dedup; regression-never-fresh; unknown-not-zero — PASS (see Advisory 1).** Step sums (`provider-exact`) and reported totals (`sdk-cumulative`) live in separate name families and never merge; message-ID dedup (bounded LRU); counter regression retains high-water and counts the reset (never "fresh"); empty accumulator → all-unknown; malformed/unidentified steps counted with lower-bound detail.

**No installs / SDK absent / no worker-facing counters — PASS.** Suite is stdlib-only and installs nothing; no `pip install`/`subprocess`/`import anthropic`/`import claude_agent` in the telemetry modules. AST test `test_no_telemetry_module_injects_model_context` proves no non-docstring string contains `additionalContext`/`hookSpecificOutput` (the sole occurrence is a docstring naming the prohibition). Independent grep for `conserve|countdown|quota|remaining tokens|budget|slow down|worker message` across all four modules → the only hit is the registry key `estimated_remaining_tokens` (a controller-private measurement NAME, not worker-facing text). R045 satisfied.

**Carried hardening bundle (M0-T086 G4-F1/F2/F3, G3-minor, G5-S1) — PASS.** `capability_probe.py` diff confirmed: `classify_flags` now uses word-boundary regex `(?<![\w-])<tok>(?![\w-])` (positives and negatives tested: `--print` no longer matches inside `--print-format`, `exec` not inside `execute`, `--strict-mcp-config` atomic); `_run` three failure branches (`TimeoutExpired`/`OSError`/non-zero exit → unknown) monkeypatch-tested; `--out`/`main`/`resolve_binaries` dual-install covered; generic matrix==live cross-check asserts `len(measured) >= 10` and per-entry equality over every measured-live id (via `_derive_live_status`, with an explicit `AssertionError` if an id is unmapped); `build_record` wires `redact_probe_meta(meta)` with **body byte-identical** (confirmed) and no import cycle (`telemetry_redaction` does not import `capability_probe`).

---

## Findings

**Advisory 1 (non-blocking) — `telemetry_ingest.py` ~L284-292: never-observed per-step field reports `0`, not `unknown`.** Once `_steps_ingested>0`, a token field never present in any ingested step reads `_step_totals.get(name,0)` → `value=0, label='provider-exact', detail='sum of deduplicated per-step usage'` with no lower-bound caveat (the caveat is gated on `_malformed_steps`, not per-field absence). Verified at runtime: a step of `{input_tokens:10, output_tokens:2}` yields `cumulative_cache_read_tokens = 0` (not unknown). This is *defensible* — a per-step SUM of observed contributions where an absent Anthropic cache field conventionally means 0 — so it is **not a correctness defect**, but it is philosophically inconsistent with the status-line "absent → unknown" rule and the fully-absent-field path is untested (`_step` always supplies explicit `0` cache fields). Recommend B2 re-decide 0-vs-unknown against real provider payloads and add a test.

**Advisory 2 (non-blocking for B1) — `telemetry_redaction.py` ~L152-158: prompt-like key with a list/dict value is not digest-withheld.** `sanitize_structure` withholds prompt-like keys (`prompt`/`conversation`/`instructions`/…) only when the value is a `str`. A prompt-like key holding a LIST or DICT of short (<512 char) message strings is walked and stored verbatim (escape/path/secret/bound only). Verified: `{'conversation': ['hello secret worker text', …]}` and `{'prompt': ['line one of prompt', …]}` are stored verbatim. **Zero impact on B1**: neither B1 ingestion path (`ingest_status_line`, `UsageAccumulator`) emits records with prompt-like list/dict keys, and long text (>512) is still bounded+digested. But it is a latent §5.3/R044 gap for the B2+ phases that WILL carry transcript/SDK/subagent structures. Recommend closing (recurse withholding into list/dict values under a prompt-like key) with a red/green test before M0-T089 transcript/message ingestion lands.

---

## Scope / provenance notes

- Frozen diff stays within `allowed_paths` (`tools/agent_supervisor/**`, `tools/test_agent_supervisor_telemetry_core.py`, `project-control/reports/M0-T088-*`) plus orchestrator-owned control-plane records; no `forbidden_paths` touched; no dependency manifest/lockfile changed (stdlib-only confirmed).
- Supervisor-freeze qualifying evidence **D-024-R100** is cited in the packet objective, the producer report, and the commit message; suite baseline re-established. Actuation stays OFF (no consumer of these records); nothing installs the SDK.
- This is the **G4 QA** verdict only. The full requirement-by-requirement pass over the 34 applicable D-024 ids (evidence-map `M0-T088-evidence-map.json`) is the independent `directive-compliance-verifier`'s scope (`verification.json`, producer ≠ verifier) and is not adjudicated here; the QA-relevant requirements I directly exercised at frozen identity (R038, R039, R040, R042, R043, R044, R045, R100, R107, R120) reproduce PASS.

**Recommendation to orchestrator:** record **G4 = PASS**. The two advisory findings are non-blocking for M0-T088 acceptance; carry them forward as inputs to the M0-T089+ (Phase B2) packet rather than as rework on this task.

---

*Orchestrator disposition (recorded at gate time): G4 Advisory 1 (per-step absent-field 0-vs-unknown
decision + test) and Advisory 2 (wholesale withholding of prompt-like non-scalar values, required
BEFORE transcript/message ingestion lands) join G5-S2, G3-minor(a), and the test-helper nit as the
named cleanup bundle carried into the M0-T089 (Phase B2) packet — matching the M0-T086→M0-T088
carried-bundle precedent. None blocking for this task.*

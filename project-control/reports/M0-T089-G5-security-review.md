# GATE REPORT — M0-T089 — G5 independent security review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only, per the report-preservation rule). Reviewer: security-reviewer
(independent, read-only). Producer: orchestrator.

---

# G5 Security Review — M0-T089 (D-024 Phase B2)

**VERDICT: PASS** (no blocking findings; 3 minor + 2 nit advisory items, none gating)

**Reviewer:** security-reviewer (independent, read-only)
**Reviewed content identity:** `b7be085a73e2399367d7b28bfc3b7ddf0951e338` (frozen)
**Live HEAD:** `66d93999f2c3cbbb141543a305491a17a6c1a77c` — verified to differ from frozen only in `project-control/` records; `git diff --name-only b7be085 66d9399` shows zero non-control-plane files, so the reviewed code identity is intact.
**Evidence:** all commands reproduced locally (Python 3.11.9). Test suite executed: **86 passed** (`test_agent_supervisor_telemetry_core.py` + `test_agent_supervisor_subagent_telemetry.py`, 5.59s); the 37-case B2 file passes standalone.

## Scope confirmation
Frozen 18-file diff (`git diff --stat 9037bb3 b7be085`): 5 new modules (`telemetry_subagent/hooks/sdk/transcript/status.py`), carried fixes in `telemetry_ingest.py`/`telemetry_records.py`/`telemetry_redaction.py`, `fixtures/capability_matrix_v1.json`, two test files, and `project-control/` records. Confirmed the frozen diff touches **no** `.claude/`, `settings.json`, `ORCHESTRATION_POLICY.md`, `.claude/hooks`, or any dependency manifest (grep returned empty). `cli.py` and all control-flow modules are untouched. Stdlib-only imports throughout.

---

## Closure verifications (explicit)

### G5-S2 — CLOSED (verified)
`fixtures/capability_matrix_v1.json`: `claude_binary_note` and `claude.dual_install_resolution` now carry `[HOME]/…` in place of `C:/Users/MLFLL/…` and `AppData/Roaming/npm` (diff confirmed at frozen SHA). Closure is proven as a **class**, not one file: `test_all_committed_fixtures_free_of_home_prefixes` globs **all** `*.json` under the fixtures dir and asserts no real home prefix. I independently reproduced the identical regex scan against all 3 committed fixtures (`capability_matrix_v1.json`, `capability_probe_live_2026-08-25.json`, `m0_t063_documented_test_command.json`) → **zero leaks**. `test_matrix_binary_notes_are_masked` additionally asserts `"MLFLL" not in json.dumps(matrix)`. A tree-wide search for `MLFLL` under `tools/agent_supervisor` returns hits **only** in local `__pycache__/*.pyc` build artifacts; `git ls-files | grep -E '\.pyc$|__pycache__'` is empty and `git check-ignore` confirms `__pycache__` is gitignored, so those compiled paths are not in the public repo. No new file leaks paths/identity; test-fixture `cwd` values are synthetic (`C:/w1`, `C:/w2`).

### G4-Adv2 / D1 — CLOSED (verified)
`telemetry_redaction.sanitize_structure` (lines 169-174) now routes any prompt-like **key** whose value is non-empty — scalar **or** list/dict — through the new `withhold_prompt_value` (lines 84-97), which collapses the whole subtree to one canonical-JSON SHA-256 digest reference. **Ordering is sound:** the key-driven branch sits in the `elif` chain *before* the `else: out[key] = walk(value)`, so a prompt-keyed non-scalar is never recursed into and can never survive as per-string excerpts. The empty-container guard `value not in (None, "", [], {}, ())` keeps `[]`/`{}` honest (nothing to leak). Red/green proof present and passing (`test_prompt_like_list_and_dict_values_withheld_wholesale`): list and dict prompt values both become `[PROMPT-WITHHELD sha256=…]`, and `"secret worker"`/`"assignment"` are absent from the serialized output. I traced every `sanitize_structure` path and found no route where prompt content under a prompt key reaches the output.

---

## Per-dimension verdicts

**1. Data exposure (PUBLIC repo) — PASS.** G5-S2 masked and class-scanned (above). Transcript module (`telemetry_transcript.py`) extracts **only** numeric usage (via `acc.ingest_step(message.get("id"), message.get("usage"))` — id used for dedup, never emitted), compaction `preTokens`/`postTokens`/`trigger`, and `sessionId`; it never reads `message.content`/text. The per-step records it drives are discarded (accumulator side-effect only); its emitted record holds sums + counters. All persistence surfaces (`TelemetryJournal.append`, `TelemetrySidecar.update`) are sanitize-first: both call `_to_sanitized_dict` → `sanitize_structure` before any disk write (`telemetry_journal.py` lines 88-96, 116, 184). No B2 module persists on its own.

**2. G4-Adv2/D1 closure — PASS** (above).

**3. Injection surface — PASS.** Grep over the 5 modules for `eval|exec|compile|pickle|marshal|yaml|os.system|subprocess|popen|__import__|import_module|socket|urllib|requests|httpx` → **no matches**. SDK presence is probed with `importlib.util.find_spec` only (`telemetry_sdk.py` 40-49), wrapped in `try/except (ImportError, ValueError)`, no import/install/side-effect (R040 satisfied; `test_sdk_stays_absent_and_probe_has_no_side_effects` asserts `sys.modules` stays clean). `telemetry_status.main` is argparse-only and read-only: `read_only_status` constructs `TelemetryJournal` (constructor sets attributes only) and calls `read_all`, which iterates only `.exists()` paths and never `mkdir`s — verified `test_status_main_prints_json_and_stays_read_only` (`not none.jsonl.exists()` post-run) and `test_read_only_status_assembles_without_writing` (before==after dir listing). Missing sidecar/journal → `null`/empty, never zero, never file creation.

**4. No model-context injection / autonomy broadening — PASS.** `test_no_b2_module_injects_model_context` AST-parses all five B2 modules and asserts no non-docstring string constant contains `additionalContext` or `hookSpecificOutput`. Grep confirms only `telemetry_status/transcript/sdk/hooks/subagent`, the two test files, and two report files reference the new symbols — **nothing in control-flow consumes the records** (shadow). No `.claude/`, settings, policy, or manifest changes.

**5. Resource safety — PASS with minor advisories.** `SubagentRegistry` is bounded (`max_entries=512`) with correct **closed-first** eviction (`_evict` scans oldest-first for a closed entry, else `popitem(last=False)`); an attacker-shaped event stream cannot grow it without bound (`test_subagent_registry_bounded_eviction_prefers_closed` confirms). `UsageAccumulator` dedup memory bounded (`max_seen_ids=4096`). Transcript derivation is line-streamed; the journal's single-record byte bound (`TelemetryBoundsError`) backstops oversized records at persistence. See minor items M1/M2 for the two unbounded-in-principle dicts (both non-material under the threat model).

**6. Worker-facing leak (R045) — PASS.** No usage numbers reach any worker-visible surface. Records are controller-private; the only output sink is `telemetry_status.main` → stdout (operator CLI, not a hook/statusLine, not wired in `.claude/settings.json`, which is unchanged and a forbidden path). No `additionalContext`/`hookSpecificOutput` emission anywhere.

**7. Secret scan — PASS.** Secret-pattern grep over added lines matched only LLM "token/tokenCount/tokenSamples" and `sdk-task-cumulative` label strings — no credentials, keys, or bearer tokens.

---

## Findings

**Minor (non-blocking, advisory)**

- **M1 — `SdkTaskTracker._tasks` has no cardinality bound** (`telemetry_sdk.py:62,77`). Unlike `SubagentRegistry`, the per-task dict grows one small entry per distinct `task_id` with no eviction. **Not material:** the Agent SDK is absent-by-policy (this path is inert in production today), task_ids originate from the trusted local SDK (not an untrusted network source), entries are tiny, and the module is shadow-only. Recommend, for consistency with the registry's bounded philosophy, adding an analogous cap when/if the SDK path is ever activated. Not gating.

- **M2 — Transcript accumulators (`compactions`, `session_ids`, `unknown_types`) are unbounded in principle** (`telemetry_transcript.py:57-59`). An adversarial transcript with millions of compact-boundary/unknown-type lines would grow these. **Not material:** the transcript is the operator's own local file (not remote-attacker input), records are not persisted by B2, and the journal single-record byte bound would reject an oversized record at write time. An explicit cap would be tidier. Not gating.

**Nit**

- **N1 — `sanitize_structure` sanitizes dict values but not dict keys** (`telemetry_redaction.py:159-177`). The only data-derived keys today are transcript `unknown_types` (`str(ltype)`); all other attribute dicts use fixed keys and sanitized values. Since transcript records are not persisted, there is no live leak, but if a future write-path stores data-derived keys, a maliciously-shaped `type` value could place unsanitized text in a stored key. Defense-in-depth suggestion for the eventual persistence wiring. Not gating.

- **N2 — `compactions[].post_tokens` / `.trigger` stored without type-narrowing** (`telemetry_transcript.py:88-93`). `preTokens` is validated (`int/float>=0 or None`) but `postTokens`/`trigger` are stored raw. Normally numeric/enum; if ever persisted they pass `sanitize_structure` first (values sanitized). No leak; symmetry-only observation.

---

## Regression / correctness notes (not security defects)
SDK high-water logic (duplicates counted, regressions retain high-water, out-of-order completion tolerated, final `usage` labelled `final_request_*` never assumed cumulative — R043) is proven by dedicated tests. `UsageAccumulator` never-observed-field-is-unknown (G4-Adv1) and `step_*` vs `cumulative_*` name families (G3-minor) are red/green tested and pass. No regressions: full core+B2 suite green.

**Recommendation to orchestrator: record G5 = PASS.** G5-S2 and G4-Adv2/D1 closures are independently reproduced. The three minor/nit items are advisory hardening for the eventual owner-activated persistence/actuation path and do not block acceptance of this shadow-only, controller-private telemetry.

---

*Orchestrator disposition (recorded at gate time): advisory items M1 (SdkTaskTracker cardinality
bound), M2 (transcript accumulator bounds), N1 (data-derived dict-key sanitization), and N2
(postTokens/trigger narrowing) are carried as named hardening inputs into the next Phase B/C task
that wires persistence or activates these paths (campaign record names them at advance). None
blocking for this shadow-only task.*

# GATE REPORT — M0-T088 — G5 independent security review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only, per the report-preservation rule). Reviewer: security-reviewer
(independent, read-only). Producer: orchestrator.

---

I have everything needed. The probe's subprocess invocation, `PROBE_COMMANDS`, `MUTATING_TOKENS`, and resolved-path execution are all unchanged; the only probe edits are the `redact_probe_meta` wiring, the `import re`, and the word-boundary `classify_flags` (which `re.escape`s each fixed-allowlist token — no injection). The new persistence classes (`TelemetryJournal`/`TelemetrySidecar`/`UsageAccumulator`/`ingest_status_line`) are imported only by the test file and their own package-internal siblings — no live loop, hook, controller, or worker surface consumes them, confirming shadow mode.

Here is my full G5 report and verdict.

---

# G5 Security Review — M0-T088 (D-024 Phase B1: telemetry core + primary-session ingestion, shadow)

**Reviewer:** security-reviewer (independent, read-only)
**Reviewed identity (FROZEN):** `23f0d80a1e6097e0e8f7616be3fde43de3a202cd`
**Live HEAD:** `74dc0987c3c89a0be2e6d938bf00431d4004a577` — verified to add **only** control-plane records (`git diff --stat 23f0d80..HEAD -- tools/` is empty; the two extra commits touch only `project-control/gates`, `state.json`, `tasks/M0-T088.json`). Source identity is intact.
**Repository:** PUBLIC.

## VERDICT: PASS

The four new stdlib-only modules are sound, the redaction ordering and bounds are correctly enforced sanitize-first, there is no injection/eval/deserialization surface, no model-context injection, and the shipped feature is genuinely shadow-only (no live consumer). The **G5-S1 loop is CLOSED** for its scoped target (`probe_meta`). I record one **non-blocking minor** finding: a *sibling* fixture (`capability_matrix_v1.json`, introduced by the prior task M0-T086, outside this task's diff) still publishes the operator's real username and home paths in the public repo — the same exposure *class* as G5-S1, in a file the probe_meta remediation did not cover. It does not block this gate but should be queued as a follow-up.

Evidence reproduced in-sandbox (Python 3.11.9): `tools/test_agent_supervisor_telemetry_core.py` → **49 passed**; `tools/test_agent_supervisor_capability_probe.py` → **16 passed** (no regression from the hardening). Credential scan at the frozen SHA across all changed files is clean.

---

## G5-S1 CLOSURE STATEMENT (explicit)

**CLOSED for probe_meta.** The regenerated fixture `tools/agent_supervisor/fixtures/capability_probe_live_2026-08-25.json` `probe_meta` block now shows `[HOME]\.local\bin\claude.EXE`, `[HOME]\AppData\Roaming\npm\...` — no `C:\Users\MLFLL` prefix, no username. The frozen diff of that file touches only the five `probe_meta` binary-path lines and `generated_at`; the deterministic `body` is untouched, corroborating the "body byte-identical" claim. `capability_probe.build_record()` now returns `{"body": body, "probe_meta": redact_probe_meta(meta)}` (`capability_probe.py:201`), routing metadata through `telemetry_redaction.redact_probe_meta` → `sanitize_structure` → `redact_user_paths`. Two tests lock this: `test_committed_live_fixture_probe_meta_is_redacted` (asserts no `"Users"`/`"/home/"` in the committed fixture) and `test_probe_meta_paths_are_home_redacted_live` (asserts freshly-generated meta is `[HOME]`-prefixed). A direct `git grep` for `MLFLL`/home prefixes over the frozen changed set returns nothing in the new files or the fixture.

---

## Per-dimension verdicts

### 1. Data exposure & redaction ordering — PASS
- **Sanitize-first on both write paths (VERIFIED).** `TelemetrySidecar.update` (`telemetry_journal.py:114`) and `TelemetryJournal.append` (`:182`) both call `_to_sanitized_dict` (`:88`) as their first operation; that runs `sanitize_structure(raw, extra_literals=never_send)` before any `json.dumps`, bound-check, or `os.replace`/append. No code path writes a raw record. The bound is measured on the *sanitized, serialized* bytes, so redaction growth (digest markers) is accounted for before the write decision.
- **Ordering escape-strip → path-mask → secret-redact → bound (VERIFIED).** `sanitize_text` (`telemetry_redaction.py:90-118`): `strip_terminal_escapes` → `redact_user_paths` → `redact_text` → `bound_text`, in that order.
- **Truncation cannot leak a recognized secret head (SOUND).** Because `redact_text` runs *before* `bound_text`, any pattern-matched credential is already collapsed to a short `[REDACTED:label]` marker that the 128-char excerpt cannot bisect; and `bound_text`'s digest is computed over the already-redacted string, so the digest itself reveals nothing. Test `test_long_free_text_bounded_with_digest_reference` confirms `[TRUNCATED sha256=…]` behavior. (Inherent limitation, not a defect: pattern-based redaction cannot catch an *unstructured* secret with no key/shape; that is the accepted D-007 posture.)
- **Prompt-like keys withheld digest-only (VERIFIED for string values).** `PROMPT_KEY_PATTERN` (`:42`) → `withhold_prompt` emits `[PROMPT-WITHHELD sha256=… chars=…]`; test `test_prompt_like_keys_withheld_as_digest_references` confirms no source text survives.
- **No raw payload to disk before sanitization (VERIFIED).** As above.

**nit (defense-in-depth, not exercised today):** In `sanitize_structure` (`telemetry_redaction.py:152`) the prompt-withhold branch fires only when the value is a **string** (`isinstance(value, str)`). A prompt-like key whose value is a nested list/dict (e.g. `"conversation": [ {...} ]`) is *not* wholesale-withheld — its inner strings are recursively bounded to ≤512 chars each but retained as excerpts. No current ingestion path routes conversation/transcript arrays into a record (status-line ingestion stores only `transcript_path`, not transcript text), so this is latent. Consider withholding the whole subtree when a prompt-like key holds a non-scalar, before later phases wire richer payloads.

### 2. Secret-pattern quality / D-007 reuse — PASS
- **No weakening of the D-007 pass.** `tools/agent_supervisor/redaction.py` is **not** in this task's diff (verified against the frozen file list); `telemetry_redaction` imports and reuses `redact_text` and `SENSITIVE_KEY_PATTERN` unchanged (`telemetry_redaction.py:29`). The sensitive-key masking in `sanitize_structure` mirrors `redact_structure` exactly (including the None/empty shape-preservation).
- **`extra_literals` (never_send) plumbed through (VERIFIED).** `TelemetrySidecar`/`TelemetryJournal` accept `never_send` (`:104`,`:157`) and pass it as `extra_literals` via `_to_sanitized_dict` → `sanitize_structure` → `sanitize_text` → `redact_text`, where literals are masked verbatim before the pattern pass.
- Test `test_journal_append_read_round_trip_and_redaction` proves `api_key` value → `[REDACTED:sensitive_key]` and `sk-ant-…` disappears from the stored line and the read-back.

**nit (inherited D-007 behavior, not a regression):** Dict **keys** are preserved verbatim (only values are sanitized). Provider-controlled `rate_limits` sub-keys are passed through as keys. In practice these are fixed labels (`five_hour`, `seven_day`); low risk, and consistent with the documented D-007 "keys are structure, not payload" choice.

### 3. Injection surface — PASS
- **No eval/exec/compile/pickle/marshal/yaml/`__import__`/`os.system`** in any of the four telemetry modules (grep-verified). Ingestion consumes already-parsed structures with strict `isinstance` guards and never deserializes untrusted bytes; journal/sidecar reads use `json.loads` only and fail closed to `None`/skipped-line (never invent).
- **subprocess only in `capability_probe`, unchanged and safe.** The frozen `capability_probe.py` diff adds only (a) `import re` + `from .telemetry_redaction import redact_probe_meta`, (b) word-boundary `classify_flags`, (c) the `redact_probe_meta(meta)` wrap. The `_run` call — `subprocess.run([exe, *argv[1:]], capture_output=True, text=True, timeout=30, check=False)` — is **untouched**: `shell` is not passed (→ `shell=False`), argv is the fixed `PROBE_COMMANDS` allowlist, and execution is via the `shutil.which`-**resolved** path. `MUTATING_TOKENS` guard intact; `test_probe_allowlist_is_read_only` enforces no mutating verb in the allowlist.
- The new `classify_flags` regex applies `re.escape(tok)` to each token (`capability_probe.py:128-129`); tokens come from the fixed `CLAUDE_FLAG_TOKENS`/`CODEX_FLAG_TOKENS` lists, so there is no attacker-controlled regex path regardless.

### 4. No model-context injection / no autonomy broadening — PASS
- **AST structural test present and correct.** `test_no_telemetry_module_injects_model_context` (`:505`) parses each of the four modules, extracts every **non-docstring** string literal, and asserts neither `additionalContext` nor `hookSpecificOutput` appears — i.e. docstrings may *name* the prohibition, code may not compose it.
- **Shadow confirmed by consumer analysis.** A repo-wide grep for `TelemetryJournal|TelemetrySidecar|UsageAccumulator|ingest_status_line|telemetry_*` shows the only importers are the test file and the modules' own package-internal siblings (`telemetry_journal`→records/redaction; `telemetry_ingest`→records; `capability_probe`→`redact_probe_meta` for offline fixture generation). No live supervisor loop, hook, controller, `SendMessage`, or worker channel consumes the records. Nothing actuates.
- **No governance/config surface touched.** Frozen file list confirms no `.claude/hooks`, `.claude/settings.json`, `.claude/ORCHESTRATION_POLICY.md`, or dependency manifest changed (all in the packet's `forbidden_paths`). Imports are stdlib + package-internal only (`dataclasses`, `hashlib`, `re`, `json`, `os`, `pathlib`, `threading`, `itertools`, `time`, `collections`, `typing`).

### 5. Resource safety — PASS
- **Bounds checked before write in every path (VERIFIED).** Sidecar: `len(payload) > self.max_bytes` (256KiB default) raises `TelemetryBoundsError` **before** `_atomic_write_bytes` (`:119-125`); test `test_sidecar_bounds_refuse_oversized_snapshot` asserts `read() is None` afterward (nothing written). Journal: `len(line) > self.max_bytes` (4MiB default) raises **before** rotate/append (`:187-191`). A hostile payload cannot bypass — the check is on the final sanitized serialized bytes.
- **Generation cap enforced.** `_rotate` (`:170`) drops `.max_generations` oldest; `test_journal_rotation_and_bounded_retention` verifies nothing beyond `.2` survives and total bytes stay bounded.
- **Atomic temp files cleaned on failure.** `_atomic_write_bytes` (`:56`) writes a pid+counter-unique temp, `flush`+`fsync`, then `os.replace`, with a `finally` that unlinks a surviving temp only on the failure path. `test_sidecar_interrupted_before_rename_keeps_previous_snapshot` and `..._after_rename_shows_complete_new_snapshot` prove no torn reads.
- **fsync behavior correct.** Sidecar always fsyncs; journal fsyncs when `fsync=True` (default). Read paths tolerate torn final lines (skipped + counted, never invented).
- No ReDoS: `_HOME_PREFIXES`, `_TERMINAL_ESCAPES`, and the reused D-007 patterns use bounded/negated classes and lazy `.*?` with no nested quantifiers; per-record input is capped by the 4MiB journal bound.

**nit (reliability, not security):** `_rotate` uses bare `os.replace` without the bounded `PermissionError` retry that `_atomic_write_bytes` has. Rotation is serialized under an in-process lock and the design is single-controller, so this is not exploitable; worth mirroring the retry if cross-process journaling is ever introduced.

### 6. Worker-facing telemetry leak (D-024 R045) — PASS
No usage number reaches any worker-visible surface. The modules persist to controller-private sidecar/journal files and *return* records to their (orchestrator) caller; there is no `SendMessage`, `additionalContext`, status-line emission, or worker channel anywhere in the four modules. Reinforced by the shadow analysis (dimension 4) — no live consumer exists at all. The ingest docstrings explicitly document "nothing here prompts the model, adds additionalContext, or messages a worker."

### 7. Secret scan — PASS (with tooling caveat)
- `git grep` at the frozen SHA over all changed source/fixture/report files for `AKIA|ASIA|sk-ant-…|gh[pousr]_…|xox…|-----BEGIN|eyJ….` returns **only** the redaction **pattern definitions** in `redaction.py:46,52` — detection patterns, not secrets. Test fixtures such as `sk-ant-abc123456789012345`, `hunter2-value`, `super-secret-value` are obviously synthetic and exist precisely to prove redaction fires.
- The report `M0-T088-telemetry-core.md:21` uses a generic `C:\Users\name` as documentation of the masking rule — not the real username.
- **gitleaks hook presence: not directly confirmable in this sandbox.** This checkout's `.git` is a **linked-worktree pointer** (not a directory: `.git/config`, `.git/hooks/*` are unreachable; the shared gitdir lives elsewhere), and the read-only guard blocks `find`/`git config`. Per review protocol I did **not** return BLOCKED for this — instead I verified the **security outcome directly**: the committed content of both frozen commits contains no credential-like material. Recommend the orchestrator confirm hook installation out-of-band if a positive attestation is required.

---

## Findings summary

| ID | Severity | File:line | Status |
|----|----------|-----------|--------|
| G5-S1 | (prior) | `capability_probe.py:201`, fixture `probe_meta` | **CLOSED** — probe_meta home paths masked, tested |
| G5-S2 | **minor (non-blocking; follow-up)** | `tools/agent_supervisor/fixtures/capability_matrix_v1.json:12` | Open — pre-existing, outside this diff |
| D1-nit | nit | `telemetry_redaction.py:152` | Non-scalar prompt-key values not wholesale-withheld (latent) |
| D2-nit | nit | inherited D-007 | Dict keys preserved verbatim (provider-controlled keys) |
| D5-nit | nit | `telemetry_journal.py:170` | `_rotate` lacks the PermissionError retry (reliability) |

**G5-S2 detail (minor, non-blocking):** `capability_matrix_v1.json:12` (`"claude_binary_note"`) still contains `C:/Users/MLFLL/.local/bin/claude.EXE` and `AppData/Roaming/npm/...` — the operator's real username and install layout, in a PUBLIC repo. `git log` shows it was introduced by **M0-T086 (372b4f7)**, not this task, and it is **outside the M0-T088 frozen diff** and outside G5-S1's scoped target (which was `probe_meta` specifically). It therefore does **not** block this gate. However, it is the same exposure *class* G5-S1 addressed, so the repo-level objective ("no operator home paths/username in the public repo") is not fully met while this hand-authored fixture remains. Recommend a follow-up remediation task to `[HOME]`-mask this note (and a lightweight test asserting no `Users\<name>`/`/home/<name>` prefix across **all** committed `agent_supervisor/fixtures/*.json`, so the class is closed rather than one file at a time).

---

## Modularity note
Four focused modules with clear single responsibilities (records = typing/validation; redaction = sanitization; journal = persistence/bounds/rotation; ingest = feed parsing), well under thresholds, explicit interfaces, no dumping-ground, and dedicated boundary tests. No responsibility mixing observed. (Full modularity adjudication belongs to G3; noted here only as consistent with the security posture.)

**Recommended orchestrator action:** record G5 = **PASS**; open a follow-up task for G5-S2 (mask `capability_matrix_v1.json` + add a cross-fixture home-prefix assertion). Nits D1/D2/D5 are optional hardening for later phases.

---

*Orchestrator disposition (recorded at gate time): G5-S2 (pre-existing matrix-fixture home paths,
outside this frozen diff) + the cross-fixture home-prefix assertion are carried as a named
follow-up item into M0-T089 (Phase B2), matching the M0-T086→M0-T088 carried-bundle precedent.
Nits D1/D2/D5 noted as optional hardening for later phases; no action this task.*

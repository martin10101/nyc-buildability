# M0-T143 — Evidence record: Codex `--output-schema` strict-subset repair (D-024 Amendment 46)

## 1. Frozen corrected candidate

| Identity | Value |
|---|---|
| Frozen corrected candidate commit | `3f4cee8680ba5c9a167327507af387d316f5dbc3` |
| Commit tree | `04688351af830e5cb15cab7d1653054b15044515` |
| `tools/agent_supervisor` subtree tree | `209026fdf83b160b1d42f0009fdaccdd3148e52f` |
| Branch | `candidate/D-024-mrl-option-b` (local; base `origin/main` `d8b3899f`) |
| Installer binding | `tools/controller_update/source_binding.json` rebound to `3f4cee86` (supersedes `f8f0f0c8`) |

Every later commit in this task is control-plane only (reports, binding, handoff); none touches
`tools/agent_supervisor/**`, so the supervisor subtree tree above is the reviewed material identity.

## 2. The defect (named; ERS §1/§3.3)

canary-b5-02r2 (2026-09-02 22:34–22:37Z, runtime dir `9aca7075…` = `C:\SupervisorController`):
the Fable-5 worker leg PASSED end-to-end; the Codex reviewer child spawned and exited 1 in ~1–3 s
with an EMPTY stderr tail and an empty `--output-last-message` file → `no_decision` →
`review_unavailable` → WAIT_FOR_OWNER (audit seq 48; journal transitions 20–25). The owner's
diagnostic probe captured the provider error verbatim:

> `invalid_request_error` / code `invalid_json_schema`, status **400**, param `text.format.schema`:
> `Invalid schema for response_format 'codex_output_schema': In context=('properties',
> 'evidence_ref_ids'), 'uniqueItems' is not permitted.`

Probe evidence directory:
`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\codex-schema-probe-20260902-191655532`
(`stdout.jsonl` UTF-16, sha256 `5e51a5c51fd5e6da12fb4f9cf6d9076b0eec71e7da42e4f760a69af49d453faf`;
`stderr.txt` empty — confirming the R706 blindness: under `--json` the provider error travels on
stdout, which the pre-repair failure path discarded).

Sibling-defect history: `codex_decision.schema.json` hit this same provider constraint earlier
("'allOf' is not permitted") and received a static regression guard
(`test_agent_supervisor_reviewer.py::SchemaStrictSubsetTests`) — but the guard covered only that
one file and only composition keywords; `review_verdict.schema.json` (M0-T136) was created outside
it and was never live-exercised until canary-b5-02r2 (b5-01 refused pre-launch; b5-02/b5-02r1
stopped before review). M0-T143 closes the class with a runtime pre-spawn inspection over every
Codex-facing schema plus a sweep test over every provider-facing schema.

## 3. The change (ERS §2 smallest fitting change)

One bounded package at the owning boundaries, no new module, no parallel implementation:

1. **`schemas/review_verdict.schema.json`** — flattened in ONE change to the provider-proven
   strict subset: `uniqueItems`, `minLength`, `maxLength`, `minItems`, `maxItems` removed
   TOGETHER (R702). Retained: types, enum, required, array item type,
   `additionalProperties:false`.
2. **`mrl_codex_decision.py`** — every removed guarantee enforced in
   `ReviewVerdict.from_provider` at the trust boundary (R703): nonempty rationale ≤ 4096; 1..64
   evidence ids; nonempty ids ≤ 128 chars; uniqueness (duplicates named); issued-ids-only
   (pre-existing); shape/types/enum/no-extra-keys still via `validate_instance` over the
   flattened schema. Constants `RATIONALE_MAX_CHARS`/`EVIDENCE_REF_IDS_MAX`/
   `EVIDENCE_REF_ID_MAX_CHARS` carry the old schema values.
3. **`mrl_provider_schema.py`** — `assert_codex_output_schema_strict`: fail-closed typed
   refusal (`codex_schema_unsupported_keyword`) of any non-structural keyword, open object, or
   not-fully-required object, called BEFORE ANY spawn (even the `--version` probe) in
   `OneShotReviewer.review` and `CodexReviewer.review` (R705).
4. **`codex_reviewer.py`** — `bounded_stream_tail` (redact-then-bound, explicit truncation
   marker, 600 chars) + `failure_tails`; `no_decision_error` now carries both tails;
   `OneShotReviewer` classifies through the shared helper: a provider failure event becomes
   `provider_rejected_request` with the parsed first `error`/`turn.failed` code+message, the
   child returncode, and both bounded redacted tails; an unparseable failure is
   `missing_decision_file` with the same diagnostics; the timeout path also carries tails.
   A known provider error is never reduced to a bare `no_decision` (R706). Full prompt,
   credentials, and unbounded output never land in the record (redaction seeded-token test +
   truncation test).
5. **`fixtures/codex_schema_probe_20260902.jsonl`** — the owner capture re-encoded UTF-8
   (fixture sha256 `3c40d9e9af9e228cebd0ec0f9c89627372dfccb262125abf494bc6b0405e60a0`), used as
   the regression fixture; the fixture-driven test asserts the parsed classification carries
   `invalid_json_schema` and `'uniqueItems' is not permitted` (R710).

Model pin untouched (R707): no model-selection surface in the diff; no `fable` alias and no
`claude-fable-5-1` anywhere in the change; the owner script re-validates `claude-fable-5` via the
doctor's `model_selection` row before the canary.

## 4. Behavior proof (ERS §3; red → green → mutation)

- **RED (schema-flatten guarantee loss observed):** at the flattened schema WITHOUT controller
  bounds — `python -m pytest tools/test_agent_supervisor_mrl_codex_decision.py -q` →
  **2 failed, 14 passed** (`test_lengths_and_cardinality_rejected`,
  `test_more_than_max_ids_rejected`).
- **GREEN:** after the `from_provider` bounds — same command → **24 passed** (including the new
  `M0T143ControllerEnforcedBoundsTests`: boundary accepts 4096/64/128, empty-rationale,
  overlong-rationale, empty-id, duplicate-ids-named, wrong-item-type, non-object payloads).
- **RED (observability):** pre-repair MRL path returned `no_decision`
  (`test_no_json_object_is_no_decision` 5 params failed against the new contract) — retyped to
  `missing_decision_file` + tails.
- **Mutation proof (§3.4, recorded pair):** uniqueness check disabled
  (`if False and len(set(ids)) != len(ids)`) → `test_lengths_and_cardinality_rejected` +
  `test_duplicate_ids_name_the_duplicates` **2 failed**; restored → **2 passed**.
- **Pre-spawn proof:** `test_unsupported_schema_keyword_refuses_before_any_spawn` asserts
  `rh.calls == []` AND `rh.version_calls == []` — zero child processes for a rejected schema.

## 5. Verification contexts (ERS §8)

- Focused suites (touched surfaces): `mrl_provider_schema` + `mrl_codex_decision` +
  `mrl_one_shot_review` + `reviewer` + `ephemeral_review` + `codex_channel` +
  `mrl_worker_result` → **339 passed** (then +new tests → 47/24/81 per file, all green).
- **Full affected-suite regression at the frozen candidate `3f4cee86`** (§8.8, one run):
  `python -m pytest tools/test_agent_supervisor_*.py -q` →
  **3626 passed, 2 skipped, 0 failed in 288.69 s** (raw exit 0). The 2 skips are the
  pre-existing baseline shape (M0-T142 freeze: 3593/2/0 at `f8f0f0c8`; M0-T141: 3566/2/0).
  Supervisor-freeze suite-baseline duty (≥ 1165, 0 failures) re-established.
- Lint: `ruff check` on every touched file → **All checks passed** (4 pre-existing errors in
  untouched files `config.py`/`github_flow.py`/`rotation.py` under local ruff 0.9.9; CI runs
  0.13.0 and is green at the base).
- Modularity: `python tools/modularity_check.py --check` → no new findings (3 pre-existing
  warnings in untouched files).
- **No live provider call anywhere in implementation or tests** (R710): every Codex process is
  the injected `ReviewHarness`/fake seam; the fixture is a static file.

## 6. Recovery-path determination (R709) — explicit statement

**The controller has NO safe supported review-resume path.** Evidence:

- `loop.py` `CYCLE_ENTRY_STATES = {PREFLIGHT, START_CLAUDE, CLAUDE_RUNNING}` — a cycle can never
  begin at `CODEX_REVIEW`; the evidence packet is built in-cycle from the live worker checkpoint.
- The only `WAIT_FOR_OWNER` exits are `resume-pending-prompt` (requires a `pending_prompt/<run>`
  record — canary-b5-02r2 forwarded nothing, so none exists) and the restart-channel
  `resume-after-answer` (`owner_answer_validated` → `PREFLIGHT`), which re-runs full preflight.

Therefore, per the owner's stated fallback, the package uses **one successor full canary**
(`canary-b5-02r3`, one fresh Fable-5 worker launch + one Codex review), reached through the
canonical audited surfaces only: `recovery-status` → `resume-after-answer` (WAIT_FOR_OWNER →
PREFLIGHT, fail-closed on SAFE_CHECKPOINT classification) → `start --launch-manifest`. No bypass
is invented; no state is hand-edited.

## 7. Corrected canary reporting semantics (R708)

For the preserved canary-b5-02r2 and for the successor readout:

- Item 3 (child authentication) splits legs: **Claude authentication = PASS**
  (session `fc7ddb4c-0120-4d66-8457-ae3780e521bf`); the Codex leg alone was unavailable.
- Item 4 (Fable WorkerResult / runtime identity) = **PASS** (primary `claude-fable-5`, argv
  `--model claude-fable-5`, launch version 2.1.252 == pin).
- Item 7: the worker execution succeeded; **Codex review was the only failed/unavailable leg**
  (now typed `provider_rejected_request` instead of blind `no_decision`).
- Item 8 (bounded subagent fan-out) = **already PASS** in canary-b5-02r2.
- Item 10 = **NOT_RUN** (merely not reached), executed by the successor script after a passing
  canary.

## 8. Reliability-standard sections applied

§1 (differential trace, prior turn), §2.1/2.2/2.5 (owning-boundary fix, reuse of
`provider_failure_reason`/`no_decision_error`, no parallel path), §3.1–3.5 (red/green recorded,
behavior-shaped asserts, defect named in tests, mutation pair recorded, no weakened test — the
one retyped test tightened), §7.1/7.4/7.5 (typed stable codes, redaction before bounding, cause
chained via shared classification), §8.2 (Windows host run), §8.8 (frozen-identity full run),
§8.9 (independent G3/G4/DCV follow).

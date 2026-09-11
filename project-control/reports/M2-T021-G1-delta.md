<!-- Reviewer return preserved VERBATIM by the orchestrator (report-preservation rule,
.claude/rules/project-control.md). Reviewer: independent code-reviewer subagent
(G1 delta re-review), returned 2026-09-11, reviewed HEAD 96c398aa. -->

All verifications complete. Working tree matches HEAD for the reviewed source; the guard is present at HEAD 96c398aa. Here is my delta-review report.

---

VERDICT: PASS

# M2-T021 — G1 independent code DELTA re-review (round-2 corrections)

**Reviewer:** code-reviewer (independent; same reviewer as the prior G1 rounds at `d4cdbe79` and `eb6a15f8`; did not write this code)
**Reviewed HEAD:** `96c398aa` (ledger resubmit). Delta reviewed: producer commit `01c01c5f` (4 files, +115/−21) and record commit `7a43d2d0` (3 files, +16/−7).
**Scope:** delta only, per the prior re-review at `eb6a15f8` (PASS with three corrections BLOCKING acceptance). I did not re-review the whole connector.
**Discipline:** read-only per ADR-005. No file written (the guard blocked a scratchpad write; I ran the probe via stdin heredoc instead), no pytest/ruff, no ledger/git-write. All Python ran `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=.` from `services/api`, injected in-memory transport only. `git status` production source is unchanged (only ledger/report JSON and untracked memory/scratchpad show modified; the connector, tests and registry match HEAD byte-for-byte — `git diff 96c398aa` on those paths is empty).

---

## Blocking correction 1 — N1 (vacuous deep-copy assertion) → CLOSED

The vacuous assertion (`res.raw_fields["bbl"]="MUTATED"` then comparing two fresh disk parses) is **removed**, not replaced with another tautology (test file lines 163-169: only `assert res.raw_fields == addr` survives, with an honest comment explaining the removal). The deep copy stays in code, relabeled **defense-in-depth** at the dataclass field comment (`raw_fields` field) and in the module docstring — no longer over-claiming a digest-invalidation property.

I evaluated the ruling basis on the merits. **I could not construct any non-vacuous externally-observable assertion of the deep copy today, and I confirm none exists:**
- `provenance["response_digest"]` is a stored `str` computed before return — probe confirmed it is `str` and stable after mutating `res.raw_fields` (would hold identically with or without the copy).
- Each call re-parses `response.body` fresh (`json.loads` returns a new object) — probe confirmed a second call returns unmutated `raw_fields`; this depends on re-parsing, not on the copy.
- The connector retains no internal parsed state across the return (`parsed`/`address` are locals that die at return), and `raw_fields` aliases nothing else in the outcome (`provenance`, `request_params`, `suggestions` are all independently constructed). So even a shallow `raw_fields = address` would produce no observable difference for any current or nested fixture value.

The producer's/G3's reasoning that my originally-suggested replacements (digest-stability, second-call comparison) are themselves vacuous is **correct**. Disposition confirmed.

## Blocking correction 2 — N2 (type-drift swallow undocumented) → CLOSED

The rule is now stated in all three required consumer-facing places, behavior unchanged:
- **`AddressResolution` docstring:** "None in exactly two cases: OMITTED … or … DRIFTED type … drift is never coerced … drifted value preserved verbatim in `raw_fields`."
- **Module docstring honesty rules:** added as "the third honesty rule" beside null-omission and empty-string.
- **`geoclient.json` `response_semantics.type_drift_rule`:** present (probe confirmed the key exists and the file is valid JSON).

Behavior is pinned by `test_s8_type_drift_is_never_coerced` (numeric-bbl, string-latitude, bool-latitude). I reproduced all three end-to-end: canonical field → `None`, `raw_fields[field]` → drifted value verbatim. The documentation now matches the pinned behavior.

## Blocking correction 3 — N3 (allowed_paths mismatch) → CLOSED

The orchestrator recorded a **scope RULING** in the packet `progress_log` (entry `2026-09-11T23:10:12`, "ORCHESTRATOR SCOPE RULING") rather than widening `allowed_paths`, with the stated rationale (widening would move directive applicability under the selective-citation guard). Round-2 was split as required:
- **Producer commit `01c01c5f`** touches only `services/api/app/connectors/geoclient_address.py`, `services/api/tests/connectors/test_geoclient_address.py`, `docs/research/source-registry-drafts/geoclient.json`, `project-control/reports/M2-T021-producer-report.md` — I checked each against the packet `allowed_paths`; **all four are inside scope, none in forbidden_paths.**
- **Record commit `7a43d2d0`** carries the three out-of-scope record files (`docs/MVP_AGENDA.md`, `B-004`, evidence-map) under ADR-005 orchestrator record authority, separately.

This satisfies my original correction ("amend allowed_paths, or record the widening in the packet") — the disposition I explicitly deferred to the orchestrator. The producer-material commit now satisfies its scope on its face. Confirmed.

## Item 4 — G5-N1 RecursionError guard code quality → SOUND

Verified in source (`geoclient_address.py:698-712`) and reproduced via probe:
- **Placement before the constructor:** the `try/except` at 703-712 precedes `outcome = AddressResolution(...)` at 714. ✓
- **Both recursive ops covered:** `copy.deepcopy(address)` and `canonical_json_digest(parsed)` are both inside the one `try`; results hoisted and reused (`raw_fields=raw_fields`, `response_digest=response_digest`), so no double computation. I confirmed these are the only unbounded-recursion operations left — `json.loads` already catches `RecursionError` (line 676, same typed mapping), and `_malformed_shape_detail`/`_classify`/`_extract_suggestions`/`_string_or_none` are all flat `.get` access. No gap. ✓
- **Typed `MalformedResponseError`, `from None`, detail shape:** probe on a depth-600 body returned `MalformedResponseError` with `__cause__ is None` (confirming `from None` — no body-laden frames ride the traceback) and `detail` keys exactly `{body_chars, url}`. ✓
- **`deepnest600` test case:** present (`test_s5_malformed_200_bodies_fail_closed` ids include `deepnest600`), correctly built as a raw string to dodge `json.dumps` recursion, and robust to which layer (`json.loads` vs deepcopy) breaks first — both map to the typed error. ✓

## Item 5 — no new defects introduced by the delta

Full read of both commits. `01c01c5f` is additive docstrings + the guard + the hoist + the honest test edit; `7a43d2d0` is record/agenda/blocker corrective text. All three JSON files touched (`geoclient.json`, evidence-map, `B-004`) parse as valid JSON. The connector AST-parses; a clean-body call still returns `resolved`. No behavior change beyond the guard. **No defect of MEDIUM or higher introduced.** The LOW/non-blocking items (N4–N7 and the sibling/shared-engine sanitizer follow-ups) are correctly left as recorded carry-forwards in the preserved reports and MVP_AGENDA C4, not silently dropped.

---

## What I verified vs. took on record

**Independently verified (read + reproduced):** all three blocking corrections; the guard's typed behavior, `from None` suppression and detail shape; type-drift behavior for all three cases; the vacuity of the deep-copy assertions (digest is a stored string, calls re-parse fresh, `raw_fields` aliases nothing); allowed_paths membership of every `01c01c5f` file; JSON validity of all touched record files; working-tree-equals-HEAD for the reviewed source.

**Taken on record (CI is the execution authority, per ADR-005):** the producer's red/green record for `deepnest600` (fix-reverted → `RecursionError` FAILED; restored → 99 passed) and the aggregate `99 module / 438 connectors passed, ruff clean, modularity exit 0, secret-scan PASS`. I did not run pytest/ruff/modularity. My offline probe independently reproduced the fix behavior the red/green record asserts.

All three blocking corrections are genuinely closed, the main delta production change (the RecursionError guard) is correct and well-scoped, and the delta introduces no new defect. **VERDICT: PASS.**

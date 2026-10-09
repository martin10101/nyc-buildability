# M5-T040 producer report — PARTIAL implementation (web parity-test repair; backend wiring accounted, pending)

Task: M5-T040. Producer: backend-engineer. Stage: in_progress (PARTIAL — not a whole-task completion claim).
Directives in scope: D-073-R006 (DISPLAY CONTRACT / DB-025 a–c), D-045-R009 (DRAFT / not-verified
preservation), D-066-R001 (code-graph navigation). Contract v1.1.0 stays CLOSED — no schema, generated-TS,
integration.py, or response.py edit (none in allowed_paths; none touched).

This resubmission repairs the report-view wide-street parity tests and accounts for the backend
named-street wiring already present in the working tree. It is a PARTIAL M5-T040 increment: web changes
prove only in CI, and backend acceptance requires its own complete diff and evidence (below). Whole-task
completion stays pending.

## Web repair delivered (this resubmission)

`apps/web/src/components/architect/__tests__/report-view.test.tsx`

1. Restored the missing `within` import (`:7`) — the prior report claimed it was added but the file still
   imported only `cleanup, render, screen`, so every `within(...)` reference was unresolved.
2. Made the DB-025(c) provenance assertions work against the report's CLOSED `<details>`. `ReportView`
   nests `CalculationEvidence` inside `#brief-calculations` (`ReportView.tsx:94-97`), so the provenance
   `<h3>` is outside the accessibility tree until expanded. The heading queries now pass
   `{ hidden: true }` (`:224-225`, `:240`, `:254`) so they assert the heading regardless of the collapsed
   state, and a value-caption assertion read via `textContent` (`:226-227`, `:241`) — unaffected by the
   closed `<details>` — proves the intended caption too.
3. Preserved the within, not-within, and professional-review controls and the shared
   `reportValue === screenValue` comparison (`:230`), unchanged in intent.

## Web display gating (present from the prior loop increment; unchanged this resubmission)

- `CalculationEvidence.tsx:16-26,41,44` — provenance heading + value caption derive from
  `determination_state` (not-within → "Governing floor-area ratio"; within/review → "Wide-street
  conditional FAR"); DB-025(a) review-label gate (`:17,42`); DRAFT wording preserved (`:30,42,44`).
- `DevelopmentLimits.tsx:62-96` — `WideStreetResult` gates the whole panel on `determination_state`;
  accessible section label follows the within/not-within distinction (`:79`).
- `development-limits.test.tsx:621-649` — DB-025(c) panel + `aria-label` assertions.

## Backend modifications present in the working tree (accounted here — NOT removed, NOT out-of-scope)

Four `services/api` files carry the named-street WIRING integration and DB-021(e) coverage. These are IN
scope for M5-T040 (packet ORDER OF WORK step 3; outputs 2–3). They are neither deleted nor declared
outside the task on worker authority; they are held for backend clearance under its own evidence pass.

- `app/rules/wide_street_wiring.py` (+255) — consumes `named_street_override` at the attestation seam per
  WIRING SEMANTICS, fail-closed (D-051): `exceptions_checked` True only on all-NOT_MATCHED with
  fully-resolved typed inputs; MATCHED_OVERRIDE → professional-review refusal carrying override provenance;
  INDETERMINATE / any missing input → refusal unchanged; no alternate-width value applied numerically.
- `app/spatial/wide_street_live_provider.py` (+70) — provider construction of that status; DB-021(e)
  branches.
- `tests/rules/test_wide_street_wiring.py` (+334), `tests/spatial/test_wide_street_live_provider.py`
  (+28) — wiring truth-table + branch regression coverage.

Backend clearance requires the complete relevant backend diff and its independent-review evidence
(data-contract, code-review, qa, security, directive-compliance gates). That evidence is not assembled in
this unit, so **backend acceptance remains PENDING**. `named_street_override.py` / `test_named_street_override.py`
were closed at 987930a2 (RUN-45 harvest, DB-023 a–d) and are not reopened here.

## Documented-command outcomes (supervisor-reproduced this run)

cwd `services/api`:
1. `python -m ruff check .` → **All checks passed!**
2. `python -m pytest tests/rules/test_named_street_override.py tests/rules/test_wide_street_wiring.py -q`
   → **98 passed**
3. `python -m pytest tests/spatial/test_wide_street_live_provider.py -q` → **38 passed**
4. `python -m pytest tests/api tests/rules/test_rules_integration.py -q` → **475 passed**

cwd repository root:
5. `python tools/modularity_check.py --check` → **failures 0; warnings 21** (pre-existing review signals;
   `wide_street_wiring.py` is now above the warning threshold — a cohesion signal for the backend review to
   weigh before it grows further, not a CI failure).

No unrelated root lint was fixed (ruff surfaced none).

## Verification limits (honest)

- **Web proves ONLY in CI on the orchestrator-pushed head.** Thin-client policy: no local npm/npx/node was
  run or documented. Do not read the web test/report changes as verified until CI is green on the pushed head.
- The python/modularity commands above are supervisor-reproduced in-worktree this run.
- **Backend acceptance and whole-task completion remain PENDING** until the complete backend diff and its
  independent-review evidence are captured. This report is a partial-increment evidence pass, not a
  completion claim.

## Acceptance-scenario mapping (this increment)

- AS-6 (display, CI): three surfaces gate on `determination_state`; shared screen/report fixture — implemented; proves in CI.
- AS-8 (DRAFT/not-verified preservation): DRAFT + professional-review wording untouched.
- AS-1..AS-3 (DB-023): closed at 987930a2 (RUN-45), not reopened.
- AS-4 (wiring), AS-5 (provider hardening / DB-021(e)): backend present in-tree; documented suites green;
  acceptance pending the complete backend diff + independent review.
- AS-7 (ruff / suites / modularity / contract byte-untouched): documented suites green; modularity 0
  failures; contract files not in allowed_paths and not touched.

## Left to the orchestrator (out of producer scope)

Commits, pushes, and acceptance. Producer made no commit and no push; the closed contract is preserved.

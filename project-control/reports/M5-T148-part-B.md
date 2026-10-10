# M5-T148 part B - producer's report

The builder (frontend-engineer, an AI agent) made no report file in its commit; its return is kept here unchanged, saved by the orchestrator from the session transcript (`return-builder-w20-T148B.txt`).

```
I am an AI agent (frontend-engineer producer). M5-T148 PART B — presentation adapters — is built, all checks pass, one commit made. No STOP; no file outside my scope changed.

WORKTREE: /root/project/nyc-buildability/.claude/worktrees/agent-af7926118fdbbbbbe
COMMIT: 36887c5cf90d4392fe2e569cff02c8092bf78839  PARENT: 42fc2ae11e6b90084972e7ca32816cc50b8a085a (contract head). `git status --porcelain` empty.

FILES CHANGED (10; 880+/30-): the five adapters metric-format.ts, result-status.ts, result-identity.ts, presented-results.ts, presented-notices.ts under apps/web/src/lib/architect/, and their five tests under its __tests__/. The placeholders were replaced. Nothing else.

WHAT EACH ADAPTER GIVES ON THE BENCHMARK (recorded_215_16_northern_journey):
- metric-format: reads values for display — "20,150 sq ft", "0 sq ft" (0 is a value, never Not known), "1,234,567.89 sq ft"; null/undefined/non-finite → the not-known state, never a digit; an unknown unit → the bare number. The value is only read, never changed.
- result-status: the benchmark's 6 withheld states → "Not known" with the document reason and no numeric field; its 10 conditional states → "Conditional"; settled/absent → no marker. No code path to "Verified".
- presented-results: floor-area allowance values + the three withheld legal unit limits → allowance; the envelope heights + withheld lot coverage/rear yard/setback → envelope; building B → a SCHEDULED option, display "20,150 sq ft", status Conditional, note "Site fit not verified", never "achieved"; the capacity estimate → an estimate, the document's range "17.27 to 21.59" (ruling V9). A thin layer over the existing contract types.
- presented-notices: the two conditions repeated across the document (the lot-area-confirmed condition and the four-unchecked-conditions condition) are listed once as C1/C2; many results refer to them (floor-area values both, heights one, building B both); none lost (set-equal to an independent collection). capNotices(5 notices) → 3 shown + "2 more"; ≤3 → all shown, no count.
- result-identity: a known identity — lotBbl 4073340070, lotDisplay "Queens block 7334, lot 70", resultsId res-215-16-northern-journey, an 8-hex revision fingerprint (changes when the revision changes, so a stale export is caught); another lot → mismatch; a document with no scope (synthetic_all_answers_available) → unknown, never a guessed lot.

CHECKS (in apps/web unless noted; direct exit codes):
- `npx vitest run src/lib/architect` → EXIT 0; Test Files 24 passed (24), Tests 380 passed (380).
- `npm run lint` → EXIT 0 (2 warnings, both in pre-existing files I did not touch: lot-site-setup.test.tsx, study-vocabulary.test.ts; 0 from my files).
- `npm run typecheck` → EXIT 0.
- root `python3 tools/modularity_check.py --check` → EXIT 0 (warnings are all pre-existing services/api & tools files; none of my adapters flagged).
- root `python3 scripts/lanes/check_lane_paths.py --coverage` → EXIT 0, "LANE COVERAGE PASS: 9810 file(s), each owned by exactly one lane."

MUTATION PROOFS (in a scratch copy OUTSIDE the repo; reverted/deleted; repo untouched):
1. Zero turned into not-known: changed the guard `value == null` → `!value` in metric-format.ts. CAUGHT by metric-format.test.ts › "formats exactly 0 as '0 sq ft', never 'Not known'".
2. A withheld value given a number: changed the withheld branch display from the no-digit NOT_KNOWN_DISPLAY to `{ kind:"value", text:"999" }` in presented-results.ts. CAUGHT by presented-results.test.ts › "never gives a withheld value a digit, and only uses the four known kinds" (and two benchmark S6 tests).

ASSUMPTIONS / DECISIONS (please verify at the gate):
- ResultKind is "allowance" | "envelope" | "scheduled" | "estimate" — deliberately NO "achieved" member. Rulings V5/V8 ("nothing is called achieved"; a schedule whose site fit is not established is the scheduled area) override the §8 sketch's "achieved". Every building option (the building_alternatives AND, on legacy fixtures, the single building_option answer) is tagged "scheduled" with the note "Site fit not verified".
- A result's label is read from the document verbatim (the established three-answers pattern). Some legacy fixtures carry the canonical label "Achieved zoning floor area" on the single building_option answer's value; that is document text the adapter reads, not adapter wording. The "no achieved/verified" test asserts only adapter-controlled fields (resultKind, note, status, constants), never pass-through document labels.
- These adapters are pure libraries; no component consumes them yet (no component changed this task, per the brief and ruling V2). The draft-value hiding gate stays the component's / three-answers' responsibility; presented-results does not re-implement it.
- metric-format also maps a non-finite number (NaN/Infinity) to the not-known state (a defensive extension of the null/undefined rule; it never shows "NaN"). displayQuantity, quantityText, conditionList and twoDp are reused from three-answers/first-building-options unchanged.

NO SERVER STARTED; ports 3000/3001/8000 untouched.

REPORT FILE: per my session's no-report-file override I did NOT create project-control/reports/M5-T148-part-B.md, and the commit contains only the 10 code files (matching its message). Please save THIS return verbatim as that report at the submit seam.

REQUESTED STATUS: awaiting_gate (G0 already PASS at the contract head; this increment is ready for G2 self-check / G3 / G4).
END-OF-REPORT

```

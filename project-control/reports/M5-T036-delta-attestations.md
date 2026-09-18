# M5-T036 delta-attestations at the corrected head 82143124 (VERBATIM returns)

Context: all five independent reviews returned PASS at 657b238d. Web CI at that head then
failed exactly two tests in the new panel suite (TestingLibraryElementError: "Found multiple
elements" for R3-2 / C1-4 — ambiguous single-match queries; production correct). The loop-2
producer's rework commit (worktree 1b6ac1c4, cherry-picked as 82143124) is test-only: six
getByText(value) queries became getAllByText(value).length >= 1 counted presence assertions
plus explanatory comments, and a dated producer-report addendum. Each reviewer was sent the
delta description and reviewed `git show 82143124` read-only; their attestations follow
verbatim (transport entity-decoding only).

## G1 — data-contract-verifier (rev-g1-m5t036)

YES — my G1 PASS carries unchanged to 82143124 (HEAD now 8214312480e80e2ce10abbbc423ff590afe4651b). Reviewed git show 82143124 read-only: test-only diff (six ambiguous getByText(value) -> getAllByText(value).length>=1 in zoning-context-panel.test.tsx, unique "Source for C1-4" single-match kept) plus a report addendum; NO production file changed, so all my F1-F6 findings (faithful consumption, real provenance path, honest absence, DB-005 links, print-exclusion, scope) are untouched — the fix actually corroborates F2 (designation values legitimately duplicate inside their provenance-disclosure original/normalized rows, which is what made getByText ambiguous in CI). O1 observation and the AS-6 web-CI evidence-capture note stand.

## G3 — code-reviewer (rev-g3-m5t036)

Delta-attestation, M5-T036 at 82143124 (HEAD verified == 8214312480e80e2ce10abbbc423ff590afe4651b): YES — my G3 PASS carries to 82143124 unchanged.

Basis (one sentence): git show 82143124 touches only zoning-context-panel.test.tsx and the producer report — zero production change, so C1/C2/C3/C5/C6 stand verbatim, and the AS-1 edit is exactly the fix my C4 predicted (each value also renders inside its provenance-disclosure original_value/normalized_value <dd> rows, so single-match getByText was ambiguous).

Non-tautological confirmation: the counted-presence form stays a real assertion — testing-library's getAllByText throws on zero matches, so getAllByText("R3-2").length >= 1 fails the test if the value does not render; it is a weaker "renders at least once" than a single-element match but that is precisely what AS-1 requires, both split-lot districts (R3-2 and C4-1) are still each independently asserted present, and the unique disclosure summary labels ("Source for C1-4", etc.) legitimately keep single-match getByText.

## G4 — qa-engineer (rev-g4-m5t036)

Delta-attestation, M5-T036 @ 82143124: YES — my G4 PASS carries; the counted-presence form preserves real assertion strength.

Reviewed `git show 82143124` read-only (test-only: 6 query forms in zoning-context-panel.test.tsx + report addendum; stat shows no production file and no other suite touched, so my 657b238d regression analysis carries unchanged).

Assertion-strength judgment: `getAllByText(value).length >= 1` throws on ZERO matches, and each designation (R3-2, C4-1, GI, INDIVIDUAL LANDMARK, Governors Island Historic District, C1-4) is asserted independently — so the split-lot "both districts, not just the first" guarantee and honest-presence are fully intact. The edit only drops an implicit uniqueness check that was itself wrong: the value legitimately also renders inside its provenance-disclosure original_value/normalized_value <dd> rows (that duplication is the root cause CI proved). getAllByText+count is the correct RTL idiom here, not a snapshot or tautology. The overlay test rightly keeps `getByText("Source for C1-4")` single-match, which still proves the D5 fallback join resolved. The companion AS-1 test ("Source for R3-2" etc., unique summary labels) and the chip being emitted in the same ZoningValueList iteration as its disclosure together still bind the chip's actual render.

Honesty note: this delta corrects a miss in my original PASS (I asserted single-match by counting only the chip node and missed the resolved-provenance value rows). No other getByText(value) in the suite is affected — the remaining getByText calls target unique strings (empty-text notes, "Source for X" labels, dt flag labels), consistent with CI reporting exactly two failures. CI green on 82143124 remains the AS-6 authority (orchestrator-captured, running).

## G5 — security-reviewer (rev-g5-m5t036)

**Attestation — G5 M5-T036 at 82143124: YES**, my G5 PASS carries to `82143124` unchanged. `git show --name-only` confirms the commit touches only `zoning-context-panel.test.tsx` (getByText → getAllByText assertion fix) and the producer report — no production, link, network, or rendering path changed, so every finding in my PASS at `657b238d` still holds.

## Human-journey — human-journey-reviewer (rev-hj-m5t036)

Delta-attestation, M5-T036 — YES, my journey PASS carries to 82143124 unchanged.

`git show 82143124` is test-only: six AS-1 `getByText(value)` → `getAllByText(value).length >= 1` presence assertions (R3-2, C4-1, GI, INDIVIDUAL LANDMARK, Governors Island Historic District, C1-4), correct because each value legitimately also renders inside its provenance-disclosure original/normalized `<dd>` rows (ProvenanceDisclosure.tsx:53-57) — the exact ambiguous-query failure CI proved at 657b238d, and the "Source for X" summary labels stay unique single-match. `git diff --name-only 657b238d 82143124` shows no production `.tsx`/`.ts` outside `__tests__` changed (only the test file, control-plane reports/ledger, and the backlog), so the three journey components (ZoningContextPanel, PropertyOverview, AddressConfirmCard) are byte-identical and every finding in my G3 report holds at 82143124.

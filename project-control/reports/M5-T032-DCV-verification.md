# M5-T032 DCV verification (verbatim reviewer return; directive-compliance-verifier, read-only, pinned c2437717)

Saved verbatim by the orchestrator (reviewer authorized: "Report body above may be saved verbatim").

---

# DCV REPORT — M5-T032 (D-064) — VERDICT: PASS

**Frozen head:** c2437717af33601d61ef467e39fe162e8b797361 (`git rev-parse HEAD` confirms).
**Requirements in scope:** D-064-R005, D-064-R007.
**Reviewer:** directive-compliance-verifier (read-only; producer ≠ verifier). No write/CLI/git-write/gh commands run.

## Ancestry / content-identity anchor (load-bearing)
- cbc10397, 71d4abb3, 2b440f41, a8ed75be are all ancestors of c2437717.
- `git diff --name-only 2b440f41 c2437717` = ONLY control-plane files (evidence-map, seam-evidence, state.json, M5-T032.json). `git diff --stat 2b440f41 c2437717 -- apps/web/` is **empty**. So every web source/test file is byte-identical between the CI-green head (2b440f41) and the frozen head. The orchestrator-captured CI evidence therefore applies to frozen-head content.

## D-064-R005 (ZoLa-first human-readable link) — **SATISFIED (PASS)**
Primary evidence, read directly at frozen head:
- `apps/web/src/lib/provenance-link.ts` L15 `ZOLA_LOT_PREFIX = "https://zola.planning.nyc.gov/bbl/"` (module constant); L53-56 `zolaLotUrl(bbl)` returns prefix+BBL only when `BBL_PATTERN /^[1-5][0-9]{9}$/` and length 10 match, else `null` (honest absence, no server-echoed URL); L80 `zolaUrl` gated by `currentRecordUrl !== null` — the SAME identity/conflict guard as the raw record.
- M5-T030 guards preserved unchanged: diff of cbc10397 shows `identityMatches`, `datasetConflict`, and `currentRecordUrl = identityMatches && !datasetConflict ? plutoRecordUrl(...) : null` logic is verbatim (only refactored into a const and reused). No guard weakened.
- All four UI surfaces render ZoLa **first/primary** and PLUTO JSON demoted to `className="section-note"` secondary, dataset link retained: `ProvenanceDisclosure.tsx` L42-47, `EvidenceInspector.tsx`, `EvidenceRecord.tsx`, `ReportSources.tsx` (verified in cbc10397 diff; `View this lot on ZoLa` + `data-testid="zola-lot-link"` rendered before the `section-note` PLUTO link).
- Deterministic tests present and correct: `provenance-link.test.ts` L148-188 (5-borough valid build; 19 hostile/malformed → null; output ALWAYS exactly prefix+BBL; same-guard-as-raw-record); `source-links.test.tsx` `expectLotLinks` asserts `getAllByRole("link")[0] === zola` (ZoLa first), PLUTO present as secondary, wrong-lot/conflict/non-PLUTO → both null; `sections.test.tsx` +84-line block asserts primary-not-`section-note`, raw-record `section-note`, DOM order zola<raw, conflict→honest absence; `provenance-disclosure.test.tsx` (71d4abb3) positional assertion updated PLUTO-first→ZoLa-first WITH added href assertion (contract update, PLUTO assertion retained — not weakened).
- AS-11 live smoke (orchestrator-captured seam evidence): ZoLa `…/bbl/3052960043` → HTTP 200, no redirect, matching the module constant.

## D-064-R007 (focused testing; full suite once at seam; no test weakened/deleted) — **SATISFIED (PASS)**
Primary evidence:
- Task packet `M5-T032.json` `documented_test_commands` = `["python tools/modularity_check.py --check", "python tools/validate_directive_compliance.py --check"]` — focused python checks ONLY, no web suite for the producer. `inputs` bind web tests to CI-at-seam (M5-T023 pattern); `risks[1]` states "Full suite + browser journeys run at the integration seam per D-064-R007; producer runs the focused commands only."
- One full regression at the seam: `M5-T032-orchestrator-seam-evidence.md` records CI green at 2b440f41 (18/18 jobs; web lint+typecheck+build; web-e2e vitest 971/971, Playwright 113/113) + a convergence record for three intermediate red clusters (A control-plane, B strict-TS casts, C behavior-contract consumers) — batched, not serial rerun-discovery.
- No test weakened or deleted (verified by diffs): provenance-disclosure test = contract update + added assertion; sections.test.tsx = purely additive; source-links.test.tsx = strengthened (added zolaUrl null-guards); e2e spec = expected-copy update to the new typed rate-limited message (still asserts a visible outcome + manual/BBL recovery). No deletions.

CI-execution component is verified as orchestrator-captured stored evidence (`.claude/rules/project-control.md` evidence-capture division of labor), not personally re-run — thin client, read-only, and the loop starves the full validator. The touched files are byte-identical to the CI-green head, so the result binds to frozen-head content.

## Evidence-map accuracy — **ACCURATE**
`M5-T032-evidence-map.json`: material_commit/commits, integration a8ed75be, ci_green_head 2b440f41 all verified as ancestors. R005 rows (constant-prefix zolaLotUrl, ProvenanceDisclosure primary/secondary, AS-10 tests in provenance-link.test.ts + sections.test.tsx, legacy consumer update in 71d4abb3, honest absence, AS-11 200) each reproduced. R007 rows (focused python-only producer run, full web suite once at seam 971/971 + 113/113, three convergence clusters) each reproduced against packet + seam record. No overstated or unbacked row. Note: the in-commit producer report's "UNVERIFIED / loose unattributed edits" framing is an earlier snapshot superseded by the seam evidence (attribution to loop worker claude-opus-4-8, S4.1 APPROVE_ONCE journal entries; committed as cbc10397) — my verdict rests on the committed source, not that snapshot.

## No prohibited action
Nothing merged/deployed/accepted/closed by this review. Task status `awaiting_gate`. Verdict is advisory; orchestrator records it.

## RESTAMP RULING — **GRANT (conditional)**
I pre-authorize carrying this PASS forward to a new head produced by control-plane-only commits (gate records, verification.json, state/task lifecycle — no change to any file this verification relied on), **conditional on:** `git diff --name-only c2437717 <restamp-target>` returns **only** paths under `project-control/**` (state.json, tasks/M5-T032.json, gates/**, directives/**/verification.json, reports/**) and **zero** `apps/web/**` path. If any `apps/web/**` source or test path I examined differs, this restamp authorization is void and R005/R007 must be re-verified at the new head.

# M5-T159 reviews (every return kept unchanged)

- G3 code-reviewer at f48b3d97: FAIL (F1 REQUIRED: the task's tests were red against M5-T157's fixture change; production code correct). Delta at 0330d598 after the builder's test-only fix: PASS.
- G4 qa-engineer at f48b3d97: FAIL (same cause); delta at 0330d598: PASS.
- Identity: production files unchanged since f48b3d97; the fix touched only the test file and the producer report (0330d598).

## G3 delta

<!-- saved unchanged by save_return.py from agent-a8922c079cfbfde75.jsonl, entry 2026-10-11T06:09:30.059Z, sha256 479230f1fc49f8e169fb57dcfea2d543f4af0fc967a577b17181b9e330b07523 -->
# G3 delta verdict — M5-T159 at `0330d598eaa3197d4867048b88f85a2bd2be2aae`

## VERDICT: PASS (F1 resolved)

My earlier REQUIRED finding F1 (test suite red at the reviewed head) is fixed. All earlier PASS checks (allowlist parity, no-synthesis, module design, scope) carry forward unchanged because the production files did not move.

### Checks performed at 0330d598 (fresh `git archive` export to /tmp, lanes venv)

1. **Production code unchanged.** `git diff f48b3d97..0330d598 -- law_links.py page_evidence.py sources.py` → empty. Only `test_report_law_links.py` (+155/−44) and the producer report changed. My prior checks 1–4 and 6 on the production code stand.

2. **Suite green at the reviewed head.**
   - `pytest tests/drawings/report/test_report_law_links.py` → **22 passed** (was 19 passed / 2 failed at f48b3d97).
   - `pytest tests/drawings/report` → **90 passed, 0 failed** (was 87 passed / 2 failed). Consistent with your 7062-passed/8-skipped full-folder run for this folder.

3. **s1/s6 are now count-independent and fixture-derived.** `_rendered_citations` reads the two figure blocks' non-withheld values via `readers`; expectations come from a local, independent oracle `_capture_section_url(page)` that scans the capture files directly (local `_PAGE_RE`, local `_last_segment`, direct `json`/`glob`) — it does **not** call `law_links` or `sources` to derive expected URLs. s1 asserts `Counter(hrefs) == Counter(expected_links)` and `_HOMEPAGE not in hrefs`; s6 asserts every rendered label is intact, `set(hrefs) == expected`, no homepage. Both now survive the T157 fixture change (23-52 / 23-52(b) / 11-25) that broke the old hard-coded counts.

4. **Explicit named-section test present and correct.** `test_s1_known_sections_link_or_print_plain_from_captures` asserts, with every URL read from the capture files (no typed URL), that 23-22, 23-52 (page), 23-52(b) (→ page 23-52) and 23-432 render as `<a href="{capture request_url}">…{visible}…</a>`, and that 11-25 (captured only on wrong host `zr.planning.nyc.gov`) prints `<span class="nowrap">11-25</span>` with no `</span></a>` — plain text, no guessed URL. I reproduced this behavior directly against the rendered HTML in the prior pass.

5. **Oracle independence / no typed URL confirmed.** `_capture_section_url` returns a capture's own `request_url` (official-host, no `?`, no `@`, last segment == page) or `None`; the only module-under-test calls remaining are in the targeted S2/S3/S5 unit tests, which is appropriate. The independent oracle being looser than `law_links`'s allowlist is a safe asymmetry: any divergence would make the asserted `<a …>` absent and fail the test; on the real captures they agree.

### Could not check (unchanged from prior report)
- Live URL reachability (no network; not required — captures are the authority).
- The exported-PDF link-destination harness of D-094-R027 (R060) — packet defers it to report v3 (P-3/P-7).
- The formal D-094-R027 / D-090-R584 directive stamp — that is the directive-compliance-verifier's pass; behaviorally the "exact section, never homepage" obligation is met and now has green evidence.

Advisory items F2 (the brief's "valid main capture supplies the section" holds only for 34-23, not 23-421/11-25 — still correct fail-closed behavior) and F3 (3-digit-lead sections unlinkable by both allowlists — parity-correct) stand as non-blocking notes.

No defects remain for G3.

END-OF-REPORT


## G3 round 1

<!-- saved unchanged by save_return.py from agent-a8922c079cfbfde75.jsonl, entry 2026-10-11T05:53:48.478Z, sha256 e55c19b2c39bbd34e6e37b3b0b85d6aaa5dbbe06f191c34bb3f84f5194919524 -->
# G3 (code-reviewer) gate report — M5-T159 "report law links go to the exact ZR section"

Reviewed identity: frozen head `f48b3d971f6964b119f905f2c5903ee7e587103f` (branch `task/wave23-density-zoning-lot`).
Note: during review the shared worktree `/root/project/w-wave20` HEAD advanced to `2bbfed943` (a sibling task). All evidence below was produced against an isolated read-only `git archive` export of `f48b3d97` under `/tmp/claude-0/t159`; no repo state was modified.

## VERDICT: FAIL

The three production files are correct and faithful; the defect is that the task's own test file does **not pass at the frozen reviewed head**. `tests/drawings/report` has 2 reproducible failures, both in the new `test_report_law_links.py`.

## Findings

### F1 — REQUIRED — `services/api/tests/drawings/report/test_report_law_links.py:108` and `:208`
At `f48b3d97`, `python -m pytest tests/drawings/report` → **2 failed, 87 passed**.
- `test_s1_every_href_is_the_exact_section_and_never_the_homepage` fails at line 108 `assert len(hrefs) == len(rendered)` (12 hrefs vs 13 rendered pages).
- `test_s6_only_link_targets_change_labels_and_text_stay` fails at line 208 `assert len(hrefs) == 10` (`AssertionError: assert 12 == 10`).

Root cause (reproduced, not inferred): sibling task **M5-T157** (commit `9e19afacb`, "special density area…") changed the shared benchmark fixture `packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` — which is **outside T159's allowed_paths** — so a present (non-withheld) `floor_area_allowance` value now cites `["ZR 23-52","ZR 23-52(b)","ZR 11-25"]` in addition to the four `ZR 23-22` rows. The T159 tests were written against the pre-T157 fixture (producer self-check "21 passed" was run at base `439e22b2`, before T157 landed on the branch), and hard-code 10 hrefs and the exact set `{23-22, 23-432}`. At the frozen head the page now renders 12 hrefs. `test_s1` additionally assumes every rendered section has a link (`len(hrefs)==len(rendered)`), which is false once an uncaptured section (11-25) is present, so the fix is a logic fix, not a count bump.

This is exactly the "known-red consumer of a changed shared fixture" case CODING_RULES warns about. Per the policy that the full suite must pass in CI at the exact accepted/merged head, a red `tests/drawings/report` at the reviewed identity blocks the gate.

Required correction (bounded, in-scope — the test file is a T159 allowed path): update `test_s1`/`test_s6` to match the fixture at head — 12 hrefs; `set(hrefs) == {zr-23-22, zr-23-52, zr-23-432 request_urls}`; 11-25 asserted as plain text (no anchor); and `test_s1`'s per-page assertion must allow rendered pages with no capture (11-25) to have no href. (Orchestrator may instead route the fixture-collision sweep.) The **production code needs no change.**

### F2 — ADVISORY — brief check (1) premise
The brief says the guard "drops captures with a wrong host or chapter-only URL and a valid main capture still supplies the section (verify on zr-23-421-g, zr-11-25, zr-34-23-contents)." Verified from the capture files:
- `zr-34-23-contents` (`request_url` `…/article-iii/chapter-4`, chapter-only) is correctly dropped; `zr-34-23` (`…/chapter-4/34-23`) supplies section 34-23. Matches the brief.
- `zr-23-421-g` (`request_url` `https://zr.planning.nyc.gov/entityprint/pdf/node/18075`) is dropped — but there is **no valid main capture for 23-421**: all three 23-421 captures (`zr-23-421`, `zr-23-421-g`, `zr-23-421-r1-r2`) use host `zr.planning.nyc.gov`, which fails the allowlist. Section 23-421 therefore fails closed to plain text.
- `zr-11-25` likewise has no valid alternate; 11-25 fails closed to plain text.
Behavior is correct (never a guessed/homepage URL — S3), but the brief's "a valid main capture still supplies the section" holds only for 34-23. None of these sections affect the rendered report except 11-25 (now in the fixture), which correctly renders as plain text. No code defect.

### F3 — ADVISORY — shared allowlist limitation (parity-correct)
The path regex (both Python and TS) accepts only a `\d{2}-\d{2,4}` section segment, so any ZR section with a 3-digit leading number is unlinkable. No such section is currently captured and the website allowlist has the identical limit, so this is parity-correct, not a T159 regression — flagged only for future capture work.

## Checks performed and results
1. **No URL synthesized (check 1):** PASS. `law_links._section_index` builds only from `snapshot.request_url`, validated by `official_zoning_text_url` AND `_last_path_segment(url)==page`; `section_url` returns only from that index; `page_evidence._law_links` prints plain text when `section_url` is `None`. Verified rendered output: 23-52 and 23-52(b) → `<a href=".../23-52">…</span></a>`; 11-25 → `…</span>` plain text (no anchor). zr-23-421-g, zr-23-421-r1-r2, zr-23-424-r1-r2, zr-11-25 dropped (wrong host); zr-34-23-contents dropped (segment `chapter-4` ≠ `34-23`).
2. **Python allowlist = `apps/web/src/lib/architect/source-links.ts` rule-for-rule (check 2):** PASS. Line-by-line match (string prefix, length≤500, forbidden-char class `[\u0000- \u007f\\]`, scheme/host/user/pass/port/query, path regex `^/article-[ivxlcdm]+/chapter-\d{1,2}(?:/\d{2}-\d{2,4})?$`, fragment `#\d{2}-\d{2,4}`, canonical rebuild). Empirical probes agree, incl. explicit `:443` → None (rejected at the prefix check in both), uppercase host/roman → None, trailing slash → None, `zr.planning.nyc.gov` → None.
3. **Only link targets change (check 3):** PASS behaviorally. 87 other report tests pass (incl. untouched `test_report_pages.py`); `test_s6`'s label assertions (the `<span class="nowrap">` wording) pass — only the href-count/set assertions fail. Diff to `page_evidence.py` changes only the href/plain-text branch; labels preserved.
4. **Module design (check 4):** PASS. `law_links.py` 117 lines, focused; immutable module state (`lru_cache(maxsize=1)` + `MappingProxyType`); no import-time I/O — the index is built lazily on first call via the existing `SnapshotStore` loader. `sources.py` grew by one small helper (`zr_section_page_number`). `ruff check` → All checks passed. `modularity_check.py --check` → exit 0, no T159 file flagged (only pre-existing warnings).
5. **Tests catch homepage/guessed URL (check 5):** The assertions are correctly designed to catch regressions (S1/S4/S6 assert `href != homepage`, `href == capture request_url`, allowlist round-trip), and the producer's documented mutation proof is plausible — **but this check cannot be marked satisfied because the suite is red at the reviewed head (F1).**
6. **No out-of-scope file changed by T159 (check 6):** PASS. The single T159 commit `f48b3d97` touches exactly the 5 allowed paths (law_links.py, page_evidence.py, sources.py, test_report_law_links.py, producer report). `readers.py` and `test_report_pages.py` untouched by it. (The broader `439e22b2..f48b3d97` range includes M5-T157/T158/T160 files, which belong to those tasks, not T159.)

## What I could not check / out of scope
- Live reachability/currency of the recorded URLs (no network; not required — resolution is from committed captures).
- The exported-PDF link-destination check named in D-094-R027 `required_harness`/`required_evidence` (R060) — the packet explicitly defers it to report v3 (P-3/P-7); this task covers HTML law links only.
- The formal directive stamp for D-094-R027 / D-090-R584 — that is the `directive-compliance-verifier`'s pass; behaviorally the "exact section, never homepage" obligation is met by the code, but its evidence (the tests) is red.

## Reproduction
```
git -C /root/project/w-wave20 archive f48b3d97 | tar -x -C /tmp/t159
cd /tmp/t159/services/api
PYTHONPATH=/tmp/t159/services/api /root/project/lanes-runtime/venv/bin/python -m pytest -q -p no:cacheprovider tests/drawings/report/test_report_law_links.py
# => 2 failed, 19 passed  (test_s1_every_href..., test_s6_only_link_targets...)
```
Fixture provenance: `git -C /root/project/w-wave20 log --oneline 439e22b2..f48b3d97 -- packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json` → `9e19afacb M5-T157`.

END-OF-REPORT


## G4 delta (verdict B)

<!-- saved unchanged by save_return.py from agent-a458e08ba9c79cc79.jsonl, entry 2026-10-11T06:14:06.776Z, sha256 a79274f31ac0d436d6064083f7189891f6bb0ff4d202562a3f914fd28a691cd5 -->
G4 DELTA RE-VERIFICATION — M5-T157 and M5-T159 at new head 0330d598eaa3197d4867048b88f85a2bd2be2aae (branch task/wave23-density-zoning-lot). Fresh detached worktree at 0330d598, read-only, mutations restored, worktree removed. D-093 observed.

===== DELTA VERDICT A (M5-T157): PASS =====
===== DELTA VERDICT B (M5-T159): PASS =====
My prior Finding 1 (the sole blocker; FAIL cause for B, required correction for A) is CLEARED at 0330d598. Findings 2 and 3 were ADVISORY and remain non-blocking.

WHAT CHANGED SINCE f48b3d97 (verified against T157/T159 allowed paths):
1. NB-05 (docs/research/evidence-records/NB-05-special-density-area.json): `git diff f48b3d97..0330d598` shows ONLY a new entry appended to review.agent_reviews (data-contract-verifier, reviewed_revision 2, verdict "agrees"). `revision` stays 2; evidence/meaning/measurement/implementation/conclusion all byte-unchanged. No T157 logic touched. The new G1 entry independently reproduces the law (4 digests, 20,150/680=29, boundaries 29.75→30 / 29.7485→29 / 10,710/680=16) and did a live Socrata probe confirming spdist1='DB' for Downtown Brooklyn CD 302 lots — corroborating the "DB" token empirically. It carries two of its own ADVISORIES (the SDB snapshot not yet cited as an evidence[] item; OQ-5 Appendix A kept open) — these are the verifier's, not G4 blockers.
2. test_report_law_links.py: production unchanged; the test file was rewritten to be fixture-derived. The new s1/s6 compute expectations from the rendered fixture citations plus an INDEPENDENT capture-file oracle (`_capture_section_url` scans the snapshot files directly, not through law_links/sources under test), with no hard-coded counts or URL strings; a new `test_s1_known_sections_link_or_print_plain_from_captures` explicitly pins 23-22/23-52/23-52(b)/23-432 as links and 11-25 (wrong-host capture only) as plain text. Other inter-head commits are M5-T160 (NB-06) + control records, outside both tasks' paths.

COMMANDS RUN (frozen head 0330d598, lanes venv):
- pytest tests/drawings tests/rules → 2144 passed, 6 skipped (was 2 failed / 2141 passed at f48b3d97 — the 2 red tests now pass, +1 new test).
- pytest tests/scenario/three_answers tests/journey tests/api → 1717 passed, 2 skipped. (Consistent with the orchestrator's 7062 passed, 8 skipped across all affected folders.)
- My own quick mutation (brief request): forced page_evidence._law_links to emit the homepage for every captured section (`url = "https://…nyc.gov/"`). → all three guards FAILED — test_s1_every_rendered_section_links_to_its_capture_or_prints_plain, test_s1_known_sections_link_or_print_plain_from_captures, and test_s6_only_link_targets_change_labels_and_text_stay (each asserts the exact `<a href="{capture_url}">` form and `_HOMEPAGE not in hrefs`). Restored byte-for-byte; worktree left clean then removed.

CONFIRMATIONS REQUESTED:
- New s1/s6 are fixture-derived: YES — expectations come from the fixture's rendered citations + the capture files via an oracle independent of the module under test; no typed URL/count. They would (and do) fail on a homepage or guessed URL, proven by my mutation.
- NB-05 change is only the review entry: YES — review.agent_reviews gained one data-contract-verifier entry; nothing else in T157's paths changed; revision stays 2.

CARRY-FORWARD (unchanged, non-blocking): my original A verification stands — fold correct vs ZR 12-10, values 29/16/30/29 vs ZR 23-52, invariant/record-wins/nine-combination coverage proven real, register + research_record checks PASS, 5 web files 71 passed, ruff + modularity clean. B's allowlist is a faithful port of source-links.ts (Finding 2 advisory: no automated parity test — still just advisory).

Both tasks now meet their acceptance at the integrated head; the wave's law-links regression is resolved with a test-only change and no production edit.

END-OF-REPORT


## G4 round 1 (verdict B)

<!-- saved unchanged by save_return.py from agent-a458e08ba9c79cc79.jsonl, entry 2026-10-11T05:58:21.541Z, sha256 cee2b5983a978adbe87cab21cde011ec5b9c6711ed5fc036fcabdb55105fa075 -->
G4 (qa-engineer) INDEPENDENT GATE — M5-T157 and M5-T159. Frozen head f48b3d971f6964b119f905f2c5903ee7e587103f on task/wave23-density-zoning-lot. Reviewed read-only in a detached worktree (/tmp/rv-qa-w23, created at f48b3d97, removed at end; left clean, HEAD unchanged). Venv /root/project/lanes-runtime/venv. No ports touched.

================ VERDICT A (M5-T157): PASS WITH REQUIRED CORRECTIONS ================
VERDICT B (M5-T159): FAIL
Both failures share ONE root cause (finding 1 below) with ONE fix, owned by T159's test file.

===== WHAT I VERIFIED INDEPENDENTLY (law first, then tests) =====
LAW (opened the primary captures, not the brief/reports):
- zr-12-10-special-density-areas (digest e8029ab3…f401b6): special density areas = (a) Manhattan Core; (b) Special Downtown Brooklyn District.
- zr-12-10-manhattan-core (2c04132a…c59c56): Manhattan Community Districts 1–8.
- zr-12-10-special-downtown-brooklyn-district (ae66c93e…d7dd2d): designated by the letters "DB".
- zr-23-52 (f48f1ddc…b908ac): (b) factor 680; "Fractions equal to or greater than three-quarters … considered to be one dwelling unit"; (a)(1) no factor in special density areas.
All three digests hard-coded in special_density_geography.py EQUAL the committed snapshots. Engine copies exist under services/api/app/_zr_snapshots/v1/.

ARITHMETIC (worked myself from ZR 23-52 before reading tests):
- 20,150/680 = 29.63 → 29 (0.63 < 0.75). ✓ matches fixture row "20,150 ÷ 680 = 29.63", value 29.0.
- 10,710/680 = 15.75 → 16 (0.75 ≥ 0.75, boundary up). ✓
- 20,230/680 = 29.75 → 30 (exact .75, up). ✓   20,228/680 = 29.747 → 29 (< .75). ✓
- 20,400/680 = 30 exactly; 20,229/680 = 29.7485 → 29. ✓ (NB-05 worked_example consistent.)

FOLD LOGIC (special_density_geography.decide_special_density) — read line by line, correct:
either IN signal alone suffices (DB token OR Manhattan-Core cd 101–108); NOT IN requires BOTH the Manhattan-Core question answered no AND every special-district column read with none "DB"; everything else (cd None/unrecognised/joint-interest-area e.g. 164, Manhattan-Core cd contradicted by non-Manhattan borocode e.g. 105+borocode 3, or special-district columns not fully read) is NOT KNOWN; "not read" is never "no". Matches S1/S2/S3 exactly.

===== COMMANDS RUN (frozen head) =====
T157:
1. pytest tests/scenario/three_answers → 475 passed, 2 skipped.
2. pytest tests/scenario/three_answers tests/api tests/journey tests/rules tests/drawings tests/cad → **2 failed, 4473 passed, 8 skipped** (286s). The ONLY 2 failures: tests/drawings/report/test_report_law_links.py::test_s1 and ::test_s6 (T159's file). tests/journey (benchmark legal unit limit = 29 Conditional), tests/api law-examples, tests/rules, tests/cad all green.
3. render_review_register.py --check → "register check PASSED (no issues)".
4. research_record_check.py --check → PASS; NB-05 revision=2, status=answered_from_primary_source, code_current=True, review_state=stale (expected — awaits the fresh G1 review of rev 2; disclosed in-record).
5. apps/web: npm@11.18.0 ci (exit 0) then npx vitest run on the 5 changed web files (journey-215-16-northern, results-contract-checks, presented-notices, presented-results, three-answers) → **5 files / 71 tests passed**.
6. My own mutation (brief A#3): in the fold, forced the final "columns not fully read" branch to return NOT_IN (`if True`). → test_special_district_columns_not_read_is_not_known FAILED (got NOT_IN, expected NOT_KNOWN). Restored byte-for-byte (worktree clean).
7. ruff check . → All checks passed!  modularity_check --check → exit 0, failures 0 (new modules special_density_geography.py 238L and law_links.py 117L not flagged; result_ways.py is a pre-existing warn).

T159:
1. pytest tests/drawings/report/test_report_law_links.py → 2 failed, 19 passed.
2. pytest tests/drawings tests/rules (brief B#3) → **2 failed, 2141 passed, 6 skipped** (153s). Same 2 failures (test_s1, test_s6).
3. Independent benchmark href build through the REAL builder (build_report_html on packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json): evidence page has **12 hrefs** — 4× 23-22, 2× 23-52, 6× 23-432. EVERY href equals a capture's source.request_url (zr-23-22, zr-23-52, zr-23-432); NO homepage href. ZR 11-25 is cited but has no allowlist-valid capture, so it correctly prints as plain text (live proof of S3 at the benchmark).
4. allowlist port: compared law_links.official_zoning_text_url line-by-line against apps/web/src/lib/architect/source-links.ts — faithful (same prefix, length cap, forbidden-char class \u0000- /\u007f/\\, scheme/host/user/pass/port/query checks, path regex /^/article-[ivxlcdm]+/chapter-\d{1,2}(?:/\d{2}-\d{2,4})?$/, fragment \d{2}-\d{2,4}; '#' handled separately because urlsplit drops it). section_url drops the sub-paragraph for lookup, keeps it in the label; fail-closed to None/plain text; drops wrong-host (entityprint) and chapter-only captures.
5. My own mutation (brief B#3): removed the query rejection in official_zoning_text_url. → test_s4_allowlist_rejects_disallowed_urls[…?x=1] FAILED. Restored byte-for-byte.

===== FINDINGS =====
FINDING 1 — REQUIRED (the FAIL for B; the required correction for A). Cross-task interaction: T157's benchmark-fixture change breaks T159's law-links tests at the frozen head.
Files: services/api/tests/drawings/report/test_report_law_links.py:75 (test_s1) and :208 (test_s6).
Evidence: test_s1 `assert len(hrefs) == len(rendered)` → 12 == 13; test_s6 `assert len(hrefs) == 10` → 12 == 10. Cause: T157 added citations ZR 23-52, ZR 23-52(b), ZR 11-25 to the floor_area_allowance block (the conditional legal unit limit, 20,150÷680=29). So the evidence page now renders 13 cited sections across floor_area_allowance+permitted_envelope and 12 law hrefs (11-25 has no capture → plain text), vs the pre-T157 fixture's 10 hrefs / set {23-22,23-432} the tests were written against. T159 and T157 ran in parallel on different files, so T159's builder (base 439e22b2) could not see T157's fixture change.
IMPORTANT: the link BEHAVIOUR is CORRECT — I independently confirmed all 12 hrefs are exact section URLs equal to the captures' request_url, none is the homepage, and 11-25 (no capture) correctly prints as plain text. This is a STALE-TEST defect, not a code defect; no production change is needed.
Required fix (in T159's scope — test_report_law_links.py): (a) test_s6 → expect 12 hrefs and set {zr-23-22, zr-23-52, zr-23-432}; (b) test_s1 → its invariant `len(hrefs)==len(rendered)` is now false because a rendered section (11-25) has no capture and prints plain text; rework it to count only rendered sections that resolve to a URL, and add an explicit assertion that 11-25 is plain text (this is a genuine new S3 case on the benchmark). Because both T157 and T159 land in one wave ("never merged alone"), this fix must land before the wave merges; it clears both A's and B's red suite. If T159 cannot be reopened, route test_report_law_links.py via a scope correction as was done for test_result_way_engine_bridge.py.

FINDING 2 — ADVISORY (B). No automated test asserts that law_links.py's allowlist stays in parity with source-links.ts; I verified parity by hand this round. Consider a parity/golden test so a future edit to either side cannot drift silently. Not a blocker.

FINDING 3 — ADVISORY (A, context only). NB-05 revision 2 is code_current=True but review_state=stale: its agent_reviews still carry revision-1 code identities. The record discloses it awaits a fresh independent review of rev 2; T157's G1 (data-contract-verifier) covers that. Not a G4 blocker.

===== WHY THESE VERDICTS =====
A (M5-T157) — PASS WITH REQUIRED CORRECTIONS: every acceptance scenario S1–S7 is independently verified (fold against ZR 12-10, values against ZR 23-52, invariant/record-wins/nine-combination coverage present and proven real by my mutation, journey=29 Conditional, register+NB-05 checks pass, 5 web files pass, ruff+modularity clean, changed expectations explained and strengthened not weakened). The only frozen-head failures are in a sibling task's test file, caused by T157's CORRECT fixture change; the required correction is finding 1 (owned by T159) and must land before the wave merges.
B (M5-T159) — FAIL: the link-resolution code is correct and well-tested, but 2 tests in the task's own deliverable (test_report_law_links.py) are red at the frozen head; the packet's named suite (tests/drawings) does not pass. Fix = finding 1.

===== WHAT I COULD NOT CHECK =====
- Live reachability/currency of the recorded ZR URLs (no network to the ZR portal; by design the captures are the authority — I verified href == capture request_url).
- Exact PLUTO "DB" token spelling (PLUTO Appendix A not captured; OQ-5) — a known open item flagged for G1, matched here to the ZR 12-10 map-designation letters only; carried as a condition, never a zoning rule.
- Full web vitest suite (only the 5 changed files per brief; producer reported 128 files green at T157's base; no other web file changed in the wave).
- Professional/legal verification — out of scope per ADR-007; the 29/16 figures remain Conditional ceilings, never confirmed entitlements.

END-OF-REPORT

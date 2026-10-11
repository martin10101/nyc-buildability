# M5-T161 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `5cf8acdcaeb59913d236f4c2d3a9d2b00f174e2a` (branch `task/wave23-density-zoning-lot`, review copy `git plumbing at the frozen head`). Directives D-090, D-093, D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R255, R520, R584, R639, R051, R034, R035.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. G3 and G4 each recorded only non-blocking advisories (aggregate diff spans ledger + a disjoint peer report; a cross-reference comment to the vitest leg; the zoning-lot wording is an engine-text contract to update in lockstep if reworded). No action required for acceptance.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 09:22 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T161 (directives D-090, D-093 and D-094, 7 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, read-only verification, not a human or professional engineering/legal review. I produced none of this work. I worked from primary evidence (git objects at the frozen head, product source, the reference case, the NB-05 record and its cited ZR/MapPLUTO snapshots, CI run JSON, and the two allowed validators); every report/map/gate/brief was treated as an unverified claim.

(1) HEAD VERIFIED
 - git rev-parse HEAD in /root/project/w-wave20 = 5cf8acdcaeb59913d236f4c2d3a9d2b00f174e2a on branch task/wave23-density-zoning-lot; I read all registry/product/control files through `git show 5cf8acdc:<path>`. Worktree clean (git status --porcelain empty). The validator exited 0 (no transient c14).

(2) ROWS

ROW D-090-R255 — PASS
 - Owner text traced to source-035-amendment.md:16 ("Facts and legal eligibility must come from evidence. A user assumption can support a clearly labeled conditional scenario, but must not become a verified fact.").
 - This task's share: the browser journey asserts the city's RECORD decides the special density area and that the user's agreeing statement changes nothing (same Conditional 29), and that no line names the statement — spec line 244 `expect(dialog).not.toContainText("as the user states")`.
 - I confirmed in product source result_way_bridge.py `_density` that a usable NOT_IN record yields EVIDENCE_NOT_IN_ONE, and result_ways.py puts "as the user states" ONLY in the USER_STATEMENT_NOT_IN_ONE (no-record) branch, so it is never shown here; the limit is marked Conditional, never a verified fact.
 - Nothing stays open for this task's share (the deciding behaviour is M5-T157's accepted work; this is a test assertion over it).

ROW D-090-R520 — PASS
 - Owner text traced to source-055-amendment.md ("29 for standard residences", "35 for qualifying affordable housing", "These remain conditional ceilings").
 - Spec reads UNIT_LIMIT_STANDARD = Number(rowValue("L6")) from docs/reference-cases/R6B/cases/real-lot.json; I confirmed row L6 expected.value = 29 (dwelling units) — asserted as `${UNIT_LIMIT_STANDARD} units`, never hard-coded.
 - The standard limit is asserted with answer-conditional-marker "Conditional" (a conditional ceiling, never settled); the qualifying-affordable/senior rows are Withheld in this journey and are not this spec's subject.
 - Open: the 35/affordable and no-senior-factor figures are not exercised in THIS browser spec (withheld this milestone); for this task's share the standard conditional-29 retention is satisfied, nothing further owed here.

ROW D-090-R584 — PASS
 - Owner text traced to source-060-amendment.md ("Keep the existing activation restrictions."); classification hold.
 - Material commit f2f76654 touches exactly two files (apps/web/e2e/results.flag-on.spec.ts, project-control/reports/M5-T161-producer-report.md); no flag, render.yaml, product or config file changed, so production switch defaults are unchanged.
 - The "flag-on" spec name is a Playwright test-project route (testMatch), not a production switch; no hidden feature is turned on by this test-only change.
 - Nothing stays open.

ROW D-090-R639 — PASS (with a carry-forward obligation at the accept head)
 - Owner text traced to source-064-amendment.md ("All required full-suite and security checks must pass in CI for the exact code being accepted or merged…").
 - The repair is real: CI web-e2e was failure at claim head 8cc9a3a0 (run 38126000985) and b54b6194 (38125073082) with the stale spec blob 2541dc9e; at reviewed head 5e3e8e68 run 38126925965 = 21/21 jobs success, incl. web-e2e, web (lint+typecheck+build), api and security jobs.
 - The fixed spec blob d5ba312c is byte-identical at f2f76654 (material), 5e3e8e68 (reviewed), eb110032 (submit) and 5cf8acdc (frozen), so the green CI at 5e3e8e68 covers exactly the frozen-head spec identity.
 - Open: the frozen-head CI run 38127632651 is still in_progress; acceptance MUST read a green full-suite + security CI run at the actual live accept head before this task is accepted (see carry-forward (4)).

ROW D-093-R051 — PASS
 - Owner text traced to source-001.md:135 ("For changed logic, test meaningful boundaries… Avoid tests that merely copy the implementation's formula. A synthetic fixture must never be relabeled as a professionally verified real-site result.").
 - The changed assertions test the deciding boundary (record NOT_IN + an agreeing statement) using the independently-worked reference value L6=29, not a program run or the implementation formula; the old check read innerText of a folded row and passed vacuously, the new checks open the disclosure and assert toBeVisible() first.
 - Non-vacuity is proven two ways: G4's mutations (A: `.not.toContainText("29 units")` fails @183; B: "tax lot" fails @185) and the producer's mutations (A @184, B @246) both fail on the pre-M5-T157 / reworded expectation; the 29 is asserted only as Conditional, never a verified real-site result. I confirmed NB-05 is answered_from_primary_source and research_record_check.py --check = PASS (exit 0).
 - Nothing stays open.

ROW D-094-R034 — PASS
 - Owner text traced to source-001.md:119-121 ("Current ZR 12-10 defines these areas as Manhattan Core and Special Downtown Brooklyn. This Queens property is outside those geographies. Resolve that source fact through the normal rule/evidence process. If the application cannot yet use it, record the implementation limitation separately.").
 - NB-05 (revision 3) resolves the fact through the evidence process: E1/E2 ZR 12-10 snapshots (special density areas = Manhattan Core [CD 1-8] + Special Downtown Brooklyn) with sha256 + saved copies that exist at the frozen head, and MapPLUTO lot 70 Borough QN / SPDist1 null → NOT in a special density area; the browser journey shows this as a Conditional 29 at the first press, independent of any user declaration.
 - The implementation limitation (the e2e harness carries no ACRIS zoning-lot index → generic zoning-lot condition) is recorded separately in the evidence map known_limits and producer report §1/§7.
 - Nothing stays open for this task's share.

ROW D-094-R035 — PASS
 - Owner text traced to source-001.md:121 ("This does not by itself establish the property's legal unit limit… Do not promote the earlier conditional arithmetic example of 29 units to a confirmed site entitlement."); classification prohibition.
 - The spec asserts 29 ONLY as a Conditional ceiling (answer-conditional-marker "Conditional") carrying "If this tax lot is the whole zoning lot", never settled; existing guards kept — options.innerText not.toMatch(/feasible|complies|legally correct/i) (line 168) and dialog.innerText not.toContain("maximum for this property").
 - I confirmed in result_ways.py that the standard way returns Conditional with an always-present, never-removed zoning-lot condition (plus area/K20), so the 29 cannot render as a confirmed entitlement.
 - Nothing stays open (the zoning-lot/area/K20 inputs stay unresolved and are preserved as conditions).

(3) BINDING B1–B5
 - B1 PASS: contract commit b6af242a appended only "M5-T161" to applicability.task_ids for all 7 rows (D-090 ×4, D-093 ×1, D-094 ×2); the only other +/- lines were the manifest/requirements updated_at bump — no requirement text changed.
 - B2 PASS: at the frozen head sha256_text_artifact(requirements.json) equals each manifest.requirements_content_digest_sha256 (D-090 e5ca6383, D-093 8d694d27, D-094 f772d7ab) and the id-digest matches each manifest.requirements_id_digest_sha256; no locked id missing.
 - B3 PASS: each verification.json carries exactly one M5-T161 task_verifications row with producer frontend-engineer, verifier "" (empty), schema directive_verification/v2, every requirement state "pending", evidence [] — ids D-090[R255,R520,R584,R639], D-093[R051], D-094[R034,R035].
 - B4 PASS: reg.evaluate_task_refs(M5-T161) → ok=True, applicable_ids == cited_ids == the 7 rows, missing_ids [], invalid_refs [], unresolved [].
 - B5 PASS: missing_ids empty means nothing else across the active directives applies to this task uncited. Gate records: G0 PASS (contract head b6af242a), G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer) — G2/G3/G4 all at reviewed_sha eb110032 with one identical content_manifest_sha256 11ababc1f0a636401b3ffbb2d96408dfc2cef6a85c087198375478907f6bd735.

(4) CARRY-FORWARD CONDITION
 - This verdict may be stamped at a later head WITHOUT a new review iff the blob-level predicate holds: apps/web/e2e/results.flag-on.spec.ts keeps blob d5ba312ccffa94e89d3b0dc343f9fd2826a642c0 and project-control/reports/M5-T161-producer-report.md keeps blob c4250ff798ec39b9551cf28f595de4dea5cb9eb6, and the 7 rows' text plus their M5-T161 binding are unchanged (digests in B2 unchanged).
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file — other tasks' source under services/, apps/, packages/, docs/, their packets/gates/reports/directive bindings, ledger state — plus this task's own acceptance records and a merge of the main line that changes none of the predicate's files.
 - For R639 specifically: at the stamping/accept head the orchestrator MUST read a CI run on that exact head (or on a head byte-identical in the web/api/security/control-plane inputs) whose required full-suite and security jobs are all success — i.e. the green web-e2e/web/api/security identity proven at 5e3e8e68 must be confirmed live green at the accept head (the frozen-head run 38127632651 was still in_progress at my read).

(5) REQUIRED CORRECTIONS
 - None. G3 and G4 each recorded only non-blocking advisories (aggregate diff spans ledger + a disjoint peer report; a cross-reference comment to the vitest leg; the zoning-lot wording is an engine-text contract to update in lockstep if reworded). No action required for acceptance.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run the browser e2e myself (read-only; ports 3000/3001/8000 held; running browser tests forbidden). I relied on CI run 38126925965 (21/21 success incl. web-e2e) at reviewed head 5e3e8e68 plus the proven spec blob identity to the frozen head, the product-source trace, and the two reviewers' mutation outputs.
 - I did not run the full api suite or tools/test_directive_compliance.py (forbidden). CI is the authoritative full-suite proof. I did run validate_directive_compliance.py --check (exit 0) and research_record_check.py --check (exit 0, PASS).
 - I did not fetch live ZR 12-10 or MapPLUTO; I read the committed NB-05 record, its excerpts, and confirmed the two ZR-12-10 snapshot files exist at the frozen head — not the live web sources.
 - The frozen-head CI run (38127632651) was in_progress at read time; I confirmed green only at the byte-identical reviewed head 5e3e8e68, so the accept-head-green condition for R639 remains for the orchestrator to confirm.
 - I did not independently recompute the ACRIS zoning-lot composition; it is correctly carried as an always-present unresolved condition.

END-OF-REPORT
```

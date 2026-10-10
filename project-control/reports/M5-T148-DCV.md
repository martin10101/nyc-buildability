# M5-T148 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `db7824e70e0ca0fbd6e5fb4b61a57621a899fb8c` (branch `task/wave20-presentation-slice`, review copy `/root/project/rv-w6-a`). Directive D-090. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R641, R804, R807, R810, R811, R812, R833, R835, R836, R837, R838, R855, R856, R857, R858, R859, R871, R872, R873, R877, R886, R888, R890, R895.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. One non-blocking observation: the evidence map's R877 line "focus-ring tokens exist" is not backed by a distinct focus token in presentation-tokens.json (the source has no focus/reduced-motion token); focus visibility and reduced motion are correctly deferred to M5-T149, so this does not affect R877's this-task contrast share. No change required.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived one return, received whole, received 2026-10-10 04:51 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T148 (directive D-090, 24 rows)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an independent, read-only, machine verification, NOT a human or professional review. I produced none of the code or records; I re-derived each item from primary evidence (source files, the generator, the tests and what they assert, the registry tools, the gate records and git objects). The producer's reports and evidence map were treated as claims to reproduce.

(1) HEAD VERIFIED
 - Frozen head db7824e70e0ca0fbd6e5fb4b61a57621a899fb8c on branch task/wave20-presentation-slice, base main 0bb6acb293278d125e31c76da18e4ffe6e4b9ac1. The read-only guard blocked `git checkout` of my copy /root/project/rv-w6-a, so I inspected the frozen head through the existing worktree /root/project/w-wave20 (at db7824, `git status` clean) and `git show db7824e70e0c:<path>`.
 - Wave branch; M5-T148 is my scope only. `git diff --name-only d745b635..db7824` = 26 files, all under project-control/; the 18 M5-T148 material files are byte-identical from the reviewed code head d745b635 to the frozen head (empty `git diff` on those paths), so the G3/G4 reviews at d745b635 apply at db7824.
 - Permitted checks run at the frozen head: node --test presentation-tokens.test.mjs 10/10 (exit 0); node presentation-tokens.mjs --check exit 0; pytest tests/drawings/test_presentation_tokens.py 6/6 (exit 0); tools/validate_directive_compliance.py --check DIRECT_EXIT=0.

(2) ROWS (each judged on THIS task's share; the row stays open in the registry for the rest)

ROW D-090-R641 — PASS
 - result-status.ts maps the document value_state to the owner's three screen words only: settled (no marker), conditional → "Conditional", withheld → "Not known" with the document reason and no digit; the switch is exhaustive with no "verified" branch.
 - __tests__/result-status.test.ts walks every committed fixture and asserts JSON.stringify(status) never contains "Verified"; the node and python token tests assert no "verified" key in status tokens. All passed.
 - Open: applying these words on the screen is M5-T149, and the PDF's six labels (owner question C2) are not mapped onto the screen in this wave — the row stays bound to M5-T149 too.

ROW D-090-R804 — PASS
 - Only presentation files change: `git diff --name-only 0bb6acb2..db7824` contains no apps/web/package.json, package-lock, requirements.txt, .github/, deploy, services/api/app/rules/rulesets/*, migration or styles.py; the five adapters are pure (format/group only).
 - The task is awaiting_gate, not in state.json accepted_tasks; no production switch flipped, nothing merged/accepted/deployed/installed/purchased/closed.
 - Open: this is a standing preservation prohibition across all tasks; nothing specific remains for M5-T148.

ROW D-090-R807 — PASS
 - globals.css is purely additive: `git diff 0bb6acb2..db7824 -- globals.css` has 0 deletion lines; every pre-existing token is preserved and only the marked generated block is added — "preserve fixes already made" is satisfied in code.
 - Part A read layout.tsx and styles.py read-only; the adapters add no route wiring, so no active route/export path was rewritten.
 - Open: the pre-edit reconciliation narrative (branch/task/directive/route recheck, "never infer from a stale handoff") is an orchestrator process claim partly outside code evidence; the code-level portions reproduced clean.

ROW D-090-R810 — PASS
 - presented-results.ts gives each result in the contract's reading order: label, then display (a formatted value OR the not-known state), one material `exception`, and a `detailsKey` — concise fields, the long detail pushed to the evidence surface, not into the row.
 - metric-format.ts produces concise one-line values ("20,150 sq ft"); FormattedMetric separates number/unit/text.
 - Open: rendering concise metric rows and the separate open-items table on the screen/PDF is M5-T149 and the PDF step; this task supplies the data shape only.

ROW D-090-R811 — PASS
 - presented-notices.ts collectConditions dedupes each distinct "If …" line by exact text in first-appearance order (C1, C2, …) and records per-result references by id, so shared context is stated once and none is lost.
 - __tests__/presented-notices.test.ts proves on the benchmark that the shared set equals an independently computed distinct-condition set, ids resolve, and multiplicities (2 and 1) are preserved; capNotices partitions visible/hidden with no drop.
 - Open: "retain a local exception only where it changes that result" on the screen lives in three-answers.ts (M5-T149, forbidden to this task); this task supplies the shared-once grouping adapter.

ROW D-090-R812 — PASS
 - presented-results.ts tags results allowance | envelope | scheduled | estimate; there is deliberately no "achieved" member; a listed building is "scheduled" carrying note SITE_FIT_NOT_VERIFIED = "Site fit not verified".
 - __tests__/presented-results.test.ts asserts floor-area/unit-limits=allowance, heights/coverage=envelope, building B=scheduled with the note and never "achieved", capacity=estimate.
 - Open: the on-screen visual treatment that keeps a floor schedule from looking like proof is M5-T149/PDF; this task tells the kinds apart in the model.

ROW D-090-R833 — PASS
 - result-status.ts follows the R641 screen mapping; a withheld value becomes "Not known" (never relabelled "Conditional" to be shown) and carries a short reason, never a digit; there is no code path to "Verified", so it is never a synonym for merged/arithmetic/source-link.
 - presentation-tokens.json marks status colour color_role:"secondary" (colour secondary), markers on conditional/not-known only.
 - Open: the PDF six-label mapping (owner C2) is the owner's open decision and not applied to the screen here.

ROW D-090-R835 — PASS
 - presentation-tokens.json font.family = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif", byte-equal to apps/web/src/app/layout.tsx fontFamily (ruling V4); the node S2 and python font tests read layout.tsx and assert equality.
 - metric-format.ts yields "20,150 sq ft" and keeps full precision (metric-format.test.ts asserts the input value is unchanged across repeated formats); presented-results tags the capacity as an "estimate".
 - Open: tabular-numeral right alignment is applied in screen/PDF CSS (M5-T149+), and PDF font embedding is the PDF step; this task provides the single family token and the formatting adapter.

ROW D-090-R836 — PASS
 - presentation-tokens.json carries spacing 4,8,12,16,24,32,48 px, control.height 44, control.radius 6, radius.panel 8; python test_contract_section_5_values and node S2 assert these exact values and generate the CSS/Python from the one source.
 - The generated globals.css block emits --pt-space-4..48, --pt-control-height:44px, --pt-control-radius:6px, --pt-radius-panel:8px.
 - Open: the ~1,360 px shell, dividers-not-boxes, 55–80 char lines and "no fixed-height cards/overflow:hidden" are layout behaviours applied on the screen/PDF (M5-T149+); this task fixes the token values.

ROW D-090-R837 — PASS
 - presentation-tokens.json declares 15 contrast pairs; presentation-tokens.test.mjs computes WCAG 2.2 relative-luminance ratios and asserts text ≥ 4.5:1 and control edges ≥ 3:1. Reproduced ratios: text 5.76–14.53:1, control edges 7.14 and 7.83:1; the quiet divider pairs (1.22, 1.34) are marked controlEdge:false and asserted never a control edge.
 - The nine palette colours match the contract §5 table exactly (verified against ARCHITECT_PRESENTATION_CONTRACT.md Palette).
 - Open: checking actual rendered foreground/background combinations, visible focus and reduced-motion are the screen's job (M5-T149 browser walkthrough); this task checks the declared token pairs arithmetically.

ROW D-090-R838 — PASS
 - One source docs/design/presentation-tokens.json generates both the marked globals.css block and services/api/app/drawings/kit/presentation_tokens.py; `node presentation-tokens.mjs --check` exit 0 confirms both equal a fresh render.
 - Drift fails closed: node S1 and python test_changed_json_colour_without_regeneration_fails prove a changed colour without regeneration breaks both outputs; dr.sha256_text_artifact(requirements.json) and the parity tests all reproduced.
 - Open: consumers (TSX/SVG/PDF templates) adopting the tokens instead of scattered magic numbers is later work (M5-T149+); the shared source and parity mechanism exist now.

ROW D-090-R855 — PASS
 - All five adapters read values/labels/units/reasons/conditions from the generated contract types and only format or group; I read each file and found no law decision, no zoning recalculation and no geometry invention (ruling V2).
 - presented-results/presented-notices operate over ThreeAnswersResults; result-identity reads scope; metric-format reuses displayQuantity/quantityText; nothing writes back or recomputes.
 - Open: none for this task; wiring the adapters over the one canonical result on the screen is M5-T149.

ROW D-090-R856 — PASS
 - metric-format.ts distinguishes 0 (a value → "0 sq ft") from null/undefined/non-finite (→ not_known, never a number) using `value == null || !Number.isFinite(value)`, never `value || 0`; metric-format.test.ts proves exactly-0 and the null/NaN/Infinity cases.
 - result-identity.ts carries a revisionFingerprint (FNV-1a over results_id/study_id/option_id/revision/computed_at); identitiesMatch returns false for another lot and for a bumped revision (stale export caught), proven in result-identity.test.ts.
 - Open: enforcing "screen and export share one revision / prevent stale export" across surfaces is wired in M5-T149/PDF; the full six-way taxonomy (NA, not-assessed, failed-check) lives in the document value_state model plus result-status reasons — this task supplies the distinctions and the stale-export detector.

ROW D-090-R857 — PASS
 - No reference sample constant enters the adapters: production values are read from the document (e.g. presented-results computes `${twoDp(estimate.quotient_low)} to ${twoDp(estimate.quotient_high)}`); the only constants are UI wording ("Not known", "Conditional", "Site fit not verified", NO_SCOPE_REASON).
 - The literal "17.27 to 21.59" appears only in a TEST as a cross-check of the fixture value; the benchmark fixture carries quotient_low 17.27 / high 21.59 (ruling V9), confirmed in packages/contracts/fixtures/valid/results/recorded_215_16_northern_journey.json.
 - Open: none for this task.

ROW D-090-R858 — PASS
 - presentation-tokens.mjs imports only Node built-ins (node:fs, node:url, node:path, node:process); the Python module is generated text with no import; apps/web/package.json and package-lock.json are unchanged in the whole branch diff.
 - No framework, chart library, PDF converter or font service added.
 - Open: none for this task.

ROW D-090-R859 — PASS
 - This task is the contract's step 2 (shared presentation: tokens + metric formatting + status/reason presentation + result identity), the step M5-T149 (step 3, the website slice) consumes; the wave concurrency record and the packet order place it before the slice.
 - The adapters are built as pure libraries with no component consuming them yet, matching "establish shared presentation" before "finish one website slice".
 - Open: steps 3–7 (website slice, PDF slice, remaining sections, bounded acceptance, deliver) are M5-T149 and later tasks.

ROW D-090-R871 — PASS (UX-03)
 - PresentedStatus has no numeric field and no "verified" case; presented-results never gives a withheld value a digit (presented-results.test.ts "never gives a withheld value a digit" over every committed fixture) and never produces "verified"/"achieved".
 - result-status.test.ts over every committed fixture asserts withheld→not_known-with-reason-no-digit and never "Verified"; these are state tests on the canonical generated contract.
 - Open: the full UX-03 state tests on the live screen (promotion on the rendered surface) are M5-T149; this task meets it at the adapter/contract level.

ROW D-090-R872 — PASS (UX-04)
 - collectConditions lists shared notices once with per-result references; capNotices caps at three and counts the rest ("2 more") dropping none; proven in presented-notices.test.ts.
 - The adapter preserves which result carried a condition, so a material local exception is not lost.
 - Open: applying "shared once, local exception visible" on each screen surface and the disclosure inventory is M5-T149.

ROW D-090-R873 — PASS (UX-05)
 - result-identity.ts gives lot BBL, lot display, resultsId and a revision fingerprint; identitiesMatch is true only for same lot+resultsId+fingerprint, false for another lot and for a different revision (the stale-response detector), proven in result-identity.test.ts.
 - A document with no scope yields an unknown identity that matches nothing, never a guessed lot.
 - Open: using this identity to keep screen, comparison, drawings and PDF on one property/scenario/revision/basis, and the live stale-response scenario, are M5-T149 and the PDF/drawing step.

ROW D-090-R877 — PASS (UX-09, contrast share only)
 - The contrast portion is met: every declared text/background and control pair is computed in presentation-tokens.test.mjs (text ≥ 4.5:1, control edge ≥ 3:1), and status is told by words (plain "Conditional"/"Not known"), never colour alone.
 - This task is a token/adapter library with no rendered screen.
 - Open: keyboard, focus, modal return, accessible names and status announcements are the screen's keyboard walkthrough in M5-T149; only the declared-pair contrast is satisfiable here.

ROW D-090-R886 — PASS (evidence)
 - Correctness values are independently established: the node/python token tests assert the contract §5 table values and compute contrast arithmetically; the adapter tests read expected values from the committed reviewed fixtures (recorded_215_16_northern_journey, synthetic_all_answers_available), not from the adapters' own output.
 - The estimate expectation is cross-checked against the fixture (quotient_low/high 17.27/21.59), not a second copy of one fixture.
 - Open: screenshot baselines are M5-T149's browser gate; this task has none.

ROW D-090-R888 — PASS
 - Producer/reviewer separation held: producer frontend-engineer (two builders, parts A/B); gate records show G3 reviewer "code-reviewer", G4 reviewer "qa-engineer" (both ≠ producer); G2 is role "self_check" recorded by orchestrator, not called independent review; I am the independent DCV.
 - No extra orchestration added; heavy suites were CI's job (I did not re-run them).
 - Open: visual-quality and human-journey reviews concern the rendered screen (M5-T149); they are not applicable to this task's headless adapters.

ROW D-090-R890 — PASS
 - The producer reports and evidence map claim only what changed and was tested; they explicitly state "no component consumes them yet", "the review should confirm the chosen points", and never say perfect/fully verified/complete/production ready.
 - No overclaim based on green tests was found in the M5-T148 records.
 - Open: none for this task.

ROW D-090-R895 — PASS
 - presented-results.ts has no "achieved" kind; a listed building is "scheduled" carrying note SITE_FIT_NOT_VERIFIED = "Site fit not verified" set as a field separate from any caveat; presented-results.test.ts asserts never "achieved" and note == "Site fit not verified" across fixtures.
 - R895's own text says "site fit unverified"; the orchestrator's ruling V5 (which governs, later-over-earlier) standardised the wording as "site fit not verified" — same meaning, no weakening.
 - Open: the on-screen/PDF ordering ("before any caveat") and the PDF text search for "achieved" are M5-T149 and the PDF step; this task guarantees the adapter never emits "achieved".

(3) BINDING
 - B1 PASS. The requirements.json diff 0bb6acb2..db7824 appends M5-T148 to 23 pre-existing rows' applicability.task_ids with their `text` unchanged (script comparison: all 23 text_unchanged=True, M5-T148 absent at base, present at head); no existing row's text changed (changed-list empty). R895 is a NEW row added by the source-080 amendment (one of R892–R899) and already carries M5-T148 in task_ids — a new-row capture, not an edit of an existing row.
 - B2 PASS. dr.sha256_text_artifact(requirements.json) = 59a3752d3d2c60ed2f4d858295f914b12d14cdf97faa3811e8f157f63d2e5304, equal to manifest.requirements_content_digest_sha256; validate_directive_compliance.py --check exit 0 validates the id digest, source digests (incl. source-080 df30f9…) and the amendment chain; manifest lists source-080-amendment.md and an "amended" audit entry plus the M5-T148 applicability_bound entry naming exactly the 24 rows.
 - B3 PASS. verification.json has exactly one M5-T148 row (producer "frontend-engineer", verifier ""), applicable_requirement_ids = the 24, reviewed_sha null, reviewed_manifest_sha256 null, and all 24 requirement entries state "pending", evidence [], reviewed_sha null.
 - B4 PASS. reg.evaluate_task_refs(M5-T148 packet) = {ok:true, applicable_ids == cited_ids == the 24, missing_ids [], invalid_refs [], unresolved [], reasons []}.
 - B5 PASS. reg.derive_applicable(task) across all active directives returns exactly the 24 ids, unresolved []; conjunction semantics (every non-empty applicability dimension must match, active directives only) means no other active directive's requirement binds M5-T148 uncited. (A naive OR-scan flags D-009/D-004/D-007/D-064 path/type rows, but those fail the real conjunction/active test — the authoritative derivation excludes them.)
 - GATES PASS. G0 PASS (orchestrator, administrative, reviewed_sha 61be9792). G2 PASS (orchestrator, self_check), G3 PASS (code-reviewer), G4 PASS (qa-engineer) all at one content identity: content_manifest_sha256 734f2446…, reviewed_sha 5bf6f729. gh read of CI run 38023638114 at headSha d745b635 = completed/success, 21/21 jobs; gate reviewed_at 04:37 UTC is after CI completion 04:26 UTC, so gates were recorded after CI was green; the M5-T148 material blobs are byte-identical from d745b635 to the frozen head.

(4) CARRY-FORWARD CONDITION
 - My PASS may be stamped at a later head WITHOUT a new review while this blob-level predicate holds: the blob ids of apps/web/src/lib/architect, apps/web/src/app/globals.css, apps/web/scripts, docs/design, services/api/app/drawings, services/api/tests/drawings, packages/contracts, .github, tools and the task's reports are unchanged, AND these 24 rows' text and the M5-T148 binding (requirements.json task_ids, manifest digests, the verification.json row) are unchanged.
 - Tolerated later commits: those touching only project-control/, docs/DISCOVERY_BACKLOG.md, docs/SESSION_HANDOFF.md, the acceptance seams of M5-T149/M5-T150 on this branch, and a main-line merge that changes none of the predicate's files. I confirmed all commits d745b635..db7824 touch only project-control/ (26 files), so the condition already holds from the reviewed code head to the frozen head.

(5) REQUIRED CORRECTIONS
 - None. One non-blocking observation: the evidence map's R877 line "focus-ring tokens exist" is not backed by a distinct focus token in presentation-tokens.json (the source has no focus/reduced-motion token); focus visibility and reduced motion are correctly deferred to M5-T149, so this does not affect R877's this-task contrast share. No change required.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I could not move my copy rv-w6-a to the frozen head (read-only guard blocks git checkout); I inspected via the w-wave20 worktree (already at db7824, clean) and git plumbing.
 - I did not run the full web vitest/Playwright suites or the full api pytest (per brief and policy); I verified the five adapters' tests by reading their assertions, ran the permitted node and python token tests, and read CI run 38023638114 = 21/21 success at d745b635 (material blobs byte-identical to the frozen head). Real rendered-pixel contrast, keyboard/focus and the browser walkthrough are M5-T149's gates.
 - I did not re-run CI and cannot attest to the pushed state beyond d745b635 (the commits after it are local/unpushed per the brief); I relied on the frozen-head git objects and the single permitted validator run.
 - Owner questions C1 (verified-label) and C2 (six PDF labels on the screen) are the owner's open decisions, outside my verification.

END-OF-REPORT
```

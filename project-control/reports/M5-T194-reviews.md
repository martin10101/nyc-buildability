# M5-T194 reviews (every return kept unchanged)

- One producer round (backend-engineer, worktree): f9fee602, integrated as the cherry-pick 7f6dc46c on task/wave29-scenario-drawings (6 files, all inside the allowed paths; blobs equal to the builder commit).
- G2 orchestrator self-check at 8e1d5912: the whole api suite passed on the increment (10179 passed, 8 skipped; api-suite-B124.log); ruff, research record check and lane coverage PASS.
- G3 code-reviewer PASS, G4 qa-engineer PASS at the builder commit (same content). Carried into the wiring part (M5-T173): an explicit not-drawn illustration state once the legacy predicate is deleted; the 'illustrative_footprint' kind pinned against the kit style kind.

Every reviewer is an AI agent; none is a human or professional review.

## G3 (code-reviewer)

VERDICT: PASS (G3 code-review, M5-T194). I am an AI agent (read-only reviewer); this is not a human or professional review.

# Gate Report

- Gate ID: G3
- Task ID: M5-T194 (M5-T173 part B4 — drawn-content manifest)
- Reviewer: code-reviewer (AI, read-only)
- Producer: backend-engineer
- Result: PASS
- Clean environment/worktree used: reviewed commit f9fee602e874a3b25f4de5e771daa9b847c7dcd7 (parent b9e9d563). Read via `git -C /root/project/nyc-buildability/.claude/worktrees/agent-a0df7849c15c5732f show f9fee602:<path>`; ran against a clean `git archive f9fee602` extract at /tmp/claude-0/code-reviewer/repo3 using the lanes venv (/root/project/lanes-runtime/venv), PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider, multi-file runs under flock /root/project/lanes-runtime/heavy-run.lock.

## Acceptance criteria reviewed
Scope is exactly the 6 allowed-path files (git show --stat confirms +485/-35, no forbidden path touched; builder.py, page_location.py, kit/ untouched as required — wiring is part W).
- S1 (byte-identical defaults): PASS. Full `tests/drawings/report` folder = 235 passed, exit 0, incl. test_report_comparison.py and test_report_appendix.py. All pre-existing tests pass unedited with the new production code → new kwargs default to legacy output.
- S2 (manifest feeds chart, 3 honest states): PASS. Reproduced via test_s2 and an independent probe.
- S3 (appendix reads state; never "shown" without a drawn SVG): PASS (test_s3 + probe).
- S4 (non-finite share → None, no inf/nan): PASS (test_s4).
- S5 (zero allowance → no chart, pinned): PASS (test_s5).
- S6 (embed_map footprint failure keeps map + names what was not drawn): PASS (test_s6).
- S7 (ruff + modularity; manifest <150 SLOC; drawings_embed/page_evidence grow ≤40): ruff clean; SLOC budget met (see modularity note). modularity_check.py itself not executed in sandbox — see note.

## Directive/requirement verification
This task is in-regime (directive_refs D-094 R050/R095/R098/R198/R200/R203/R204/R205/R277/R278). Per the gate protocol the independent directive-compliance-verifier performs the per-requirement re-derivation and records it in the directive's verification.json (producer ≠ verifier). I did not have the D-094 requirement source text to re-derive each ID, so I report them UNVERIFIED-BY-ME; from a code-review standpoint the behavior matches the audit-section-3 intent (every drawn/shown/placed claim reads rendered Embedded content, never a hard-coded constant or a bare results field). ACTION FOR ORCHESTRATOR: do not accept until the directive-compliance-verifier PASS is recorded for all ten requirement IDs at content identity f9fee602.

## Steps independently executed (clean extract repo3, venv)
1. `ruff check .` → All checks passed, exit 0.
2. `pytest tests/drawings/report/test_report_drawn_manifest.py` → 8 passed, exit 0.
3. `flock … pytest tests/drawings/report` → 235 passed, 1 warning, exit 0; collect-only confirms the new file contributes 8 collected nodes.
4. Independent `python -c` probe (no file writes): (P1) absent site_plan can never yield "Shown on the site plan"; (P2) a drawing with a wrong kind name → "Worked out; not drawn" (the kind literal is load-bearing); (P3) the exact `illustrative_footprint` kind → "Shown"; (P5) confirmed the handoff semantics — method `illustration_state=None` follows the legacy predicate while an explicit non-None sentinel bypasses it.
5. Read manifest.py in full: it reads only Embedded.is_drawing / .kinds_drawn / .svg data-roles; no results field, no arithmetic. Verified kit contracts: `area_zone_apartment/other` and `area_bar_apartment/other` data-roles exist in kit/area_allocation.py (lines 427/429/459/461) and `Drawing.kinds_drawn` exists (kit/model.py:196).

## Expected versus actual
Builder claimed 235 folder-pass; reproduced 235 exactly on a clean extract. (A transient 227 I saw mid-review was an artifact of my first scratch extract's test file being clobbered to a placeholder; the committed f9fee602 test file is the real 205-line content, re-verified by `git show`. Not a defect in the commit.)

## Evidence paths
- manifest.py: /root/project/nyc-buildability/.claude/worktrees/agent-a0df7849c15c5732f (git show f9fee602:services/api/app/drawings/report/manifest.py)
- Clean extract run tree: /tmp/claude-0/code-reviewer/repo3/services/api
- Packet: project-control/tasks/M5-T194.json (allowed/forbidden paths, S1–S7, directive_refs)

## Regression/security/provenance findings
No regression: 235 existing+new tests green; HTML/byte identity for unwired callers proven. Provenance sound: manifest carries only booleans + one state word derived from rendered content; every figure still read from the document via readers. No security surface.

## Defects
None blocking.

## Required rework
None.

## Advisory findings (not blocking; carry into part W / orchestrator notes)
1. ADVISORY — manifest.py:24 `_FOOTPRINT_KIND = "illustrative_footprint"` is a forward cross-part contract the kit does NOT yet emit (grep confirms it appears only in manifest.py; part B1 is unbuilt). Until B1 emits exactly this kind, the chart safely under-claims ("Worked out; not drawn"); if B1 emits a different kind name the footprint will never read as drawn. Part W's integration test must pin this literal equal to the kit style kind (packet RISK 1). This matches the brief's declared "unknown and staying unknown."
2. ADVISORY — None-value collision for part W: the manifest's `area_illustration_state=None` means "not drawn", but `page_evidence._area_illustration_method(illustration_state=None)` means "use the legacy predicate". Output is coincidentally correct today (legacy returns False). When part W deletes `_area_illustration_drawn`, it MUST pass an explicit non-None/non-'zones'/'bar' not-drawn sentinel (tested path) or rewrite the None branch. The builder documented this accurately and completely in the handoff; recommend the orchestrator copies this constraint into part W's packet.
3. ADVISORY — drawings_embed.embed_map: when both an overlay (constraint_lines/input_facts) and a placed_footprint are supplied and the first render raises, the retry drops BOTH extras and the note may say the zoning line could not be drawn even if only the footprint failed. Safe direction (never over-claims a drawing); pre-existing drop-the-overlay pattern extended. No action required.

## What I did NOT check
- Did not execute `tools/modularity_check.py --check` (the extract is not a git repo and the read-only guard blocks `git init`). Verified the budget directly instead: manifest.py 94 total lines (~66 SLOC) < 150; net growth drawings_embed.py +31 and page_evidence.py +19 lines, both < the 40-line S7 budget; all far below the tool's WARN=600 threshold; the new module has one clear responsibility and page_evidence's new `_area_illustration_drawing_clause` is a clean extraction (no dumping-ground, no giant function). Builder reported EXIT 0; CI runs it authoritatively.
- Did not render a PDF (N/A: this part changes no rendered page; byte-identity proven by S1 + the 235-test run).
- Did not re-derive each D-094 requirement from source (directive-compliance-verifier's role).
- Did not verify part W wiring or part B1 kit emission (out of scope; unknown and staying unknown per the brief).
- Note: test_scenario_sheet.py (1 line) and test_qualifying_options.py (0 lines) are pre-existing empty placeholders outside this task's scope; their zero collected tests are not a regression.

## Reviewer conclusion
PASS. The commit satisfies the packet objective and S1–S7, reads claims from rendered content (no results-field or arithmetic coupling), keeps unwired callers byte-identical, and the part-W handoff note is correct and complete. Acceptance remains conditional on the orchestrator recording the directive-compliance-verifier PASS for all ten D-094 requirement IDs at f9fee602; the three advisories above should be carried into part W's packet but do not block this gate.

END-OF-REPORT

## G4 (qa-engineer)

VERDICT: PASS

G4 (qa-engineer) independent gate for M5-T194 (M5-T173 part B4 — drawn-content manifest). Frozen commit f9fee602e874a3b25f4de5e771daa9b847c7dcd7, parent b9e9d563. Reviewed read-only on a scratch archive under /tmp/claude-0/qa-m5t194/repo (extracted via `git archive f9fee602` from the shared object store; the isolation guard blocks `git -C` to the builder's worktree). I am an AI agent; this is not a human or professional review.

CONTENT IDENTITY (verified)
LF sha256 (`tr -d '\r' | sha256sum`) of all five changed files matches the builder's producer report exactly:
manifest.py f5e7a04a…, drawings_embed.py 399c3db7…, page_option_comparison.py 70e67ef9…, page_evidence.py 667e90af…, test_report_drawn_manifest.py 00875cce…. So the code I tested is the frozen submission, and it was pristine again after my mutation/restore cycle.

CHECKS RERUN ON SCRATCH (venv /root/project/lanes-runtime/venv, PYTHONDONTWRITEBYTECODE=1, pytest -p no:cacheprovider; api from services/api)
- ruff check . → All checks passed! EXIT 0
- tests/drawings/report/test_report_drawn_manifest.py → 8 passed in ~1.0s EXIT 0
- tests/drawings/report (under flock heavy-run.lock) → 235 passed, 1 warning in 83.63s EXIT 0 (matches the builder; confirms S1 byte-identity — the untouched existing tests, incl. test_report_comparison.py and test_report_appendix.py, pass unedited; diff stat shows only 6 files changed, none of them existing test files)
- modularity: the git-based `tools/modularity_check.py --check` cannot run on a plain archive (needs `git ls-files`), so I verified its inputs directly with its own `source_lines()` + the committed baseline: manifest.py NEW at 66 SLOC (far below WARN 600); growth drawings_embed.py +20, page_evidence.py +17, page_option_comparison.py +2 — all within the packet's S7 bound (≤40) and the tool thresholds. No new oversized file, no material over-growth. (Authoritative git run is CI's / the builder's EXIT 0.)
- No review_register entry and no evidence record pins any of the four edited files (grep-confirmed) — the producer claim is accurate; no stale-pin red-turn risk.

FOUR CLAIMED MUTATIONS — all reproduced exactly (revert → test fails → restore):
1. manifest footprint flag forced False → test_s2 FAILED `assert (True and False)`.
2. chart ignores footprint_drawn (drawn = legacy predicate only) → test_s2 FAILED, "Shown on the site plan" absent ("Worked out; not drawn" instead).
3. page_evidence zones clause replaced → test_s3 FAILED, zones sentence absent.
4. manifest zone-role detection disabled → test_s3 FAILED `assert None == 'zones'`.

DISCONFIRMING INPUT STATES I ADDED (not in the builder's test file; run through the REAL area kernel + manifest, all PASS):
(a) site plan that drew the lot + overlay but NOT the footprint — kinds_drawn=("lot_outline","established_overlay") → site_plan_drawn True, site_plan_draws_footprint False, chart "Worked out; not drawn" (the brief's suggested state; builder had only tested empty-kinds).
(b) footprint present AMONG other kinds → site_plan_draws_footprint True, chart "Shown on the site plan".
(c) a non-drawing short line AHEAD of a real drawn zones illustration in the list → state "zones" (the loop correctly skips non-drawing entries).
(d) anti-false-positive: an SVG carrying only ONE of the two zone roles → state None (both roles required by `_svg_has_roles`'s all()); a real fitted=False illustration → state "bar".
I also independently confirmed the kit `Drawing` carries `kinds_drawn` (model.py:196) and that `attrs()` renders `data-role="area_zone_apartment"` double-quoted, matching the manifest's literal lookup — so the design's SVG-role detection is wired to the real output format, not an invented one.

DESIGN CONFORMANCE (verified against H4 Parts 2-3 and H5 PART 1 item 5 / PART 2 B4)
- Manifest is built ONLY from rendered Embedded values (kinds_drawn; SVG data-roles) — no results field, no arithmetic (manifest.py reads only Embedded; figures stay in the document).
- Every new keyword defaults to byte-identical legacy output (footprint_drawn=None → legacy predicate; illustration_state=None → legacy clause; embed_map placed_footprint=None forwards nothing). Confirmed by test_s1 + the 235-test run.
- The three chart states and the appendix clause cannot claim a drawing that is absent (mutations + states a/b/d).
- embed_map failure path keeps the map and names what was not drawn (footprint note / overlay note, conditional on which extra was forwarded; M5-T175 overlay-drop behavior preserved — single _OVERLAY_DROPPED_NOTE on the overlay-only path). test_s6 + 235 run.
- No zoning arithmetic introduced in any renderer.

HANDOFF NOTE FOR PART W — correct and complete. The one subtlety: `None` is overloaded across the two layers — manifest `area_illustration_state=None` means "not drawn", but `_area_illustration_method(illustration_state=None)` means "use the legacy `_area_illustration_drawn` predicate". B4 keeps this SAFE (the legacy predicate stays and returns False → correct "not yet drawn" output) and provides a tested explicit-not-drawn branch (test_s3_explicit_not_drawn_state_ignores_the_legacy_predicate). The builder's return (line 49) states W must pass an explicit non-None not-drawn token or rewrite the None branch once it deletes the legacy constant. I confirm this is accurate, and that the footprint path has NO such ambiguity — the manifest returns a plain bool (never None), so wiring `footprint_drawn=manifest.site_plan_draws_footprint` is unambiguous.

DIRECTIVE REQUIREMENTS (corroborating only; the directive-compliance-verifier owns the authoritative verdict)
- D-094-R050 ("'Shown on the site plan' only when it is"): satisfied — chart status driven by the real footprint-kind flag (mutation 2, states a/b).
- D-094-R095 ("appendix method calls the illustration shown only when drawn"): satisfied — "it is shown as zones/bar" only for a 'zones'/'bar' state derived from real drawn SVG roles (test_s3, state d).
- D-094-R098 ("every drawn/shown claim decided from rendered content"): satisfied — manifest reads only rendered Embedded, no constant, no results field.

FINDINGS
- No REQUIRED findings.
- ADVISORY 1 (for part W, not a B4 defect): carry forward the `illustration_state=None` overloading above; pass an explicit not-drawn token from the manifest's None state. Already flagged + tested by the builder.
- ADVISORY 2 (unknown, staying unknown per the brief): the 'illustrative_footprint' kind literal and the kernel data-role names are cross-part contracts with B1 (not built) and the kernel; B4 cannot verify B1 emits that exact kind. W's integration test must pin kind == kit style kind.
- NOTE: build_manifest gives area_illustrations/sections a () default though the planner listed them without defaults — additive and harmless (a caller passing all three is identical); the builder reported it.

WHAT I DID NOT CHECK
- No PDF/real-print or integrated-report render: part B4 changes no rendered page (all new behavior defaults to legacy), so there is nothing new to print here — that is part W's job (the brief lists the wiring and B1 as staying unknown).
- No full api pytest / web suites (out of G4 scope; CI runs them at the accepted head).
- `modularity_check.py --check` end-to-end (needs git; verified SLOC/baseline inputs directly instead).
- Authoritative D-094 requirement verdict is the directive-compliance-verifier's.

END-OF-REPORT

# M5-T179 reviews (every return kept unchanged)

- G2 orchestrator self-check: the builder's commit integrated as d36341bc (cherry-pick of 0f5c23d8); its five files inside the allowed paths (test_report_pages.py added by the scope correction of 2026-10-14 for the one assertion that pinned the defect); LF sha256 equal to the builder's return.
- G3 code-reviewer: PASS, no required finding.
- G4 qa-engineer: PASS; its one advisory (the CI run at the material commit was cancelled by the next push) is answered by reading CI green at the submit head.

Every reviewer is an AI agent; none is a human or professional review.

## G3 (code-reviewer)

<!-- saved unchanged by save_return.py from agent-a33cba4253513fab2.jsonl, entry 2026-10-14T18:32:34.173Z, sha256 efec2971cf45039687b6e6c0a3432e8d337057f420ef41e347460255c1f912ae -->
# M5-T179 — G3 code-reviewer gate report

I am an AI agent (code-reviewer), independent and read-only; this is not a human or professional review. Pin `d36341bc9` on `task/wave24-report-v3` in /root/project/w-wave20; claim head `6cc452af0`.

## VERDICT: PASS

No REQUIRED findings. The change is a correct, minimal, byte-scoped presentation fix; every G3 item re-derived from source and reproduced.

## What I verified (all reproduced independently)

Cherry-pick identity — the pin's four material blobs are byte-identical to the builder's commit `0f5c23d8` (`git hash-object` match on builder.py, page_assumptions.py, test_report_pages.py, test_report_scope_note_maps.py).

Correctness & scope:
- Pass-through is the builder's own `maps_present` (builder.py:81 `maps_present = surroundings.available`), the same value already handed to page 1 (page_decision_summary, builder.py:86). builder.py:92 now adds `maps_present=maps_present`; no other builder change.
- `page_assumptions.render` / `_material_exclusions` take `maps_present` as keyword-only, default `False`, forwarded to `coverage.coverage_groups`. Default preserves every other path.
- `coverage.py` is byte-identical to the claim head (`git diff` empty) — not edited, and it already supported `maps_present`.
- Only caller of `page_assumptions.render` in the whole repo is builder.py (git grep); `_material_exclusions` is private. The keyword-only default makes the signature backward-compatible.
- Docstring now true: it states 'Context maps' is excluded only when maps are not printed and that the builder's `maps_present` reaches it — matches behavior.
- `test_report_pages.py`: the only change is the final assertion of `test_q3_...` (`"Context maps" in text` → `"Context maps" not in text`, + 2 comment lines). Semantically right: the coverage inventory left page 1 (M5-T165), so with maps printed 'Context maps' belongs to "In this report", is listed nowhere visible, and the scope note drops it. The test (coverage data check + `<svg>` presence + whole-text absence) is coherent and passes.
- New test file asserts the displaced value — S4 mutation: wrapping `page_assumptions.render` to drop `maps_present` (exactly the reverted builder line) makes 'Context maps' reappear in the scope note (would fail S1's `assert "Context maps" not in names`); as-shipped it is absent. Confirmed.

Focused checks in an archive copy of the pin (lanes venv, `-p no:cacheprovider`, from services/api):
- `ruff check .` → exit 0, All checks passed.
- new test file + the q3 test → 15 passed, exit 0.

S2 (my own script, claim head vs pin): all 12 valid results fixtures built without a map context are byte-identical — per-fixture SHAs match and COMBINED digest `d08781ff…` is equal on both versions.

S3 (my own script): benchmark with its recorded window map context — claim head SHA `3a178918…` (len 139949) vs pin `ee751109…` (len 139935), matching the builder's recorded values. In-process the simulated claim-head output reproduces `3a178918…` exactly, and the sole delta vs the pin is a single contiguous removal of `; Context maps` (common prefix 125497 B + common suffix 14432 B, PIN middle empty) — no other byte changes anywhere. Delta −14 B.

Modularity: trivial change (one keyword-only param + docstring/comment; new focused test file in the existing folder). No responsibility mixing, no module growth, public interface stable. No findings.

Research/verification (D-093): confirmed presentation-only. No zoning fact, source reading, calculation or certainty label changes; section-state source of truth (coverage.py) unedited; no evidence records touched (forbidden path). The scope note now matches what the report actually prints.

## ADVISORY findings
1. (ADVISORY, reproducibility note — not a defect) The read-only guard blocks shell file-writes even under the scratch dir, so I performed the S4 mutation and S3 byte-diff in-memory (wrapping `page_assumptions.render`) rather than editing a scratch copy; the simulation's SHA matches the real claim-head archive build, so the proof is faithful.

## What I could not check (out of G3 scope / by rule)
- Full `tests/drawings` heavy suite and CI at branch head — the qa-engineer's section (I ran focused tests only).
- S5 live preview print (needs integration; the S3 byte proof is the page-7 before/after evidence).
- Browser/e2e/ports — forbidden.

END-OF-REPORT

## G4 (qa-engineer)

<!-- saved unchanged by save_return.py from agent-a7f2abb6d8a266164.jsonl, entry 2026-10-14T18:36:37.614Z, sha256 7518ae1765ff8eb57c9edc103c3645e0e545fd32a7b1c4fd4e6234c161f1a71d -->
M5-T179 — G4 QA GATE REPORT (independent, read-only). I am an AI agent, not a human/professional reviewer; I did not produce this work. Reviewed at pinned material commit d36341bc9 (cherry-pick of builder 0f5c23d8) on task/wave24-report-v3; claim head 6cc452af0.

VERDICT: PASS

== What I ran (archive copy of d36341bc9 in /tmp/claude-0/m5t179-g4; lanes venv; PYTHONDONTWRITEBYTECODE=1; pytest -p no:cacheprovider) ==
- ruff check . (services/api): exit 0, "All checks passed!"
- pytest -q tests/drawings (services/api, heavy, run once; pgrep showed NO other pytest): exit 0 — 1179 passed, 6 skipped, 158.55s. Matches builder return 2.
- modularity_check.py --check (isolated scratch git repo): exit 0, 0 failures; warnings all pre-existing, none on builder.py/page_assumptions.py.
- check_lane_paths.py --coverage: exit 0, "LANE COVERAGE PASS" (every file one lane).
- CI at branch: `gh run list --branch task/wave24-report-v3` (read-only, not rerun) — the M5-T179 commit (d36341bc) main CI run 38614710031 is CANCELLED (secret-scan + context-budget succeeded); it was cancelled when the next push (M5-T175 046c717d, 18:30) landed 7 min later — the known "own push cancels in-flight CI" signature, not a failure. Branch head is now 046c717d with CI in_progress.

== Scenario table (test proves each; asserts the "then") ==
- S1 test_s1_scope_note_drops_context_maps_when_maps_are_printed: PASS. Asserts "Context maps" not in the printed note AND names == no-maps names minus "Context maps" (same order/words); expected read from coverage.coverage_groups, not retyped.
- S2 test_s2... (12 params, every valid results fixture): PASS. Asserts note still lists "Context maps" without a map context. Full byte-identity "then" proven by my own script below (test guards only the note subset — acceptable; existing suite goldens cover the rest).
- S3 test_s3...: PASS. Asserts the only scope-note difference is "Context maps"; byte-level "no other byte changes" proven by my script below.
- S4 (my mutation): reverted builder.py:92 to drop maps_present → S1 AND the corrected q3 test both FAIL (exit 1, "assert 'Context maps' not in [...]"); restored → both PASS (exit 0). Both guard the displaced value.
- S5 (preview before/after): not executable in this worktree (integration-time); the S3 byte delta is the page-7 before/after evidence (R083).
Verbose run of the new file + the corrected q3 test: 15 passed.

== My own S2/S3 byte scripts (baseline = git archive 6cc452af0, after = d36341bc9) ==
- S2: all 12 valid results fixtures built WITHOUT a map context are BYTE-IDENTICAL (sha256 diff empty) between claim head and after.
- S3: benchmark WITH its recorded window pack (LANE_E_ENABLED=1): baseline 3a178918… len 139943 vs after ee751109… len 139929. Common prefix 125497 B + common suffix 14432 B identical; the ONLY middle delta is baseline '; Context maps' → after '' (−14 B); single diff hunk 818c818. Digests match the producer's exactly. The note goes from "…; Financial analysis inputs (held); Context maps" to "…; Financial analysis inputs (held)"; every other name, order, label-chip and provenance line unchanged.

== Correctness / scope ==
- Pass-through is the builder's own maps_present = surroundings.available, the same value page 1 (page_decision_summary) receives (builder.py:81,86,92). Only caller of page_assumptions.render is the builder (git grep). New params are keyword-only with default False, so every other path and the no-map report are unchanged (S2 confirms).
- coverage.py NOT edited (it already supports maps_present; coverage_entries moves "Context maps" to IN_REPORT when maps_present). Confirmed not in the commit.
- Commit touches exactly 5 files, all in allowed_paths (producer report, builder.py, page_assumptions.py, test_report_scope_note_maps.py new, test_report_pages.py via the recorded scope correction). No forbidden path touched.
- test_report_pages.py change is the single assertion (in→not in) + a 2-line comment, as the scope correction authorizes; nothing else in that file.
- Docstring in _material_exclusions is now true (no longer says the page is built without map context).
- Modularity boundaries fine: trivial growth, no responsibility mixing, no new module, public interface backward-compatible, behavior covered by the new tests.
- D-093: presentation-only — no fact, reading, calculation or verification label changes. S2 byte-identity and the S3 single-string delta confirm no label-chip/provenance/number moved.
- Directive content: R137 (page 7 no longer lists context maps when printed) satisfied by S1/S3 and the q3 test; R083 (before/after of the changed page) satisfied by the S3 byte delta. The authoritative in-regime directive pass belongs to the directive-compliance-verifier.

== Findings ==
1. ADVISORY (informational, not a defect): the main CI job at the M5-T179 head (d36341bc) is CANCELLED, not green, because the next push cancelled it. Correction: the orchestrator must read a green full CI at the actual accept head before acceptance (D-090-R639). Not a defect in this work.

== Could not check ==
- Browser/e2e/server/ports 3000/3001/8000 (forbidden; not run).
- Full services/api pytest and CI green at the accept head (orchestrator's job).
- S5 preview print before/after (needs integration; the S3 byte delta substitutes as page-7 evidence).

No REQUIRED findings. All scenarios reproduce; scope clean; checks green at the pinned content.
END-OF-REPORT

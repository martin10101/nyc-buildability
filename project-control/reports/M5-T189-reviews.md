# M5-T189 reviews (every return kept unchanged)

- One build round (backend-engineer, worktree): builder commit 032c64d5 (parent the claim head 1cbc8ccf) integrated as the cherry-pick 23aeeff5 on task/wave28-placement-wiring (7 files, all inside the packet's allowed paths; LF sha256 of each equal to the builder's return). Scope correction 1 (55272ad0, G0 re-recorded at f0ab8a4e) added scenario S10 (the print-stylesheet wrap rule for the run identity column, DB-280) while the builder worked; no path changed.
- G2 orchestrator self-check at 23aeeff5: the seven files equal the builder's digests; nothing outside the allowed paths; lane coverage PASS; the evidence record NB-04 and close_frame_dimensions.py untouched; the real-preview print of 23aeeff5 with the code commit set (print-23aeeff5, the preview now passes GIT_COMMIT_SHA as production passes RENDER_GIT_COMMIT) has 10 pages, pages 1 to 9 text-identical to main 86a450d4's print and page 10 different only in the run identity (the wrapped commit and the fingerprint); main's print with the commit set had 8 pages (the defect).
- The four 'orphan calculation page' failures the builder saw in the whole api suite came from the contract's placeholder pages of M5-T172, removed at dc8449d1 (the parent of this head).
- The report's document fingerprint differs between runs of the same request (seen by the builder and in the orchestrator's prints); it is not caused by this task (CSS cannot change a results hash) and is checked separately.

Every reviewer is an AI agent; none is a human or professional review.

## G3 (code-reviewer)

# G3 Code Review — M5-T189 (report/figure rendering hardening; DB-277/DB-278/DB-280 S10)

I am an AI agent (code-reviewer), read-only. This is not a human/professional review. Reviewed at the pinned frozen SHA `23aeeff5d2af48e584661d79e19aa265387eb203` (`task/wave28-placement-wiring`, worktree `/root/project/w-wave20`, which was at this HEAD throughout). Ran tests from a scratch copy extracted by `git archive 23aeeff5`.

## VERDICT: PASS

No REQUIRED findings. One ADVISORY observation below.

## What I checked (each CHECK item)

1. **`_css_string` escape order (layout.py:31-47)** — Correct. Backslash doubling (`.replace("\\","\\\\")`) runs FIRST; the two new `.replace("<","\\3C ")` / `.replace(">","\\3E ")` run LAST, so the escape's own backslash is not re-doubled. Verified the mapping: `\3C`=0x3C=`<`, `\3E`=0x3E=`>`, and the trailing space after each hex escape is the CSS whitespace terminator that is consumed (a real following space is preserved — test asserts `"a < b > c"` → `"a \3C  b \3E  c"`, two spaces). Independently reproduced the mutation: removing the `<` replace makes raw `</style>` reappear in the stylesheet; post-fix output contains no `</style>`/`<script>`; a bracket-free value is byte-identical (no-op).

2. **`_as_float` callers all handle None (formatting.py:24-32)** — Confirmed. `_as_float` is module-private; `grep` over `services/api/app` finds NO external caller. All in-module callers (`format_int_commas`, `format_ratio`, `format_sqft`, `format_feet`, `format_measure`, `whole_percent_shares`) guard `is None` and RETURN None — none raise. The added `inf/nan → None` path only widens an already-handled None contract. Mutation reproduced: without `math.isfinite`, `format_int_commas(inf)` raises OverflowError and `format_ratio(inf) == "inf.0"`; post-fix both return None.

3. **`format_number` callers pass finite reals (kit/labels.py:30-41)** — Searched every caller in `services/api/app`: furniture.py:88-89, scope.py:150, site_plan.py:202/242/261/381, massing.py:110, maps/close_frame_dimensions.py:181/254/255, maps/site_context_plan.py:385/444 (profile/.../dob_rows.py has its own unrelated `format_area`). All feed geometry/measurement values (edge lengths, yard depths, floor numbers, areas, heights, mapped widths) that are finite on valid data. The only NEW raise vs. old behavior is inf/nan (previously rendered `"inf"`/`"nan"` text; str/None already raised). Byte-identity of the kit/maps/cad suites (below) confirms no real fixture produces a non-finite input. The report-figure path (formatting.py) deliberately degrades to None/missing; the kit path fails closed by raising — intentional asymmetry, both honest.

4. **S10 selector scope (layout.py:198 `.evidence-column li { overflow-wrap: anywhere }`)** — The run-identity commit is emitted at page_evidence.py:119/125 as `div.evidence-column > ul > li`. `.evidence-column` occurs ONLY in page_evidence.py (appendix); the selector therefore touches only the three appendix columns. It is layout-neutral for the other two because `overflow-wrap:anywhere` wraps only an overflowing token and the flex columns carry `min-width:0` (neutralizing the min-content effect). Empirically confirmed layout-neutral (see PDFs).

5. **Tests (one per input state; mutations prove each guard)** — The three new files assert finite byte-identity AND non-finite/garbage fail-closed per input state. Mutation proofs are recorded in the producer report (per the packet's scenario text) and I reproduced all three independently. Adequate.

6. **ruff** — `ruff check` on the 3 changed prod files + 3 new test files: "All checks passed!"

7. **`modularity_check.py --check`** — exit 0, `selected 812 files; failures 0; warnings 33`; none of the 3 changed files flagged (layout.py 206, formatting.py 112, labels.py 92 lines; +a handful each, no threshold crossed). S9 satisfied.

8. **Test runs (scratch copy, under `flock heavy-run.lock`)** — `tests/drawings/report` + `tests/drawings/kit` + the 3 new files: **699 passed, 1 failed**, the single failure being `test_s9_presentation_contract_has_the_dated_entry` purely because `docs/design/ARCHITECT_PRESENTATION_CONTRACT.md` was absent from my partial checkout — it **passes** once extracted (1 passed). `tests/drawings/maps` + `tests/cad`: maps green; the 9 cad failures were all `FileNotFoundError` on un-extracted golden `docs/samples/cad/*` — after extracting them the full `test_cad_owner_samples.py` is **10 passed**. So all required + adjacent suites are green with no snapshot edited (S8). Note: test_report_benchmark strips `<style>…</style>` (line 51) before asserting, which is why the added CSS rule does not move any benchmark snapshot.

9. **Real-preview byte-identity (orchestrator-captured PDFs/HTML)** — `print-23aeeff5/report.pdf` = **10 pages** with the 40-char commit set; `print-main-86a450d4/report-with-commit-8-pages.pdf` = 8 pages (the defect). Per-page `pdftotext` diff of main-commit-unknown (10pg) vs this head (10pg): pages 1-9 byte-identical; page 10 differs only in run-identity — the document fingerprint (`efb2e8145ae6`→`5dfbaac4c427`, the pre-existing run-to-run non-determinism explicitly handled elsewhere, not this task) and the commit line, now wrapped across lines. `<style>` diff of main's 8-page HTML vs this head's HTML is **exactly** the one `.evidence-column li { overflow-wrap: anywhere }` rule + comment — nothing else moved. S10 confirmed.

## Finding

1. **ADVISORY** — `kit/labels.py:35-40`: `format_number` now RAISES ValueError on inf/nan (previously printed `"inf"`/`"nan"`), while the report formatters degrade to missing. On valid data this path is unreachable (kit/maps/cad suites byte-identical), and failing loud on a degenerate geometry value is defensible fail-closed. Suggested (non-blocking): confirm the drawing-render caller surfaces a non-finite value as a handled error rather than an unhandled 500 of the whole report. No correction required for this task.

## What I could not check
- I did not run Chromium/Playwright myself (read-only; ports 3000/3001/8000 are the owner's). I inspected the orchestrator-captured preview PDFs/HTML directly (page counts, per-page text, stylesheet diff) — the intended division of labor.
- I did not run the full api suite; the 4 pre-existing orphan-calculation-page failures are out of scope per the brief.
- The document-fingerprint run-to-run non-determinism is explicitly investigated separately.

END-OF-REPORT

## G4 (qa-engineer)

G4 QA GATE REPORT — M5-T189 (report/figure rendering hardening; DB-277, DB-278, DB-280/S10)
Reviewer: qa-engineer, independent, read-only. I am an AI agent; this is not a human or professional review. Reviewed at the pinned frozen SHA 23aeeff5d2af48e584661d79e19aa265387eb203 (parent dc8449d1) on task/wave28-placement-wiring, via `git archive` copies under /tmp/claude-0/review-t189-g4. I did not produce this task.

VERDICT: PASS (1 ADVISORY; no REQUIRED defect).

CONTENT IDENTITY — the 7 changed files' LF sha256 all match the builder return exactly (layout.py 04e7ae8e, formatting.py ab7d544a, kit/labels.py 6ffd21f5, + 3 test files + producer report). Change set = exactly the 7 allowed_paths files (+440/-8); no forbidden/snapshot/benchmark-test file touched; close_frame_dimensions.py is byte-identical to parent (NB-04 respected).

WHAT I CHECKED (reproduced, lanes venv, -p no:cacheprovider, heavy runs under flock):
1. New tests: the 3 new files → 15 passed, exit 0.
2. Whole api suite at the reviewed head: `pytest -q` → 10081 passed, 8 skipped, exit 0 (502s). The 4 prior "orphan calculation page" failures the builder saw at its claim head are GONE here (10077+4=10081) — the parent dc8449d1 removed the contract placeholders, exactly as the brief's "known/handled elsewhere" note said. tests/drawings and tests/cad are included and green; no snapshot file is in the diff (byte-identity proof S8).
3. Independent mutation proofs (revert each guard in my copy → targeted tests fail → restore to exact head hash):
   • Guard 1 CSS (removed the <,> replaces): test_report_css_escaping → 4 failed / 2 passed; raw `</style>` re-appears; the byte-identity no-op test and the S10 test still pass.
   • Guard 2 formatting (return result unconditionally): test_report_formatting_hardening → 3 failed / 2 passed; direct probe: format_int_commas(inf)=OverflowError, format_ratio(inf)=='inf.0' (reproduces T169-G5 F2).
   • Guard 3 labels (removed fail-closed if): test_labels_format_number → 3 failed / 1 passed; probe: format_number(inf)=='inf', format_number('abc') raises the cryptic "Unknown format code 'f' for object of type 'str'" (reproduces T188-G5 advisory).
   • Guard 4 S10 (removed the rule): test_evidence_column_list_item_breaks_a_long_commit fails. All three source files confirmed restored to the head LF sha256.
   Direct probe also confirms S1/S2: _css_string('Results revision 3') returns it verbatim (no-op); a `</style><script>` payload → `\3C /style\3E …`, no raw `</style>` in report_css.
4. Byte-identity (TestClient POST /report, benchmark_provider(with_zoning_lot=True, street_on=True) + recorded_pack_provider(window pack)), built at parent dc8449d1 and head 23aeeff5: after normalizing the fingerprint, head-vs-parent differs by EXACTLY the one S10 CSS block (the comment + `.evidence-column li { overflow-wrap: anywhere; }`) and nothing else — the 3 guards change zero bytes of the valid benchmark document. Two head runs are identical except the Document fingerprint (2903fa408f11 vs e88af0a299ae), so the fingerprint IS non-deterministic run-to-run (pre-existing, not from this CSS task; out of scope, already flagged DB for backlog).
5. Print (orchestrator-captured real-preview PDFs; I verified, did not re-render): main commit-unknown = 10 pages; main code + 40-char commit set = 8 pages (defect reproduced); head 23aeeff5 + commit set = 10 pages (fix). diff_pages.py main(10pp) vs head(10pp): pages 1–9 IDENTICAL text; page 10's only differences are the Document fingerprint and the Code-commit line, which now wraps inside the evidence column (…661d7 / 9e19aa26…) instead of overflowing and shrinking the whole report. Matches S10 exactly: 10 pages with the commit set, text identical to main apart from the commit line and the fingerprint.
6. Modularity: tools/modularity_check.py --check (scratch git index) → exit 0, failures 0, warnings 33, none of them M5-T189's three files.
7. Directive D-094-R054 (obligation: keep missing data / incomplete software honest, no repeated "not yet" prose): functional evidence supports it — non-finite/garbage values now degrade to "missing" (honest) instead of printing "inf.0"/"inf sq ft", and output stays byte-identical (no new prose). The authoritative requirement-by-requirement pass belongs to the separate directive-compliance-verifier gate (in reviewer_agents).

All ten acceptance scenarios (S1–S10) independently reproduced.

FINDINGS:
F1 — ADVISORY (record accuracy only; not a code defect). project-control/reports/M5-T189-producer-report.md, "Mutation proofs", Guard 1: records the CSS mutation as "4 failed, 1 passed". At the final file content the same revert yields 4 failed, 2 passed — the extra pass is test_evidence_column_list_item_breaks_a_long_commit, the S10 test added later by scope correction 1 (the mutation was evidently run before that test existed). No effect on correctness; the guard is load-bearing exactly as claimed. Concrete correction: restate as "4 failed, 2 passed (final content)" or note the mutation predates the S10 test. Does not block acceptance.

WHAT I COULD NOT CHECK:
- Live POST /report over a real server/port (read-only; ports 3000/3001/8000 are the owner's preview) — used in-process TestClient, the documented method.
- Playwright re-rendering of the PDFs (no apps/web/node_modules in the archive; read-only); I verified the orchestrator's captured PDFs and reproduced page counts via pdfinfo/pdftotext. Pixel-scale equality beyond "10 pages, pages 1–9 text-identical" not separately measured.
- e2e/web and full security/dependency gates — CI's job at the accepted head.
- Per-requirement directive derivation — the directive-compliance-verifier's gate.

No REQUIRED correction. The three guards are fail-closed and byte-identical on valid documents; the S10 rule restores the 10-page print with the commit set; regressions clean.
END-OF-REPORT

## G5 (security-reviewer)

G5 SECURITY GATE REPORT — M5-T189 (report/figure rendering hardening; DB-277, DB-278, S10/DB-280)

Reviewer: security-reviewer — independent, read-only AI agent. This is NOT a human or professional review. Pinned SHA 23aeeff5d2af48e584661d79e19aa265387eb203 on task/wave28-placement-wiring; /root/project/w-wave20 is currently AT that SHA with a clean tree on the reviewed paths (verified: HEAD==23aeeff5, `git diff --stat 23aeeff5 HEAD` on the 7 files is empty). Probes run with the lanes venv against a `git archive 23aeeff5` copy under /tmp/claude-0/review-t189-g5.

VERDICT: PASS. All three prior findings are closed; no REQUIRED defect. One minor ADVISORY (pre-existing, out of scope).

=== WHAT I VERIFIED (reproduced, real committed code) ===

1. F1 CLOSED (return-T169-G5 F1, </style> breakout — layout._css_string). The guard adds `.replace("<","\\3C ").replace(">","\\3E ")` AFTER the backslash doubling. Executing the real `report_css`/`_css_string`:
   - `</style><script>alert(1)</script>` → `\3C /style\3E \3C script\3E …` — no `</style>`, `<script>`, `</script>`, and NO raw `<`/`>` anywhere.
   - Case/space variants `</STYLE>`, `</Style >` → neutralized (HTML end-tag matching is case-insensitive but every `<` is gone).
   - Backslash-before-bracket `\<` → `\\\3C ` (backslash doubled first, the hex-escape backslash correctly NOT doubled) — renders `\<`, no breakout.
   - Newline + `</style>` → newline→space then escaped.
   - CSS-comment/brace injection `/*x*/ } body{display:none}` → passes through unchanged and is HARMLESS: it sits inside `content:"…"` (a quoted string), so `{`/`}` are literal, `"` is escaped — no CSS rule injected.
   - Pre-formed hex `\3C /style\3E ` → backslashes doubled → literal `\\3C` text, never a `<`.
   - Unicode look-alikes `‹/style›` (U+2039/U+203A) → unchanged and harmless (not U+003C/003E, so no HTML tag).
   Full `report_css(hostile_header, hostile_footer)`: no `</style>` substring, no raw `<`/`>`. Header and footer are the ONLY document-derived strings in the `<style>` block; all other interpolations are COLOR/TYPE token constants (trusted). Confirmed sole caller is builder.py:105. New test test_report_css_escaping.py pins header + footer breakout, the byte-identical no-op, the S10 rule, and the backslash-ordering edge.

2. F2 CLOSED (return-T169-G5 F2, non-finite figure formatting). `_as_float` now returns None for non-finite. Executed report formatting: inf/-inf/nan → None for format_int_commas/format_ratio/format_sqft/format_feet (no OverflowError, no 'inf.0'/'nan.0'); bool True/False → None; 'abc'/None → None. whole_percent_shares: [inf,1.0]→None, [nan,1.0]→None, [1.0,3.0]→[25,75]. Finite values byte-identical (20150.0→'20,150'; 6716.6666→'6,716.67'; 2.0 ratio→'2.0'; 144.6→'144.60 ft').

3. T188 ADVISORY CLOSED (kit/labels.format_number). Executed: inf/-inf/nan/'abc'/None/True/False → all raise ValueError (fail closed); finite unchanged (-0.0→'0', 1234.5→'1,234.5', 2.0→'2'). This also covers close_frame._fact_figure via the call path with NO edit to the NB-04-pinned close_frame_dimensions.py (diff touches only the 7 allowed files; forbidden paths untouched).

4. S2 byte-identity: the two new replaces are a no-op for every angle-bracket-free run-identity value ('Results revision 3', 'computed 2026-10-15', addresses) — _css_string output is identical to the pre-change escaping.

5. S8 byte-identity reconciled: the benchmark test's visible_text() strips the whole `<style>…</style>` block before counting, so adding one CSS rule is invisible to the word-budget/repeat assertions — that is why the benchmark stays green with no snapshot edited. No report test pins the raw stylesheet; the only valid-document HTML change is the intended `.evidence-column li { overflow-wrap: anywhere; }` block. SVG/DXF/kit/maps snapshots are unaffected (format_number changes only non-finite/non-numeric inputs, absent from valid fixtures).

6. S10 cannot hide/truncate: `overflow-wrap: anywhere` only introduces soft break opportunities inside an otherwise-unbreakable token; there is no `overflow:hidden`/`text-overflow`/clipping companion, and it is scoped to `.evidence-column li`. No content is hidden or truncated; it only lets the 40-char commit wrap.

7. No new attack surface: the diff adds only `import math` (formatting.py); labels already imported math; layout adds no import. No network/file/env/subprocess/eval/exec added. No dependency/lockfile touched. Run-identity env/commit handling (run_identity.deployed_commit) is unchanged (not in the diff), so service-role secrecy and the 'unknown'-unless-hex-git-id fail-safe stand. No auth, storage, RLS/cross-tenant, upload, SSRF, or LLM-prompt surface is touched by this change — those dimensions are N/A to this diff.

8. Other stylesheet/raw-HTML sinks swept (report package): every raw()-emitted fragment escapes its document text (escape()/escape_attr()); SVG embeds in drawings_embed go through xml.sax.saxutils.escape (name_s/status_s/value_s); the only unescaped raw interpolation, components.answer_block value_text, has NO importer in the report package (not a reachable sink). No other untrusted document text reaches the `<style>` block.

=== FINDINGS ===
A1 — ADVISORY (pre-existing, NOT a T189 regression, out of DB-277/DB-278 scope). A FINITE but extreme value (e.g. 1e308) passes math.isfinite and renders as a ~309-digit string in both report formatting (format_int_commas/sqft/feet/ratio) and kit format_number. Not a crash and not an injection (digits only; in the evidence column the S10 rule wraps it). Upstream the results contract and map adapter (MAX_ABS_COORD_FT=1e8) bound document values, so this is not reachable with validated input. No action required for this gate; optionally track a magnitude cap in formatting. File: services/api/app/drawings/report/formatting.py _as_float; services/api/app/drawings/kit/labels.py format_number.

=== WHAT I COULD NOT CHECK ===
- The task's three guard-test files via pytest: queued behind the heavy-run.lock (a parallel G4 full-suite run holds it); I did not wait. I instead executed the real committed functions in-process (stronger than a green test), reproducing every S1–S7 behavior above.
- The live 8-vs-10-page print (S10) end to end: no server/ports/Playwright (read-only rules). I verified the CSS mechanism and rely on the orchestrator's real-preview PDFs for the page-count evidence; the rule cannot hide content.
- Modularity (S9) and functional/visual byte-identity across the full suites: other reviewers' shares (code-architecture / qa / directive-compliance-verifier); the diff is net-small and splits nothing.

Security dimension of G5: PASS. All three latent fail-open/crash sinks (F1 </style> breakout, F2 non-finite crash, T188 non-numeric/non-finite) are closed and fail closed; valid-document output is byte-identical apart from the intended S10 CSS rule; no new attack surface. Only A1 is ADVISORY.
END-OF-REPORT

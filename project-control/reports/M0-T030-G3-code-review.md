<!-- Orchestrator note: code-reviewer return saved VERBATIM from the agent-return channel.
     Reviewed head baa09f87780057dc1c5cb29cd7a9f6caf9b4b170; recorded for gate G3 of M0-T030.
     Verdict PASS with blocking correction C1 (recorded per gate-verdict semantics: the
     correction is BLOCKING for the next gate and for acceptance). -->

# Gate Report

- Gate ID: G3 (code review)
- Task ID: M0-T030
- Reviewer: code-reviewer (independent, read-only)
- Producer: backend-engineer (worktree agent); benchmark evidence authored separately at `baa09f8`
- Result: **PASS — with 1 BLOCKING correction (C1) required before acceptance**
- Clean environment/worktree used: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T030-codegraph` at frozen SHA `baa09f87780057dc1c5cb29cd7a9f6caf9b4b170` (verified `git rev-parse HEAD`); branch has exactly two commits over base `613c4b1` (`9c95e12` implementation, `baa09f8` benchmark only)

## Acceptance criteria reviewed

| AS | Verdict | Evidence |
|---|---|---|
| AS-1 | PASS | `--check` completed in 2.3 s wall (budget 120 s); meta contains `source_fingerprint`, `generator_version` 1.0.0, `mode` code-only, `include_roots`, `exclude_dirs`, `node_counts`, `input_file_count` 235, and `edge_counts.by_language_confidence` — all reproduced from a fresh generation |
| AS-2 | PASS | `--check` PASS (two fresh generations byte-identical); artifacts contain 0 CR bytes, end in LF, 0 drive-letter tokens, 0 ISO-date-like strings; all collections sorted; `json.dumps(sort_keys=True)` with binary LF writes |
| AS-3 | PASS as written, with C1 caveat | Tests prove input-edit changes fingerprint; artifacts/excluded-trees/reports do not; CRLF-invariant. However `apps/web/tsconfig.json` is a generation input outside the fingerprint (Finding 1 / correction C1) |
| AS-4 | PASS | Sentinel test plants .py/.ts under 11 excluded trees incl. `.claude/worktrees`, `node_modules`, `.next`, `__pycache__`, `.pytest_cache`, `.venv`, `dist`, `build`, `coverage`, `.git`; none indexed; `exclude_dirs` recorded in meta (also `_quarantine`, `graphify-out`) |
| AS-5 | PASS | Live graph: 0 of 1,491 edges missing/invalid confidence; edge types exactly `{contract_ref, dynamic_import, import}` live (+`reexport` in fixtures) — no caller/callee type exists anywhere; all 9 unresolved edges inspected (3 CSS, 6 JSON fixture imports — honest blind spots, raw specifiers preserved); ambiguity path returns `unresolved`, never guessed (generate.py:216-219) |
| AS-6 | PASS | `--no-regen` on cold cache → `STALE`, exit 3; auto-regen prints one line then answers; `find e --limit 9999` → exactly 201 lines (200 + `...truncated (2707 more)`) — whole graph never dumpable; every edge line starts with repo-relative path:line (external nodes carry no path, by design) |
| AS-7 | PASS | 26/26 tests pass in 3.7 s; temp fixture repos only; stdlib-only enforced by an AST-enumeration test over all three files (`sys.stdlib_module_names` requires Python ≥3.10; CI ubuntu-latest python3 satisfies; local 3.11.9 verified) |
| AS-8 | PASS (local portion) | `git diff 613c4b1..HEAD -- .github/workflows/ci.yml` = 18 insertions, 0 deletions, one appended `code-graph` job; checkout SHA `34e11487…` identical to all 12 existing pins; no setup steps or third-party actions added; file parses as YAML. **Orchestrator must confirm the job is green on the task PR** (reviewer cannot run `gh`) |
| AS-9 | PASS at G3 scope | 18 frozen questions, per-question A/B table with ops/files/correct/complete/missed/false, overall scoring, zero token claims, timing omitted with documented reproducibility reason; honest negative finding (B used ~1.75x ops — no efficiency claim); correctness gate explicitly passes (B 18/18 vs A 15/18). Header state (`9c95e12`, fingerprint `18d461e2…`, 235 files, 2907/1491) matches my regeneration at head exactly (only the benchmark file differs between the two commits, and it is not a fingerprint input). Judge-independence is a process claim for G4/directive-compliance-verifier; two spot checks verified (below) |
| AS-10 | PASS | `git diff --stat 613c4b1..HEAD` = exactly the 7 allowed paths; no `.claude/**`, `.git/hooks/**`, product trees, or dependency manifests touched |

## Directive/requirement verification (D-005-R066..R089 at baa09f8)

| Req | Verdict | Reproduced evidence |
|---|---|---|
| R066 | PASS | Single controlled task packet covers generator + CI check + benchmark |
| R067 | PASS | No Graphify anywhere in diff (only the `graphify-out` exclusion name and packet prohibition) |
| R068 | PASS | No installs, no dependency-manifest changes, no downloads in code |
| R069 | PASS | Clarifications 1-10 embedded in packet (allowed_paths_note, risks, AS text) before implementation |
| R070 | PASS | Four-value confidence enforced at emit time (generate.py:661-662 raises on unlabeled); 0/1,491 violations live |
| R071 | PASS | No caller/callee edge type exists; test bans `call|caller|callee|invoke` substrings (test_code_graph.py:236-238) |
| R072 | PASS | Deferred by design; README states it |
| R073 | PASS | No committed artifact; `_assert_outside_repo` (generate.py:819-829) test-enforced; fingerprint excludes artifacts |
| R074 | **FAIL (narrow) → C1** | Fingerprint omits `apps/web/tsconfig.json`, which the generator reads for alias resolution — see Finding 1 with reproduction |
| R075 | PASS | Meta fields verified from fresh generation |
| R076 | PASS | CI job runs `--check` (two fresh generations, byte-compare); query recomputes fingerprint every invocation |
| R077 | PASS | Include-roots + name-based exclusion pruning; sentinel test incl. nested `services/api/node_modules` |
| R078 | PASS | Husks only excluded from traversal; diff touches nothing under `.claude/**` |
| R079 | PASS | Edge types limited to import/reexport/dynamic_import/contract_ref |
| R080 | PASS | `mode: "code-only"`; no properties/zoning/filings/plans in graph; project-control not an include root |
| R081 | PASS | No project-control graph built; benchmark ran without one |
| R082 | PASS | 9 bounded subcommands, source-locatable lines, deterministic sorted output |
| R083 | PASS | Hard cap 200 lines reproduced; no full-dump subcommand exists |
| R084 | PASS | README trust model with the mandatory-verification categories; repeated in query.py docstring and argparse description |
| R085 | PASS (G3 scope) | Benchmark content as under AS-9; no fabricated tokens; process independence to be confirmed at G4/verification.json |
| R086 | PASS | Verdict section explicitly refuses efficiency claim, scores correctness first, declares "NOT DEMONSTRATED" where unsupported |
| R087 | PASS | Reuses the house `--check` generator pattern (validate_product_map precedent); regenerable anywhere; CI-verifiable |
| R088 | PASS | Isolated additive diff; no other lane's files touched |
| R089 | PASS (not yet due) | Post-acceptance obligation: benchmark's correctness gate passed, so the owner decision packet is owed AFTER acceptance; nothing downstream was prematurely implemented in this diff. Orchestrator follow-up item |

## Steps independently executed (exact commands, worktree root, Python 3.11.9)

1. `git rev-parse HEAD` → `baa09f87780057dc1c5cb29cd7a9f6caf9b4b170`; `git log --oneline 613c4b1..HEAD` → 2 commits; `git diff --stat 613c4b1..HEAD` → 7 files, 2,272 insertions, all allowed paths
2. `python tools/test_code_graph.py` → **Ran 26 tests … OK**
3. `python tools/code_graph/generate.py --repo . --check` → **determinism check PASS: 2 generations byte-identical (235 input files, fingerprint 18d461e2910ab476)**, 2.3 s — fingerprint/counts match producer report AND benchmark header
4. `python tools/code_graph/generate.py --repo . --out <scratchpad>\g3out` → 235 files, 2907 nodes, 1491 edges; artifact inspection: 0 unlabeled edges; live edge types `contract_ref/dynamic_import/import`; by_confidence `{derived:259, exact:1220, partial:3, unresolved:9}` = meta tallies = producer report; 0 CR bytes; no drive letters; no date strings; trailing LF
5. `CODEGRAPH_CACHE_DIR=<scratch> python tools/code_graph/query.py --repo . --no-regen find CoverageBadge` → `STALE`, exit 3; then `downstream services/api/app/profile/builder.py` → `regenerated (stale fingerprint)` + 9 lines byte-matching the producer report; source spot-check `sed -n '59,63p' services/api/app/api/v1/properties.py` confirms line 61 is `from app.profile.builder import build_property_profile`
6. `query.py --limit 9999 find e | wc -l` → 201 (hard cap + truncation, 2707 suppressed); `contracts property_profile | wc -l` → 40 (matches producer's "exactly 40")
7. tsconfig-gap reproduction (temp fixture only, via the suite's own `build_fixture_repo`): edit fixture `apps/web/tsconfig.json` alias target → `fingerprint changed: False`, `graph bytes changed: True`, aliases `apps/web/src/` → `apps/web/somewhere-else/`
8. `python -c "import yaml…"` → ci.yml parses OK; checkout-pin grep → 12 identical existing pins
9. Benchmark spot-check: `services/api/app/rules/__init__.py` lines 15-20 show the direct `evaluator` re-export the Q17 judge note cites

## Defects / findings (numbered, severity-tagged)

1. **MEDIUM — BLOCKING (C1). Generation input excluded from the freshness identity.** `tools/code_graph/generate.py:416-446` (`_load_ts_aliases`) reads `apps/web/tsconfig.json` to resolve `@/` aliases, but `compute_source_fingerprint` (generate.py:149-158) hashes only the indexed source set. Reproduced (step 7): editing tsconfig `paths` changes graph bytes while the fingerprint is unchanged, so `query.py` (`load_graph`, query.py:52-72) would report a cached pre-change graph as FRESH — one narrow channel where stale data is presented as current, contradicting the packet output spec ("stale data can never be presented as current", M0-T030.json line 17) and D-005-R074 ("fingerprint over the exact canonical inputs used to generate"). The `build_graph` docstring "Pure function of the input file bytes" (generate.py:682) is also inaccurate. **Required correction C1:** include `apps/web/tsconfig.json` bytes (CRLF-normalized, when present) — or the computed alias table — in the fingerprint hash, add a fixture test (tsconfig edit ⇒ fingerprint changes; tsconfig absent ⇒ stable), and fix the docstring. AS-3's "artifacts/excluded/report files never change it" invariants must keep passing.
2. **LOW (advisory).** Python absolute-import resolution tries importer-directory siblings first and a cross-root key union second (generate.py:207-220); single-segment keys from top-level files (e.g. `tools/*.py`) can yield a unique-but-wrong `exact` internal edge when runtime `sys.path` differs from the heuristic. Correct for this repo's observed imports (spot-checked), but the hazard is absent from README's blind-spot list — suggest documenting or downgrading sibling/cross-root hits to `derived`.
3. **LOW (advisory).** TS extraction is string-naive: a literal containing `from '…'` inside a buffered `import`/`export` statement can emit a false `exact` edge (generate.py:549-563); README discloses string-naive comment scrubbing but not this case. Also, an export-brace list spanning >40 lines/4,000 chars is silently dropped (generate.py:611-616) — missing symbols only, never false edges.
4. **LOW (test gaps).** No fixture test for: (a) the ambiguous-dotted-specifier ⇒ `unresolved` branch (generate.py:216-219), (b) the tsconfig-missing/unparseable alias fallback (generate.py:444-446), (c) meta `by_language_confidence`/`include_roots` presence (AS-1 fields). All verified by review and live run instead; recommend adding alongside C1's test.
5. **INFO.** `--limit` must precede the subcommand (global flag, query.py:356) — already self-reported as benchmark finding 5; non-blocking usability item.
6. **INFO (G5 advisory re-assessment — none G3-blocking).** (a) graph.json not hash-bound in meta: write order in `generate_into` (graph.json before graph.meta.json, generate.py:836-839) makes torn writes self-heal via fingerprint mismatch; residual corruption yields a loud traceback, not silent wrong data — concur LOW/advisory. (b) cache key by repo basename: collisions only cause regeneration churn because the fingerprint is recomputed every invocation — concur INFO. (c) symlink readability and (d) `load_graph` OSError handling — concur INFO; none blocks G3.

## Required rework (blocking for acceptance)

- **C1** as specified in Finding 1 (fingerprint must cover `apps/web/tsconfig.json` or the derived alias table; fixture test; docstring fix). Everything else in this review is non-blocking.

## Reviewer conclusion

Implementation quality is high: determinism, LF discipline, honesty labels, exclusions, bounded queries, stdlib-only, additive CI, and isolation all reproduce exactly from the frozen SHA; producer-report numbers were re-derived, not trusted; the benchmark is honest to the point of reporting an unfavorable efficiency result. The single reproducible defect is the tsconfig freshness gap (C1) — narrow in practice, but it dents the tool's central "staleness is detected, never trusted" invariant and D-005-R074, and the fix is a few lines plus a test.

**Verdict: PASS with required corrections — C1 is BLOCKING for the next gate and for acceptance** (per the recorded gate-verdict semantics). Orchestrator to additionally capture: CI `code-graph` job green on the task PR (AS-8 remote half), and the R089 owner decision packet as a post-acceptance follow-up.

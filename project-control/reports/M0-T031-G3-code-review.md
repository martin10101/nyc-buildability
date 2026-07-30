<!-- Orchestrator note: code-reviewer return saved VERBATIM from the agent-return channel.
     Reviewed head 1891ef3f886c7ba65413ddd9727b5a596c8e705a; recorded for gate G3 of M0-T031.
     Verdict PASS, zero blocking findings (Finding 1 LOW offered as optional rework only). -->

All verification complete. Here is the gate report.

---

# Gate Report

- Gate ID: G3 (code review)
- Task ID: M0-T031
- Reviewer: code-reviewer (independent, read-only)
- Producer: backend-engineer
- Result: **PASS**
- Clean environment/worktree used: yes — `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T031-codegraph-hardening` at frozen HEAD `1891ef3f886c7ba65413ddd9727b5a596c8e705a` (verified `git rev-parse HEAD`; `git status --porcelain` clean), base `cc273b5`.

## Acceptance criteria reviewed

AS-1 through AS-9 from `project-control/tasks/M0-T031.json`, plus the specific review scope assigned by the orchestrator (write-order/verify-on-load semantics, cache key, `--limit` argparse, determinism, fingerprint untouched, 7 new tests, guidance-diff discipline, dict-or-None nit). Full delta reviewed: `git diff cc273b5..1891ef3` = exactly 7 files (generate.py, query.py, README.md, test_code_graph.py, CLAUDE.md +1/-0, SKILL.md +3/-0, producer report), all inside `allowed_paths`; `.github/` diff is empty (0 lines).

## Directive/requirement verification

Reviewed at SHA `1891ef3f886c7ba65413ddd9727b5a596c8e705a`, re-derived from `project-control/directives/D-005-codebase-knowledge-graph-pilot/source-003-amendment.md`. (The full regime pass is the directive-compliance-verifier's lane; below is my independent G3 verification of every row in the amendment-2 range.)

| Requirement ID | Reviewed SHA | Verdict | Reproduced evidence |
|---|---|---|---|
| D-005-R090 | 1891ef3 | PASS | Owner-acceptance statement; downstream obligations verified in R091–R110. |
| D-005-R091 | 1891ef3 | PASS | README.md 73–80: correctness/completeness/fewer-false-claims stated as the only proven benefit; savings explicitly disclaimed. |
| D-005-R092 | 1891ef3 | PASS | Grep of delta for `graph-first|always use|mandatory graph|token|time sav|faster|saves` matched only the two disclaimers ("not universal graph-first", "No token or time savings are claimed"). |
| D-005-R093 | 1891ef3 | PASS | Task contracted as M0-T031 under normal control plane (packet + PR #116 at base). |
| D-005-R094 | 1891ef3 | PASS | All four hardening items verified below (write-order/hash-bind; realpath cache key; OSError/ValueError handling; stdlib-only — `test_generator_query_tests_import_stdlib_only` still green, no new imports beyond stdlib `hashlib`/`json`). |
| D-005-R095 | 1891ef3 | PASS | Delta confined to the 4 existing code-graph files + 2 contemplated guidance surfaces + report; no new platform surface. |
| D-005-R096 | 1891ef3 | PASS | SKILL.md added paragraph: "Graph use is never required on every task"; README: "Graph use is NEVER required on every task." |
| D-005-R097 | 1891ef3 | PASS | Decision model (materially useful? YES→graph→narrow→source verification; NO→direct navigation) present in README (verbatim block) and SKILL.md paragraph. |
| D-005-R098 | 1891ef3 | PASS | README names all 9 SHOULD-prefer cases verbatim. SKILL.md paragraph condenses to 7 of 9 — see Finding 1 (LOW, non-blocking; paragraph links to README). |
| D-005-R099 | 1891ef3 | PASS | All 5 NOT-mandatory cases present in both README and SKILL.md paragraph. |
| D-005-R100 | 1891ef3 | PASS | Decision model encoded in both surfaces, faithful to source-003 lines 64–71. |
| D-005-R101 | 1891ef3 | PASS | No token/time-savings claim anywhere in the delta (grep evidence above); README carries the explicit disclaimer + "any such claim requires new evidence". |
| D-005-R102 | 1891ef3 | PASS | Guidance routes simple/local cases to direct navigation; graph reserved for relationship-material cases. |
| D-005-R103 | 1891ef3 | PASS | "advisory in every case … graph → likely locations → actual source verification, never graph → assumption" (README); "advisory only, and material conclusions must be verified in the actual source" (SKILL.md); CLAUDE.md row says "selective, advisory". |
| D-005-R104 | 1891ef3 | PASS | Fingerprint logic byte-untouched (generate.py diff = exactly 3 hunks: version, `default_out_dir`, `generate_into`; grep of diff for `CONFIG_INPUTS|compute_source_fingerprint|FINGERPRINT` = 0 lines). Fingerprint still recomputed FIRST every invocation (query.py:105). |
| D-005-R105 | 1891ef3 | PASS | No `.git/hooks`, `.claude/hooks`, watcher, or scheduler in the delta. |
| D-005-R106 | 1891ef3 | PASS | Cache keyed per-checkout realpath; no cross-branch graph merging introduced; symlinked duplicates of the same checkout correctly collapse to one namespace. |
| D-005-R107 | 1891ef3 | PASS | `git diff cc273b5..1891ef3 -- .github/` = 0 lines; no CI/security-process change. |
| D-005-R108 | 1891ef3 | PASS | Exactly the two contemplated guidance surfaces: CLAUDE.md numstat 1/0 (one table row); SKILL.md numstat 3/0 (one paragraph + surrounding blank lines). Both purely additive. |
| D-005-R109 | 1891ef3 | PASS | No Mission Control / layer-B / six-PRD / evidence-KG / Graphify / Agent-Teams-injection surface in the delta. |
| D-005-R110 | 1891ef3 | PASS (orchestrator lane) | Lifecycle handling is orchestrator authority; packet is in normal lifecycle (`in_progress`, gates G0/G3/G4/G5 required). |

## Steps independently executed

All from worktree root, cache artifacts written only to the session scratchpad (outside the repo):

1. `git rev-parse HEAD` → `1891ef3f886c7ba65413ddd9727b5a596c8e705a`; `git status --porcelain` → clean.
2. `python tools/test_code_graph.py` → **Ran 36 tests in 7.157s — OK** (base had 29 `def test_`, head has 36 → exactly 7 new).
3. `python tools/code_graph/generate.py --repo . --check` → **determinism check PASS: 2 generations byte-identical (235 input files, fingerprint 21aa77fb90376adc)** — matches the expected fingerprint.
4. `python tools/context_budget_check.py` → **PASS** with the CLAUDE.md row added.
5. Manual `--limit` reproduction: `query.py --repo . find project_control --limit 2` (post-subcommand) works; `--limit 5 find project_control --limit 2` → 2 result lines + truncation notice (subcommand value wins); cold cache printed the unchanged `regenerated (stale fingerprint)` message.
6. Manual tamper reproduction: flipped one mid-file byte in the cached `graph.json`; `--no-regen` → `STALE (cache integrity): refusing to serve the cached graph`, exit 3, zero result lines; without `--no-regen` → `regenerated (cache integrity)`, exit 0, correct results. No traceback either way. Cache dir observed with new key format `ef435abbcd93-M0-T031-codegraph-hardening`.
7. Manual pre-1.1.0-cache reproduction: deleted `graph_sha256` from a valid meta; `--no-regen` → exit 3 refuse; normal run → `regenerated (cache integrity)`, exit 0. Old 1.0.1 caches auto-upgrade safely.

## Expected versus actual

All expected outcomes met: 36/36, determinism PASS at fingerprint `21aa77fb90376adc`, context budget PASS, all failure-path behaviors as specified.

## Evidence paths

- Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M0-T031-codegraph-hardening`
- Reviewed files: `tools/code_graph/generate.py`, `tools/code_graph/query.py`, `tools/code_graph/README.md`, `tools/test_code_graph.py`, `CLAUDE.md`, `.claude/skills/start-controlled-task/SKILL.md`, `project-control/reports/M0-T031-producer-report.md` (treated as claims; independently reproduced)
- Directive source: `project-control/directives/D-005-codebase-knowledge-graph-pilot/source-003-amendment.md`, `requirements.json` rows R090–R110

## Human-style walkthrough findings

N/A (no UI). CLI walkthrough covered in steps 5–7.

## Regression/security/provenance findings

Assigned review-scope verification, all confirmed correct:

- **Write-order/verify-on-load (generate.py:858–872, query.py:60–125).** Order is: serialize graph → write `graph.json` → hash the exact written bytes → write meta containing the hash. Interruption between the two writes fails safe: an old/absent meta yields stale-fingerprint or hash-mismatch on next load → regenerate. Partial `graph.json` writes fail the hash check. Hash is verified against on-disk bytes *before* JSON parse, so an altered cache is never parsed, let alone served. `--no-regen` refuses with one line + exit 3 on every failure class. The regen path re-verifies after rebuild (query.py:121–124) and exits 3 with one line if still unusable — no infinite loop, no traceback. `generate_into` OSError during rebuild → one-line `cache regeneration failed (...)` + exit 3 (query.py:117–119); `_assert_outside_repo` raises `SystemExit` with a message (also traceback-free). Cold-cache path byte-for-byte preserves the pre-existing `regenerated (stale fingerprint)` message contract; the pre-existing stale tests are unmodified in the diff and still pass.
- **Cache key (generate.py:822–842).** `sha256(realpath(repo_root))[:12] + "-" + basename` applied uniformly across all three fallback locations. Deterministic per machine/path (query.py abspaths `--repo` first; realpath canonicalizes case for existing paths on Windows and normalizes trailing separators); symlink aliases of one checkout share one namespace (correct — same fingerprint); same-named checkouts at different paths get distinct namespaces (fixture test + observed live). Key affects only the cache *directory name*, never artifact bytes, so determinism/byte-identity is unaffected — confirmed by `--check` and `test_determinism_two_generations_byte_identical` which now covers the meta with `graph_sha256`.
- **`--limit` dual position (query.py:409–425, 442).** The distinct `dest="limit_sub"` (default `None`) is the correct fix for argparse's subparser-default-clobbers-global behavior; precedence (subcommand wins) verified by test and manual run; `emit` clamp (1..HARD_CAP 200, default 40) untouched; hard cap tested in the post-subcommand position.
- **Fingerprint untouched.** generate.py diff contains exactly 3 hunks, none touching `CONFIG_INPUTS` (generate.py:149), `FINGERPRINT_ALGORITHM` (151), `_fingerprint_entry` (160), or `compute_source_fingerprint` (167); grep of the diff for those symbols = 0 matches; live fingerprint matches the expected `21aa77fb90376adc`.
- **Determinism.** No timestamps or absolute paths added to artifacts; `graph_sha256` is a pure function of the graph bytes; `GENERATOR_VERSION` correctly bumped 1.0.1 → 1.1.0 for the meta-semantics change.
- **7 new tests — good quality.** Tamper test uses XOR 0xFF (guaranteed byte change), asserts message, no traceback, correct answer, AND that the cache holds the original bytes again (determinism-backed proof the altered content is gone); the directory-in-place trick for the OSError test is genuinely cross-platform (IsADirectoryError on POSIX, PermissionError on Windows — both OSError) and additionally covers the regeneration-failure branch; the cache-key test checks both separation and end-to-end population; the `--limit` test checks positional equivalence, precedence, and the hard cap. `cache_out_dir` env mutation is restore-safe (`finally`).
- **dict-or-None nit (assigned).** `_read_cache_attempt` (query.py:60–100) is the only dict-or-None helper; its sole caller is `load_graph`. Runtime-safe by construction: it returns a graph only after `isinstance(graph, dict)` (query.py:98–100), and non-None graph iff reason is None; both `return graph` sites (query.py:111, 125) are gated on the reason check. Pyright would still flag `dict | None` vs the declared `-> dict` because the tuple type doesn't encode the correlation — static nit only, see Finding 4. Downstream, `GraphIndex` subscripts `graph["nodes"]`/`graph["edges"]` on a hash-verified generator-produced artifact, so KeyError is unreachable for cached loads.

## Defects

Numbered, severity-tagged. **None are blocking.**

1. **LOW — SKILL.md SHOULD-prefer list omits 2 of the owner's 9 cases.** `.claude/skills/start-controlled-task/SKILL.md:14` (added paragraph) names 7 graph-preferred cases but omits "contract-change impact" and "unfamiliar subsystem orientation where dependencies are unclear" (source-003-amendment.md:44–54). Non-blocking because: the paragraph links to `tools/code_graph/README.md`, which carries all 9 verbatim (AS-7/R098 satisfied by the guidance set as a whole); the omission contradicts nothing and errs toward *less* graph use, consistent with the owner's anti-overreach condition. Flagged for the directive-compliance-verifier to weigh independently; "contract-change impact" is the notable omission in this contract-heavy repo. Optional rework: add the two missing items to the SKILL.md paragraph (still one paragraph).
2. **INFO — module docstring slightly overstates the "cache integrity" class.** `tools/code_graph/query.py:14` says "a missing/corrupt/unreadable artifact … prints 'regenerated (cache integrity)'", but a *cleanly missing* meta or graph file yields `regenerated (stale fingerprint)` by design (query.py:73–74, 84–85 — the preserved cold-cache contract). The helper docstring (query.py:65–71) and README §Cache integrity are precise; only the headline is loose. Doc nit.
3. **INFO — no fixture test for the missing-`graph_sha256` (pre-1.1.0 cache) path.** Handled at query.py:91–93 and reproduced manually (refuse exit 3 / `regenerated (cache integrity)`), but not pinned by a test. Not required by AS-1..AS-4; suggested for a future hardening pass.
4. **INFO — Pyright-style `dict | None` return.** `_read_cache_attempt`'s tuple type cannot statically prove `graph is not None` when `reason is None`, so query.py:111/125 type as `dict | None` against `load_graph -> dict`. Runtime-safe (see above); no repo type-check gate is affected. No change required.
5. **INFO — TOCTOU edge fails safe rather than retrying.** If sources change between the fingerprint computation (query.py:105) and the in-process regeneration (query.py:116), re-verification fails with `cache unusable even after regeneration (stale fingerprint)` + exit 3 instead of retrying with a fresh fingerprint. Never serves wrong data; acceptable.
6. **INFO — pre-existing, unchanged:** `compute_source_fingerprint` at query.py:105 can raise uncaught OSError if a *source* file vanishes mid-scan. Outside the mandated hardening scope (cache/meta reads); unchanged from the accepted M0-T030 implementation.

## Required rework

None blocking. Finding 1 is offered as optional rework at orchestrator/directive-verifier discretion.

## Reviewer conclusion

**PASS.** All four owner-mandated hardening items are correctly implemented and well tested; every cache failure path (tamper, corrupt meta, OSError, missing hash, missing files) regenerates or exits 3 without ever serving altered data or leaking a traceback; the cold-cache message contract is preserved; the fingerprint algorithm is byte-untouched; determinism holds (`--check` PASS at the expected fingerprint `21aa77fb90376adc`); `--limit` works in both positions with unchanged caps; the two guidance diffs are purely additive, strictly selective, and claim no token/time savings; the delta touches only allowed paths with CI byte-untouched. 36/36 tests and the context budget check pass, independently reproduced.

# Gate Report (DELTA re-review)

- Gate ID: G4 (QA) — delta re-review, rework 1
- Task ID: M0-T043 — Bounded context-pack builder (AD-044..AD-046; 0A.4 budgets)
- Reviewer: qa-engineer (independent; read-only)
- Producer: backend-engineer
- Result: **PASS**
- Reviewed content identity: rework commit `e41dad3`. Worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T043-context-pack`, HEAD `52c3813`. Verified `git diff --name-only e41dad3 52c3813` touches only control-plane files (`project-control/reports/M0-T043.json`, `state.json`, `tasks/M0-T043.json`); the three under-test files (`tools/context_pack.py`, `tools/test_context_pack.py`, `docs/CONTEXT_PACKS.md`) are byte-identical at HEAD vs `e41dad3`. Rework commit `e41dad3` (parent `5e9336e`) touched only the 3 allowed files + orchestrator-owned control-plane; forbidden-path scan (`tools/agent_supervisor/`, `.claude/`, `apps/`, `services/`, `.github/`) empty. All probe outputs under `%TEMP%/…/scratchpad/t043/` only; no repository file edited.

## Delta scope

Re-verifies the single defect that governed rework — G3 **F1** ≡ G4 **D-1** (overflow/bound decision undercounted the emitted `context.md` by the whole footer, so near-bound builds emitted over-bound packets at exit 0) — plus producer's collateral fixes F2/F3/F4/F5/F6. First-pass PASS probes that are unaffected by the diff are not re-run; the delta focuses on the bound-enforcement contract and determinism through the new footer-aware fixpoint.

## Per-item results (1–8)

### 1. Suite — both runners, twice each; flake; drift RAN not skipped — **PASS**
```
python --version                              -> Python 3.11.9
python tools/test_context_pack.py    (run 1)  -> Ran 15 tests in 15.180s  OK
python tools/test_context_pack.py    (run 2)  -> Ran 15 tests in 15.866s  OK
python -m pytest -q .../test (run 1)          -> 15 passed in 16.14s
python -m pytest -q .../test (run 2)          -> 15 passed in 16.03s
pytest -k drift -v                            -> 3 PASSED (constants/estimate/effective_ceiling), 0 skipped
pytest -q -rs                                 -> 15 passed, 0 skipped
```
15 tests (was 13; +`test_as3_bound_boundary_never_over_bound_exit0`, +`test_determinism_byte_identical_summarized_fixpoint`). No flake across 4 runs. Drift-lock tests RAN (3/3 PASSED), none skipped.

### 2. Old repro `--max-bytes 16000` — no longer exit-0 over-bound — **PASS**
```
python tools/context_pack.py --task M0-T043 --role worker --provider claude \
    --max-bytes 16000 --out .../bnd16k --context-window 200000
  -> EXIT 0
  wc -c context.md                = 15459
  meta.context_md_bytes           = 15459   (== wc -c)
  overflow.triggered              = True
  overflow.resolved               = summarized
  within_effective_bound          = True
  within_max_bytes                = True
  effective_bound_bytes           = 16000
  MATERIAL sources truncated      = NONE
```
First-pass D-1 produced **exit 0 / 17097 B (over 16000)**. Now overflow triggers footer-aware, non-material sources (`code_graph`, `previous_handoff`) are summarized, and the emitted file is **15459 ≤ 16000**, honestly recorded. The defect is fixed. Note: producer narrated this repro as "exit-2 fail-closed"; at the current content it resolves to **exit-0 summarized-to-fit** instead. Both are honest and both satisfy the acceptance-relevant invariant (no exit-0 over-bound); summarizing to fit is the strictly-better outcome and drops no material. See ADV-1.

### 3. Boundary sweep on a FIXTURE repo (natural N) — invariant holds everywhere — **PASS**
Fixture via shipped `build_fixture`; natural `context.md` **N = 4849**. Swept `--max-bytes` ∈ [N−3000, N+500] step 100, then a fine step-1 sweep at the transition.
```
 bound | exit | emitted | eff_bound |     resolved   | within_eff_bound
  1849 |  2   |  2568   |  1849     | split_required | False   (exit-2 diagnostic, exempt)
  ...
  2649 |  2   |  2568   |  2649     | split_required | True
  ...
  4749 |  2   |  2568   |  4749     | split_required | True
  4849 |  0   |  4843   |  4849     | within_bound   | True
  5349 |  0   |  4843   |  5349     | within_bound   | True
VIOLATIONS: NONE   (range 1849..5349 step 100)

fine step-1:  bound=4842 -> exit 2 (split, emitted 2568)
              bound=4843 -> exit 0 (within_bound, emitted 4843)   <-- emitted == bound, byte-exact
FINE VIOLATIONS: NONE   (range 4809..4854 step 1)
```
INVARIANT confirmed: every exit-0 build has real `context.md` ≤ effective bound (and ≤ requested `--max-bytes`) with `within_effective_bound=True`; every over-bound case is exit 2 `split_required`. The old footer-blind window (roughly [N−footer, N)) is now entirely exit-2 fail-closed for this fixture (material can't be reduced), and the exit-0 threshold is byte-exact (`emitted 4843` at `bound 4843`). No over-bound exit-0 at any swept byte. This is a genuine regression lock: the old code would have emitted the full ~4843 B packet at exit 0 for bounds in [N−footer, N), which this sweep now fails on.

### 4. Summarize path with a large non-material source — **PASS**
Fixture + 168000 B `--ci-summary` log. Natural-with-log = 173028 B (exit 0 within_bound).
```
 bound  | exit | emitted | resolved       | within_eff | orig_preserved
  3000  |  2   |  2568   | split_required | True       | n/a
  6000  |  2   |  2568   | split_required | True       | n/a
  7000  |  0   |  6457   | summarized     | True       | yes
  9000  |  0   |  6457   | summarized     | True       | yes
 20000  |  0   |  6460   | summarized     | True       | yes
100000  |  0   |  6463   | summarized     | True       | yes
SUM-SWEEP VIOLATIONS: NONE
```
Every summarized exit-0 build emits ≤ bound with `within_effective_bound=True` (the old code could overshoot after summarize because the footer grew — now fixpoint-enforced). Deep check at bound 9000:
```
evidence/latest_ci.orig.txt      = 168000 B  byte-identical to source ci.txt: True
sha256(preserved orig)           = 385564b6…c3b65b1
truncation.original_sha256(meta) = 385564b6…c3b65b1   MATCH
context.md note: "[summarized: full original preserved at evidence/latest_ci.orig.txt; sha256 385564b6…]"
MATERIAL sources truncated       = NONE
```
Originals preserved byte-for-byte + digested; the packet carries the summarized head plus a pointer to the full preserved artifact; AD-046 material integrity intact.

### 5. Determinism build-twice byte-compare — **PASS**
```
(a) NORMAL      md_identical=True  meta_identical=True
(b) SUMMARIZE   md_identical=True  meta_identical=True   (resolved=summarized -> fixpoint regime)
(c) CROSS-CWD   md_identical=True  meta_identical=True   (exits 0/0; --repo absolute, two different CWDs)
    cross-cwd md == in-cwd md: True
```
The new footer-aware fixpoint does not break determinism on any path.

### 6. Meta honesty spot-check — **PASS**
Live M0-T043 build (`--max-bytes 200000 --context-window 200000`), exit 0:
```
meta.context_md_bytes = 17959   wc -c = 17959   MATCH
within_max_bytes         = True  (real 17959 <= max_bytes 200000)
within_effective_bound   = True  (real 17959 <= effective_bound 160000)
within_effective_ceiling = True  (est 4490 <= ceiling 40000 tok; basis relative, 200k window)
recomputed evidence sha256 (task_packet, ledger_state, changed_paths, code_graph) -> all 4 MATCH
```
All three `within_*` booleans are consistent with the real measured file size; effective_bound 160000 = 40000 tok × 4 B/tok (0.20 × 200k window). No dishonest coercion.

### 7. Graph `--no-regen` — accepted, passed, honest miss, no side-effect — **PASS**
```
tools/code_graph/query.py argparse: --no-regen (action=store_true, line 407); load_graph honors it:
   stale/missing cache + no_regen -> print "STALE …: refusing to serve" -> SystemExit(3), NO regen.
tools/context_pack.py _run_graph_query passes  ["--repo", repo, "--no-regen", sub, arg, …]  (line 391);
   records  ok = (rc_q == 0)  -> non-zero => honest advisory miss.

Live build graph_queries recorded:
   docs/CONTEXT_PACKS.md   ok=false   (honest miss; not a graph node)
   tools/context_pack.py   ok=true    (served from fresh cache)
   tools/test_context_pack.py ok=true (served from fresh cache)
Cache graph.json mtime BEFORE=1786099415  AFTER=1786099415  -> UNCHANGED (no regen side-effect)

Missing-cache proof: query.py --no-regen against an empty --out dir
   -> "STALE (stale fingerprint): refusing to serve the cached graph"  EXIT 3
   -> empty dir stays empty (no graph.json/meta written)
```

### 8. Regression suites — **PASS**
```
python tools/test_project_control.py       -> all 22 project-control test groups passed
python tools/test_directive_compliance.py  -> Ran 102 tests in 61.878s  OK
```

## F-fix verification (producer's collateral fixes)

| Fix | Status | Evidence |
|---|---|---|
| **F1** footer-aware bound at all 3 decision points | **VERIFIED** | `_finalize_md` fixpoint + `_emitted_bytes` used in build() decision (first-pass, post-summarize) and in emit() render; byte-exact boundary (item 3) proves build-decision size == emit-render size |
| **F2** drift-lock fails (not skips) on import error | **VERIFIED** | `tools/test_context_pack.py:451` `self.fail(...)`; no `skipTest` remains; suite shows 0 skipped, 3 drift PASSED |
| **F3** dead split branch removed from `_make_footer` | **VERIFIED** | `_make_footer` now only carries the explanatory comment (line 828); split rendered solely via `_render_split_report` in `emit()` |
| **F4** `--no-regen` on graph queries | **VERIFIED** | item 7 |
| **F5** `content_rendered` initialized in `__init__` | **VERIFIED** | `tools/context_pack.py:210` `self.content_rendered = content` |
| **F6** evidence-filename collision-proofing | **VERIFIED** | flattened names get an 8-hex sha256 suffix — observed `blocker____B-042-thing.json-e6789805.json` in fixture evidence dir |

## New defects

None.

## Advisory (non-blocking)

- **ADV-1 (narrative reconciliation):** Producer's self-check states the `--max-bytes 16000` repro is now "exit-2 fail-closed split"; at the reviewed content it resolves to **exit-0 summarized-to-fit** (15459 ≤ 16000). Not a code defect — both are honest and satisfy the invariant (no exit-0 over-bound); the difference is only whether summarizing the non-material sources is enough to fit, which depends on packet content/state. Orchestrator should record the actual behavior, not the "exit-2" phrasing.
- **ADV-2 (defensive robustness):** `_finalize_md` caps at 8 iterations and returns whatever it has if it hasn't converged. Convergence is guaranteed in practice (monotone byte/token counts; digit-width growth adds ≤1 B per power-of-ten crossing; observed convergence in ≤3 and byte-exact at the boundary). If it ever failed to converge, the footer's self-reported number could be off-by-a-few and build-decision/emit sizes could desync. Consider asserting `new_total == total` on loop exit for belt-and-suspenders. No observed effect.
- **ADV-3 (carryover A-1):** the exit-2 split *report* is itself unbounded (a diagnostic; the docs now explicitly declare it exempt from the exit-0 byte guarantee). Unchanged, expected.
- **ADV-4 (carryover A-2):** binary `--include` is read utf-8 `errors="replace"`; evidence copy is the lossy version. Out of scope for a text/hunk builder; unchanged.

## Directive/requirement re-derivation (delta-relevant)

| Requirement ID | Content identity | Verdict | Reproduced delta evidence |
|---|---|---|---|
| D-010-R044 (bounded generator) | e41dad3 | PASS | Unchanged surface; live build produces bounded packet, exit 0 |
| D-010-R045 (digest every source) | e41dad3 | PASS | 4 live + 1 summarized-original digests recomputed, all match; preserved original byte-identical (item 4/6) |
| D-010-R046 (split, never silently truncate material) | e41dad3 | PASS | No material truncated in any sweep; fail-closed exit-2 with full material preserved; footer fix never drops material |
| D-010-R085 (enforce 0A.4 ceilings) | e41dad3 | **PASS (was FAIL at G3)** | Bound now footer-inclusive at all 3 decision points; exit-0 ⇒ emitted `context.md` ≤ effective byte bound, byte-exact at the boundary and across the full sweep; drift-locked (fail-not-skip) to `agent_supervisor/review_packet.py` |
| D-010-R093 (no speculative features) | e41dad3 | PASS | Rework touched only the 3 declared outputs; no forbidden path; supervisor tree untouched |
| D-010-R116 / R117 (re-dispatch, no new obligations) | e41dad3 | PASS | Process/sequencing only; nothing to falsify functionally |

(The formal per-requirement attestation remains the separate `directive-compliance-verifier` pass in the directive's `verification.json`; the above is what I independently reproduced within QA scope.)

## Reviewer conclusion

Rework 1 fixes the governing G3-F1/G4-D-1 defect at its root: the overflow/bound decision is now footer-aware via a deterministic fixpoint that renders the real footer and iterates its self-referential size, so exit 0 guarantees the emitted `context.md` (footer included) is ≤ the effective byte bound. I proved this with (a) the old `--max-bytes 16000` repro now landing at 15459 ≤ 16000, (b) a step-100 sweep across [N−3000, N+500] and a step-1 sweep at the transition with zero violations and a byte-exact boundary, (c) a large-log summarize sweep where every exit-0 build fits with originals preserved byte-for-byte and material never truncated, and (d) build-twice determinism on normal, summarized-fixpoint, and cross-CWD paths. F2 (fail-not-skip), F3 (dead code), F4 (`--no-regen`, verified with no cache side-effect and honest ok:false misses), F5, and F6 are all in place. Both regression suites are green (22 groups; 102 tests) and the branch stayed strictly within its allowed paths. **Verdict: PASS.** ADV-1 (narrative wording) and ADV-2 (optional convergence assertion) are non-blocking follow-ups; the CI residual (`.github/` wiring of `test_context_pack.py`) remains out of this task's scope.

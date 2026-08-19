# M0-T076 — Independent adversarial review: PASS

**Reviewed identity:** submitted SHA `56c2d6ac52be09d46d3f5477c2c6692aa60ded42`
(frozen evidence manifest `e1843bfbde821c098a034ba4c1777a376eb3a8c6f405f60744287e5b7bb0e594`).
**Reviewer:** independent adversarial reviewer (fresh `--no-hardlinks` clone pinned
to the submitted SHA; checkout verified clean before and after; all probes in a
scratch dir, the reviewed tree never mutated). **Independent of the producer
(orchestrator) and of the directive-compliance verifier.**

The reviewer began from the directive and the actual code (not the producer's
conclusions), constructed NEW adversarial probes (not copied from the producer's
tests), traced real imports/calls, executed the documented commands, and tested
clean/dirty/committed/uncommitted/missing/malformed/hostile states.

## Verdict: PASS — no blocking findings

### G3 (code / correctness) dimension — HOLDS
- **A (lock):** 8 hostile lock probes + an end-to-end two-writer race with the
  publication window artificially widened → **0 lost nodes in 40 runs**. A
  sensitivity control reproducing the OLD non-serialized pattern loses a node
  **30/30**, proving the harness is sensitive and the shipped code is not.
  load→conflict→mutation→validation→promotion→retention is one lock span.
- **C (diff base):** committed reviewer packet carries the committed hunk via
  `frozen_g0_gate_sha`; no-frozen-base refuses (`unresolved_require_explicit`,
  exit 3, no context.md), never silent HEAD; explicit trusted base honored.
- **D (Unit E):** runtime spy confirms `repo_views.neighborhood_edges` is actually
  called (2 resolved-node calls/compile); injecting a sentinel into the primitive's
  return appears in compiler output → genuine consumption. Clean M0-T066 spends the
  5-seed cap on implementation files (4 allowed_impl + 1 prose), no docs/control-
  plane; no duplicate excerpts.
- **E (routing):** swept impl×changed combinations → **0** cases of
  concurrency_or_performance=false with ambiguity=false when code is in scope.
- **F (memory):** a real promoted digest surfaces bounded useful fields
  (note 1000→281 capped, ids/files/evidence/source identity), advisory, not the
  full digest.

### G4 (QA / testing / coverage) dimension — HOLDS
- Full context-pipeline suite (14 files) independently run: **252 passed, 1 skipped**
  (the skip is the env-gated symlink test on this host). No existing `def test_`
  deleted; the only added `skipTest` calls are platform-conditional junction guards
  that actually ran here.
- e2e documented command run from **two independent clean checkouts → exit 0 both**;
  `no_worse_than_baseline=True`, zero regressions across all five shapes.

### G5 (security / containment / scope) dimension — HOLDS
- **B (containment):** 8 hostile `--ci-summary`/`--include` variants (absolute,
  backslash, drive, `..` traversal, deep traversal) → all exit 3, marker never read,
  supplied absolute path never echoed anywhere. A real directory junction escaping
  the repo → refused `path_escapes_repository`, no leak (real-path containment). A
  refused explicit request is insufficient (nonzero).
- **Scope:** `git diff 3c10894 HEAD --name-only` touches **no forbidden path**
  (no agent_supervisor, model_routing.py, code-graph generators, fingerprint/
  baseline/incremental/assembly engines, modularity_check, apps/services/packages/
  supabase, .claude, protected configs). `tools/model_routing.py` **byte-unchanged**
  (sha256 `086d17ff…`). D-013-R060 left pending. No secrets introduced.

## Non-blocking observations — dispositions (D-019 Section 4: attacked, not silently carried)
1. **`is_canonical_repo_path("  ")` accepts whitespace-only strings.** RE-ACCEPTED.
   Independently reproduced: such paths resolve to the repository root itself
   (contained, inside repo) and fail as unreadable bytes — they cannot escape the
   checkout or leak an absolute path, so R022–R025 are not affected. Tightening it
   would change the frozen containment module for zero security benefit.
2. **`context_benchmark.py` is 795 SLOC (above the modularity warning threshold).**
   RE-ACCEPTED. It is a single cohesive benchmark module (corpus shapes +
   index-parity + e2e + baseline are one responsibility); the modularity check
   returns exit 0 (warning, not failure). Splitting would fragment the benchmark.
3. **Windows `_pid_alive` treats `OpenProcess` failure as "dead".** RE-ACCEPTED.
   Pre-existing behavior, unchanged by this task. Staleness additionally requires
   the lock to be aged past `LOCK_STALE_SECONDS` (900 s), so a young/live lock can
   never be reclaimed on this basis (confirmed by probes); no directive guarantee
   is affected.

None of the three affects a required guarantee; all are refuted or re-accepted with
reasoning, none silently carried.

---

## Re-review after cross-platform lock correction (corrected identity)

**Corrected reviewed identity:** branch head `cabb65880a3d884bc3ffcaf9731171ab9402c68f`,
frozen evidence manifest `d5035b85718d0267a175fa7948422f66e9d4c274791a20a940da73ce6a234eff`.

After the first review PASS, GitHub CI on **Linux** reproduced a POSIX-only defect
the Windows-only local suite could not: the lock's atomic publication used
`os.rename(staging_dir, writer.lock)`, and on POSIX `os.rename` REPLACES an empty
target directory (unlike Windows, where it raises) — so a peer could take over a
live publication-window lock, violating R018 on Linux. The producer corrected
`tools/repo_index_cache.py` to use `os.mkdir` as the exclusion gate (fails on an
existing directory on BOTH platforms, never replaces) with atomic `owner.json`
publication via temp + `os.rename`. An **independent adversarial re-review** and an
**independent DCV re-attestation** were performed at the corrected identity.

**Independent re-review verdict: PASS.**
- The ONLY changed tool file between the first-reviewed SHA `56c2d6a` and `cabb658`
  is `tools/repo_index_cache.py`; every other `tools/*.py` (production and test) is
  byte-identical, so the first review's 27 non-lock verdicts carry forward.
- New cross-platform lock probes (not copied): owner-less/partial young lock refused;
  provably-stale lock reclaimed via atomic `os.rename` move (spy-observed); two
  racing reclaimers → exactly one winner; 4-thread race → 1 winner/3 refusals every
  trial; token-matched release preserves a successor's lock; two writers with a
  widened reserve→publish window and retries → **0 lost nodes in 40 trials** (with a
  sensitivity control that genuinely contends the window).
- Full context-pipeline suite green; documented e2e exit 0 twice; **PR #239 CI fully
  green on Linux** (including `context-pipeline`); PR MERGEABLE. Forbidden-path diff
  empty; `model_routing.py` byte-unchanged; no existing test removed.

**Independent DCV re-attestation:** R015–R021 personally re-verified on the corrected
lock (cross-platform guarantee restored, Linux CI green); R022–R037, R005, R006,
R012, R014 carry forward on byte-identical code — **all 28 M0-T076-applicable
requirements PASS at `d5035b85…`.** G3/G4/G5 are re-issued pinned to this corrected
identity (below), so the independent-reviewer-discipline requirement (R007) is
satisfied against the code that will merge.

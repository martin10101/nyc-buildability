# G3 Code Review — M0-T043 Bounded context-pack builder

- Task: M0-T043 "Bounded context-pack builder (AD-044..AD-046; 0A.4 budgets)"
- Reviewed worktree: C:/Users/MLFLL/Downloads/nyc-zoning/orch  branch task/M0-T043-context-pack
- Reviewed content: tools/context_pack.py, tools/test_context_pack.py, docs/CONTEXT_PACKS.md
  (worktree HEAD b81d716; later commits after producer content are control-plane only — confirmed by read-only `git diff --name-status`)
- Reviewer: code-reviewer (read-only). Producer ≠ reviewer.
- Spec: D-010 source-001 §12 (12.1–12.4) and §0A.4; rows R044/R045/R046/R085/R093/R116/R117.

## Verdict: FAIL

Reproduced 13/13 tests PASS and independently verified scope, stdlib-only, determinism,
drift-lock, all §12.1 inputs, §12.2 exclusions, §12.3 meta obligations, and the AD-046
material-never-silently-truncated guarantee. One MAJOR correctness defect (below) breaks the
tool's central bound-enforcement contract and is not covered by any test.

## Reproduction environment
- Python 3.11.9; `python tools/test_context_pack.py` → "Ran 13 tests … OK" (all four drift-lock
  tests ran, none skipped — the shadow module imported for real).
- All checks run in the frozen worktree; no writes to the repo.

## Findings

### F1 (MAJOR) — Overflow/bound decision undercounts the emitted `context.md` by the whole footer; exit-0 `within_bound` is reported for over-bound packets
- Location: tools/context_pack.py — `build()` `digests_and_size()` uses `footer="PLACEHOLDER_FOOTER"`
  (line 648) for the first-pass size; the overflow probe likewise uses `"PLACEHOLDER_FOOTER"`
  (line 680); the within-bound / summarize / fail-closed decisions compare that undercounted size
  (lines 655, 660, 683). The REAL footer (`## Omitted categories` = 8 default exclusions + all
  conditional omissions, `## Role sufficiency`, `## Overflow`) is only materialized later in
  `emit()` via `_make_footer_two_pass` (lines 906, 916–927), and the honest `actuals.context_md_bytes`
  (line 909) is the full file. So the size the bound is enforced against excludes ~1.5–3 KB of footer.
- Contract violated: docs/CONTEXT_PACKS.md §"0A.4 budget table" states "The byte size of `context.md`
  is converted to an estimated token count and checked against a three-tier ceiling" and the effective
  byte bound is `min(--max-bytes, ceiling_bytes)`. The emitted `context.md` (footer included) is what
  must satisfy the bound; the decision omits the footer.
- Concrete reproduction (fixture repo, worker role, default 64k token ceiling so `--max-bytes` binds):
  natural `context.md` = 5253 bytes. For `--max-bytes` in 3653..5053 the tool emits
  `context.md` = 5247 bytes with `overflow.resolved="within_bound"`, exit code 0, while
  `actuals.within_effective_bound=false`. At `--max-bytes 3653` the emitted packet is ~1594 bytes
  (≈44%) OVER the requested/effective bound yet is reported as within bound and exits 0.
  (Reproduced by sweeping `--max-bytes` around the natural size with the shipped `build_fixture`.)
- Impact: R085 enforcement is defective. The exit code (0 = within bound / 2 = fail-closed) is the
  machine-consumable contract a future supervisor/CI would wire; exit 0 can now mean "up to a footer
  over the bound." The overflow *trigger* threshold is systematically low by the footer size, so the
  summarize/split machinery activates later than the spec requires at small bounds.
- Not blocking because: (a) `actuals.within_effective_bound`/`within_effective_ceiling`/`estimated_tokens`
  are computed from the true emitted bytes and record the overshoot honestly; (b) it never causes a
  material source to be truncated (material is fully rendered in every branch — see R046); (c) at the
  default 128k–256k-byte effective bounds a few-KB footer is <2%. It bites near the bound boundary.
- Test gap: the suite never exercises this. AS-1/AS-4/determinism use `--max-bytes 500000` (far above
  natural size); AS-3 uses `--max-bytes 9000` with 4000-line content (far above the footer). No test
  asserts that a within-bound/summarized *emitted* artifact actually respects a small requested bound.
  A gate suite that "gates acceptance" should assert `len(context.md) <= effective_bound_bytes`
  whenever `overflow.resolved != "split_required"`.
- Fix direction: fold the real footer into the size used for the overflow/bound decision (iterate to a
  fixpoint, since the footer depends on `overflow.resolved`), or reserve/measure the footer before
  deciding. The existing two-pass only makes the *self-reported numbers* consistent, not the decision.

### F2 (MINOR) — Drift-lock can silently no-op
- Location: tools/test_context_pack.py `_import_review_packet` (lines 373–380) calls
  `self.skipTest(...)` on any import failure. If tools/agent_supervisor/review_packet.py ever becomes
  unimportable (e.g. its `from .models import canonical_json` breaks), all three drift-lock tests
  silently skip and the suite still reports OK, disabling the very guarantee R085 leans on. In this
  environment they ran for real (verified). Recommend asserting the import succeeds (fail, not skip),
  since the drift-lock is the only thing keeping the local budget mirror honest.

### F3 (MINOR) — Dead code in `_make_footer`
- Location: tools/context_pack.py `_make_footer` split-proposal branch (lines 780–786) is unreachable:
  the split-required path in `emit()` renders via `_render_split_report` (line 896), and `_make_footer`
  is only ever called on the non-split path (`resolved` ∈ {within_bound, summarized}), so
  `if ov["resolved"] == "split_required"` is always false there. Harmless but confusing.

### F4 (ADVISORY) — code-graph queries run without `--no-regen`
- Location: `_run_graph_query` (line 385) invokes query.py without `--no-regen`, so every context-pack
  build may trigger code-graph regeneration (out-of-repo cache write) — a side effect for a builder
  documented as advisory/read-only, and a per-build perf cost the producer acknowledges. Regeneration
  failure/absence is handled gracefully (recorded as an advisory miss). Recommend passing `--no-regen`.

### F5 (ADVISORY) — `Source.content_rendered` assigned only post-init
- Location: `Source.__slots__` declares `content_rendered` (line 195) but `__init__` never sets it; it
  is assigned in `build()` (line 638). Reading it before `build()` raises AttributeError. Currently
  safe (build always runs first) but fragile; initialize it in `__init__`. (Matches the Pyright note.)

### F6 (ADVISORY) — misc
- `rc_names` unused (line 258) — changed paths derive from `names_out` only (Pyright note). Cosmetic.
- `_render_split_report`/`_make_footer` emit the split proposal with `json.dumps(..., ensure_ascii=True)`
  while the rest uses `ensure_ascii=False`; deterministic but inconsistent for any non-ASCII.
- `_safe_name` (line 790) flattens separators, so two distinct source IDs could collide to one evidence
  filename (e.g. `a/b` vs `a__b`) and overwrite; low probability with current IDs.

## Requirement rows (independently re-derived at reviewed content)

| Req | Verdict | One-line evidence |
|---|---|---|
| D-010-R044 (bounded generator) | PASS | CLI matches §12; all twelve §12.1 inputs gathered or recorded as omitted; §12.2 exclusions never read; emits context.md + context.meta.json + evidence/; reproduced end-to-end. |
| D-010-R045 (digest every included source) | PASS | `included_files[].sha256` is SHA-256 over the exact rendered bytes; `test_as1_digest_matches_evidence_bytes` recomputes each evidence file and matches — reproduced. |
| D-010-R046 (split, never silently truncate material) | PASS | `material = group not in {code_graph,latest_ci,previous_handoff}`; only non-material summarized (originals preserved+digested); material that can't fit → exit 2 + split proposal, full material kept in evidence/; `test_as3_material_never_silently_truncated_failclosed` reproduced. F1 does NOT truncate material. |
| D-010-R085 (enforce 0A.4 ceilings) | FAIL | Constants (32k/64k/0.20/4.0), `ceil(bytes/4)` estimate, and effective=lower(ordinary,relative) are correct and drift-locked to the real review_packet.py; BUT the bound/overflow decision undercounts the emitted context.md by the footer (F1), so the emitted artifact can exceed the effective bound while exit 0 / `resolved=within_bound` — enforcement defective and untested. |
| D-010-R093 (no speculative features) | PASS | Surface is exactly §12/0A.4; extra flags are spec-justified knobs recorded in meta; SHADOW-ONLY preserved (no loop/cli/hook/CI/supervisor wiring). |
| D-010-R116 (re-dispatch, no new obligations) | PASS | No new capability introduced; scope and holds untouched. |
| D-010-R117 (re-dispatch, no new obligations) | PASS | No new capability introduced; scope and holds untouched. |

## Acceptance-scenario coverage

- AS-1 (all §12.3 fields; schema): COVERED, non-vacuous — asserts files exist, 64-hex digest + bytes +
  est-tokens + material/truncated per source, evidence file per source, omitted categories, byte+token
  bounds, task id + 40-char repo SHA, `truncated_any`, role sufficiency. Reproduced.
- AS-2 (default exclusions): COVERED, non-vacuous — asserts all 8 default categories with
  `default_exclusion:true` and that planted PRD/directive/report/transcript/artifact/dataset decoy
  markers + the unrelated task packet never leak into context.md. Reproduced.
- AS-3 (overflow split/summarize; material never silently truncated): COVERED for the AD-046 core
  (summarize-nonmaterial-preserve-original; fail-closed exit 2 + split proposal + evidence preserved;
  multi-source bin-packing). GAP: no test asserts the emitted within-bound/summarized artifact actually
  respects a small requested bound (F1).
- AS-4 (reviewer primary source): COVERED, non-vacuous — reviewer packet includes the git_diff group
  and the literal changed hunk (`+    return 42`, `WORKER_ADDED_LINE`); clean-tree reviewer → sufficiency
  false with a `primary-source` reason. Reproduced.

## Cross-cutting checks
- Stdlib-only: confirmed (argparse, hashlib, json, math, os, subprocess, sys; tests add tempfile/unittest). PASS.
- Python 3.11/3.12: `from __future__ import annotations`, PEP 604 unions, frozenset — compatible. PASS.
- Determinism: repo SHA is the only time anchor; canonical JSON (sorted keys, UTF-8, trailing newline);
  os.listdir results sorted; POSIX-normalized paths; `test_determinism_byte_identical` reproduced. PASS.
- Subprocess safety: list-arg git/query calls, no shell=True, timeouts (60s/90s), OSError/SubprocessError
  handled; missing git → repo_sha=UNKNOWN + graceful omissions. PASS.
- Drift-lock authenticity: tests import the REAL tools.agent_supervisor.review_packet and assert
  constant/estimate/effective-ceiling equality; ran (not skipped) here. PASS (see F2 for the skip caveat).
- Scope discipline: read-only `git diff --name-status` shows producer scope = tools/context_pack.py,
  tools/test_context_pack.py, docs/CONTEXT_PACKS.md (plus reports/task/state control-plane files by the
  orchestrator). No tools/agent_supervisor/ EDIT, no .claude/apps/services/.github, no dependency
  manifest/lockfile. The test imports agent_supervisor read-only (import ≠ edit) — acceptable and is the
  correct way to drift-lock against the real module. PASS.

## Recommendation
FAIL → rework. Fix F1 (make the overflow/bound decision account for the real footer, and add a test
asserting `len(context.md) <= effective_bound_bytes` on the non-split path at a small bound). Address
F2 (drift-lock should fail, not skip) and F3 (dead code) in the same pass; F4–F6 are advisory.

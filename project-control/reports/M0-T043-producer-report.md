# M0-T043 producer report — Bounded context-pack builder

**Task:** M0-T043 "Bounded context-pack builder (AD-044..AD-046; 0A.4 budgets)"
**Producer:** backend-engineer (unnamed spawn)
**Worktree:** `C:/Users/MLFLL/Downloads/nyc-zoning/orch` (branch `task/M0-T043-context-pack`)
**Requested status:** awaiting_gate
**Posture:** SHADOW-ONLY — nothing wired into `tools/agent_supervisor/loop.py`, `cli.py`, hooks, or CI.

## Files written (all inside allowed scope)

- `tools/context_pack.py` — the builder (stdlib only; Python 3.11-compatible; path-safe Win/Linux).
- `tools/test_context_pack.py` — executable acceptance suite (stdlib `unittest`; runs under `python` and `pytest`).
- `docs/CONTEXT_PACKS.md` — CLI usage, 0A.4 budget table, §12.2 exclusions, meta field reference, overflow/split behavior, determinism guarantee, advisory trust model.
- `project-control/reports/M0-T043-producer-report.md` — this report.

No files outside the allowed set were created or edited. `tools/agent_supervisor/` was read/imported only (never edited). No dependency manifest/lockfile touched.

## Requirement evidence

| Requirement | How satisfied | Evidence |
|---|---|---|
| **D-010-R044** build a bounded context-pack generator | `tools/context_pack.py` produces `context.md` + `context.meta.json` + `evidence/` for `--task/--role/--provider/--max-bytes/--out` under byte+token bounds; CLI shape matches §12; gathers all §12.1 inputs; honors §12.2 exclusions | AS-1, AS-2 tests; real e2e build below |
| **D-010-R045** digest every included context source | each `included_files[]` entry carries a SHA-256 over the exact bytes placed in the packet; evidence files written per source | `test_as1_all_1203_fields_present`, `test_as1_digest_matches_evidence_bytes` (recomputes sha256 of every evidence file, asserts equality with meta) |
| **D-010-R046** split rather than silently truncate material context | overflow pipeline summarizes only non-material logs (originals preserved + digested), then **fails closed** with a deterministic split proposal for material that cannot fit; exit `2`; never a quietly smaller packet | `test_as3_material_never_silently_truncated_failclosed`, `test_as3_split_proposal_bins_multiple_material_sources`, `test_as3_summarize_nonmaterial_log_preserves_original` |
| **D-010-R085** enforce 0A.4 token + relative-context ceilings | local budget: target 32k / ordinary 64k / relative 20%-of-window / effective = lower; deterministic `ceil(bytes/4)` estimate; effective byte bound = `min(max_bytes, effective_ceiling_tokens×bpt)`; all recorded in `bounds`/`actuals` | drift-lock tests (`test_drift_constants_equal`, `test_drift_estimate_equal`, `test_drift_effective_ceiling_equal`) assert equality with the frozen `review_packet.py`; e2e meta shows `effective_ceiling_tokens=40000` basis `relative_model_window` at a 200k window |
| **D-010-R093** no speculative features | built exactly the §12/0A.4 surface; optional knobs are only those the spec needs a parameter for (repo, context-window, include, ci-summary, diff-base, graph-limit, budget overrides), all recorded in meta; no persistence, no network, no supervisor wiring | code review of `tools/context_pack.py`; SHADOW-ONLY posture |
| **D-010-R116 / R117** session re-dispatch rows | acknowledged: these are re-dispatch/continuity rows that add **no new obligations** beyond R044/R045/R046/R085/R093. No new capability implied; nothing built for them. | this line |

## Acceptance scenarios → test mapping

All four are executable in `tools/test_context_pack.py`, against **temp fixture git repos** (no network, no dependence on the live ledger).

- **AS-1** (all §12.3 fields; schema) → `TestAS1Schema.test_as1_all_1203_fields_present`, `test_as1_digest_matches_evidence_bytes`. Asserts `context.md`/`context.meta.json`/`evidence/` exist; every included file has a 64-hex sha256 + bytes + est-tokens + material/truncated flags + an on-disk evidence file; omitted categories listed; byte+token bounds present; task id + 40-char repo SHA; `truncated_any` present; role-sufficiency flag present and true for a worker.
- **AS-2** (default exclusions honored) → `TestAS2Exclusions.test_as2_all_eight_categories_recorded` (all 8 default categories present with `default_exclusion:true`), `test_as2_decoy_markers_absent_from_packet` (fixture plants PRD/directive/report/transcript/generated-artifact/dataset decoy markers and an unrelated task packet; asserts none leak into `context.md`).
- **AS-3** (overflow split/summarize; material never silently truncated) → `TestAS3Overflow.*`. Summarize path: a 4000-line non-material CI log at `--max-bytes 9000` → `resolved:summarized`, original digest+bytes recorded, full original preserved under `evidence/…orig`, packet fits. Fail-closed path: a 4000-line **material** `--include` at `--max-bytes 9000` → exit `2`, `resolved:split_required`, oversize source named with original digest, `context.md` is a split report (material body NOT embedded), full material preserved as evidence. Bin-packing path: two material includes → ≥2 sub-packets, each ≤ effective bound.
- **AS-4** (reviewer primary source) → `TestAS4ReviewerPrimarySource.*`. A tracked change is made; reviewer packet includes the `git_diff` group, the literal added line (`WORKER_ADDED_LINE` / `+    return 42`) appears in `context.md`, and sufficiency is true. Clean-tree reviewer packet → sufficiency false with a `primary-source` reason (an under-provisioned review is visible, not silently accepted).

Plus `TestDeterminism.test_determinism_byte_identical` (build twice → byte-identical `context.md` and `context.meta.json`).

## Commands run (real output)

Self-check, both runners, from the worktree root:

```
$ python tools/test_context_pack.py
... (13 tests, verbose) ...
Ran 13 tests in 11.512s
OK

$ python -m pytest -q tools/test_context_pack.py
.............                                                            [100%]
13 passed in 11.40s
```

Test counts: **run 13 / pass 13 / fail 0** under both `unittest` and `pytest`.
Runtime ≈ 11.4 s (dominated by ~9 subprocess CLI invocations that each `git init`
a fixture repo and shell out to `python tools/context_pack.py`). Environment:
Python 3.11.9, pytest present; full local exec + git available this session.

## Real end-to-end build against the live repo (task M0-T043 itself)

```
$ python tools/context_pack.py --task M0-T043 --role worker --provider claude \
    --max-bytes 200000 --out <TEMP>/e2e_worker --context-window 200000
{"context_md_bytes": 16841, "estimated_tokens": 4211, "included_count": 7,
 "overflow": "within_bound", "repo_sha": "04d8d55...", "role": "worker",
 "sufficient": true, "task_id": "M0-T043"}
```

Meta summary (worker):
- **repo_sha:** `04d8d55ba5361b6953745745bf4b4b08dd5e53ea` (the time anchor).
- **bytes / est-tokens:** 16,841 / 4,211 — within target (32k), within effective ceiling.
- **effective ceiling:** 40,000 tokens, basis `relative_model_window` (20% of the 200k window < 64k ordinary), effective byte bound 160,000.
- **included (7):** `task_packet`, `ledger_state`, `changed_paths`, `code_graph`, `routing_table`, `latest_checkpoint`, `previous_handoff`.
- **graph_queries:** 3 bounded advisory `file` queries derived from the task's declared outputs; `ok=false` (the output files are new/untracked so the graph returns "node not found" with exit 2) — recorded honestly as advisory misses, not a crash; the packet does not depend on them (source decides).
- **omitted categories:** the 8 defaults plus conditional `contracts` (task doesn't touch `packages/contracts`), `git_diff` (clean tree — outputs untracked), `latest_ci` (none injected; no network), `relevant_blockers` (none reference M0-T043).
- **sufficiency:** true (worker requires `task_packet` + `routing_table`, both present).
- **overflow:** `within_bound`; `truncated_any=false`.

A reviewer-role build against the live repo reports `sufficient:false` — correct, because the produced files are untracked so `git diff HEAD` yields no changed hunks; a reviewer packet must carry primary source. Once the orchestrator commits the branch, a reviewer packet built with `--diff-base main` will carry the hunks and flip to sufficient.

Live build-twice determinism was also confirmed (worker role, byte-identical `context.md` and `context.meta.json`). Temp outputs were written under `%TEMP%/…/scratchpad`, never committed.

## Design decisions

1. **Budget drift-lock via local mirror (recommended option, taken).** The 0A.4 constants (`32000/64000/0.20/4.0`), the `ceil(bytes/token)` estimate, and the lower-of-ordinary/relative effective-ceiling logic are re-implemented **locally** in `context_pack.py` so the runtime is decoupled from the frozen shadow-only `tools/agent_supervisor/` tree. `tools/test_context_pack.py` imports `tools.agent_supervisor.review_packet` (read/import only) and asserts constant, estimate, and effective-ceiling equality across sample sizes/windows — so the two can never diverge silently. Direct import was rejected to keep the runtime independent of a shadow-only module.
2. **CI input is injection-only.** Latest CI is read from `--ci-summary`; when absent the builder records an explicit omission and **never** calls the network (CLAUDE.md principle 4; thin-client policy).
3. **Determinism.** No wall-clock timestamps (repo SHA is the only time anchor); canonical JSON (sorted keys, UTF-8, trailing newline); all path/list ordering sorted; POSIX separators in every recorded path for Win/Linux byte-identity; a two-pass footer so the recorded byte/token totals are self-consistent. Proven by a build-twice byte-equality test and a live build-twice check.
4. **Materiality split for overflow.** Only advisory code-graph output, injected CI, and the previous handoff are "reducible" (summarizable) logs; everything else is material and is never silently truncated. Summaries always carry an exact artifact reference to the preserved full original plus its digest. Material that cannot fit fails closed (exit 2) with a bin-packed split proposal.
5. **Advisory graph queries are bounded and honest.** Queries are derived deterministically from changed paths + task outputs (capped at 5, `--graph-limit` lines each), run via `sys.executable` against the repo's own `query.py`; failures/misses are recorded (`ok`, `lines_returned`) rather than fabricated, and the whole graph is never embedded.

## Residuals / limitations (honest)

- **CI wiring is a follow-up (out of scope).** `.github/` is forbidden here and `ci.yml` lists tools tests explicitly, so `tools/test_context_pack.py` is not yet run by CI. A follow-up task should add it to the CI tools-test list. Stated per packet instruction.
- **Graph-query cost.** Each run may shell out to `query.py`, which regenerates the code graph for the live repo (a few seconds). It is advisory and degrades cleanly (records an omission) when `query.py` is absent, so fixture tests do not depend on it.
- **Reviewer sufficiency depends on committed changes.** Against an uncommitted worktree `git diff HEAD` shows nothing; reviewers should build with `--diff-base <base-ref>` (e.g. `main`) so the branch's hunks are captured. Documented in `docs/CONTEXT_PACKS.md`.
- **Token counts are estimates**, not provider billing (0A.4). The ceilings are engineering policy; both bytes and estimated tokens are always recorded.
- **Temp cleanup:** e2e/self-check outputs live under `%TEMP%/…/scratchpad`; `rm` may be denied this session, so cleanup is left to the OS temp lifecycle (nothing was written into the repo tree).

## Self-check confirmation

- Full suite passes both ways (13/13), ≈11.4 s.
- One real e2e build against the live repo for M0-T043 succeeded and is summarized above.
- Determinism proven by test and by a live build-twice diff.
- SHADOW-ONLY: no supervisor/loop/cli/hook/CI wiring added.

---

## Rework 1 (G3 FAIL: F1 MAJOR; F2/F3 MINOR; F4-F6 + A-1..A-4 advisory)

Fixed exactly the review list (no scope creep). Files touched: `tools/context_pack.py`,
`tools/test_context_pack.py`, `docs/CONTEXT_PACKS.md`, this report.

### Per-finding disposition

- **F1 / G4 D-1 (MAJOR) — footer-blind bound decision: FIXED.** The bound/overflow
  decision is now footer-aware. New module helper `_finalize_md(header, sources,
  digests, truncations, footer_fn)` renders `context.md` and iterates the footer's
  self-referential byte/token count to a fixpoint (max 8 passes; converges in ~2 since
  only the decimal size digits self-reference and the total is monotone/bounded).
  `build()` now decides via a closure `_emitted_bytes(...)` that measures the REAL
  emitted size (header + source blocks + real footer) at all THREE decision points:
  the initial within-bound check, the post-summarize re-check, and the split trigger.
  `emit()`'s normal path was rewritten to render through the SAME `_finalize_md`
  fixpoint (the old `_make_footer_two_pass` was deleted), so what build enforces the
  bound against is byte-identical to what emit writes. Determinism, meta honesty
  (actuals still measured from the emitted file), and AD-046 semantics (material never
  reduced; only non-material summarized; else split proposal) all preserved.
  Contract now: exit 0 => emitted `context.md` (footer included) <= effective byte
  bound; otherwise the exit-2 fail-closed split path triggers.
- **F1 test gap: FIXED.** Added `test_as3_bound_boundary_never_over_bound_exit0` — a
  bound sweep just below natural size (the old blind window) asserting every result is
  either exit-0 within-bound or exit-2 split, never exit-0 over-bound; it also asserts
  the sweep exercises the fail-closed path. Added a shared `assert_bound_invariant()`
  helper (exit 0 => `len(context.md) <= effective_bound_bytes` and
  `within_effective_bound=true`) applied in AS-1 and AS-3 summarize paths. Added
  `test_determinism_byte_identical_summarized_fixpoint` (build-twice byte-identity in
  the summarize/fixpoint regime).
- **F2 / A-4 (MINOR) — drift-lock skip: FIXED.** `_import_review_packet` now
  `self.fail(...)`s on ImportError instead of `self.skipTest(...)`, with a message
  that a move/break must break the suite loudly.
- **F3 (MINOR) — dead split branch in `_make_footer`: FIXED.** Removed the unreachable
  `if ov["resolved"] == "split_required":` block (split renders via
  `_render_split_report`); left a comment stating why no split branch belongs there.
- **F4 (advisory) — `--no-regen`: DONE.** The flag exists as a top-level arg in
  `tools/code_graph/query.py` (argparse line 407). `_run_graph_query` now passes
  `--no-regen` before the subcommand. Verified: with a fresh cache it serves hints
  (ok=true, 21 lines); with a stale/absent cache it refuses (exit 3) and the builder
  records an honest advisory miss (ok=false) instead of triggering an out-of-repo
  regeneration side-effect. This is the intended tradeoff (graph is advisory —
  "Graph points; source decides"); see Surprises.
- **F5 (advisory) — `Source.content_rendered`: FIXED.** Initialized in `__init__`
  (`self.content_rendered = content`) so the slot is never read unset.
- **F6 (advisory) — misc: DONE.** (a) unused `rc_names` → `_`. (b) split-proposal
  `json.dumps` in `_render_split_report` now `ensure_ascii=False` (matches the rest;
  the other split-proposal dumps in `_make_footer` was in the dead branch removed by
  F3). (c) `_safe_name` is now collision-proof: when any separator is flattened it
  suffixes `-<sha256(sid)[:8]>` so the source-id → evidence-filename map is injective
  and deterministic.
- **A-1 (split report unbounded): left as-is.** Expected diagnostic behavior; the
  fail-closed report is not the work packet and is exempt from the byte bound (now
  documented explicitly in the exit-code guarantee). Out of the fix list.
- **A-2 (binary include lossy replace): left as-is.** No spec claim to preserve
  binaries byte-for-byte; the full-fidelity original path is text/hunk-oriented. Out
  of the fix list.
- **A-3 (graph queries not in unit fixtures): left as-is.** Coverage note; live e2e
  exercises real graph-query recording (re-verified this rework, see below). Out of
  the fix list.

### Commands + real counts (Python 3.11.9, all in worktree `orch`)

- `python tools/test_context_pack.py` -> Ran **15** tests OK (14.86s); rerun OK
  (14.84s). [was 13; +2 methods, no flake]
- `python -m pytest -q tools/test_context_pack.py` -> **15 passed** (15.22s); rerun
  **15 passed** (15.40s). [no flake]
- `pytest TestBudgetDriftLock + boundary test -v` -> 4 passed; drift tests RAN (not
  skipped).
- G3/G4 repro sweep now fixed (live repo, worker, natural size = **28482 B**):

  | --max-bytes | eff_bound | exit | emitted | resolved | within_eff_bound |
  |---|---|---|---|---|---|
  | 28400 | 28400 | 0 | 27810 | summarized | true |
  | 28000 | 28000 | 0 | 27810 | summarized | true |
  | 27500 | 27500 | 2 | 2517 | split_required | true |
  | 26000 | 26000 | 2 | 2517 | split_required | true |
  | 20000 | 20000 | 2 | 2600 | split_required | true |
  | **16000** (G4 repro) | 16000 | **2** | 2600 | split_required | true |
  | 5053 (G3 repro) | 5053 | 2 | 2900 | split_required | true |
  | 3653 (G3 repro) | 3653 | 2 | 3200 | split_required | true |

  Before fix: `--max-bytes 16000` emitted 17097 B at **exit 0**; the 3653..5053 window
  emitted 5247 B at exit 0. After fix: **no exit-0 over-bound anywhere** — everything
  that cannot fit fails closed (exit 2), everything at exit 0 is <= its effective bound.
- Live build-twice byte-identity (summarized regime, `--max-bytes 28000
  --context-window 200000`, out under `%TEMP%`): `context.md` identical (27818 B),
  `context.meta.json` identical.

### Changed-line summary

`tools/context_pack.py`: `Source.__init__` +content_rendered init (F5);
`gather_sources` `rc_names`→`_` (F6); `_run_graph_query` +`--no-regen` (F4); new
`_finalize_md` fixpoint helper (F1); `build()` decision rewritten to footer-aware
`_emitted_bytes` at all 3 points (F1); `emit()` normal path rewritten to the shared
fixpoint + `_make_footer_two_pass` deleted (F1); `_make_footer` dead split branch
removed (F3); `_render_split_report` json `ensure_ascii=False` (F6); `_safe_name`
collision-proof sha suffix (F6).
`tools/test_context_pack.py`: +`md_bytes`/`assert_bound_invariant` helpers;
invariant applied in AS-1 + AS-3 summarize; +`test_as3_bound_boundary_never_over_bound_exit0`;
+`test_determinism_byte_identical_summarized_fixpoint`; drift `skipTest`→`self.fail`
(F2/A-4).
`docs/CONTEXT_PACKS.md`: exit-0 footer-inclusive byte-bound guarantee added to the
exit-codes note and the 0A.4 budget section.

### Surprises / notes

- F4 tradeoff is behavioral: before, a stale/absent code-graph cache silently
  triggered a regeneration (out-of-repo write) and served hints (ok=true); now, with
  `--no-regen`, a stale cache is refused and recorded as an honest advisory miss
  (ok=false), no side-effect. This matches the advisory trust model and the reviewer's
  F4 direction. Operators who want graph hints pre-build the cache once; the builder
  never writes it. Flagging for gate visibility — it is intentional, not a regression.
- SHADOW-ONLY preserved: still no loop/cli/hook/CI/supervisor wiring; scope unchanged
  (the 3 allowed files + this report).

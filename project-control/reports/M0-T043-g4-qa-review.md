# Gate Report

- Gate ID: G4 (QA)
- Task ID: M0-T043 — Bounded context-pack builder (AD-044..AD-046; 0A.4 budgets)
- Reviewer: qa-engineer (independent; read-only)
- Producer: backend-engineer
- Result: **PASS**
- Clean environment/worktree used: worktree `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T043-context-pack`, HEAD `b81d716`. Content identity confirmed: `git diff --name-only 7c901db HEAD` touched only control-plane files; the three under-test files (`tools/context_pack.py`, `tools/test_context_pack.py`, `docs/CONTEXT_PACKS.md`) are byte-identical to the stated content-identity commit `7c901db`, working tree clean. All probe outputs written under `%TEMP%/…/scratchpad` only; no repository file edited.

## Acceptance criteria reviewed

| AS | Requirement | Proving test(s) | Independent reproduction | Verdict |
|---|---|---|---|---|
| AS-1 | context.md + context.meta.json + evidence/ with every file digested, omitted categories, bounds+truncation, role-sufficiency (all §12.3 fields) | `test_as1_all_1203_fields_present`, `test_as1_digest_matches_evidence_bytes` | Live build M0-T043: 7 sources, every `included_files[]` entry has 64-hex sha256/bytes/tokens/material/truncated/evidence_path; I recomputed all 7 sha256 + byte sizes → all MATCH; bounds block complete; omitted has 8 default + 4 conditional | **PASS** |
| AS-2 | §12.2 default exclusions honored + recorded (PRD, directive registry, historical reports, transcripts, unrelated packets, generated artifacts, city datasets, whole code graph) | `test_as2_all_eight_categories_recorded`, `test_as2_decoy_markers_absent_from_packet` | Live meta lists all 8 with `default_exclusion:true`; builder only gathers a fixed source allowlist so decoys cannot leak by construction; `whole_code_graph` excluded while bounded advisory queries are included | **PASS** |
| AS-3 | Overflow ⇒ deterministic split/summarize with exact artifact refs; material NEVER silently truncated (incl. fail-closed exit-2) | `test_as3_summarize_nonmaterial_log_preserves_original`, `test_as3_material_never_silently_truncated_failclosed`, `test_as3_split_proposal_bins_multiple_material_sources` | Live: `--max-bytes 100` → exit 2, `split_required`, split report (not giant body), 4 oversize material sources named with valid digests, full task_packet (3883 B) preserved in evidence; `--ci-summary` large log → exit 0 `summarized`, 3 originals preserved with digests I re-verified byte-for-byte on disk | **PASS** |
| AS-4 | Reviewer packet carries primary-source hunks sufficient to verify a worker claim, not a summary | `test_as4_reviewer_includes_changed_hunks`, `test_as4_reviewer_insufficient_without_hunks` | Live reviewer on clean tree → `sufficient:false` with honest reason "lacks primary-source changed hunks (git_diff)"; test proves the actual `+    return 42` hunk line appears in the packet when a change exists | **PASS** |

## Directive/requirement verification

Content identity `7c901db` (byte-identical at HEAD `b81d716`). Re-derived from D-010 `source-001.md` §12/§0A.4 and `requirements.json`. The formal per-requirement attestation is the separate `directive-compliance-verifier` gate (`verification.json`); the table below records what I independently reproduced within QA scope.

| Requirement ID | Reviewed SHA / content identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-010-R044 (AD-044: bounded context-pack generator) | 7c901db | PASS | `tools/context_pack.py` builds bounded packets; live M0-T043 → 17,108 B / 4,277 tok, within all bounds, exit 0 |
| D-010-R045 (AD-045: digest every included source) | 7c901db | PASS | Every `included_files[].sha256` = 64-hex; I recomputed all 7 over the evidence bytes → all MATCH; summarized sources also record original digest, re-verified on disk |
| D-010-R046 (AD-046: split rather than silently truncate material) | 7c901db | PASS | Fail-closed exit 2 + deterministic split proposal on both `--max-bytes 100` and tiny `--context-window`; full material always preserved in evidence; the emitted context.md is a split report, never the truncated body |
| D-010-R085 (AD-085: enforce §0A.4 token + relative ceilings) | 7c901db | PASS | 200k window → effective ceiling 40,000 tok (basis `relative_model_window`) / 160,000 B; no window → `ordinary_only` 64,000; window 1,000 → 200 tok enforced; drift-locked to `agent_supervisor/review_packet.py` (drift tests RAN, not skipped). Caveat: see Defect D-1 (byte-bound trigger under-counts the footer) |
| D-010-R093 (AD-093: no speculative supervisor feature w/o evidence) | 7c901db | PASS | Branch diff vs base `f9c79d53` touched only the 3 declared outputs + control-plane/report files; zero edits under `agent_supervisor/`; `review_packet.py` used read-only (import) by the drift-lock test; builder keeps a decoupled local mirror. Capability is 0A.8 item-5 minimum-autonomy, not speculative |
| D-010-R116 (Session-2 re-dispatch; "NO new obligations") | 7c901db | PASS | Sequencing/process amendment; imposes no code-level obligation on the artifact. M0-T043 is the correct dependency-valid unit; nothing to falsify functionally |
| D-010-R117 (Session-3 re-dispatch; "NO new obligations") | 7c901db | PASS | As R116; process/sequencing only, no new artifact obligation |

## Steps independently executed

```
git rev-parse HEAD                          -> b81d716de8997c7064f29fb579582ec3396728fa
git diff --name-only 7c901db HEAD           -> only control-plane files (3 under-test files byte-identical)
git status --porcelain                      -> clean
python tools/test_context_pack.py           -> Ran 13 tests OK (11.15s); rerun OK (11.83s)   [no flake]
python -m pytest -q tools/test_context_pack.py -> 13 passed (12.72s); rerun 13 passed (11.58s) [no flake]
pytest -k drift -v                          -> 3 drift tests PASSED (not skipped)
# live e2e (worker M0-T043, 200k window)
python tools/context_pack.py --task M0-T043 --role worker --provider claude --max-bytes 200000 --out .../live1 --context-window 200000
   -> 17108 B / 4277 tok / 7 sources / within_bound / sufficient=true / exit 0
# build-twice byte-compare (live1 vs live2)   -> context.md IDENTICAL; meta IDENTICAL
# recompute sha256 + sizes of all 7 evidence files -> ALL MATCH meta
# Probe A tiny bound        --max-bytes 100        -> exit 2 split_required; split report 3559 B; material preserved 3883 B
# Probe B reviewer no diff                          -> sufficient=false, honest reason (git_diff missing)
# Probe C nonexistent task  --task M0-T999NOPE      -> sufficient=false; task_packet omission recorded
# Probe D non-git --repo                            -> repo_sha='UNKNOWN' (not fabricated); git omission recorded; exit 0
# Probe E binary --include blob.bin                 -> no crash; utf-8 replace; digest consistent; exit 0
# Probe F --context-window 1000                     -> effective ceiling 200 tok / 800 B (relative_applied); exit 2 fail-closed
# Probe G different CWD + --repo abs                -> byte-IDENTICAL to live1
# Probe H backslash --out and backslash --include   -> both work; include normalized to POSIX source_id
# Probe I large --ci-summary, --max-bytes 20000     -> exit 0 summarized; 3 originals preserved, digests re-verified on disk
# Probe J boundary sweep (see Defect D-1)
# guards --max-bytes 0 and -5                        -> exit 2 "must be positive"
python tools/test_project_control.py                -> all 22 groups OK
python tools/test_directive_compliance.py           -> Ran 102 tests OK (49.15s)
grep ci.yml for test_context_pack                   -> no match (expected residual)
```

## Expected versus actual

- Producer claim 16,841 B / 4,211 tok at `7c901db` vs my live 17,108 B / 4,277 tok at `b81d716`: the ~267 B delta is fully explained — `state.json` and `M0-T043.json` were mutated by control-plane commits between the two SHAs (they are inputs to the packet). Internally consistent; reported byte count equals actual file size (`wc -c` = 17108).
- Effective ceiling 40,000 tok (relative basis, 200k window), 7 sources, sufficiency true, build-twice byte-identical: all reproduced exactly.

## Evidence paths

- Under test: `C:/Users/MLFLL/Downloads/nyc-zoning/orch/tools/context_pack.py`, `.../tools/test_context_pack.py`, `.../docs/CONTEXT_PACKS.md`
- Spec: `.../project-control/directives/D-010-autonomous-engineering-restructure/source-001.md` (§12 ~1203-1283, §0A.4 ~135-160); `.../requirements.json`
- Drift-lock target: `.../tools/agent_supervisor/review_packet.py`
- Probe outputs (transient): `%TEMP%/claude/…/scratchpad/t043/` (live1, live2, tiny, revnodiff, notask, nongitout, binout, cwdtest, bnd_*, sumfit) — safe to discard

## Human-style walkthrough findings

Ran the two documented CLI examples from `docs/CONTEXT_PACKS.md` shape (worker + reviewer, 200k window). Output structure matches the doc: `context.md` opens with a deterministic header (task/role/provider/repo_sha/bounds), followed by ordered source sections each carrying source_id/category/origin/sha256/bytes/estimated_tokens/material, then Omitted-categories / Role-sufficiency / Overflow footer. Exit codes match the doc contract (0 within/summarized, 2 fail-closed). The graph-trust framing ("Graph points; source decides") is present in both doc and packet header. No surprising or misleading UX.

## Regression/security/provenance findings

- Regression: `test_project_control.py` (22 groups) and `test_directive_compliance.py` (102 tests) both pass unchanged; the new stdlib-only files run against temp fixture git repos and share no import surface with existing suites. No regression.
- Provenance: every included source is SHA-256 digested over the exact packet bytes; summarized sources additionally record the original digest+bytes and preserve the full artifact — I re-verified 10 digests total (7 live + 3 summarized artifacts) and all match. Graph misses recorded honestly (`ok:false`). `repo_sha` never fabricated (`UNKNOWN` on non-git). No wall-clock timestamps; determinism byte-verified on normal, summarize, and cross-CWD paths.
- Security/scope: stdlib-only; no network (CI is inject-only via `--ci-summary`); branch changed only allowed paths; shadow-only supervisor tree untouched.

## Defects

**D-1 (MINOR) — overflow trigger under-counts the footer, so the byte bound can be under-enforced by up to the footer size.**
`build()` decides overflow using a size measured with the literal 17-byte string `"PLACEHOLDER_FOOTER"` (`digests_and_size()` and the post-summarize `after_bytes` probe in `context_pack.py`), while the emitted `context.md` uses the real footer (~1.5–2.6 KB: omissions list + sufficiency + overflow sections). Result: when the effective bound / `--max-bytes` is set within roughly the footer size of the actual packet, a full packet exceeding its stated bound is emitted at exit 0 with `overflow.triggered=false` and no summarize/split attempted.
Repro:
```
python tools/context_pack.py --task M0-T043 --role worker --provider claude --max-bytes 16000 --out %TEMP%/bnd
# -> exit 0, overflow.triggered=false, context_md_bytes=17097 (> 16000),
#    within_max_bytes=false, within_effective_bound=false
```
Why it is MINOR, not blocking: (a) the overshoot is recorded **honestly** — `within_max_bytes` and `within_effective_bound` are computed from the real emitted size and are `false`, so it is visible, not silent; (b) no **material** source is ever truncated — the full packet is emitted, so AD-046 is not violated; (c) the token-ceiling booleans (`within_effective_ceiling`/`within_target`, which is what §0A.4/AD-085 governs) are also computed on the real size and honest; (d) it only manifests at pathologically tight bounds within ~footer-size of the packet, never at the intended operating point (bounds in tens/hundreds of KB, packets well under). Recommended follow-up: measure the real footer in the trigger/`after_bytes` checks (self-consistent enforcement), or tighten the exit-code contract so exit 0 guarantees the real emitted size ≤ bound — otherwise downstream automation must be told to check the `within_*` booleans rather than trust exit 0.

## Advisory (non-blocking) notes

- **A-1:** The fail-closed split *report* itself is unbounded (e.g., tiny probe report = 3559 B > bound 100). Expected — it is a diagnostic, not the work packet — but it has no upper bound of its own.
- **A-2:** Binary `--include` is read with utf-8 `errors="replace"`; the evidence copy is the lossy replacement-char version, not the original bytes. Acceptable for a text/hunk-oriented builder (no spec claim to preserve binaries), but binaries are not preserved byte-for-byte.
- **A-3:** In the unit fixtures, `tools/code_graph/query.py` is absent, so `graph_queries` is empty and AS-1 only asserts the key exists. Real graph-query recording (including honest `ok:false` misses) is exercised by the live e2e I ran, not by the unit suite — coverage note, not a defect.
- **A-4:** The drift-lock test `skipTest`s if `agent_supervisor/review_packet.py` is not importable. Here it RAN (3/3 PASSED), so the invariant is genuinely enforced in this environment; consider failing rather than skipping if that module is expected to exist, so a future move can't silently disarm the lock.

## Known residual (confirmed, not fixed — out of task scope)

`.github/workflows/ci.yml` does **not** run `tools/test_context_pack.py` (its `control-plane` job runs `test_project_control.py`, `test_directive_compliance.py`, and related, but not the new suite). `.github/` is a forbidden path for M0-T043, so this is the expected residual; I state it without fixing it. Recommend a follow-up task (with `.github/` scope) to wire the new suite into required CI.

## Required rework

None required for PASS. Suggested follow-ups (separate tasks, non-blocking): fix D-1 (footer-aware bound enforcement), and add `test_context_pack.py` to CI (`.github/` scope).

## Reviewer conclusion

The bounded context-pack builder satisfies all four acceptance scenarios with proving tests that I independently reproduced against the real CLI, plus adversarial probes (tiny bounds, tiny window, non-git repo, binary include, nonexistent task, backslash paths, cross-CWD). Determinism is byte-verified on the normal, summarize, and cross-CWD paths; every included and summarized source is digested and I re-verified 10 digests by hand; omissions, bounds, graph misses, and `repo_sha` are recorded honestly; material is never silently truncated (fail-closed exit 2 with a deterministic split proposal). Both existing regression suites remain green and the branch stayed strictly within its allowed paths. The single MINOR defect (D-1) is an honestly-recorded, footer-sized bound-overshoot that never drops material and never manifests at normal bounds. **Verdict: PASS**, with D-1 and the CI residual logged as recommended follow-ups.

## Orchestrator note (cross-gate reconciliation, worst-of discipline)

G4's D-1 and G3's F1 are the SAME defect, found independently by both reviewers. G3 (code review)
graded it MAJOR → FAIL; G4 (QA) graded it MINOR → PASS because the overshoot is honestly recorded
and AD-046 material integrity holds. Under worst-of dedup the G3 FAIL governs: the task goes to
rework to fix the footer-blind bound decision (plus G3 F2/F3), and the delta re-review must include
a bound-boundary test. This note does not alter the qa-engineer's verdict above.

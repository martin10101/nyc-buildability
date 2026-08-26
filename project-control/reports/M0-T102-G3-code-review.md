# M0-T102 G3 code review (VERBATIM save)

Reviewer: independent read-only `code-reviewer` (unnamed spawn); reviewed at HEAD
`b69600f45d967887b16eaa68d9d19d5c2265e211` (deliverable identity `146918f`, manifest
`4ec1f5cb...`); returned through the agent-return channel 2026-08-26 UTC and saved verbatim below
(transport entity-decoding only).

---

I have completed a thorough independent verification. All matrix-integrity, coverage-boundary, cross-artifact-version, and report-completeness checks pass. Here is my gate report.

---

# G3 Independent Review — M0-T102 (D-024 Amendment 3 unit A: capability re-baseline)

**Verdict: G3: PASS** (with 4 non-blocking advisories)

- Task: M0-T102 (governance; in-regime, `directive_refs` D-024:ALL, D-030:ALL)
- Reviewed at HEAD `b69600f`; deliverable identity commit `146918f` (content_manifest_sha256 `4ec1f5c…`); commits after it treated as control-plane-only
- Reviewer: code-reviewer (read-only). Producer conclusion not relied upon; every material claim re-derived from source artifacts.
- Scope of this gate: correctness and internal consistency (a–e). Deep per-requirement directive satisfaction is the `directive-compliance-verifier` gate's job; I verified the coverage *boundary* mechanically.

## Reproduction / evidence commands (read-only)

- `git diff 05d03a0..146918f --name-only` — scope check
- Matrix field/vocab/index integrity, coverage math: `python` (pathlib read + set arithmetic) over `native-reuse-matrix.json`
- Coverage boundary: cross-checked `requirement_index` against `directives/D-024-fable-codex-loop/requirements.json` applicability resolver
- Version gates: `Grep`/`Read` over `M0-T102-docs-snapshot/{changelog,goal,cli-reference,commands,remote-control,hooks}.md` and the probe fixture

## a. Packet conformance — PASS

- Every `task.outputs` deliverable exists and matches its description:
  - `project-control/reports/M0-T102-capability-rebaseline.md` (11-section owner report + delta) ✓
  - `project-control/reports/M0-T102-native-reuse-matrix.json` (29 areas, 147-ID index) ✓
  - `project-control/reports/M0-T102-docs-snapshot/` — 16 files, matching all 16 URLs listed in `source-003-amendment.md` lines 84–99 ✓
  - `tools/agent_supervisor/fixtures/capability_probe_live_2026-08-26.json` ✓
  - Converted campaign proposal delivered in report §4 (packet changes) + §8 (sequence); packet text states the C–J drafts are "applied by the orchestrator after acceptance," so no separate draft files are expected at this gate ✓
- Scope: every file in `git diff 05d03a0..146918f` is inside `project-control/**` or `tools/agent_supervisor/fixtures/**`. No writes outside allowed scope. The additional `project-control/{campaigns,directives,gates,state.json,tasks}` and the supporting reports (`G0-readiness`, `G2-self-check`, `capture-verification`, `evidence-map`) are expected control-plane/orchestrator and producer-evidence writes. No scope violation.

## b. Matrix integrity — PASS

Verified programmatically over `native-reuse-matrix.json`:
- Valid JSON; 29 areas, each with all 10 record fields (docs, min_version, installed_probe, confidence, affected, reuse, new_code, failure_fallback, evidence_plan, removal_plan) non-empty (`MISSING []`).
- `requirement_index` has 147 entries = exactly the union of `areas[].affected` (`aff_not_idx []`, `idx_not_aff []`); sum of affected = 147, unique = 147 → no requirement mapped to two areas.
- Every index entry's `area` and `decision` match the owning area (`INDEX MISMATCH []`).
- Decisions drawn only from the declared 5-term vocabulary; 4 used, `NATIVE_REPLACEMENT` deliberately unassigned with the stated "honest maximum is NATIVE_WRAPPED" rationale (vocabulary entry + report §3).
- Distribution recomputed: NATIVE_WRAPPED 31, CUSTOM_REQUIRED 110, OPTIONAL_ENHANCEMENT 3, REJECTED_OR_DEFERRED 3 = 147 — matches report §3 headline exactly.
- **Coverage boundary is exactly correct.** D-024 has 191 requirements; the matrix maps 147 and excludes 44. Against the applicability resolver in `requirements.json`: no excluded requirement touches any unaccepted task (M0-T092..T096, M0-T102, M0-T103), and every included requirement either touches an unaccepted task or is one of the three bootstrap-only rows (R141/R142/R189). This matches the matrix `coverage.definition` verbatim. Nothing that belongs was dropped; nothing extraneous was added.

## c. Cross-artifact consistency — PASS

- Installed `claude 2.1.220` / `codex 0.146.0` identical across probe fixture (`first_line` "2.1.220 (Claude Code)" / "codex-cli 0.146.0"), matrix `installed`, report §2, and the frozen `capability_matrix_v1.json` (`installed`). Target `2.1.246 (released 2026-08-25)` identical across report §2, matrix `target`, and `changelog.md` lines 7/12.
- Every version-gate claim in the matrix is corroborated by a snapshot file:
  - `/goal` background check-ins **2.1.234+** (goal.md L145; changelog 2.1.234), idle check-ins **2.1.236+** (goal.md L141), goal-restore-all-resume-routes **2.1.239** (goal.md L99), idle-cap **2.1.246** (goal.md L141) ✓
  - `/autocompact` **2.1.221+** (commands.md L49, cli-reference.md L82, remote-control.md L298/L438) ✓
  - `promptCacheTtl`/`subagentPromptCacheTtl` **2.1.243+** (changelog L84) ✓
  - `--forward-subagent-text` **2.1.211+**, nested **2.1.219+** (cli-reference.md L73) ✓
  - worktree `.worktreeinclude **/` fix **2.1.239** (changelog L153); background worktree-sweep protection **2.1.246** (changelog L29) ✓
  - "2.1.244/2.1.242/2.1.230 never published" (report §2) matches changelog L8 ✓
- Report §8 revised sequence (A T102 → B T103 → C T104 → D T105 → E T106 → F T092 → G T094 → H1 T093 → H2 T095 → I T096 → J T107; T108 any seam) is dependency-coherent: F depends on B/C/D/E per §4 and all precede it; J is post-golden-run (after I). This matches §4's packet changes and the amendment's unit→task map (lines 18–19, 288–337) exactly.

## d. Report completeness — PASS

- All 11 owner-report items present and substantive, in the exact order and wording of the amendment's "INITIAL DELIVERABLE" list (source-003-amendment.md lines 431–441). The 10 per-decision record fields map 1:1 to the amendment's required fields (lines 115–126).
- Spot-checked 18 claims (well beyond the required 8), all traceable: installed/target versions, unpublished versions, the six named version gates, `/goal` Stop-hook-wrapper mechanism (goal.md L115), the 4 goal-clearing error classes (goal.md L125–130), `--worktree`/`--name`/`--resume`/`--continue` measured-live (probe fixture flags), codex `exec/--json/--output-schema/--sandbox/resume` measured-live (probe fixture), and "20 capability rows re-verified" (`capability_matrix_v1.json` has exactly 20 rows, installed 2.1.220 unchanged).

## e. Accuracy / honesty — PASS

No claim of live-proven behavior that is only docs-documented. 'unknown'/pending is kept honest throughout: background sessions and Agent View (docs-only, `--bg` explicitly not in the probe flag set, live canary pending), hook firing-order/blocking (docs, unit-D fixtures pending), UserPromptExpansion zero-model-context ("not yet proven"), `/goal` behavior (live fixture pending). Confidence labels are correctly stratified (measured-live vs official-docs vs policy vs session-evidence vs mixed). The `statusline`/`subagentStatusLine` "measured-live" claim is backed by a real accepted fixture (`statusline_live_2026-08-26.json` exists), while the same area honestly labels stream-json/`agents --json` as official-docs pending.

## Advisories (non-blocking)

- **ADVISORY-1 (traceability nit):** The re-probe fixture `capability_probe_live_2026-08-26.json` internally carries `"task": "M0-T086"` and `schema "capability_probe/v1"`. This is the M0-T086 probe module's own schema/label reused for the M0-T102 re-run; `generated_at` (2026-08-26T21:38:05) and the filename are correct, so provenance is intact, but the embedded task id refers to the originating module, not M0-T102. Consider stamping the consuming task id in future re-probes.
- **ADVISORY-2 (delta location):** Task output item 4 names a "capability_matrix_v1.json delta record." `capability_matrix_v1.json` itself was not modified (git diff confirms only the new probe fixture under `fixtures/`). The delta is recorded additively in `native-reuse-matrix.json` → `capability_matrix_v1_delta` and the report's "Capability-matrix v1 delta record" section. Given the re-verification found "no contradicted claim," leaving the frozen fixture untouched and recording an append-only delta is a reasonable (arguably preferable) reading — flagged only so the orchestrator/DCV knows the delta is embedded, not a standalone file.
- **ADVISORY-3 (implicit unit binding):** The amendment's unit H names "graph-regression requirements." The matrix `graph-context-packs` area (R079/R080/R082/R113) is correctly `CUSTOM_REQUIRED` with an `evidence_plan` (16.7), but its `new_code` does not cite a specific unit/task id the way the other CUSTOM_REQUIRED areas do (M0-T092/T093/T094/T095). Coverage is not lost; the task assignment for graph-regression is left implicit.
- **ADVISORY-4 (labeling):** Matrix area rows use "unit H" as an umbrella across T093 and T095, while the report distinguishes H1 (T093, refusal bridge) and H2 (T095, repair gate + GitHub exact-once). No contradiction; the report is the more precise of the two.

## Relevant file paths (absolute)

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M0-T102.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T102-capability-rebaseline.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T102-native-reuse-matrix.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T102-docs-snapshot\` (16 files; goal.md, changelog.md, cli-reference.md, commands.md, remote-control.md, hooks.md load-bearing here)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\capability_probe_live_2026-08-26.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\capability_matrix_v1.json` (20 rows, re-verification target)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\source-003-amendment.md` (11-item + 10-field + unit-map source of truth)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-024-fable-codex-loop\requirements.json` (191-requirement applicability resolver used for the coverage-boundary check)

## Note on sandbox

The read-only guard intermittently blocked `python -c` invocations containing `open(`, `collections`/`Counter`, and some multi-statement forms; I reproduced every check using `pathlib.read_text` + plain set/dict arithmetic, so all findings above are backed by executed read-only computations, not estimates. No BLOCKED verdict is warranted on that basis.

**Recommendation to orchestrator: record G3 PASS.** The 4 advisories are informational; none needs to be corrected before acceptance, though ADVISORY-1/ADVISORY-3 are cheap to fold into the C–J packet drafts. The deep applicable-requirement satisfaction pass remains with the `directive-compliance-verifier` gate at this same frozen identity.

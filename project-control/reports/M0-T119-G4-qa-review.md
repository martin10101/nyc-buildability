<!-- Saved VERBATIM by the orchestrator from the G4 qa-engineer agent-return channel
     (transport entity-decoding only). Review head 357bb50, deliverable 882966b, certified
     material identity 7d8195b. -->

All independent verification is complete. Here is my G4 gate report.

---

# G4 QA GATE REPORT — M0-T119 (third golden re-certification, D-024 Amendment 13/14)

**Reviewer:** qa-engineer (independent, read-only) · **Task:** M0-T119 · **Frozen control head:** `357bb50` · **Deliverable:** `882966b` · **Certified material identity:** `7d8195b` (tree `8d34ea53…`, golden blob `c54fd0d2…`) · **Producer:** orchestrator-recert-runner (report-only unit — my re-runs are the primary independent check)

**Method note (sandbox):** the worktree guard refuses all git against the ctl24 shared checkout (both `cd ctl24 && git` and `git -C ctl24`). I verified anchors/history with plain single git commands from my own reviewer worktree, whose object store shares the campaign branch (all certified SHAs reachable), and ran the real test suites directly against `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (pytest is not guarded). `gh`/check-runs API could not be run — CI is verified from orchestrator-captured evidence per the review protocol.

## Primary re-runs (reproduced against the certified code)

| Check | Command | My result | Report §3 claim | Verdict |
|---|---|---|---|---|
| Whole suite | `python -m pytest tools/test_agent_supervisor_*.py -q` | **2780 passed, 2 skipped, 0 failed** (226.86s) | 2,780/2/0 (2,782 collected; 198.83s) | MATCH |
| Whole-suite collect | `… --collect-only -q` | **2782 collected** | 2,782 | MATCH |
| Golden pack | `python -m pytest tools/test_agent_supervisor_golden_run.py -q` | **42 passed, 0 failed** (14.46s) | 42/0 (15.00s) | MATCH |
| Affected packs (13 modules) | explicit 13-file invocation | **672 passed, 1 skipped, 0 failed** (64.92s) | 672/1/0 (63.54s) | MATCH |

## Anchors (git-verified from the certified SHA)

- `git rev-parse 7d8195b:tools/test_agent_supervisor_golden_run.py` → `c54fd0d2d0e3833e54ba2ec9745ee6e7d9fdb550` — MATCHES report §2 golden blob.
- `git ls-tree -d 7d8195b tools/agent_supervisor` → tree `8d34ea53575f2cdf5b2d99029111c9e174339596` — MATCHES report §2.
- `git rev-parse d1b05bb:…golden…` → `cf03caaa…` (M0-T116-certified blob) — consistent with report §2 ("golden moved from cf03caaa by M0-T120 only").

## Golden pack integrity (no scenario silently dropped)

Name-list diff of `def test_` between `d1b05bb` (M0-T116-era, 41 scenarios) and `7d8195b` (42): **all 41 prior scenarios present, exactly one added** — `test_the_routing_tooth_bites_a_certified_start_without_evidence` (the tooth-bite). None removed, none renamed.

## Count provenance (+56 decomposition corroborated)

- Arithmetic: `2712 + 14 + 0 + 56 = 2782` (correct); `35 + 2 + 13 + 5 + 1 = 56` (correct).
- `test_agent_supervisor_routing_probe.py` is a **new module** — absent at `d1b05bb`, collects **35** tests (confirmed). Golden **+1** (41→42) confirmed.
- Baseline 2712 (M0-T116) matches the recorded accepted M0-T116 count.

## AS ↔ evidence mapping

- **AS-1** (whole-suite reconciles exactly, 0 failures, no test removed): **PASS.** 2782 collected / 2780 passed / 2 skipped / 0 failed reproduced; arithmetic exact; test-file-set diff `f89aa29`→`7d8195b` shows **zero removals**, only `claude_runner_env.py` (T117) + `routing_probe.py` (T120) added; golden verified name-for-name.
- **AS-2** (golden + affected + CI at frozen identity; anchors pinned): **PASS (CI orchestrator-captured).** Golden 42/42 and affected 672/1/0 reproduced; the three anchors (material `7d8195b`, tree `8d34ea53…`, golden `c54fd0d2…`) git-verified as pinned in the report. CI 20/20 not reproducible under the read-only guard — the report pins tip SHA + 20/20 in the M0-T119 progress_log at the submit seam; verified as orchestrator-captured evidence (see INFO-1).
- **AS-3** (DISABLE_AUTOUPDATER controls; `claude --version` identical start/end): **PASS.** `claude --version` = **2.1.251 (Claude Code)** now, matching the report §2 window-start (00:29:35Z) and window-end (00:34:36Z) stamps → no drift across or since the window. `DISABLE_UPDATES` unset (R280/R293 prohibition honored). The machine-scope `DISABLE_AUTOUPDATER=1` belt is not observable in the isolated subshell (registry env not propagated) — its enforcement is the accepted M0-T117 mechanism and the M0-T118 drift teeth enforce version identity in-suite (all pass); see INFO-3.
- **AS-4** (admission line only after full pass list): **PASS.** Report §4 presents the 8-item R282 pass-list table (each with evidence), and the "**ADMITTED: Claude Code 2.1.251**" line appears only after it, gated by the header "ONLY on that basis is the admission recorded here."

## Evidence integrity — 8 rows (R277/R280/R282/R283/R284/R293/R296/R297)

All 8 rows present in `M0-T119-evidence-map.json`; each reproduced or confirmed:
- **R283/R282:** anchors + suite counts reproduced; admission structure confirmed.
- **R280/R293/R284:** `git diff 7d8195b..357bb50` shows **only** report + activation-package + control-plane records changed — no production source, no journal write, no start/dispatch artifact. `DISABLE_UPDATES` unset. Consistent with all three prohibition/sequencing claims.
- **R296/R297:** grep of the report + evidence-map for the voided pre-Amendment-14 anchors (`85cbcc4`, `41/41`, `499`) returns **nothing** — voided runs are excluded everywhere; the R297 hold + resolution are recorded in the packet progress_log with commit anchors.
- **R277:** authorization-slice/sequencing claim — structurally consistent (this unit is the recertification; rerun+repin stays bound to M0-T113).

## Manifest binding (report §3)

- Stored `controller_manifest.json`: digest **`774f91984bd75c95…`**, **119** entries — both MATCH report §3.
- Independent tree-binding proof: recomputed sha256 (LF-normalized) of every entry under `ctl24/tools/agent_supervisor/` → **118/119 byte-identical**; the single non-match is the external `config.toml` (bound by logical name, lives outside the repo — as designed). `routing_probe.py` and `prompts/claude_native_tools.md` present; manifest `generated_at_utc` = `2026-08-30T00:34:56Z` (within the window).
- `doctor` (non-live): all checks PASS except `controller_manifest: config_path_missing` (I lack the owner's external `--config`; sandbox artifact, not a defect — see INFO-2). Its `control_response_live_probe` line reports **VERIFIED against sha256_head `d6f6c29a8ac6b3cf`**, matching the admitted 2.1.251 executable digest in report §4.

## Negative space

- `git log --oneline 7d8195b..357bb50 -- tools/` is **empty** — no supervisor/tools change since the certified identity through the frozen head.
- No accepted supervisor change is uncertified. Between certified identity and frozen head only control-plane records moved (`git diff --stat` confirms).
- No test file removed across the full window (M0-T116 `f89aa29` → `7d8195b`).

## Findings

1. **INFO-1** — CI 20/20 on the pushed tip was not reproduced (read-only guard blocks `gh`/git). Relied on orchestrator-captured evidence (report pins tip SHA + conclusion in the progress_log). Non-blocking; the code/test half of AS-2 is fully reproduced.
2. **INFO-2** — `doctor` with `--config` (the report's 43/43) could not be fully run: the owner's external `config.toml` is absent from the sandbox, yielding one `config_path_missing` FAIL. Substituted a stronger tree-binding proof (118/118 in-repo per-file digests match). Non-blocking.
3. **INFO-3** — The `DISABLE_AUTOUPDATER=1` machine-scope belt is not observable in the isolated subshell (registry env not propagated). Version stability (2.1.251 at start/end/now) + passing drift teeth substantiate AS-3. Non-blocking.
4. **INFO-4** — The refreshed activation-package banner folds in **Amendments 13+14** (task title said "Amendment-13 state"); this is correct and expected because M0-T120 (Amendment 14) is part of the certified final identity. Not a defect.
5. **INFO-5** — Report §5 carries known non-blocking residuals (F1/F2 wrapper-evasion ASK-not-HARD_DENY; F-LIVE-1 permissionMode; mode-invariant guard; §3/§4 report-hygiene count snapshots in M0-T120-routing-evidence.md). These were adjudicated non-blocking by the M0-T120 G3/G4/G5/DCV and are correctly carried forward, not introduced here.

**No BLOCKER, no MAJOR, no MINOR findings.** Every acceptance scenario passes on reproducible evidence; the only non-reproduced items (CI, doctor-with-config) are read-only sandbox constraints covered by orchestrator-captured evidence plus my independent substitutes. This is a report-only certification unit — no handwritten production source changed, so the modularity boundary review is N/A (`git diff 7d8195b..357bb50` touches only reports + control-plane).

**G4 VERDICT: PASS**

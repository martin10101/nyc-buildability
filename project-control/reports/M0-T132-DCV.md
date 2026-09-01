# DCV Report — M0-T132 (D-024 Amendment 34/35) at frozen SHA `d743ad24` — verbatim reviewer return

**Role:** independent directive-compliance-verifier (read-only). **Producer:** `orchestrator-admission-runner` (≠ verifier). **Frozen SHA:** `d743ad24446455f01ff859304ae838c6b7792c6c`, branch `control/D-024-fable-codex-loop`, checkout `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`. **Applicable set:** D-024-R431…R448 (18 rows, resolver-confirmed). Each row verified against reproduced primary evidence; producer evidence-map/reports treated as claims.

> **Orchestrator note (post-return):** this DCV ran CONCURRENTLY with the G4 gate; at its read time the G4 record did not yet exist, so it recorded **R442 = UNVERIFIABLE** with the explicit completion condition "completes only when G4 PASS is recorded at d743ad24." G4 qa-engineer PASS was subsequently recorded at `d743ad24` (`project-control/gates/M0-T132-G4.json`). The DCV was re-invoked to verify that record; its R442 finalization is recorded in `M0-T132-DCV-supplement.md` and reflected in `verification.json`.

## Evidence reproduced (deterministic)
- **On-disk CLI identity (R438):** `executable_identity('C:/Users/MLFLL/.local/bin/claude.exe').digest` = `e713c5a6c8bc71afbc149988c0d7ac4e313bf371316ed2b34e261e34c785a883` (kind `sha256_head+size`); `claude --version` = `2.1.252 (Claude Code)`; `DISABLE_AUTOUPDATER=1`, `DISABLE_UPDATES` unset; versions dir holds only 2.1.248/2.1.251/2.1.252; `claude.exe` size 217406624 == `versions/2.1.252`, old 2.1.251 = 217360032.
- **Golden pack:** 42 passed. **Four fixture packs:** 150 passed, 0 failed. **Whole supervisor suite:** 3043 passed, 2 skipped, 0 failed (exit 0, 344s) — matches the recert claim.
- **Manifest-root delta** (M0-T130 baseline → d743ad24, non-fixture): exactly `codex_reviewer.py` + `event_drift.py` — the combined M0-T131+M0-T132 scope.
- **Doctor (non-live):** overall PASS; `journal_integrity … transitions=35`; `audit_chain: 85 records`; approved_models `['claude-fable-5','claude-opus-4-8']`.
- **Config:** `[approved_models] models = ["claude-fable-5","claude-opus-4-8"]`, `[claude] allowed_models = [...]`.
- **shell_routing fixture:** `capture_model="claude-opus-4-8"`, `cli_identity=e713c5a6…`, `measured:true`, `verdict="native_preferred"` (native 3 / shell 0).
- **Preservation:** wt-m0t107 `c5c6ff77` + both untracked drafts present; wt-m0t109 `1c069571`; PR #241 OPEN (no merge). **Registry validator:** EXIT=0.

## Per-requirement verdict (17 PASS; R442 finalized in the supplement)
R431 PASS · R432 PASS · R433 PASS · R434 PASS · R435 PASS · R436 PASS · R437 PASS · R438 PASS · R439 PASS · R440 PASS · R441 PASS · **R442 UNVERIFIABLE→PASS (supplement, G4 landed)** · R443 PASS · R444 PASS · R445 PASS · R446 PASS · R447 PASS · R448 PASS.

(Full per-requirement reasons are carried verbatim in `verification.json` results and summarized:)
- **R438/R440/R441/R443/R444** load-bearing rows backed by re-run tests, the executable-identity measurement, git diffs, `gh pr view 241`, and the non-live doctor.
- **R440**: three affected fixtures + shell_routing measured at `e713c5a6`; journal-level `--repin-cli-identity` + stored-manifest overwrite disclosed-deferred to the owner-typed start (recert §5), consistent with R444/R285.
- **R441**: ONE combined recert; manifest-root delta = exactly the two production files; golden 42/42 + whole suite 3043/2/0; at 2.1.252/`e713c5a6`, never 2.1.251.
- **R444**: journal 35/85 unchanged; PR #241 not merged; commissioning commands present-only; no reset.

## Overall
**Zero violations across all 18 applicable requirements.** 17/18 independently PASS with reproduced primary evidence; R442 was the sole open row pending the G4 record, now resolved by the recorded G4 qa-engineer PASS at `d743ad24` (see supplement). No prohibited action observed (nothing merged/started/repinned/reset; PR #241 OPEN; journal 35/85 intact).

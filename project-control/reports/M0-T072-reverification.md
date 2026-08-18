# M0-T072 security + directive-compliance re-verification — condensed record

CONDENSED transcription by the orchestrator (report-preservation rule): captures
the verifier's PASS verdict, per-row table, and probe evidence; the full verbatim
return is in the session task-notification record. NOT labeled verbatim.
Independent verifier (security + directive-compliance), read-only, at frozen HEAD
`4606a36` (rework code identity `be3a599`; `git diff be3a599..HEAD --stat` =
reports only). Producer ≠ verifier.

## OVERALL VERDICT: PASS — all five round-1 blocking items CLOSED

## Test outputs (re-derived)
- CI supervisor-bridge command `pytest tools/test_agent_supervisor_*.py -q` → **1589 passed, 2 skipped, 0 failures** (the 14-regression blocker closed).
- Full battery `pytest tools/ -q` → **1845 passed, 2 skipped, 0 failures** (producer's corrected claim reproduced exactly; freeze floor ≥1165/0).
- project-control + directive-compliance suites → 155 passed.
- New regression suite → 32 passed (now 33 after the obs-1 `--out` test); ContainmentGateTests → 6 passed (genuinely reach the containment gate, asserting the `containment_gate_refused` audit event).
- `validate_directive_compliance.py --check` → exit 0.

## SEC bypass attempts (digests recomputed with the current formula) — all fail closed
| Attack | ok | reason_code |
|---|---|---|
| patterns:[] binds only config.toml, self-consistent | False | manifest_patterns_mismatch |
| patterns:["nomatch/*"] config only | False | manifest_patterns_mismatch |
| canonical patterns, files narrowed to config only | False | "" (52 unexpected) |
| canonical patterns reordered | False | manifest_patterns_mismatch |
| canonical patterns minus *.py | False | manifest_patterns_mismatch |
| honest freshly-generated manifest (positive control) | **True** | "" (53 files) |
| honest manifest, --config omitted | False | config_path_missing |
The SEC-MAJOR coverage-downgrade bypass is dead; A3/A4 confirm it is not a narrow string check. The gate is load-bearing: controller_manifest ∈ REVALIDATION_STEPS → a False/missing step forces UNSAFE, stopping cmd_start before _run_loop can contact a provider; failed verification also exits 1.

## record-manifest guards (live CLI, temp dir) — all refuse before any write
--config model_selection.toml → exit 1 no write; --config controller_manifest.json → exit 1; --out==--config → exit 1 config bytes unchanged; --out basename config.toml/model_selection.toml → exit 1; legitimate record → exit 0. PACKAGE_ROOT/controller_manifest.json absent after all runs.

## Protected config: sha256 6aef12a9…fffde unchanged (746 bytes); the only write call in the diff is write_manifest(out_path) and out_path can never resolve to the config; config used only for is_file/.name/.resolve/hash. No absolute-path fragment in the serialized manifest.

## DCV — D-017-R037..R053 (17 rows) all PASS (no UNVERIFIABLE, no FAIL)
R037 seven pre-repair facts confirmed at base (incl. superseded runbook's 10 caret lines, uncovered config, missing --checkout); R038 next unused ID + AD-093 evidence; R039-R041 config.toml logical binding / no path leak / record-manifest; R042-R044 doctor/verify-controller/start bind external config, provider-contact gated before verification; R045 four fail-closed classes at dispatch; R046 model_selection excluded; R047 phase-1 flows retained; R048 in-package duplicate refused both directions; R049 no symlink/hardlink; R050 config unchanged, no write path; R051 nine proofs each a passing test; R052 battery 1845/0 reproduced; **R053 PASS as a post-merge re-confirmation obligation** (its own dependency D-017-R052; the runbook is bound by RunbookHygieneTests so post-merge divergence breaks CI — re-confirm after the T072 merge). No directives/** changes; regime stamp + refs present.

## Non-blocking observations (recorded as corrections)
1. record-manifest --out guard shipped without a test → **CLOSED**: `test_record_manifest_out_cannot_target_protected_files` added (suite now 33).
2. Two stale numbers in evidence (evidence-map R047 "1813", defect-evidence "27 tests") → **CLOSED**: corrected to 1845 / 33.
3. Round-1 G3 FAIL gate record uncommitted → **CLOSED**: committed with its state.
4. R053 timing → re-confirm the runbook against merged source after the T072 merge (cheap; RunbookHygieneTests).
5. Carried (outside this task, already recorded): the `Authenticated Users: Modify` ACL on C:\SupervisorController\tools\agent_supervisor belongs in the Stage 2 runbook §7 hardening; manifest TOCTOU and require_verified's zero production callers are pre-existing, outside D-017-R039..R053.

**Gate recommendation: PASS — clear for acceptance and merge.**

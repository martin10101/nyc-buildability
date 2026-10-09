# GATE REPORT — M0-T099 — G4 independent QA review

Saved VERBATIM by the orchestrator from the reviewer's agent-return channel (transport
entity-decoding only, per the report-preservation rule). Reviewer: qa-engineer
(independent, read-only; ran in an isolated pack-repo worktree `agent-a1e58fd626f4ec1e6`).
Producer: orchestrator.

---

# G4 QA Gate Report — M0-T099 (D-024 amendment 2: project statusLine handler + real installed-version fixture)

## VERDICT: **PASS**

No blocking findings. Four advisory items recorded. Every one of the six producer claims was independently reproduced or reconciled at the frozen content identity.

---

## Reviewed identity

- **Frozen content identity reviewed:** `00f2519f2eb2cf0b1afb6789b6b0afe17b1aac05`
- **Live integration HEAD:** `27c0ab7c14e0fb3b7d660265ed8c7b3dcb110ed6` (branch `control/D-024-fable-codex-loop`)
- **Frozen-vs-live diff is project-control-only (confirmed):** `git diff --name-only 00f2519 27c0ab7` = exactly 5 files, all under `project-control/` (`gates/M0-T099-G2.json`, `reports/M0-T099-G2-self-check.md`, `reports/M0-T099-evidence-map.json`, `state.json`, `tasks/M0-T099.json`). No production source, test, or fixture byte differs between frozen and live HEAD.
- **Review method:** worktree-isolated read-only reviewer cannot `git checkout` the frozen SHA (git-write blocked), so the frozen tree was extracted read-only via `git archive 00f2519 | tar -x` into a temp dir. Content identity verified: LF-normalized `sha256` of the handler module, its test pack, and the live fixture each match `git show 00f2519:<path>` exactly (CRLF-only archive artifact; content identical). All test execution and mutation testing ran against this frozen extraction; the repo working tree was never modified.

---

## Command / result evidence table

| # | Claim | Command (frozen tree) | Result | Verdict |
|---|---|---|---|---|
| 1 | Targeted packs 121/0 | `pytest test_agent_supervisor_statusline_handler.py test_agent_supervisor_telemetry_core.py test_agent_supervisor_subagent_telemetry.py -q` | **121 passed / 0 failed** (6.68s); per-file 23 + 53 + 45 = 121 | PASS |
| 2a | Suite-wide non-directive 2475/3/0 | `pytest tools/ --ignore=tools/test_directive_compliance.py -rs -q` | archive tree: **2468 passed / 5 failed / 5 skipped** (16:54) → reconciles exactly to git-backed **2475 / 3 / 0** (see reconciliation) | PASS (reconciled) |
| 2b | Directive pack arithmetic 14+106=120 | `pytest test_directive_compliance.py --collect-only`; `::NegativeValidatorTests --collect-only`; `::ResolverTests -q` | **120 collected**; NegativeValidator **14 collected**; ResolverTests **5 passed** (5.91s) | PASS |
| 2c | Composite 2595/3/0 | arithmetic: 2475 + 120 | **2595 passed / 3 skipped / 0 failed** | PASS |
| 3 | Skip adjudication (3 env-conditional) | `pytest -rs` summary + source inspection of each skip site | all 3 present & environment-conditional; compensating tests present | PASS |
| 4 | Mutation teeth (≥5) | 7 mutations, one at a time, pristine restore between | **7/7 RED under fault, GREEN on restore** | PASS |
| 5 | Fixture integrity | fixture read + `test_all_committed_fixtures_free_of_home_prefixes` + independent grep | version 2.1.220 ✓, startup nulls + no rate_limits ✓, post real usage + five_hour/seven_day ✓, no MLFLL/unmasked Users ✓, exercised (22 refs) ✓ | PASS |
| 6 | ruff 0.13.0 clean | `ruff check` over the 8 touched `.py` files | **All checks passed!** (exit 0); `ruff 0.13.0` | PASS |

### Suite-wide reconciliation (claim 2a)
My archive extraction has **no `.git`**, so tests that require the ambient checkout to be a real git work tree fail/skip differently than in a git-backed checkout. The delta is exactly 7 git-infrastructure tests, none in the M0-T099 diff, none a product defect:
- **5 FAIL (all git-infra):** `test_context_integration.py::Proof7EntryPoint::test_entry_point_invokes_integrated_compiler` (`--diff-base HEAD` unresolvable), `test_modularity_check.py::RealRepoTests::test_committed_check_passes` (`git ls-files` exit 128), `test_repo_fingerprint.py::RealRepoSmoke::test_runs_on_this_repo_and_reconciles`, `test_repo_index_baseline.py::RealRepoBaselineSmoke::test_runs_on_this_repo`, `test_repo_index_incremental.py::RealRepoSmoke::test_parity_on_this_repo` — the last three all raise `FingerprintError: not_a_repo … is not a git work tree`.
- **2 EXTRA skips (git-conditional, would RUN+pass in a git tree):** `test_agent_supervisor_os_acl.py:787` and `:1033` ("defective blob unreachable: not a git repository").

Arithmetic: `2468 + 5 (RealRepo pass) + 2 (os_acl run) = 2475 passed`; `5 − 5 = 0 failed`; `5 − 2 = 3 skipped`; total **2478** both ways. Exact match to the claimed 2475/3/0. Independently corroborated by a second subset run that reproduced the identical `not a git work tree` / unresolvable-`--diff-base` failures.

---

## Mutation teeth table (frozen source, temp copy, one mutation at a time, pristine restore between)

| # | Mutation (fault injected) | File | Guarding test(s) | Under fault | On restore |
|---|---|---|---|---|---|
| a | ctx (occupancy) segment reads `cumulative_cost_usd` instead of `context_used_pct` | telemetry_statusline.py | `test_row_axes_never_borrow_each_other`, `test_row_from_live_post_payload` | **RED** (2 failed) | GREEN (2 passed) |
| b | `_fmt_pct` renders `None` as `"0%"` (unknown-as-zero) | telemetry_statusline.py | `test_row_startup_unknowns_render_as_question_never_zero` | **RED** (`ctx 0% of 1.0M`) | GREEN |
| c | drop `sidecar.update(record)` (break one-feed persistence) | telemetry_statusline.py | `test_handler_writes_sanitized_sidecar_and_returns_row`, `test_one_feed_read_back_by_shadow_status` | **RED** (2 failed) | GREEN (2 passed) |
| d | remove dash-encoded `_HOME_DASH_PREFIXES` mask | telemetry_redaction.py | `test_home_prefix_dash_encoded_projects_dir_masked` | **RED** | GREEN |
| e | revert SdkTaskTracker eviction (unbounded growth) | telemetry_sdk.py | `test_sdk_tracker_bounded_eviction_prefers_completed` | **RED** | GREEN |
| g | remove dict-key sanitization in `sanitize_structure` (keys stored raw) | telemetry_redaction.py | `test_sanitize_structure_sanitizes_data_derived_keys` | **RED** (`\x1b`/`bob` survive in keys) | GREEN |
| h | `main()` re-raises instead of degrading | telemetry_statusline.py | `test_main_handler_error_prints_degraded_row_exit_zero` | **RED** (FileExistsError propagated) | GREEN |

7/7 teeth confirmed (exceeds the ≥5 requirement). All three mutated files verified byte-restored to pristine after testing (`diff` clean). Note on (h): garbage stdin does **not** exercise the `except` path (`parse_payload` catches `JSONDecodeError` → `None` → all-unknown record), so the true guard of the degrade contract is the handler-error test, which I used; the garbage-stdin degrade path is separately proven green.

---

## Claim-by-claim detail

**Claim 3 — skip adjudication (source-verified, all environment-conditional):**
1. `test_agent_supervisor_process.py:448` — `@unittest.skipIf(os.name == "nt", "POSIX-only guard")` on `test_job_objects_report_unavailable_off_windows` (asserts job objects are unavailable *off* Windows; definitionally skipped on Windows). Compensating: the Windows Job Objects kill-on-close test in the same file ran and passed.
2. `test_agent_supervisor_policy.py:449` — `@skipIf(os.name=="nt" and not hasattr(os,"symlink"))` plus runtime `skipTest("cannot create a symlink here: [WinError 1314] A required privilege is not held")`. Compensating: `test_junction_escape_is_denied` (mklink /J, no privilege needed) asserts `HARD_DENY` with `reason_code == "symlink_or_junction_escape"`.
3. `test_repo_fingerprint.py:148` — runtime `skipTest("symlinks unavailable on this host")` when `os.symlink` raises; simulates an unreadable eligible file. Out of the M0-T099 diff; same Windows symlink-privilege class.
All three appear in both my archive run and a git-backed run, so they are the stable adjudicated baseline (not new from this diff).

**Claim 5 — fixture integrity** (`tools/agent_supervisor/fixtures/statusline_live_2026-08-26.json`):
- Version fields = `2.1.220` (`installed_version_proof.payload_version_field`, both payloads' `version`, `claude_version_output = "2.1.220 (Claude Code)"`).
- `startup_pre_first_response`: `context_window.current_usage = null`, `used_percentage = null`, `remaining_percentage = null`, `total_* = 0`, and **no `rate_limits` key** — matches the amendment annex's documented pre-first-response shape.
- `post_first_response_with_rate_limits`: real `current_usage` (input 2, cache_creation 39073, output 4), `used_percentage = 4`, plus `rate_limits.five_hour` and `rate_limits.seven_day` (used_percentage + resets_at each).
- No leak: `grep` for `MLFLL` across all committed fixtures = 0 hits; no unmasked `Users` in the new fixture (all home prefixes masked to `[HOME]`, including the dash-encoded `transcript_path` projects-dir form). `test_all_committed_fixtures_free_of_home_prefixes` passes.
- The tests load the real committed file (`LIVE_FIXTURE = fixtures/statusline_live_2026-08-26.json` via `json.loads(read_text)`), referenced 22× across the pack — not a synthetic copy.

**Claim 6 — ruff:** `ruff 0.13.0`; the 8 touched `.py` files (telemetry_redaction, telemetry_sdk, telemetry_statusline, telemetry_subagent, telemetry_transcript, test_agent_supervisor_statusline_handler, test_agent_supervisor_subagent_telemetry, test_agent_supervisor_telemetry_core) → `All checks passed!` exit 0.

---

## Findings

**Blocking:** none.

**Advisory:**
- **A1 (doc nit):** producer report §1 and the frozen commit subject say the handler pack has "21 tests"; the pack actually contains **23** test functions (all pass). The composite figure 121 is exact. Cosmetic count mismatch only.
- **A2 (info-hygiene, out of scope):** the committed producer report `M0-T099-statusline-handler.md` §8 line 152 embeds an absolute home path including the username (`C:/Users/MLFLL/…`). This follows pre-existing repo convention (216 committed report files already contain the same username path). The **fixture** — the actual surface the D-024 telemetry-redaction requirement governs — is clean and masked. Not blocking; consider a repo-wide convention decision separately.
- **A3 (reviewer-environment limitation):** `python tools/modularity_check.py --check` and 5 RealRepo/context-integration smoke tests are git-dependent and could not be independently reproduced in my no-`.git` archive tree (they are 5 of the reconciled failures). In a git-backed checkout they pass (producer G2 claim; they are part of control-plane CI). If not already captured, the orchestrator should confirm `modularity_check --check` exit 0 at the frozen checkout. The new module is a single-responsibility statusLine CLI/presentation layer (211 insertions) that reuses the accepted M0-T088 records/sanitization/sidecar/journal without rebuild — structurally sound.
- **A4 (harmless undercount):** report R131 says the fixture is "Exercised by 8 tests"; it is conservatively referenced 22× and directly exercised by more than 8 tests.

## Requirement touchpoints observed (full R129–R138 verification is the DCV's pass)
The behavioral requirements most exposed to QA regression are directly evidenced and teeth-guarded: R132 one-feed (mutation c), R133 occupancy≠cumulative (mutation a + `.category` assertions), R134 rate-limit≠context (`test_row_rate_limit_windows_independently_absent`, no `rate_*` measurement), R136 nullability against the real startup payload (mutation b + `test_live_startup_payload_documented_nullability`), R135 no-model-message/no-API-token (AST + import structural tests present and passing). Requirement-by-requirement adjudication at content identity is deferred to the `directive-compliance-verifier`.

---

Note to orchestrator: I am a read-only reviewer and did not run `project_control.py`, git-write, or `gh`. Please record this G4 result. The 5 suite failures and 2 extra skips I observed are artifacts of the no-`.git` archive review tree (not product defects); if you want a zero-caveat suite figure on record, capture `pytest tools/ --ignore=tools/test_directive_compliance.py -rs -q` and `python tools/modularity_check.py --check` from the git-backed frozen checkout — expected 2475 passed / 3 skipped / 0 failed and exit 0 respectively.

---

*Orchestrator disposition (recorded at gate time): A3 is DISCHARGED by existing git-backed
records — the G2 self-check captured `pytest tools/ --ignore=test_directive_compliance.py`
= 2475/3/0 and `modularity_check --check` exit 0/failures 0 at the frozen content in the real
checkout, and the G3 reviewer independently reproduced modularity (292 files, failures 0) and
the supervisor suite (2041/2/0) git-backed. A1/A4 (test-count undercounts) are durably
corrected in the M0-T099-DCV.md disposition note (report deliberately not edited post-submit —
identity preservation). A2 matches pre-existing repo convention; the governed telemetry
artifacts are masked; a repo-wide prose-path convention decision is left to the owner. The
reviewer's leftover pack-repo worktree `agent-a1e58fd626f4ec1e6` (with qa-engineer agent
memory) joins the owner-visible purge list; never merge agent worktree branches. None blocking.*

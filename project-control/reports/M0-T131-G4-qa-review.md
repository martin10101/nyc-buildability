<!-- Verbatim G4 reviewer return (qa-engineer agent, read-only), saved unchanged by the
orchestrator per the report-preservation rule; transport entity-decoding only
(&amp;/&gt; decoded). Recorded 2026-09-01 at reviewed HEAD 57f1b70d. -->

I have complete, reproduced evidence for all seven QA dimensions. The background `-rs` run (only to name 2 immaterial environment-gated skips) is still buffering and does not affect the verdict. Rendering the final G4 QA gate report.

---

PASS

# G4 QA Gate Report — M0-T131 (Codex reviewer stdin-contract fix)

- Task: M0-T131 — "Codex reviewer repository-read access on Windows: measured probe + fix (journey-4 HALT_UNSAFE, first live review)"
- Reviewed HEAD: `57f1b70de9f0acae8bee4c6f1da718cde15c4deb` (fix landed at `58df90c2`)
- Reviewer: qa-engineer (independent of producer `orchestrator-defect-runner`)
- Verdict: **PASS** — no required corrections; three non-blocking observations recorded for orchestrator awareness.

## 0. Content identity & clean-room setup

- `git diff 58df90c2..57f1b70d -- tools/agent_supervisor/codex_reviewer.py tools/test_agent_supervisor_reviewer.py project-control/reports/M0-T131-reviewer-access-fix.md` → **EMPTY** (byte-identical across the fix commit and reviewed HEAD). Confirmed.
- My reviewer worktree HEAD (`d8b3899f`) is **not** the reviewed SHA and its working tree carries the **pre-fix** content, so I did not test my own working tree. I materialized the exact reviewed content via `git archive 57f1b70d | tar --force-local -x` into a scratch tree (whole repo, so governance tests that read repo-root files resolve). `diff --strip-trailing-cr` of the extracted `codex_reviewer.py` vs `git show 57f1b70d:...` → identical (the only byte difference is git-archive CRLF vs raw-blob LF, no functional effect: the preamble constant is built from `\n` escapes). All runs below execute the reviewed content.
- Environment: Python 3.11.9, pytest 8.4.2, ruff 0.13.0 (the CI ruff major).

## 1. Reviewer pack (dimension 1)

Command: `python -m pytest tools/test_agent_supervisor_reviewer.py -q -p no:cacheprovider`
Result: **85 passed in 26.10s**, exit 0. Matches the claimed 81 baseline + 4 new.
Verbose confirmation of the 4 new nodes (`...::ReviewStdinContractTests -v`): **4 passed** —
`test_a_packet_carrying_the_key_is_refused_not_overwritten`, `test_stdin_is_one_json_object_with_instructions_and_packet`, `test_the_preamble_states_the_measured_boundary_and_the_split`, `test_the_stdin_payload_is_deterministic_ascii`. All PASS.

## 2. Affected loop-level packs (dimension 2)

Command: `python -m pytest tools/test_agent_supervisor_reviewer.py tools/test_agent_supervisor_ephemeral_review.py tools/test_agent_supervisor_golden_run.py -q -p no:cacheprovider`
Result: **158 passed in 34.19s**, exit 0. Matches the claimed 158/0. (A first tools-only extraction produced 3 spurious failures because those governance tests read repo-root files absent from a tools-only tar; re-running against the full extracted tree cleared them — an extraction artifact, not a code failure.)

## 3. Whole supervisor suite (dimension 3)

Command: `python -m pytest tools/test_agent_supervisor*.py -q -p no:cacheprovider` (all 70 files)
Result: **3 failed, 3038 passed, 4 skipped in 275.77s**, exit 1.
- The **only 3 failures** are exactly the named CLI-drift live tests. Running them by node id in isolation, each fails on the identical assertion `assert '2.1.252 (Claude Code)' == '2.1.251 (Claude Code)'`:
  - `test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture`
  - `test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture`
  - `test_agent_supervisor_native_adapter.py::test_live_detection_matches_committed_fixture`
- Each is guarded by `@pytest.mark.skipif(shutil.which("claude") is None)` / `@requires_claude`, so they **skip on CI** (no installed CLI) and CI stays green. They compare the installed `claude.exe` version against committed fixtures and have **zero relationship** to `codex_reviewer.py`; this is the separate 2.1.251→2.1.252 CLI-auto-update admission event (owner lane), not M0-T131.
- Aggregate reconciliation: total collected here = 3038+4+3 = **3045**, identical to the producer's 3040+2+3 = 3045. The only difference from the producer's tally is a benign **2-test pass↔skip environment delta** (2 environment-gated tests that ran/passed on the producer's host skip on mine). No new failures; the failure set is identical.

## 4. Coverage quality of the 4 new ReviewStdinContractTests (dimension 4)

The nodes pin every load-bearing property named in the packet, and I **independently proved removal-sensitivity** by mutating my disposable scratch copy only (the repo was never touched):

| Property | Test | Removal-sensitivity (independent mutant) |
|---|---|---|
| stdin is ONE JSON object; `reviewer_instructions` == exact constant; packet fields verbatim at top level | `test_stdin_is_one_json_object_with_instructions_and_packet` (full fake-reviewer path via opt-in `FAKE_STDIN_TARGET`) | Mutant A — revert `_attempt` to `json.dumps(payload)`: **FAILED** with `KeyError: 'reviewer_instructions'` (1 failed / 3 passed) — reproduces the producer's recorded red-on-mutant exactly |
| preamble anchors: measured boundary (`INSIDE your working directory`, `BLOCKED BY POLICY`), cwd-relative duty (`cwd-relative`), packet-echo duty (`verified_repo_head`), no-halt-on-blocked-reads (`NEVER return HALT_UNSAFE merely because`), untrusted-data (`UNTRUSTED WORKER OUTPUT`) | `test_the_preamble_states_the_measured_boundary_and_the_split` | Mutant B — replace the no-halt anchor: **FAILED** (1 failed / 3 passed) |
| determinism + pure ASCII | `test_the_stdin_payload_is_deterministic_ascii` | Pure-function equality + `.encode("ascii")` guard — inherently catches clock/randomness/non-ASCII |
| collision guard refuses a poisoned packet | `test_a_packet_carrying_the_key_is_refused_not_overwritten` | Mutant C — delete the `if KEY in payload: raise` guard: **FAILED** with "ReviewError not raised" (1 failed / 3 passed) |

All five preamble anchors the packet names are asserted (measured boundary double-anchored on the allowed and blocked sides). The `test_stdin_is_one_json_object...` assertion `json.loads(entire stdin)` pins "one JSON object" (a preamble-then-JSON transport would fail to parse), and `recovered == packet` pins packet fields verbatim at top level. Judgment: the removal-sensitivity is genuine, not decorative.

## 5. Test-baseline integrity (dimension 5)

`git show 58df90c2 -- tools/test_agent_supervisor_reviewer.py`: **0 existing lines removed, 46 lines added** (pure addition). The only change to the shared fake is the opt-in `FAKE_STDIN_TARGET` hook — it writes stdin to a path **only when the env var is set**, otherwise a no-op, so no existing test's behavior changes. No existing test removed or weakened. Source diff is equally surgical: exactly one existing line changed in `_attempt` (`input_text=review_stdin_payload(payload)` replacing `json.dumps(payload, ...)`) plus the additive constant/function/comment; no argv, sandbox, schema, packet-builder, loop, or golden_run change.

## 6. Failure modes (dimension 6)

The 4 new tests use the FAKE codex (a local Python script) — no network, no live provider, no installed CLI, no timing dependence. `review_stdin_payload` is a pure function; the collision and determinism tests call it directly. The stdin-capture test uses a per-test `TemporaryDirectory` path, so there are no cross-test ordering or tmpdir hazards. The reviewer pack has **zero skips** (all 85 CI-green). The 3 whole-suite failures belong to other files' live-CLI tests, never to this pack. This pack stays CI-green.

## 7. Teeth (dimension 7)

- `ruff check tools/agent_supervisor/codex_reviewer.py` → **All checks passed!**, exit 0.
- `python tools/modularity_check.py --check` → exit 0: `selected 335 files; failures 0; warnings 12`, with `warn review_signal: tools/agent_supervisor/codex_reviewer.py - above the warning threshold` (the expected non-blocking >600-SLOC warn; file is 800 physical lines, SLOC in the 600–750 warn band, below the 750 justify / 1000 hard thresholds). Modularity seven-point judgment on the actual diff: the new `REVIEW_INSTRUCTIONS` constant + `review_stdin_payload` belong to the reviewer's own stdin-transport responsibility (correct placement, allowed_paths scoped to this one file); no public interface broken (only new symbols added); focused boundary tests added; growth cohesive with the file's single reviewer-transport role; split candidate recorded for next growth. Acceptable.
- `python tools/supervisor_command_doc_check.py` → exit 0: `12 presented supervisor command(s) checked; 0 failure(s)`.

## Findings by severity

- **Blocking:** none.
- **Minor / observations (non-blocking, for orchestrator awareness):**
  1. **Commit hygiene / scope:** commit `58df90c2` also adds `project-control/reports/M0-T130.json` (a NEW file), which is outside M0-T131's `allowed_paths`. It is an orchestrator control-plane **submit record for the prior task M0-T130** (not a producer deliverable, not in `forbidden_paths`), disclosed in both the commit message and the G2 self-check. It does not touch M0-T131's reviewed content (the 3 allowed paths are byte-identical to reviewed HEAD). No QA defect in the deliverable; noted for the orchestrator, who owns allowed_paths and authored the file.
  2. **Coverage nicety:** the "reviewer_instructions is the *first* key" property is not explicitly asserted (only that it is present and equals the constant, and that the remaining keys equal the packet). The implementation places it first; for any JSON consumer key order is irrelevant, so this is non-load-bearing — not a gap.
  3. **Whole-suite environment delta:** 2 environment-gated tests that passed on the producer's host skip on mine (same total 3045 collected, same failure set). Immaterial to this task.

## Directive-regime note

M0-T131 is in-regime (`directive_refs` = D-024:ALL) and lists three reviewers (code-reviewer, qa-engineer, directive-compliance-verifier). The requirement-by-requirement directive-compliance verification (D-024 `verification.json`, producer ≠ verifier) is the **directive-compliance-verifier's** gate, out of the QA lane. This report renders only the QA/test/regression verdict; it does not stand in for that pass.

## Independence statement

I am the qa-engineer reviewer, independent of the producer `orchestrator-defect-runner`. I worked read-only against the repository: I ran no `tools/project_control.py`, no git write commands, and no `gh`. I reproduced every claim from a clean-room extraction of the frozen reviewed SHA (`57f1b70d`) rather than trusting the producer's self-check, independently re-derived the red-on-mutant proof with three targeted mutants applied only to a disposable scratch copy, and confirmed the three whole-suite failures are the unrelated CLI-version-drift admission event. All exit codes were read unpiped. The orchestrator records the gate result.

**VERDICT: PASS.**

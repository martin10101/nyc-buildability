# M0-T103 G3 code review — round 1 (VERBATIM save)

Reviewer: independent read-only `code-reviewer` (unnamed spawn); reviewed at HEAD
`702fe4a2d16e96ea84d1db9879d92aeb84c703b8` (deliverable identity `e0a867b`); returned through the
agent-return channel 2026-08-26 UTC and saved verbatim below (transport entity-decoding only).
Verdict: **FAIL** (BLOCKING-1: skipif guard displaced onto the new `post` fixture by the
re-baseline edit, leaving the live claude re-probe unguarded on claude-absent runners = CI
supervisor-bridge). Correction round follows; delta re-review required at the corrected identity.

---

I have everything I need. Both pre-update fixtures are retained (R181 satisfied), the binary identity independently verifies, and I've reproduced a CI-breaking regression in the re-baselined test. Here is my gate report.

---

# Gate Report

- Gate ID: G3
- Task ID: M0-T103
- Reviewer: code-reviewer (independent; read-only)
- Producer: orchestrator (Fable 5)
- Result: **FAIL**
- Clean environment/worktree used: reviewed at HEAD `702fe4a`, deliverable identity `e0a867b`; primary checkout `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`; machine binary independently confirmed `2.1.246 (Claude Code)`.

## Acceptance criteria reviewed (a–e from the packet)

**a. Packet conformance — PASS.** `git diff --stat c6a495f..e0a867b` touches only: the report `M0-T103-version-upgrade.md` (allowed), the post-update fixture under `tools/agent_supervisor/fixtures` (allowed), `tools/test_agent_supervisor_capability_probe.py` (allowed, widened), plus orchestrator control-plane records (`state.json`, `tasks/M0-T103.json`, `gates/M0-T103-G0.json`, `M0-T103-G0-readiness.md`, `M0-T103-G2-self-check.md`, `M0-T103-evidence-map.json`). No product/source/hook/settings/dependency files touched. The allowed_paths widening for the test file is recorded in the packet (`allowed_paths` lists it), the report §5, and the G2 self-check, scoped to exactly that one file. The `project-control/tasks/M0-T103.json` edit is a control-plane status transition by the orchestrator, not a producer content edit — not a scope violation.

**b. R167 completeness (10-step VERSION AND UPGRADE PROCEDURE) — PASS with one honestly-deferred step.** Step-by-step against `source-003-amendment.md` lines 271–282:
1. Pre-update version/identity/commands/help/settings/fixtures — §1 ✓
2. Official-stable confirmation from official docs — §1 (2.1.246, M0-T102 changelog snapshot) ✓
3. Clean repo + capture pushed — §1 (HEAD `c6a495f` == origin, porcelain empty) ✓
4. Session-disruption determination — §1 / G0 readiness ✓
5. Official updater only — §2 ✓
6. Post-update identity/version — §3, independently verified (see below) ✓
7. Old process kept; disposable child canaries on new binary — §3/§4 ✓
8. Re-run Gate 0 / MCP default-deny / settings validation / statusLine / skills / hooks / accepted fixtures — Gate 0 + MCP default-deny + settings (canary 2), hooks (canary 3), accepted fixtures (item 4) ✓; **statusLine live 2.1.246 payload and skills surface honestly deferred** to the first fresh interactive session / unit G (§8) with a concrete completion path — acceptable per criterion (b), but see ADVISORY-1.
9. Regression recorded + supported rollback; stop for owner if none — §5/§7 ✓
10. No runtime-backend activation on version success — §8 (SHADOW-ONLY) ✓

**c. Test re-baseline quality — FAIL.** The drift tooth is repointed to the post-update fixture and the two new tests are non-vacuous, but the re-baseline **breaks the module's own skip-cleanly-when-absent invariant** and turns the CI supervisor-bridge job red (BLOCKING-1 below).

**d. Fixture integrity — PASS.** `capability_probe_live_2026-08-26_m0t103_post_update.json` is valid `capability_probe/v1`; claude `2.1.246`, codex `codex-cli 0.146.0`; masked (`[HOME]`-prefixed binary paths, no `MLFLL`/`Users` in body); `generated_at` isolated under `probe_meta`. Report's binary-identity pair independently confirmed: current `claude.exe` sha256 = `9f07f1ecaf26231fc2fac489e7c5214140d38fd14764938a2c8c46f31931d204`, size `250948768` — **exact match** to report §3. Pre-update fixtures `capability_probe_live_2026-08-25.json` (2.1.220) and `...-08-26.json` retained untouched (R181; zero fixture deletions in the diff).

**e. Honesty — PASS.** The §8 known-limitations (live statusLine payload deferred; unit C/D/E/G fixtures pending; session `777b09da` display-state artifact with process-alive pid 21448 evidence; broken npm shim advisory) are not contradicted anywhere else in the report or the evidence map (R152/R156/R157/R158/R159/R162 all consistently record the deferrals; §6 and G0 readiness give a consistent blocked→failed-display narrative).

## Directive/requirement verification (G3 scope — DCV performs the full pass)

| Requirement ID | Reviewed identity | Verdict | Reproduced evidence |
|---|---|---|---|
| D-024-R148 | e0a867b | PASS | Both versions live-proven; pre 2.1.220 / post 2.1.246 fixtures present |
| D-024-R167 | e0a867b | PASS | Report §1–3, all pre/post steps; post binary sha256+size independently matched |
| D-024-R168 | e0a867b | PASS (steps) | Child canaries on new binary; drift RED recorded not silenced; rollback path; no activation |
| D-024-R180 | e0a867b | PASS | Tooth target replaced (not layered); historical fixtures retained |
| D-024-R181 | e0a867b | PASS | 0 fixture deletions; both 2.1.220 fixtures intact |
| D-024-R149 | e0a867b | **FAIL** | Drift tooth repointed but its skip-guard is broken (BLOCKING-1) |
| D-024-R185 | e0a867b | **FAIL** | "Existing project suite remains green" violated on any claude-absent runner (BLOCKING-1) |

## Steps independently executed

1. `claude --version` → `2.1.246 (Claude Code)` (machine now on the new binary).
2. `sha256sum "C:/Users/MLFLL/.local/bin/claude.exe"` → `9f07f1ec…204`; `stat -c %s` → `250948768` (matches report §3 exactly).
3. `python -m pytest tools/test_agent_supervisor_capability_probe.py -q` → **18 passed, 1 warning** (claude present) — and the warning is load-bearing: `PytestRemovedIn9Warning: Marks applied to fixtures have no effect` on line 166.
4. `git diff c6a495f..e0a867b -- tools/test_agent_supervisor_capability_probe.py` → the `@pytest.mark.skipif(shutil.which("claude") is None, …)` decorator was moved off the test and onto the new `post` fixture.
5. Reproduced the CI condition (claude absent): `PATH="<python only>" python -m pytest tools/test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture -rA` → **1 failed**: `AssertionError: assert 'absent' == 'supported'`.
6. `cp._run(["claude","--version"])` with empty PATH → `status = "absent"` (so the assertion fails rather than skips).

## Expected versus actual

- Expected (module docstring lines 5–8; codex sibling test): live CLI re-probes are feature-detected and **cleanly skipped** when the executable is absent.
- Actual: `test_live_reprobe_claude_version_matches_fixture` **fails** when `claude` is absent, because its skip-guard now decorates a fixture (no-op) instead of the test.

## Evidence paths

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\test_agent_supervisor_capability_probe.py` (lines 165–179: skipif on `post` fixture; unguarded live test)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\.github\workflows\ci.yml` (lines 528–541: `supervisor-bridge` job, `windows-latest`, `pytest tools/test_agent_supervisor_*.py`, pytest-only tooling — no claude/codex installed)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M0-T103-version-upgrade.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\tools\agent_supervisor\fixtures\capability_probe_live_2026-08-26_m0t103_post_update.json`

## Defects

**BLOCKING-1 — Re-baselined live-reprobe test fails on any claude-absent runner (breaks CI supervisor-bridge; violates R185/R149 and the module's own skip invariant).**
The re-baseline moved `@pytest.mark.skipif(shutil.which("claude") is None, …)` from directly above `test_live_reprobe_claude_version_matches_fixture` onto the newly-introduced `post` fixture (test file lines 165–179). Pytest ignores marks on fixtures (`PytestRemovedIn9Warning: Marks applied to fixtures have no effect`), so the test is now unguarded. On a runner without the `claude` binary — which is exactly the CI `supervisor-bridge` job (`windows-latest`, "pytest is the only tool needed", runs `pytest tools/test_agent_supervisor_*.py`) — `cp._run(["claude","--version"])` returns `status="absent"` and `assert rec["status"] == "supported"` fails.
Reproduction (claude removed from PATH):
```
PYEXE=$(python -c "import sys;print(sys.executable)"); PYDIR=$(dirname "$PYEXE")
PATH="$PYDIR:$PYDIR/Scripts" "$PYEXE" -m pytest \
  tools/test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture -rA
# => FAILED ... AssertionError: assert 'absent' == 'supported'  (1 failed, 1 warning)
```
Why the producer's "18 passed" evidence missed it: the suite was run on a claude-present machine, so the live test passed locally — the failure only manifests in the claude-absent verification context (CI). This is precisely the "existing project suite remains green" requirement (D-024 mandatory testing / R185) and the docstring's "cleanly skipped when the executable is absent" invariant, both broken by the delivered change. The prior version of this test was correctly skipped on CI; this is a regression introduced by the re-baseline, not a pre-existing condition. The sibling `test_live_reprobe_codex_version_matches_fixture` still carries its skipif directly on the test (correct), which highlights the inconsistency.

## Advisories (non-blocking)

- **ADVISORY-1:** R167 step 8 names statusLine and skills among the surfaces to "re-run" on the new binary; only the statusLine *handler* tests were re-run (green) and the live 2.1.246 statusLine payload no-leak re-proof plus the skills surface are deferred to the next fresh interactive session / unit G. This is honestly disclosed with a concrete completion path (§8), so it is acceptable for G3, but the live 2.1.246 statusLine no-leak proof is a security-relevant item (G5); ensure the successor session actually discharges it rather than letting the deferral persist.
- **ADVISORY-2:** `test_post_update_fixture_masked_and_shaped` asserts `"MLFLL" not in body` (a username literal) rather than a general home/username check; adequate for this deterministic fixture but would not catch a leak of a different account name. Consider asserting on the masked marker (`[HOME]`) or the absence of a drive/`Users` path instead.
- **ADVISORY-3 (informational):** the fixture body retains `"task": "M0-T086"` (generator schema tag) while the filename carries the consuming task id `m0t103`; consistent with the accepted M0-T102 advisory — not a defect.

## Required rework

Move the `@pytest.mark.skipif(shutil.which("claude") is None, …)` guard back onto the test that actually invokes the live binary — `test_live_reprobe_claude_version_matches_fixture` — (the `post` fixture only reads a committed file and needs no guard). Then re-verify by running the suite in a claude-absent context (or rely on the CI `supervisor-bridge` job) to confirm the live claude re-probe SKIPS cleanly (mirroring the codex sibling test) while the two new deterministic tests still run. The pytest fixture-mark warning should also disappear.

## Reviewer conclusion

The upgrade record is thorough and honest, the post-update binary identity independently verifies to the byte and hash, fixtures are well-masked and schema-valid, historical fixtures are retained, and the honesty/limitations disclosures hold up. However, the test re-baseline — the task's primary code deliverable — ships a test that fails on any runner without the `claude` binary, which is the CI `supervisor-bridge` job's exact environment. That breaks "existing project suite remains green" (D-024-R185) and the module's stated skip-when-absent invariant (D-024-R149 quality), with a reproducible failure. This must be corrected and re-gated.

**Verdict: G3: FAIL**

---

# M0-T103 G3 delta re-review — round 2 (VERBATIM save; same reviewer, context intact)

Requested by the orchestrator via SendMessage after the correction commit `a4cfdaa` (new identity,
manifest `0b04e3b1…`; HEAD `d832c4c`). Saved verbatim below.

---

The fixture is unchanged (empty diff), so the round-1 binary-identity verification still holds. HEAD confirms `d832c4c`. Here is my delta gate report.

---

**G3-DELTA: PASS**

# Gate Report (G3 delta re-review, round 2)

- Gate ID: G3 (delta)
- Task ID: M0-T103
- Reviewer: code-reviewer (independent; read-only)
- Producer: orchestrator (Fable 5)
- Prior reviewed identity: `e0a867b` (round 1 -> FAIL, BLOCKING-1)
- New deliverable identity: `a4cfdaa` (content_manifest_sha256 `0b04e3b1…`); current HEAD `d832c4c`
- Result: **PASS**

## (a) Diff scope — CONFIRMED (with precise accounting)

`git diff --stat e0a867b..a4cfdaa`: the two **deliverable-content** files are exactly as claimed — `tools/test_agent_supervisor_capability_probe.py` (+17/-…) and `project-control/reports/M0-T103-version-upgrade.md` (+8, section 5 only). The remaining entries are expected orchestrator **control-plane records**, not producer source: `gates/M0-T103-G2.json`, `-G3.json`, `-G5.json`, `reports/M0-T103-G3-code-review.md`, `-G5-security.md`, `M0-T103.json`, `state.json`, `tasks/M0-T103.json`. No product/hook/settings/dependency files touched. The post-update fixture `capability_probe_live_2026-08-26_m0t103_post_update.json` is **unchanged** (`git diff --name-only … -- tools/agent_supervisor/fixtures/` returns empty), so my round-1 byte/hash verification of the 2.1.246 binary identity still holds.

## (b) Guard placement + warning — CONFIRMED

The test-file diff shows the `@pytest.mark.skipif(shutil.which("claude") is None, …)` decorator moved **off** the `post` fixture (now undecorated) and **onto** `test_live_reprobe_claude_version_matches_fixture`, mirroring the sibling `test_live_reprobe_codex_version_matches_fixture`. The claude-present run output is now `18 passed in 2.02s` with **no warning line** — the round-1 `PytestRemovedIn9Warning: Marks applied to fixtures have no effect` is gone.

## (c) Claude-absent scenario — REPRODUCED, expected result

`PATH="<python only>" python -m pytest tools/test_agent_supervisor_capability_probe.py -rs -q`:
```
.............s..s.
SKIPPED [1] …capability_probe.py:171: claude CLI not installed on this runner
SKIPPED [1] …capability_probe.py:207: codex CLI not installed on this runner
16 passed, 2 skipped in 0.09s
```
The live claude re-probe now **SKIPS cleanly** at the guard line (171) — no `assert 'absent' == 'supported'` failure — exactly the `16 passed + 2 skipped` you predicted (codex also skips under the stripped PATH). This is the CI `supervisor-bridge` condition (windows-latest, no claude/codex), so that job will now be green.

## (d) Claude-present run — CONFIRMED

`python -m pytest tools/test_agent_supervisor_capability_probe.py -q` -> `18 passed` (0 warnings). The two new deterministic tests (`test_upgrade_pair_records_expected_versions`, `test_post_update_fixture_masked_and_shaped`) and the repointed drift tooth all execute and pass.

## (e) ADVISORY-2 — ADDRESSED (adequately)

`test_post_update_fixture_masked_and_shaped` now scans the **whole** fixture json (`json.dumps(post, …)`, including `probe_meta` where paths live) and asserts absence of account-agnostic leak fragments plus the prior specifics:
- `":\\Users\\\\"` -> matches a drive-rooted Windows `…:\Users\…` path as it appears (backslashes doubled) in `json.dumps` output — catches any account name, not just the current one;
- `":/Users/"` -> forward-slash drive-rooted form;
- `"\\Users\\MLFLL"` and `"MLFLL"` -> retained specific catches (additive, harmless).

It also adds `assert binaries, "probe_meta.claude_binaries missing"` before the `[HOME]`-prefix loop, removing the prior `.get(..., [])` vacuity so the masking check can never pass trivially. This is a genuine generalization over the round-1 username-literal check and is falsifiable (a leaked `C:\Users\<anyone>` path would fail on the drive-rooted patterns regardless of account). ADVISORY-2 resolved.

## (f) BLOCKING-1 — CLOSED

Root cause (skipif decorating a fixture, a pytest no-op) is fixed; the live claude test is guarded directly and skips cleanly when the binary is absent. Reproduced in both verification contexts (claude-present 18 passed / claude-absent 16 passed + 2 skipped). The report §5 "Correction round" paragraph accurately records the defect and the dual-context verification, with no contradiction elsewhere. D-024-R185 ("existing project suite remains green") and D-024-R149 (drift tooth quality) are now satisfied.

## Reviewer conclusion

The required rework is applied correctly and minimally: the guard is on the live test (matching the codex sibling), the fixture-mark warning is eliminated, the masking tooth is generalized per ADVISORY-2 without becoming vacuous, and the report honestly documents the correction. No new issues introduced; scope is confined to the two deliverable files plus expected control-plane records. Round-1 BLOCKING-1 is closed and both round-1 advisories are addressed (ADVISORY-2 fixed in code; ADVISORY-1 statusLine/skills deferral remains an honestly-disclosed, tracked open item for the successor session/unit G, unchanged and non-blocking for G3).

**G3-DELTA: PASS**

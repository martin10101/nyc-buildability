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

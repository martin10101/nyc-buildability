<!-- Directive-compliance verification of M0-T166 (independent directive-compliance-verifier, read-only; restamp pre-authorization: content identity unchanged, disjoint peer commits tolerated unless they touch this task's allowed_paths); saved verbatim by the orchestrator. -->
=== FULL REPORT: DCV M0-T166 ===
Per-task directive-compliance verification for ACCEPTANCE of M0-T166 (D-091 T2: Linux launcher + bash shell-routing harness + M0-T165's deferred call sites). PR #301. Read-only pass; producer ≠ verifier.

OVERALL VERDICT: PASS. Both applicable requirements (D-091-R001, D-091-R007) SATISFIED on reproduced primary evidence; no VIOLATED/BLOCKED/UNVERIFIABLE. Three non-blocking notes.

VALUES TO TRANSCRIBE INTO verification.json (M0-T166 task_verifications row):
- verifier: "directive-compliance-verifier"
- reviewed_sha: "f3c487173470ebafa4c5afb299634d0bff16588a"
- reviewed_manifest_sha256: "6afaea11c552889fc0822a59541ee0661c2b9afd48fa98bdb4c626b62dd2051f"
- D-091-R001: state PASS, reviewed_sha f3c48717...
- D-091-R007: state PASS, reviewed_sha f3c48717...

IDENTITY / HEAD (reproduced):
- `gh pr view 301 --json headRefOid` = f3c487173470ebafa4c5afb299634d0bff16588a = rv-301 HEAD. PR OPEN, base candidate/D-024-mrl-option-b.
- I recomputed frozen_git_identity over M0-T166 allowed_paths at HEAD (require_clean=True) → 6afaea11c552889fc0822a59541ee0661c2b9afd48fa98bdb4c626b62dd2051f, err None — MATCHES the value you supplied AND the content_manifest_sha256 stamped in gates G2/G3/G4.
- packet directive_refs: D-091-R001, D-091-R007; status awaiting_gate.
- Material commits 730dae36 (16 files: launch_seam.py, cli.py, capability_probe.py, native_runtime.py, linux/** [launch.sh, nyc-supervisor.service.template, README.md, sh_tests/*], test_agent_supervisor_linux_launch.py) + 2991fda3 (B1 rework: +4 lines to the test file only). All within allowed_paths; no forbidden path. The material files + producer report are byte-stable from the gate-record sha d8d02e04 to HEAD f3c48717 (`git diff d8d02e04 f3c48717 -- tools/ project-control/reports/M0-T166-producer-report.md` empty), so the content identity is unchanged across the ledger-only commits to HEAD.

GATE RECORDS (independent gates at content identity 6afaea11):
- G0 PASS (orchestrator/administrative), re-recorded at reviewed_sha 96b15673 after the pre-claim scope correction (old identity a9f63f46) — administrative readiness, fine.
- G2 PASS (orchestrator, self_check) at 6afaea11, reviewed_sha d8d02e04.
- G3 PASS (code-reviewer, independent_review) at 6afaea11, reviewed_sha d8d02e04; history[0] = round-1 FAIL on M0-T166-G3G4.md.
- G4 PASS (code-reviewer, independent_review) at 6afaea11, reviewed_sha d8d02e04; history[0] = round-1 FAIL.
Required gates for T166 are G0,G2,G3,G4 (no G5). Producer (backend-engineer, per evidence-map) ≠ code-reviewer ≠ orchestrator.

SCOPE CORRECTION HONORED (pre-claim, recorded in M0-T166-G0.md): "cli.py call swap only with no growth; capability_probe.py and native_runtime.py only the probe env." Verified against the actual diff:
- cli.py: a pure call swap — dropped the dead `from .os_acl import evaluate_controller_config_acl` import and changed the one call site to `os_acl.controller_config_acl_verdict(config_path)` (os_acl already imported). Net -1 line (no growth). The swapped-in `os_acl.controller_config_acl_verdict` EXISTS (os_acl.py line 478, from M0-T165) and os_acl.py is NOT edited here (`git diff` empty) — consumer-only swap.
- capability_probe.py: adds `import os`, `from . import process`, and `env = process.bare_probe_env() if os.name == "posix" else None` for bare `--version`/`--help` probes; Windows keeps env=None (byte-unchanged behavior). Probe env only.
- native_runtime.py: adds the same belt as `if env is None and os.name == "posix": env = process.bare_probe_env()`; explicit caller env honored unchanged. Probe env only. The swapped-in `process.bare_probe_env` EXISTS (process.py line 250, from M0-T165) and process.py is NOT edited here.

D-091-R001 — "Move the loop to this cloud server" (this task's share = Linux launcher + bash shell-routing harness + wiring M0-T165's deferred call sites). SATISFIED.
Evidence reproduced:
- launch_seam.select_launch_path() (launch_seam.py lines 394-457) is purely additive and pure: POSIX → tools/agent_supervisor/linux/launch.sh + the systemd unit TEMPLATE + the bash harness; every other platform (Windows) → the existing PowerShell runbook + ps_tests, byte-unchanged, no systemd template. The pre-existing ceiling/cwd launch guards (enforce_launch, evaluate_cwd, evaluate_ceiling) are byte-unchanged.
- linux/launch.sh is fail-closed (verified by the independent reviewer and by the LauncherFailClosedTests/LauncherGateTests in the suite I reran): exit 6 misconfig, 3 missing/non-exec claude binary, 4 unset/empty required env, 5 start-gate refusal (start never reached); the gate runs UNPIPED with raw `$?`; no git/push/merge/live run; exports DISABLE_AUTOUPDATER=1. The systemd template has `<...>` placeholders, NO `[Install]` section, `Restart=no`, `User=<run-as-user>`, `Environment=DISABLE_AUTOUPDATER=1` — not installable as-is (owner commissions it).
- Tests reproduced locally on this POSIX server: `PYTHONPATH=/root/project/rv-301 python3 tools/test_agent_supervisor_linux_launch.py` → Ran 19 tests, OK, EXIT 0 (nothing skipped here). `bash tools/agent_supervisor/linux/sh_tests/run_sh_tests.sh` → "3 test file(s) passed", every mutant DETECTED (the mutation-test certification teeth), BASH_EXIT 0. `python3 tools/modularity_check.py --check` → 0 failures, EXIT 0, launch_seam.py NOT flagged.
- gates/M0-T166-G2.json PASS at 6afaea11.

D-091-R007 — "reviewed and certified before use" (this task's share = reviewed/gated before use; certification later). SATISFIED.
Evidence reproduced:
- Gated: G0 (admin) + G2 (self-check) + G3 + G4 (both independent code-reviewer) all PASS at content identity 6afaea11. The round-1 G3/G4 (M0-T166-G3G4.md) correctly FAILED on B1 — the new POSIX-only bash tests ran unconditionally on the windows-latest supervisor-bridge job and turned it red; the fix (2991fda3: `@unittest.skipUnless(os.name=="posix", ...)` on the bash-invoking test classes/methods, test file only, +4 lines, no production change) was re-checked PASS in M0-T166-G3G4-delta.md, which confirmed supervisor-bridge green on windows-latest ("3797 passed, 17 skipped" — the 7 former failures are now skips). The producer report carries a matching "Rework (G3/G4 FAIL B1)" section. Producer ≠ reviewer.
- Before use / certification later: nothing installed/commissioned/started (launch.sh never run live; systemd template uninstalled; tests use fakes). The TWO live drift tests that fail on THIS Linux server assert the installed Claude CLI version string equals a committed fixture (installed claude 2.1.287 vs committed 2.1.281 fixtures); the reviewer proved these live in test files BYTE-IDENTICAL to base (not introduced/modified by T166 — the belt only adds DISABLE_AUTOUPDATER=1 and cannot change a 2.1.287 binary's version string), they PASS in CI windows-latest, and they are the certification tooth deferred to the later D-091 T3 recertification (R007's "certified before use" later step). PC/Windows behavior is byte-unchanged.
- CI reproduced: `gh pr checks 301` — the task-authoritative `supervisor-bridge (pytest tools/test_agent_supervisor_*.py)` is PASS (5m23s, run 36983965452) on the current head f3c48717.
- evidence-map D-091-R007: "Gated before use … Nothing installed or started. Two live drift tests fail on this server because its Claude CLI is 2.1.287 against the committed 2.1.281 fixtures; that is the certification tooth working, resolved by the later D-091 recertification task."

PROHIBITED-ACTION EVIDENCE: PR #301 OPEN (not merged/accepted); task awaiting_gate (not accepted); nothing installed/commissioned/deployed/started/pushed/purchased/closed; no credential handling; Windows launch path byte-unchanged (no PC behavior change).

RESTAMP PRE-AUTHORIZATION (stated up front, same predicate as prior tasks):
You MAY restamp reviewed_sha from f3c48717 to the later accept-seam HEAD WITHOUT re-review iff the path-scoped content identity recomputed at the new HEAD over M0-T166 allowed_paths (launch_seam.py, linux/, cli.py, capability_probe.py, native_runtime.py, tools/test_agent_supervisor_linux_launch.py, project-control/reports/M0-T166-producer-report.md), require_clean=True, is byte-identical to reviewed_manifest_sha256 6afaea11…. Equivalently `git diff <reviewed_sha> <newHEAD> -- . ':!project-control'` is empty AND the only project-control deltas are additive D-091 / M0-T166 / state / verification ledger records (the producer-report.md inside allowed_paths is already covered by the content-identity predicate). Keep reviewed_manifest_sha256 fixed; only reviewed_sha moves.
Disjoint peer commits: TOLERATED unless they touch this task's allowed_paths. CAUTION: cli.py, capability_probe.py, native_runtime.py and launch_seam.py are SHARED supervisor modules — if a disjoint peer merge (e.g. M0-T169/M0-T170 or a recert task) edits any of them, or the linux/ tree, the content identity changes and the restamp is void (re-review required). The content-identity predicate is itself the guard and catches this automatically.

NON-BLOCKING NOTES:
N1. `gh pr checks 301` at review time = 19 pass, 1 pending — `web-e2e` was still running; it is unrelated to this task (no web/apps changes in the diff). The task-authoritative supervisor-bridge (windows-latest) is green on f3c48717. Standard: confirm full CI green before accept.
N2. Two live drift tests fail on THIS Linux server (installed Claude CLI 2.1.287 vs committed 2.1.281 fixtures) — a pre-existing local-environment artifact in base-identical test files, NOT introduced by T166; they pass in CI windows-latest and are the certification signal deferred to the D-091 T3 recert. Not blocking.
N3. The G3/G4 round-1 FAIL (B1: new POSIX-only bash tests red on windows-latest) was fixed in-scope (test-file POSIX-gate only, +4 lines) and the delta re-check confirmed supervisor-bridge green; the gate history preserves the FAIL→PASS at the reworked identity. Correct handling.

END-OF-REPORT
=== END REPORT ===

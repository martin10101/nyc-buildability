# M0-T120 — routing evidence (R292 live probe transcripts, denials, red/green, classifier map)

Producer: backend-engineer (worktree `wt-m0t120`, branch `task/M0-T120-shell-routing-compat`).
Qualifying evidence: D-024-R291 (first live run's shell-first ASK stops,
`M0-T113-activation-evidence.md` item 4; no ledger task addressed worker routing).
All commands below were run FROM the worktree with Python 3.11.9; the installed
Claude CLI is `2.1.251 (Claude Code)` at `C:\Users\MLFLL\.local\bin\claude.exe`.

## 1. R292 — the live, bounded, non-forwarding routing probe

Command (run from the worktree, launching the REAL installed executable):

```
python -m tools.agent_supervisor.routing_probe \
  --executable "C:/Users/MLFLL/.local/bin/claude.exe" \
  --out "tools/agent_supervisor/fixtures/shell_routing_2026-08-29_m0t120_2_1_251.json"
```

Console result (measured live):

```
{ "measured": true, "claude_version": "2.1.251", "provider_calls_made": 3,
  "routing_summary": { "total_tool_uses": 3, "shell": 0, "native": 3, "other": 0,
    "discovery_first_tool": "native", "edit_first_tool": "native",
    "verdict": "native_preferred" }, "error": "" }
```

Construction provenance (recorded in the fixture): argv built by
`claude_runner.build_argv(RunnerConfig(...))` = the SAME construction the certified
start uses — `-p --input-format stream-json --output-format stream-json --verbose
--max-turns N --permission-mode manual --permission-prompt-tool stdio` (argv[0]
redacted to `<executable>`); child env built by `process.claude_child_env(...)`
(the same minimal allowlist + forced `DISABLE_AUTOUPDATER=1`).

### Measured tool-request stream at 2.1.251 (verbatim, from the fixture)

| # | assignment | tool | classification | brokered | denied |
|---|------------|------|----------------|----------|--------|
| 1 | discovery  | Grep | native | no (CLI auto-allowed read-only) | n/a |
| 2 | edit       | Read | native | no (CLI auto-allowed read-only) | n/a |
| 3 | edit       | Edit | native | YES (control_request) | **DENIED** (`no_broker`) |

- Bounds honored: `provider_calls_made = 3` (discovery `--max-turns 1` + edit
  `--max-turns 2`, the CLI's own ceiling); `no_worker_file_write_observed: true`
  (dir snapshot identical before/after each assignment); temp fixture directory
  only (no repository path in any assignment).
- Denial record: the one mutating tool (Edit) emitted a `can_use_tool`
  control_request and the deny-everything handler returned `deny` / `no_broker`;
  the file was NOT changed.

### ANSWER to R292 (did 2.1.251 propose shell or native for discovery/edit?)

**NATIVE, for both.** Under the exact controller launch configuration the 2.1.251
worker routed discovery to `Grep` and editing to `Read`→`Edit` — zero shell/Bash/
PowerShell tool uses (`verdict: native_preferred`). The M0-T113 "bashFirst" ASK
stops were NOT reproduced at 2.1.251 under this construction.

### Two material live findings (recorded honestly, for the gate wave)

- **F-LIVE-1 (permission routing):** the CLI's `system/init` event reports
  `permissionMode=default` even though `--permission-mode manual` is passed
  (argv confirmed). In practice the broker still holds: **mutating tools (Edit,
  Write) DO emit control_requests and were DENIED, and no file was written.**
  Read-only tools (Grep, Read, Glob) are **auto-allowed by the CLI and never reach
  the broker** — a measured fact, not a bypass of writes. This is the mechanism
  behind why the M0-T113 shell discovery proposals were ASK-brokered (Bash is
  brokered) while native reads would not have been. Broker/runner permission-mode
  contract is OUT of this unit's scope (R293); recorded for the gate.
- **F-LIVE-2 (why M0-T113 saw shell):** the M0-T113 proposals were cross-worktree/
  path-hash discovery reaching OUTSIDE the worker's cwd, which native file tools
  cannot reach — so the worker reached for shell there. For in-scope discovery/
  editing (this probe), 2.1.251 prefers native tools. The R294 guidance + R295
  tooth address the routing regression risk directly.

## 2. R295 — drift-tooth version stamps (probe start/end)

`claude --version` at probe start and end: `2.1.251 (Claude Code)` (unchanged).
The committed fixture records `claude_version: "2.1.251"`; the tooth passes iff a
measured `shell_routing/v1` fixture's `claude_version` equals the installed CLI's
version. Smoke check (from the worktree):

```
match:   passes=True  (fixture shell_routing_2026-08-29_m0t120_2_1_251.json, verdict native_preferred)
stale:   reason_code=routing_evidence_stale   (installed_version=9.9.9)
absent:  reason_code=routing_evidence_absent  (empty/missing dir)
unknown: reason_code=cli_version_undetermined (no version supplied)
```

## 3. Red/green (removal-sensitive), verbatim

GREEN — the three touched/added test modules:

```
python -m pytest tools/test_agent_supervisor_routing_probe.py \
  tools/test_agent_supervisor_recovery_probes.py \
  tools/test_agent_supervisor_command_authority.py -q
=> 160 passed in 14.47s
  (routing_probe 27, recovery_probes 88, command_authority 45)
```

RED 1 — R295 tooth stubbed to always-pass (simulating the pre-change code):

```
FAIL: test_no_evidence_at_all_refuses_fail_closed            AssertionError: True is not false
FAIL: test_evidence_for_a_different_cli_identity_refuses      AssertionError: True is not false
FAIL: test_an_undetermined_cli_version_fails_closed           AssertionError: True is not false
Ran 3 tests ... FAILED (failures=3)
```

RED 2 — R294 guidance append made a no-op (simulating the pre-change code):

```
FAIL: test_the_guidance_is_appended_exactly_once             AssertionError: 0 != 1
Ran 1 test ... FAILED (failures=1)
```

## 4. Full supervisor suite (self-check, after the L1 follow-up)

```
python -m pytest tools/test_agent_supervisor_*.py -q
=> 2773 passed, 2 skipped in 201.30s
   2775 collected; +49 tests over the 2726 baseline; 0 failures
```

Modularity: `python tools/modularity_check.py --check` → `failures 0` (10
pre-existing warnings; EXIT 0). CI ruff runs only under `services/api/` (ci.yml
working-directory), so `tools/**` is not CI-linted; my new source is ruff-clean
apart from one PRE-EXISTING `F401` unused import (`AuditLog`) in
`test_agent_supervisor_recovery_probes.py` (last touched by M0-T115, not this
diff) — left untouched to avoid unrelated scope.

## 5. Windows-shape classifier coverage map (R293; classifier BYTE-UNTOUCHED)

Empirically captured against the installed classifier via `policy.evaluate`
(kind="command", tool_name="Bash"). Metacharacters `| > < & ; \n \r`;
substitution markers include `$(`, `` ` ``, `${`, `$env:`, `iex`,
`invoke-expression`, `-encodedcommand/-enc`, `| sh`, `| bash`.

| shape (Windows-style input)            | mechanism                     | tier / reason_code |
|----------------------------------------|-------------------------------|--------------------|
| PS here-string `@' ... '@` (newline)   | newline metacharacter         | ASK undocumented_command |
| pipeline `type f \| findstr b`         | metacharacter                 | ASK undocumented_command |
| redirection `> out.txt` / `< in.txt`   | metacharacter                 | ASK undocumented_command |
| compound `;` / `&&` / `&`              | metacharacter (segment split) | ASK undocumented_command |
| `cmd /c "dir & type f"` / `&&` chain   | metacharacter in the chain    | ASK undocumented_command |
| scratch copy `copy x %TEMP%\y`, Copy-Item | unknown program, 1 segment | ASK undocumented_command |
| ambiguous `$env:` read (non-concealing)| substitution, not concealing  | ASK undocumented_command |
| `iex (...)` / `-EncodedCommand`        | concealed dynamic execution   | HARD_DENY concealed_execution |
| credential read `$env:USERPROFILE\.netrc` | credential-path detection  | HARD_DENY credential_access |
| `del /s`, `rm -rf`, recursive delete   | recursive/wildcard delete     | HARD_DENY recursive_or_wildcard_delete |
| `--no-verify` / hooks-off              | CONTROL_DISABLING_MARKERS     | HARD_DENY control_disabling |

Security invariant verified for every shape above: **never AUTO** (unclassifiable
is ASK, never AUTO — policy S4.3). New assertions added in
`WindowsShapeCoverageTests`; the classifier itself is unchanged.

### Two recorded permissiveness FINDINGS (not fixed — classifier frozen; both stay GATED as ASK)

- **F1** `python gen.py | sh` (pipe raw output into an interpreter) classifies
  **ASK `undocumented_command`, not HARD_DENY `concealed_execution`** — the `| sh`
  substitution marker only hard-denies when it ALSO conceals a destructive segment
  or hits an iex/-enc marker. Still gated (ASK), never AUTO.
- **F2** a destructive delete wrapped as `powershell -Command "Remove-Item
  -Recurse -Force ..."` classifies **ASK `undocumented_command`, not HARD_DENY
  `recursive_or_wildcard_delete`** — the delete verb is inside the quoted
  `-Command` argument, so the segment program is `powershell` and the
  destructive-segment check does not reach inside the string. Still gated (ASK),
  never AUTO.

Both are captured as explicit tests (`test_finding_f1_*`, `test_finding_f2_*`) that
assert the current (ASK) behavior, so a future classifier change that tightens
them will surface as a test update rather than a silent drift.


## 6. L1 CLOSED — the R295 fold is LIVE and gates the certified run

`start_gate.live_revalidation` now applies, scoped to the certified `limited-auto`
run (R295: "cannot silently enter a **certified** run"):
```
if getattr(args, "mode", "") == MODE_LIMITED_AUTO:
    revalidation["cli_capability_manifest"] = bool(
        revalidation.get("cli_capability_manifest") and answers["shell_routing"].passes)
```
The pinned identity is the executable DIGEST (`_claude_identity_digest`, a file
hash — no `claude --version` spawn). Evidence is read from the shipped fixtures dir
(the REAL claude, `cli_identity d6f6c29a…`) AND the durable journal
(`SHELL_ROUTING_EVIDENCE_KEY`, the M0-T072 bound-manifest precedent for fake-CLI
harnesses).

### 6a. Tooth BITES — certified start with evidence CLEARED (verbatim)

`golden_run.clear_routing_evidence` removes the seed; the certified start refuses:
```
dispatched: False   provider_calls: 0   exit_outcome: unsafe 11
classification: UNSAFE_OR_DRIFTED   failed_steps: ['cli_capability_manifest']
shell_routing.passes: False   reason: routing_evidence_stale
shell_routing.detail: shell-routing evidence exists but only for
  ['d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8'], not the
  pinned CLI identity '87e1498008d330a2924c673f3b44d4d81a0bf2b264f6b8db6122f55c4c98a2d4';
  changed shell-routing behavior must be re-measured before it enters a certified run
```
Permanent test: `TwoUnitGoldenRunTests::test_the_routing_tooth_bites_a_certified_start_without_evidence`.

### 6b. Seeded GREEN

- `golden_run` pack: **42 passed** (was 41; +1 tooth-bites). Every dispatching
  limited-auto golden start passes because `GoldenRunBase.setUp` records routing
  evidence for its own fake identity in the temp runtime journal.
- Full suite: **2780 passed, 2 skipped** (2782 collected), 0 failures.

### 6c. Real-production path preserved (instruction 5)

`probe_shell_routing_evidence(installed_identity=<real claude digest d6f6c29a…>)`
PASSES against the committed fixture (test
`RoutingFixtureShapeTests::test_the_committed_fixture_passes_for_the_real_claude_digest`).
So the genuine installed claude is not gated out — only a CHANGED, un-re-measured
CLI identity refuses.

### 6d. Why limited-auto scoping (not unconditional)

An unconditional fold additionally refused shadow/supervised cmd_start starts in
SIX files (25 failures), THREE of them outside even the twice-extended allowed
paths (`manifest_binding`, `model_chain`, `start_reentry`). Scoping to `limited-auto`
is faithful to R295's "certified run", is not a weakening (the tooth still runs and
reports in every mode; only its GATING effect is scoped to the unattended run), and
avoids editing unadmitted files. To gate every mode instead, admit those three
files and drop the one-line mode guard.

### 6e. Golden blob moves (R296)

These edits change the supervisor tree hash; the single M0-T119 recertification
certifies the new final identity (accepted by the orchestrator).

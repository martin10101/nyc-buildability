# M0-T117 — DISABLE_AUTOUPDATER=1 evidence (red/green + owner-side command pack)

Task: M0-T117 (D-024 Amendment 13 unit Q). Producer: backend-engineer.
Worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t117`
(`git rev-parse --show-toplevel` verified this exact path before any other command).
Python: 3.11.9 (sandbox). Interpreter: `C:\Users\MLFLL\AppData\Local\Programs\Python\Python311\python.exe`.

The change forces `DISABLE_AUTOUPDATER=1` into the environment of every
controller-launched CLAUDE child, at both `claude_runner` Popen sites, via a new
claude-scoped helper `process.claude_child_env` (applied AFTER the env allowlist and
any config `extra_env`). Codex children (which use the shared `minimal_env`) are
untouched.

Fail-closed choice for AS-6: **the forced pair wins**. A config `extra_env` that
supplies a conflicting `DISABLE_AUTOUPDATER` value (e.g. `"0"`) is overridden back to
`"1"` rather than raising. Rationale: the guarantee this control exists to make is
that NO input (parent env, allowlist, or config) ever yields a controller-launched
claude child without `DISABLE_AUTOUPDATER=1`. An unconditional forced value delivers
that for every input; a launch-time typed refusal is strictly weaker (it fails the
launch on a config typo instead of neutralizing it, and adds an error path that could
itself regress to fail-open).

---

## RED — AS-1/AS-2 against UNMODIFIED production code (meaningful failure)

The AS-1/AS-2 tests intercept the real `subprocess.Popen` at both claude call sites
and assert the captured `env` carries the var. Against unmodified code the env is
built by `minimal_env` and lacks it — `None != '1'`:

```
$ python -m pytest "tools/test_agent_supervisor_claude_runner_env.py::ClaudeChildEnvInjectionTests" -q

    def test_as1_worker_launch_injects_even_when_parent_and_allowlist_omit_it(self) -> None:
        ...
        store: dict[str, object] = {}
        with mock.patch("subprocess.Popen", _capturing_popen(store)):
            with self.assertRaises(_StopLaunch):
                cr.ClaudeRunner(_base_config()).run_unit("probe prompt")

        env = store["env"]
        assert isinstance(env, dict)
>       self.assertEqual(env.get("DISABLE_AUTOUPDATER"), "1")
E       AssertionError: None != '1'

tools\test_agent_supervisor_claude_runner_env.py:85: AssertionError
___ ClaudeChildEnvInjectionTests.test_as2_probe_launch_injects_identically ____
        ...
>       self.assertEqual(env.get("DISABLE_AUTOUPDATER"), "1")
E       AssertionError: None != '1'

tools\test_agent_supervisor_claude_runner_env.py:97: AssertionError
=========================== short test summary info ===========================
FAILED tools/test_agent_supervisor_claude_runner_env.py::ClaudeChildEnvInjectionTests::test_as1_worker_launch_injects_even_when_parent_and_allowlist_omit_it
FAILED tools/test_agent_supervisor_claude_runner_env.py::ClaudeChildEnvInjectionTests::test_as2_probe_launch_injects_identically
2 failed in 0.24s
```

Full new module against unmodified code (AS-3/AS-5/AS-6 additionally red because the
helper does not yet exist):

```
$ python -m pytest tools/test_agent_supervisor_claude_runner_env.py -q
...
E   AttributeError: module 'tools.agent_supervisor.process' has no attribute 'claude_child_env'
...
=========================== short test summary info ===========================
FAILED ...::test_as1_worker_launch_injects_even_when_parent_and_allowlist_omit_it
FAILED ...::test_as2_probe_launch_injects_identically
FAILED ...::test_as3_no_collateral_change_vs_minimal_env
FAILED ...::test_as3_only_difference_is_the_single_forced_key
FAILED ...::test_as6_extra_env_conflict_is_overridden_forced_pair_wins
FAILED ...::test_as6_unrelated_extra_env_still_passes_through
FAILED ...::test_as5_codex_channel_still_uses_the_uninjected_builder
7 failed, 1 passed in 0.43s
```

(The 1 pass is `test_as5_shared_minimal_env_does_not_inject_the_control`, correctly
green both before and after — `minimal_env` never injects the control.)

---

## GREEN — after implementing `claude_child_env` and wiring both call sites

```
$ python -m pytest tools/test_agent_supervisor_claude_runner_env.py tools/test_agent_supervisor_process.py -q
..................................s....                                  [100%]
38 passed, 1 skipped in 9.43s
```

- new module `test_agent_supervisor_claude_runner_env.py`: 8 tests, all pass
  (AS-1, AS-2, AS-3 x2, AS-5 x2, AS-6 x2).
- `test_agent_supervisor_process.py`: +2 new tests
  (`test_minimal_env_does_not_inject_the_claude_autoupdater_control`,
  `test_claude_child_env_forces_the_autoupdater_control`) — 30 pass, 1 skip
  (pre-existing skip unrelated to this change).

---

## AS-4 — REMOVAL SENSITIVITY (injection line proven load-bearing)

With the single injection line `env.update(FORCED_CLAUDE_CHILD_ENV)` temporarily
removed from `claude_child_env` (helper still present), the injection- and
seam-dependent tests go red — a real `KeyError`/`None != '1'`, not a missing symbol:

```
$ python -m pytest tools/test_agent_supervisor_claude_runner_env.py tools/test_agent_supervisor_process.py -q
...
>       self.assertEqual(pc.claude_child_env()["DISABLE_AUTOUPDATER"], "1")
E       KeyError: 'DISABLE_AUTOUPDATER'
tools\test_agent_supervisor_process.py:244: KeyError
=========================== short test summary info ===========================
FAILED ...claude_runner_env.py::...::test_as1_worker_launch_injects_even_when_parent_and_allowlist_omit_it
FAILED ...claude_runner_env.py::...::test_as2_probe_launch_injects_identically
FAILED ...claude_runner_env.py::...::test_as3_no_collateral_change_vs_minimal_env
FAILED ...claude_runner_env.py::...::test_as3_only_difference_is_the_single_forced_key
FAILED ...claude_runner_env.py::...::test_as6_extra_env_conflict_is_overridden_forced_pair_wins
FAILED ...claude_runner_env.py::...::test_as6_unrelated_extra_env_still_passes_through
FAILED ...process.py::EnvironmentTests::test_claude_child_env_forces_the_autoupdater_control
7 failed, 31 passed, 1 skipped in 9.46s
```

Injection line restored → green again:

```
$ python -m pytest tools/test_agent_supervisor_claude_runner_env.py tools/test_agent_supervisor_process.py -q
..................................s....                                  [100%]
38 passed, 1 skipped in 9.33s
```

---

## Full supervisor suite

```
$ python -m pytest tools/test_agent_supervisor_*.py -q
...
3 failed, 2717 passed, 2 skipped in 192.08s (0:03:12)
```

Collected 2722 = baseline 2712 + 10 new (8 new module + 2 in process module).

The 3 failures are ALL the same pre-existing live drift tooth — installed CLI
`2.1.251` vs the committed fixture `2.1.248` (AD-093 drift, M0-T118's fixture-recapture
scope), and are unrelated to this change (this change touches env building, not version
detection):

- `tools/test_agent_supervisor_capability_probe.py::test_live_reprobe_claude_version_matches_fixture`
- `tools/test_agent_supervisor_event_bus.py::test_s8_live_version_matches_catalog_fixture`
- `tools/test_agent_supervisor_native_adapter.py::test_live_detection_matches_committed_fixture`

All three assert `'2.1.251 (Claude Code)' == '2.1.248 (Claude Code)'` and fail by
design until M0-T118 recaptures fixtures. NOT fixed or touched by this task.

NOTE / deviation: the packet named ONE expected drift-tooth failure
(`test_s8_live_version_matches_catalog_fixture`); in fact there are THREE live-drift
teeth (capability_probe, event_bus, native_adapter), all failing for the identical
`2.1.251`-vs-`2.1.248` reason. All are pre-existing and out of scope.

---

## OWNER-SIDE command pack (OWNER-EXECUTED — NOT run by this producer, R288)

Recorded verbatim from the packet. An agent NEVER sets a machine-scope environment
variable; this is an owner action in an Administrator PowerShell during the
certification window (defense in depth — the forced per-child injection does not
depend on it).

```powershell
# Set (Administrator PowerShell):
[Environment]::SetEnvironmentVariable('DISABLE_AUTOUPDATER', '1', 'Machine')

# Verify stored value (any new PowerShell window)  -> must print 1:
[Environment]::GetEnvironmentVariable('DISABLE_AUTOUPDATER', 'Machine')

# Verify inheritance (any NEW terminal)  -> must print 1:
$env:DISABLE_AUTOUPDATER
```

Behavioral check: `claude doctor` reports the result of the most recent update
attempt; already-running terminals keep their old environment and must be restarted.

None of the above owner-side commands were executed by this producer.

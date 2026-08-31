# M0-T127 - R247 recertification at the Amendment-22 final frozen identity (D-024-R390)

Executed by the orchestrator (`orchestrator-recert-runner`) 2026-08-31 in the PRIMARY control
checkout (certification environment). ONE recertification at ONE identity, per R390.

## 1. The final frozen identity

| Anchor | Value |
|---|---|
| Material commit (supervisor content) | `2d46fb0` (M0-T126 remediation; accepted at `b325e37`) |
| `tools/agent_supervisor` tree | `46722aa1af8f92f063d74b638a5a04e996a1f52d` |
| Golden pack blob | `deeca07b` (moved from `c54fd0d2` by the DISCLOSED M0-T126 D10 correction: the golden restart row previously passed only via the D10 bug; change reviewed by G3/G4/DCV) |
| Launch-seam pack blob | `0aed4902` (D2 repo-binding tests added) |
| Provider CLI | Claude Code **2.1.251 UNDRIFTED** - supervisor-native identity `sha256_head+size` digest `d6f6c29a8ac6b3cf...` reproduced exactly this session; size 217,360,032 B; NO admission event, NO repin. (A raw full-file `Get-FileHash` differs by design - the admitted scheme is the supervisor's `executable_identity`.) |
| Codex CLI | codex-cli **0.146.0** unchanged |
| Registry | `validate_directive_compliance.py --check` EXIT=0 at this content |

## 2. Golden certification pack - 42/42, and the 3h13m figure RESOLVED

* **Canonical single-process run** (`python -m pytest tools/test_agent_supervisor_golden_run.py -q`):
  **42 passed, 0 failed in 52.20s.**
* **Sharded corroboration** (5 concurrent processes, every one of the 42 tests exactly once):
  Soak 2/0.48s; AcceleratedOvernight 1/0.86s; AutonomousSelection+CampaignCrossing 3/0.51s;
  ExtendedPause+OnDemandAfterCompact+registers 9/4.20s; fast-27 27/25.34s. A two-class
  concurrent parallel-safety probe preceded the shards (both clean).
* **Timing-anomaly resolution (owner question 2026-08-31):** the recorded "3h13m" golden cost
  (M0-T125 G4 observation O2, `42 passed in 11616.50s`) is an environmental artifact of that
  ONE reviewer session, not intrinsic test time: the M0-T119 certification measured the SAME
  pack at **15.00s**, and at this identity every class measures sub-5 seconds individually.
  The O2-based ~3h budget carried into this window's planning is retired; certification cost
  is now recorded honestly as under one minute.

## 3. Suite evidence at the frozen identity

| Run | Result |
|---|---|
| WHOLE supervisor suite - all 70 `test_agent_supervisor_*.py` files INCLUDING golden, one process | **2,990 passed, 2 skipped, 0 failed** (449.11s; the 2 skips are the pre-existing env `skipif` pair, unchanged since M0-T125) |
| 25 core packs (independent shard, same session) | 1,205 passed, 1 skipped |
| 8 defect packs (three independent reproductions this window: orchestrator, G4 delta, DCV) | **401 passed** each time (next_task 18, command_docs 17, orientation 13, checkpoint_journey 25, recovery 63, launch_seam 69, loop 122, runner 74) |

**Baseline reconciliation (freeze rule):** M0-T124 whole-suite baseline **2,889** + net **+101**
M0-T126 tests (73 in the four new packs command_docs/orientation/checkpoint_journey/next_task +
28 net across launch_seam/loop/recovery/runner/golden and remediation additions) = **2,990**.
No test removed; the one golden-row change is the disclosed D10 correction (section 1).
**Labeling correction for the record:** the M0-T126-era phrase "full suite excl. golden = 2990"
(producer return 3, G4 delta) was mislabeled - 2,990 IS the whole suite including golden (the
`--ignore` had not bitten); no pass/fail conclusion changes (golden passes standalone 42/42 and
inside the suite; the same tests ran under both labels).

## 4. Controller binding, doctor, and preservation

* `record-manifest` from the ctl24 root: **125 files**, manifest digest `a43f133b2bf49c0e...`,
  external `config.toml` bound, round-trip verification passed. Prior stored manifest
  (sha256 `83430212...`) recorded here for provenance before overwrite - re-recording the
  activation manifest at the newly certified tree IS the certified procedure (T112/T116/T119/
  T122/T124 precedent); it is not a preserved-evidence artifact.
* `verify-controller`: PASS ("controller verified, including the external config.toml binding").
* `doctor` (full, non-live) against the ctl24 journal: **overall PASS**, config OS-ACL posture
  **PROTECTED**, model-selection accepted, journal integrity ok.
* `doctor --live` NOT re-run in-window (R375 caution: it contacts the provider binary; the
  admitted control-response evidence stands - seq-30 VERIFIED `d6f6c29a8ac6b3cf` - and section 1
  proves the executable identity is byte-identical, so the probe's subject is unchanged).
* **Preservation (R374) verified BEFORE and AFTER the battery:** journal
  `current_state=PAUSED_RECOVERY`, transitions **22**, audit **53** records, effects/outbox/
  inbox **0**; `wt-m0t107` clean at `796e18f`; worker transcript 97 lines. Identical counts at
  G0, after doctor, and at report time. No restart, no clear-recovery, no journal edit, no
  repin, no PR #241 action, no live launch.

## 5. Tooling teeth at the identity

`modularity_check --check` failures 0 (335 files); `supervisor_command_doc_check.py` exit 0
(12 presented commands, 0 drift - now CI-wired by M0-T126 D1); CI **20/20 success** on the
pushed chain at the material commit and at the M0-T127 G0 tip `1c82a50`; validator EXIT=0.
Both presented commissioning commands in the stabilization report were dry-run validated this
session against `build_parser()` + the pinned-flag set + `dispatch_inputs_missing` (both OK) -
the D17 lesson made mechanical.

## 6. Verdict

R247 recertification: **PASS at the one final frozen identity** (material `2d46fb0`). The
certification cost question is closed (section 2). Carried non-blocking observations for the record:
DCV obs 2 (one producer-recomputed runbook digest not sandbox-recomputable), DCV obs 5
(runbook `wt-m0t063` residual EXAMPLES outside the register's D15 scope - candidate follow-up),
G3 O1 (the tooth scans the runbook only; certification packages re-derive presented commands -
done mechanically for this package, see section 5), G4 O2 (exact-at-ceiling unit-scope naming).

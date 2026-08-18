# M0-T072 producer report — external-config manifest binding repair

Producer: orchestrator (M0-T070 precedent). Branch `task/M0-T072-manifest-config-binding`,
base `4a604ff` (D-017 capture). Governing rows: D-017-R037..R053, bound at claim.
Freeze-lane qualifying evidence: `project-control/reports/M0-T072-defect-evidence.md`
(reproduced defect + demonstrated security risk, cited per supervisor-freeze §3).

## What changed (scope: exactly the allowed paths)

- `tools/agent_supervisor/manifest.py` (+~120 lines, additive):
  `CONFIG_LOGICAL_NAME = "config.toml"`; `ManifestVerification.reason_code`;
  `manifest_is_stale()` (wrong running controller version, or an edited manifest whose
  recorded digest no longer matches its own recorded content); and
  `verify_manifest_with_config()` — the ONE production check, fail-closed in order:
  `manifest_stale` → `config_duplicated_in_package` (an in-package config.toml would
  shadow the external binding; D-017-R048) → `manifest_missing_config` →
  `config_path_missing` → content verification with the external config bound under
  its stable logical name (missing → `missing`, byte change → `changed`).
- `tools/agent_supervisor/cli.py`:
  - doctor `_check_manifest(manifest, config)` uses the production check; `--manifest`
    without `--config` fails closed; the no-manifest result now states NOTHING was
    verified (D-017-R042).
  - `verify-controller` gains `--config`; without `--manifest` it FAILS CLOSED instead
    of self-generating and reporting ok having verified nothing (D-017-R043).
  - `record-manifest` (new): the only supported way to record a production manifest —
    binds the external config by logical name, never writes the absolute path,
    refuses an in-package config.toml, round-trip verifies before reporting success
    (D-017-R039/R040/R041).
  - `start`: `--manifest` added to the required dispatch inputs; when supplied the
    manifest is verified WITH the external config before any provider contact; the
    journal payload records the `manifest_binding` verdict; a FAILED verification
    exits non-zero (missing-input stops still exit 0) (D-017-R044/R045).
- `tools/agent_supervisor/README.md`: external-binding contract + record-manifest
  procedure; the false "covered by the controller manifest" claim corrected to the
  real external-binding mechanism.
- `docs/CONTROLLER_UPDATE_RUNBOOK.md` (new): regenerated from this merged source —
  PowerShell-native (backticks, no CMD carets), resolved executables, non-destructive
  timestamped backups (no /MIR), `doctor --live` as the ONLY bounded live probe,
  every status/stop naming its `--checkout`, exact rollback (D-017-R053 + R051 item 9).
- `tools/test_agent_supervisor_manifest_binding.py` (new): 27 tests covering
  AS-1..AS-9 (packet) = the nine D-017-R051 proofs; see the mapping in
  `M0-T072-before-after-evidence.md`.

Explicitly NOT changed: the protected config (byte-identical, never read for write);
model_selection.toml; policy.py/broker.py/loop.py/config.py; any A1 file; the live
controller. Test-only synthetic-root manifest flows (phase1) remain valid (D-017-R047):
the in-package-config guard applies to the production entry points only.

## Test evidence (all at this branch, Python 3.11.9, Windows)

- New regression suite: `python -m pytest tools/test_agent_supervisor_manifest_binding.py`
  → **32 passed** (round-1 rework added AS-1 start dispatch positive control, AS-8
  through production dispatch, patterns-mismatch, excluded-source-name, schema).
- Full battery `python -m pytest tools/ -q` at be3a599 → **1845 passed, 2 skipped, 0 failures**
  (12m35s) — re-establishing the M0-T039 freeze baseline (≥1165, 0 failures) with the
  repair applied. Includes the full supervisor, project-control, directive-compliance,
  and new regression suites (D-017-R052).
- Targeted pre-battery run of the nine modules that reference the changed surfaces
  (broker, endurance, ipc, loop, model_chain, phase1, reviewer, runner, start_reentry):
  **561 passed**.
- Disclosure: an earlier full-battery attempt was externally stopped at ~93% and its
  progress line showed 5 failures in one cluster; the failure names were never printed
  (killed before the summary) and the complete clean rerun above reproduced none of
  them. No test was modified between those runs.

## Requirement disposition notes

- D-017-R046 (model_selection excluded by design): unchanged EXCLUDED_NAMES mechanism +
  AS-6 test.
- D-017-R049/R050 (no symlink/hardlink workaround; no config duplication): no link of
  any kind is created anywhere; duplication is actively REFUSED by both record-manifest
  and the production verification.
- D-017-R051 item 8 (doctor --live remains the only intentional bounded live probe):
  no new live-call path was added; the runbook states it and the AS-9 test enforces the
  runbook wording; `start` is documented as never being a probe.
- D-017-R053 (runbook from merged source): the committed runbook cites only commands
  that exist in this source; the AS-9 test fails on CMD carets or unresolved
  executable placeholders.

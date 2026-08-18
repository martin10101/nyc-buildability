# M0-T072 defect evidence — external-config manifest binding (AD-093 defect lane)

Qualifying evidence for the supervisor-freeze rule (§2/§3), reproduced read-only at
main@`026e7cb` (`task/M0-T072-manifest-config-binding` base `4a604ff`). Line numbers refer
to the PRE-repair source at that identity.

## Reproduced defect

1. **Config binding structurally unreachable.** `manifest.generate_manifest` /
   `verify_manifest` accept `extra_files` `(logical_name, path)` pairs designed for the
   external config (`manifest.py:138-150`, `:203-208`), but `verify_manifest` is called
   WITHOUT `extra_files` on every CLI path: doctor `cli.py:443`, verify-controller
   `cli.py:1551`, start `cli.py:2704-2705`. Repo-wide, the only `extra_files` caller was a
   negative test (`test_agent_supervisor_phase1.py:574`). Consequence: a manifest that
   correctly recorded a `config.toml` logical entry would FAIL verification as `missing` —
   binding the config was not merely skipped, it was impossible through the CLI, and the
   only manifest that could pass was one that omitted the config.
2. **`start` without `--manifest` silently passed.** `manifest_ok = ... if args.manifest
   else True` (`cli.py:2704-2705`), and `--manifest` was absent from the required dispatch
   inputs (`_dispatch_inputs_missing`, `cli.py:2228-2237`), so production dispatch could
   proceed with `controller_manifest: True` having verified nothing.
3. **`verify-controller` had no `--config`** (`cli.py:3023-3028`) and, with no
   `--manifest`, self-generated a manifest and reported `ok: true` unconditionally
   (`cli.py:1529-1545`) — a verification command that verified nothing.
4. **No CLI command recorded a manifest.** `write_manifest` had no production caller and
   was not imported by `cli.py`; no `controller_manifest.json` existed anywhere; the
   README documented no generation procedure (only `--manifest <path to a recorded ...>`).
5. **No staleness check.** `generated_at_utc` had zero readers; the recorded
   `controller_version` was never compared to the running `CONTROLLER_VERSION`; the
   recorded `manifest_digest` was copied through verbatim and never recomputed
   (`manifest.py:203-236`), so an edited manifest was self-consistent by construction.
6. **`require_verified`** — the "before every forwarded action" enforcement promised in
   `manifest.py:3-8` — had zero production callers.

## Demonstrated security risk

Production dispatch could proceed with a manifest that omitted the active immutable
config entirely, defeating the config-binding guarantee documented in
`tools/agent_supervisor/README.md` ("config.toml — immutable, covered by the controller
manifest", pre-repair line 454), while the protected config at
`C:\Program Files\SupervisorConfig\config.toml` lay outside the package tree that
`verify_manifest(PACKAGE_ROOT, …)` covered.

## Runbook consequence (why this blocked D-017 Stage 2)

The superseded runbook `CONTROLLER_UPDATE_RUNBOOK_2026-08-18.md` §5 generated the
manifest with plain `generate_manifest(pathlib.Path('tools/agent_supervisor'))` — no
`extra_files` — while asserting "config.toml IS covered"; executing it would have
deployed a live controller whose manifest never bound its protected config. Its
commands also used CMD-style caret continuation (`^`) inside a PowerShell workflow
(§13) and unresolved executable placeholders. Regenerated replacement:
`docs/CONTROLLER_UPDATE_RUNBOOK.md` (from merged source; PowerShell backticks; resolved
paths; `doctor --live` as the only bounded live probe; every `status`/`stop` names its
`--checkout`).

## Repair identity

Additive `verify_manifest_with_config` + `manifest_is_stale` + `CONFIG_LOGICAL_NAME`
(`manifest.py`); doctor/verify-controller/start wired to the same production
verification; `record-manifest` command; `--manifest` added to required dispatch
inputs; failed verification exits non-zero and never contacts a provider. Proven by
`tools/test_agent_supervisor_manifest_binding.py` (33 tests, AS-1..AS-9 + guard regressions).

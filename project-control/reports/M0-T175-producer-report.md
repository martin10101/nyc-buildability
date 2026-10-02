# M0-T175 producer report — D-091 TW5 Linux commissioning checklist

Task: M0-T175 (D-091 TW5). Producer: cloud-architect. Branch: `task/M0-T175-linux-commissioning`.
Directive refs: D-091-R001, D-091-R006, D-091-R007, D-091-R008.

## What this increment is

This first increment is the **checklist only**. The owner's commissioning steps (root config,
Codex sign-in, systemd install, supervised certified start) and the lane-1 canary evidence are
**still pending** — they are owner-typed and happen at commissioning time. This report records the
checklist and its evidence; it records no owner action and no canary result (none has happened).

## What I wrote

Replaced the placeholder `docs/D091_LINUX_COMMISSIONING.md` with a short, plain-words checklist:
a 5-line summary, then numbered owner-typed steps, each with the exact command to type and the
orchestrator's read-only check right after it; a combiner-OFF step with a separate later enable
step; an "if a step fails" stop rule; and an owner-only note at the top.

Scope held to the two allowed files only: `docs/D091_LINUX_COMMISSIONING.md` and this report. No
other file touched. No commissioning command, `systemctl`, `codex login`, or `sudo` was run; I ran
only read-only `grep`/`sed`/`ls` to verify facts.

## Steps and the orchestrator's check (one line each)

1. Root config — `install -m 0444 -o root` the example to `/etc/nyc-supervisor/config.toml`, fill
   model allowlists → check `doctor` prints OS-ACL posture `PROTECTED` + `verify-controller` binds the config.
2. Codex sign-in (OD-C) — owner `codex login` → check `codex --version` = `codex-cli 0.157.0`.
3. systemd unit — fill the template placeholders, install, `daemon-reload`, `enable` → check
   `systemd-analyze verify` parses, unit carries `DISABLE_AUTOUPDATER=1`, ExecStart runs `launch.sh`.
4. Supervised certified start of lane 1 (canary) — owner approves the certified-start prompt-digest
   and `systemctl start` → check stored evidence: gate passed, one clean cycle, memory under the 70%
   ceiling, review cap (2 global / 1 per lane) honored.
5. Combiner OFF until OD-B — leave the switches absent (default off); later enable step adds
   `review_combiner.enabled`/`model` + `claude.reviewer_enabled`/`reviewer_model` once the owner names the model.

## Every fact with its file:line source

- POSIX config default path `/etc/nyc-supervisor/config.toml`: `tools/agent_supervisor/config.py:375-383`
  (`default_config_path`), note `:377-378`; `platform_paths` delegation `:382-383`.
- Config keys to fill: `[codex] allowed_models` `config.example.toml:24,28`; `[claude] allowed_models`
  `:30,34`; `[approved_models] models` `:36,78`.
- PROTECTED verdict (POSIX) = root-owned uid 0 + not group/world-writable + protected parent + no
  symlink, fail-closed: `tools/agent_supervisor/posix_acl.py:77-145` (owner/mode `:117-137`, symlink
  `:110-117`, parent `:179`, combine `:159-169`); OS dispatch `os_acl.py:478-495` (POSIX branch `:493-495`).
- `doctor` emits the ACL posture: `cli.py:1419` (compute), `:1435` (payload key), `:510-533` (builder),
  `:1456-1459` (printed line). `doctor`/`verify-controller` module entry `python -m tools.agent_supervisor`
  (`__main__.py` present; subcommands `cli.py:13`, verify-controller parser `cli.py:3468`).
- Manifest binds config: `manifest.py:47,54` (`CONFIG_LOGICAL_NAME = "config.toml"`); verify-controller
  expectation runbook section 6 (`docs/CONTROLLER_UPDATE_RUNBOOK.md:177-195`).
- Codex admitted version `0.157.0`: pin `tools/codex_cli/package-lock.json:16`; certified fixture
  `tools/agent_supervisor/fixtures/capability_probe_live_2026-10-02_m0t174_2_1_287.json:62`
  (`"codex-cli 0.157.0"`); claude certified `2.1.287` same fixture `:44`.
- Reviewer reads none of the owner's personal config: `--ignore-user-config` `codex_reviewer.py:135`
  (reason `:17`, canonical argv `:55`).
- systemd template facts: `tools/agent_supervisor/linux/nyc-supervisor.service.template` —
  `DISABLE_AUTOUPDATER=1` `:22`; no `[Install]` + `Restart=no` `:8-9,30`; ExecStart→`launch.sh` `:29`;
  owner placeholders `User :18`, `WorkingDirectory :19`, `NYC_SUP_CLAUDE_BIN :26`, `NYC_SUP_GATE_CMD :27`,
  `NYC_SUP_START_CMD :28`.
- Launcher fail-closed gate: `tools/agent_supervisor/linux/launch.sh` — gate refuse exit 5 `:78-82`,
  binary exit 3 `:62-64`, env exit 4 `:67-72`, hands gated start only on pass `:84-88`.
- 70% memory ceiling: `resource_sampling.py:160` (`MEMORY_PAUSE_FRACTION = 0.70`), `:232`
  (`resolve_memory_ceiling_bytes`), `:297` (`linux_memory_gauge_sample`); config note
  `config.example.toml:112-118`, `max_memory_bytes` `:123`.
- Review cap: `run_budget.py:793` (`admit_review_or_combine`); caps `config.example.toml:137`
  (global `= 2`), `:138` (per-lane `= 1`); atomic, fail-closed reservation `review_slots.py:28-30`;
  conductor acquires a slot before each spawn `dual_review.py:309-313`.
- Combiner/reviewer OFF by default: `review_combiner.py:459-467` (reader), `:420` (key
  `"review_combiner"`), `:433-434` (dataclass defaults `enabled=False`, `model=""`);
  `claude_reviewer.py:395-403` (reader), `:364-365` (dataclass defaults).
- Combiner enable guards: model required, no default `review_combiner.py:512-516` and
  `dual_review.py:239-245`; combiner default-off refusal `dual_review.py:246-250`; combiner model must
  be on the `[claude]` allowlist `dual_review.py:251-256`.
- OD-B recommendation (Opus 5.5) already recorded: `docs/SESSION_HANDOFF.md:51`.

## NOT FOUND items (orchestrator to confirm)

1. **A code check that the combining model is literally DIFFERENT from the Claude reviewer model.**
   Not found. The code enforces reviewer/combiner **identity** independence
   (`review_combiner.py:572-584` `_assert_independent`) and the allowlist (`dual_review.py:251-256`),
   not a model-string inequality. "Distinct models for reviewer vs combiner" is a design mitigation
   (`D091_WAVE3_WIRING_PLAN.md:174-175`), and `SESSION_HANDOFF.md:51` says "commissioning checks that".
   The checklist flags this and asks the orchestrator to confirm whether a model-string check is added
   before enabling.
2. **`review_combiner.enabled` / `claude.reviewer_enabled` keys are not present in
   `config.example.toml`.** Off is the default (absence = off), so the checklist's "keep it off" act is
   to leave them absent; an explicit `enabled = false` belt is optional.
3. **The exact controller start command and lane-1 selection** are owner-configured in
   `NYC_SUP_START_CMD` (`template:28`), not a fixed command in the repo. Orchestrator confirms with the owner.
4. **`doctor`/`verify-controller` Linux paths** for `--manifest` and `--model-selection`: the runbook's
   examples are Windows (runbook section 6-7); the Linux equivalents are supplied by the owner/orchestrator.

## Self-checks run

- Read the doc once as the owner would: steps are plain, each has a command then its check, the
  owner-only note is at the top, the stop rule is at the bottom.
- Verified every cited key/path/flag/line against the repo with `grep`/`sed` (POSIX ACL rules,
  config keys and line numbers, codex version pin and fixture, systemd template lines, launcher exit
  codes, memory 70% constants, admission caps, combiner/reviewer switch defaults, CLI subcommands).
- Ran no commissioning command, no `systemctl`, no `codex login`, no `sudo`, installed nothing.

## Pending (not in this increment)

The owner's four steps and the lane-1 canary evidence are pending — this increment delivers the
checklist only. When the owner runs the steps, the orchestrator records the canary evidence
(gate passed, one clean cycle, memory under 70%, review cap honored) and the OD-B model choice.

END-OF-REPORT

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

## NOT FOUND items — resolution (rework 1)

1. **Combining model DIFFERENT from the Claude reviewer model — RESOLVED by a read-only
   orchestrator check (no code change now).** A code-level gate would touch `tools/agent_supervisor/**`
   and void the M0-T174 certification, so it is logged as a later improvement. The checklist's step 5
   now carries an explicit `python3 -c` (tomllib) check run before the owner starts with the combiner
   on: it reads `/etc/nyc-supervisor/config.toml` and prints `PASS` only when `[review_combiner].model`
   and `[claude].reviewer_model` are both present, non-empty, DIFFERENT, and both in
   `[claude].allowed_models`; otherwise `STOP` and the owner does not start. Keys verified against the
   code: `[review_combiner].model` (`review_combiner.py:512-516`, field `:434`), `[claude].reviewer_model`
   (`claude_reviewer.py:384`), `[claude].allowed_models` (conductor allowlist `dual_review.py:251-256`,
   example `config.example.toml:34`). The already-written identity-independence
   (`review_combiner.py:572-584`) and allowlist facts are kept.
2. **`doctor`/`verify-controller` Linux paths — RESOLVED with code defaults.** The CLI arg defaults
   are `None`, so the owner/orchestrator passes them: `--config /etc/nyc-supervisor/config.toml`
   (`platform_paths.py:41`, `:67-77`); `--manifest "${XDG_CONFIG_HOME:-$HOME/.config}/nyc-supervisor/
   ctl24-activation/controller_manifest.json"` (POSIX default `platform_paths.py:80-97`, `:101-107`;
   filename `manifest.py:38`; the manifest file is produced by record-manifest at activation, and
   `verify-controller` without `--manifest` fails closed, `cli.py:480-489`). `--model-selection` has
   **no** platform default in code — the owner supplies the runtime `model_selection.toml` path
   explicitly (`cli.py:3250-3251`); it lives outside the manifest. No path invented.
3. **`NYC_SUP_START_CMD` — RESOLVED as far as the repo defines it; the concrete value stays
   orchestrator-prepared.** launch.sh requires the value to be the **gated controller start**, run only
   on a passing gate, adding no push/merge/run of its own (`launch.sh:28-29`, `:84-88`). The gated start
   is the supervised `start` subcommand: `python -m tools.agent_supervisor start --mode supervised
   --config /etc/nyc-supervisor/config.toml --model-selection <path> --approve-prompt-digest <digest>`
   (`cli.py:3289` mode, `:3309` config, `:3310` model-selection, `:3335` approve-prompt-digest); the canary is
   one single-task start (`--max-tasks` default `1`, `cli.py:3329`); there is **no** `--lane` flag, so
   "lane 1" means this single canary start. The repo does NOT define a fixed concrete value — it is
   environment-driven (`launch.sh:23-29`) and a `<...>` placeholder (`template:28`); the exact flag
   string (model-selection path, prompt-digest) is orchestrator-prepared and shown to the owner before
   step 4, not invented.
4. **`review_combiner.enabled` / `claude.reviewer_enabled` not in `config.example.toml` —
   RESOLVED (informational).** The readers treat absence as off (`review_combiner.py:459-467`,
   `claude_reviewer.py:395-403`), so the safe act is to leave them out; an explicit `= false` belt is
   optional. Reworded in the doc as a resolved note, not an open NOT FOUND.

Nothing remains open: all four are resolved in-place with file:line evidence.

## Self-checks run

- Read the doc once as the owner would: steps are plain, each has a command then its check, the
  owner-only note is at the top, the stop rule is at the bottom.
- Verified every cited key/path/flag/line against the repo with `grep`/`sed` (POSIX ACL rules,
  config keys and line numbers, codex version pin and fixture, systemd template lines, launcher exit
  codes, memory 70% constants, admission caps, combiner/reviewer switch defaults, CLI subcommands).
- Rework 1: verified `platform_paths.py` POSIX defaults (config/manifest/activation/runtime),
  `MANIFEST_FILENAME` (`manifest.py:38`), the `start` subcommand flags (`cli.py:3289/3309/3310/3329/3335`),
  the absence of a `--lane` flag, the tomllib check's key names against the code, and the no-code-change
  (certification-preserving) decision for the model-difference gate.
- Ran no commissioning command, no `systemctl`, no `codex login`, no `sudo`, installed nothing. The
  tomllib check in step 5 is read-only and was NOT run (there is no live `/etc/nyc-supervisor/config.toml`).

## Pending (not in this increment)

The owner's four steps and the lane-1 canary evidence are pending — this increment delivers the
checklist only. When the owner runs the steps, the orchestrator records the canary evidence
(gate passed, one clean cycle, memory under 70%, review cap honored) and the OD-B model choice.

END-OF-REPORT

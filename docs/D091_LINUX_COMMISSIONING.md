<!-- D-091 TW5 (M0-T175). The ledger, not this file, holds task state. Owner directive D-091;
D091_WAVE3_WIRING_PLAN.md section 3. Plain words; every key/path/flag carries file:line evidence. -->
# D-091 Linux commissioning checklist (M0-T175)

**Read this first.** The owner types every step below (root config, Codex sign-in, systemd
install, the start). The orchestrator never runs them; after each step the orchestrator only
checks the result with the read-only command shown. The combiner stays OFF until the owner picks
the combining model (step 5); until then the loop runs with the Codex reviewer only. If any step
fails, stop and keep the evidence (section "If a step fails") — do not retry.

Server: Ubuntu, 4 CPU / 8 GiB. Certified CLIs: `claude 2.1.287`, `codex-cli 0.157.0`.

## 1. Root-owned config file (owner types; orchestrator checks)

Copy the example, fill in the owner's model choices, make it root-owned and parent-protected.

```
sudo install -D -m 0444 -o root -g root \
  tools/agent_supervisor/config.example.toml /etc/nyc-supervisor/config.toml
sudo ${EDITOR:-nano} /etc/nyc-supervisor/config.toml   # fill the owner choices below
```

Fill these keys (leave the combiner/reviewer switches absent for now — see step 5):

| Key | Where in the example | Fill with |
|---|---|---|
| `[codex] allowed_models` | `config.example.toml:24,28` | the Codex models the owner permits |
| `[claude] allowed_models` | `config.example.toml:30,34` | the Claude worker model(s) the owner permits |
| `[approved_models] models` | `config.example.toml:36,78` | the owner-approved model list, in order |

The Linux path `/etc/nyc-supervisor/config.toml` is the code default on POSIX
(`config.py:375-383` `default_config_path`, resolved via `platform_paths`, note `config.py:377-378`).

**Orchestrator checks** (read-only; no change made):

```
python -m tools.agent_supervisor doctor --config /etc/nyc-supervisor/config.toml
```

Expect `controller-config OS-ACL posture: PROTECTED` (`cli.py:1456-1459`; posture built at
`cli.py:510-533`, emitted at `cli.py:1435`). PROTECTED on Linux means the file is **root-owned
(uid 0), not group- or world-writable, has a protected parent, and is not a symlink** — all four,
fail-closed (`posix_acl.py:77-145`, owner/mode check `:117-137`, parent `:179`, combine `:159-169`;
dispatched by OS at `os_acl.py:493-495`). Then confirm the manifest binds the config:

```
python -m tools.agent_supervisor verify-controller \
  --manifest <controller-manifest.json> --config /etc/nyc-supervisor/config.toml
```

Expect `controller verified, including the external config.toml binding` (runbook section 6;
`config.toml` is a bound logical name, `manifest.py:47,54`).

These commands do not know the file paths on their own, so type the paths in. Use these three:

- The config file: `--config /etc/nyc-supervisor/config.toml`. That is the standard Linux spot.
  Sources: `platform_paths.py:41` (`POSIX_CONFIG_DIR`), `:67-77` (`default_config_path`).
- The manifest file:
  `--manifest "${XDG_CONFIG_HOME:-$HOME/.config}/nyc-supervisor/ctl24-activation/controller_manifest.json"`.
  The manifest was written earlier by the record-manifest step; it is not made here. Always pass it:
  if you leave `--manifest` off, `verify-controller` checks nothing, prints `HALT`, and exits with an
  error.
  Sources: `platform_paths.py:80-98` (`default_activation_dir`), `:101-107` (`default_manifest_path`),
  filename `manifest.py:38`; the fail-closed `HALT` is `cli.py:1696-1714`.
- The model-list file (full doctor only): `--model-selection <your model_selection.toml>`. The code
  has no standard spot for this one, so give the path to your own file. Do not make up a path. This
  file sits outside the manifest, so changing a model never breaks the controller.
  Sources: `cli.py:3250-3251`.

## 2. Codex sign-in on the server (OD-C; owner types; orchestrator checks)

The owner signs in to Codex once, on the server. The orchestrator never handles the credential
(D-091-R006). The credential lands in `~/.codex/`, outside the repo.

```
codex login        # "Sign in with ChatGPT" (or API key), owner-typed, once
```

**Orchestrator checks** (read-only):

```
codex --version
```

Expect `codex-cli 0.157.0` — the admitted, certified version (pinned
`tools/codex_cli/package-lock.json:16`; certified fixture
`tools/agent_supervisor/fixtures/capability_probe_live_2026-10-02_m0t174_2_1_287.json:62`). The
review reads nothing from the owner's personal config: the reviewer argv is built with
`--ignore-user-config` (`codex_reviewer.py:135`; reason `codex_reviewer.py:17`). The live provider
round-trip is proven only by the supervised start (step 4), not here.

## 3. systemd unit install (owner types; orchestrator checks)

The owner fills every `<...>` placeholder in the template, installs it, reloads, and enables it.

```
sudo cp tools/agent_supervisor/linux/nyc-supervisor.service.template \
  /etc/systemd/system/nyc-supervisor.service
sudo ${EDITOR:-nano} /etc/systemd/system/nyc-supervisor.service   # substitute every <...>
sudo systemctl daemon-reload
sudo systemctl enable nyc-supervisor.service
```

The placeholders the owner fills: `User` (`template:18`), `WorkingDirectory` (`template:19`),
`NYC_SUP_CLAUDE_BIN` (`template:26`), `NYC_SUP_GATE_CMD` (`template:27`), `NYC_SUP_START_CMD`
(`template:28`). The template ships with no `[Install]` section and `Restart=no`
(`template:8-9,30`), so a stray `enable` has no target and nothing auto-restarts.

**Orchestrator checks** (read-only):

```
systemd-analyze verify /etc/systemd/system/nyc-supervisor.service   # unit parses
grep -n 'DISABLE_AUTOUPDATER=1' /etc/systemd/system/nyc-supervisor.service
grep -n 'launch.sh'             /etc/systemd/system/nyc-supervisor.service
```

Expect: the unit parses with no errors; it carries `DISABLE_AUTOUPDATER=1` (template `:22`); and
`ExecStart` runs the gated launcher `.../linux/launch.sh` (`template:29`). The launcher is
fail-closed: it refuses to start when the start gate refuses (exit 5, `launch.sh:78-82`), when the
claude binary is missing (exit 3, `launch.sh:62-64`), or when a required env var is empty (exit 4,
`launch.sh:67-72`), and it never pushes, merges, or starts a run of its own.

> `systemd-analyze verify` is a standard systemd command, not a repo file.

## 4. Supervised certified start of lane 1 as a canary (owner types; orchestrator checks)

The owner approves the certified-start prompt-digest (supervised mode — runbook section 12,
touchpoint 1) and starts lane 1 as the canary.

```
sudo systemctl start nyc-supervisor.service   # runs the gated launcher; owner approves the
                                              # certified-start prompt-digest when shown
```

The unit runs `launch.sh`, which runs `NYC_SUP_START_CMD` only after the start gate passes.

What `NYC_SUP_START_CMD` must be: launch.sh requires it to be **the gated controller start**, run
only on a passing gate; the launcher adds no push, merge, or live run of its own (`launch.sh:28-29`,
`:84-88`). The gated controller start is the `start` subcommand in supervised mode:
`python -m tools.agent_supervisor start --mode supervised --config /etc/nyc-supervisor/config.toml
--model-selection <path> --approve-prompt-digest <digest>` (`--mode supervised` `cli.py:3289`,
`--config` `:3309`, `--model-selection` `:3310`, `--approve-prompt-digest` `:3335`). The canary = one supervised
single-task start: `--max-tasks` defaults to `1`, the certified single-task shape (`cli.py:3329`);
there is no `--lane` flag in the repo, so "lane 1" means this single canary start, not a CLI option.

> The repo does **not** define a fixed, concrete `NYC_SUP_START_CMD` value — it is environment-driven
> (`launch.sh:23-29`) and a `<...>` placeholder in the unit (`template:28`). The exact flag string
> (the `model_selection.toml` path and the supervised `--approve-prompt-digest`) is prepared by the
> orchestrator and shown to the owner before this step; it is not invented here.

**Orchestrator checks** — verify the stored lane-1 canary evidence shows one clean cycle:

- the start gate passed and the loop started (launcher reached step 5, `launch.sh:84-88`);
- memory stayed under the **70%** ceiling — the Linux pause ceiling is derived at launch as 70% of
  measured physical RAM, never hard-coded (`resource_sampling.py:160` `MEMORY_PAUSE_FRACTION = 0.70`,
  `:232` `resolve_memory_ceiling_bytes`, gauge `:297`; config note `config.example.toml:112-118`);
- the **review cap was honored** — at most 2 review/combine processes across all lanes and 1 per
  lane, reserved atomically before each spawn and fail-closed (`run_budget.py:793`
  `admit_review_or_combine`; caps `config.example.toml:137` global `= 2`, `:138` per-lane `= 1`;
  atomic reservation `review_slots.py:449` `try_reserve` (count-decide-reserve under the exclusive
  lock) via the `reserve` context manager `:501`).

## 5. Combiner stays OFF until the owner picks the combining model (D-091-R008 / OD-B)

Until the owner names the combining model, **leave the combiner and the Claude reviewer switches
absent** from `/etc/nyc-supervisor/config.toml`. Absent = off, fail-closed: the readers return off
for any absent / non-bool / non-`true` value (`review_combiner.py:459-467`, key
`review_combiner` `:420`; `claude_reviewer.py:395-403`), and the dataclass defaults are `False`
(`review_combiner.py:433`, `claude_reviewer.py:364`). With both off the loop keeps its single Codex
reviewer, byte-for-byte. If the owner wants an explicit belt, the lines are:

```
[claude]
reviewer_enabled = false      # absence already = off; this is an explicit belt
[review_combiner]
enabled = false               # absence already = off; this is an explicit belt
```

> Note (resolved): these two keys are **not** present in `config.example.toml`; the readers treat
> absence as off (`review_combiner.py:459-467`, `claude_reviewer.py:395-403`), so the safe act is to
> leave them out — no key to set to keep the combiner off.

**Later step — the owner names the model (do not do this during steps 1-4).** When the owner gives
the combining model, add under `/etc/nyc-supervisor/config.toml`:

```
[claude]
reviewer_enabled = true
reviewer_model   = "<owner-chosen-claude-reviewer-model>"
[review_combiner]
enabled = true
model   = "<owner-chosen-combining-model>"
```

The combining `model` is required with no default (`review_combiner.py:512-516`;
`dual_review.py:239-245`) and must be on the `[claude] allowed_models` allowlist — the conductor
refuses before any process if it is not (`dual_review.py:251-256`). The reviewer/combiner
independence that the code enforces is by **identity**, not model string
(`review_combiner.py:572-584` `_assert_independent`).

**Orchestrator check before the owner starts the loop with the combiner ON** (read-only; makes no
change). This enforces that the combining model and the Claude reviewer model are both set,
different, and both allowlisted — the "distinct models" independence the design calls for
(`D091_WAVE3_WIRING_PLAN.md:174-175`):

```
python3 -c '
import tomllib
c = tomllib.load(open("/etc/nyc-supervisor/config.toml","rb"))
combiner = c.get("review_combiner",{}).get("model","")
reviewer = c.get("claude",{}).get("reviewer_model","")
allowed  = c.get("claude",{}).get("allowed_models",[])
ok = bool(combiner) and bool(reviewer) and combiner != reviewer \
     and combiner in allowed and reviewer in allowed
print("PASS" if ok else "STOP",
      {"combiner": combiner, "reviewer": reviewer, "allowed": allowed})
'
```

Keys checked (verified against the code): `[review_combiner].model` (`review_combiner.py:512-516`,
field `:434`), `[claude].reviewer_model` (`claude_reviewer.py:384`), `[claude].allowed_models`
(allowlist the conductor enforces, `dual_review.py:251-256`; example `config.example.toml:34`). On
`PASS` the owner may start with the combiner on; on `STOP` the owner does **not** start.

We could instead put this same rule inside the program code. We are not doing that now. Changing
any supervisor code would force the whole loop to be certified again (the M0-T174 certification would
no longer hold). So we run the read-only check above at commissioning for now, and we have written
down "add the rule in code later" as a future improvement.

Sources: certified code lives under `tools/agent_supervisor/**`; the certification is M0-T174.

The orchestrator's recommendation (Opus 5.5) is already recorded in
`docs/SESSION_HANDOFF.md:51`; this checklist recommends nothing further.

## If a step fails

Stop. Keep the evidence exactly as it is (the command output, the doctor JSON, the launcher exit
code, the journal). Do not retry the step. Tell the orchestrator. This is the commissioning stop
rule: a failed step is a signal to inspect, not to re-run.

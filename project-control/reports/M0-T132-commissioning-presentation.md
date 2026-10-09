# M0-T132 — commissioning presentation (R445, PRESENT-ONLY; nothing here was executed)

The exact owner-typed sequence to start the next commissioning journey on the admitted 2.1.252
identity under Fable unavailability. **All commands are mechanically parse-validated** (built through
`cli.build_parser().parse_args(...)` without dispatch — no execution; R444) and every referenced path
was confirmed to exist. Type each with the `!` prefix in the orchestrator session, in order, forward
slashes. **The orchestrator did NOT run any of these.**

## Preconditions (all satisfied)
- M0-T132 ACCEPTED: 2.1.252 (`e713c5a6`) admitted; combined R247 recert PASS at manifest `c228b7ca`
  (binds M0-T131 `codex_reviewer.py` + M0-T132 `event_drift.py`); whole suite 3,043/2/0 (the 3
  M0-T131 CLI-drift failures resolved); shell-routing evidence present at `e713c5a6` (native_preferred).
- Journal state: **HALTED** (transitions 35, audit 85; trigger `decision_halt_unsafe` from journey-4).
- opus-4-8 is APPROVED in `config.toml` and confirmed available (not capped).

## The sequence (four owner-typed steps)

**Step 1 — rebind the certified stored manifest to the recertified tree** (the orchestrator's
re-record was blocked by the local write classifier; this writes the certified activation manifest,
so it is an explicit owner act). Re-records `26a05096…` → `c228b7ca…`:
```
! python -m tools.agent_supervisor record-manifest --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 --config "C:/Program Files/SupervisorConfig/config.toml" --out C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json
```

**Step 2 — pin the worker model to opus-4-8** so the loop runs while Fable is capped (opus is
approved; this is the disclosed model decision under Amendment 35 R447, not a silent substitution).
Edit `C:/SupervisorController/model_selection.toml`, in the `[claude]` section change:
```
model = ""            ->   model = "claude-opus-4-8"
```
(Leave codex + fallback lines as-is. This is a runtime file outside the manifest, so it does not
re-trigger R247. If you'd rather the orchestrator make this one-line edit, say so — it's held back
only because it sets the autonomous loop's model, R146.)

**Step 3 — exit HALTED** (audited `owner_explicit_restart`, HALTED → IDLE; M0-T107 driver):
```
! python -m tools.agent_supervisor owner-restart --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24
```

**Step 4 — the bounded limited-auto journey** (one command; `--repin-cli-identity` accepts the new
`e713c5a6` CLI at the journal level — the per-launch admission completion, R285):
```
! python -m tools.agent_supervisor start --mode limited-auto --owner-enable-bounded-auto --repin-cli-identity --checkout C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 --repo C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107 --branch task/M0-T107-plugin-portability --worktree C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t107 --max-cycles 3 --max-tasks 3 --packet-queue C:/Users/MLFLL/Downloads/nyc-zoning/commissioning-queue.json --claude-executable C:/Users/MLFLL/.local/bin/claude.exe --codex-executable C:/Users/MLFLL/AppData/Roaming/npm/codex.cmd --task-packet project-control/tasks/M0-T107.json --config "C:/Program Files/SupervisorConfig/config.toml" --model-selection C:/SupervisorController/model_selection.toml --manifest C:/Users/MLFLL/AppData/Local/NYCBuildabilitySupervisor/ctl24-activation/controller_manifest.json
```

## What each step does / honest caveats
- The start runs the first task (M0-T107) on the worker model opus-4-8, up to 3 Codex-reviewed cycles;
  on a COMPLETE verdict it advances exactly-once and selects the next ELIGIBLE queue entry (≤3 tasks).
  A conservative first journey may use `--max-tasks 2`.
- **`--repin-cli-identity` is required this time** (the CLI moved 2.1.251→2.1.252); without it the start
  refuses on drift by design.
- The start's pre-dispatch relies on `cli_capability_manifest` + the digest-keyed `shell_routing`
  evidence (captured at `e713c5a6`), NOT a live control-response round-trip. The `doctor --live`
  control-response probe currently fails only because it hardcodes the capped Fable default (it is not a
  2.1.252 protocol break — the routing probe observed live `can_use_tool` brokering at 2.1.252 on opus);
  it does not gate the start. Refresh it with `doctor --live` once Fable is available (S8.5 follow-up).
- **On ANY live failure (R394): the run stops without retry, preserves evidence byte-for-byte, and
  returns ONE consolidated assessment** for a new owner decision. The M0-T107 owner-touch cap is at
  excess, so any counted stop is an immediate owner matter.

## Standing gates untouched
Never merge PR #241; autostart, C1 canary, Telegram live send, natural-event graduation, OS-ACL
hardening, production, credentials, payments, legal — all owner-only and closed. This journey proves
the bounded loop on the admitted identity; any wider autonomy is a separate owner decision each time.

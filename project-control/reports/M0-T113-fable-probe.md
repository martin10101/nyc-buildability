# M0-T113 — R263 read-only live capability probe: Fable 5 launch PROVEN (+ R265 revert applied)

Recorded by the orchestrator 2026-08-29 (Amendment 10, rows R261–R267; capture commit
`c5ca81a`, validator EXIT=0). Sequence: capture → probe → evidence → single authorized
model-selection edit → doctor re-verify. **No launch performed (R267 hold in force).**

## 1. Probe A — certified bounded control-response probe (`doctor --live`)

Exact command: `python -m tools.agent_supervisor doctor --live --json --checkout <ctl24>
--config "C:\Program Files\SupervisorConfig\config.toml" --model-selection
"C:\SupervisorController\model_selection.toml" --manifest
"%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\controller_manifest.json"
--claude-executable "C:\Users\MLFLL\.local\bin\claude.exe"` → EXIT=0, overall PASS.
`control_response_live_probe`: **"VERIFIED (live run, sha256_head:8a9c9c9018460062): the
installed CLI accepted the exact control_response bytes this build emits, denied the tool,
and echoed our deny message back in permission_denials."** Full JSON:
`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\doctor_live_probe.json`.

## 2. Probe B — supplemental model-identity probe (same shipped flow, events persisted)

The shipped probe discards its event stream, so it proves the round-trip but not the model
id. Probe B replicates the IDENTICAL flow via the shipped builders (`_probe_argv` →
`RunnerConfig(max_turns=1)` → `assert_argv_safe(build_argv(...))`, `minimal_env()`,
`build_control_response` deny, one turn, throwaway directory, workdir cleaned) and persists
the events. Script: session scratchpad `fable_probe.py`; events:
`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\fable_probe_events.json`.

Result summary (verbatim keys):

```json
{"events": 7,
 "init_model": ["claude-fable-5"],
 "result_models": ["claude-fable-5", "claude-haiku-4-5-20251001"],
 "control_request_seen": true,
 "permission_denials": 1,
 "deny_message_echoed": true,
 "target_file_created": false}
```

**The controller's shipped launch path (no `--model` flag → account/CLI default) started a
live session whose CLI init event reports `model: claude-fable-5`,** completed the bounded
control round-trip (tool denied, nothing written), and exited within bound. The haiku entry
in `result_models` is the CLI's internal utility model, not the conversation model.
**PROBE VERDICT: PASS — the controller can launch Fable 5 successfully.** (Independently
consistent with R261: the owner's active main session runs Fable 5 on the same account and
installed CLI 2.1.248.)

## 3. R265 — the single authorized model-selection edit (applied after the probe)

`C:\SupervisorController\model_selection.toml` `[claude] model`: `"claude-opus-4-8"` → `""`
(the file's own recorded revert value; account/CLI default = Fable 5). The stale
exhaustion-era comment block was replaced by the Amendment-10 provenance note. **Nothing
else changed** (codex section, fallback lists untouched). `model_selection.toml` is outside
the controller manifest by design, so the manifest binding and certified code identity are
unmoved.

- New file SHA-256 (raw, `Get-FileHash`): `FCBBF70F553AE115FA126183DE9A26134A2F54BC4AC66D726A3F292101ECDD2B`
  (supersedes the runbook §1 expected value `0E2432C0…` — doc refresh is a non-blocking
  follow-up; the runbook's value was the exhaustion-era snapshot).
- Post-edit `doctor` (non-live): **overall PASS**; `model_selection: claude model '';
  selection digest b2b927c65342579d…; no effort key present`;
  `model_selection_allowlists: PASS` (empty = account default, no explicit selection).

## 4. Remaining before launch (R266/R267 — owner administrator step)

MISMATCH 2 of the activation preflight stands: `[approved_models]` in the protected config
is empty → every model-selection act (rotation successor, quota chain, turnover) is a
terminal HALT. The owner must apply the administrator edit (exact instructions delivered in
the session report; summary: add `[approved_models] models = ["claude-fable-5",
"claude-opus-4-8"]` and extend `[claude] allowed_models` with `"claude-fable-5"` in
`C:\Program Files\SupervisorConfig\config.toml` under elevation). After that owner edit:
re-record the manifest (the manifest binds the external config digest), re-run
`verify-controller` + `doctor`, and re-run the COMPLETE activation preflight. **Launch
happens only after all of that passes (R267).**

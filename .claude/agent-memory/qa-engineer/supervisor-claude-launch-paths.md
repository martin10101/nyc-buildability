---
name: supervisor-claude-launch-paths
description: The supervisor launches the claude binary from FIVE seams, not two — env-injection scope reviews must check all of them
metadata:
  type: project
---

When reviewing any change to the controller-launched Claude child ENVIRONMENT (e.g. D-024 Amendment 13 / M0-T117 forced `DISABLE_AUTOUPDATER=1`), the claude binary is launched from more than the two `claude_runner.py` worker/probe Popen sites:

- `tools/agent_supervisor/claude_runner.py:1126` (worker, `run_unit`) and `:1557` (`probe_model_launch`) — the two seams M0-T117 routed through `process.claude_child_env`.
- `tools/agent_supervisor/preflight.py:126` (`control_response_round_trip`, live claude child) — uses `minimal_env()`.
- `tools/agent_supervisor/capability_probe.py:99` (`_run`, `claude --version/--help`) — `subprocess.run` with NO env arg → inherits full parent env.
- `tools/agent_supervisor/native_runtime.py:101` (`run_command`) — `env=None` → inherits parent env.

**Why:** an env-injection task scoped to "the claude child seam" can silently leave 3 other live/probe claude launches on parent-env inheritance. R278(1) demanded injection "NOT dependent on parent-environment inheritance"; those 3 paths still are — covered only by the R288 owner machine-scope env var.

**How to apply:** for any "inject/scrub an env var on claude children" review, grep the whole `tools/agent_supervisor/` package for `subprocess.Popen|subprocess.run` and confirm which launch the claude executable; codex launches go through `codex_channel` → `minimal_env` and are a deliberate scope boundary (AS-5).

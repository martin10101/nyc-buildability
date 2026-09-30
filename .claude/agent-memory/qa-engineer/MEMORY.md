# Memory index

- [Supervisor claude launch paths](supervisor-claude-launch-paths.md) — the claude binary is launched from FIVE seams (claude_runner x2 + preflight + capability_probe + native_runtime); env-injection scope reviews must check all of them, not just the two worker/probe Popen sites

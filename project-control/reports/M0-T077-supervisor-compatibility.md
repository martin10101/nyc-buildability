# M0-T077 — Supervisor compatibility (D-020 §8, READ-ONLY)

No supervisor file was modified, executed, or configured. Everything below is static
code inspection of `tools/agent_supervisor/**` at the frozen base plus one
fresh-process configuration-resolution probe that does not involve the supervisor.

## Finding: supervised launches DO resolve the repository's checked-in settings

Call-path trace (actual code path, not module presence):

1. **Production worker launch** — `tools/agent_supervisor/cli.py:2686-2689`:
   `RunnerConfig(executable=args.claude_executable, cwd=str(worktree), …)` — the
   worker's `cwd` is the supervised task's repository worktree.
2. **Turnover redispatch** — `tools/agent_supervisor/turnover_adapters.py:404-412`:
   `RunnerConfig(…, cwd=self._targets.checkout, …)` — same property.
3. **Preflight probe** — `tools/agent_supervisor/preflight.py:91`:
   `RunnerConfig(…, cwd=cwd)` — same property.
4. **Process spawn** — `tools/agent_supervisor/claude_runner.py:1085`:
   `subprocess.Popen(argv, …, cwd=self.config.cwd or None, env=env, …)` — the Claude
   CLI subprocess actually starts in that worktree.
5. **No override of settings resolution** — `build_argv` emits the confirmed base
   invocation (`claude -p --input-format stream-json --output-format stream-json
   --verbose` + `--max-turns/--model/permission wiring`); a grep of the whole package
   finds NO `--settings`, NO `--mcp-config`, NO `--strict-mcp-config` — so the worker
   performs Claude Code's STANDARD configuration resolution from its cwd.
6. Claude Code's standard resolution loads the project `.claude/settings.json` of the
   directory tree the process starts in (official settings behavior; the same
   resolution `claude mcp list` performs). Empirical anchor: a fresh process started
   in a clean worktree of this repository resolves the policy and reports
   `No MCP servers configured` (see M0-T077-fresh-session-proof.md Runs A/B) — that is
   the identical cwd + resolution a supervised worker gets at step 4.
7. The runner's `env_allowlist` filters ENVIRONMENT variables only; settings loading
   is file-based and unaffected.

Conclusion: a supervised worker launched from a worktree of this repository loads the
checked-in project settings, and therefore the MCP default-deny policy, exactly like
the proven fresh processes. Additionally, supervised workers' permission events flow
through the broker (`claude_runner.py:1660-1700` → `broker.evaluate_request`), which
maps unknown tools to deny-by-default — a second, independent layer that already
constrains any MCP tool use in supervised runs.

## Honest residual gap (owner-gated)

A LIVE end-to-end supervised worker launch asserting an empty MCP roster from inside
the worker session was NOT performed: live supervisor probes are owner-present-only
under the standing D-018/D-019 boundaries, and this task changes nothing in
`tools/agent_supervisor/**`. The static trace + same-cwd fresh-process resolution is
the strongest evidence available without a live probe.

**Smallest owner-gated next step (proposed separately, NOT part of this task):** when
the owner next runs the (already separate, owner-present) controller/rehearsal
session, add one assertion to the existing rehearsal checklist: launch one bounded
supervised worker in a clean worktree and record that its session reports no MCP
servers. No code change is required for this — it is a checklist line in an
owner-present procedure.

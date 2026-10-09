# D-024 Amendment 2 — Official statusline capability evidence + primary statusLine handler requirements

Captured: 2026-08-26 UTC by the orchestrator (Fable 5), verbatim from the owner's message in the
active session. Channel: Claude Code interactive session (session_01YVDmxRbkkrk3ifPmwvPtBP).
Base identity at capture: branch `control/D-024-fable-codex-loop`, HEAD
`66d93999f2c3cbbb141543a305491a17a6c1a77c` (origin/main `d8b3899f61efa6620e18a26541ced96020f5bef9`).
Amends: `source-001.md` (owner directive v4). Requirement IDs assigned: D-024-R129..R138.

Registry context at capture (for the reverse trace): M0-T088 (B1 telemetry core + primary
status-line ingestion) ACCEPTED at frozen content `23f0d80` earlier this same day; M0-T089 (B2
subagent telemetry incl. the official subagentStatusLine ingestion) submitted and under
independent review at frozen content `b7be085`. The owner's "M0-T088" items therefore bind to the
follow-up bounded task (M0-T099) that continues the accepted B1 architecture — accepted work is
immutable and is NOT reopened; nothing here restarts or rebuilds it (per the directive's own item 1).

## Verbatim owner text

Official capability evidence update directly relevant to M0-T088:

The official Claude Code status-line documentation confirms that `statusLine` receives structured main-session JSON containing context-window usage, window size, model, effort, session identity, rate-limit usage, worktree, and related fields.

It also officially confirms `subagentStatusLine`. Its task objects include id, name, status, description, startTime, model, effort, contextWindowSize, tokenCount, tokenSamples, and cwd. The documented tokenCount/contextWindowSize requirement is Claude Code 2.1.205+, and effort requires 2.1.214+; installed 2.1.220 qualifies.

Use this as primary official capability evidence.

For M0-T088:

- Continue the existing bounded task; do not restart or rebuild the telemetry architecture.
- Prove primary `statusLine` ingestion with a real installed-version fixture before acceptance.
- The project status-line handler should both write the sanitized telemetry sidecar and print a compact human-readable status row, so Codex monitoring and owner visibility use one feed rather than competing configurations.
- Keep live context occupancy separate from cumulative usage.
- Keep five-hour/seven-day rate-limit pressure separate from context pressure.
- Confirm the status-line process adds no model messages and consumes no API tokens.
- Handle absent/null fields safely.
- Do not expand M0-T088 into sub-agent ingestion if that belongs to the next campaign task. Instead, durably route the official `subagentStatusLine` implementation and live canary to the correct next bounded task, reusing M0-T088's records, sanitization, sidecar, and journal.
- Record the official documentation URL and the installed-version proof in the verification evidence.

Official source:
https://code.claude.com/docs/en/statusline

## Capture annex — official-source verification (external fact check, fetched 2026-08-26)

The orchestrator fetched https://code.claude.com/docs/en/statusline at capture time and verified the
owner's capability claims against the live official page. Confirmed verbatim facts (primary
capability evidence, superseding any weaker docs-derived assumption in the capability matrix):

- statusLine main-session stdin JSON includes: `session_id`, `transcript_path`, `cwd`, `model`,
  `workspace`, `version`, `effort.level` (absent when the model lacks the effort parameter),
  `thinking.enabled`, `fast_mode`, `cost.total_cost_usd` / `total_duration_ms` /
  `total_api_duration_ms` / `total_lines_added` / `total_lines_removed`,
  `context_window.total_input_tokens` / `total_output_tokens` / `context_window_size` /
  `used_percentage` / `remaining_percentage` / `current_usage{input_tokens,
  cache_creation_input_tokens, cache_read_input_tokens, output_tokens}`, `exceeds_200k_tokens`,
  `rate_limits.five_hour.used_percentage` / `.resets_at` and `rate_limits.seven_day.used_percentage`
  / `.resets_at`, plus `worktree`, `agent`, `pr.*`, `vim.mode`.
- Nullability: `current_usage` is null before the first API call and again after `/compact` until
  repopulated; `used_percentage`/`remaining_percentage` may be null early; `rate_limits` appears
  only for Claude.ai subscribers after the first API response, each window independently absent;
  `total_*` are 0 before the first response; `used_percentage` is input-only
  (input + cache_creation + cache_read, no output). `cost.total_cost_usd` resets to $0 when
  `/clear` starts a new session (>= v2.1.211).
- Official note, verbatim: "The status line runs locally and does not consume API tokens."
- Runtime behavior: event-driven with 300ms debounce; optional `refreshInterval` (min 1s);
  an in-flight script is cancelled when a new update triggers; script output = status row text
  (multi-line allowed).
- subagentStatusLine: command runs once per refresh tick; receives ALL visible subagent rows as one
  JSON object (base hook fields + `columns` + `tasks[]`); each task has `id`, `name`, `type`,
  `status`, `description`, `label`, `startTime`, `model`, `effort`, `contextWindowSize`,
  `tokenCount`, `tokenSamples`, `cwd`. `model`+`contextWindowSize` require v2.1.205+ and are
  omitted until the task's model resolves; `effort` requires v2.1.214+ and is absent when the
  subagent inherits the session effort. Output contract: one JSON line per overridden row
  `{"id": "<task id>", "content": "<row body>"}`.
- Installed-version proof: `claude --version` = 2.1.220 (live capability fixture
  `tools/agent_supervisor/fixtures/capability_probe_live_2026-08-25.json`), which satisfies every
  documented version gate above.

Full fetched page preserved at capture time in the session tool-result store; the durable primary
reference is the URL + this annex + the installed-version fixture.

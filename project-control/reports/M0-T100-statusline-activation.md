# M0-T100 — passive statusLine wiring activation (D-027; M0-T099 report §4 owner step)

**Producer:** orchestrator · 2026-08-26 UTC · branch `control/D-024-fable-codex-loop`
**Authorization:** D-027 (`project-control/directives/D-027-statusline-activation/source-001.md`,
sha256 `c9c203d6…ef9a9a`) — owner mid-turn terminal message 2026-08-26 activating owner step (1)
from the accepted M0-T099 report.

## 1. What was activated (exactly report §4, nothing else)

Two files changed, both inside the packet's allowed paths, matching M0-T099 report §4 verbatim:

1. `.gitignore` — appended ignore rule `.claude/telemetry/` (runtime sidecar/journal are never
   committed). Verified: `git check-ignore -v .claude/telemetry/statusline_sidecar.json` →
   matched by the new rule.
2. `.claude/settings.json` (project) — added the documented block:
   ```json
   "statusLine": {
     "type": "command",
     "command": "python -m tools.agent_supervisor.telemetry_statusline --journal .claude/telemetry/statusline_journal.jsonl"
   }
   ```
   The `--journal` option is §4's documented bounded-history addition ("add `--journal
   .claude/telemetry/statusline_journal.jsonl` for bounded history"). No other key in either file
   was touched (full diff = 4 added lines in settings.json, 3 in .gitignore).

**No code changed.** `tools/agent_supervisor/**` untouched (supervisor freeze not triggered; no
tree-hash change; no suite-baseline re-establishment duty). No dependencies added. Accepted
M0-T099 artifacts (packet, report, gates, checkpoint, frozen content `00f2519`, material identity
`d6e90bfc`) untouched — `git status` shows no modification under any M0-T099 path (D-027-R002).

## 2. Passive shadow/read-only posture (D-027-R004, R010)

The wired command is the accepted M0-T099 handler: it parses stdin, persists ONE sanitized
record (sidecar + journal), prints ONE row, exit 0 always. It opens no network connection,
composes no prompts, consumes no API tokens (official statusline doc, quoted in the module
docstring), and has **no actuation surface**: nothing can stop agents, rotate sessions, change
models, or take any supervisory action. Continuous/autonomous supervision remains owner-gated
(D-024 §18, R595 prerequisite untouched); the supervisor stays SHADOW-ONLY. The continuous
Codex loop was **not** activated.

## 3. REAL live check — both outputs from the same feed (D-027-R006)

**Live activation observed in the running session.** Within ~30 s of the settings edit, the
owner's live Claude Code TUI (this session, v2.1.220) began invoking the wired command on its
refresh ticks — no restart needed:

- `.claude/telemetry/statusline_sidecar.json` — created 2026-08-26T05:52 UTC by the live TUI,
  atomically refreshed every tick (observed `timestamp_utc` advancing 05:54:22 → later reads).
- `.claude/telemetry/statusline_journal.jsonl` — 33 records between 05:52:20Z and 05:54:22Z
  (one per tick), count still growing during evidence capture.
- The sidecar carries THIS session's real state (`session_id 4333c462-…`, model `Fable 5`
  `claude-fable-5`, `ctx 14–15% of 1.0M`, `sess $9.64→$10.12`, `5h 5–6% / 7d 35%`), i.e. live
  data, not fixture data. Reconstructed human row from the live journal tail record:
  `Fable 5 | ctx 15% of 1.0M | sess $10.12 12m | 5h 6% 7d 35% | v2.1.220` — this is what the
  TUI status row displays (the effort segment appears when the live payload reports
  `effort.level`).

**Single-invocation two-output proof (exact wired command, REAL captured payload).** The
committed REAL live-capture payload (`tools/agent_supervisor/fixtures/statusline_live_2026-08-26.json`,
`post_first_response_with_rate_limits`) was piped into the exact wired command with a scratch
sidecar/journal. ONE invocation produced BOTH outputs, exit 0:

- stdout (human row): `Fable 5 xhigh | ctx 4% of 1.0M | sess $0.78 1m | 5h 29% 7d 33% | v2.1.220`
- sidecar (machine record): same feed — `context_used_pct 4`, `context_window_tokens 1000000`,
  `cumulative_cost_usd 0.7828…`, `five_hour 29%/seven_day 33%`, `version 2.1.220`.

One-feed linkage is structural (`handle_status_line`: the sidecar write happens BEFORE the row
is returned, from the same ingested record — R132) and observed: every row value above is the
sidecar record's value. The sidecar is the machine-readable surface for future Codex monitoring
(`telemetry_status.read_only_status` reads it; read-back command in M0-T099 report §4 notes).

## 4. Sensitive-content scan of the live artifacts (D-027-R007)

Scans over the FULL live sidecar and the FULL 33-record live journal (raw bytes):

| Pattern | Hits |
|---|---|
| `MLFLL` (username) | 0 |
| `Users` (home path component) | 0 |
| `C:\` (drive path prefix) | 0 |
| `C--` (dash-encoded home form) | 0 |
| `ghp_` / `sk-` / `Bearer` (credential shapes) | 0 |

Home-directory prefixes are masked to `[HOME]` in both slash and dash-encoded forms (production
mask incl. the M0-T099 dash-form fix): live `cwd` → `[HOME]\Downloads\nyc-zoning\ctl24`, live
`transcript_path` → `[HOME]\.claude\projects\[HOME]-Downloads-nyc-zoning-ctl24\<uuid>.jsonl`.
Sidecar `redaction_count: 3` documents the applied redactions. No credentials, tokens, or
secrets of any kind appear (the statusline payload never carries them).

**Explicit disposition — retained identifiers (not silently passed):** the record KEEPS the
session UUID (`session_id`) and the transcript-file UUID inside the masked path. This is by
design: the session id is the monitoring key Codex needs to correlate records per session.
These identifiers live ONLY in `.claude/telemetry/` — runtime-local, newly gitignored, never
committed, never pushed (repo is public; nothing telemetry-related enters git). This matches
the accepted M0-T099 posture (G5 MIN-1 applies to FUTURE public committed fixtures, not to the
local runtime sidecar). No personal path, username, or credential is written anywhere, masked
or not, beyond the `[HOME]`-masked forms shown above.

## 5. Precedence check — project-only, global fallback intact (D-027-R005)

- The owner's user-global `~/.claude/settings.json` was **read-only inspected, never written**:
  sha256 `32c6fb008a95c33793d76efeed781511cf5d824dbb4fbd8af2911c9ccdc6afa7`, mtime
  2026-08-26 04:29:57 UTC (predates this task's first write at ~05:48 UTC). Its personal
  statusLine (`powershell … C:/Users/MLFLL/.claude/statusline.ps1`) and `subagentStatusLine`
  remain exactly as the owner configured them.
- Claude Code settings precedence (official settings docs): project `.claude/settings.json`
  overrides user-global settings **within this project only**. The new `statusLine` block
  exists only in this repository's settings, so: inside ctl24 sessions the project telemetry
  row displays (proven live, §3); in every other directory the personal `statusline.ps1`
  fallback continues to govern (no project override exists there). `subagentStatusLine` is not
  set at project level, so the owner's personal subagent row is inherited unchanged even here.
- Nothing competes: one key, deliberately shadowed inside one repo, zero edits to the global file.

## 6. Tests and self-checks (D-027-R008 input)

- Targeted handler pack at the wired tree: `pytest tools/test_agent_supervisor_statusline_handler.py -q`
  → **23 passed / 0 failed** (0.31 s).
- Exact wired command exit code with real payload: 0 (row printed, sidecar + journal written).
- `git check-ignore` proves the telemetry dir can never be committed; `git status` shows the
  telemetry files as ignored (absent), and no unintended file changed.
- Registry validator `python tools/validate_directive_compliance.py --check`: EXIT=0 run
  recorded at the capture/claim seam (result noted in the G2 self-check record).
- No production code changed → no modularity/ruff/suite-baseline duties triggered; the full
  supervisor suite baseline stands as accepted at M0-T099 (2595/3/0 composite).

## 7. Prohibitions honored (D-027-R009, R010, R012, R013)

- The three external leftover pack-repo agent worktrees (`agent-a97cd976cfb4344f0`,
  `agent-ac83580dbc0f69fce`, `agent-a1e58fd626f4ec1e6`) were **not** touched (no purge
  commands executed; M0-T099 report §8 remains the owner's documented procedure).
- No continuous-loop/supervisor activation of any kind; PR #241 untouched; no owner-only
  boundary crossed (no credentials, payment, production, or legal action).
- Scope stayed at exactly: two wiring files + this report + minimal control records; no
  accepted work repeated or reopened.

## 8. Follow-on (D-027-R011)

After acceptance of M0-T100 is recorded and pushed, the campaign record's NEXT action resumes
unchanged: claim M0-T090 (C1 bounded subagent contracts + structural workload sizing) carrying
the named M0-T099 advisory bundle (G3-M1, G5-NIT-1, G5-NIT-2; G5-MIN-1 standing guidance for
the live-canary task). The campaign record itself was not modified by this task.

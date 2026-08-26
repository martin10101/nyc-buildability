# M0-T103 — D-024 Amendment 3 unit B: official-updater upgrade 2.1.220 → 2.1.246 (R167/R168 record)

Producer: orchestrator (Fable 5), 2026-08-26 UTC. Task cites `D-024:ALL`; supervisor-freeze
qualifying evidence: D-024-R001 + D-024-R149 (packet), D-024-R148/R149/R168 (test re-baseline).

## 1. Pre-update record (R167 steps 1–4)

- **Version/identity:** `claude --version` = `2.1.220 (Claude Code)`; native binary
  `[HOME]/.local/bin/claude.exe`, sha256 `af5bf1f1b2aadffc768eccd787084c6fdf9ba81624cbe96c1c6d9ac1a1550231`,
  265,720,480 bytes. PATH order: native first, npm shim (`[HOME]/AppData/Roaming/npm/claude`)
  second. **The npm shim is BROKEN pre-update** ("not compatible with the version of Windows
  you're running") — a dead leftover, not a usable fallback.
- **Commands/help/settings/fixtures:** frozen in `capability_probe_live_2026-08-26.json`
  (help/version output_sha256 per probe; masked) + the accepted M0-T102 docs snapshot; settings
  tracked in-repo (`.claude/settings.json`, unchanged this task).
- **Official stable confirmed:** `2.1.246` (2026-08-25) — M0-T102 changelog snapshot.
- **Clean + pushed:** HEAD `c6a495f` (checkpoint CP-D024-M0-T102) == origin tip; porcelain empty.
- **Session disruption check:** `claude daemon status` = daemon pid 9896 on 2.1.220 (transient,
  1 bg worker); `claude agents --json` = 2 sessions: background `777b09da` (owner's parked
  review session, state `blocked` on a permission prompt for ~6.8 days, process pid 21448) and
  this interactive session. Official semantics (agent-view snapshot): running processes keep
  their binary; blocked/attached sessions are not interrupted; supervisors only move sessions to
  NEWER versions. Determination: no disruption. (G0 report `M0-T103-G0-readiness.md`.)

## 2. Update (R167 step 5)

`claude update` (official updater only): "Successfully updated from 2.1.220 to version 2.1.246.
Background service will restart on the new version shortly; background jobs continue
uninterrupted." The updater auto-corrected a config mismatch (config said `global`, running
install is `native` → config updated to `native`) and warned about the leftover npm global
install (fix: `npm -g uninstall @anthropic-ai/claude-code` — owner-machine hygiene, not
performed by this task). No third-party build, SDK, or wrapper involved.

## 3. Post-update record (R167 step 6)

- Fresh child `claude --version` = **`2.1.246 (Claude Code)`**; native binary sha256
  `9f07f1ecaf26231fc2fac489e7c5214140d38fd14764938a2c8c46f31931d204`, 250,948,768 bytes
  (identity changed as expected).
- `claude doctor`: native 2.1.246, commit `1ba9d2211ae1`, platform win32-x64, config method
  `native`, auto-updates enabled (channel latest); **1 warning** = the pre-existing leftover npm
  shim (unchanged by this task).
- Daemon: restarted itself onto **2.1.246** (new pid 10124) shortly after the update, exactly as
  the updater stated — live confirmation of the documented supervisor auto-update behavior.
- **This orchestrator session still runs the old 2.1.220 binary** (running processes keep their
  binary) — every proof below therefore uses disposable child launches on the NEW binary
  (R168 step 7).

## 4. Child canaries on the new binary (R168 steps 7–8)

1. **Capability probe (deterministic):**
   `capability_probe_live_2026-08-26_m0t103_post_update.json` — claude `2.1.246`, codex
   `0.146.0` (unchanged), all probed flags still `supported`, masked (`[HOME]`, 0 username
   hits). Filename carries the consuming task id (G3 ADV-1 applied; the module-internal
   `task: M0-T086` label is the generator's schema tag, per the accepted M0-T102 advisory).
2. **Gate 0 / MCP default-deny / model canary:** `claude -p "Reply with exactly:
   CANARY-OK-2146" --strict-mcp-config --output-format json` → result exactly `CANARY-OK-2146`,
   `is_error: false`, model resolved `claude-fable-5` (settings honored), no MCP servers loaded
   (strict + none configured). Clean launch on the new binary proven.
3. **Hook-execution canary:** `claude -p "Use the Read tool … reply HOOK-CANARY-OK"
   --strict-mcp-config` → `HOOK-CANARY-OK`, `is_error: false`, 2 turns — a real tool call ran
   through the PreToolUse hook chain (readonly guard wiring) on 2.1.246 without error.
4. **Accepted fixture suites on the upgraded machine:** capability-probe tests **18 passed**
   (after the re-baseline below), statusline handler + telemetry core + subagent telemetry +
   bounded contracts + runtime supervision **228 passed**, 0 failed.

## 5. Drift tooth fired RED, then re-baselined (R168 step 9 — recorded, not silent)

On first post-update run, `test_live_reprobe_claude_version_matches_fixture` **FAILED exactly as
designed** (live 2.1.246 ≠ frozen 2.1.220 fixture) — the version-drift tooth works. Re-baseline
(this task's deliverable, packet allowed_paths widened accordingly and recorded): the live drift
tooth now targets the post-update fixture; two new tests pin the dual-version pair
(`test_upgrade_pair_records_expected_versions`: pre fixtures freeze 2.1.220, post fixture
freezes 2.1.246, codex unchanged) and the post-fixture masking/shape contract. The 2026-08-25
and 2026-08-26 pre-update fixtures are retained untouched as the historical 2.1.220 record
(R181: nothing deleted).

## 6. Session integrity after the update (honest observation)

Post-update `claude agents --json` lists 5 sessions: this one (busy, old binary), three other
owner interactive sessions (`nyc-ami-calculator-*`, unaffected), and background `777b09da` now
displayed **`failed`** (was `blocked`) while its fields still say `waiting / permission prompt`.
Its process **is alive** (pid 21448 verified via tasklist, 189 MB) — nothing was killed; the NEW
daemon simply has not reconnected to a session that was already parked mid-permission-prompt for
~7 days, and displays it as failed until reattach. Recovery is the documented one-step path
(`claude attach 777b09da` or `claude respawn 777b09da`) and is left to you (it is your parked
review session with a pending permission decision; attaching from here could answer/disturb it).
Transcript is on disk regardless. Classified: display-state artifact, not a kill; recorded per
R168 rather than worked around.

## 7. Rollback plan (R168 step 9)

Supported path: `claude install 2.1.220` (official installer accepts an exact version), then
re-run the same canary set and repoint the drift tooth back. No regression requiring rollback
was found. If a later unit hits a 2.1.246 regression without a safe rollback → stop for the
owner (R168 step 9, unchanged).

## 8. Known limitations (disclosed)

- **Live statusLine payload on 2.1.246 not yet captured:** the statusLine feed is produced by
  interactive sessions; this session still runs 2.1.220. Handler tests are green and the
  no-leak contract is unchanged; the live 2.1.246 statusline fixture + no-leak re-proof lands in
  the FIRST fresh interactive session on the new binary (successor session or unit-C canary) —
  the same next-session discharge pattern accepted for M0-T091. Tracked in the campaign record.
- `/goal`, background-session dispatch, UserPromptExpansion live behavioral fixtures remain
  unit C/D/E/G deliverables (unchanged plan).
- **No runtime backend was activated** because the version command succeeded (R168 step 10):
  the supervisor stays SHADOW-ONLY; nothing consumes 2.1.246 features yet.

## 9. Prohibition compliance

No bypass flags persisted anywhere (canaries used `--strict-mcp-config` only); no MCP
servers/channels added; no dependency/lockfile change; no SDK; no PR touched; ledger unchanged
except this task's records.

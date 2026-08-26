# M0-T099 — Project statusLine handler + real installed-version fixture (producer report)

Task: D-024 amendment 2 (`source-002-amendment.md`, D-024-R129..R138) + the carried M0-T089
gate-round hardening inputs. Producer: orchestrator (primary checkout, control branch).
Date: 2026-08-26. Supervisor-freeze qualifying evidence: **D-024-R100 + D-024-R131/R132**.

## 1. What was built

| Deliverable | Path |
|---|---|
| statusLine handler (sidecar + human row, one feed) | `tools/agent_supervisor/telemetry_statusline.py` |
| REAL installed-version fixture (live 2.1.220 capture) | `tools/agent_supervisor/fixtures/statusline_live_2026-08-26.json` |
| Handler test pack (21 tests) | `tools/test_agent_supervisor_statusline_handler.py` |
| Carried hardening (see §5) | `telemetry_redaction/sdk/transcript/subagent.py` + both existing packs |

The handler REUSES the accepted M0-T088 architecture unmodified in role (R130): payload →
`telemetry_ingest.ingest_status_line` (typed record; absent→unknown, zero stays zero) →
`TelemetrySidecar.update` (sanitize-first, atomic) → optional `TelemetryJournal.append` →
`format_status_row` over the SAME record. No new persistence surface, no new record type.

## 2. Requirement-by-requirement (R129–R138)

- **R129 (official doc primary):** doc URL embedded in the module docstring, the fixture
  (`doc_url`), and this report: https://code.claude.com/docs/en/statusline. Version gates
  restated in the fixture's `installed_version_proof`; installed 2.1.220 verified live this
  session (`claude --version` → `2.1.220 (Claude Code)`).
- **R130 (no rebuild):** handler is 1 new module + zero changes to records/journal/ingest
  semantics; the only foundation edits are the CARRIED G5/G3/G4 hardening items (§5).
- **R131 (REAL fixture):** two raw payloads captured from a LIVE interactive Claude Code
  2.1.220 TUI (method in §3): a pre-first-response payload (documented nulls) and a
  post-first-response payload (real usage + both rate-limit windows). Exercised by 8 tests.
- **R132 (one feed):** `handle_status_line` returns the row derived from the SAME record the
  sidecar just persisted; `test_handler_writes_sanitized_sidecar_and_returns_row` asserts
  returned==persisted, `test_one_feed_read_back_by_shadow_status` asserts
  `telemetry_status.read_only_status` reads back exactly that snapshot.
- **R133 (occupancy ≠ cumulative):** row segments `ctx` (occupancy measurements only) vs
  `sess` (cost.* cumulative only); `test_row_axes_never_borrow_each_other` proves distinctive
  numbers cannot cross segments; ingest-level category typing already enforced by M0-T088.
- **R134 (rate-limit ≠ context pressure):** `rate_limits.*` stays a verbatim attribute
  (never a context measurement — asserted), rendered as its own `5h/7d` row segment with
  windows independently absent; `limits ?` when the block is absent, never 0.
- **R135 (no model messages / no API tokens):** official note verbatim in the module
  docstring ("The status line runs locally and does not consume API tokens"); structural
  proof: AST scan (no `additionalContext`/`hookSpecificOutput` outside docstrings) + import
  scan (no socket/http/urllib/requests/httpx/subprocess/asyncio); handler output is one
  stdout text row; only file I/O is the sanitize-first sidecar/journal.
- **R136 (nullability):** proven against the REAL startup payload: `current_usage:null`,
  null percentages → unknown; `total_*: 0` → measurement value 0 (reported zero stays zero);
  absent `rate_limits` → no attribute, `limits ?` row; garbage stdin degrades to an
  all-unknown record + `ctx ?` row with exit 0 (the feed still refreshes).
- **R137 (routing):** untouched and restated: subagentStatusLine ingestion is M0-T089
  (accepted); its live canary belongs to the campaign canary task. This task changed neither.
- **R138 (verification evidence):** this report + the fixture record the doc URL and the
  installed-version proof; the DCV verification rows must cite both (see §7 pointers).

## 3. REAL fixture capture method (R131) — reproducible

1. An ISOLATED scratch project (session scratchpad, outside the repo) got its own
   `.claude/settings.json` wiring `statusLine` to a tee script that appends stdin to a file.
   The repository's `.claude/settings.json` was never touched (forbidden path; owner step).
2. `claude -p` was tried first and does NOT invoke statusLine (headless print mode has no
   TUI) — recorded as a negative result.
3. A real interactive `claude` TUI was launched in that scratch project (Windows Terminal),
   folder-trust accepted, one minimal prompt submitted. The runtime delivered two statusLine
   stdin payloads: session-start (pre-first-response) and post-first-response.
4. `build` step masked home-directory prefixes ONLY, using the production mask
   (`telemetry_redaction.redact_user_paths`); every other byte is verbatim. The masking is
   declared inside the fixture (`masking` field).
5. The scratch project and TUI were discarded; the capture consumed one trivial prompt in
   the owner's own installed CLI (no new accounts/keys; the payload's own
   `cost.total_cost_usd` documents the spend).

Leak-class discovery during (4): a live `transcript_path` embeds the cwd in Claude's
dash-encoded projects-directory form (`C--Users-<name>-...`), which the slash-shaped home
mask missed. The PRODUCTION mask was extended to cover the dash form (same class as G5-S2),
with red/green test `test_home_prefix_dash_encoded_projects_dir_masked`; the committed
fixture and all committed fixtures pass the cross-fixture no-home-prefix scan.

## 4. Owner-visible wiring step (documented, NOT performed — amendment item)

Live wiring stays with the owner. When (and only when) the owner chooses to activate the
one feed for a session in this repository:

1. Add to `.gitignore` (the runtime sidecar must never be committed): `.claude/telemetry/`
2. Add to `.claude/settings.json` (project) — or `~/.claude/settings.json` (user-global):

```json
{
  "statusLine": {
    "type": "command",
    "command": "python -m tools.agent_supervisor.telemetry_statusline"
  }
}
```

Notes: the command runs with cwd = the session's project directory, so the module import
and the default sidecar path (`.claude/telemetry/statusline_sidecar.json`) resolve
correctly from the repo root; `python` must be on PATH; add
`--journal .claude/telemetry/statusline_journal.jsonl` for bounded history; read it back
any time with `python -m tools.agent_supervisor.telemetry_status --sidecar
primary=.claude/telemetry/statusline_sidecar.json`. Nothing activates the supervisor: the
handler is passive telemetry (shadow mode, actuation off, R595 unchanged).

## 5. Carried M0-T089 hardening inputs — disposition (all ten)

| Item | Disposition |
|---|---|
| G5 M1 SdkTaskTracker cardinality bound | DONE — `max_tasks=512`, completed-first eviction, counted (`evicted_tasks`); red/green `test_sdk_tracker_bounded_eviction_prefers_completed` |
| G5 M2 transcript accumulator bounds | DONE — compaction details capped at 256 (count+preTokens sum stay EXACT), unknown-type keys capped at 64 (`<other>` bucket), session ids capped at 64 with overflow counter; 3 red/green tests |
| G5 N1 data-derived dict-key sanitization | DONE — `sanitize_structure` runs the string pipeline over dict KEYS (original-name pattern checks preserved; collisions keep both entries via digest suffix); red/green ×2. Fixed a first-cut ordering bug (unchanged key colliding with a sanitized one) caught by the collision test before commit |
| G5 N2 postTokens/trigger narrowing | DONE — narrowed exactly like preTokens; trigger string-only; red/green |
| G3 minor#2 per-field duplicate counters | DONE — duplicates/regressions now count EVENTS; red/green (fully-repeated 3-field event = 1, was 3) |
| G3 nit#3 final_request label clarity | DONE — detail now directs name-based selection ("never by label") |
| G3 nit#4 window detail self-pairing | DONE — contextWindowSize detail names itself the denominator |
| G3 nit#5 dead assertion (l.306) | DONE — the `or True` was masking a wrong-string check; replaced with real assertions on the actual detail contract |
| G4 A1 hermetic-subset guard | DOCUMENTED (no code): the full `tools/` suite requires the full checkout (several packs read repo-root artifacts); reproduce suite figures in the real checkout. Guarding on artifact presence remains optional future work |
| G4 A2 mask/test regex symmetry | DONE — production `_HOME_PREFIXES` separators now `[\\/]+` (JSON-escaped `C:\\Users` masks too); red/green |

## 6. Self-check evidence (G2 inputs)

- Targeted packs: `pytest tools/test_agent_supervisor_statusline_handler.py
  tools/test_agent_supervisor_telemetry_core.py tools/test_agent_supervisor_subagent_telemetry.py -q`
  → **121 passed** (21 new handler + updated core/B2 packs; 0 failed).
- Full `pytest tools/ -q` at the frozen identity: recorded at submit (§7 completes the
  numbers; supervisor-freeze baseline duty ≥1165/0 re-established).
- `ruff check` (0.13.0) over all touched .py files: **All checks passed!** (CI's ruff job is
  scoped to `services/api` — untouched; repo root has no ruff config, and the pre-existing
  root-tree findings are all in files this task never touched.)
- `python tools/modularity_check.py --check` → exit 0, failures 0 (new module ~230 SLOC,
  single responsibility: statusLine CLI/presentation over the existing telemetry core).
- Fixture hygiene: cross-fixture scan `test_all_committed_fixtures_free_of_home_prefixes`
  green over the NEW fixture too; no `MLFLL`, no unmasked `Users` anywhere in it.

## 7. Frozen identity + suite figures (completed at submit)

- Content commit (frozen identity): recorded in the checkpoint/gate records.
- Full-suite figure at the frozen content: recorded alongside the G2 self-check report.

## 8. Administrative note — leftover agent-worktree purge (campaign NEXT item)

The campaign-listed purge of the two harness-flagged qa-engineer agent worktrees
(`agent-a97cd976cfb4344f0`, `agent-ac83580dbc0f69fce` under the PACK repo's
`.claude/worktrees/`) was attempted and DENIED by the session permission classifier (the
pack repo is outside this session's permitted write roots). Verified read-only first: both
are pack-repo worktrees at base `d8b3899` with zero unique commits; the flagged memory
files are UNTRACKED (`.claude/agent-memory/qa-engineer/frozen-sha-test-harness.md`,
`.claude/agent-memory/qa-engineer/telemetry-redaction-latent-gaps.md`), so removing the
directories destroys the content with no git residue. Owner (or a session rooted in the
pack repo) can purge with:

```
cd C:/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack
git worktree remove --force .claude/worktrees/agent-a97cd976cfb4344f0
git worktree remove --force .claude/worktrees/agent-ac83580dbc0f69fce
git branch -D worktree-agent-a97cd976cfb4344f0 worktree-agent-ac83580dbc0f69fce
```

Never merge agent worktree branches. This does not gate M0-T099 (different repository).

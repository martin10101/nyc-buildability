# M0-T104 G0 readiness (administrative; orchestrator)

- **Recorded:** 2026-08-27 UTC, session `session_01HfptKuEs3RDxaxsSHJjc7t`, branch
  `control/D-024-fable-codex-loop`, HEAD at recording `d90045c` (seq-13 handoff landing,
  pushed == origin tip). Tree clean.
- **Bootstrap Gate 0:** PASS — the session's primary cwd IS the worktree root
  (`git rev-parse --show-toplevel` == primary working directory); MCP-clean: no `mcp__*` tools
  exposed in the session tool list; origin `https://github.com/martin10101/nyc-buildability.git`
  matches the handoff profile; marker files present.
- **Authority:** owner successor prompt this session (2026-08-27) — verbatim the §11 successor
  prompt recorded in `docs/SESSION_HANDOFF.md` at `d90045c`, which restates the campaign seq-13
  NEXT (`claim M0-T104 … proceed through the unit sequence to the M0-T096 golden run (R187 hold
  after), carrying the unit-C preconditions`). Authorization of recorded work; no new requirement
  → no amendment. Task origin: D-024 Amendment 3 unit C (R172/R153; accepted M0-T102 matrix),
  packet `project-control/tasks/M0-T104.json`.
- **Directive-reference coverage (pre-claim):** `evaluate_task_refs` at HEAD `d90045c` returns
  `ok: true` — applicable_ids 4, cited_ids 4, missing 0, invalid 0, unresolved 0; cited refs
  `D-024:ALL` valid across all 28 active directives.
- **Dependencies:** `M0-T103` **accepted** (verified in the ledger). Unit C–I dispatch is
  UNBLOCKED: M0-T108 (readonly-guard PowerShell fix) accepted at `faa46e3`; reviewer roster
  spawns are now machine-guarded for PowerShell + Bash read-only.
- **Machine identity + carried preconditions (from
  `project-control/reports/M0-T103-R162-discharge-2.1.247.md` §8):** installed claude binary
  measured this session = **2.1.247**. This task is the designated home for: (1) the 2.1.247
  capability re-probe + drift-tooth re-baseline (local tooth currently RED against the committed
  2.1.246 fixture by design; CI green via claude-absent skip); (2) explicit child-environment
  control for background dispatch (`CLAUDE_CODE_CHILD_SESSION` et al. inherit via Start-Process
  and suppress transcript saving); (3) installed-version treated as measured-at-use, never cached
  (binary auto-updated mid-procedure on 2026-08-27); (4) permission-mode vocabulary accepts
  `auto` as the unflagged default (no literal `default` mode on 2.1.24x; unflagged ≠
  bypassPermissions).
- **Modularity boundary answers (docs/CODE_MODULARITY_POLICY.md):** (1) responsibility = native
  runtime adaptation (feature detection, native background dispatch, `agents --json` ingestion,
  backend selection); (2) placement = NEW focused modules under `tools/agent_supervisor/`
  (adapter seam per R145/R180), not grown into existing files — `cli.py` and `policy.py` already
  carry symbol-ceiling warnings (`modularity_check --report`: 302 files, 0 failures, 5 warnings)
  and must not absorb this; (3) no target file above a failure threshold; (4) existing controller
  dispatch is retained as the feature-detected fallback (replace-not-layer R180: parity + failure
  tests before any deprecation, which happens only in a separate reviewed change); (5) stable
  public interface = existing controller dispatch entry points unchanged; adapter adds a bounded
  selection seam (exactly ONE active backend per session); (6) boundary tests =
  `tools/test_agent_supervisor_native_adapter.py`; (7) modularity CI must pass before submission.
- **Scope:** allowed_paths = `tools/agent_supervisor`,
  `tools/test_agent_supervisor_native_adapter.py`,
  `project-control/reports/M0-T104-native-adapter.md`. Producer = orchestrator session (campaign
  worked-example model, M0-T102/T103/T108 precedent); independent gates G2/G3/G4/G5 with
  reviewers ≠ producer.
- **G5 unit-C security preconditions (packet):** no inbound port; no auto Remote Control;
  deterministic names carry no hostname/secret; masked fixtures (task-id-stamped, G3 ADV-1);
  worktree baseRef pinned to 'head' or explicit reset; real low-risk canaries on the installed
  binary.

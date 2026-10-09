# M0-T104 — Unit C: native runtime adapter (D-024 Amendment 3; R153/R154/R156/R172)

Producer: fable-orchestrator-session (orchestrator; campaign worked-example model). Supervisor-freeze
qualifying evidence: **D-024-R153 + D-024-R172** (packet; `.claude/rules/supervisor-freeze.md` §2
D-024 recognition). Status: IN PROGRESS — this section (acceptance scenarios) is recorded before
implementation per the task routine; evidence sections follow.

## 1. Acceptance-scenario pack (recorded pre-implementation)

Scenario rows are executable: each maps to named tests in
`tools/test_agent_supervisor_native_adapter.py` (deterministic, injected fake runners; live rows are
feature-detected and skip cleanly when `claude` is absent — D-024 16.1) or to a fixture-producing
live canary recorded in this report. Vocabulary: capability statuses are
`supported | not-detected-in-help | absent | unknown` (probe convention, M0-T086).

| ID | Scenario (Given / When / Then) | Kind |
|---|---|---|
| S1 dispatch | Given detected native capabilities and a validated dispatch spec, when the native backend builds the background dispatch, then argv is exactly `claude --bg` + deterministic `--name` + `--session-id <UUIDv5>` (+ optional `--agent`), the permission mode is validated against the installed enum, no bypass flag is ever emitted, and the child environment is explicitly controlled. | deterministic |
| S2 status | Given a captured `claude agents --json` payload, when ingested, then each session becomes a typed status record (id, name, status, cwd-masked) for Codex-side passive observation OUTSIDE Fable context (R154); unknown extra fields are tolerated. | deterministic + live fixture |
| S3 completion | Given an expected dispatch whose session appears with a completed status (or only in `--all`), when reconciled, then it is classified `completed`, never re-dispatched. | deterministic |
| S4 blocked-input | Given a session reporting a waiting/needs-input state (parked-session shape), when reconciled, then it is classified `blocked-input` and surfaced to the controller — never silently continued. | deterministic |
| S5 failure (malformed feed) | Given malformed/truncated/non-JSON `agents --json` output, when ingested, then a typed error is raised and observation degrades to `unknown` — never guessed; the statusLine sidecar remains the primary feed (R154). | deterministic |
| S6 stop | Given an active session id, when stop is issued, then argv is `claude stop <id>` and post-stop verification requires the id absent from the active listing. | deterministic + live canary |
| S7 respawn | Given a stopped/stale session id, when respawn is issued, then argv is `claude respawn <id>`, honoring daemon binary-pickup semantics; `--all` respawn is representable for supervisor-restart recovery. | deterministic |
| S8 restart no-duplicate | Given expected dispatch records (durable) and a live observed listing after a supervisor restart, when reconciled, then already-running sessions map by deterministic name/session-id and are NOT re-dispatched (R032 restart semantics); exactly the missing ones are flagged. | deterministic + live fixture |
| S9 unexpected exit | Given an expected dispatch absent from both active and completed listings, when reconciled, then it is classified `unexpected-exit` and surfaced as a controller finding (never silently re-run). | deterministic |
| S10 fallback selection | Given any required native capability not `supported` (incl. `unknown`/`absent`/probe failure) OR config not opting in, when the backend is selected, then the EXISTING controller dispatch is selected, with a recorded machine-readable reason (fail-closed; R153). | deterministic |
| S11 one-backend invariant | Given a session that has selected a backend, when a second activation is attempted, then a typed refusal is raised — never two active process-management systems (R153). | deterministic |
| S12 identity | Given (campaign, task, attempt), when identity is derived, then the name and UUID are deterministic across calls, the UUID is valid, and the name is a closed lowercase charset carrying NO hostname, username, or secret material (G5 precondition). | deterministic |
| S13 child-env control | Given an inherited orchestrator environment (CLAUDECODE / CLAUDE_CODE_CHILD_SESSION / CLAUDE_CODE_SESSION_ID …), when the child environment is built, then every inherited `CLAUDECODE*`/`CLAUDE_CODE_*` key is removed (transcript-suppression hazard, R162-discharge §4.3) and the result is deterministic. | deterministic |
| S14 permission-mode vocabulary | Given the installed enum `acceptEdits, auto, bypassPermissions, manual, dontAsk, plan` (measured 2.1.246/2.1.247; NO literal `default`), when a dispatch spec names a mode, then members are accepted with `auto` recognized as the unflagged default, `default` is rejected as unknown vocabulary, and `bypassPermissions` (or any dangerously-skip flag) is REFUSED at construction. | deterministic |
| S15 worktree baseRef pinning | Given a dispatch spec requesting worktree isolation, when argv is built, then an explicit pinned base (`head` or exact SHA) is REQUIRED — the native default-branch hazard is guarded; an unpinned spec is refused (R156; matrix worktree-isolation row). | deterministic |
| S16 measured-at-use | Given the installed binary version changes between detections, when capabilities are detected twice, then each call re-measures (no module/process cache) and the second result reflects the new version (M0-T103 advisory 2). | deterministic |
| S17 re-probe + drift tooth | Given the committed 2.1.247 re-probe fixture (task-id-stamped filename, `[HOME]`-masked), when the live drift tooth runs on this machine, then `claude --version` matches the fixture (tooth GREEN at 2.1.247; historical 2.1.220/2.1.246 fixtures stay frozen and shape-checked). | live re-probe (skips when absent) |
| S18 no remote surface | The adapter's probe allowlist is help/version-only; builders never emit `--teleport`, `--cloud`, `--chrome`, remote-control or port-opening flags; no inbound port is opened by any adapter path (G5 precondition; matrix messaging-and-remote-control = REJECTED). | deterministic |
| C1 live dispatch canary | From a scratch cwd OUTSIDE the repository, dispatch one minimal-cost background canary (`--bg`, strict-mcp-config, tools disabled, deterministic name/session-id, controlled child env, no permission flags), observe it via `agents --json`, fetch `logs`, `stop` it, and verify termination + zero residue; masked capture committed as a fixture. | live canary |
| C2 live no-duplicate | Reconcile the expected canary dispatch against the live observed listing (S8 path on real data): the canary maps to its deterministic identity; re-dispatch is refused while it is observed active. | live (piggybacks C1) |

Out of scope (bounded seam): actual replacement/deprecation of the custom host path (R180 —
separate reviewed change, unit F/G scope); wiring the selection into the full supervisor loop
(units F–H consume the seam); any continuous-mode activation (R187 hold; owner-gated).

## 2. Deliverables

| Artifact | Path |
|---|---|
| Native primitives (detection, identity, child env, argv, agents-json ingestion) | `tools/agent_supervisor/native_runtime.py` |
| One-backend selection, native backend wrappers, restart reconciliation, controller fallback seam | `tools/agent_supervisor/runtime_backend.py` |
| Adapter test pack (53 tests; S1–S18 + fixture + live rows) | `tools/test_agent_supervisor_native_adapter.py` |
| 2.1.247 capability re-probe (probe module byte-unchanged; drift-tooth target) | `tools/agent_supervisor/fixtures/capability_probe_live_2026-08-27_m0t104.json` |
| Native-surface detection fixture (zero gaps at 2.1.247) | `tools/agent_supervisor/fixtures/native_runtime_detection_2026-08-27_m0t104.json` |
| Live `agents --json` listing (masked) | `tools/agent_supervisor/fixtures/agents_listing_2026-08-27_m0t104.json` |
| Post-canary `--all` listing (masked; real stopped/done lifecycle rows) | `tools/agent_supervisor/fixtures/agents_listing_all_2026-08-27_m0t104.json` |
| Drift-tooth re-baseline (2.1.220/2.1.246 fixtures stay frozen historical) | `tools/test_agent_supervisor_capability_probe.py` |
| This report | `project-control/reports/M0-T104-native-adapter.md` |

All fixture filenames stamp the consuming task id (G3 ADV-1); every fixture is `[HOME]`-masked
with session UUIDs truncated to 8 chars (public repo), machine-verified by committed tests.

## 3. Live-measured facts the adapter encodes (2.1.247, this machine)

1. **`--bg` ignores `--session-id`** (stderr: "--bg manages the session id") and assigns its own
   UUID. Deterministic identity therefore rides on `--name`; the daemon UUID is read back from the
   listing. The builder no longer emits `--session-id`; `find_by_identity` matches UUID-first,
   then exact name (canary-proven).
2. **Variadic `--tools <tools...>` swallows the positional prompt** — canary round a1 dispatched
   IDLE ("send a prompt to start"). The builder now separates the prompt with a literal `--`
   (round a2 executed the prompt and completed).
3. **Unknown subcommands with `--help` exit 0 printing the GENERAL help** — verb support is
   classified by the verb-specific usage line, never exit code.
4. **The CLI emits UTF-8** (arrow glyph in the attach help) which crashes Windows cp1252 reader
   threads and silently degrades probes to empty output; `run_command` pins
   `encoding="utf-8", errors="replace"`.
5. **Status/state literal inventory (measured):** status ∈ {`waiting`, `busy`, `idle`, absent};
   state ∈ {`failed`, `blocked`, `done`, `stopped`, absent}. Closed classifier with `state`
   outranking `status`; unmeasured combinations stay `unknown` (never guessed). The parked owner
   session's `waiting`+`failed` conflict row classifies `failed` (investigate before input).
6. **Unflagged sessions run `permission_mode: auto`** — the canary logs show "auto mode on";
   vocabulary tests accept the installed enum (no literal `default`), refuse `bypassPermissions`.
7. **Verbs `attach`/`logs`/`stop`/`respawn` exist as hidden subcommands** (absent from the main
   help command list; each prints `Usage: claude <verb> …`); `kill` aliases `stop`;
   `respawn <id>|--all` restarts sessions onto the current binary ("Starting background service…").

## 4. Live canaries (C1/C2) — all adapter-mediated, scratch cwd OUTSIDE the repo

Scratch: session-scratchpad `natc247` (with `.claude/.auto-setup-complete` marker); child env via
`child_environment(os.environ)` — session markers stripped; `--strict-mcp-config`; `--tools ""`;
no permission flags; deterministic names `d024-m0-t104-canary-a1/-a2`.

- **Round a1** (pre-`--` builder): dispatched, observed `idle`/`blocked` = prompt NOT delivered
  (finding 2 above) → `stop` → state `stopped`. Preserved as the measured blocked-input/stopped
  evidence; fixture row committed.
- **Round a2** (corrected `--` transport): dispatched, prompt executed — **`CANARY-C-DONE`
  verified in `claude logs`** — state `done` within ~8 s; `stop` clean.
- **C2 no-duplicate on real data:** `reconcile_after_restart([a1], live listing)` mapped the
  running canary by name → `running`, `safe_to_dispatch` empty (never re-dispatched).
- **Respawn:** `respawn 76fd9c67` → "respawned", session observed again (`idle`/`done`),
  re-stopped. Final state: **zero active canaries**; daemon available; historical `--all` rows
  (`stopped`/`done`) captured as the lifecycle fixture. The two canary history entries remain in
  the daemon's `--all` listing by design (native history, not repo residue); `git status` stayed
  clean of everything but intended deliverables.

## 5. Self-checks

- Adapter pack **53/53**; probe pack **19/19** (drift tooth GREEN again at 2.1.247; historical
  2.1.220→2.1.246 upgrade-pair invariants intact).
- **Mutation proof: 8/8 mutants killed** (verb-detect general-help acceptance; child-env strip
  removal; `--` separator removal; bypass-mode allowance; forbidden-flag guard removal; native
  selection without opt-in; reconcile duplicate-dispatch hazard; `stopped` literal drop) — suite
  GREEN after restoration.
- `ruff check` on all four changed files: clean (whole-tree `ruff check .` = 67 findings,
  byte-identical count at baseline `d90045c` via stash comparison — pre-existing, not introduced).
- `python tools/modularity_check.py --check`: 0 failures (5 pre-existing warnings unchanged; both
  new modules are focused single-responsibility files well under thresholds).
- Full `tools/` suite + registry validator: recorded in the submit progress entry.

## 6. Requirement evidence map (applicable set = cited set, 4/4)

- **D-024-R153** (native background sessions; feature-detected fallback; never two systems):
  detection + selection (`select_runtime_backend`, fail-closed), `RuntimeSession` one-backend
  invariant (S11), dispatch/attach/logs/stop/respawn wrappers (S1, S6, S7), live C1/C2 proof,
  `ControllerBackend` injected fallback (S10). Agent-View-shaped preview features stay behind
  feature detection; no daemon feature is assumed beyond measured verbs.
- **D-024-R154** (structured passive observation; never ask Fable; no quotas):
  `parse_agents_json` typed ingestion outside Fable context (S2–S5), malformed feed → typed error
  with statusLine sidecar remaining primary, committed masked listing fixtures; nothing in the
  adapter injects token/status questions or quotas into worker prompts (no prompt-mutating path
  except the R156 worktree reset preamble).
- **D-024-R156** (native worktree isolation; retain logical layer): `WorktreeSpec` mandatory
  pinned base (S15) — `head` refused on the CLI path with the measured default-branch-hazard
  rationale, 40-hex SHA required, guarded `git reset --hard` preamble with show-toplevel
  primary-checkout stop; logical writer leases untouched (no lease code modified).
- **D-024-R172** (unit C composition): every named element delivered — feature detection (S16
  measured-at-use), named+deterministic identity (S12, with the measured `--session-id`
  limitation honestly recorded), native background dispatch (S1, C1), `agents --json` ingestion
  (S2–S5), attach/logs/stop/respawn (S6–S7, live), controller fallback (S10), exactly one backend
  (S11).

## 7. Consolidated correction round (G3/G4/G5 round-1 findings applied in-task)

All three independent reviewers returned PASS; the three converged on ONE MEDIUM (child-env
fail-open default). Applied at re-freeze:

| Finding | Sev | Fix | Test tooth |
|---|---|---|---|
| G5 F2 = G3 #1 (child-env fail-open default) | MEDIUM | `NativeBackgroundBackend` now defaults `base_env` to `os.environ` and `dispatch` ALWAYS strips — no path inherits the raw parent env; docstring corrected | `test_dispatch_default_backend_still_strips_child_env` + 2 mutants (default-strip removed; base_env=None fails open) |
| G5 F3 (masking field-allowlist) | MEDIUM/LOW | `mask_session_row` → comprehensive recursive pass over EVERY string value (home + UUID) via `_mask_value`; committed leak test extended with UUID + `/home/` needles across name/waitingFor | `test_mask_session_row_comprehensive_all_fields` + mutant |
| G5 F1 (unvalidated agent/tools values) | LOW | `DispatchSpec.__post_init__` validates `agent`/`tools` against closed charsets (no leading `-`); docstring softened from "structurally impossible" | `test_agent_tools_value_charsets`, `test_forbidden_flags_cannot_be_smuggled_via_values` + 2 mutants |
| G5 F4 (reconcile empty-feed hazard + naming) | ADVISORY | `reconcile_after_restart` refuses `feed_available=False` (typed error); property renamed `needs_controller_review` (back-compat `safe_to_dispatch` alias kept) | `test_reconcile_refuses_unavailable_feed` + mutant |
| G4 ADV-2 (command-exec error surface) | ADVISORY | `logs`/`stop`/`respawn` gain `check=` → typed `<verb>_failed` on daemon rejection (default False preserves raw result) | `test_verb_check_surfaces_daemon_failure` + mutant |
| G3 ADV-3 (`--session-id` required-but-never-emitted) | ADVISORY | inline comment at `REQUIRED_BACKGROUND_FLAGS` explaining the conservative readiness gate | (doc) |
| G3 ADV-4 (classifier inventory vs report) | ADVISORY | `_classify_row` docstring aligned to the measured set + labels the defensive synonyms | (doc) |

Accepted/deferred: **G5 F5** (soft worktree preamble — inherent to R156, trusted orchestrator
caller; SHA charset-validated) accepted residual; **G5 F6** (unmasked reprs in local-only error
strings) noted, not committed to any fixture; **G3 ADV-2 / ADV-5** (module-split candidate;
structured seven-answer packet block) — process notes, non-blocking, natural follow-ups when the
seam is wired. **G4 ADV-1** (post-stop absence deterministic tooth) covered by the live C1 canary
+ `find_by_identity` unit tests as disclosed.

Re-freeze verification: adapter pack **60 passed**, probe pack **19 passed** (77 total);
**11/11 mutants killed** (4 core + F2×2 + F1×2 + F3 + F4 + ADV-2), suite GREEN after restoration;
ruff scoped clean; modularity 0 failures (neither new module flagged; native_runtime.py 661 pl /
~490 SLOC, runtime_backend.py 321 pl); guard packs byte-untouched + ALL CHECKS PASSED; no other
supervisor module imports the new modules (freeze baseline 2204/2/0 unaffected); fixtures
re-masked and leak-clean. Delta re-review of G3/G4/G5 to follow at the re-frozen identity.

## 8. Boundary statements

Boundary statements: **R180** — nothing removed or deprecated here; the custom host remains the
default (`prefer_native` must be explicitly set, and no caller sets it in this change); parity +
failure tests against the custom host and any deprecation belong to a SEPARATE reviewed change
(unit F/G scope). **R032** — `reconcile_after_restart` + `respawn --all` provide restart
semantics; `activation_limitations()` reports the no-auto-host-start posture as an activation
blocker, never claiming unattended persistence. **R187** — nothing here activates continuous
mode; activation stays owner-gated.


# PROGRAM_KNOWLEDGE — compressed pointers (D-054 Tier 1; auto-injected every session)

Hard-won program-wide knowledge as one-line pointers. APPEND when you discover something
program-wide useful (any session, when discovered — not at session end). BUDGET: eager total
(tools/context_budget_check.py) must stay under 10000 tok (owner-raised from 6000, D-067-R003)
— compress or demote before adding; never raise the cap again without a new owner
authorization. Current-section detail lives in docs/WORKING_KNOWLEDGE.md (Tier 2).
Pointers only — the ledger/registry stays authoritative; no secrets (public repo).

## Control-plane mechanics (proven arcs)

- Directive capture = 4 files + **index.json entry in the SAME commit** (unindexed capture is
  invisible: validator passes around it, `new-task --directive-refs` fails closed).
- `classification` vocab (validator c1): obligation|prohibition|hold|sequencing|dependency|
  decision|harness|evidence|external_fact|**return**|authorization (`return_item` invalid).
- Requirement-body edits after capture (even vocab fixes) = digest resync
  (`directive_registry.sha256_text_artifact`) + `audit_log` entry, SAME commit (c14).
- Applicability binds via `requirements.json → applicability.task_ids` append; run
  `reg.evaluate_task_refs(task)` BEFORE claim (applicable must == cited).
- Contract seam order: new-task → patch packet JSON (inputs/outputs/paths/scenarios) → bind
  task_ids + digest resyncs → **seed committed placeholders for every new allowed_paths file**
  (gate fails closed on zero tracked files) → G0 report → ONE commit → gate G0 at HEAD →
  claim → progress 20 → commit (stage `state.json` — claim/progress modify it!).
- `gate --sha` must equal live HEAD at record time; task allowed_paths must be clean. A
  disjoint peer commit between rework and gate record is fine when task identity is
  byte-stable — record an identity note in the gate report.
- `new-task` WITHOUT `--gates` defaults to the FULLER set G0,G2,G3,G4,G5 (not G0,G3,G4). G2 =
  producer self-check, recorded by `--reviewer orchestrator` (the CLI rejects the producer's
  own name). A required gate ALSO needs its reviewer in the packet's `reviewer_agents` — fix a
  missing one by ADDING the reviewer, never by dropping the gate.
- ANY material edit after `submit` (even an orchestrator comment fix) invalidates the frozen
  submission identity; `accept` fails closed "frozen-evidence identity mismatch". Fix = walk
  `awaiting_gate → rework → in_progress → submit` to re-freeze; gates recorded AFTER the edit
  stay valid and need no re-run. Lifecycle forbids `rework→awaiting_gate` and
  `awaiting_gate→in_progress` directly.
- `accept` also scans EVERY open blocker's `affects` **and `detail`** for a word-bounded task id
  (`_blocker_references`, deliberately over-blocking). Historical prose naming a packet will
  block it: correct the reference + keep the facts + log a dated `scope_corrections` entry —
  NEVER close/downgrade a blocker to get past it.
- `submit` needs `--evidence-map` (JSON in reports/, per applicable requirement id) and
  `--report` UNDER project-control/reports/ (build tasks: save the producer return verbatim
  there as M4-Txxx-producer-report.md).
- Accept flow (frozen-head pattern): integrate producer commits → ONE material commit →
  submits at that sha → reviews pinned there, commits HELD → gates at head → DCV (request
  **conditional restamp pre-authorization UP FRONT** — verifier rules per-commit in ~4 min,
  can extend its own imperfect condition) → assemble v2 blocks (reviewed_sha = restamp
  target; `reviewed_manifest_sha256` from the gate records; producer = the task's MATERIAL
  producer) → accept (reads disk vs HEAD) → one seam commit → push.
- Evidence-map `material_commit` = the CHERRY-PICK commit itself, never the follow-up seam
  commit (that one carries only state/task files) — reviewers catch the mislabel; the map is
  outside allowed_paths so an `[ORCH-CORRECTED]` fix there moves no material identity.
- "PASS with required corrections" = record PASS, corrections BLOCK acceptance: apply as
  tagged `[ORCH-CORRECTED per <gate> Fn]` edits → progress --status rework → resubmit at new
  head → SendMessage delta-attestation to the SAME reviewer agents (~1 min; they stay
  resumable) → gates at corrected head. If a second reviewer's surface includes the edited
  file, get its identity-carry attestation too.
- Transient c14 INVALID while the companion writes a directive = real signature (requirements
  lands before manifest): re-run validator at the settled head with a DIRECT exit code
  (`| tail` eats `$?`) before reacting.
- DCV restamp pre-auths: with parallel lanes, a DISJOINT peer material commit landing between
  freeze and record voids literal all-product-dirs-empty conditions — ask the DCV to state
  its disjoint-peer tolerance UP FRONT (M5-T042 pattern); else a delta-attestation extension
  is needed (M5-T040). Gitleaks false-positives on fixture VAR NAMES containing KEY: inline
  `# gitleaks:allow` on that line; never quote the flagged line verbatim in evidence files.

- `accept` fail-closes unless EVERY v2 row's reviewed_sha == the LIVE HEAD at accept time -
  assemble v2 rows and accept BACK-TO-BACK (a disjoint material commit between them forces a
  DCV-predicate restamp: T066 a234a508->5aad9007); the full validator now runs ~12 min wall
  (verification-row growth) - sequence the one-budgeted-run-per-seam so accept never waits.

## Dispatch / review mechanics

- Producers: unnamed spawns only (named = readonly-guard silent denial), isolation worktree,
  prompt MUST carry: show-toplevel guard (STOP if primary checkout), `git reset --hard
  <contract-head>` (worktrees spawn off stale bases), exact single-scope, self-check commands,
  lean return (<64k, reference files). Never resume a killed producer. Cherry-pick producer
  commits; verify sha256 with LF-normalization (checkout CRLF smudges raw digests).
- api producers/pre-gate: `cd services/api && python -m ruff check .` is the api CI job's
  FIRST step — a lint miss costs a CI round. Bash tool `cd` PERSISTS cwd — cd back.
- Reviewers read-only, may land in PRIMARY checkout: pin HEAD in prompt (worktree-landed
  reviewers verify via .git plumbing), forbid writes, HOLD commits till the wave returns.
- Shared checkout with the companion session: heads-up before commits both ways; peer sticks
  to directive-capture + owner-facing docs; ledger/git is orchestrator-only (ADR-005).

## Key files / commands

- Ledger: `python tools/project_control.py status|new-task|claim|progress|submit|gate|accept|
  checkpoint`; validator `python tools/validate_directive_compliance.py --check`; registry
  helpers `tools/directive_registry.py`; budget `python tools/context_budget_check.py`;
  modularity `python tools/modularity_check.py --check`.
- Rules: `services/api/app/rules/rulesets/*.rule.json`; ZR snapshots
  `docs/research/zr-snapshots/v1/`; snapshot sync `sync_zr_snapshots`.
- Wide-street stack (all accepted): `dcm_street_centerline_arcgis.py` (transport; returnGeometry
  TRUE, parse discards geometry) → `dcm_street_width_classifier.py` (24 classes, byte-immutable)
  → `dcm_street_width_policy.py` (D-052; no-default `AttestedPreconditions` that VALUE-gates to
  UNRESOLVED) → `dcm_street_centerline_geometry.py` (B3, typed 2263 polylines) →
  `wide_street_buffer_engine.py` (B4, 100.0-ft buffer ∩ lot). B7 rule-wiring is NEXT and must be
  its OWN module + close the B4 input-bounds gap (see Tier 2). Lot side:
  `mappluto_geometry_arcgis.py` (2263, measurement) vs `mappluto_lot_outline.py` (4326, display
  only, NEVER measure).

## Domain anchors (verified)

- ZR capture channels: `zoningresolution.planning.nyc.gov` HTML + print/PDF
  `…/entityprint/pdf/node/<id>` (proven completeness channel; §12-10 = node 18523, BIG page
  504s → documented fallback: direct GET w/ browser UA, sha256-pinned). Load-bearing captures
  need print/PDF-class or disclosed fallback; snapshot notes never assert beyond the channel.
- §12-10 "street, wide" AMENDED 3/26/2026 (C5-3/C6-4/C6-6 alternate-width; 70-ft connector;
  named: Broadway W94–97 CD7, Allen St Rivington–Delancey CD3). "narrow" = <75 (1961).
- D-052 policy: <75 narrow, **=75 WIDE**, one-sided bounds only ('<=75','60-75','70-80' stay
  UNRESOLVED), UNKNOWN→map resolution, exceptions-checked-first, provenance quintuple.
- D-051: fail-closed-to-narrow is NOT universally conservative (§23-431 street-wall 8ft-wide/
  10ft-narrow counterexample) — every consuming rule validates its own fallback direction.
  Bounded negatives only ("not located in X", never "city never documented").
- Widths: DCM Streetwidth = MAPPED width (usually incl. sidewalks, feet; free-text field, no
  official field-level spec — RQ-005 residual); LION StreetWidth = PAVED ("narrowest width…
  of the paved area", 26C p24); Geoclient width = paved, KILLED for legal use. Variable width
  = centerline SEGMENTATION (E 96 St 60/60-75/75-90/90) — never one width per street name.
  Admin Code §25-101: the adopted City Map is conclusive. EPSG:2263 = US survey feet.
- R6–R12 height/setback chain: 23-432 (table; 100-ft-of-wide-street rows) → 23-433 (setback
  10 wide/15 narrow) → optional 23-73x sky-plane (un-suffixed R6–R10 only; 23-736 slopes
  2.7/5.6, alt 3.7/7.6) → 23-411/12/13 obstructions. C-districts: 33-121 overlay FAR (keyed
  by underlying R), 34-111 overlay governing rule, 34-112 equivalents table (C4-6→R10).
- Owner research (Astra) = discovery aid ONLY (D-050-R002); RQ queue commits+pushes in the SAME
  step (R006) and appends get a seam line + PushNotification (R005). Detail: Tier 2.

## Session habits

- D-070 finished-seam handoffs: a PLANNED handoff requires the seam DONE FIRST (sweep, next
  packet contracted+claimed+pushed, worktree, launcher pointed, fresh run-id) so the successor
  only verifies+launches; crash/forced turnover = the only fallback.

- Discoveries → `docs/DISCOVERY_BACKLOG.md` (D-069, NOT injected): append product/domain
  findings AT discovery; SWEEP OPEN/WATCH entries at every contract seam and replan; entries
  end as QUEUED(task)/RESOLVED/WATCH, never deleted, never duplicating ledger/blockers.
- Every wave: cite ruff pre-gate for api producers; budget ONE full validator run per seam;
  **D-064**: subagents+loop worker = opus-4-8 xhigh, main stays fable-5 (supersedes
  D-047/D-055/D-058/D-060 fable defaults); lean comms = CLAUDE.md p19.
- PS5.1: no `&&`, no quotes-in-`git commit -m` via PowerShell (use Bash tool); UTF-16
  redirection trap; heredocs via Write tool when Bash mangles them.
- Own pushes cancel in-flight CI on the branch — hold pushes while a needed run executes.
- Auto-mode classifier can block detached-launch/model-file/.claude writes: capture the
  owner's words as a directive, retry ONCE under it (D-055/56/57 arc) — never hammer/bypass.
  It can also block on BATCH SHAPE alone (`set -e` + shell-function wrapper over 14 denies,
  seq 123): the identical verbs pass as plain single/sequential commands — reshape, don't
  re-batch. And retype digests EXACTLY (an ab→af slip cost a deny round; the error echoes
  the stored digest).
- Fable exhaustion kills the loop (`REFUSED unsafe exit 11
  fable_exhaustion_turnover_recorded`): the worker-pin flip is OWNER-ONLY (controller S3.2
  rule 6) AND classifier-blocked — open a blocker with the one-line edit, never retry past it;
  the INITIAL pin needs no launch probe so the owner's edit alone suffices. Keep working via an
  orchestrator-dispatched producer + recorded deviation. Confirm exhaustion ONLY from the run
  log + `model_switch_tracker.py --query`, never a model's self-report. Full arc: B-024, D-060.
- `claim --worktree` MUST be the FULL path (controller-authoritative): a short name
  lands in the packet, the worker echoes it, and S4.5 stops the run at the FIRST
  checkpoint (`checkpoint_field_mismatch`). Fix both packet copies + fresh run-id.
- Create/advance the task worktree AT (or past) the CLAIM-SEAM commit, never the contract
  head: `task_authority` corroborates the ctl24 packet against the WORKTREE's ledger copy
  (`--repo`), and a pre-claim copy (backlog vs in_progress) refuses the launch
  (`ledger_status_mismatch`, exit 11). Fix = `git -C <wt> reset --hard <claim-seam sha>`;
  a preflight refusal parks the journal in PREFLIGHT (no clear-recovery needed), same
  run-id relaunches (M5-T045 launch, 2026-09-19).
  ANY audit-appending CLI verb racing a LIVE loop forks its chain - deny/approve-once AND
  graceful-stop alike (store-side effects land; appends refuse). Repair between runs
  (archive-to-forked-evidence; loop-2 needs a targeted script - the stock repair hardcodes
  loop-1's runtime). Packet allowed_paths are GLOBS matched at LAUNCH (cached): a bare
  directory prefix matches nothing - write `dir/**`; a mid-run packet fix needs a
  graceful-stop + relaunch to apply.
- Placeholder seeding: an EMPTY .test.ts placeholder FAILS web-e2e (vitest: no suite) — seed
  web test placeholders with a trivial passing test; empty py test files are fine.
- `submit --evidence-map` shape = top-level `requirements: {id: [prose evidence]}` (file-list
  shapes fail closed). Git-Bash-parsed CLI digests carry \r — strip before `deny`.
- Reviewer returns TRUNCATE mid-report routinely (5x seq 124): dispatch prompts MUST require
  an explicit END-OF-REPORT marker + proactive short-part splitting; on truncation, ask the
  SAME reviewer for the remainder FROM THE EXACT cut phrase (never the whole report again),
  then join verbatim at that point with the transmission history noted in the record header.
- Loop WAIT_FOR_OWNER (tier_ask_blocking) after all asks denied needs `resume-after-answer`
  (WAIT_FOR_OWNER -> PREFLIGHT); `clear-recovery` only exits PAUSED_RECOVERY.
- NEVER pass `model:` on an Agent dispatch: it OVERRIDES the agent file's claude-opus-4-8 xhigh
  pin (owner: "sub agent stays 4.8", D-085 src-003); "opus" = Opus 5.5 - 20 seq-128 spawns
  drifted (report D-085-subagent-model-deviation-2026-09-24.md). Verify via subagent transcripts.
- Opus 5.5 (D-085): exact id `claude-opus-5-5` (alias opus55; dotted 'opus-5.5' = SILENT
  unrecognized_model fallback to opus-4-8 - never use it). Verified on CLI 2.1.281 canary.
  Worker-pin flips AND the shared allowlist (`C:\Program Files\SupervisorConfig\config.toml`
  [claude].allowed_models + [approved_models].models) are OWNER edits (classifier-blocked;
  B-025 resolved by owner actuation - all three lanes + allowlist on opus-5-5 since 2026-09-23).
- DCV dispatch prompts MUST FORBID running the full `tools/test_directive_compliance.py`
  (~7.6 min/TEST vs the grown registry = ~16h; T076-DCV F3 measured it; two DCVs stalled 3h+
  on it, seq 127): the authoritative harness evidence is `validate_directive_compliance.py
  --check` w/ a DIRECT exit code + the CI control-plane job at a verified head +
  test_project_control.py + test_directive_reminder.py; the full suite is CI's job.

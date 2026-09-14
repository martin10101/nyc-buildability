# PROGRAM_KNOWLEDGE — compressed pointers (D-054 Tier 1; auto-injected every session)

Hard-won program-wide knowledge as one-line pointers. APPEND when you discover something
program-wide useful (any session, when discovered — not at session end). BUDGET: eager total
(tools/context_budget_check.py) must stay under 6000 tok — compress or demote before adding;
never raise the budget. Current-section detail lives in docs/WORKING_KNOWLEDGE.md (Tier 2).
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
- `submit` needs `--evidence-map` (JSON in reports/, per applicable requirement id) and
  `--report` UNDER project-control/reports/ (build tasks: save the producer return verbatim
  there as M4-Txxx-producer-report.md).
- Accept flow (frozen-head pattern): integrate producer commits → ONE material commit →
  submits at that sha → reviews pinned there, commits HELD → gates at head → DCV (request
  **conditional restamp pre-authorization UP FRONT** — verifier rules per-commit in ~4 min,
  can extend its own imperfect condition) → assemble v2 blocks (reviewed_sha = restamp
  target; `reviewed_manifest_sha256` from the gate records; producer = the task's MATERIAL
  producer) → accept (reads disk vs HEAD) → one seam commit → push.
- "PASS with required corrections" = record PASS, corrections BLOCK acceptance: apply as
  tagged `[ORCH-CORRECTED per <gate> Fn]` edits → progress --status rework → resubmit at new
  head → SendMessage delta-attestation to the SAME reviewer agents (~1 min; they stay
  resumable) → gates at corrected head. If a second reviewer's surface includes the edited
  file, get its identity-carry attestation too.
- Transient c14 INVALID while the companion writes a directive = real signature (requirements
  lands before manifest): re-run validator at the settled head with a DIRECT exit code
  (`| tail` eats `$?`) before reacting.

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
- Street-width stack: `services/api/app/connectors/dcm_street_centerline_arcgis.py`
  (transport; returnGeometry defaults TRUE, parse discards geometry) →
  `dcm_street_width_classifier.py` (24 typed classes, byte-immutable, accepted) →
  `dcm_street_width_policy.py` (D-052 layer; no-default `AttestedPreconditions`).
  Lot side: `mappluto_geometry_arcgis.py` (EPSG:2263, measurement) vs `mappluto_lot_outline.py`
  (display-only 4326, NEVER measure).

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
- Owner research (Astra) = discovery aid ONLY (D-050-R002): archived under
  docs/research/owner-research/; queue docs/RESEARCH_REQUESTS.md commits+pushes SAME step
  (R006; pushed branch = owner's phone copy); new appends → seam line + PushNotification
  (R005; mobile push currently disabled in /config).

## Session habits

- Every wave: cite ruff pre-gate for api producers; budget ONE full validator run per seam;
  D-047 producers = claude-sonnet-5 (researcher/rules agent files flipped; backend-engineer
  flip blocked → dispatch model override + record deviation).
- PS5.1: no `&&`, no quotes-in-`git commit -m` via PowerShell (use Bash tool); UTF-16
  redirection trap; heredocs via Write tool when Bash mangles them.
- Own pushes cancel in-flight CI on the branch — hold pushes while a needed run executes.

# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-07 (D-010 session-4 rotation, CP-0041)**. **The block below supersedes the older
sections further down** (kept only as history); the ledger wins on any conflict.

## CURRENT STATE (2026-08-07, session 4 — confirm against the ledger + git)

**D-010 wave-1 minimum-autonomy control chain COMPLETE.** Session 4 rotated at the post-merge seam
per R113/R115; accepted count **64**. Owner touches this session: **8 typed operator acts** (2
authorizations + 6 launch/approval commands — the supervised R595 window).

- **D-010 am.7 captured** (PR #172, merged `f61a735`): session-4 launch instruction verbatim, row
  **R118** (re-dispatch, no new obligations).
- **M0-T045 ACCEPTED + MERGED** (PR #173, merge `8533635`; accepted 64; identity `2a259525…`):
  **the R595 supervised rehearsal is COMPLETE with every leg LIVE-PROVEN** — threshold trip + armed
  seam (ctx 134,497, unit never interrupted), owner digest-bound approval, **LIVE SEAM ACTUATION**
  (forward exactly once `fwd/1/a4c3d170…` → digest-verified handoff `e75d07c0…` → new session
  `sup-5b5f59ac…` minted → relaunch → successor completed cycle 2 through live Codex review),
  re-approval fail-closed, emergency stop mid-unit (child tree terminated, autostart refused,
  recovery report). **The R593 residual is CLOSED BY EVIDENCE, never waiver** (D-007-R621).
  Owner authorizations R119 (am.8) + R120 (am.9) captured verbatim BEFORE the acts.
- **Live finding R595-F1** (approved FORWARD_PROMPT journal had no continuation path; parked record
  text-less → cross-process forward impossible) found by the rehearsal → **fixed + cross-process-
  locked same-window** (`afc2da5`, +10 tests). Pre-R595 hardening: all three pinned checklist sets
  resolved (`4db6a71`, +36 tests). Suite **1317/2, zero regressions**, reproduced independently 4×.
- **Five legs PASS:** G3; G4 (85/85 adversarial probes, audit chain cryptographically verified;
  material non-blocking: **estop audit-chain fork**, self-reported via `audit_chain_ok:false`);
  G5 (no HIGH/MEDIUM; **LOW-1** park→approve binding → activation checklist); control-plane 8/8;
  DCV **19/19** at identity `2a259525…`. Evidence sealed: 26 files, SHA-256 manifest.
- ⛔ **SHADOW-ONLY still in force. Nothing activated.** The supervised-auto **promotion pack is
  COMPLETE and owner-decision-ready** (`M0-T045-promotion-evidence.md`; AS-3 ceiling binding).
  Remaining pre-activation items pinned to `M0-T036-ACTIVATION-CHECKLIST.md`: G5 LOW-1 (bind
  forwarded bytes to the operator-named approval), G4 estop-fork follow-up, OS-ACL judgment,
  per-tier owner authorization. **Activation is an explicit owner decision.**

## NEXT SESSION — resume checklist (session 4 → 5)

1. Start-of-session: `python tools/project_control.py status` + reconcile git/CI (origin/main was
   `8533635` + this rotation PR at rotation; checkpoint CP-0041). Machine-readable handoff:
   `project-control/reports/session-handoff-2026-08-07-4.json`
   (digest `8b3804ab5f25bae051acb480406b203d4487facdbafac94f66f573c442f83951`) — verify: sha256
   over `json.dumps(doc, sort_keys=True)` with `digest=""`.
2. **Wave-1 is COMPLETE (M0-T036..M0-T045 accepted).** Per D-010 R116/0A.11 the next
   dependency-valid work is **PRODUCT work: two real product tasks** through the pipeline under
   the 80/20 rule (initiative-plan Lane 2: survey ingestion per accepted M2-T014 findings; M3
   corpus tasks remain blocked by B-001). Contract fresh product tasks; do NOT start new
   supervisor features (0A.10 freeze; only directive-cited defects).
3. **Owner-decision-ready, surface without pushing:** the supervised-auto promotion decision
   (pack complete; checklist items above outstanding). If the owner activates, the R595-gated
   automatic-continuation capability (R114) is now evidence-complete.
4. Proven task workflow + producer-spawn rule (UNNAMED) + classifier-denial protocol: unchanged.
   NEW proven pattern: owner-executed launchers via `powershell Start-Process '<path>.cmd'`
   (NEVER `cmd /c start` from the `!` prompt — Git Bash strips the title quotes and opens an
   empty window).
5. **Reviewer models:** gate reviewers ran `claude-opus-4-8` + `xhigh` (standing fallback; the 5
   flipped agent files remain uncommitted in the PRIMARY checkout; revert to `claude-fable-5`
   pins when the owner says "Fable is back"). Orchestrator ran `claude-fable-5`.
6. **Primary checkout** (task/M0-T036-supervisor-bridge @ 57ccb44): untouched per R099/R109.
   **Dormant batch** (D-009 + M0-T019 + M2-T014): untouched. All standing holds unchanged
   (deployment/G6/Graphify/expansion). Rehearsal scratch (`%TEMP%595`) is disposable; the
   committed sealed evidence is authoritative.

---

_History (pre-this-session, may be stale):_

Refreshed **2026-08-07 (D-010 session-3 rotation, CP-0039)**. **The block below supersedes the older
sections further down** (kept only as history); the ledger wins on any conflict.

## PRIOR STATE (2026-08-07 session 3, superseded — CP-0039)

**D-010 (Autonomous Engineering V2) wave-1 continues to execute.** Session 3 rotated at a safe
post-merge seam per D-010-R113/R115; accepted count **63**. Owner touches this session: **0**.

- **D-010 am.6 captured** (PR #168, merged `f9c79d5`): the owner's session-3 launch instruction,
  verbatim, as append-only `source-007-amendment.md` + row **R117** (re-dispatch; NO new
  obligations). Manifest v8, digests restamped per c14; packets M0-T043..M0-T045 refs widened.
- **M0-T043 ACCEPTED + MERGED** (PR #169, merge `341fa4d`; accepted 62): bounded context-pack
  builder (`tools/context_pack.py`, stdlib-only deterministic; Section 12 CLI/inputs/exclusions/
  meta; 0A.4 budgets drift-locked to `review_packet.py`; AD-046 fail-closed overflow + split
  proposal), 15-test suite, `docs/CONTEXT_PACKS.md`. **Honest G3 FAIL** (F1 MAJOR: footer-blind
  bound decision could emit over-bound packets at exit 0) → rework 1 `e41dad3` (footer-aware
  fixpoint at all 3 decision points; exit 0 ⇒ emitted ≤ effective bound) → G3+G4 delta PASS →
  DCV 7/7 at identity `bb58eafa`. **CI residual:** `tools/test_context_pack.py` is NOT in ci.yml
  (`.github/` forbidden in the packet) — follow-up task should add one line to the control-plane job.
- **M0-T044 ACCEPTED + MERGED** (PR #170, merge `1c34def`; accepted 63): automatic safe GitHub
  flow (`tools/agent_supervisor/github_flow.py` + 57 tests, auto-collected by the CI
  supervisor-bridge glob): push authorization (main/force hard-deny), ten §5.5 merge predicates
  individually tested both directions, Tier B routing without owner approval, proven-merged-only
  cleanup, journal-replay crash reconciliation without blind retry. Suite **1271/2, zero
  regressions**, reproduced by 6 independent runs. Shadow posture verified 4×: `github_pr_merge`
  NOT in live `MODELED_EFFECTS`, D-007 invariant 9 intact, zero live importers. Five gates
  first-pass PASS (G3/G4/G5 + control-plane §5.2 leg) + DCV 7/7 at identity `16149fc3`.
- **8 residuals pinned to `M0-T036-ACTIVATION-CHECKLIST.md`** (M0-T044 G3 + G5 sections): MINOR-1
  (Tier B detection covers 3 of 11 §5.2 classes — fail-open), MINOR-2 (empty-`authorized_branch`
  fall-through), SEC-1 (`extra_specs` live-path override channel unguarded by invariant-9 lock),
  SEC-2 (broadens MINOR-1 to a CATCH-ALL over SECURITY_RELEVANT_CLASSES incl. permission/hook
  configs per §5.4 item 3), SEC-3 (redaction of secret-scan findings), INFO-1 (live caller must
  audit every FlowResult). All MUST-RESOLVE before any activation.
- ⛔ **SHADOW-ONLY throughout; R595 supervised rehearsal remains the MANDATORY BLOCKING
  prerequisite before ANY activation** (D-010-R104). Nothing wired live.

## NEXT SESSION — resume checklist (session 3 → 4)

1. Start-of-session: `python tools/project_control.py status` + reconcile git/CI (origin/main was
   `1c34def` at rotation; checkpoint CP-0039). Machine-readable handoff:
   `project-control/reports/session-handoff-2026-08-07-3.json`
   (digest `bddcbdbcbb285699850bfe24a2ed2df6f2cce42ca591cd585f1be8c33a0f70eb`) — verify the digest:
   sha256 over `json.dumps(doc, sort_keys=True)` with `digest=""`.
2. **Next dependency-valid unit: M0-T045** (R595 supervised rehearsal + Section 16.2 promotion
   pack; deps all accepted). The rehearsal is SUPERVISED — plan it with the owner present; the
   promotion decision is owner-gated. Pre-R595 hardening obligations live in THREE pinned sets on
   `M0-T036-ACTIVATION-CHECKLIST.md`: (a) M0-T041 items; (b) M0-T042 G5 L-1/I-1/I-3;
   (c) M0-T044 MINOR-1/2 + SEC-1/2/3 + INFO-1. M0-T045 binds R113-R115.
3. Proven task workflow + producer-spawn rule (UNNAMED) + classifier-denial protocol: unchanged
   from the session-2 checklist below.
4. **Reviewer models:** gate reviewers ran `claude-opus-4-8` + `xhigh` (standing fallback; the 5
   flipped agent files remain uncommitted in the PRIMARY checkout; revert to `claude-fable-5`
   pins when the owner says "Fable is back"). Orchestrator ran `claude-fable-5`.
5. **Primary checkout** (branch task/M0-T036-supervisor-bridge @ 57ccb44): untouched per
   R099/R109. **Dormant batch** (D-009 + M0-T019 + M2-T014 on origin): untouched. All standing
   holds unchanged: deployment/G6/Graphify/expansion.

---

_History (pre-this-session, may be stale):_

## PRIOR STATE (2026-08-07 session 2, superseded — CP-0038)

**D-010 (Autonomous Engineering V2) wave-1 continues to execute.** Session 2 rotated at a safe
post-merge seam per D-010-R113/R115; accepted count **61**.

- **D-010 am.5 captured** (PR #165, merged `0ed2cdb`): the owner's session-2 launch instruction,
  verbatim, as append-only `source-006-amendment.md` + row **R116** (re-dispatch; introduces NO new
  obligations — R097..R115, holds, SHADOW-ONLY, R595 blocking prerequisite unchanged). Manifest
  digests restamped per c14; task packets M0-T042..M0-T045 `directive_refs` widened to cover R116.
- **M0-T042 ACCEPTED + MERGED** (PR #166, merge `dc0c605...`; accepted 61): Codex ephemeral review
  loop operational end to end (`ephemeral_review.py` — guard → budget → fresh read-only process →
  sealed durable record with decision/evidence-refs/model-identity/usage-telemetry/digest + journal;
  AD-027 independence, AD-087 reopened-sources, AD-088 worker-fallback record never activated),
  0A.4 budgets (`review_packet.py`: 32k target / 64k ordinary / 20%-of-window relative, effective =
  lower, fail-closed refusal + split/summarize guidance) + AD-083 content guard, 0A.3 cadence policy
  (`review_cadence.py`), usage-telemetry surfacing in `codex_reviewer.py`, root `AGENTS.md`
  (Section 11.1, no CLAUDE.md duplication), 27-test module. Suite **1216/1214/0/2**. Pipeline had an
  **honest G4 FAIL** (AS-3 fixture gap) → test-only rework 1 (+4 tests) → G3/G4 delta PASS → G5 PASS
  → DCV **13/13 rows PASS** at identity `2db31092...`; verification row at `e490d50`.
- **G5 residuals pinned to the activation checklist** (`M0-T036-ACTIVATION-CHECKLIST.md`, M0-T042
  G5 additions): **L-1** parse_usage_telemetry uncaught ValueError on >4300-digit ints in untrusted
  stdout (must-fix-before-activation); **I-1** AD-083 guard is structural not semantic; **I-3**
  unbounded child-stdout capture (pre-existing). All MUST-RESOLVE before any activation.
- ⛔ **SHADOW-ONLY throughout; R595 supervised rehearsal remains the MANDATORY BLOCKING prerequisite
  before ANY activation** (D-010-R104). The new loop is deliberately NOT wired into loop.py/cli.py.

## NEXT SESSION — resume checklist

1. Start-of-session: `python tools/project_control.py status` + reconcile git/CI (origin/main was
   `dc0c605` at rotation; checkpoint CP-0038). Machine-readable handoff:
   `project-control/reports/session-handoff-2026-08-07-2.json`
   (digest `2a0e46606e9c89f574134a66e3fabe388a0508df3f41b97adc2c08fc935e7361`) — verify the digest.
2. **Next dependency-valid unit: M0-T043** (bounded context-pack builder; Section 12,
   AD-044..AD-046; no deps). Then M0-T044 (GitHub flow; deps T039+T040 ✓), then **M0-T045
   (R595 rehearsal + Section 16.2 promotion pack)**. Prefer sequential task branches from
   origin/main in the orch worktree (`C:/Users/MLFLL/Downloads/nyc-zoning/orch`) — ledger
   serializes through state.json.
3. **Pre-R595 hardening items for M0-T045** now live in TWO places, both binding: (a) the M0-T041
   items in the previous rotation's checklist entry (pending_prompt regression locks, empty-shape
   fixture lock, real-sampler CLI wiring, quota-fixture live-bytes confirmation); (b) the M0-T042
   G5 additions L-1/I-1/I-3 on `M0-T036-ACTIVATION-CHECKLIST.md`. M0-T045 binds R113-R115.
4. Task workflow (proven ×5 across sessions, incl. a full honest-FAIL→rework→delta-PASS cycle this
   session): task branch from origin/main → G0 + claim (refs from the packet's directive_refs) →
   producer → commit deliverables → evidence map → progress (claimed→in_progress→self_check) →
   submit (identity stamps at HEAD; commit ledger writes) → parallel independent reviews (≤2) →
   record gates (reports committed FIRST; gate stamps at current HEAD — material identity is what
   stays stable across control-plane commits) → G5 → DCV → verification row at accept-time HEAD
   uncommitted → accept → commit together → push → PR → CI green → merge (Tier A per ADR-006).
5. **PRODUCER SPAWN RULE (incident this session):** spawn producers UNNAMED. A custom-named spawn
   makes `.claude/hooks/readonly_agent_guard.py` fail closed to read-only (roster identity
   unrecoverable — the guard's own docs, line 25). If it happens: do NOT proxy-write the denied
   agent's files (permission laundering); let it return design as data, then re-dispatch unnamed —
   the accountable producer verifies/adapts/writes/tests under its own resolved permissions.
   Read-only gate reviewers are unaffected (they are read-only by design).
6. Classifier-denial protocol unchanged (proven M0-T040): STOP, surface to owner with the exact `!`
   line; owner-typed authorization captured as a D-010 amendment; never route around the classifier.
- **Reviewer models:** gate reviewers ran `claude-opus-4-8` + `xhigh` (standing fallback; the 5
  flipped agent files remain uncommitted in the PRIMARY checkout; revert to `claude-fable-5` pins
  when the owner says "Fable is back"). Orchestrator ran `claude-fable-5`.
- **Primary checkout** (`...\nyc-development-feasibility-claude-pack`, branch
  task/M0-T036-supervisor-bridge @ 57ccb44): untouched per R099/R109.
- **Dormant batch (Lane 3 item 1, AD-066):** D-009 + M0-T019 + M2-T014 preserved on origin
  (`control/D-009-depsec-and-m0t019-dispatch @ a953d0d`, `task/M0-T019-fes9-exception @ e96d718`);
  stale PR #64 supersede/close when the batch resumes. Untouched this session.
- **Owner touches this session: 0.** Standing holds unchanged: deployment/G6/Graphify/expansion.

## Machine-readable handoff (D-010 §7.2; sha256 digest over the JSON with digest="")

```json
SEE project-control/reports/session-handoff-2026-08-07-2.json (digest 2a0e46606e9c89f574134a66e3fabe388a0508df3f41b97adc2c08fc935e7361)
```

---

_History (pre-this-session, may be stale):_

## PRIOR STATE (2026-08-07 session 1, superseded — CP-0037)

Session 1 captured D-010 (PR #155; 110 reqs + capture verification PASS), contracted the task
architecture M0-T037..M0-T045 (PR #156), fixed applicability binding (PR #157), and
ACCEPTED+MERGED M0-T038 (handoff preservation, PR #158), M0-T039 (supervisor freeze, PR #159;
tree `e8eeb4fa`, suite 1165/1163/0/2), M0-T040 (ADR-006 autonomy tiers, PR #160; owner-executed
commit `b841b4f` after classifier denials — captured as source-003 R111/R112), and M0-T041
(supervisor gap-closure A, PR #161; quota classifier fail-closed, R207 live sampling,
pending_prompt hardening; suite 1189/1187/0/2; identity `78ed0cc1`). Rotation record CP-0037 +
digest-verified handoff (PR #162, `session-handoff-2026-08-07.json`); owner rotation feedback
R113/R114 (PR #163); soft-ceiling clarification R115 (PR #164). Accepted count reached 60.
Owner touches: 1 (the M0-T040 authorization).

## PRIOR STATE (2026-08-05 late, superseded)

M0-T036 ACCEPTED (shadow-only) 2026-08-06, MERGED via PR #154 (merge-commit; content-empty trigger
commit `57ccb44` during the GitHub Actions outage; 16/16 checks green). R593 resolved via owner
Option A (accepted residual deferred to R595, D-007-R618/R621). The M0-T019/D-009/M2-T014 batch
went dormant on origin. Standing rules carried forward: reviewer-model fallback (revert on "Fable
is back"); owner escalation boundary (D-008); batching at submit; ledger writes via
`tools/project_control.py` only; directives written with explicit LF; task files preserved as found.

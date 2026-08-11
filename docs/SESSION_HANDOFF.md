# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA here as still-current.** This
file is orientation only. Rules/gates/workflow routes live in `CLAUDE.md`. Old blocks (1–15) via
`git log -p docs/SESSION_HANDOFF.md`. Keep CURRENT-ONLY: the `context-budget` CI check fails > ~4000 tok.

## SESSION 16 — D-010-R283 acceptance chain landed; P1/P2/P3/P6 are the remaining work

Refreshed **2026-08-11 (session 16; `claude-opus-4-8`)**. **Accepted = 78.** Owner directive captured as
**D-011 amendment-003** (`directives/D-011-bounded-truth-reconciliation/source-003-amendment.md`). The
integration branch is **PR #220 `control/session15-acceptance`**, worktree `.claude/worktrees/session15-acc`,
HEAD ≈ `3a6b2c5` (verify live). Do control-plane accept work HERE. The ledger wins.

### PATH TO CODEX (ordered runway — what's left)
1. **P1 M0-T058** gate wave → accept (build first; P2/P3 branch off its claude_runner.py).
2. **P2 M0-T059** + **P3 M0-T060** gate waves (after P1) → accept. **P6 M0-T061** may run in parallel.
3. Follow-ups: drain M0-T056 grandfather entry; add the M0-T057 O1 justification test; run **M0-T047/#219**
   (nanoid) gate wave → accept → merge #219 to main.
4. **Merge PR #220 → main** (Tier A, after required checks green) so the accepted ledger + guard land on main.
5. **M0-T056** (R595 production actuation) — **OWNER-GATED**: held by D-011 R001; the owner must explicitly
   lift the M0-T056 hold before it can be built/accepted.
6. **Owner flips R595** + adds the accept allowlist (Tier D, owner-only) → Codex runs live.
Steps 1–4 are autonomous under standard gates; steps 5–6 need explicit owner authorization.

### Done this session (fixed order D-010-R283) — all on #220, pushed
1. **M2-T016 ACCEPTED** (76) at repaired identity `ac3d45cb`. Fresh independent DCV 77/77 D-010 PASS
   (`reports/M2-T016-DCV-final-ac3d45cb.json`); gates G0/G2/G3/G4/G5; new independent **frontend G5 delta**
   PASS (`reports/M2-T016-frontend-G5-delta-security-review.md`) closed the outstanding G5-delta gap; G4 =
   all required CI green at `e3c2ce6`. **B-001 precision fix**: it named the survey-review UI task in its
   prose, which the accept-guard word-matched as a false block; the authoritative `affects` names M2-T019
   (the production ReviewStore), not the UI task — described generically; no hold weakened.
2. **M0-T053 ACCEPTED** (77) at identity `e6746f68`. DCV 4/4 D-010 PASS; gates G0/G2/G3/G5. Its G5's three
   items are pinned **P1/P2/P3** (pre-M0-T056, non-blocking for M0-T053).
3. **M0-T057 ACCEPTED** (78) at identity `6525ddfb` — the empty-identity fail-closed guard (D-011 item 6).
   Cherry-picked from `task/M0-T057-empty-identity-guard`, **M0-T055 drained** from the c17 grandfather
   allowlist (now accepted at real identity `f3a6a363`), 3 dead locals removed. BOTH reviews PASS (G3
   code-review + control-plane-verifier). D-001 empty-set verification row (0 applicable, M2-T014 precedent).

### NEXT — Step 4: supervisor safety fixes P1/P2/P3/P6 — CONTRACTED as M0-T058..T061 (each its own gate wave)
The real remaining engineering before M0-T056/R595. All in `tools/agent_supervisor/`, under the
supervisor-freeze lane (defect-only, cited evidence, gates **G0/G2/G3/G5**, must re-establish the M0-T039
**≥1165-test baseline, 0 failures**). All four are tracked backlog tasks (directive_refs D-010:ALL, qualifying
evidence + acceptance scenarios in each packet); **no producers dispatched yet** — run each gate wave
coherently (contract→claim→producer in an isolated worktree→G3+G5→DCV→accept). Pinned in
`reports/M0-T036-ACTIVATION-CHECKLIST.md`:
- **M0-T058 (P1)** `claude_runner.py:1283-1298` — capture `terminate_all()`'s bool, bounded `process.wait()`,
  raise a DISTINCT code if the child is still alive (unverified termination assertion → live orphan → next
  `start` double-launches; D-010-R347).
- **M0-T059 (P2)** `recovery.py:190-191` — `clear_child_record` remove by `(pid, start_token)`, not whole-key.
  **depends_on M0-T058** (both edit claude_runner.py — build P1 first, never parallel).
- **M0-T060 (P3)** achieved per-cycle containment `!= "job_object"` must **STOP**, not merely record.
  **depends_on M0-T058**; producer confirms exact file (loop.py/claude_runner.py) at G0.
- **M0-T061 (P6)** reviewer-silence → bounded timeout → ONE retry → hard fail-closed **STOP** with recorded
  reason; additive to (not a duplicate of) `accept`. Disjoint module (review_cadence/ephemeral_review/
  codex_reviewer) → **may parallelize** once its file set is confirmed disjoint at G0.

### Non-blocking follow-ups recorded (do NOT reopen accepted work)
- Drain **M0-T056** from `_EMPTY_IDENTITY_GRANDFATHERED` (it gained real paths → now resolves non-empty; the
  entry is inert; control-plane-verifier flagged it). Do at the next control-plane touch (moving it now would
  disturb M0-T057's accepted identity).
- Add a unit assertion for empty/whitespace/non-string `path_free_justification` (M0-T057 O1; code already
  fails closed).
- **PR #219 / M0-T047** (nanoid 3.3.17): the override + CI-regenerated lock exist on `task/M0-T047-nanoid-lock`
  and #219 is mergeable, but **M0-T047 is still backlog with ZERO gates** — it is NOT a bare merge. Run its full
  gate wave (claim → G0/G2/G3/G5 → D-009 DCV → accept, like M0-T057 was landed) THEN merge; merging un-gated
  code is not permitted even under the owner's "when convenient". #220's own `web-dependency-security` stays red
  on nanoid until the fix reaches this branch (known non-required; D-011 item 1).

### Holds (unchanged) + Codex
**M0-T056 NOT started, R595 NOT activated, accept allowlist NOT added** (D-011 R001-R003/R029). "Open Codex
fully" is the destination after P1-P3/P6 land + owner flips the switch — NOT authorization to actuate.
Codex model-fallback = RESOLVED (tries main model first each session, non-sticky). deployment/G6/Graphify/
expansion holds; `default_mode=shadow`; LIMITED-AUTO off; supervisor is Windows-Job-Object-only today (P8).

### Carried rules
Accept-mechanics recipe (proven again this session): work in the #220 worktree, keep accept evidence
uncommitted until after accept (`reviewed_sha`==HEAD), material identity stable across control-plane commits;
fresh independent DCV per task bound to the real identity (never transcribe a stale/narrative DCV); gates
stamped at HEAD. Producers spawned UNNAMED. `project-control/**`+`directives/**` explicit LF; stage exact
paths. Reviewer/orchestrator model `claude-opus-4-8` xhigh. Prose `allowed_paths` = empty-set identity (now
guarded by M0-T057).

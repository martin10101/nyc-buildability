# SESSION HANDOFF — seq 120 (2026-09-19, session seq 119 close; PLANNED finished-seam handoff, D-070)

Orientation only — the ledger (`python tools/project_control.py status`) wins on any conflict.

## D-070 preamble (permanent)

A PLANNED handoff requires the seam DONE FIRST (sweep, next packet contracted+claimed+pushed,
worktree, launcher pointed, fresh run-id) so the successor only verifies+launches;
crash/forced turnover is the only fallback. THIS handoff is the planned kind, with one
deliberate difference: the D-075 10-hour window ELAPSED at this close, so NO next packet is
pre-contracted — the successor contracts the next lanes fresh at its first seam (see NEXT
LANES below). Both loops are DOWN at clean seams by design; nothing is live.

## State at handoff

- **236 tasks accepted.** This session segment accepted SIX: M5-T049 (matcher extraction,
  231st), M5-T048 (proposal contract B0, 232nd), M5-T050 (confirm-arc polish, 233rd),
  M5-T052 (condo records view — DB-031 closed, 234th), M5-T053 (proposal validation route +
  DB-034(a)/(b) gate, 235th), M5-T051 (phase B1 derivation — DB-034(c)/(e) closed, 236th).
  Every acceptance: full independent wave + DCV, zero blocking; two G3
  PASS-with-required-corrections cycles (T052 report wording) closed with delta-attestations.
- Branch `candidate/D-024-mrl-option-b` pushed at the closing seam commit (236th acceptance);
  CI green at every material head this segment (runs 35435873943, 35439235554, 35440808156,
  35451055372, 35454834946, 35455214032).
- Repo root C:\Users\MLFLL\Downloads\nyc-zoning\ctl24; loops' controllers
  C:\SupervisorController{,2}; controller source wt-controller-src.
- Worktrees wt-m5t048/49/50/51/52/53 are all HARVESTED (material cherry-picked); safe to
  `git worktree remove` when convenient — verify `git -C <wt> status` clean first.

## OWNER-ONLY pending

- **The release execution** — one ~10-minute pass;
  `project-control/reports/release-request-2026-09-18-seq118.md` §8-§9 (acceptances 228-236
  all ride the same single pass; flags posture unchanged; deploy the then-current head).
- DB-030(a) owner question and the WATCH rows (DB-003/008/011) — unchanged.

## NEXT LANES (contract fresh at the successor's first seam; per docs/PROPOSAL_EDITOR_PHASED_PLAN.md)

1. **B2 — rule-engine wiring** (producer rules-engineer per the plan row): the existing
   rule families evaluated against proposal-derived facts. B1 (derivation) is ACCEPTED, so
   B2 is contractable. BIND the recorded wiring preconditions on whichever packet first
   wires `derive_proposal` to a route/caller: LotContext list-size ceiling + coordinate
   finiteness guards + the area_sq_ft repr instance (T051-wave G5; recorded at the T053
   backlog sweep), plus DB-034(d) version-emission at B2/B3.
2. **B3 — editor UI increment 1** (frontend-engineer; the validation route from T053 is its
   backend seam; DB-034(a)/(b) already closed there).
3. **Rider clusters** DB-035 (confirm-arc residuals incl. the pixel-CLS e2e spec) and
   DB-036 (condo-surface riders incl. the slash-district sanitizer PRECONDITION on any
   zoning-propagation packet) — small packets or fold-ins.
4. DB-026 second lane stays deliberately deferred (do-not-rush ruling).

## Loop relaunch drill (unchanged, plus this segment's lessons)

- Launchers: C:\SupervisorController{,2}\autostart-launch.ps1 — edit the ACTIVE-TASK block
  (TaskPacket/Repo/Branch/RunId), fresh run-id every launch. Worktree AT/past the claim-seam
  commit. Deny ALL parked asks in BOTH stores between runs (pending-approvals CLI per
  checkout); never audit-append against a live run.
- **Model-downgrade rotation collisions** (4x on loop-2 this segment): provider downgrades
  the opus-4-8 worker mid-run → controller wants rotation → any outstanding parked ask makes
  the seam non-quiet → S4.5 unsafe_seam stop. Work SURVIVES. Drill: deny parked asks, then
  resolve the journal-side `turnover_refused/...` open ask via the library
  (`cli.DurableJournal(cli.runtime_dir_for(checkout)/cli.DB_FILENAME).open();
  journal.resolve_ask(ask_id, answer)` — ask_id from `status --json` open_asks; NO CLI verb
  reaches it), clear-recovery, relaunch. Scratchpad scripts existed as
  deny_all_2.py/resolve_ask_loop2.py (session-scoped; rewrite if needed).
- **Crash class** (loop-2 run 16): supervisor dies with NO policy stop event → boot refuses
  `unit_dispatch_unreconciled` → after read-only evidence (pending effects 0, children 0),
  call `recovery.reconcile_dispatch_intent(journal)` (the gate-3 drill), then relaunch.
- **S14 missing-checkpoint after completed edits** (loop-1 3x): worker context exhaustion at
  ~230-245k live tokens; the build survives in the worktree — ASSESS FOR HARVEST before any
  relaunch (suites in-worktree; if complete and remaining demands are orchestrator-side,
  harvest).
- Breaker at 6 (D-074): trips 19-20 this segment, both after substantive work — the raise
  works; the pattern persists.

## Segment lessons already in Tier-1/Tier-2 (verify before relying)

- Journal-side queued_asks (turnover_refused class) block the `pending_requests` boot probe
  even when `pending-approvals` lists 0 — resolve via journal.resolve_ask between runs
  (docs/WORKING_KNOWLEDGE.md ask-mechanics section).
- The `semantically_invalid/` third fixture class: the contracts CI job requires everything
  under `invalid/` to fail SCHEMA validation; geometry invariants JSON Schema cannot express
  live in `fixtures/semantically_invalid/<schema>/` (walked by api tests, not the CI schema
  job). Precedent: M5-T048.
- The sanitizer-boundary class (three hits this segment): boundedToken's [A-Za-z0-9._-]
  corrupts ISO timestamps (fixed: boundedTimestamp) and WILL corrupt slash-districts
  (M1-5/R7-2) if recorded_zoning is ever wired through it (DB-036(a) precondition).
  Identifiers, timestamps, and district codes are different vocabularies.
- v2 row `reviewed_manifest_sha256` = the TASK's allowed_paths git identity FROM THE GATE
  RECORDS (content_manifest_sha256), never a directive-registry digest.
- Producer full-suite counts can be stale-worktree-base (T051's "439 api" vs true 497):
  verify the task's OWN suite + attribute deltas via byte-stability + ancestry before
  treating a count mismatch as a failure.

## Resume procedure (for the OWNER after the account switch)

The conversation lives on this computer, not on the account: log out, log in with the other
account, then from the SAME folder run `claude --resume` and pick this conversation
(`claude --continue` if most recent). If not on Fable: `/model` → Fable, or
`claude --model claude-fable-5 --resume`. If resume is unavailable, a FRESH session recovers
from this file + the ledger: run the start-of-session routine, verify 236 accepted, and
contract the NEXT LANES above at a fresh seam.

# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff — seq 115 (rev 2): THREE TASKS ACCEPTED (217 total), loop parked at a clean seam

Turnover reason (owner, VERBATIM): "at a seam do seasen handoff"; rev 2 adds the owner's
product-direction ruling and DB-016 (owner asked for the rewrite explicitly).

Generated 2026-09-17 ~21:5x UTC by session_01SewZxbFqxV3yYhcDb7bMJt (the seq-114 successor;
same conversation continued across one machine-sleep restart). Root
`C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch `candidate/D-024-mrl-option-b`,
HEAD `6173a740`-era (pushed; CI green at every material head this session). Origin
`https://github.com/martin10101/nyc-buildability.git`. PR #241 OPEN — NEVER merge.
Dirty at landing: ONLY conventional `.claude/agent-memory/**` + `scratchpad/` (leave them).
**217 accepted** (never present as an MVP percentage — D-059-R006).

## COMPLETED THIS SESSION (durable evidence in ledger/gates/reports)

1. **M5-T032 ACCEPTED (215th)** — address-search reliability + ZoLa-first links. Deployed
   LIVE by the owner (frontend); full live journey verified. Advisory follow-ups → backlog.
2. **M5-T033 ACCEPTED (216th)** — spatial-failure root cause. BOTH runtime causes then
   CONFIRMED + FIXED live with the owner: `LIVE_SPATIAL_PROVIDER_ENABLED` was absent
   (added), then `PYTHON_VERSION` unpinned (Render drifted to 3.14 → source-built shapely →
   geometry-pin guard refused; owner set 3.12.11). **The live spatial path now runs
   end-to-end in production for the first time.** Residual outcomes verified CORRECT against
   city records: 350 Fifth Ave genuinely split-zoned (C5-3+C6-4.5+MiD) →
   `geometry_uncertain` right; 3022647515 = condo billing BBL absent from ZTLDB by design.
   Record: `project-control/reports/M5-T033-owner-confirmation.md`.
3. **M5-T034 ACCEPTED (217th)** — B7 wide-street FAR wiring (own module, first production
   consumer of the wide-street stack) + B4 input bounds. Five reviews PASS; two evidence
   corrections via rework→resubmit→delta-attestation; DCV restamp carried to `6d5e1c42`.
   The rule.json deviation (evaluator-seam consumption; DSL has no determination primitive)
   ruled SOUND by G3+G1+DCV.
4. **Directives captured:** D-067 (keep-going-through-compaction INTERACTIVE-SESSION-ONLY
   per amendment — loop-side ~400k rotation stands; 10k eager budget applied), D-068
   (CODING_RULES.md, auto-injected, append at discovery), **D-069 (docs/DISCOVERY_BACKLOG.md
   — NOT injected; record product discoveries at discovery, sweep OPEN/WATCH at EVERY
   contract seam/replan; entries end QUEUED/RESOLVED/WATCH, never deleted)**. Backlog
   DB-001..DB-016. How each audience learns of it: successors via the PROGRAM_KNOWLEDGE
   pointer (auto-injected) + directive registry + this handoff; Codex ONLY via packet text
   (loop-packet contract item 6, added this session); the code graph doesn't and needn't.
5. **Owner product-direction ruling (2026-09-17, in-chat):** the differentiator is the
   COMPUTED ANSWER with receipts — ZoLa shows labels, never answers; keep building the
   engine. AND the owner is right that the surface looks thinner than ZoLa on context we
   already fetch → **DB-016 context-panel parity** (show special districts/overlays/landmark
   status we already retrieve, with provenance + ZoLa link). Sequencing suggestion the owner
   heard without objection: DB-015 live provider wiring FIRST, DB-016 context panel right
   after (the panel convinces most next to a real computed answer).
6. Owner artifact delivered: "From Empty Lot to Keys" (architect process + R1-R12 explainer),
   https://claude.ai/code/artifact/8bc264c4-143a-4d05-a258-7cb6c6f2e574

## THE LOOP (DOWN deliberately — clean seam; relaunch on the NEXT packet)

Run 39 ended via the `consecutive_revision_loops` breaker (4 cycles) with the build COMPLETE;
the task was accepted at this seam. No supervisor running; no asks pending; audit chain
repaired post-run-39 (fresh at genesis). Launcher
`C:\SupervisorController\autostart-launch.ps1` still points at M5-T034/run-39 — update the
ACTIVE-TASK block to the next packet + fresh run-id (40+) before launching. **Read
`docs/WORKING_KNOWLEDGE.md` FIRST**: loop-packet contract (now 6 items — item 6 = discovery
routing), watcher-v2 pattern (asks serialize as `DEFER_TO_OWNER`; poll `queued_asks`;
tasklist pid check — MSYS ps lies), ask-answer fork-race caution, machine-sleep recovery
drill, from-root pytest artifact. Breaker budget (4) is owner config (DB-012 WATCH).

## SUCCESSOR DUTIES

1. **Contract the next packet with the D-069 backlog sweep at the seam** (binding,
   D-069-R003) + D-066-R001 navigation block (regenerate graph) + REVIEWER HONESTY BAR +
   the new discovery-routing packet line. Next lane per the owner's product ruling:
   **DB-015 live wide-street/spatial provider wiring**, then **DB-016 context-panel parity**;
   D-065 affordable scenarios after those. Bind refs via `reg.evaluate_task_refs`
   (applicable == cited).
2. **Relaunch the loop** on that packet (worktree off the contract head; update launcher;
   `revoke-all` first; fresh run-id) and **re-arm the watcher-v2 Monitor immediately**
   (Monitors die with the session).
3. Answer asks fast (approve-once in-scope git add/commit = designed path; deny stale
   chained variants; verify answers landed in `queued_asks` if the audit CLI races).
4. At the worker seam: capture+attribute the tree, push, CI = authority, review wave
   (5 reviewers, pin HEAD, deviations up front), gates, v2 verification rows, accept —
   proven 3x this session; mirror the M5-T034 reports.
5. Owner comms: SIMPLE ENGLISH ONLY, no paths/IDs/jargon (D-064 p19; owner escalated —
   see private memory owner-communication-style).

## STANDING (unchanged unless noted)

D-067: THIS interactive session lineage keeps going through auto-compaction (~1M); the
loop-side ~400k rotation rule stands (amendment 002). D-064 models: loop worker + subagents
opus-4-8 xhigh; main fable-5. Eager budget 10000 (D-067-R003). Open blockers: B-001
(Supabase), B-010, B-011. Holds: PR #241, expansion §2, Tier D/Section 20. G6 legal stays
owner. Deployed: frontend = M5-T032 build (owner-deployed today); backend live on `nycdf-api`
with BOTH spatial env fixes. ZTLDB source staleness = DB-003 WATCH.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `tasks/M5-T03{2,3,4}.json` (accepted) ·
`docs/DISCOVERY_BACKLOG.md` (sweep duty; DB-015/016 = next lanes) ·
`docs/WORKING_KNOWLEDGE.md` · `.claude/rules/PROGRAM_KNOWLEDGE.md` + `CODING_RULES.md` ·
`project-control/directives/{D-067,D-068,D-069}-*/` ·
`C:\SupervisorController\autostart-launch.ps1` (outside repo).

## NEXT ACTION (exact)

Backlog sweep → contract DB-015 (live provider wiring) as the next packet → relaunch loop
run 40 → re-arm watcher-v2 → quiet monitor. Stop for: Tier D items, credential asks (B-001),
a breaker trip that repeats after the honesty-bar packet fix, or account exhaustion (blocker
+ one-line owner action, never retry past a classifier block).

## COPY INTO THE NEW SESSION

Resume as monitor-only orchestrator for the NYC Buildability loop. Work from repository
evidence, not assumptions about the old chat. First: verify repo root
C:\Users\MLFLL\Downloads\nyc-zoning\ctl24, branch candidate/D-024-mrl-option-b, and pull;
read CLAUDE.md and docs/SESSION_HANDOFF.md (seq 115 rev 2) and the authoritative files it
lists; run python tools/project_control.py status and reconcile (ledger and git win over
prose). The loop is DOWN at a clean seam (217 accepted; no supervisor running, no pending
asks). Before touching any packet read docs/WORKING_KNOWLEDGE.md completely. Then: perform
the D-069 backlog sweep, contract the next packet (DB-015 live provider wiring per the
owner's product ruling; include the D-066 navigation block, reviewer honesty bar, and the
discovery-routing line), relaunch the loop with a fresh run-id via
C:\SupervisorController\autostart-launch.ps1 (update its ACTIVE-TASK block; revoke-all
first), and immediately re-arm the watcher-v2 Monitor from the Tier 2 notes. Owner replies:
simple English only, no technical identifiers. Report READY TO RESUME or BLOCKED, then
continue from the handoff's exact next action without repeating work.

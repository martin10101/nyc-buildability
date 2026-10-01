# SESSION HANDOFF — seq 133 (2026-10-01 ~17:20 UTC; owner-invoked /session-handoff; reason: "ok I will get more so 5 loops can run meantime our chat got big gonna restart i wanna run now 2 loops"; Claude Code session 01PXWfnLcrZ5cqzDfHbwVTeT, claude-opus-5-5; directive D-090)

Orientation only. The ledger (`python tools/project_control.py status`) and `project-control/` WIN
over this prose. Seq 132 is in git at `31e938ad` (#270). The PC-only items are UNCHANGED and still
open: C: disk cleanup, owner-typed D-088 commissioning, the M5-T110 canary, and B-026.

## Identity (live at generation)
- **Machine:** a DigitalOcean droplet ("DO-Regular"), Linux, **1 CPU / 2 GB RAM**, 48 GB disk with 31 GB free. Not the owner's PC.
- **Repos:** main checkout `/root/project/nyc-buildability`. The handoff is written in worktree `/root/project/w-handoff2`, branch `task/session-handoff-2026-10-01-cloud`. Integration branch `candidate/D-024-mrl-option-b` @ `5aa9e735`.
- **No open work:** no dirty or unpushed worktree, no running agent, no pending merge job.
- **Gate 0 deviation:** this session ran from `/root/project`, outside the repo, with claude.ai connectors attached. Because of that, the repo hooks and `.claude/agents` were not loaded, and the producers and reviewers were generic subagents that inherited Opus 5.5 instead of the D-064/D-085 opus-4-8 pin. Record this with the directives.

## Owner decisions (verbatim) in force
- **Option B merges.** The owner said "1 b" and applied it as `autoMode` rules in `~/.claude/settings.json` on this droplet: "Reviewed merge in nyc-buildability" and "Next queue item in nyc-buildability". A robot may merge only when all of these hold:
  - a different agent's review is PASS with 0 blocking, naming the exact head;
  - all CI on that head is green;
  - the merge uses `--match-head-commit`;
  - the PR touches **no Lane A zoning-math path**.
  
  Zoning-math PRs need the owner's yes.
- **Spending:** "no i pay flat". There is no spending limit; robots pause when the plan's limit is reached.
- **Parallelism:** "i wanna run now 2 loops". Run **at most 2 robots at once** until the owner resizes the droplet:
  - minimum 4 CPU / 8 GB for 5 robots;
  - 8 CPU / 16 GB for 6 robots;
  - resize with "CPU and RAM only" (reversible), and stop the robots first.
- **R6B (#262/#269):** the owner said "Yes—I'd approve all three based on the reported switch being off…". The full quote is on #262 and #269. Its conditions:
  - **`LANE_A_ENABLED` stays unset; merging ≠ activation.** It is turned on only on the owner's explicit word.
  - The labels are "Tax-lot-only estimate", and "Not confirmed" for whole-site capacity, remaining capacity, and combined-lot coverage/rear yard.
  - Once the zoning lot is verified, the warning names lots 1 and 70.
- **Codex loop to the new CC:** this can only be done on the PC. The pin is a SHA-256 over the PC's `claude.exe`. Steps: `docs/CONTROLLER_UPDATE_RUNBOOK.md` §13.

## Done since seq 132 (merged; independent PASS 0-blocking at the exact head, verified PR body, CI 40/40)
- #263: E-01 drawing kit.
- #277: the owner's `.claude` files, cherry-picked from `e0c222da` (the codex-loop directive plus a backend-engineer memory note).
- #270: handoff seq 132.
- **#262 A-02a R6B FAR + heights, OWNER-approved.** Its overlay note now names the Article III checks.
- **#269 A-02b R6B coverage, rear-yard waiver and units, OWNER-approved.** Golden `cb6f5c77…` (note text only).
- **#278:** an always-visible tax-lot-only warning plus labels on every cap/FAR surface, including print and legacy Compare.

The evening total is 16 merges. The seq-132 list (#261, #265–#267, #271–#276) still stands.

## Open PRs
| PR | State |
|---|---|
| #268 E-03 DXF (draft) | Not reviewed; needs A-04 |
| #241 | Never merge |
| #64 M0-T019 (against `main`) | Old; untouched |

## Owner decisions pending
1. **Remaining-capacity wording:** A "Not confirmed" or B "Not available — needs existing zoning floor area"? I recommended B. Both currently print in one brief (#278 N1).
2. **When to turn on `LANE_A_ENABLED`:** owner only.
3. **A verified zoning-lot source** to name lots 1 + 70. It may need the architect or a legal opinion.
4. **G6/Q12 licensed review** of the R6B rules, and the reviewer's name and hours.
5. Q4, Q8, #243–#246, the Q1 pilot, and the droplet resize timing.

## Benchmark facts (215-16 Northern, BBL 4073340070)
- **Zoning lot:** tax lots 1 + 70 per DOB A1 421803891. It is about 200 × 100 ft with two corners; Lane B must confirm.
- **Lot 70 frontages:** 103.88 ft on Northern Blvd (wide) and 99.98 ft on 215 Pl (narrow).
- **Existing floor area (B-05):** lot 70 = **Unknown — enter**. The DOB figure 39,934 is set aside, because it may be zoning-lot-wide. The recorded figure is 54,488 (reference only). The existing building records 38 units.
- **R6B draft results, lot 70 only:**
  - FAR 2.00/2.40 → 20,150/24,180 sq ft;
  - heights 30/45/55, or 30/45/65 qualifying (min base / max base / max building);
  - corner coverage 100% and the corner rear-yard waiver;
  - units 29 (35 qualifying). §23-52 divides the ZONING LOT's floor area, so these are not the site cap.
- **Second opinion (an LLM, not licensed; saved at `docs/research/owner-research/2026-10-01-r6b-second-opinion-{questions,answer}.md`):**
  - It agrees with the district rules.
  - C2-2 changes street-wall placement (§35-631(b): at least 70% of the street wall within 8 ft of the street line). Not modeled.
  - In mixed buildings the rear yard starts at the lowest dwelling floor (§35-53). Not modeled.

## Follow-ups (non-blocking, on PRs)
- **#278:** wire the verified zoning lot (a Lane B fact, a Lane C contract field, and the Lane D containers passing `zoningLot`). D-05's ThreeAnswersPanel needs the warning before M1-12.
- **#262:** A-11 street-wall location (§35-631(b)). A Lane C request for the stale `config.py:40` comment. `tools/residential_validation.py` is 622 SLOC; split it if it grows.
- **#269:**
  - N1: an always-shown note that the units dividend is the zoning lot's;
  - N2: cite 35-53;
  - N3: define the 100-ft input (corner portion vs radius) with Lane B;
  - N4: the 23-363 note should say "may increase".
- **Earlier:**
  - #271 N1: passive-effect focus in 4 screens;
  - #273 N1: `ownership_at` fallback;
  - #276 N1/N3: reflection routes and the comment wording;
  - #274 N7: Lane C must supply all block filings;
  - #265: stale `results.py` docstring and the `raw_digest` check;
  - #275 N8/N9: `seen_at` tie-break;
  - #277 N2: reword the memory note.

## Ledger (authoritative) and what is NOT recorded
- No ledger gates, DCV rows or accepts exist for any evening merge. #247–#250 have G0 only.
- Owner words since D-090 source-002 have not been captured with /directive-compliance.
- Lessons are recorded in `PROGRAM_KNOWLEDGE.md` (Tier 1), `docs/WORKING_KNOWLEDGE.md` (the "Cloud Road-1 run" section) and `docs/DISCOVERY_BACKLOG.md` (DB-097–DB-102).

## Standing restrictions
- Tier D / Section 20 stops. PR #241 is never merged. The expansion §2 hold stands. Commissioning is owner-typed. Never pass `model:`.
- Dependency security: no waiver. No local npm/node; CI is the web executor. Producers never write `project-control/`.
- **`LANE_A_ENABLED` stays off. At most 2 robots at once.** A reviewer verifies every PR body before merge.

## EXACT NEXT ACTION (successor)
1. **Gate 0,** then report READY TO RESUME or BLOCKED. Confirm that `claude auto-mode config` lists the two owner rules; if not, the owner merges.
2. **Capture the owner words above** via /directive-compliance, including both deviations.
3. **Two robots:**
   - **B-07 multi-lot site math (Lane B):** it turns the lot-70 numbers into whole-zoning-lot inputs for 1 + 70.
   - **One cheap follow-up:** #269 N1 (zoning math, so it needs the owner's yes) or #273 N1.
   
   Each goes producer → independent review (body included) → green CI → option-B merge.
4. **If the owner hasn't answered A/B,** ask once, in plain words.

## COPY INTO THE NEW SESSION
Resume as the NYC Buildability orchestrator (verify the model with /model). Work only from repository
evidence. Verify: cwd IS the repo worktree root (`git rev-parse --show-toplevel`), branch
candidate/D-024-mrl-option-b, HEAD == origin, /mcp empty (Bootstrap Gate 0). Read CLAUDE.md,
docs/SESSION_HANDOFF.md and `python tools/project_control.py status` (the ledger wins). Check open PRs
with `gh pr list` and `claude auto-mode config`. Report READY TO RESUME or BLOCKED, then continue from
EXACT NEXT ACTION without repeating work. Run at most 2 robots at once; keep LANE_A_ENABLED off;
zoning-math merges need the owner's yes; explain things to the owner in plain, simple words. Stop for
Tier D, PR #241, owner holds and owner-typed commissioning; never pass `model:`.

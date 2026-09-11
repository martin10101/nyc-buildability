# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 97: 177 accepted; M4-T009 landed out-of-loop; Render API live; M2-T021 built+reworked, re-review IN FLIGHT

Generated 2026-09-11 ~16:30 ET by session `cc0c1f1f-17b8-46d0-973d-fb1f681d84d3` (owner ran
`/session-handoff`, no reason stated). Root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, worktree
ctl24, branch `candidate/D-024-mrl-option-b`, HEAD `eb6a15f8` **pushed** (origin same; a ledger
commit for this handoff follows it). Dirty: only untracked `.claude/agent-memory/qa-engineer/*`
(reviewer-agent memory, left per policy) and `scratchpad/` (prior-session working files). Repo
PUBLIC. `main` untouched at `d8b3899f`.

## STATE (verify live; ledger wins)

1. **Accepted = 177.** M5-T004 ACCEPTED this session (`49ac5206`): the independent DCV re-anchored
   its D-038 row to the moved HEAD after accept refused fail-closed on a stale `reviewed_sha` —
   row re-anchors, gates NEVER restamp; memory `verification-row-stale-anchor-reanchor` has the
   pattern. Verifier's report at `project-control/reports/M5-T004-directive-verification.md`.
2. **M4-T009 (R1-R12 FAR rules): producer output LANDED OUT-OF-LOOP**, ledger 85% `in_progress`.
   Branch `task/M4-T009-r1r12-far` @ `197156b9` (wt-m4t009): loop runs 30/31/33 built it; every
   run died on checkpoint TRANSPORT (timeout once; twice the worker abbreviated `starting_sha` —
   controller refuses per S14), never on the work. 359 rules tests green on the repaired base.
   Memory `loop-checkpoint-sha-transport-failure` records the resolution pattern. OWED before its
   gate wave: a small AS-5 unit adding `content_digest_sha256` to each rule's `citations[]` + the
   comparison test (the digest convention question is now answered — see 4). NO further loop runs
   needed; supervisor is DOWN in PAUSED_RECOVERY (run 33), only matters if a new run is wanted
   (then: `revoke-all` stale asks → `clear-recovery` → owner-run launch script).
3. **CI transformed: 15/18 jobs green** (was: api dead at ruff, ~245 hidden failures). Fixed this
   session: secret-scan (canary `secretscan:allow` pragmas), api 27 ruff errors, ZR snapshot
   bundle sync, **C3 snapshot digest divergence** (September captures wrote whole-record digests;
   v1 = sha256(excerpt); conformed with originals preserved in `notes[]`, second shape drift
   `source.section_last_amended` restored), starlette-1.x route-enumeration tests
   (`_flattened_route_list`). REMAINING 3 reds, all decision-pending (MVP_AGENDA): web-e2e (one
   real M5-T004 assertion defect, `compare-screen.test.tsx:404` empty `from`), npm audit (7
   vulns incl. the Next.js RCE — owner authorization), control-plane (directive-registry CRLF
   digests D-032/033/034/038 — normalization decision). **CI on `eb6a15f8` UNCONFIRMED** at
   handoff — check `gh run list` first.
4. **Render PROVISIONED (owner-driven):** `nycdf-api` LIVE staging (starter/oregon, health
   green); `nycdf-web` WITHHELD from render.yaml (`23817a9f`) pending the RCE fix (restoration
   owed in that change); `previews:` removed (Hobby workspace rejects it). URL is PRIVATE (no
   auth; flags unset). Owner to confirm Blueprint Auto Sync = No.
5. **Geoclient END-TO-END; B-004 RESOLVED** (record updated with evidence): key on owner machine
   + Render; fixtures G01 (documented example, 00/00), G02 (EE + suggestion), G03 (42 reject) —
   timestamps corrected to raw-capture-file write times with basis stated (G1 finding 1: the
   originals were hand-estimates; error disclosed in-fixture). **Street-width pilot**
   (`docs/research/street-width-source-pilot-2026-09-11.md`): Geoclient `streetWidth` = PAVED
   width, KILLED for the ZR 75-ft test; **DCM Street Center Line (SODA `g6zj-tzgn`) confirmed**
   as the mapped-width candidate WITH per-segment geometry — B2's "source not chosen" blocker has
   a verified answer.
6. **M2-T021 (Geoclient address connector): built → 4-gate wave → reworked → RE-REVIEW IN
   FLIGHT.** Ledger 80% `rework`. Wave at `d4cdbe79`: G1 FAIL / G3 PASS / G4 FAIL / G5 PASS —
   reports verbatim at `project-control/reports/M2-T021-G{1,3,4,5}.md`; the wave caught the
   ORCHESTRATOR fabricating fixture timestamps and four evidence-map overstatements (the
   M5-T004 pattern again). Rework `eb6a15f8`: every blocking finding, one bounded change; 98
   connector tests (was 36), 437 connectors green, ruff/modularity/secret-scan clean. **Four
   re-review subagents (M2T021-G1/G3/G4/G5) are running**, instructed to write
   `M2-T021-G{1,3,4,5}-rereview.md` into
   `C:/Users/MLFLL/AppData/Local/Temp/claude/C--Users-MLFLL/cc0c1f1f-17b8-46d0-973d-fb1f681d84d3/scratchpad/`
   — healthy+bounded, not stopped; COLLECT FROM THOSE FILES (they survive session end). G3 also
   found: D-038 R003/R004 `applicability.task_ids` are M5-only and the submission computed
   applicable_requirements EMPTY for M2-T021 — reconcile via owner-gated D-038 amendment, not
   argument. Note: `wt-m2t021` lags at `dc227c0a` (rework landed on candidate, M5-precedent).
7. **MVP_AGENDA updated:** §I Render + Geoclient records + the OWNER DIRECTIVE line ("go ahead
   with the address entry connector", verbatim, so citations resolve); C3 resolution; **C4 NEW**:
   wave-wide `$`-anchor sanitizer newline defect in three accepted connectors
   (`mappluto_geometry_arcgis.py:314`, `zoning_features_arcgis.py:266`, `ztldb_soda.py:345`) +
   M2-T021 carry-forwards (GRC 50/75 capture task; consumers must escape reflected text;
   endpoint packet must map to `source_fact`).
8. **Campaign record divergence (disclosed):** `campaign_continuity --status` NEXT still points
   at M0-T136 Tranche B (seq 71, 2026-09-01); the sessions since worked the product queue
   task-by-task. Ledger + git win over the campaign prose; reconcile via `advance()` only.
9. Five legacy `project-control/campaigns/D-032-*.json` records print INVALID (missing fields) —
   pre-existing noise, untouched.

## OWNER ITEMS OUTSTANDING
Auto Sync = No confirm (Render Blueprint); portal rate-limit quotas for the registry record
(B-004 resolution notes them UNCONFIRMED); Next.js RCE upgrade authorization; Supabase token
(B-001); demo mode decision (local recommended); practitioner tricks list; D-038 amendment
activation if the verifier requires one.

## NEXT ACTION (exact, in order)
1. Check CI on `eb6a15f8` (`gh run list --branch candidate/D-024-mrl-option-b`).
2. Collect the four re-review files from the scratchpad path in item 6; preserve verbatim to
   `project-control/reports/M2-T021-G*-rereview.md`; record the four gates.
3. If PASS 4-0: dispatch an INDEPENDENT directive-compliance verifier (never the orchestrator —
   it co-produced) for the D-038 row, then `accept` M2-T021 (→178). If any FAIL: cluster and
   rework as this session did.
4. Then the M4-T009 AS-5 unit + its 5-gate wave (→179 path), then the address-resolution API
   endpoint packet, then the confirm-screen/address-entry UI packet.

## Standing restrictions (unchanged)
NEVER merge PR #241; supervisor frozen (changes need cited D-024-R###); expansion hold; Bootstrap
Gate 0 before any write (cwd = this worktree root, `/mcp` empty/allowlisted); no bare `git stash`;
no new packages outside `docs/DEPENDENCY_SECURITY_POLICY.md`; no hosted web deploy before the RCE
fix; API URL stays private until auth; key never in chat/files/logs.

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Bootstrap Gate 0: primary cwd must BE
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` and `/mcp` empty or allowlisted BEFORE any write.
Verify root/worktree/branch/HEAD/origin live. Read `CLAUDE.md`, `docs/SESSION_HANDOFF.md` (seq
97), `docs/MVP_AGENDA.md`; run `python tools/project_control.py status` and reconcile — **ledger
+ git + CI win over all prose.** 177 accepted. M2-T021 sits in `rework` at 80% with its rework
PUSHED at `eb6a15f8` and a four-reviewer RE-REVIEW in flight whose reports land as files in the
old session's scratchpad (path in handoff item 6) — collect them, record gates, then independent
directive verification, then accept; do not re-review yourself and do not accept without the
independent D-038 row. M4-T009 is landed at 85% awaiting its small AS-5 unit + gate wave — do
NOT relaunch the loop for it. CI on `eb6a15f8` was unconfirmed at handoff — check it first. Do
NOT: merge PR #241, push/merge `main`, deploy `nycdf-web`, touch the supervisor without a cited
D-024-R###, put any secret anywhere. Report `READY TO RESUME` or `BLOCKED`.

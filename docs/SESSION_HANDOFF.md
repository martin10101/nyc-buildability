# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 107: 198 accepted; landed by /session-handoff (owner reason, verbatim: "go ahead like we discussed give me promo btw u dont have to stop the loop while we clear here")

Generated 2026-09-13 ~02:30 ET by the landing orchestrator session
(session_01JjK8w1YXwFBjUS8PRrTfHp). Root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch
`candidate/D-024-mrl-option-b`, HEAD `130e31a0` **pushed** (in sync with origin; the tip commit is
the peer session's Part-0 docs refresh). `main` untouched. PR #241 OPEN — NEVER merge. Dirty at
landing: ONLY the conventional reviewer agent-memory files (human-journey-reviewer +
qa-engineer, reviewer-owned, intentionally uncommitted) + session-local `scratchpad/`. No
sub-agent is live (all completed their bounded assignments); no loop is running.

## WHAT THIS SESSION DELIVERED (194 → 198 accepted, all end-to-end gated + DCV'd)

1. **M5-T024 (195th)** D-043 owner-executed Render internal-deploy checklist
   (`docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md`). G1 caught RC-1 (the address flow needs
   `/property?ruleeval=on` — the whole AddressResolutionScreen tree is behind the env-AND-opt-in
   two-factor gate at PropertyLookup.tsx:265); fixed + delta-attested. OWNER ITEMS OPEN at the
   directive level: execute the dashboard steps; confirm the live URL on your device.
2. **M5-T023 (196th)** lot-outline WEB rendering — **D-040-R001 chain COMPLETE, D-040 queue
   CLOSED** (research → M5-T020 route → M5-T022 maplibre admission → rendering). First
   maplibre-gl import (dynamic, WebGL-gated, constant DCP attribution after the G5 F-1 fold-in);
   two-round e2e-locator convergence VERIFIED_CLOSED; CI 18/18 green at 3ff94619 (vitest 481/481,
   Playwright 83).
3. **M4-T013 (197th)** B2 street-width research (D-045-R003 research-first half): **DCM Street
   Center Line ArcGIS = PRIMARY** (keyless, mapped/legal width, EPSG:2263); SODA g6zj-tzgn =
   documented-stale fallback; **Geoclient per-address streetWidth = PAVED width — KILLED for
   legal use** (30-vs-60 divergence, fixture-proven); free-text `Streetwidth` field ⇒ the
   connector must parse **fail-closed-to-narrow** with the ambiguity policy routed to a legal
   decision (OQ-3). Registry draft `docs/research/source-registry-drafts/dcm-street-centerline.json`.
4. **M4-T014 (198th)** R3/R4 height/setback draft families (D-045 A1 wave 1b): pitched §23-421
   explicit variants (25/35), flat §23-422 R3-2/R4=35 + R4B=25, all A2 provisions typed gaps, 90
   new tests (rules suite 458). Its G3 arc: PASS → **revised to FAIL** on the (g)-extraction
   hazard (snapshot notes asserted content the HTML channel provably couldn't render) → surgical
   provenance correction → PASS. **D-046 wave 1 CLOSED 2-wide** (T013 research + T014 rules,
   pairwise-disjoint).
5. **Directive cascade absorbed live** (all peer-captured, all validated, all applied):
   **D-045** citywide rule-coverage campaign → integrated into M4 (waves A1 → A2+B2 → A3 → C → M
   → A4; one reviewed family at a time; DRAFT-until-G6). **D-046** parallel production (ceiling
   3, disjointness mandatory). **D-047** producers = exact `claude-sonnet-5` (agent files flipped:
   rules-engineer, official-source-researcher; reviewers/orchestrator UNTOUCHED; ramp ceiling 10
   start 3-4; twice-failed-review → opus-4-8 rebuild). **D-048** B-023 disposition (named-only +
   not-assessed + `docs/ARCHITECT_REVIEW_QUESTIONS.md`; standing ambiguity pattern R004).
   **D-049** owner "encode the 11-25 reading" — supersedes D-048 for the five lettered R1/R2
   variants (suffix-inheritance 25/35 with owner-decision provenance; (g) explicit conditional;
   site modifiers never silent; the print/PDF capture-hardening BINDING).
6. **B-023** opened (the §23-421 bare-R1/R2 group-label legal question; producer wrote ZERO files
   rather than guess) and RESOLVED by the D-048/D-049 dispositions; the three interpretation
   questions are ISSUED to the professional in `docs/ARCHITECT_REVIEW_QUESTIONS.md` (G6 agenda).

Validation at landing: registry validator EXIT 0 (NOTE: now takes ~440 s); rules suite 458 passed;
sync_zr_snapshots --check EXIT 0 (10 files); generator --check EXIT 0 incl. lot_geometry;
modularity EXIT 0; CI fully green at 3ff94619 / 6fc8a878 / e49ac4bd (each material head).

## NEXT ACTIONS (in order; scopes disjoint so 1+2 may run parallel per D-046/D-047)

1. **Dispatch the M4-T012 producer** (already re-claimed: rules-engineer @ claude-sonnet-5,
   worktree `wt-m4t012-r2`, definitive D-049 scope citing D-045+D-048+D-049 — 11 rows,
   evaluate_task_refs clean). Producer's BINDING FIRST STEP: prove §23-421 full-text completeness
   from a print/PDF-class artifact (the HTML render provably loses paragraph (g)) with the
   9,500-present check, reconciled against the owner-verified verbatim in the questions doc.
   Packet: `project-control/tasks/M4-T012.json` (read its path_notes completely).
2. **Contract M4-T015: B2 street-width connector build** pinning the accepted M4-T013 research
   (DCM ArcGIS primary; fail-closed-to-narrow width parsing; recorded-official fixtures;
   M5-T020/M2-T009 connector discipline; paths disjoint from all rules dirs).
3. Then: ramp per D-047-R004 (widen past 2 only while review latency + CI stay healthy — the
   remaining A1 families genuinely depend on A2/B2, so the next lanes are the connector, then A2
   mechanics, or C-district research).
4. OWNER return items: D-043 dashboard walkthrough + live-URL confirm (checklist ready);
   Supabase B-001; the G6 professional ask in `docs/ARCHITECT_REVIEW_QUESTIONS.md`; PR #241 stays
   unmerged.

## TIPS/TRICKS THIS SESSION PROVED (owner asked these be recorded; full set in orchestrator memory)

- **PS5.1 + git commit -m: NO double quotes in commit messages.** Embedded `"` mangles native
  args → the commit FAILS as pathspec errors while later commands in the block (incl. `git push`)
  still run — one interim push went out without its fix that way. Quote-free messages, always.
- **Playwright `getByLabel` is case-insensitive SUBSTRING by default**: "Borough" matched "ZIP
  code (alternative to borough)" INSIDE the same form — scoping can't fix that; `{ exact: true }`
  does. Two CI runs were spent learning this; use /deficit-convergence after the FIRST repeat.
- **Hold ALL pushes while a material CI run is in flight** (branch cancel-in-progress kills it —
  your own control-plane pushes AND the peer's). Commit locally; push after conclusion.
- **The restamp+accept dance**: DCV rows fail closed on reviewed_sha ≠ HEAD. Get the verifier's
  CONDITIONAL restamp pre-authorization UP FRONT (empty allowed-paths diff + identity unchanged
  at restamp moment); then restamp (condition-checked) + accept in ONE command block with NOTHING
  slow between — the validator now takes ~440 s and the peer commits in the SAME checkout, so a
  slow step between = a raced HEAD and another round-trip (happened twice).
- **Peer concurrency is normal**: ctl24-8e commits interleave directly into this branch and
  pushes preempt CI. `git fetch` + ancestor-check before pushing; expect `HEAD..origin` empty
  when the peer committed locally.
- **Reviewer re-verdicts are live and correct**: route new hazards to in-flight reviewers with
  specific rulings requested; a PASS may honestly become FAIL (G3 did) — record it, rework,
  delta-attest. Producers must follow SOURCE over orchestrator paraphrase and disclose (M4-T014's
  producer corrected my (g)-trigger grouping — that behavior is required, not optional).
- **Copy producer agent-memory OUT of worktrees before they're cleaned** — and remember a
  worktree's base lags; the reset-to-base + show-toplevel guards stay mandatory in every producer
  prompt. Submit-record staleness: if a rework postdates the submit, do progress→rework → submit
  → accept, all uncommitted at the frozen HEAD.
- **Snapshot honesty rule (generalized from the (g) defect)**: `verbatim_excerpt` is an excerpt —
  notes may NEVER assert section content the capture channel couldn't render unless attributed to
  a NAMED other source; pseudo-verbatim quoting of unseen text is gate-fatal.
- `/session-handoff` is user-invocation-only; `evidence-map` files live outside allowed_paths (no
  identity churn); `M4-T00x.json` CLI submit records need staging (easy to miss); G2 is recorded
  with `--reviewer orchestrator`.

## ADVISORY BACKLOG (no task contracted; triage when convenient)

Validator runtime ~440 s (registry growth — profile/CI may need a budget bump or the validator an
index); interior-ring lot_geometry contract fixture; swiftshader WebGL e2e lane; LotOutlineMap
`interactive:false` question; stale `page.tsx:22` docstring; `.env.example` cites nonexistent
DEPLOYMENT_AND_ROLLBACK §0.1; hyphenated "buildable-envelope" ban-list gap (G3/G5 advisory);
`building_type` modeling axis → G6 attention; render.yaml nycdf-web restoration debt (+
duplicate-service caution) when the Blueprint is next touched.

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. Supervisor frozen/SHADOW-ONLY. Expansion hold except the (now-delivered)
lot-outline increment. §G dependency machinery for any admission. Internal-only deploy scope
(D-043); API URL private. Thin client (no local npm; CI is the JS authority). G6 owner-only;
DRAFT-until-G6 everywhere (D-045-R009/D-049-R005). Stop-and-ask only credentials/payments/legal
(D-008). Bootstrap Gate 0 first. Producer model = claude-sonnet-5 for campaign builders ONLY
(D-047; reviewers/orchestrator pinned set unchanged).

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `tasks/M4-T012.json` (the re-claimed packet) + `directives/
{D-045..D-049}*/` + `blockers/B-023*.json` · `reports/M4-T013-street-width-research.md` (the B2
connector's pin) + `reports/M4-T01{3,4}-*` (the freshest gate/DCV arcs incl. the G3 FAIL→PASS
provenance precedent) · `docs/ARCHITECT_REVIEW_QUESTIONS.md` (G6 agenda; owner-verified §23-421(g))
· `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` (owner walkthrough) ·
`checkpoints/CP-2026-09-13-wave1-closed.json` · `.claude/session-handoff-profile.md` · `CLAUDE.md`
· this file.

## COPY INTO THE NEW SESSION

resume from handoff seq 107: work from durable repository evidence, not assumptions about the
prior conversation. Verify root/branch/HEAD (expect C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on
candidate/D-024-mrl-option-b; origin may have advanced — ledger and CI win), Bootstrap Gate 0
(cwd = worktree root, /mcp clean), read CLAUDE.md + docs/SESSION_HANDOFF.md, run
`python tools/project_control.py status` and
`python -m tools.agent_supervisor.campaign_continuity --status` (exit 1 = fall back to
ledger+git). 198 accepted; D-040 closed; D-046 wave 1 closed; directives D-045..D-049 active.
Execute NEXT-ACTION 1 (dispatch the already-re-claimed M4-T012 producer — rules-engineer @
claude-sonnet-5, worktree wt-m4t012-r2, definitive D-049 scope; the producer's BINDING first step
is full-text 23-421 print/PDF proof with the 9,500-present check) and NEXT-ACTION 2 (contract
M4-T015, the B2 street-width connector build pinning reports/M4-T013-street-width-research.md) —
disjoint scopes, run them parallel per D-046/D-047 (ramp per D-047-R004). Read the TIPS section
of the handoff before the first commit or accept (PS5.1 quote rule; the restamp+accept one-block
rule; validator ~440 s). Report READY TO RESUME or BLOCKED before changing anything. Stop only
for owner-only items (credentials/payments/legal, PR #241, public launch, Supabase, G6).

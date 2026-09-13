# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 106: 194 accepted; landed by /session-handoff (owner: "finish what u in middle then give me the promet for next season going to clear this season")

Generated 2026-09-12 ~22:05 ET (2026-09-13 UTC) by the landing orchestrator session
(session_01JjK8w1YXwFBjUS8PRrTfHp). Root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch
`candidate/D-024-mrl-option-b`, HEAD `08378dc8` **pushed** (in sync with origin). `main`
untouched at `d8b3899f`. PR #241 OPEN - NEVER merge. Dirty files at landing: only untracked
agent-memory notes + scratchpad/ (session-local, intentionally uncommitted); tracked tree clean
except one modified agent-memory MEMORY.md (reviewer-owned, left as-is).

## WHAT THIS SESSION DELIVERED (185 -> 194 accepted, all end-to-end gated + DCV'd)

1. **M0-T156 (186th)** D-040-R003 digest normalization - the control-plane CI red RETIRED
   permanently (sha256_text_artifact at c2/c14/migration; raw identity path untouched).
2. **M5-T017 (187th) + M5-T018 (188th)** D-041 C1 BOTH halves - the honest
   `unused_draft_zoning_floor_area` scenario section (cap - PLUTO built area, negative
   preserved -> professional review, typed not-computable, ZR 12-10 machine-readable
   assumption) + the web mirror validator + rendered line per astra-research 3.1/3.3.
3. **M5-T019 (189th)** D-040-R002 flag unification - web reads INTERNAL_RULE_EVAL_ENABLED
   (M5-T015 G5 F-1 CLOSED). Owner return note: rename the old env name in any Render
   dashboard IF ever set (web service block still withheld from render.yaml).
4. **M5-T020 (190th)** D-040-R001 SERVER half - display-only EPSG:4326 lot-geometry route
   `GET /api/v1/properties/{bbl}/lot-geometry` + closed lot_geometry contract (both copies +
   generated TS w/ in-suite drift guard) + live-captured MapPLUTO fixtures (G1 byte-verified
   vs the live FeatureServer).
5. **M5-T021 (191st)** D-042 EXECUTED - next EXACTLY 15.5.24 + whole-tree advisory sweep
   (sharp 0.35.4 critical found by research beyond the listed 7; js-yaml 4.3.2; vitest
   4.1.11 major; browserslist 4.28.9 + baseline-browser-mapping 2.11.21 overrides).
   **Run 34726577993 = the FIRST FULLY GREEN CI in branch history**; every run since stays
   fully green. B-022 RESOLVED per D-042-R002.
6. **M0-T157 (192nd)** resolver-test fixture repair (the D-042 capture made the hardcoded
   "D-042" test id real; now derived max+500, mutation-proven).
7. **M5-T022 (193rd)** maplibre-gl@6.7.0 ADMITTED - policy-15 G5 provenance review over all
   22 nodes (OSV clean, integrity==registry, ages recomputed, zero install scripts, OIDC
   trusted-publishing). Package is INERT (no source imports it yet - intended).
8. **M0-T158 (194th)** D-044 executed - handoff_token_budget 4000 -> 8000 (this handoff uses it).

Directives captured/executed this session: D-042 (peer-captured, executed), D-043
(peer-captured, QUEUED - see next actions), D-044 (this session captured + executed).
Blocker B-022 resolved. All work committed AND pushed; nothing uncommitted matters.

## NEXT ACTIONS (two parallel tracks, disjoint scopes)

1. **D-040-R001 FINAL increment - lot-outline WEB RENDERING packet** (closes the whole D-040
   queue): replace the placeholder in `apps/web/src/components/address/AddressConfirmCard.tsx`
   :141-145 with a MapLibre GL JS outline consuming the ACCEPTED `/lot-geometry` route +
   `packages/contracts/generated/lot_geometry.ts`. Cite D-040:D-040-R001 (applicability append).
   Pin: `project-control/reports/D-040-R001-mappluto-research.md` + M5-T020/T022 reports.
   Must handle: MultiPolygon/holes (LOT05/LOT06 fixtures), condo-unit honest-empty,
   multiple_features review, ZoLa link + ±20ft approximate-outline copy kept; DCP attribution
   on the map; producer frontend-engineer; G0/G1/G3/G4/G5 (UI -> G3). Also wire the
   lot_geometry.ts generator/CI drift coverage (the recorded follow-up) in or before it.
2. **D-043 internal web deploy** (owner-authorized, peer-captured 89cd6576; owner ACTIVE and
   ready to do dashboard steps): contract citing D-043:D-043-R001 - the DELIVERABLE is the
   exact Render settings + env-var checklist handed to the owner (R003: OWNER performs all
   dashboard steps; fold in the standing "Render Auto-Sync confirm" item). Internal/unlisted
   URL, INTERNAL_RULE_EVAL_ENABLED=on, NEXT_PUBLIC_API_BASE_URL -> the private API service;
   R002 API URL stays env-only; R004 NOT a public launch. Route the checklist via the peer
   session (ctl24-8e) or this handoff - owner reads both.
3. Then: owner return items (Supabase B-001 + Geoclient B-004 credentials = the end-to-end
   unlock; G6 legal; PR #241 stays unmerged; Part-4 gap list awaits owner triage - D-041-R003
   forbids self-assigning it).

## ADVISORY BACKLOG (no task contracted; triage when convenient)

C1 wave: scenario-bounds central bounding; hoist check primitives; web-consumes-generated-
contract; builder.py decomposition; boundedText truncation test; GET /scenario encode guard;
FORBIDDEN_FACT_KEYS addition. M0-T156 wave: bare-CR rejection; audit_log key drift;
status_projection normalizer; migration-manifest flip test. M5-T019: NEXT_PUBLIC posture
assertion. M5-T020: transport resilience (G5 LOW-1..4); generator wiring (item 1 covers).
M5-T021: eslint-config-next 15.5.24 alignment. M5-T022: ignore-scripts=true in .npmrc;
minimist promotion note. M0-T157: D-900 + D-001-R999 latent fixture collisions.
supervisor-bridge MRL descendant-proof test flaked once (run 34689359382) - watch.

## TRAPS THIS SESSION PROVED (keep)

- Closed-contract REQUIRED key = cross-layer co-land (server half alone turns web-e2e red;
  the hand-written mirror validator + shared fixtures + generated TS move together).
- `npm install --package-lock-only` PRESERVES in-range vulnerable resolutions - override,
  don't regen; too-young fix versions fail the age gate (aged-pin override).
- generate-lockfile.yml = the ONLY sanctioned lockfile path (dispatch -> bot proves+commits;
  bot pushes DON'T trigger ci.yml - follow with any push).
- Hardcoded future directive ids in fixture tests collide with real captures (derive max+500).
- Owner/peer works in the SAME checkout: verify foreign commits vs in-flight allowed_paths;
  their pushes preempt in-flight CI (cancel-in-progress).
- DCV rows: stamp reviewed_sha at HEAD; the DCV may pre-authorize a mechanical re-stamp
  conditional on an empty allowed_paths diff. Resubmit path from awaiting_gate =
  progress --status rework -> submit.

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. Supervisor frozen/SHADOW-ONLY. Expansion hold except the released
lot-outline increment (§2.1). No bare `git stash`. Dependency admissions only via the full
§G machinery. Deploy = D-043's internal scope ONLY (no public launch). API URL private;
Geoclient key only owner env/Render. Thin client (no local npm - CI/workflow only). G6
owner-only. Stop-and-ask only credentials/payments/legal (D-008). Bootstrap Gate 0 first.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `tasks/` + `directives/{D-040,D-042,D-043,D-044}*/` ·
`reports/D-040-R001-mappluto-research.md` + `reports/M5-T02{0,1,2}-*` (the freshest arcs:
admission machinery, DCV row shapes, delta-attestation flow) ·
`docs/design/astra-presentation-research.md` (UI presentation contract) ·
`.claude/session-handoff-profile.md` · `CLAUDE.md` · this file.

## COPY INTO THE NEW SESSION

resume from handoff seq 106: work from durable repository evidence, not assumptions about the
prior conversation. Verify root/branch/HEAD (expect C:/Users/MLFLL/Downloads/nyc-zoning/ctl24
on candidate/D-024-mrl-option-b; origin may have advanced - ledger and CI win), Bootstrap
Gate 0 (cwd = worktree root, /mcp clean), read CLAUDE.md + docs/SESSION_HANDOFF.md, run
`python tools/project_control.py status` and
`python -m tools.agent_supervisor.campaign_continuity --status` (exit 1 = fall back to
ledger+git). 194 accepted; CI fully green; C1 + D-040 R003/R002/R001-server + D-042 + MapLibre
admission all done. Execute NEXT-ACTION 1 (lot-outline WEB RENDERING packet closing D-040-R001,
citing D-040:D-040-R001, frontend-engineer producer, G3 in the wave) and NEXT-ACTION 2 (D-043
internal-deploy checklist for the owner, citing D-043:D-043-R001) - disjoint scopes, may run in
parallel. Report READY TO RESUME or BLOCKED before changing anything. Stop only for owner-only
items (credentials/payments/legal, PR #241 merge, public launch, Supabase, G6).

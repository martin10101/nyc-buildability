# DISCOVERY BACKLOG — mid-work findings tracked to resolution (D-069)

NOT auto-injected. This ledger holds product/domain discoveries made mid-work that are not
yet ledger tasks, blockers, or directive requirements — it FEEDS those systems and never
duplicates them. Statuses: **OPEN** (needs a decision), **QUEUED(task)** (in the pipeline),
**RESOLVED(record)** (closed, with where), **WATCH(trigger)** (deliberately monitored).
Rules (D-069): append at discovery time; sweep OPEN/WATCH at every contract seam and replan;
entries never get deleted — only status changes.

| ID | Date | Discovery | Source | Implication | Status |
|---|---|---|---|---|---|
| DB-001 | 2026-09-17 | 350 Fifth Ave (BBL 1008350041) is genuinely SPLIT-ZONED (C5-3 + C6-4.5 + Special Midtown) — `geometry_uncertain` is correct there; the product cannot yet apportion rules across a split lot | M5-T033 owner-confirmation record; ZTLDB row | Split-lot apportionment support (ZR 77-series class) — a real feature family, needs legal research first | OPEN |
| DB-002 | 2026-09-17 | Condo billing BBLs (lot 7501+) are absent from ZTLDB by design; 3022647515 (condono 1313) honestly reports no data | M5-T033 owner-confirmation; PLUTO/ZTLDB queries | Condo→base-lot resolution step before zoning-lot lookup; also a D-059-R007 benchmark hard class | OPEN |
| DB-003 | 2026-09-17 | The city's ZTLDB source dataset is stale AT THE SOURCE (rows last updated 2026-04-05; >45-day threshold logs on every live request) | Live Render logs; ztldb_soda freshness guard | Data-quality watch; G6-era decision on how stale zoning-lot data is presented to users | WATCH(re-check dataset rowsUpdatedAt at each deploy-verification; escalate if the city updates or the product goes external) |
| DB-004 | 2026-09-17 | Deployed services need `PYTHON_VERSION` pinned (Render default drifted to 3.14 → source-built shapely → geometry-pin guard fail-closed) | Run-38 deploy log; M5-T033 owner-confirmation | Deploy checklist must gain the PYTHON_VERSION pin row (checklist file currently outside every active packet's scope) | RESOLVED(M5-T035 accepted 2026-09-18 — checklist §6d PYTHON_VERSION=3.12.11 row) |
| DB-005 | 2026-09-17 | `PropertyOverview.tsx` builds its ZoLa link inline without the validated `zolaLotUrl()` helper (pre-existing; low risk) | M5-T032 G1 finding F2 + G3 finding 1 | Unify all ZoLa links through the shared validated helper (small web task; AddressConfirmCard too) | RESOLVED(M5-T036 accepted 2026-09-18) |
| DB-006 | 2026-09-17 | `address-search.ts` classifies ANY non-ok non-429 status (incl. 4xx) as retryable `source_unavailable` — practical impact ~nil today | M5-T032 G1 finding F1 | Tighten retry/label gate to `status >= 500` (small hardening) | OPEN |
| DB-007 | 2026-09-17 | AS-3 timeout outcome lacks a direct test that the full-address /search button is offered on timeout; architect-mode "Not my property" focus return also unit-untested | M5-T032 G4 F1 + journey F3 | Two small test additions in a future web packet | OPEN |
| DB-008 | 2026-09-17 | The 6000 ms address-search deadline sits below GeoSearch's observed healthy-but-slow latencies (~6.8 s): a consistently slow service routes every user to manual entry | M5-T032 journey finding 1; handoff §6 | Product-usability watch item for the owner (deliberate no-raised-deadline decision stands) | WATCH(revisit if live smoke or users show persistent >6 s healthy latencies) |
| DB-009 | 2026-09-17 | `malformed` failure copy omits the still-rendered full-address search button (copy/affordance mismatch, minor) | M5-T032 journey finding 2 | One-line copy fix in a future web packet | OPEN |
| DB-010 | 2026-09-17 | Named-street §12-10 override table (Broadway W94–97, Allen St Rivington–Delancey) has no implementation: needs a CD+cross-street matcher and distinct override provenance; M5-T034 wiring deliberately refuses exceptions_checked=True near those segments | M4-T018 report §3; M5-T034 packet scope note | Own follow-up module after M5-T034 (was already "OPEN" in Tier 2 prose — now tracked here) | OPEN |
| DB-011 | 2026-09-17 | EC-4 boundary-tangency legal tolerance question (zero-area LineString intersects) left open for qualified review | M4-T021 B4 disclosed judgment calls | G6-era legal question; keep with the G6 queue | WATCH(G6 activation) |
| DB-012 | 2026-09-17 | Loop review-round budget (4) is one round short for report-heavy tasks; honesty-bar packet block mitigates but the limit itself is owner-config | Runs 36/37 breaker analysis | Owner option: raise `consecutive_revision_loops` in the protected config; revisit if a run trips the breaker despite the honesty bar | WATCH(FIRED 2026-09-17 run-40: breaker tripped at 4 despite the honesty bar — mid-build churn (an investigation-only checkpoint + a stale lint claim cost two rounds), not report polish; run-41 relaunched with a RUN-40 CARRYOVER packet block; owner option to raise the protected-config budget surfaced 2026-09-17; escalate again on the next trip) |

| DB-013 | 2026-09-17 | Buffer engine: lot-polygon vertex count unbounded before shapely construction; per-segment PATH count unbounded before MultiLineString build (both currently safe — server-derived inputs) | M5-T034 G5 findings 1-2 | Two cheap defense-in-depth ceilings when the engine sits behind a live request path | RESOLVED(M5-T035 accepted 2026-09-18 — MAX_LOT_VERTICES + MAX_PATHS_PER_SEGMENT typed fail-closed) |
| DB-014 | 2026-09-17 | Wide-street outcome (far_row/governing_far/provenance) deliberately NOT serialized in rule_evaluation contract v1.0.0 — clients still see only the conservative FAR even on a confident WITHIN | M5-T034 G3 INFO-B | Additive contract bump to surface the wide-street result + provenance to the UI | OPEN |
| DB-015 | 2026-09-17 | The wide-street provider seam defaults to None — no live data source feeds real determinations through /rule-evaluation yet | M5-T034 G3 INFO-C; producer report §6.1 | Live provider wiring task (fetch DCM segments + lot geometry server-side per request, bounded) — the step that makes wide-street FAR real for users | RESOLVED(M5-T035 accepted 2026-09-18 — settings-gated live provider, fail-safe None) |

| DB-016 | 2026-09-17 | OWNER OBSERVATION: the product surface shows only residential FAR while ZoLa displays rich per-lot context (special districts, overlays, landmark status, neighbor-lot highlighting) — much of which our connectors ALREADY FETCH (e.g., the ZTLDB row carries zoning_district_1/2 + special_district_1 + zoning_map_number) but never display | Owner question 2026-09-17 ("what's the point if the government site shows all this?") | Context-panel parity task: surface the designations we already retrieve (with provenance + ZoLa link) alongside computed answers; label-display carries no computation risk and closes the perceived gap; the computed-answer engine remains the differentiator | RESOLVED(M5-T036 accepted 2026-09-18) |

| DB-017 | 2026-09-17 | Client-side profile mapped_features carries flags the new context panel does not render (2007 FIRM / 2015 pFIRM flood flags, transit zone, split-zone flag, zoning map number) — panel scope was districts/overlays/special districts/landmark+historic | M5-T036 producer discovery D1 (run persistent2-local-01, cross-session return) | Decide: extend the panel or keep AdditionalZoningFlags as the carrier for these; small follow-up either way | OPEN |
| DB-018 | 2026-09-17 | Once the context panel mounts, the architect overview surface carries TWO ZoLa affordances (the panel's validated link + PropertyOverview's existing one) | M5-T036 producer discovery D2 (same return) | Consolidation is a design call (product-design-director class), not a defect; judge after the panel is accepted and visible | OPEN |

| DB-019 | 2026-09-17 | M5-T036 review-wave polish trio (all advisory, none blocking): (a) "↗" glyph inside the two ZoLa link texts lacks aria-hidden (G3 F1 + HJ F6; matches a pre-existing sibling); (b) PropertyOverview renders NOTHING on a null BBL while the panel and confirm card show an honest absent note (G5 observation — consistency nuance); (c) mapped-feature coverage_status not surfaced on the panel's landmark/historic rows (G1 O1; full coverage table stays on the zoning tab + brief) | M5-T036 gate returns (G1/G3/G5/HJ) | One small web polish packet, or fold into the DB-018 design-director pass | OPEN |

Sweep log: seeded 2026-09-17 from M5-T032/T033 gate findings, owner-confirmation records,
M4-T018/T021 carried notes, and runs-36/37 analysis. +DB-013..015 from the M5-T034 review
wave (same day). +DB-016 owner product-gap observation (same day).
Sweep 2026-09-17 (M5-T035 contract seam): DB-015 + DB-013 + DB-004 → QUEUED(M5-T035) (live
provider packet folds in the engine ceilings and the checklist PYTHON_VERSION/flag rows).
All other OPEN entries reviewed and stay OPEN (DB-016 = the owner-ruled next lane after
M5-T035; DB-005/006/007/009 = small-web-task cluster, candidates to bundle with DB-016;
DB-001/002/010/014 need their own packets or legal research). WATCH entries unchanged
(DB-003 deploy-verification trigger, DB-008 latency, DB-011 G6, DB-012 next breaker trip).
Sweep 2026-09-17 (M5-T036 contract seam, loop-2 lane per D-071): DB-016 + DB-005 →
QUEUED(M5-T036) (context panel folds in the ZoLa-link unification on the same surface).
DB-007/009 stay OPEN (small address-flow items, next small web packet). Other entries
unchanged since the same-day M5-T035 sweep.

| DB-020 | 2026-09-18 | G1 F1: `wide_street_live_provider.py:356` passes `source_raw_digest=entry.segment.streetwidth_raw` (the width TEXT, e.g. "80") where the engine documents a raw-body-digest passthrough; real digests exist (`SegmentGeometryPage.raw_digest`); lot side correct; latent while the structured block is unserialized | M5-T035 G1 finding F1 | MUST be fixed inside the DB-014 serialization packet before the provenance block reaches any response | OPEN (bind to the DB-014 packet at contract) |
| DB-021 | 2026-09-18 | M5-T035 review hardening cluster (all advisory, none blocking): (a) G5 LOW-1 provider-side `MAX_LOT_VERTICES` check before its own first `canonical_to_shapely` (:282); (b) G5 LOW-2 cap `wide_object_ids` before the geometry-fetch loop (engine's 512 ceiling runs after fetch); (c) G5 LOW-3 docstring note on the two-layer ZR 12-10 exceptions attestation (width-policy "checked" vs EC-5 "unattested") + routed to the G6 legal queue; (d) G3 O1 optional wrap of pure-assembly steps; (e) G4 branch-coverage: `segment_geometry_unexpected_error` + `_attested_lot` sub-branches untested directly | M5-T035 gate returns (G1/G3/G4/G5) | Fold into the DB-014 packet or a later hardening pass; LOW-3's legal half joins DB-011 at G6 | OPEN |

| DB-022 | 2026-09-18 | zr-12-10.snapshot.json v1 (both copies) is a STALE July-2026 draft predating the 3/26/2026 amendment: only the basic wide/narrow definition, no named-street table, no alternate-width text, section_last_amended 2024-12-05, extraction_status extracted_draft, raw_html_verified false — while the ACCEPTED amended capture lives in project-control/reports/M4-T018-zr1210-wide-street-reconciliation.md (sha-pinned channel 4a75e22f) | M5-T039 run-01 consolidated blocker report (worker refused to fabricate provenance — correct) | Snapshot refresh QUEUED into M5-T039 phase 0 (verbatim transcription from the accepted capture, digest recompute, both copies synced); sweep other v1 snapshots for the same staleness class at the next research seam | QUEUED(M5-T039) |

Sweep 2026-09-18 (M5-T035 acceptance seam): DB-015 + DB-013 + DB-004 → RESOLVED(M5-T035
accepted 2026-09-18, 219th). +DB-020/021 from the review wave (above). Next-lane queue per
D-072/D-073: DB-014 screen-wiring packet (folds DB-020, DB-021a/b candidates) = loop-1;
validation-collection + four-regression-property packet (D-073-R004/R005;
docs/research/live-case-regression-properties.md seeded) = loop-2; DB-002 condo→base-lot
resolution = loop-3. DB-001/006/007/009/010/017/018/019 reviewed, stay OPEN (DB-006/007/009/
019 remain the small-web cluster; DB-010 own module after wiring; DB-017/018 design calls).
WATCH unchanged (DB-003 deploy trigger, DB-008 latency, DB-011 G6, DB-012 breaker — owner
decision package delivered 2026-09-18, answer pending).

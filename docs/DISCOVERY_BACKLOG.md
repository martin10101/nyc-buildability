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
| DB-004 | 2026-09-17 | Deployed services need `PYTHON_VERSION` pinned (Render default drifted to 3.14 → source-built shapely → geometry-pin guard fail-closed) | Run-38 deploy log; M5-T033 owner-confirmation | Deploy checklist must gain the PYTHON_VERSION pin row (checklist file currently outside every active packet's scope) | OPEN |
| DB-005 | 2026-09-17 | `PropertyOverview.tsx` builds its ZoLa link inline without the validated `zolaLotUrl()` helper (pre-existing; low risk) | M5-T032 G1 finding F2 + G3 finding 1 | Unify all ZoLa links through the shared validated helper (small web task; AddressConfirmCard too) | OPEN |
| DB-006 | 2026-09-17 | `address-search.ts` classifies ANY non-ok non-429 status (incl. 4xx) as retryable `source_unavailable` — practical impact ~nil today | M5-T032 G1 finding F1 | Tighten retry/label gate to `status >= 500` (small hardening) | OPEN |
| DB-007 | 2026-09-17 | AS-3 timeout outcome lacks a direct test that the full-address /search button is offered on timeout; architect-mode "Not my property" focus return also unit-untested | M5-T032 G4 F1 + journey F3 | Two small test additions in a future web packet | OPEN |
| DB-008 | 2026-09-17 | The 6000 ms address-search deadline sits below GeoSearch's observed healthy-but-slow latencies (~6.8 s): a consistently slow service routes every user to manual entry | M5-T032 journey finding 1; handoff §6 | Product-usability watch item for the owner (deliberate no-raised-deadline decision stands) | WATCH(revisit if live smoke or users show persistent >6 s healthy latencies) |
| DB-009 | 2026-09-17 | `malformed` failure copy omits the still-rendered full-address search button (copy/affordance mismatch, minor) | M5-T032 journey finding 2 | One-line copy fix in a future web packet | OPEN |
| DB-010 | 2026-09-17 | Named-street §12-10 override table (Broadway W94–97, Allen St Rivington–Delancey) has no implementation: needs a CD+cross-street matcher and distinct override provenance; M5-T034 wiring deliberately refuses exceptions_checked=True near those segments | M4-T018 report §3; M5-T034 packet scope note | Own follow-up module after M5-T034 (was already "OPEN" in Tier 2 prose — now tracked here) | OPEN |
| DB-011 | 2026-09-17 | EC-4 boundary-tangency legal tolerance question (zero-area LineString intersects) left open for qualified review | M4-T021 B4 disclosed judgment calls | G6-era legal question; keep with the G6 queue | WATCH(G6 activation) |
| DB-012 | 2026-09-17 | Loop review-round budget (4) is one round short for report-heavy tasks; honesty-bar packet block mitigates but the limit itself is owner-config | Runs 36/37 breaker analysis | Owner option: raise `consecutive_revision_loops` in the protected config; revisit if a run trips the breaker despite the honesty bar | WATCH(next breaker trip) |

Sweep log: seeded 2026-09-17 from M5-T032/T033 gate findings, owner-confirmation records,
M4-T018/T021 carried notes, and runs-36/37 analysis.

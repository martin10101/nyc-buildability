# M5-T030 — Independent G1 result

**Result: PASS — functional source/link correctness. Changed live UI verification remains pending.**

- Reviewer: `source_verifier`, independent of producer.
- Reviewed SHA: `0c6340b2e0824afc1b8b579668cb337d927c1ed9`
- Verified source/test manifest: `446534176f962bed0b3abfda887d524fcb34e6c8de78d6a3059c8a588799b562`
- Supplied authoritative task identity: `5070647085f077de7f1565be58b0a1f399e7352ceb41888e2c8c31e12d6bfaf0`
- Independently rehashed all ten manifest files; every hash matched.
- Independently reproduced **96/96 passing tests**, exit 0:

```text
npm run test -- src/lib/__tests__/provenance-link.test.ts src/components/architect/__tests__/source-links.test.tsx src/components/property/__tests__/provenance-disclosure.test.tsx
```

| Requirement | G1 finding |
|---|---|
| R001 | PASS: fixed official PLUTO endpoint; exact source/dataset/BBL validation; supplied profile identity must match; dataset link remains secondary. |
| R002 | PASS: captured fields, original/normalized values, units, version, dates, review/conflict state and full metadata remain accessible. Current-versus-captured distinction is explicit. |
| R003 | PASS for source and captured-record component checks. **Post-change live UI verification remains pending.** |
| R004 | PASS within reviewed source scope: pure frontend validation/presentation; source-matched fallback; explicit dataset conflicts rejected; no `request_url`-derived href, fetch or calculation added. Remote-state preservation is attributed to the orchestrator’s scope evidence. |
| R005 | PASS for reviewed wording: explains evidence organization and supported draft checks, manual alternatives and professional judgment without measured time-saving claims. |

Independent official checks returned HTTP 200 and exactly one row for each:

- [Empire State Building](https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1008350041): BBL `1008350041`, `338 5 AVENUE`, `lotarea=91351`, version `26v2`; checked September 15, 2026, 00:29:14 UTC. The [official LPC report](https://s-media.nyc.gov/agencies/lpc/lp/2000.pdf) independently identifies 350 Fifth Avenue as Manhattan block 835, lot 41.
- [Brooklyn lot](https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3021720001): `83 TAYLOR STREET`, `lotarea=116000`, `bldgarea=341300`, version `26v2`; checked 00:28:17 UTC.

The actual ESB captured-fact test preserved its complete JSON, including `lotarea`, original `91351`, normalized/displayed `91,351`, units, version and capture time `2026-09-15T00:38:20Z`.

**Defects: none identified within G1.** This result does not establish deployment, complete R003, or accept the task. It applies to the reviewed content; later E2E selector changes require separate delta attestation.

Evidence: `M5-T030-scope.json`, `M5-T030-source-verification.md`, `M5-T030-real-building-baseline.json`, `M5-T030-esb-captured-fact.json`, and `M5-T030-producer-report.md` under `project-control/reports/`.

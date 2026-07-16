# M1-T001 Producer Report — Official-source research: PLUTO / MapPLUTO

- **Task ID:** M1-T001
- **Producer agent:** official-source-researcher
- **Date:** 2026-07-16
- **Requested status:** `blocked`
- **Worktree:** `.claude/worktrees/agent-ab7d30546f58c0a85`

## 1. Summary

The task is 100% network-dependent research (verify official PLUTO/MapPLUTO distribution channels, dataset identifiers, data dictionary, versioning, rate limits, terms — every claim requires a working official URL + retrieval date 2026-07-16 + evidence quote). **All network-capable tools were permission-denied in this producer sandbox.** Producing the research document or the source-registry draft without live verification would require guessing dataset identifiers, field semantics, units, and cadences, which is prohibited by the task rules, CLAUDE.md principle 3, and PRD §31. No research deliverables were written; only this report.

## 2. Files created

- `project-control/reports/M1-T001-producer-report.md` (this file)

Files NOT created (blocked):

- `docs/research/pluto-mappluto-2026-07-16.md`
- `docs/research/source-registry-drafts/pluto-mappluto.json`

## 3. Exact denials (commands attempted and results)

Attempt 1 — WebFetch:

- Call: `WebFetch(url="https://apps.nyc.gov/content-api/v1/content/planning/resources/datasets/pluto-mappluto", prompt="Extract PLUTO/MapPLUTO release, formats, sizes, dictionary links...")`
- Result: `Permission to use WebFetch has been denied.`

Attempt 2 — WebSearch (issued in the same turn):

- Call: `WebSearch(query='NYC Open Data "Primary Land Use Tax Lot Output" PLUTO dataset data.cityofnewyork.us')`
- Result: `Permission to use WebSearch has been denied.`

Attempt 3 — Bash (natural alternative per the denial guidance):

- Command: `curl -s --max-time 30 "https://apps.nyc.gov/content-api/v1/content/planning/resources/datasets/pluto-mappluto" | head -c 3000`
- Result: `Permission to use Bash has been denied.`

Per task instructions ("If a command you genuinely need is permission-denied, record the exact denial in your report and return requested status blocked - do not retry endlessly"), I stopped after these three distinct tool families. No further retries or workarounds were attempted.

## 4. Acceptance scenarios S1–S5 → evidence mapping

| Scenario | Status | Reason |
|---|---|---|
| S1 (distribution channels, dataset IDs, formats) | NOT EXECUTED | requires live fetch of DCP page + Open Data catalog |
| S2 (PLUTO vs MapPLUTO, version scheme, archive) | NOT EXECUTED | requires live fetch of DCP page / BYTES of the BIG APPLE archive |
| S3 (data dictionary fields, units, null conventions) | NOT EXECUTED | requires the authoritative data dictionary document |
| S4 (channel discrepancies, priority order) | NOT EXECUTED | requires comparing live channel metadata (update timestamps/versions) |
| S5 (source-registry draft, all PRD §8.2 fields) | NOT EXECUTED | draft would contain guessed identifiers without S1–S4 evidence |

## 5. Fetch plan for unblocking (exact requests the producer would run)

If network permission is granted (or the orchestrator captures evidence per the ADR-005 / 2026-07-15 evidence-capture directive), these are the fetches needed. All URLs below are **starting points to be verified live**, not claims; the M0-T002 report proved the `apps.nyc.gov/content-api` pattern for client-rendered nyc.gov planning pages.

1. **DCP PLUTO/MapPLUTO page** (S1, S2): `https://www.nyc.gov/content/planning/pages/resources/datasets/pluto-mappluto` — client-rendered; fetch content via `https://apps.nyc.gov/content-api/v1/content/planning/resources/datasets/pluto-mappluto`. Capture: latest release name (expected `YYvN` style — verify), date of data, update frequency, download formats + sizes + URLs, data dictionary/readme links, archive link, use limitations.
2. **BYTES of the BIG APPLE archive** (S2): follow the archive link found on the DCP page (do not guess the URL) to document how prior PLUTO/MapPLUTO versions are retrievable.
3. **NYC Open Data catalog search** (S1): `https://data.cityofnewyork.us/browse?q=PLUTO` (and `q=MapPLUTO`) to obtain the current dataset 4x4 IDs. Candidate IDs from prior model knowledge — **UNVERIFIED, must be confirmed, never used unconfirmed**: PLUTO `64uk-42ks`; MapPLUTO `f888-ni5f`.
4. **Dataset metadata JSON** (S1, S4): for each confirmed ID, `https://data.cityofnewyork.us/api/views/<id>.json` (small KB-scale response — permitted evidence) to capture name, description, rowsUpdatedAt, attribution, columns, and whether a SODA resource endpoint (`/resource/<id>.json`) exists vs an attachment/href-only dataset (MapPLUTO geometry is often distributed as attachments/export rather than a tabular SODA resource — verify).
5. **Authoritative data dictionary** (S3): fetch the PLUTO data dictionary PDF/page linked from the DCP page (historically hosted under DCP assets or `nycplanning` GitHub — verify live). Extract key property-profile fields (BBL/borough/block/lot, LotArea + units, LotFront/LotDepth, ZoneDist1–4, Overlay1–2, SPDist1–3, Landmark, NumBldgs/NumFloors, BldgClass, LandUse, BuiltFAR/ResidFAR/CommFAR/FacilFAR, YearBuilt, BBL vs condo billing BBL handling, Address, Latitude/Longitude/XCoord/YCoord + CRS) with units and null/placeholder conventions; flag anything undocumented.
6. **ArcGIS REST / feature services** (S1): search DCP's official GIS distribution (e.g., links from the DCP page or `services.arcgis.com` items referenced by official NYC pages) for a MapPLUTO feature service; do not guess service URLs.
7. **SODA auth/rate limits** (S5): `https://dev.socrata.com/docs/app-tokens` (official Socrata developer docs) — app-token-optional throttling rules; plus NYC Open Data terms of use page linked from `https://opendata.cityofnewyork.us/`.
8. **Cross-check** (S4): compare DCP release version/date vs Open Data dataset `rowsUpdatedAt`/metadata to document update lag between channels.

Estimated total transfer: a few hundred KB of HTML/JSON/PDF-text — well within the low-storage budget. No dataset downloads at any point.

## 6. Assumptions and defaults

- None applied to deliverables (none were written).
- Assumed the denial is sandbox-wide for network tools, based on three independent tool families being denied in sequence.

## 7. Known limitations

- No research output exists for M1-T001 yet; the task remains at claimed/scope-verified level (~10%).

## 8. Security / provenance impact

- None. No files fetched, no datasets downloaded, no code or schema touched, no secrets involved.

## 9. New risks / dependencies

- Process risk: research-type producer tasks fail in sandboxes without network permission. Recommend the orchestrator either (a) relaunch this producer with WebFetch/WebSearch allowed, or (b) capture the fetches in §5 into `project-control/reports/` per the 2026-07-15 evidence-capture directive and relaunch the producer against the stored evidence.

## 10. Recommended next steps

1. Orchestrator records M1-T001 as `blocked` with this report as evidence.
2. Unblock via one of the two paths in §9; the fetch plan in §5 is complete and immediately executable.
3. After unblocking, the same producer completes S1–S5 and submits for G1/G3 with the two research deliverables.

## 11. Report path

`project-control/reports/M1-T001-producer-report.md`

---
name: nyc-source-fetch-channels
description: Which NYC official-source channels fetch reliably vs get bot-blocked; stable research technique for source-family packets
metadata:
  type: project
---

Reliable vs blocked channels for NYC official-source research (observed 2026-07-14 through 2026-07-16):

- `www.nyc.gov` and `apps.nyc.gov/content-api/...` return HTTP 403 to non-browser sessions (bot protection) — page-level claims (download links, sizes, archive URLs) must go through a browser-capable capture or be flagged [NEEDS G1 RE-VERIFICATION]. The content-api pattern worked on 2026-07-14 (M0-T002) but was 403 on 2026-07-16 — availability is inconsistent, do not depend on it.
- `s-media.nyc.gov/agencies/dcp/assets/...` PDFs (READMEs, data dictionaries) fetch fine directly and are the authoritative DCP release documents.
- Socrata endpoints are dependable evidence: `data.cityofnewyork.us/api/views/<4x4>.json` for metadata (but summarizer-mediated timestamp readings can be wrong — read raw unix values), `resource/<4x4>.json?$limit=1` proves SODA liveness and gives a verbatim field sample. SODA omits null fields per record — never infer schema from record keys; use the api/views columns array.
- `dev.socrata.com/docs/*` and `nycplanning.github.io/*` fetch fine.

**Why:** Two research runs (M0-T002, M1-T001) hit these exact behaviors; M1-T001 run 1 was fully network-denied and unblocked via the fetch-plan → orchestrator-capture → stored-evidence pattern (ADR-005).

**How to apply:** When drafting fetch plans for the remaining PRD §8.1 source families, route claims to the channels above by reliability, pre-mark nyc.gov page claims as needing browser capture, and always request the raw api/views JSON values (not summarizer paraphrase) for timestamps.

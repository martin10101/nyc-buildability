# Storage Budget

Governing policy: `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`. This file records measurements and the running budget. Update at every checkpoint that changes local footprint.

## Measurements
| Date | Free space (C:) | Event |
|---|---|---|
| 2026-07-14 (bootstrap start) | 6.09 GB (PowerShell GB = GiB basis: ~6.1 GiB reported as 6.09) | Baseline |
| 2026-07-14 (M0-T003 review) | 6,349,840,384 bytes ≈ 5.91 GiB ≈ 6.35 GB decimal | After bootstrap work (repo ≈ 0.2 MB — negligible) |

## Budget position
- Hard floor: 4 GB free must be preserved at all times.
- Nominal discretionary allowance: 2 GB — but the binding constraint is the floor, so true local headroom is ~1.9 GiB.
- Consequence (cloud-architect review, accepted): local installs of node_modules, Python venvs with GIS wheels, or browsers are prohibited by default; they could individually consume most of the headroom.

## Standing rules in force
- No Docker Desktop, no local Supabase/PostgreSQL/PostGIS, no citywide datasets, no bulk PDFs/embeddings/reports locally.
- Local checkout stays source-only (currently ≈ 0.2 MB including .git).
- Builds, dependency installs, tests, browsers, GIS processing, ingestion: GitHub Actions / Codespaces / Render / Supabase.
- Every task packet must declare execution location, expected disk use, durable-output destination, and cleanup (G0), and reviewers verify no unexpected local artifacts (G3/G4).
- Temp evidence larger than a few MB is uploaded to cloud storage (Supabase `debug-artifacts` bucket once available), not kept locally.

## Current local footprint of this project
- Repository (source + .git): ≈ 0.2 MB
- No dependencies installed, no datasets, no build outputs.

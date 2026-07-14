# Version 3 — Low-Storage Cloud-First Update

## User constraint

- Recorded that the project owner’s PC has approximately 7 GB free and must be treated as a thin client.

## Added

- `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`
- Cloud-development preference using GitHub Codespaces or another approved remote environment.
- GitHub Actions requirement for remote builds and tests.
- Local disk budget and minimum-free-space protection.
- G0/G3/G4 storage and cleanup checks.
- Cloud-routing rules for datasets, GIS files, PDFs, embeddings, reports, and temporary processing.
- Repository `.gitignore` for dependencies, datasets, GIS files, build outputs, local databases, and test recordings.
- Project-control storage-policy metadata.

## Changed

- Updated `CLAUDE.md`, PRD, README, bootstrap skill, agent operating system, gates, and Claude operations documentation.
- Prohibited Docker Desktop, local Supabase/PostgreSQL/PostGIS, full citywide datasets, and large dependency/build caches on the owner’s PC by default.
- Required agents to estimate storage, identify execution location, upload durable output to cloud services, and clean temporary files.

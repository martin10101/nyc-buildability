# Low-Storage Cloud Development Policy

## User constraint

The project owner’s local PC has approximately **7 GB of free disk space**. Treat the local PC as a thin client. The project must not require a full local development stack or local copies of large datasets.

## Mandatory architecture

Persistent or large project assets must live in cloud services:

- **GitHub** — source code, pull requests, CI, and small text fixtures.
- **GitHub Codespaces or another approved remote development environment** — interactive development, dependency installation, builds, and test execution when local installation would consume substantial disk space.
- **Supabase Database** — PostgreSQL, PostGIS data, rules, property facts, analyses, jobs, and audit history.
- **Supabase Storage** — government source snapshots, PDFs, GIS imports, generated reports, and organization uploads.
- **Render** — FastAPI, workers, cron jobs, one-off imports, temporary processing, and long-running AI/GIS jobs.
- **Vercel** — Next.js deployments and preview builds.
- **GitHub Actions** — remote linting, tests, builds, migrations checks, and release validation.

The local PC must never be the only location of code, configuration, source documents, reports, or project data.

## Local disk budget

When Claude is operating directly on the owner’s PC:

- Preserve at least **4 GB free space** at all times.
- Do not intentionally consume more than **2 GB** of additional local disk without explicit owner approval.
- Keep the local Git checkout source-only and small.
- Before any dependency installation, dataset download, build, package cache, or generated artifact, check available disk space.
- If the projected operation could exceed the budget, stop and move the task to Codespaces, GitHub Actions, Render, Supabase, or another approved cloud environment.

## Prohibited local operations by default

Do not perform these operations on the owner’s PC unless explicitly approved after showing the expected disk use:

- Install Docker Desktop or maintain local Docker images/volumes.
- Run a local Supabase stack, local PostgreSQL/PostGIS, or local object storage.
- Download full PLUTO, MapPLUTO, GIS, DOB, ACRIS, zoning, or other citywide datasets.
- Store bulk PDFs, source snapshots, embeddings, report archives, or database backups locally.
- Build local pgvector indexes.
- Retain large `node_modules`, Python virtual environments, package caches, browser binaries, test videos, or build outputs when the work can run remotely.
- Create duplicate ZIP archives or large debug bundles in the repository.
- Use Git LFS as a substitute for Supabase Storage unless a specific reviewed use case requires it.

## Required implementation behavior

- Stream or download government data directly to a Render worker, process it in bounded temporary space, upload the durable result to Supabase, and delete temporary files after success or failure.
- Use chunked/resumable imports so workers do not require the entire source dataset in memory or on disk.
- Store only small representative API/GIS fixtures in Git for tests.
- Use signed Supabase Storage URLs for workers and users.
- Configure temporary directories and cleanup routines explicitly.
- Add maximum file-size, job-storage, and retention limits.
- Ensure failed jobs clean up abandoned temporary files.
- Run frontend/backend builds and full test suites in GitHub Actions or Codespaces rather than on the owner’s PC.
- Generate reports in Render and upload them directly to Supabase Storage.
- Use remote database migrations against development/staging Supabase projects; do not require a local database.

## Repository hygiene

The repository must ignore local-heavy artifacts, including:

- `node_modules/`
- Python virtual environments
- `.next/`, build, coverage, and cache directories
- downloaded datasets and GIS exports
- source snapshots and generated reports
- local database files
- temporary workspaces
- browser test recordings and screenshots unless intentionally committed as small reviewed fixtures

Agents must not commit large binaries or generated dependencies.

## Storage gate

G0 readiness must confirm:

1. Where the task will execute.
2. Expected temporary and persistent storage use.
3. That persistent output is routed to GitHub, Supabase, or another approved cloud service.
4. That the owner’s local PC will remain within the disk budget.
5. That cleanup behavior is defined and testable.

G3/G4 reviewers must verify that the completed feature does not unexpectedly write large or permanent files to the local user device.

## User-device experience

The finished application must be browser-based and must not require users to download citywide datasets. Normal use may download only explicitly requested reports or exports. Browser caches must not be the sole storage of any project record.

# Backend-engineer memory index

- [Producer sandbox varies per session](env-producer-sandbox-no-exec.md) — probe exec + write at session start; worktree isolation rejects shared-checkout paths, compound Bash, and can strand you off the dispatched base SHA
- [2026-07-15 no-exec fallback playbook](sandbox-no-python-exec.md) — stale as a universal rule; keeps the Grep-static/orchestrator-capture playbook for sessions where the probe fails
- [Socrata/PLUTO connector gotchas](socrata-pluto-gotchas.md) — checkbox columns are JSON booleans (='Y' gives type-mismatch 400); bbl decimal-serialized in FULL records; SODA omits nulls even under $select

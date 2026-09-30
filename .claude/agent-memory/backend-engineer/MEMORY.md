# Backend-engineer memory index

- [Producer sandbox varies per session](env-producer-sandbox-no-exec.md) — probe python/network cheaply at session start; M1-T002 had full exec+network, earlier sessions had none; rm can be denied
- [2026-07-15 no-exec fallback playbook](sandbox-no-python-exec.md) — stale as a universal rule; keeps the Grep-static/orchestrator-capture playbook for sessions where the probe fails
- [Socrata/PLUTO connector gotchas](socrata-pluto-gotchas.md) — checkbox columns are JSON booleans (='Y' gives type-mismatch 400); bbl decimal-serialized in FULL records; SODA omits nulls even under $select
- [Supervisor turnover evidence plumbing](supervisor-turnover-evidence-plumbing.md) — REAL Fable weekly exhaustion is in stream events (rate_limit_event seven_day/rejected + api-error result phrase), NOT stderr/checkpoint_error; runner distills result_text + rate_limit_rejection; classifier decides, bare 429 stays AMBIGUOUS

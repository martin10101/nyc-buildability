#!/usr/bin/env python3
"""One-off orchestrator helper: enrich the three bootstrap-proof task packets
with scope, acceptance scenarios, and reviewer assignments."""
import json
from pathlib import Path

PC = Path(__file__).resolve().parents[1] / "project-control"

ENRICH = {
    "M0-T001": {
        "producer_hint": "progress-auditor",
        "reviewer_agents": ["orchestrator"],
        "allowed_paths": ["project-control/reports/M0-T001-audit.md"],
        "forbidden_paths": ["src/**", "project-control/tasks/**", "project-control/gates/**"],
        "inputs": ["project-control/**", "git history", "repository tree"],
        "outputs": ["project-control/reports/M0-T001-audit.md"],
        "acceptance_scenarios": [
            {"id": "S1", "case": "normal", "input": "current ledger + git log", "expected": "every ledger claim (M0-T000 accepted, CP-0001/2, gates) matched to concrete file/git evidence or flagged"},
            {"id": "S2", "case": "missing-data", "input": "task with no gate report", "expected": "flagged as unsupported progress"},
            {"id": "S3", "case": "conflict", "input": "ledger vs repo mismatch", "expected": "explicit discrepancy list with file paths"},
        ],
    },
    "M0-T002": {
        "producer_hint": "official-source-researcher",
        "reviewer_agents": ["data-contract-verifier"],
        "allowed_paths": ["docs/research/M0-T002-geoclient-address-resolution.md"],
        "forbidden_paths": ["src/**", "project-control/tasks/**"],
        "inputs": ["https://api-portal.nyc.gov/", "official NYC DCP documentation"],
        "outputs": ["docs/research/M0-T002-geoclient-address-resolution.md"],
        "acceptance_scenarios": [
            {"id": "S1", "case": "normal", "input": "NYC Geoclient/Geosupport official docs", "expected": "current endpoint(s), auth model, rate limits, pagination/N-A, update cadence, field definitions for BBL/BIN resolution, with source URLs and retrieval date"},
            {"id": "S2", "case": "conflicting-source", "input": "multiple candidate address services (Geoclient vs GeoSearch)", "expected": "both documented with official status, differences, and recommendation"},
            {"id": "S3", "case": "missing-data", "input": "detail not published", "expected": "explicitly marked unknown; no guessed endpoints, fields, or units"},
        ],
    },
    "M0-T003": {
        "producer_hint": "cloud-architect",
        "reviewer_agents": ["orchestrator"],
        "allowed_paths": ["project-control/reports/M0-T003-bootstrap-review.md"],
        "forbidden_paths": ["src/**", "project-control/tasks/**", "project-control/gates/**"],
        "inputs": ["CLAUDE.md", "PRD.md", "docs/**", "project-control/**"],
        "outputs": ["project-control/reports/M0-T003-bootstrap-review.md"],
        "acceptance_scenarios": [
            {"id": "S1", "case": "normal", "input": "bootstrap plan (git init, private GitHub, Supabase/Render/Vercel plan, low-storage policy)", "expected": "each element judged sound/unsound with reasons; risks and gaps listed"},
            {"id": "S2", "case": "boundary", "input": "7 GB disk constraint", "expected": "verdict on whether planned local footprint fits the 4 GB-free floor"},
            {"id": "S3", "case": "invalid-input", "input": "any plan step contradicting PRD/policy", "expected": "flagged with document citation"},
        ],
    },
}

for task_id, fields in ENRICH.items():
    p = PC / "tasks" / f"{task_id}.json"
    t = json.loads(p.read_text(encoding="utf-8-sig"))
    t.update(fields)
    p.write_text(json.dumps(t, indent=2) + "\n", encoding="utf-8")
    print(f"enriched {task_id}")

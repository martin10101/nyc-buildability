# M0-T158 Producer Report — handoff_token_budget 4000 -> 8000 (D-044)

Producer: orchestrator. One surgical byte-level value replacement in
tools/context_budget.json: handoff_token_budget 4000 -> 8000 (D-044-R001). The diff is
exactly one line; every other key byte-identical (D-044-R002); the check script and its
tests are forbidden paths and untouched.

Verification (real output): python tools/test_context_budget_check.py -> OK (EXIT 0);
python tools/context_budget_check.py -> PASS (EXIT 0). The context-budget CI job at the
fix head is the executable authority (it runs both).

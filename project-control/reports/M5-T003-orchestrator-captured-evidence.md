# M5-T003 — Orchestrator-captured test/lint/modularity evidence

**Why this file exists:** the M5-T003 producer runs in a Python-3.11, broker-restricted sandbox and
the packet documented no test commands, so its broker fail-closes pytest/ruff/python (it correctly did
NOT bypass that). Per the evidence-capture division of labor (`.claude/rules/project-control.md`), the
orchestrator captures the executable evidence here and the gate reviewers verify this stored artifact.

## Provenance
- **Interpreter:** `C:\Users\MLFLL\AppData\Local\Programs\Python\Python311\python.exe` — **Python 3.11.9**.
- **CAVEAT (version):** CI targets **3.12** (`.github/workflows/ci.yml`). Only 3.11 and a non-resolving
  3.13 stub exist on this machine; **no 3.12 is installed**, and GitHub push is held (no fresh CI). The
  M5-T003 scenario/rule-evaluation/property test chain **collects and runs cleanly on 3.11**. The only
  3.12-only code in the tree is `services/api/app/documents/**` + `tests/documents/**` (PEP 695 `type`
  syntax, e.g. `app/documents/units.py:276`), which is OUT OF M5-T003 SCOPE — see CMD3 below.
- **Captured:** 2026-09-08 ~06:20Z, branch `task/M5-T003-scenario-endpoint`, **working-tree state**
  (producer edits not yet committed; branch HEAD 62aec042). Digests below bind exactly what ran.
- **File digests (sha256) — IDENTICAL before and after the run (no concurrent edit during capture):**
  - `7b5127ced2e69e51635caf07e670dc1eaafd82c669336c5db1c8b04974385d89`  services/api/app/api/v1/scenario.py
  - `5d27ac07b09fd203f7001cd2480d5a93b23879e188cd9a35b7f9d6dc2cbc300d`  services/api/app/config.py
  - `eb5523abcd423a00922681b0512c2b32fc89aa1f8d9540c47aab0cd6113742ab`  services/api/app/main.py
  - `47399b4aacf73d7ee246c43d37775884443d86caf49389ebdf504ebca3ad57fe`  services/api/tests/api/test_scenario_api.py

## Results

| # | cwd | command | exit | result |
|---|---|---|---|---|
| 1 | services/api | `python -m pytest tests/api/test_scenario_api.py -q` | 0 | **27 passed** in 1.70s |
| 2 | services/api | `python -m pytest tests/api/test_rule_evaluation_api.py tests/api/test_properties_v1.py tests/api/test_property_contract.py -q` | 0 | **107 passed** in 3.75s |
| 3 | services/api | `python -m pytest tests/ -k "config or flag or rule_eval" -q` | 2 | 15 COLLECTION errors — ALL in `tests/documents/**` (PEP 695, 3.12-only; out of scope). 1572 deselected. |
| 3b | services/api | `python -m pytest tests/ -k "config or flag or rule_eval" --ignore=tests/documents -q` | 0 | **111 passed**, 1018 deselected in 2.62s |
| 4 | services/api | `python -m ruff check .` | 0 | **All checks passed!** |
| 5 | repo root | `python tools/modularity_check.py --check` | 0 | selected 358 files; **failures 0**; 14 warnings (all pre-existing supervisor/apps-web/connector modules; NONE in M5-T003 files) |

**CMD3 note:** raw exit 2 is entirely the `tests/documents/**` PEP-695 collection failure that exists
independent of this task (the `-k` filter deselects them anyway; collection aborts before filtering).
Row 3b isolates the actually-targeted config/flag/rule_eval tests → **111 passed, exit 0**. On CI (3.12)
the documents tests collect normally.

## Verdict (orchestrator capture; reviewers verify)
M5-T003 endpoint: **27/27 acceptance tests pass**, **no regressions** in the adjacent property /
rule-evaluation / contract routes (107 pass), config/flag/rule_eval tests pass (111), **ruff clean**,
**modularity 0 failures**. The only non-zero exit (CMD3 raw) is a pre-existing 3.11-environment
limitation in unrelated `tests/documents/**`, not an M5-T003 defect.

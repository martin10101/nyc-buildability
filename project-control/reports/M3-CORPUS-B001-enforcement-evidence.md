# B-001 acceptance-enforcement evidence — M3-T002 / M3-T004 (amendment issue 1)

**Purpose:** prove that open **B-001** REALLY prevents acceptance of the two durable-storage corpus tasks via the control CLI's blocker mechanism — not merely via packet prose. Control-only; no real task state mutated.

## Mechanism (why it now works)

`tools/project_control.py accept` rejects when an open blocker record names the task, word-bounded, in its `affects` or `detail` (`_blocker_references`, project_control.py:525-537; accept loop :583-595). Revision-2 relied only on the task's own `blockers[]` field + prose `acceptance_preconditions`, which the CLI does **not** enforce. Fixed by amending the real `project-control/blockers/B-001-supabase-access-token.json` so its `affects` array now contains `M3-T002 (...)` and `M3-T004 (...)` and its `detail` states durable legal-corpus storage is required before acceptance.

## Permanent regression (control-plane test, not product code)

Added test group **S9** — `test_s9_b001_m3_corpus_storage_enforcement` in `tools/test_project_control.py` (the file CI runs in the `control-plane` job). It uses the SAME B-001 `affects` wording committed to the real blocker, in an isolated temporary ledger (`tempfile.mkdtemp` + `shutil.rmtree`), and asserts:

| Sub-check | Assertion |
|---|---|
| (a) | open B-001 → `accept M3-T002` fails, stderr names `B-001` |
| (b) | open B-001 → `accept M3-T004` fails, stderr names `B-001` |
| (c) | adding a `fixtures_only=true` marker (or any task field) does NOT bypass — accept still fails on B-001 |
| (d) | setting B-001 `status:"resolved"` → `accept M3-T002` succeeds, proving B-001 was the sole remaining blocker |

Both temp tasks are driven to `awaiting_gate` with all required gates PASS and no dependencies, so B-001 is the ONLY variable under test.

## Run output

```
$ python tools/test_project_control.py
...
OK: S9 B-001 blocks M3-T002/M3-T004 acceptance (fixture-only cannot bypass; resolving B-001 unblocks)
OK: all 11 project-control test groups passed
```

## Isolation confirmation

The test creates and destroys its own temp ledger and never writes to `project-control/`. Verified after the run: real `project-control/tasks/M3-T002.json` and `M3-T004.json` remain `status: "backlog"` (unchanged). No task was moved, claimed, dispatched, implemented, or accepted.

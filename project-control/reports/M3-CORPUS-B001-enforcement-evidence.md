# B-001 acceptance-enforcement evidence — M3-T002 / M3-T003 / M3-T005 (durable-storage tasks)

**Purpose:** prove that open **B-001** REALLY prevents acceptance of the three durable-storage corpus tasks — **M3-T002** (immutable original HTML/PDF captures), **M3-T003** (rendered pages + extraction/OCR evidence + review bundles), and **M3-T005** (Construction-Code + amendment-overlay corpus) — via the control CLI's blocker mechanism, not via packet prose. Control-only; no real task state mutated. (M3-T004 closure is not a durable-bulk-storage task; it is gated by its dependency on accepted M3-T002 + M3-T003, not by B-001.)

## Mechanism (why it works)

`tools/project_control.py accept` rejects when an open blocker record names the task, word-bounded, in its `affects` or `detail` (`_blocker_references`, project_control.py:525-537; accept loop :583-595). A task's own `blockers[]` field and prose `acceptance_preconditions` are NOT enforced by the CLI. The real `project-control/blockers/B-001-supabase-access-token.json` therefore lists **M3-T002, M3-T003, M3-T005** in `affects` (each with the durable-storage responsibility it carries under the §17.16 ownership split).

## Permanent regression (control-plane test, not product code)

Test group **S9** — `test_s9_b001_m3_corpus_storage_enforcement` in `tools/test_project_control.py` (the file CI's `control-plane` job runs). It is **anti-drift**: it **reads the actual committed `B-001` JSON**, asserts that the real blocker's affects/detail identify **exactly** the intended M3 storage tasks `{M3-T002, M3-T003, M3-T005}` (failing if a task is added or dropped), then **copies that real blocker into an isolated temporary ledger** (`tempfile.mkdtemp` + `shutil.rmtree`) and runs the acceptance tests there. It never duplicates the affects wording by hand, and it changes only the temporary copy's status to `resolved` — the real blocker and real task state are never mutated.

| Sub-check | Assertion |
|---|---|
| pre | the REAL committed B-001 references exactly `{M3-T002, M3-T003, M3-T005}` (drift guard) |
| (a) | open B-001 → `accept M3-T002` fails, stderr names `B-001` |
| (b) | open B-001 → `accept M3-T003` fails, stderr names `B-001` |
| (c) | open B-001 → `accept M3-T005` fails, stderr names `B-001` |
| (d) | adding a `fixtures_only=true` marker (or any task field) does NOT bypass — accept still fails on B-001 |
| (e) | setting the TEMP copy of B-001 to `resolved` → accept succeeds for all three, proving B-001 was the sole remaining blocker |

Each temp task is driven to `awaiting_gate` with all required gates PASS and no dependencies, so B-001 is the only variable under test.

## Run output

```
$ python tools/test_project_control.py
...
OK: S9 B-001 (read from the real committed record) blocks M3-T002/M3-T003/M3-T005
    acceptance (fixture-only cannot bypass; resolving B-001 unblocks all three)
OK: all 11 project-control test groups passed
```

## Isolation confirmation

The test reads the real B-001 record read-only and copies it into its own temp ledger, which it creates and destroys; it never writes to `project-control/`. Verified after the run: real `project-control/tasks/M3-T002.json`, `M3-T003.json`, and `M3-T005.json` remain `status: "backlog"` (unchanged), and the real `B-001` record's status remains `open`. No task was moved, claimed, dispatched, implemented, or accepted.

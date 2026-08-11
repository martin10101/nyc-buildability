---
name: supervisor-testing-gotchas
description: tools/agent_supervisor test mechanics - real-spawn harness, DurableJournal concurrent-first-open lock, and how to measure the true freeze baseline before/after a change
metadata:
  type: project
---

Working inside `tools/agent_supervisor/**` and its `tools/test_agent_supervisor_*.py` suite.

**Real-spawn harness already exists — reuse it.** `tools/test_agent_supervisor_runner.py`
has `_ScriptRunner` (a `ClaudeRunner` subclass that prefixes the fake script into
`build_argv`) plus a `FAKE_CLAUDE` script driven by `FAKE_MODE`; `FAKE_MODE=hang` sleeps 600
(a worker that stays alive) and the default mode emits a valid checkpoint and exits. That
gives genuine `Popen` coverage without inventing a second harness. `tools/test_agent_supervisor_loop.py`
has the parallel CLI harness (`CONFIG_TOML` / `SELECTION_TOML` / packet, `sys.executable` as
the "claude" binary → dispatch ends at the honest `no_valid_checkpoint` stop).

**DurableJournal: two connections must not perform the FIRST open concurrently.**
`open()` runs `PRAGMA journal_mode=WAL` + `_migrate()`; two connections doing that on the
same brand-new file intermittently raise `JournalError: unreadable_database: ... database is
locked` (reproduced 2 of 3 runs). Create/open the journal once before starting the second
"process", then concurrent read/write is fine (WAL + `timeout=30`). Also: the sqlite
connection is `check_same_thread=True`, so a thread that simulates another supervisor must
open its OWN `DurableJournal`, never borrow the test's.

**Freeze-baseline arithmetic.** `.claude/rules/supervisor-freeze.md` requires re-establishing
the `M0-T039-supervisor-freeze.md` baseline (>= 1165 tests, 0 failures), but the specific
count quoted in an older gate report is stale the moment another task lands. Measure the
real pre-change count in the same run: `pytest tools/test_agent_supervisor_*.py -q -k "not
<YourNewClass1> and not <YourNewClass2>"`, then check the deselect count with
`--collect-only` — test class names DO collide across modules (e.g. `ChildAccountingTests`
exists in both `recovery` and `runner` test files), so `-k` can silently deselect
pre-existing tests too.

**Lint reality:** CI's only `ruff` job runs with `working-directory: services/api`
(`.github/workflows/ci.yml`), so `tools/**` has never been ruff-gated and carries
pre-existing F401s; no pyright/mypy job exists at all. Before "fixing" a type or lint
complaint someone attributes to your diff, check it against the base commit — inserting
lines renumbers pre-existing diagnostics and makes them look new.

---
name: freeze-baseline-excludes-some-supervisor-tests
description: The 20-module supervisor freeze-baseline command does NOT include every supervisor test; some (start_reentry) monkeypatch runner internals with fixed-arity spies, so a green freeze baseline can still hide a signature-change regression
metadata:
  type: project
---

The supervisor "freeze baseline" run in producer packets lists exactly 20 `tools.test_agent_supervisor_*`
modules. That list is NOT `unittest discover` — it OMITS at least `tools/test_agent_supervisor_start_reentry.py`
(and possibly others). CI / discover still runs the omitted files.

**Why:** `test_agent_supervisor_start_reentry.py` runs the CLI IN-PROCESS (`self.cli.main(...)`) and
monkeypatches runner module globals with hardcoded-arity spies, e.g.
`def spy_clear(journal): ...; cr.clear_child_record = spy_clear`. Because `_settle_worker_record`
references the module global, the spy intercepts the real production call. So ANY signature change to
`clear_child_record` / `record_launched_child` (adding kwargs like `pid=`/`start_token=`) makes the
spy raise `TypeError: ... unexpected keyword argument`, even though the freeze-baseline command stays
green (that file isn't in the 20). Confirmed on M0-T059 (2026-08-11).

**How to apply:** When changing a signature of anything in `tools/agent_supervisor/` that is
monkeypatched by tests (grep the test tree for `cr.<name> =` / spy fakes), independently run the
OMITTED files (esp. `test_agent_supervisor_start_reentry`) — do NOT trust the 20-module freeze command
alone. If the omitted test is outside your allowed_paths, it is a real scope wall: deliver the in-scope
fix and report the companion spy edit (usually a `**kwargs`-tolerant spy) with the exact diff. See also
[[agent-supervisor-rotation-and-model-machinery]].

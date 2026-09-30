---
name: skipif-detached-onto-fixture
description: QA review gotcha — a @pytest.mark.skipif silently detaches from a test when a fixture def is inserted between the decorator and the test
metadata:
  type: feedback
---

Watch for a `@pytest.mark.skipif(...)` decorator that ends up sitting directly
above a `@pytest.fixture` definition instead of the test it was meant to guard.
Marks applied to fixtures have NO effect (pytest emits
`PytestRemovedIn9Warning: Marks applied to fixtures have no effect`), and the
test below loses its guard.

**Why:** seen in M0-T103 (`tools/test_agent_supervisor_capability_probe.py`): a new
`post()` fixture was inserted between the `skipif(claude absent)` decorator and
`test_live_reprobe_claude_version_matches_fixture`. Result: the fixture is
un-skippable (no-op mark) and the test is now UNGUARDED — on a runner without the
CLI it FAILS (`_run` returns status `absent` → `assert status=="supported"` fails)
instead of skipping cleanly, breaking the module's documented "skips cleanly when
absent" (D-024 16.1) contract.

**How to apply:** treat any "Marks applied to fixtures have no effect" warning as a
real finding, not noise — trace which test lost its guard. Direction is fail-safe
(loud fail, never a false green), so it is typically a NON-BLOCKING advisory when
the CLI is present in the target/CI env; recommend moving the `skipif` back onto the
test function (or add a separate one). Confirm severity by reasoning about the
absent-dependency path, not just the green run.

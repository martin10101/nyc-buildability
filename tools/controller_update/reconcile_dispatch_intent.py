"""OWNER-RUN operator reconciliation (S11.5 / M0-T125 D6) - 2026-09-06.

The 30-minute shell cap killed the supervisor mid-unit (cycle dispatched
06:31:05Z), leaving the durable `unit_dispatch_intent` row pending, so every
`start` correctly refuses with AMBIGUOUS_EFFECT/unit_dispatch_unreconciled.
There is no CLI verb for operator reconciliation yet (follow-up task).

Read-only evidence already gathered by the orchestrator:
  - the dead unit's only effects are UNCOMMITTED in-scope file edits in
    wt-m0t025 (git status: 3 allowed-path files, +141/-20);
  - no commits, no pushes, no ledger writes, no external effects.
Verdict: effects fully known; re-dispatch is safe and builds on those files.

This script calls the controller's OWN `reconcile_dispatch_intent` (the exact
function the loop calls after a unit journals its outcome), then prints the
before/after rows. Run from anywhere:

    python C:\\Users\\MLFLL\\Downloads\\nyc-zoning\\ctl24\\tools\\controller_update\\reconcile_dispatch_intent.py
"""
import os
import sys

REPO = r"C:\Users\MLFLL\Downloads\nyc-zoning\ctl24"
sys.path.insert(0, REPO)

from tools.agent_supervisor.durable_state import DurableJournal  # noqa: E402
from tools.agent_supervisor import recovery  # noqa: E402

DB = os.path.expandvars(
    r"%LOCALAPPDATA%\NYCBuildabilitySupervisor"
    r"\9aca707563cfe6e2cdeeee99e5d153951936dc46edac131889c37c2a9f713b6a"
    r"\supervisor_journal.sqlite3")


def main() -> int:
    journal = DurableJournal(DB).open()
    try:
        before = journal.get_state(recovery.UNIT_DISPATCH_INTENT_KEY, None)
        print("before:", before)
        if not (isinstance(before, dict) and before.get("pending")):
            print("nothing pending - already reconciled; no change made.")
            return 0
        recovery.reconcile_dispatch_intent(journal)
        after = journal.get_state(recovery.UNIT_DISPATCH_INTENT_KEY, None)
        print("after :", after)
        print("RECONCILED - `start` may now dispatch again.")
        return 0
    finally:
        journal.close()


if __name__ == "__main__":
    raise SystemExit(main())

"""Operator repair for a FORKED audit chain (M0-T046 / D-010-R125-R126 shape) - 2026-09-06.

What happened: the live supervisor run and the overnight launcher's lock-probe starts appended
audit events concurrently; two writers claimed sequence 213, so the hash chain is forked. By
design (audit_log.py `_load_head_from_log`), a forked chain is NEVER silently extended: every
append - including the audit seal of any new `start` - refuses until an explicit operator repair.
The owner previously ACKNOWLEDGED this exact same-machine race shape as repairable-by-operator.

The repair (evidence-preserving, nothing deleted, nothing rewritten):
  1. rename audit.jsonl            -> audit.jsonl.forked-evidence-<UTC timestamp>
  2. rename audit.jsonl.head.json  -> audit.jsonl.head.json.forked-evidence-<UTC timestamp>
A fresh chain then begins at the genesis digest on the next append. The forked file remains
byte-for-byte intact as tamper-evidence; verify_chain() can still report its exact fork.

Run:  python C:\\Users\\MLFLL\\Downloads\\nyc-zoning\\ctl24\\tools\\controller_update\\repair_forked_audit_chain.py
"""
import datetime
import os
import pathlib

RUNTIME = pathlib.Path(os.path.expandvars(
    r"%LOCALAPPDATA%\NYCBuildabilitySupervisor"
    r"\9aca707563cfe6e2cdeeee99e5d153951936dc46edac131889c37c2a9f713b6a"))


def main() -> int:
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    moved = 0
    for name in ("audit.jsonl", "audit.jsonl.head.json"):
        src = RUNTIME / name
        if not src.exists():
            print(f"absent (ok): {src.name}")
            continue
        dst = RUNTIME / f"{name}.forked-evidence-{stamp}"
        src.rename(dst)
        print(f"archived: {src.name} -> {dst.name} ({dst.stat().st_size} bytes preserved)")
        moved += 1
    if moved == 0:
        print("nothing to repair - no audit files present (fresh chain already in effect).")
    else:
        print("REPAIRED: a fresh audit chain starts at genesis on the next append; the forked "
              "chain is preserved verbatim as evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

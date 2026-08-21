#!/usr/bin/env python3
"""Control-plane probes: does the LEDGER actually confer this authority?

Split out of `recovery_probes.py` by the M0-T079 correction round. The sibling
probes read the REPOSITORY (git, the worktree, the remote) or the JOURNAL (the
supervisor's own durable state). These read `project-control/` - a third source,
with its own layout and its own authority semantics, changing for entirely
different reasons than either of the others.

C8 is what made the seam obvious: answering the blocker question correctly meant
reading the ledger exactly the way `project_control.py accept()` reads it, and
that is control-plane knowledge rather than probe machinery.

`recovery_probes.py` re-exports every name here, so every caller and test that
imported them from there is unchanged.
"""
from __future__ import annotations

import json
import pathlib
import re
from typing import Any, Mapping

from .probe_result import ProbeResult, fail_probe, ok_probe, unknown_probe

#: Task statuses in which a packet actually confers working authority. Same set
#: `policy.TaskAuthority.from_packet` uses for `active`, referenced rather than
#: restated so the two can never drift apart.
WORKING_STATUSES: frozenset[str] = frozenset({"in_progress", "claimed", "awaiting_gate"})


def probe_task_authority(*, packet: Mapping[str, Any], repo_root: str,
                         packet_path: str = "") -> ProbeResult:
    """The packet confers live authority AND the ledger agrees it does.

    The packet on disk is the supervisor's authority source (never a model's
    description of the task), but a packet copy can be stale. The LEDGER entry
    under `project-control/tasks/<task_id>.json` is the control plane's record,
    so this requires both to exist and to agree on the task id and status, and
    requires that status to be one that actually confers work. Whether anything
    BLOCKS the task is a separate question with a separate authority - see
    `open_blockers_for`.
    """
    step = "task_authority"
    task_id = str(packet.get("task_id", "") or "")
    if not task_id:
        return fail_probe(step, "packet_without_task_id",
                          f"the task packet at {packet_path or '<unnamed>'} names no "
                          f"task_id; a packet that does not say which task it is confers "
                          f"no authority")
    status = str(packet.get("status", "") or "")
    if status not in WORKING_STATUSES:
        return fail_probe(step, "task_not_active",
                          f"task {task_id} is {status!r}; a supervised run needs a status "
                          f"that confers work ({sorted(WORKING_STATUSES)})",
                          task_id=task_id, status=status)
    ledger_path = pathlib.Path(repo_root) / "project-control" / "tasks" / f"{task_id}.json"
    if not ledger_path.is_file():
        return unknown_probe(step, "ledger_record_missing",
                             f"no ledger record at {ledger_path}; the packet's claim to "
                             f"authority cannot be corroborated against the control plane, "
                             f"and an uncorroborated authority claim is never assumed true",
                             task_id=task_id, ledger_path=str(ledger_path))
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return unknown_probe(step, "ledger_record_unreadable",
                             f"the ledger record {ledger_path} could not be read ({exc}); "
                             f"an unreadable authority record fails closed",
                             task_id=task_id)
    if str(ledger.get("task_id", "")) != task_id:
        return fail_probe(step, "ledger_task_id_mismatch",
                          f"the ledger record at {ledger_path} names task "
                          f"{ledger.get('task_id')!r}, not {task_id!r}", task_id=task_id)
    ledger_status = str(ledger.get("status", "") or "")
    if ledger_status != status:
        return fail_probe(step, "ledger_status_mismatch",
                          f"the packet says task {task_id} is {status!r} and the ledger "
                          f"says {ledger_status!r}; the supervisor never picks the more "
                          f"permissive of two disagreeing authority records",
                          task_id=task_id, packet_status=status,
                          ledger_status=ledger_status)
    open_blockers, blocker_error = open_blockers_for(repo_root, task_id)
    if blocker_error:
        return unknown_probe(step, "blockers_unreadable",
                             f"the control plane's blocker records could not be read "
                             f"({blocker_error}); an unreadable blocker set is never read "
                             f"as 'nothing is blocking'", task_id=task_id)
    if open_blockers:
        return fail_probe(step, "task_blocked",
                          f"task {task_id} is named by {len(open_blockers)} OPEN blocker "
                          f"record(s) {open_blockers}; a blocked task confers no authority "
                          f"to continue", task_id=task_id, blockers=open_blockers)
    return ok_probe(step,
                    f"task {task_id} is {status!r} in both the packet and the ledger, and "
                    f"no open blocker record names it", task_id=task_id, status=status)


def open_blockers_for(repo_root: str, task_id: str) -> tuple[list[str], str]:
    """OPEN blocker ids naming `task_id`, read the way `accept()` reads them.

    C8 (G3 I-1). This used to read the TASK RECORD's own `blockers` list, which
    `tools/project_control.py` initialises to `[]` at creation and then never
    appends to or prunes - it is free-form historical annotation, not authority.
    Two live consequences, wrong in opposite directions: `M0-T019.json` is
    `accepted` while carrying `["B-017"]` and `B-017` is RESOLVED, so that task
    could never be supervised again; and an OPEN blocker naming a task did not
    stop `start` at all, because nothing read `blockers/`. The probe asserted "no
    unresolved blockers" from a source that could not establish it - the same
    shape of defect this whole task exists to fix.

    The authority is `project-control/blockers/B-*.json` with `status` in
    ("open", ""), matched against the task id exactly as `_blocker_references`
    does (`project_control.py:1176`): word-bounded, either the `affects` list or
    the `detail` text, and a base id also matches its rework mentions. That last
    part is deliberately conservative in the same direction the control plane
    chose - it can only block, never permit.

    Returns `(open_blocker_ids, error)`. A non-empty error means the set is
    UNDETERMINED and the caller must fail closed.
    """
    directory = pathlib.Path(repo_root) / "project-control" / "blockers"
    if not directory.is_dir():
        return [], ""
    try:
        paths = sorted(directory.glob("B-*.json"))
    except OSError as exc:
        return [], f"{type(exc).__name__}: {exc}"
    naming: list[str] = []
    for path in paths:
        try:
            record = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            return [], f"{path.name} is unreadable ({exc})"
        if not isinstance(record, Mapping):
            return [], f"{path.name} is not a blocker record"
        if str(record.get("status", "") or "").lower() not in ("open", ""):
            continue
        affects = record.get("affects") or []
        parts = ([str(x) for x in affects] if isinstance(affects, list)
                 else [str(affects)])
        parts.append(str(record.get("detail") or ""))
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(task_id)}(?!\d)", "\n".join(parts)):
            naming.append(str(record.get("blocker_id") or path.stem))
    return naming, ""

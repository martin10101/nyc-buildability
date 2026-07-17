#!/usr/bin/env python3
"""Deterministic task/gate/checkpoint control plane for Claude agents (ADR-005).

Hardened per owner code-audit directive 2026-07-17 P0 (task M0-T014).

IDENTITY IS PROCEDURAL, NOT CRYPTOGRAPHIC
    --agent and --reviewer are caller-provided labels. This tool cannot verify
    who actually invoked it; there is no authentication or signature. The
    enforcement model is procedural: per ADR-005 (2026-07-14) only the
    main-session orchestrator runs this CLI, after validating the underlying
    evidence. The validations below are integrity rails on top of that
    procedure, not a substitute for it.

GATE CLASSES (structural; no bypass flag exists)
    self_check      G2            The producer's own scenario evidence,
                                  recorded by the orchestrator. Reviewer must
                                  be exactly "orchestrator"; the record stores
                                  role="self_check" honestly. A self_check
                                  record can NEVER satisfy an independent gate.
    administrative  G0, G7        Definition-of-ready / release decisions,
                                  recorded by the orchestrator (reviewer must
                                  be exactly "orchestrator"); role =
                                  "administrative".
    independent     G1 G3 G4 G5 G6  Reviewer must be listed in the task's
                                  reviewer_agents AND differ from
                                  producer_agent; role="independent_review".

TASK LIFECYCLE (docs/GATES_AND_CHECKPOINTS.md)
    backlog -> ready -> claimed -> in_progress -> self_check -> awaiting_gate
    -> accepted, plus awaiting_gate -> rework -> in_progress, any active
    state -> blocked, superseded work -> canceled.
    The `progress` subcommand accepts only the explicit transition enum in
    PROGRESS_TRANSITIONS. It can NEVER set `accepted` (only `accept` can),
    never sets `claimed` (only `claim` can), and never sets `awaiting_gate`
    from the forward chain (only `submit`/`gate` do; the unblock path
    blocked -> awaiting_gate is the one progress exception). `accepted` and
    `canceled` are terminal: no subcommand modifies a terminal task.

ACCEPT PRECONDITIONS (all required)
    1. --agent orchestrator (procedural label, see above);
    2. task status == awaiting_gate;
    3. every required gate has a PASS record, and for independent gates the
       record must not be a self_check record and its reviewer must differ
       from producer_agent;
    4. every dependency task is accepted;
    5. zero open blocker records in project-control/blockers/*.json
       (status == "open", or missing status = fail-closed) referencing the
       task id in their affects/detail fields.

CONTAINMENT
    Task ids must match ^M\\d+-T\\d{3}(-R\\d+)?$ — derived from the ledger
    population at hardening time (M0-T000..M2-T004 plus rework id
    M0-T005-R1; 30/30 files match). Report paths must be relative,
    traversal-free, and normalize to inside project-control/reports/ (bare
    filenames are interpreted there); absolute paths, drive letters, UNC
    paths, and ".." are rejected. Gate ids are restricted to G0..G7 and
    checkpoint ids to safe filename characters, so no argument can address a
    file outside the approved directories.

BACKWARD COMPATIBILITY
    Validation applies on WRITE only. Stored history (21 accepted tasks,
    including G2/G0 gate records with reviewer "orchestrator" and no role
    field, dependencies stored as null, blocker statuses resolved/
    resolved_temporary/closed, report_file values with backslashes or legacy
    locations) is never retro-rejected on read or at accept time. Gate
    records without a role field are treated as pre-hardening history.

ATOMIC WRITES
    Every JSON write serializes first, writes to a unique temp file in the
    destination directory, then os.replace()s it into place (atomic on POSIX
    and Windows; transient Windows sharing violations are retried). An
    interrupted write leaves the previous valid file intact. Concurrent
    invocations never corrupt a file; the last writer wins (no merge).
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, re, sys, tempfile, time
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
PC = ROOT / "project-control"

TASK_ID_RE = re.compile(r"^M\d+-T\d{3}(-R\d+)?$")
CHECKPOINT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")

STATUSES = ("backlog", "ready", "claimed", "in_progress", "self_check",
            "awaiting_gate", "rework", "blocked", "accepted", "canceled")
TERMINAL_STATUSES = frozenset({"accepted", "canceled"})

# Explicit transition enum for the `progress` subcommand (see docstring).
# A missing or identical --status is a message-only update and always legal
# on a non-terminal task.
PROGRESS_TRANSITIONS = {
    "backlog":       {"ready", "blocked", "canceled"},
    "ready":         {"blocked", "canceled"},
    "claimed":       {"in_progress", "blocked", "canceled"},
    "in_progress":   {"self_check", "blocked", "canceled"},
    "self_check":    {"blocked", "canceled"},
    "awaiting_gate": {"rework", "blocked", "canceled"},
    "rework":        {"in_progress", "blocked", "canceled"},
    "blocked":       {"backlog", "ready", "in_progress", "awaiting_gate", "canceled"},
    "accepted":      set(),
    "canceled":      set(),
}

GATE_IDS = ("G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7")
SELF_CHECK_GATES = frozenset({"G2"})
ADMINISTRATIVE_GATES = frozenset({"G0", "G7"})
INDEPENDENT_GATES = frozenset({"G1", "G3", "G4", "G5", "G6"})

CLAIMABLE_STATUSES = frozenset({"ready", "rework"})
SUBMITTABLE_STATUSES = frozenset({"claimed", "in_progress", "self_check", "rework"})


def now(): return dt.datetime.now(dt.timezone.utc).isoformat()


def load(path, attempts: int = 20, delay: float = 0.05):
    """JSON read with bounded retries: on Windows a concurrent os.replace of
    the same file can surface as a transient PermissionError for readers."""
    for i in range(attempts):
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except PermissionError:
            if i == attempts - 1:
                raise
            time.sleep(delay)


def _replace_with_retry(src: str, dst: str, attempts: int = 20, delay: float = 0.05):
    """os.replace with bounded retries for transient Windows sharing violations."""
    for i in range(attempts):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i == attempts - 1:
                raise
            time.sleep(delay)


def save(path: Path, data: dict):
    """Atomic JSON write: serialize, write a unique temp file in the same
    directory, os.replace into place. On any failure the previous file is
    left intact and the temp file is removed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now()
    payload = json.dumps(data, indent=2, sort_keys=False) + "\n"
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp",
                                    dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload)
        _replace_with_retry(tmp_name, str(path))
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def fail(msg: str) -> int:
    print(msg, file=sys.stderr)
    return 2


def valid_task_id(task_id: str) -> bool:
    return bool(TASK_ID_RE.fullmatch(task_id or ""))


def task_path(task_id):
    if not valid_task_id(task_id):
        # Never build a filesystem path from an unvalidated id.
        raise ValueError(f"invalid task id: {task_id!r}")
    return PC / "tasks" / f"{task_id}.json"


def report_path(task_id): return PC / "reports" / f"{task_id}.json"


def validate_report_arg(raw: str):
    """Validate a --report argument. Returns (posix_relative_path, abs_path,
    error). The path must be relative, contain no '.'/'..' components, and
    normalize to inside project-control/reports/. A bare filename is
    interpreted as project-control/reports/<name>. Both '/' and '\\' are
    treated as separators so Windows-style escapes cannot slip through on
    POSIX. Absolute, drive-letter (including drive-relative 'C:x'), and UNC
    paths are rejected."""
    if not raw or not raw.strip():
        return None, None, "Report path is empty."
    w = PureWindowsPath(raw)
    if w.drive or w.root or PurePosixPath(raw).is_absolute():
        return None, None, f"Report path must be relative, not absolute/drive/UNC: {raw!r}"
    parts = [p for p in re.split(r"[\\/]+", raw) if p]
    if any(p in (".", "..") for p in parts):
        return None, None, f"Report path may not contain '.' or '..' components: {raw!r}"
    if not parts:
        return None, None, "Report path is empty."
    if len(parts) == 1:
        parts = ["project-control", "reports", parts[0]]
    if len(parts) < 3 or parts[0] != "project-control" or parts[1] != "reports":
        return None, None, f"Report path must be inside project-control/reports/: {raw!r}"
    abs_path = ROOT.joinpath(*parts)
    reports_root = (PC / "reports").resolve()
    try:
        contained = abs_path.resolve().is_relative_to(reports_root)
    except OSError:
        contained = False
    if not contained:
        return None, None, f"Report path escapes project-control/reports/: {raw!r}"
    return "/".join(parts), abs_path, None


def load_task(task_id: str):
    """Returns (task, path, error)."""
    if not valid_task_id(task_id):
        return None, None, (f"Invalid task id {task_id!r}: must match "
                            f"{TASK_ID_RE.pattern} (ledger convention, "
                            f"e.g. M0-T014 or M0-T005-R1).")
    p = task_path(task_id)
    if not p.exists():
        return None, None, f"Unknown task: {task_id}"
    return load(p), p, None


def sync_state():
    """Recompute state.json task rosters from the tasks directory so the
    state file never drifts from the authoritative task packets."""
    sp = PC / "state.json"
    if not sp.exists():
        return
    state = load(sp)
    tasks = [load(p) for p in sorted((PC / "tasks").glob("*.json"))]
    state["accepted_tasks"] = [t["task_id"] for t in tasks if t.get("status") == "accepted"]
    state["active_tasks"] = [t["task_id"] for t in tasks if t.get("status") in
                             ("claimed", "in_progress", "self_check", "awaiting_gate", "rework")]
    state["blocked_tasks"] = [t["task_id"] for t in tasks if t.get("status") == "blocked"]
    state["failed_gates"] = sorted(
        gp.stem for gp in (PC / "gates").glob("*-G*.json")
        if load(gp).get("result") == "FAIL")
    save(sp, state)


def init(_):
    for d in ["tasks", "reports", "gates", "checkpoints", "blockers"]:
        (PC / d).mkdir(parents=True, exist_ok=True)
    required = [PC / "master_plan.json", PC / "state.json", PC / "config.json"]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("Missing control files:\n" + "\n".join(missing), file=sys.stderr)
        return 2
    print("Project control plane ready.")
    return 0


def new_task(a):
    if not valid_task_id(a.task_id):
        return fail(f"Invalid task id {a.task_id!r}: must match {TASK_ID_RE.pattern} "
                    f"(ledger convention, e.g. M0-T014 or M0-T005-R1).")
    deps = [x for x in (a.depends or "").split(",") if x]
    bad = [d for d in deps if not valid_task_id(d)]
    if bad:
        return fail(f"Invalid dependency id(s): {', '.join(bad)} "
                    f"(must match {TASK_ID_RE.pattern})")
    p = task_path(a.task_id)
    if p.exists():
        return fail(f"Task exists: {a.task_id}")
    config = load(PC / "config.json")
    gates = a.gates.split(",") if a.gates else config["required_gates_by_task_type"].get(
        a.task_type, ["G0", "G2", "G3", "G4"])
    reviewers = [x for x in (a.reviewers or "").split(",") if x]
    data = {
        "task_id": a.task_id, "title": a.title, "task_type": a.task_type,
        "milestone_id": a.milestone, "objective": a.objective,
        "business_reason": a.business_reason or "", "inputs": [], "outputs": [],
        "dependencies": deps, "allowed_paths": [], "forbidden_paths": [],
        "acceptance_scenarios": [], "required_gates": gates, "producer_agent": None,
        "reviewer_agents": reviewers, "status": "backlog", "progress_percent": 0,
        "risks": [], "blockers": [], "created_at": now(), "updated_at": now(),
    }
    save(p, data)
    print(p.relative_to(ROOT))
    return 0


def claim(a):
    t, p, err = load_task(a.task_id)
    if err:
        return fail(err)
    if t.get("status") in TERMINAL_STATUSES:
        return fail(f"Task {a.task_id} is terminal ({t['status']}); it cannot be claimed.")
    if t.get("status") not in CLAIMABLE_STATUSES:
        return fail(f"Cannot claim from status {t.get('status')!r}: claim requires "
                    f"{sorted(CLAIMABLE_STATUSES)} (G0 readiness moves backlog to ready).")
    t.update({"producer_agent": a.agent, "worktree": a.worktree,
              "status": "claimed", "progress_percent": 10})
    save(p, t)
    sync_state()
    print(f"Claimed {a.task_id} by {a.agent}")
    return 0


def progress(a):
    t, p, err = load_task(a.task_id)
    if err:
        return fail(err)
    cur = t.get("status")
    if cur in TERMINAL_STATUSES:
        return fail(f"Task {a.task_id} is terminal ({cur}); progress may not modify it.")
    if not 0 <= a.percent <= 99:
        return fail("Percent must be 0-99. Only orchestrator acceptance may set 100%.")
    target = a.status
    if target == "accepted":
        # Unreachable via argparse choices; kept as defense in depth.
        return fail("progress can never set 'accepted'; only the accept subcommand can.")
    if target and target != cur:
        if target == "claimed":
            return fail("'claimed' is set only by the claim subcommand.")
        allowed = PROGRESS_TRANSITIONS.get(cur, set())
        if target not in allowed:
            return fail(f"Illegal transition {cur!r} -> {target!r}. Allowed from {cur!r}: "
                        f"{sorted(allowed) or 'none'} (lifecycle per "
                        f"docs/GATES_AND_CHECKPOINTS.md; awaiting_gate is entered via "
                        f"submit/gate, accepted via accept).")
        t["status"] = target
    t["progress_percent"] = a.percent
    t.setdefault("progress_log", []).append(
        {"at": now(), "agent": a.agent, "percent": a.percent,
         "status": t.get("status"), "message": a.message})
    save(p, t)
    sync_state()
    print(f"Updated {a.task_id} to {a.percent}%")
    return 0


def submit(a):
    t, p, err = load_task(a.task_id)
    if err:
        return fail(err)
    cur = t.get("status")
    if cur in TERMINAL_STATUSES:
        return fail(f"Task {a.task_id} is terminal ({cur}); submit may not modify it.")
    if cur not in SUBMITTABLE_STATUSES:
        return fail(f"Cannot submit from status {cur!r}: submit requires "
                    f"{sorted(SUBMITTABLE_STATUSES)}.")
    rel, rp, rerr = validate_report_arg(a.report)
    if rerr:
        return fail(rerr)
    if not rp.exists():
        return fail(f"Report file missing: {rel}")
    report = {"task_id": a.task_id, "producer_agent": a.agent, "report_file": rel,
              "submitted_at": now(), "requested_status": a.requested_status}
    save(report_path(a.task_id), report)
    if a.requested_status == "awaiting_gate":
        t["status"] = "awaiting_gate"
        t["progress_percent"] = 85
    elif a.requested_status == "blocked":
        t["status"] = "blocked"
    else:
        t["status"] = "rework"
    save(p, t)
    sync_state()
    print(f"Submitted {a.task_id}: {a.requested_status}")
    return 0


def gate(a):
    t, p, err = load_task(a.task_id)
    if err:
        return fail(err)
    cur = t.get("status")
    if cur in TERMINAL_STATUSES:
        return fail(f"Task {a.task_id} is terminal ({cur}); gates may not be recorded on it.")
    producer = t.get("producer_agent")
    # Structural gate classes. Every gate id has exactly one class and one
    # validation rule; there is no bypass flag or default-permit path.
    if a.gate_id in SELF_CHECK_GATES:
        if a.reviewer != "orchestrator":
            return fail(f"{a.gate_id} is the producer self-check gate: it is recorded by "
                        f"the orchestrator (role 'self_check'), not by {a.reviewer!r}. "
                        f"It never counts as independent review.")
        role = "self_check"
    elif a.gate_id in ADMINISTRATIVE_GATES:
        if a.reviewer != "orchestrator":
            return fail(f"{a.gate_id} is recorded by the orchestrator (readiness/release "
                        f"decision per ADR-005), not by {a.reviewer!r}.")
        if producer and producer == a.reviewer:
            return fail("Producer cannot record an administrative gate on its own task.")
        role = "administrative"
    else:  # INDEPENDENT_GATES
        if producer and a.reviewer == producer:
            return fail("Producer cannot independently gate own task.")
        reviewers = t.get("reviewer_agents") or []
        if not reviewers:
            return fail(f"Task {a.task_id} has no reviewer_agents; an independent gate "
                        f"({a.gate_id}) cannot be recorded until the packet names reviewers.")
        if a.reviewer not in reviewers:
            return fail(f"Reviewer {a.reviewer!r} is not in this task's reviewer_agents "
                        f"{reviewers}; independent gate {a.gate_id} rejected.")
        role = "independent_review"
    rel, rp, rerr = validate_report_arg(a.report)
    if rerr:
        return fail(rerr)
    if not rp.exists():
        return fail(f"Gate report missing: {rel}")
    gp = PC / "gates" / f"{a.task_id}-{a.gate_id}.json"
    record = {"task_id": a.task_id, "gate_id": a.gate_id, "reviewer": a.reviewer,
              "role": role, "result": a.result, "report_file": rel, "reviewed_at": now()}
    if gp.exists():
        prev = load(gp)
        hist = prev.pop("history", [])
        hist.append({k: prev.get(k) for k in
                     ("reviewer", "role", "result", "report_file", "reviewed_at")})
        record["history"] = hist
    save(gp, record)
    # Status effects are deliberately narrow: gates recorded outside the
    # states below leave the task status untouched (evidence only).
    if a.result == "FAIL":
        if cur == "awaiting_gate":
            t["status"] = "rework"
    elif a.result == "BLOCKED":
        if cur in ("claimed", "in_progress", "self_check", "awaiting_gate", "rework"):
            t["status"] = "blocked"
    else:  # PASS
        if a.gate_id == "G0" and cur in ("backlog", "rework"):
            t["status"] = "ready"
            t["progress_percent"] = max(t.get("progress_percent", 0), 5)
        elif cur == "awaiting_gate":
            passed = set()
            for x in (PC / "gates").glob(f"{a.task_id}-G*.json"):
                rec = load(x)
                if rec.get("result") == "PASS":
                    passed.add(rec.get("gate_id"))
            required = set(t.get("required_gates") or [])
            t["progress_percent"] = 95 if required.issubset(passed) else max(
                t.get("progress_percent", 0), 85)
    save(p, t)
    sync_state()
    print(f"Recorded {a.gate_id} {a.result} for {a.task_id}")
    return 0


def _blocker_references(task_id: str, blocker: dict) -> bool:
    """True when the task id appears (word-bounded) in affects or detail.
    A base id also matches its rework mentions (M0-T005 matches M0-T005-R1):
    deliberately conservative — it can only block acceptance, never allow it."""
    parts = []
    affects = blocker.get("affects") or []
    if isinstance(affects, list):
        parts.extend(str(x) for x in affects)
    else:
        parts.append(str(affects))
    parts.append(str(blocker.get("detail") or ""))
    haystack = "\n".join(parts)
    return bool(re.search(rf"(?<![A-Za-z0-9]){re.escape(task_id)}(?!\d)", haystack))


def accept(a):
    if a.agent != "orchestrator":
        return fail("Only orchestrator may accept.")
    t, p, err = load_task(a.task_id)
    if err:
        return fail(err)
    reasons = []
    if t.get("status") != "awaiting_gate":
        reasons.append(f"status is {t.get('status')!r}, not 'awaiting_gate'")
    # Gate satisfaction. Validation-on-write means stored history is
    # tolerated here: records without a role field are pre-hardening records.
    records = {}
    for x in (PC / "gates").glob(f"{a.task_id}-G*.json"):
        rec = load(x)
        records[rec.get("gate_id")] = rec
    producer = t.get("producer_agent")
    for g in sorted(set(t.get("required_gates") or [])):
        rec = records.get(g)
        if not rec or rec.get("result") != "PASS":
            reasons.append(f"required gate {g} has no PASS record")
            continue
        if g in INDEPENDENT_GATES:
            role = rec.get("role")
            if role == "self_check":
                reasons.append(f"gate {g} requires independent review; a self_check "
                               f"record can never satisfy it")
            elif role is not None and role != "independent_review":
                reasons.append(f"gate {g} requires independent review; record role "
                               f"{role!r} does not satisfy it")
            elif producer and rec.get("reviewer") == producer:
                reasons.append(f"gate {g} was recorded by the producer "
                               f"({producer!r}); independent review required")
    for dep in (t.get("dependencies") or []):
        if not valid_task_id(dep):
            reasons.append(f"dependency {dep!r} is not a valid task id")
            continue
        dp = task_path(dep)
        if not dp.exists():
            reasons.append(f"dependency {dep} has no task file")
            continue
        ds = load(dp).get("status")
        if ds != "accepted":
            reasons.append(f"dependency {dep} is {ds!r}, not accepted")
    bdir = PC / "blockers"
    if bdir.exists():
        for bp in sorted(bdir.glob("*.json")):
            try:
                b = load(bp)
            except (ValueError, OSError) as e:
                reasons.append(f"blocker file {bp.name} is unreadable ({e}); fail-closed")
                continue
            status_value = str(b.get("status") or "").strip().lower()
            blocking = status_value in ("open", "")
            if blocking and _blocker_references(a.task_id, b):
                reasons.append(f"open blocker {b.get('blocker_id', bp.name)} "
                               f"references this task")
    if reasons:
        return fail(f"Cannot accept {a.task_id}:\n" + "\n".join(f"- {r}" for r in reasons))
    t["status"] = "accepted"
    t["progress_percent"] = 100
    t["accepted_by"] = a.agent
    t["accepted_at"] = now()
    save(p, t)
    sync_state()
    print(f"Accepted {a.task_id}")
    return 0


def checkpoint(a):
    cp_id = a.checkpoint_id
    if not CHECKPOINT_ID_RE.fullmatch(cp_id or "") or ".." in cp_id:
        return fail(f"Invalid checkpoint id {cp_id!r}: letters, digits, '.', '_', '-' "
                    f"only (no path separators or traversal).")
    state = load(PC / "state.json")
    cp = {"checkpoint_id": cp_id, "timestamp": now(), "commit": a.commit,
          "branch": a.branch, "active_milestone": state.get("current_milestone"),
          "summary": a.summary}
    save(PC / "checkpoints" / f"{cp_id}.json", cp)
    state["last_checkpoint"] = cp_id
    save(PC / "state.json", state)
    print(f"Checkpoint {cp_id}")
    return 0


def status(_):
    plan = load(PC / "master_plan.json")
    tasks = [load(p) for p in sorted((PC / "tasks").glob("*.json"))]
    counts = {}
    for t in tasks:
        counts[t.get("status")] = counts.get(t.get("status"), 0) + 1
    print(json.dumps({
        "current_milestone": plan.get("current_milestone"),
        "milestones": plan.get("milestones", []),
        "task_counts": counts,
        "tasks": [{"id": t.get("task_id"), "status": t.get("status"),
                   "progress": t.get("progress_percent"),
                   "agent": t.get("producer_agent")} for t in tasks],
    }, indent=2))
    return 0


EPILOG = """identity note: --agent and --reviewer are caller-provided labels, not
cryptographic or authenticated identity. Enforcement is procedural (ADR-005:
the orchestrator alone runs this CLI) plus the structural validations this
tool applies: explicit progress-transition enum (progress can never set
'accepted'), gate classes (G2 self_check recorded by the orchestrator and
never satisfying an independent gate; G1/G3/G4/G5/G6 requiring a listed
reviewer different from the producer; G0/G7 administrative), accept
preconditions (awaiting_gate + all required gates PASS + dependencies
accepted + zero open blockers referencing the task), task-id/report-path
containment, and atomic writes. Validation applies on write only; stored
ledger history is never retro-rejected."""


def main():
    p = argparse.ArgumentParser(
        description=("Deterministic project-control CLI (ADR-005): tasks, gates, "
                     "checkpoints. See module docstring for the enforcement model."),
        epilog=EPILOG, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("init")
    x.set_defaults(fn=init)
    x = sp.add_parser("new-task")
    for n, kw in [("--task-id", {"required": True}), ("--title", {"required": True}),
                  ("--task-type", {"required": True}), ("--milestone", {"required": True}),
                  ("--objective", {"required": True}), ("--business-reason", {}),
                  ("--depends", {}), ("--gates", {}),
                  ("--reviewers", {"help": "comma-separated reviewer_agents roster"})]:
        x.add_argument(n, **kw)
    x.set_defaults(fn=new_task)
    x = sp.add_parser("claim")
    x.add_argument("--task-id", required=True)
    x.add_argument("--agent", required=True,
                   help="caller-provided producer label (not authenticated identity)")
    x.add_argument("--worktree", required=True)
    x.set_defaults(fn=claim)
    x = sp.add_parser("progress")
    x.add_argument("--task-id", required=True)
    x.add_argument("--agent", required=True,
                   help="caller-provided label (not authenticated identity)")
    x.add_argument("--percent", type=int, required=True,
                   help="0-99; 100 is set only by accept")
    x.add_argument("--status", choices=[s for s in STATUSES if s != "accepted"],
                   help="target status; must be a legal lifecycle transition "
                        "(accepted is never settable here)")
    x.add_argument("--message", required=True)
    x.set_defaults(fn=progress)
    x = sp.add_parser("submit")
    x.add_argument("--task-id", required=True)
    x.add_argument("--agent", required=True,
                   help="caller-provided producer label (not authenticated identity)")
    x.add_argument("--report", required=True,
                   help="relative path inside project-control/reports/")
    x.add_argument("--requested-status",
                   choices=["awaiting_gate", "blocked", "needs_split"], required=True)
    x.set_defaults(fn=submit)
    x = sp.add_parser("gate")
    x.add_argument("--task-id", required=True)
    x.add_argument("--gate-id", choices=list(GATE_IDS), required=True)
    x.add_argument("--reviewer", required=True,
                   help="caller-provided reviewer label (not authenticated identity); "
                        "validated against the gate class rules")
    x.add_argument("--result", choices=["PASS", "FAIL", "BLOCKED"], required=True)
    x.add_argument("--report", required=True,
                   help="relative path inside project-control/reports/")
    x.set_defaults(fn=gate)
    x = sp.add_parser("accept")
    x.add_argument("--task-id", required=True)
    x.add_argument("--agent", required=True,
                   help="must be 'orchestrator' (procedural label per ADR-005)")
    x.set_defaults(fn=accept)
    x = sp.add_parser("checkpoint")
    x.add_argument("--checkpoint-id", required=True)
    x.add_argument("--commit", required=True)
    x.add_argument("--branch", required=True)
    x.add_argument("--summary", required=True)
    x.set_defaults(fn=checkpoint)
    x = sp.add_parser("status")
    x.set_defaults(fn=status)
    a = p.parse_args()
    raise SystemExit(a.fn(a))


if __name__ == "__main__":
    main()

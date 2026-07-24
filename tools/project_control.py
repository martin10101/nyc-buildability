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
    A task leaving `blocked` for any active status (every target except
    `canceled`) must first carry a valid roster: a real producer_agent (not
    the reserved "orchestrator") and at least one reviewer in reviewer_agents
    that is neither empty, "orchestrator", nor the producer. A blocked task
    with an empty/invalid roster (e.g. legacy M0-T007/M0-T008) cannot re-enter
    the workflow until the orchestrator amends its packet (M0-T014 G3 OBS-3).

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

# Reserved control-plane identity. The orchestrator may author an explicitly
# classified G2/self_check record and run G0/G7 administrative gates (reviewer
# == "orchestrator" is REQUIRED there), but it may NEVER appear in a task's
# reviewer_agents roster: an independent gate (G1/G3/G4/G5/G6) recorded by the
# orchestrator would collapse producer and independent-reviewer authority.
# Enforced on WRITE only (M0-T014 G5 defect D1); stored history is never
# retro-rejected.
RESERVED_ORCHESTRATOR = "orchestrator"

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


# --------------------------------------------------------------------------
# Owner Directive Compliance System (directive D-001).
#
# These checks are ADDITIVE and gated on a per-packet regime stamp so no legacy
# or in-flight task is affected (correction 4: machine-enforceable migration, not
# created_at). project_control.py remains the SOLE task/gate/acceptance authority
# (D-001-R023/R118): the checks only ADD reasons to accept()'s existing list and add
# fail-closed guards to claim/submit; there is no bypass/override flag. All directive
# resolution is delegated to the shared, read-only tools/directive_registry.py so the
# CLI and tools/validate_directive_compliance.py can never diverge (correction 1).
# --------------------------------------------------------------------------

def _resolver():
    """Lazily import the shared directive resolver. Returns the module, or None if it
    is unavailable (older checkout). Callers fail closed for in-regime/governance work."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import directive_registry
        return directive_registry
    except Exception:
        return None


def _regime():
    """(enabled, version, effective_date, governance_paths) from config.json."""
    try:
        cfg = load(PC / "config.json")
    except (ValueError, OSError):
        return False, "", "", []
    r = cfg.get("directive_compliance_regime") or {}
    return (bool(r.get("enabled")), r.get("version", ""), r.get("effective_date", ""),
            list(r.get("governance_paths") or []))


def _task_in_regime(t: dict) -> bool:
    """A task is IN-REGIME when it carries an explicit regime stamp or directive_refs.
    Legacy/pre-regime tasks (neither) are grandfathered."""
    return bool(t.get("directive_regime_version")) or bool(t.get("directive_refs"))


# Volatile control-plane records excluded from the content-manifest so the frozen
# evidence identity guards the reviewable code/doc work product and does not churn on
# lifecycle bookkeeping. Registry integrity is enforced separately by the validator.
_MANIFEST_EXCLUDE_PREFIXES = ("project-control/",)

# Statuses at which a not-in-regime legacy task counts as "already active" and may finish
# its existing lifecycle without deadlock (D-001 amendment 3, Section 1). ready/backlog/
# rework/blocked are NOT here: they must enter the regime at their next claim.
_CONTINUATION_STATUSES = frozenset({"claimed", "in_progress", "self_check", "awaiting_gate"})


def _task_git_identity(reg_mod, t: dict, reviewed_sha=None):
    """Authoritative git-canonical reviewed content identity for a task's allowed_paths,
    excluding the volatile control-plane tree. Returns (identity, resolved_sha, error);
    fails closed (error != None) when `.` is not a git work tree, the reviewed SHA is
    unresolvable, or a relevant tracked file is dirty / a relevant file is untracked
    (D-001 amendment 3, Section 3). Submit, gate, and accept all call THIS one function."""
    return reg_mod.frozen_git_identity(
        list(t.get("allowed_paths") or []), reviewed_sha=reviewed_sha, root=ROOT,
        exclude_prefixes=_MANIFEST_EXCLUDE_PREFIXES, require_clean=True)


def _legacy_grandfather_check(t: dict, task_id: str):
    """For a NOT-in-regime task under an ENABLED regime at a continuation event
    (submit/accept): return an error string if it may NOT proceed as grandfathered, else
    None. Grandfathering requires (a) membership in the frozen migration manifest, (b) an
    unchanged material packet digest since baseline, and (c) an already-active continuation
    status. A missing/corrupt manifest or unavailable resolver fails closed. There is no
    bypass flag, suppression flag, or agent-selected exemption (D-001 amendment 3)."""
    reg_mod = _resolver()
    if reg_mod is None:
        return "directive resolver unavailable; legacy task cannot be validated (fail closed)."
    mm = reg_mod.load_migration_manifest()
    if mm.errors:
        return f"migration manifest unavailable/corrupt (fail closed): {mm.errors[0]}"
    if not mm.contains(task_id):
        return (f"task {task_id} is not in the frozen migration manifest (baseline "
                f"{(mm.baseline_sha or '?')[:12]}); it cannot be grandfathered by omitting the "
                f"regime stamp. Enter the regime with valid --directive-refs (fail closed).")
    if reg_mod.material_digest(t) != mm.digest_for(task_id):
        return (f"task {task_id} has a material amendment/replan since baseline (material "
                f"packet digest changed); grandfathering is invalidated. Enter the regime with "
                f"valid --directive-refs (fail closed).")
    if t.get("status") not in _CONTINUATION_STATUSES:
        return (f"task {task_id} in status {t.get('status')!r} is not an already-active legacy "
                f"task; it must enter the regime at its next claim with valid --directive-refs "
                f"(fail closed).")
    return None


def _path_touches(path: str, allowed: list) -> bool:
    p = str(path).rstrip("/")
    for a in allowed:
        ap = str(a).rstrip("/")
        if ap == p or ap.startswith(p + "/") or p.startswith(ap + "/"):
            return True
    return False


def _touches_governance(allowed_paths: list, governance_paths: list) -> bool:
    return any(_path_touches(g, allowed_paths) for g in governance_paths)


def _parse_directive_refs(raw: str):
    """Parse "D-001:ALL;D-002:D-002-R001,D-002-R002" into the directive_refs list.
    Returns (refs, error)."""
    refs = []
    for chunk in (raw or "").split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            return None, f"malformed --directive-refs entry {chunk!r} (expected DID:ALL or DID:RID,RID)"
        did, rest = chunk.split(":", 1)
        did = did.strip()
        rest = rest.strip()
        if rest.upper() == "ALL":
            refs.append({"directive_id": did, "requirement_ids": "ALL"})
        else:
            rids = [x.strip() for x in rest.split(",") if x.strip()]
            refs.append({"directive_id": did, "requirement_ids": rids})
    return refs, None


def _directive_claim_check(t: dict, agent: str):
    """Fail-closed guard run at claim. Returns an error string or None.
    Enforces (for in-regime tasks) valid directive references and (for any task whose
    allowed_paths touch governance/control-plane files) that a governance directive
    covers it (s19 / D-001-R024/R118)."""
    enabled, _version, _eff, gov_paths = _regime()
    in_regime = _task_in_regime(t)
    # The per-task in-regime enforcement stands even if the regime is globally toggled
    # off after a task was stamped (F5: uniform per-task gating, matching submit/gate/
    # accept — no fail-open re-claim). The governance-path guard is a regime feature
    # (it needs the configured governance_paths), so it is gated on `enabled`.
    touches_gov = enabled and _touches_governance(t.get("allowed_paths") or [], gov_paths)
    if not in_regime and not touches_gov:
        return None  # grandfathered legacy/pre-regime task, non-governance scope
    reg_mod = _resolver()
    if reg_mod is None:
        return ("directive resolver/registry unavailable; an in-regime or "
                "governance-scoped task cannot be claimed without reference "
                "verification (fail closed).")
    reg = reg_mod.load_registry()
    if touches_gov and not reg.covers_governance(t):
        return ("this task's allowed_paths touch governance/control-plane files but it "
                "cites no applicable active governance directive. Create/cite a governance "
                "directive scoped to this task before claiming (fail closed; s19 / D-001-R118).")
    if in_regime:
        ev = reg.evaluate_task_refs(t)
        if not ev["ok"]:
            return ("directive-compliance references invalid at claim:\n"
                    + "\n".join(f"  - {r}" for r in ev["reasons"]))
    return None


def _directive_submit_check(t: dict, evidence_map_arg, sha_arg):
    """For in-regime tasks: require an evidence map covering every applicable
    requirement, and stamp the frozen content-manifest identity. Returns (error, extra)
    where extra is merged into the report record."""
    reg_mod = _resolver()
    if reg_mod is None:
        return ("directive resolver unavailable; in-regime submit blocked (fail closed).", {})
    reg = reg_mod.load_registry()
    ev = reg.evaluate_task_refs(t)
    if not ev["ok"]:
        return ("directive-compliance references invalid at submit:\n"
                + "\n".join(f"  - {r}" for r in ev["reasons"]), {})
    applicable = set(ev["applicable_ids"])
    if not evidence_map_arg:
        return ("in-regime submit requires --evidence-map (JSON in project-control/reports/ "
                "mapping each applicable requirement id to evidence).", {})
    rel, ep, eerr = validate_report_arg(evidence_map_arg)
    if eerr:
        return (eerr, {})
    if not ep.exists():
        return (f"evidence map file missing: {rel}", {})
    try:
        emap = load(ep)
    except (ValueError, OSError) as e:
        return (f"evidence map is not valid JSON: {e}", {})
    covered = {k for k, v in (emap.get("requirements") or {}).items() if v}
    missing = sorted(applicable - covered)
    if missing:
        return (f"evidence map does not cover applicable requirement(s): {', '.join(missing)}", {})
    identity, resolved_sha, ierr = _task_git_identity(reg_mod, t, reviewed_sha=sha_arg)
    if ierr:
        return (f"in-regime submit content identity (fail closed): {ierr}", {})
    extra = {"evidence_map": rel, "content_manifest_sha256": identity,
             "reviewed_sha": resolved_sha,
             "applicable_requirements": sorted(applicable)}
    return (None, extra)


def _directive_accept_reasons(t: dict, task_id: str) -> list:
    """Reasons an in-regime task must NOT be accepted (appended to accept()'s list).
    Never a bypass: only adds reasons. Verifies references, git-canonical content-identity
    freshness, and full independent PER-TASK verification (directive_verification/v2)
    covering exactly the requirements APPLICABLE TO THIS TASK at the current identity
    (D-001 amendment 3, Sections 2+3)."""
    reasons = []
    reg_mod = _resolver()
    if reg_mod is None:
        return ["directive resolver unavailable; in-regime task cannot be accepted (fail closed)."]
    reg = reg_mod.load_registry()
    ev = reg.evaluate_task_refs(t)
    if not ev["ok"]:
        reasons.extend(f"directive refs: {r}" for r in ev["reasons"])
    identity, _resolved_sha, ierr = _task_git_identity(reg_mod, t)
    if ierr:
        return reasons + [f"content identity (fail closed): {ierr}"]
    applicable = ev["applicable_ids"]
    rep = None
    rp = report_path(task_id)
    if rp.exists():
        try:
            rep = load(rp)
        except (ValueError, OSError):
            rep = None
    if not rep or rep.get("content_manifest_sha256") != identity:
        reasons.append("frozen-evidence identity mismatch: the task's relevant contents "
                       "changed since submission (stale); re-submit and re-verify at the "
                       "new content identity before acceptance.")
    # Per-task verification: only requirements applicable to THIS task are evaluated for
    # THIS task's acceptance (one directive may govern several tasks independently). When a
    # task cites several directives, restrict the applicable set to EACH directive's own
    # requirement ids per iteration so one directive's rows are never treated as missing/
    # cross-task for another (G3 N1; a task may be governed by multiple directives).
    applicable_set = set(applicable)
    for ref in (t.get("directive_refs") or []):
        did = ref.get("directive_id") if isinstance(ref, dict) else None
        if not did:
            continue
        d = reg.get(did)
        did_applicable = applicable_set & (d.requirement_ids() if d else set())
        reasons.extend(reg.task_unresolved_requirements(did, task_id, did_applicable, identity))
    return reasons


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
    # --gates enum validation (M0-T014 G5 defect D2): every entry must be a
    # canonical gate id. Reject unknown names immediately, naming the offending
    # entry and the canonical enum, so a typo can never author a task whose
    # required_gates can never be satisfied.
    bad_gates = [g for g in gates if g not in GATE_IDS]
    if bad_gates:
        return fail(f"Invalid --gates entry(ies): {', '.join(bad_gates)}. "
                    f"Allowed gates are {', '.join(GATE_IDS)}.")
    reviewers = [x for x in (a.reviewers or "").split(",") if x]
    # Reserved-identity prohibition (M0-T014 G5 defect D1): the orchestrator may
    # never be a task reviewer. If it were rostered, an independent gate could be
    # recorded by the same identity that authors self_check/administrative
    # records, collapsing the producer/independent-review separation.
    if RESERVED_ORCHESTRATOR in reviewers:
        return fail(f"Reviewer {RESERVED_ORCHESTRATOR!r} is reserved and may not appear in "
                    f"reviewer_agents: the orchestrator records self_check (G2) and "
                    f"administrative (G0/G7) gates but can never satisfy an independent "
                    f"gate (G1/G3/G4/G5/G6). List an independent reviewer instead.")
    # Directive-compliance regime (D-001 amendment 3, Section 1): when the regime is
    # enabled every NEW task must carry valid --directive-refs. A brand-new task id can
    # never be in the frozen migration manifest (which is bound to the baseline commit),
    # so new-task WITHOUT refs fails closed; a missing/corrupt/inactive registry or a
    # missing/corrupt migration manifest also fails closed. There is no bypass flag.
    enabled, _rv, _re, _rg = _regime()
    if enabled:
        reg_mod = _resolver()
        if reg_mod is None:
            return fail("directive regime is enabled but the shared resolver is unavailable; "
                        "new-task fails closed.")
        reg = reg_mod.load_registry()
        if reg.errors or not reg.active_directives():
            return fail("directive regime is enabled but the registry is missing/corrupt/"
                        "inactive; new-task fails closed until it is healthy.")
        mm = reg_mod.load_migration_manifest()
        if mm.errors:
            return fail(f"directive regime is enabled but the migration manifest is unavailable/"
                        f"corrupt; new-task fails closed: {mm.errors[0]}")
        if not getattr(a, "directive_refs", None):
            return fail("directive regime is enabled: every new task must carry valid "
                        "--directive-refs (e.g. 'D-001:ALL'). new-task without them fails "
                        "closed (D-001 amendment 3, Section 1).")
    data = {
        "task_id": a.task_id, "title": a.title, "task_type": a.task_type,
        "milestone_id": a.milestone, "objective": a.objective,
        "business_reason": a.business_reason or "", "inputs": [], "outputs": [],
        "dependencies": deps, "allowed_paths": [], "forbidden_paths": [],
        "acceptance_scenarios": [], "required_gates": gates, "producer_agent": None,
        "reviewer_agents": reviewers, "status": "backlog", "progress_percent": 0,
        "risks": [], "blockers": [], "created_at": now(), "updated_at": now(),
    }
    # Directive-compliance regime (D-001): a new task created WITH --directive-refs is
    # born in-regime; without it the task is pre-regime/grandfathered (existing flow).
    if getattr(a, "directive_refs", None):
        refs, rerr = _parse_directive_refs(a.directive_refs)
        if rerr:
            return fail(rerr)
        data["directive_refs"] = refs
        enabled, version, _e, _g = _regime()
        if enabled:
            data["directive_regime_version"] = version
            data["directive_regime_entered_at"] = now()
        reg_mod = _resolver()
        if reg_mod is not None:
            ev = reg_mod.load_registry().evaluate_task_refs(data)
            if not ev["ok"]:
                return fail("directive references invalid for new task:\n"
                            + "\n".join(f"  - {r}" for r in ev["reasons"]))
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
    # Directive-compliance regime entry on (re)claim (D-001, correction 4): --directive-refs
    # stamps the task in-regime; then references are enforced fail-closed.
    if getattr(a, "directive_refs", None):
        refs, rerr = _parse_directive_refs(a.directive_refs)
        if rerr:
            return fail(rerr)
        t["directive_refs"] = refs
        enabled, version, _e, _g = _regime()
        if enabled:
            t["directive_regime_version"] = version
            t.setdefault("directive_regime_entered_at", now())
    # Regime entry is MANDATORY at claim/reclaim (D-001 amendment 3, Section 1): under an
    # enabled regime a task that is still not in-regime after any --directive-refs stamp
    # cannot be claimed as grandfathered. A previously-unstarted legacy task, and any
    # backlog/ready/rework/blocked legacy task at its next claim, must enter the regime
    # here (fail closed). The migration manifest never exempts claim.
    enabled, _rv, _re, _rg = _regime()
    if enabled and not _task_in_regime(t):
        return fail(f"Cannot claim {a.task_id}: the directive regime is enabled and this task is "
                    f"not in-regime. Claiming or reclaiming is a regime-entry event: pass valid "
                    f"--directive-refs (e.g. 'D-001:ALL') so the task enters the regime. A legacy "
                    f"task cannot be claimed as grandfathered (fail closed; D-001 amendment 3).")
    dcerr = _directive_claim_check(t, a.agent)
    if dcerr:
        return fail(f"Cannot claim {a.task_id}: {dcerr}")
    t.update({"producer_agent": a.agent, "worktree": a.worktree,
              "status": "claimed", "progress_percent": 10})
    save(p, t)
    sync_state()
    print(f"Claimed {a.task_id} by {a.agent}")
    return 0


def invalid_unblock_roster(task: dict):
    """Return an explanatory string when a task's packet does not carry a valid
    producer + independent-reviewer roster, else None.

    Blocked-task roster precondition (M0-T014 G3 OBS-3): a task in `blocked`
    status must not be able to re-enter the active workflow until its packet is
    amended with a real producer and at least one usable independent reviewer.
    A valid roster requires:
      - a non-empty producer_agent that is not the reserved orchestrator; and
      - at least one reviewer in reviewer_agents that is neither empty, the
        reserved orchestrator, nor equal to the producer (an independent gate
        recorded by such a reviewer would otherwise be impossible to satisfy).
    Enforced on WRITE only at the unblock transition; stored history untouched.
    """
    producer = (task.get("producer_agent") or "").strip()
    if not producer:
        return ("no producer_agent is set; amend the packet with a producer before "
                "unblocking.")
    if producer == RESERVED_ORCHESTRATOR:
        return (f"producer_agent is the reserved {RESERVED_ORCHESTRATOR!r}; amend the "
                f"packet with a real producer before unblocking.")
    reviewers = task.get("reviewer_agents") or []
    usable = [r for r in reviewers
              if r and r != RESERVED_ORCHESTRATOR and r != producer]
    if not usable:
        return ("reviewer_agents has no usable independent reviewer (must be non-empty "
                f"and contain a reviewer that is neither {RESERVED_ORCHESTRATOR!r} nor "
                f"the producer {producer!r}); amend the packet before unblocking.")
    return None


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
        # Blocked-task roster precondition (M0-T014 G3 OBS-3): leaving `blocked`
        # for any active status requires an amended, usable producer/reviewer
        # roster. `canceled` is exempt (a blocked task may always be abandoned).
        if cur == "blocked" and target != "canceled":
            roster_err = invalid_unblock_roster(t)
            if roster_err:
                return fail(f"Cannot unblock {a.task_id} ({cur!r} -> {target!r}): "
                            f"{roster_err} A blocked task cannot re-enter the workflow "
                            f"until the orchestrator amends its packet with a valid "
                            f"producer and independent-reviewer roster.")
        # Regime-entry guard (D-001 amendment 3, Section 1; G3 F1): a not-in-regime legacy
        # task under an ENABLED regime may not be laundered from a non-continuation status
        # (blocked/rework/backlog/ready) INTO a continuation status (in_progress/self_check/
        # awaiting_gate) via `progress`, which would slip it past the claim-time regime-entry
        # requirement and grandfather it at accept. Regime entry happens ONLY at claim
        # (with valid --directive-refs); this transition fails closed. `canceled` is exempt.
        enabled, _rv, _re, _rg = _regime()
        if (enabled and not _task_in_regime(t) and target != "canceled"
                and cur not in _CONTINUATION_STATUSES
                and target in _CONTINUATION_STATUSES):
            return fail(f"Cannot move {a.task_id} {cur!r} -> {target!r}: the directive regime "
                        f"is enabled and this legacy task is not in-regime. A blocked/rework/"
                        f"backlog/ready legacy task enters the regime at its next CLAIM (with "
                        f"valid --directive-refs), not via progress (fail closed; D-001 "
                        f"amendment 3, Section 1).")
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
    # In-regime submit (D-001): require an evidence map covering every applicable
    # requirement and stamp the git-canonical frozen content identity (Section 3). A
    # not-in-regime task under an enabled regime may only submit if it is grandfather-
    # eligible (in the frozen migration manifest, material-unchanged, already-active);
    # otherwise it must enter the regime (fail closed, D-001 amendment 3, Section 1).
    if _task_in_regime(t):
        serr, extra = _directive_submit_check(
            t, getattr(a, "evidence_map", None), getattr(a, "sha", None))
        if serr:
            return fail(serr)
        report.update(extra)
    else:
        enabled, _rv, _re, _rg = _regime()
        if enabled:
            gferr = _legacy_grandfather_check(t, a.task_id)
            if gferr:
                return fail(f"Cannot submit {a.task_id}: {gferr}")
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
        # Reserved-identity prohibition (M0-T014 G5 defect D1): the orchestrator
        # can never satisfy an independent gate, even if a legacy packet lists it
        # in reviewer_agents. Validated on WRITE only; stored gate history is
        # never retro-rejected (accept() tolerates legacy records).
        if a.reviewer == RESERVED_ORCHESTRATOR:
            return fail(f"Reviewer {RESERVED_ORCHESTRATOR!r} is reserved and cannot record an "
                        f"independent gate ({a.gate_id}): it records self_check (G2) and "
                        f"administrative (G0/G7) gates only. An independent reviewer "
                        f"(!= producer, listed in reviewer_agents) must record {a.gate_id}.")
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
    # In-regime gate (D-001): stamp the git-canonical content identity and reviewed SHA so
    # acceptance can detect stale post-review edits. Same shared identity implementation as
    # submit and accept (D-001 amendment 3, Sections 2+3); fail closed on identity error.
    if _task_in_regime(t):
        reg_mod = _resolver()
        if reg_mod is None:
            return fail(f"directive resolver unavailable; in-regime gate on {a.task_id} "
                        f"cannot be recorded (fail closed).")
        identity, resolved_sha, ierr = _task_git_identity(
            reg_mod, t, reviewed_sha=getattr(a, "sha", None))
        if ierr:
            return fail(f"Cannot record gate for in-regime {a.task_id}: content identity "
                        f"(fail closed): {ierr}")
        record["content_manifest_sha256"] = identity
        record["reviewed_sha"] = resolved_sha
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
    # Directive-compliance acceptance gate (D-001): for in-regime tasks, require valid
    # references, a matching git-canonical content identity, and full independent PER-TASK
    # verification at that identity. A not-in-regime task under an enabled regime is
    # accepted only if grandfather-eligible (in the frozen migration manifest, material-
    # unchanged, already-active); otherwise it must enter the regime. Only ADDS reasons.
    if _task_in_regime(t):
        reasons.extend(_directive_accept_reasons(t, a.task_id))
    else:
        enabled, _rv, _re, _rg = _regime()
        if enabled:
            gferr = _legacy_grandfather_check(t, a.task_id)
            if gferr:
                reasons.append(gferr)
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
                  ("--reviewers", {"help": "comma-separated reviewer_agents roster"}),
                  ("--directive-refs", {"help": "directive-compliance refs, e.g. "
                                        "'D-001:ALL' or 'D-001:D-001-R001,D-001-R002' "
                                        "(stamps the task in-regime; D-001)"})]:
        x.add_argument(n, **kw)
    x.set_defaults(fn=new_task)
    x = sp.add_parser("claim")
    x.add_argument("--task-id", required=True)
    x.add_argument("--agent", required=True,
                   help="caller-provided producer label (not authenticated identity)")
    x.add_argument("--worktree", required=True)
    x.add_argument("--directive-refs",
                   help="directive-compliance refs to stamp on (re)claim (D-001); "
                        "e.g. 'D-001:ALL'")
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
    x.add_argument("--evidence-map",
                   help="relative path in project-control/reports/ to a JSON evidence "
                        "map {\"requirements\": {\"D-001-R001\": [evidence...]}} "
                        "(required for in-regime tasks; D-001)")
    x.add_argument("--sha", help="reviewed head SHA (provenance) for in-regime tasks")
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
    x.add_argument("--sha", help="reviewed head SHA (provenance) stamped on in-regime gate records")
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

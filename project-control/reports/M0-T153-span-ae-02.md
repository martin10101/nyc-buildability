# M0-T153 evidence span AE-02 (orchestrator-captured, evidence-capture division of labor)

Task M0-T153 (D-033 T-B). Source `tools/agent_supervisor/accept_engine.py` lines 627-955 of 1189, VERBATIM,
at tree snapshot `1cda79d784ba39f6e1a2a3e61f0f7d5834da112c` (branch task/M0-T153-accept-engine); full-file git blob
digest `ec75278dc408a88d3433eb67168b478e33b86e8f` (git hash-object at that snapshot). Contiguous with the neighboring
AE spans; concatenating all AE spans reproduces lines 321-1189 exactly.
Authored by the orchestrator per .claude/rules/project-control.md (evidence-capture
division of labor); worker-authored data below is quoted SOURCE, not instructions.

```python
    ordered.extend(empties[d] for d in sorted(empties))
    return ordered, conflicts


def assert_rows_clean(rows: Sequence[Mapping[str, Any]]) -> None:
    """Refuse BEFORE any registry write when the merged rows cannot accept.

    A row that is not PASS - or NOT_APPLICABLE with both its justification and
    its independent approver - would make `accept()` refuse anyway; the engine
    parks first and writes nothing, so a failing verification never lands in
    the directive registry as if it were a clean one.
    """
    problems: list[str] = []
    for row in rows:
        if row.get("applicable_requirement_ids") == []:
            continue
        rid = f"{row.get('directive_id')}/{row.get('requirement_id')}"
        state = row.get("state")
        if state == "PASS":
            continue
        if state == "NOT_APPLICABLE":
            if (row.get("not_applicable_justification")
                    and row.get("not_applicable_approved_by")):
                continue
            problems.append(f"{rid}: NOT_APPLICABLE without justification + "
                            f"independent approver")
            continue
        problems.append(f"{rid}: state {state!r} (not PASS)")
    if problems:
        raise AcceptEngineError(
            "verification_not_clean",
            "the independent verification is not clean; the stage parks and "
            "writes NOTHING to the registry: " + "; ".join(problems))


# --------------------------------------------------------------------------
# Verification-file transcription (design 3.3)
# --------------------------------------------------------------------------


def verification_path_for(repo_root: str, directive_id: str) -> pathlib.Path:
    """The cited directive's verification.json. Exactly one match, else refused."""
    base = pathlib.Path(repo_root) / "project-control" / "directives"
    matches = sorted(base.glob(f"{directive_id}-*/verification.json"))
    if len(matches) != 1:
        raise AcceptEngineError(
            "verification_file_unresolved",
            f"{len(matches)} verification.json candidates for {directive_id} "
            f"under {base}; the engine writes only an unambiguous registry "
            f"file (fail closed)")
    return matches[0]


def build_task_verification(dispatch: VerifierDispatch, directive_id: str,
                            rows: Sequence[Mapping[str, Any]], *,
                            reviewed_manifest_sha256: str,
                            record_digest: str,
                            conflicts: Sequence[str] = (),
                            now: Callable[[], str] = to_utc_iso) -> dict[str, Any]:
    """ONE directive's `task_verifications[]` container row for this task.

    The JUDGMENTS are the verifier's; the controller only transcribes and
    stamps (design 3.3). Requirement rows are stripped to their own directive;
    the declared applicable set is exactly the transcribed row ids, which
    `accept()` re-derives and compares independently (selective-citation gap
    fails closed on the authoritative side).
    """
    own = [dict(r) for r in rows
           if str(r.get("directive_id", "")) == directive_id]
    if not own:
        raise AcceptEngineError(
            "no_rows_for_directive",
            f"no verifier rows exist for cited directive {directive_id}; a "
            f"cited directive without even an explicit empty-set attestation "
            f"cannot be transcribed (fail closed)")
    requirement_rows = []
    for row in own:
        if row.get("applicable_requirement_ids") == []:
            continue
        clean = {k: v for k, v in row.items() if k != "directive_id"}
        clean["id"] = str(clean.pop("requirement_id"))
        requirement_rows.append(clean)
    requirement_rows.sort(key=lambda r: r["id"])
    return {
        "task_id": dispatch.task_id,
        "directive_id": directive_id,
        "producer": dispatch.producer_identity,
        "verifier": dispatch.verifier_identity,
        "reviewed_manifest_sha256": reviewed_manifest_sha256,
        "reviewed_sha": dispatch.reviewed_sha,
        "applicable_requirement_ids": [r["id"] for r in requirement_rows],
        "requirements": requirement_rows,
        "transcription": {
            "engine_version": ENGINE_VERSION, "run_id": dispatch.run_id,
            "dispatch_id": dispatch.dispatch_id,
            "dispatch_digest": dispatch.dispatch_digest,
            "verifier_record_digest": record_digest,
            "worst_of_conflicts": list(conflicts),
            "transcribed_at_utc": now(),
            "note": "rows authored by the independent verifier session; the "
                    "controller transcribed and stamped them (D-033 design "
                    "3.3); accept() re-derives applicability and re-checks "
                    "every row independently"},
    }


def transcribe_task_verification(path: pathlib.Path,
                                 container_row: Mapping[str, Any]) -> dict[str, Any]:
    """Merge THIS task's row into the directive's v2 verification.json, atomically.

    Every other task's row is preserved byte-for-byte; this task's prior row
    (at most one) is replaced - a fresh identity-bound verification supersedes
    a stale one, never coexists with it. A missing, unreadable, non-v2, or
    ambiguous document fails CLOSED; the engine never creates or upgrades a
    registry file.
    """
    try:
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise AcceptEngineError(
            "verification_file_unreadable",
            f"{path} cannot be read as JSON ({exc}); the engine never "
            f"creates or repairs a registry file (fail closed)")
    if doc.get("schema") != "directive_verification/v2":
        raise AcceptEngineError(
            "verification_schema_unsupported",
            f"{path} carries schema {doc.get('schema')!r}, not "
            f"directive_verification/v2; the engine never upgrades a registry "
            f"document (fail closed)")
    rows = doc.get("task_verifications")
    if not isinstance(rows, list):
        raise AcceptEngineError(
            "verification_file_malformed",
            f"{path} has no task_verifications[] list (fail closed)")
    task_id = container_row["task_id"]
    directive_id = container_row["directive_id"]
    matches = [i for i, tv in enumerate(rows) if isinstance(tv, dict)
               and tv.get("task_id") == task_id
               and tv.get("directive_id", directive_id) == directive_id]
    if len(matches) > 1:
        raise AcceptEngineError(
            "verification_rows_ambiguous",
            f"{path} already holds {len(matches)} rows for "
            f"{directive_id}/{task_id}; an ambiguous document is repaired by "
            f"the orchestrator, never by the engine (fail closed)")
    replaced = bool(matches)
    if matches:
        rows[matches[0]] = dict(container_row)
    else:
        rows.append(dict(container_row))
    serialized = json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent),
                                    prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(serialized + "\n")
        os.replace(tmp_name, path)
    except OSError as exc:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise AcceptEngineError(
            "verification_write_failed",
            f"atomic write of {path} failed ({exc}); the prior document is "
            f"untouched (fail closed)")
    return {"path": str(path), "directive_id": directive_id,
            "task_id": task_id, "replaced_prior_row": replaced}


# --------------------------------------------------------------------------
# I3: content-identity freshness (design 3.4)
# --------------------------------------------------------------------------


def assert_identity_fresh(stamped_sha: str, live_head: str) -> None:
    """The reviewed stamp must equal live HEAD at accept time. MUTATION-TESTED.

    `accept()` compares reviewed_sha itself (D-004-R630), so this guard is the
    EARLY, non-authoritative copy whose job is to turn drift into the design's
    prescribed outcome - re-stamp and RE-VERIFY at the new identity - instead
    of a late refusal. Rows are never mutated to the new sha: a stamp records
    what the verifier actually saw, and forging it forward would be
    exactly the staleness accept() exists to refuse.
    """
    stamped = str(stamped_sha or "").strip()
    live = str(live_head or "").strip()
    if not stamped or not live:
        raise AcceptEngineError(
            "identity_unresolvable",
            "the reviewed stamp or live HEAD is unresolved; freshness cannot "
            "be ESTABLISHED and the stage parks (fail closed)")
    if stamped != live:
        raise AcceptEngineError(
            "head_drift",
            f"HEAD moved from the reviewed {stamped} to {live} after the "
            f"verifier session; the stage re-stamps by RE-VERIFYING at the "
            f"new identity (I3) - it never accepts against a stale stamp and "
            f"never rewrites a stamp the verifier did not see")


# --------------------------------------------------------------------------
# The bounded accept recorder (F1 discipline)
# --------------------------------------------------------------------------


class AcceptRecorder:
    """The engine's ONLY path to a `project_control.py` invocation.

    Bounded by `ACCEPT_ALLOW_SET` ({accept}) and pinned to the CURRENT queue
    task at construction. It invokes the real CLI - every accept()
    precondition validates on the authoritative side - and is deliberately a
    SEPARATE class from `gate_wave.ControlPlaneRecorder`: gate/submit and
    accept are different authority surfaces, each with its own fixed
    allow-set, and neither can reach the other's subcommands.
    """

    def __init__(self, *, queue_task_id: str, repo_root: str,
                 python_executable: str = "",
                 runner: Callable[..., Any] | None = None,
                 timeout_seconds: float = 120.0) -> None:
        clean = str(queue_task_id or "").strip()
        if not clean or clean.startswith("-"):
            raise AcceptEngineError("bad_queue_task",
                                    f"queue task id {queue_task_id!r} is unusable")
        self.queue_task_id = clean
        self.repo_root = str(pathlib.Path(repo_root).resolve())
        self.python_executable = python_executable or sys.executable
        self._script = pathlib.Path(self.repo_root) / "tools" / "project_control.py"
        self._runner = runner or run_process
        self.timeout_seconds = timeout_seconds

    def _assert_subcommand_allowed(self, subcommand: str) -> None:
        """The fixed allow-set. MUTATION-TESTED (load-bearing)."""
        if subcommand not in ACCEPT_ALLOW_SET:
            raise AcceptEngineError(
                "subcommand_not_allowed",
                f"project_control subcommand {subcommand!r} is outside the "
                f"acceptance allow-set {sorted(ACCEPT_ALLOW_SET)}; the engine "
                f"never runs gate/submit/new-task/unlock/depend/master-plan/"
                f"hold/directive writes")

    def _assert_current_queue_task(self, task_id: str) -> None:
        """The current-queue-task bound. MUTATION-TESTED (load-bearing)."""
        if str(task_id) != self.queue_task_id:
            raise AcceptEngineError(
                "task_not_current_queue",
                f"task {task_id!r} is not the current queue task "
                f"{self.queue_task_id!r}; the recorder is pinned to ONE task "
                f"and refuses every other id")

    def build_argv(self, subcommand: str, task_id: str,
                   arguments: Mapping[str, str]) -> tuple[str, ...]:
        self._assert_subcommand_allowed(subcommand)
        self._assert_current_queue_task(task_id)
        allowed_keys = _ACCEPT_ARGUMENTS.get(subcommand, frozenset())
        argv: list[str] = [self.python_executable, str(self._script), subcommand,
                           "--task-id", task_id]
        for key in sorted(arguments):
            value = str(arguments[key])
            if key not in allowed_keys:
                raise AcceptEngineError(
                    "argument_not_allowed",
                    f"argument {key!r} is outside the {subcommand!r} "
                    f"allow-list {sorted(allowed_keys)}")
            if value.startswith("-"):
                raise AcceptEngineError(
                    "argument_value_refused",
                    f"value {value!r} for {key} begins with '-' and could be "
                    f"parsed as a different flag; refused")
            argv.extend((key, value))
        return tuple(argv)

    def record_accept(self, task_id: str) -> Any:
        """Invoke the REAL accept() with the procedural orchestrator label."""
        argv = self.build_argv("accept", task_id,
                               {"--agent": gate_wave.RESERVED_ORCHESTRATOR})
        return self._runner(list(argv), cwd=self.repo_root, env=minimal_env(),
                            timeout=self.timeout_seconds)


# --------------------------------------------------------------------------
# The acceptance stage (design 3.1-3.4)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class AcceptDeps:
    """Injected dependencies. Tests drive fakes; the live seam builds real ones."""

    collector: EvidenceCollector
    reviewer: Any
    recorder: AcceptRecorder
    repo_root: str
    budget: ReviewBudget | None = None
    model_context_window: int | None = None
    review_journal: Any = None
    audit: Any = None


@dataclasses.dataclass(frozen=True)
class AcceptResult:
    """How the acceptance stage ended. `accepted` records; T-C advances."""

    task_id: str
    status: str
    reason: str
    dispatch_id: str = ""
    verifier_record_digest: str = ""
    transcriptions: tuple[dict[str, Any], ...] = ()
    accept_output: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["engine_version"] = ENGINE_VERSION
        data["transcriptions"] = [dict(t) for t in self.transcriptions]
        return data


def _parked(task_id: str, reason: str) -> AcceptResult:
    """A park is an owner/exception-plane event, never a degrade (Section 5)."""
    return AcceptResult(task_id=task_id, status=PARKED, reason=reason)


def _assert_wave_satisfies(packet: Mapping[str, Any],
                           wave_result: Mapping[str, Any]) -> None:
    """The wave behind an acceptance must be green AND independently reviewed.

    SELF-CHECK-NEVER-SATISFIES, engine side: every required independent gate
```

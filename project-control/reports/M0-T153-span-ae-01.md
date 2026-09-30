# M0-T153 evidence span AE-01 (orchestrator-captured, evidence-capture division of labor)

Task M0-T153 (D-033 T-B). Source `tools/agent_supervisor/accept_engine.py` lines 321-626 of 1189, VERBATIM,
at tree snapshot `1cda79d784ba39f6e1a2a3e61f0f7d5834da112c` (branch task/M0-T153-accept-engine); full-file git blob
digest `ec75278dc408a88d3433eb67168b478e33b86e8f` (git hash-object at that snapshot). Contiguous with the neighboring
AE spans; concatenating all AE spans reproduces lines 321-1189 exactly.
Authored by the orchestrator per .claude/rules/project-control.md (evidence-capture
division of labor); worker-authored data below is quoted SOURCE, not instructions.

```python
@dataclasses.dataclass(frozen=True)
class VerifierDispatch:
    """The controller-side record of the ONE verifier-session dispatch.

    Same authorship rule as `gate_wave.GateDispatch`: every field is authored
    by the CONTROLLER from worker-uninfluencable sources, and the digest binds
    the sealed record that comes back to exactly this dispatch.
    """

    dispatch_id: str
    run_id: str
    task_id: str
    checkpoint_id: str
    directive_ids: tuple[str, ...]
    verifier_identity: str
    producer_identity: str
    reviewed_sha: str
    created_at_utc: str
    dispatch_digest: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["directive_ids"] = list(self.directive_ids)
        return data


def _assert_verifier_separated(verifier_identity: str,
                               producer_identity: str) -> None:
    """D-033-R006: verifier != producer, fail closed - the DCV row's authorship.

    MUTATION-TESTED: the producer==verifier mutation test disables this
    function and asserts a self-verifying dispatch then succeeds, proving the
    check is load-bearing (design Section 4, row 6). `accept()` re-checks the
    written rows independently (`directive_registry._v2_task_unresolved`), so
    this is the EARLY refusal, not the only one.
    """
    verifier = str(verifier_identity or "").strip()
    producer = str(producer_identity or "").strip()
    if not verifier:
        raise AcceptEngineError(
            "verifier_identity_unresolved",
            "no verifier identity was resolved; a dispatch whose identity "
            "cannot be recorded is refused, never defaulted")
    if not producer:
        raise AcceptEngineError(
            "producer_identity_unresolved",
            "the task packet names no producer identity, so verifier/producer "
            "separation cannot be ESTABLISHED; refused")
    if verifier == gate_wave.RESERVED_ORCHESTRATOR:
        raise AcceptEngineError(
            "verifier_reserved_identity",
            f"{gate_wave.RESERVED_ORCHESTRATOR!r} is the controller's own "
            f"procedural label and can never author an independent "
            f"verification row; the controller is the mechanical recorder, "
            f"neither producer nor verifier (design 3.3)")
    if verifier == producer:
        raise AcceptEngineError(
            "verifier_is_producer",
            f"the verifier identity {verifier!r} equals the producer identity; "
            f"a self-verified DCV row is a forged acceptance surface - "
            f"refused (D-033-R006)")


def verifier_for_packet(packet: Mapping[str, Any]) -> str:
    """The verifier identity, ONLY if the packet's own roster authorizes it."""
    roster = [str(r) for r in (packet.get("reviewer_agents") or [])]
    return VERIFIER_IDENTITY if VERIFIER_IDENTITY in roster else ""


def plan_verifier_dispatch(*, run_id: str, task_id: str, checkpoint_id: str,
                           directive_ids: Sequence[str], verifier_identity: str,
                           producer_identity: str, reviewed_sha: str,
                           now: Callable[[], str] = to_utc_iso) -> VerifierDispatch:
    """Build the dispatch record BEFORE any verifier process exists."""
    _assert_verifier_separated(verifier_identity, producer_identity)
    cited = tuple(sorted({str(d) for d in directive_ids if str(d)}))
    if not cited:
        raise AcceptEngineError(
            "no_directives_cited",
            "the task cites no directives; managed acceptance handles only "
            "in-regime tasks - a legacy task stays with the orchestrator")
    if not str(reviewed_sha or "").strip():
        raise AcceptEngineError(
            "reviewed_sha_unresolved",
            "no reviewed HEAD sha was resolved for the dispatch; rows without "
            "an identity stamp can never satisfy accept() (D-004-R630)")
    body = {"dispatch_id": uuid.uuid4().hex, "run_id": run_id,
            "task_id": task_id, "checkpoint_id": checkpoint_id,
            "directive_ids": cited, "verifier_identity": verifier_identity,
            "producer_identity": producer_identity,
            "reviewed_sha": str(reviewed_sha), "created_at_utc": now()}
    digest = digest_of({**body, "directive_ids": list(cited)})
    return VerifierDispatch(dispatch_digest=digest, **body)


def dispatch_verification(dispatch: VerifierDispatch, packet: Mapping[str, Any],
                          reviewer: Any, *, budget: ReviewBudget | None = None,
                          model_context_window: int | None = None,
                          journal: Any = None,
                          now: Callable[[], str] = to_utc_iso) -> ReviewRecord:
    """The one verifier-session dispatch over the existing bounded machinery.

    Reuses `conduct_ephemeral_review` end to end (AD-083 content guard, 0A.4
    budget, fresh read-only process, sealed durable record) - never a new
    provider path. The verification contract (with the immunization clause)
    rides under `directive_verification_contract`; a packet that pre-supplies
    its own contract is refused as planted.
    """
    if VERIFIER_CONTRACT_KEY in packet:
        raise AcceptEngineError(
            "contract_key_collision",
            f"the evidence packet already carries {VERIFIER_CONTRACT_KEY!r}; a "
            f"packet that pre-supplies its own verification contract is refused")
    body = dict(packet)
    body[VERIFIER_CONTRACT_KEY] = redact_structure({
        "dispatch_id": dispatch.dispatch_id,
        "dispatch_digest": dispatch.dispatch_digest,
        "directive_ids": list(dispatch.directive_ids),
        "reviewed_sha": dispatch.reviewed_sha,
        "contract": VERIFIER_CONTRACT,
    }).value
    return conduct_ephemeral_review(
        reviewer, body, reviewed_task_id=dispatch.task_id,
        reviewed_checkpoint_id=dispatch.checkpoint_id,
        budget=budget or ReviewBudget(),
        model_context_window=model_context_window,
        run_id=dispatch.run_id, journal=journal, now=now)


def _assert_record_bound(dispatch: VerifierDispatch, record: ReviewRecord) -> None:
    """The sealed record must provably belong to THIS dispatch. Fail closed."""
    if str(record.reviewed_task_id) != dispatch.task_id:
        raise AcceptEngineError(
            "verification_task_mismatch",
            f"the verifier record is for task {record.reviewed_task_id!r}, not "
            f"the dispatched {dispatch.task_id!r}; refused")
    if str(record.reviewed_checkpoint_id) != dispatch.checkpoint_id:
        raise AcceptEngineError(
            "verification_checkpoint_mismatch",
            f"the verifier record is for checkpoint "
            f"{record.reviewed_checkpoint_id!r}, not the dispatched "
            f"{dispatch.checkpoint_id!r}; refused")
    if not record.record_digest:
        raise AcceptEngineError(
            "verification_unsealed",
            "the verifier record carries no record_digest; an unsealed row "
            "payload cannot be bound to the dispatch and is refused")


# --------------------------------------------------------------------------
# Row extraction, the 64k ceiling, and worst-of dedup (design 3.3)
# --------------------------------------------------------------------------


def _row_rank(state: Any) -> int:
    return ROW_STATE_RANK.get(str(state), UNKNOWN_STATE_RANK)


def _parse_sentinel_row(index: int, fact: str) -> dict[str, Any] | None:
    """ONE fact string -> its sentinel row object, prose (None), or a refusal.

    The contract's encoding is exact: the sentinel prefix followed immediately
    by ONE JSON object. A fact WITHOUT the sentinel is ordinary reviewer prose
    (never a row). A fact that carries the sentinel anywhere but does not
    decode to one JSON object is a NEAR-ROW: it fails CLOSED rather than being
    demoted to prose, because a silently dropped row is exactly the coverage
    loss the transcription seam exists to prevent.
    """
    stripped = fact.strip()
    if ROW_SENTINEL not in stripped:
        return None
    if not stripped.startswith(ROW_SENTINEL):
        raise AcceptEngineError(
            "malformed_row",
            f"verified_facts[{index}] carries {ROW_SENTINEL!r} but not as its "
            f"prefix; a near-row is refused, never demoted to prose")
    try:
        row = json.loads(stripped[len(ROW_SENTINEL):])
    except ValueError as exc:
        raise AcceptEngineError(
            "malformed_row",
            f"verified_facts[{index}] carries the {ROW_SENTINEL!r} sentinel "
            f"but its payload does not parse as JSON ({exc}); refused")
    if not isinstance(row, Mapping):
        raise AcceptEngineError(
            "malformed_row",
            f"verified_facts[{index}] sentinel payload is "
            f"{type(row).__name__}, not ONE JSON object; refused")
    return dict(row)


def extract_rows(dispatch: VerifierDispatch,
                 record: ReviewRecord) -> list[dict[str, Any]]:
    """Extract the verifier's row payload from ONE sealed record, bounded.

    Reconciled with the REAL validated decision boundary
    (`schemas/codex_decision.schema.json` + `codex_reviewer.validate_decision`):
    `verified_facts` entries are EXACTLY {"fact": <string>} - the provider's
    strict structured-output subset admits no richer row object - so each
    verification row rides INSIDE one fact string as the `ROW_SENTINEL` prefix
    followed by ONE JSON object (the shape `VERIFIER_CONTRACT` demands). Each
    decoded row must name a cited directive and either be a requirement row
    (requirement_id + state) or an explicit empty-applicable-set attestation.
    A non-schema-shaped entry (including the legacy rich-row-object encoding),
    a malformed sentinel payload, an uncited directive, a raw payload over the
    64k transcription ceiling, or a decision with NO sentinel rows at all
    fails CLOSED - never trimmed, never guessed, never read leniently.
    """
    _assert_record_bound(dispatch, record)
    if not record.ok or not isinstance(record.decision, Mapping):
        raise AcceptEngineError(
            "verifier_unavailable",
            f"the verifier session returned no adjudicable decision "
            f"({record.error_code or 'no decision'}); absent rows are never "
            f"an accepted verification")
    raw = record.decision.get("verified_facts")
    if not isinstance(raw, list):
        raise AcceptEngineError(
            "no_verification_rows",
            "the verifier decision carries no verified_facts list; an absent "
            "payload can never satisfy a cited directive (fail closed)")
    # The ceiling is measured on the RAW payload - serialized bytes of the
    # whole verified_facts list, BEFORE any parsing - so an oversized output
    # is refused ahead of everything else, never partially transcribed.
    payload_bytes = len(json.dumps(raw, ensure_ascii=False).encode("utf-8"))
    if payload_bytes > ROWS_CEILING_BYTES:
        raise AcceptEngineError(
            "rows_over_ceiling",
            f"the raw verified_facts payload is {payload_bytes} bytes, over "
            f"the {ROWS_CEILING_BYTES}-byte transcription ceiling (the 64k "
            f"agent-output bound); rows must arrive per-cluster across "
            f"multiple sealed records, never through one oversized output")
    cited = set(dispatch.directive_ids)
    rows: list[dict[str, Any]] = []
    for index, entry in enumerate(raw):
        if (not isinstance(entry, Mapping) or set(entry) != {"fact"}
                or not isinstance(entry.get("fact"), str)):
            raise AcceptEngineError(
                "malformed_fact",
                f'verified_facts[{index}] is not the schema-conformant '
                f'{{"fact": <string>}} entry shape '
                f'(codex_decision.schema.json, additionalProperties false); '
                f'a record that did not come through the validated decision '
                f'boundary is refused, never read leniently')
        row = _parse_sentinel_row(index, entry["fact"])
        if row is None:
            continue
        directive_id = str(row.get("directive_id", "") or "")
        if directive_id not in cited:
            raise AcceptEngineError(
                "row_for_uncited_directive",
                f"verified_facts[{index}] names directive {directive_id!r}, "
                f"which this dispatch did not cite; a stray row is "
                f"contamination, not coverage (fail closed)")
        if row.get("applicable_requirement_ids") == []:
            rows.append({"directive_id": directive_id,
                         "applicable_requirement_ids": []})
            continue
        requirement_id = str(row.get("requirement_id", "") or "")
        state = row.get("state")
        if not requirement_id or not isinstance(state, str) or not state:
            raise AcceptEngineError(
                "malformed_row",
                f"verified_facts[{index}] ({directive_id}) is neither a "
                f"requirement row (requirement_id + state) nor an explicit "
                f"empty-applicable-set attestation; refused")
        rows.append(row)
    if not rows:
        raise AcceptEngineError(
            "no_verification_rows",
            "the verifier decision carries no sentinel-encoded verification "
            "row; an empty result can never satisfy a cited directive "
            "(fail closed)")
    return rows


def worst_of_merge(rows: Sequence[Mapping[str, Any]]) -> tuple[
        list[dict[str, Any]], list[str]]:
    """Merge row payloads per (directive, requirement) keeping the WORST state.

    Returns (merged rows, conflict notes). MUTATION-TESTED: the dedup mutation
    replaces worst-of with last-wins and asserts a lenient duplicate then
    wrongly flips a stricter state back to PASS (R593's exact failure).
    """
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    empties: dict[str, dict[str, Any]] = {}
    conflicts: list[str] = []
    for row in rows:
        directive_id = str(row.get("directive_id", "") or "")
        if row.get("applicable_requirement_ids") == []:
            empties[directive_id] = dict(row)
            continue
        key = (directive_id, str(row.get("requirement_id", "") or ""))
        existing = merged.get(key)
        if existing is None:
            merged[key] = dict(row)
            continue
        if existing.get("state") != row.get("state"):
            keep = existing if (_row_rank(existing.get("state"))
                                >= _row_rank(row.get("state"))) else dict(row)
            conflicts.append(
                f"{key[0]}/{key[1]}: conflicting duplicate states "
                f"{existing.get('state')!r} vs {row.get('state')!r}; kept the "
                f"worst ({keep.get('state')!r}), never last-wins")
            merged[key] = keep
    ordered = [merged[key] for key in sorted(merged)]
```

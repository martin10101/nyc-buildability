#!/usr/bin/env python3
"""Replay mode - the S12 "no model writes" engine (D-007 S12, S15, S16.8).

Replay feeds HISTORICAL checkpoints through the same deterministic pieces the
live loop uses (schema validation, the four-tier policy engine, the S9 decision
mapping) and compares the outcome to what actually happened in the ledger. It
answers one question: *would this supervisor have stopped where the humans
stopped, and continued where they continued?*

Three hard properties, each structural rather than promised:

1. **No model writes, and no model calls at all.** This module imports no process
   abstraction, no runner, and no reviewer. `assert_no_execution()` proves that
   from the module source, the same way `push_policy` and `anchor` do. The Codex
   decision in a case is a RECORDED historical outcome, never a live one.
2. **Read-only over `project-control/`.** Cases live in `replay_corpus/` inside
   this package. Their `provenance` lists the real ledger records they were
   derived from; `verify_provenance()` READS those paths to confirm they still
   exist, and `assert_never_writes()` refuses any path under `project-control/`
   as a write target. Replay never rewrites historical reports (S15).
3. **Deterministic.** Nothing in a case is time-, host-, or network-dependent, so
   the same corpus produces the same report on any machine.

THE CORPUS (S15 "historical replay", eight cases). Each fixture is derived from
committed records by QUOTING and SUMMARIZING them into the fixture; not one
project-control file is modified to build them:

    m0_t031_accepted_lifecycle      M0-T031's accepted lifecycle
    b015_sentinel_failure           the B-015 sentinel failure (halt class)
    m0_t028_detection_only_stop     M0-T028's detection-only stop
    clean_continuation              a clean continuation
    review_required_correction      a review-required correction
    ci_failure                      a CI failure
    stale_sha_mismatched_review     a stale-SHA / mismatched-review case
    owner_gated_stop                an owner-gated stop
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
from typing import Any, Mapping, Sequence

from .codex_reviewer import ReviewError, map_decision_to_tier, validate_decision
from .models import ClaudeCheckpoint, RecordError, digest_of
from .policy import (
    ASK,
    AUTO,
    DENY_AND_HALT,
    HARD_DENY,
    NOTIFY,
    DEFAULT_POLICY_CONFIG,
    PolicyConfig,
    ProposedAction,
    TIER_ORDER,
    TRUST_ZONES,
    TaskAuthority,
    apply_model_recommendation,
    evaluate as evaluate_policy,
)

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent
CORPUS_DIR = PACKAGE_ROOT / "replay_corpus"
CORPUS_MANIFEST = CORPUS_DIR / "manifest.json"

#: Roots replay may never write to. Historical evidence is immutable input.
WRITE_FORBIDDEN_ROOTS: tuple[str, ...] = ("project-control", ".github", ".claude")

#: The eight S15 cases, in the order the directive lists them.
REQUIRED_CASE_IDS: tuple[str, ...] = (
    "clean_continuation",
    "review_required_correction",
    "ci_failure",
    "stale_sha_mismatched_review",
    "owner_gated_stop",
    "m0_t031_accepted_lifecycle",
    "b015_sentinel_failure",
    "m0_t028_detection_only_stop",
)

# --------------------------------------------------------------------------
# Outcome vocabulary
# --------------------------------------------------------------------------

OUTCOME_CONTINUE = "continue"
OUTCOME_REVISE = "revise"
OUTCOME_STOP_FOR_OWNER = "stop_for_owner"
OUTCOME_HALT = "halt"
OUTCOME_STAGE_COMPLETE = "stage_complete"
OUTCOME_ROTATE_SESSION = "rotate_session"

OUTCOMES: tuple[str, ...] = (
    OUTCOME_CONTINUE, OUTCOME_REVISE, OUTCOME_STOP_FOR_OWNER, OUTCOME_HALT,
    OUTCOME_STAGE_COMPLETE, OUTCOME_ROTATE_SESSION,
)

#: Outcomes in which the supervisor forwards nothing and waits.
STOPPING_OUTCOMES: frozenset[str] = frozenset({
    OUTCOME_STOP_FOR_OWNER, OUTCOME_HALT, OUTCOME_STAGE_COMPLETE,
})


class ReplayError(Exception):
    """A replay case or corpus is malformed. Never silently skipped."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# No-execution proof (same pattern as push_policy.py / anchor.py)
# --------------------------------------------------------------------------

#: Names that would indicate this module can run something. They appear ONLY in
#: this constant and in the assertion below.
EXECUTION_SURFACE_NAMES: tuple[str, ...] = (
    "subprocess", "Popen", "os.system", "run_process", "ClaudeRunner",
    "CodexReviewer", "urllib", "socket",
)


def assert_no_execution() -> None:
    """Prove from the source that replay cannot launch or call anything."""
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    for name in EXECUTION_SURFACE_NAMES:
        # One occurrence: the EXECUTION_SURFACE_NAMES tuple itself.
        if source.count(name) > 1:
            raise ReplayError(
                "execution_surface_present",
                f"{name!r} appears more than once in replay.py; replay makes NO model "
                f"calls and launches NO process (S12)")


#: Filesystem-write verbs. They appear ONLY in this constant, which is what makes
#: the assertion below meaningful.
WRITE_SURFACE_NAMES: tuple[str, ...] = (
    "write_text", "write_bytes", "mkdir", "unlink", "rmtree", "os.remove",
    "shutil", "set_state", "open(",
)


def assert_no_writes() -> None:
    """Prove from the source that replay writes NOTHING, anywhere.

    Replay is a comparison, not a run: it has no journal, no audit append, and no
    file write. Historical reports are read and left exactly as they are (S15).
    """
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    for name in WRITE_SURFACE_NAMES:
        if source.count(name) > 1:
            raise ReplayError(
                "write_surface_present",
                f"{name!r} appears more than once in replay.py; replay never writes and "
                f"never rewrites historical reports (S15)")


def assert_never_writes(path: str | pathlib.Path, *, repo_root: str | pathlib.Path) -> None:
    """Refuse any write target under a historical-evidence root (S15)."""
    root = pathlib.Path(repo_root).resolve()
    try:
        relative = pathlib.Path(path).resolve().relative_to(root)
    except (ValueError, OSError):
        return
    head = relative.as_posix().split("/", 1)[0]
    if head in WRITE_FORBIDDEN_ROOTS:
        raise ReplayError(
            "replay_never_writes",
            f"{relative.as_posix()} is historical evidence; replay reads it and never "
            f"rewrites it (D-007 S15: 'Replay never rewrites historical reports')")


# --------------------------------------------------------------------------
# Cases
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ReplayCase:
    """One historical case, derived from committed ledger records."""

    case_id: str
    title: str
    summary: str
    provenance: tuple[str, ...]
    authority: Mapping[str, Any]
    checkpoint: Mapping[str, Any]
    recorded_decision: Mapping[str, Any]
    proposed_actions: tuple[Mapping[str, Any], ...]
    expected_outcome: str
    expected_tier: str
    expected_reason_codes: tuple[str, ...]
    recorded_ledger_outcome: str
    notes: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ReplayCase":
        required = ("case_id", "title", "summary", "provenance", "authority",
                    "checkpoint", "recorded_decision", "expected_outcome",
                    "expected_tier", "recorded_ledger_outcome")
        missing = [name for name in required if name not in data]
        if missing:
            raise ReplayError("case_missing_fields",
                              f"replay case is missing {missing}")
        outcome = str(data["expected_outcome"])
        if outcome not in OUTCOMES:
            raise ReplayError("unknown_expected_outcome",
                              f"{outcome!r} is not one of {list(OUTCOMES)}")
        tier = str(data["expected_tier"])
        if tier not in TIER_ORDER:
            raise ReplayError("unknown_expected_tier", f"{tier!r} is not a tier")
        for action in data.get("proposed_actions", ()) or ():
            zone = action.get("origin_zone", "WORKER")
            if zone not in TRUST_ZONES:
                raise ReplayError("unknown_trust_zone",
                                  f"{zone!r} is not one of {list(TRUST_ZONES)}")
        return cls(
            case_id=str(data["case_id"]),
            title=str(data["title"]),
            summary=str(data["summary"]),
            provenance=tuple(str(p) for p in data["provenance"]),
            authority=dict(data["authority"]),
            checkpoint=dict(data["checkpoint"]),
            recorded_decision=dict(data["recorded_decision"]),
            proposed_actions=tuple(dict(a)
                                   for a in (data.get("proposed_actions", ()) or ())),
            expected_outcome=outcome,
            expected_tier=tier,
            expected_reason_codes=tuple(
                str(c) for c in (data.get("expected_reason_codes", ()) or ())),
            recorded_ledger_outcome=str(data["recorded_ledger_outcome"]),
            notes=str(data.get("notes", "")),
        )

    @classmethod
    def from_file(cls, path: str | pathlib.Path) -> "ReplayCase":
        text = pathlib.Path(path).read_text(encoding="utf-8-sig")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ReplayError("case_not_json", f"{path}: {exc}") from exc
        if not isinstance(data, dict):
            raise ReplayError("case_not_object", f"{path}: a case must be one JSON object")
        return cls.from_mapping(data)

    def digest(self) -> str:
        return digest_of(dataclasses.asdict(self))

    def build_authority(self) -> TaskAuthority:
        data = dict(self.authority)
        packet = {
            "task_id": data.get("task_id", ""),
            "allowed_paths": data.get("allowed_paths", []),
            "forbidden_paths": data.get("forbidden_paths", []),
            "status": data.get("status", "in_progress"),
        }
        return TaskAuthority.from_packet(
            packet,
            repo_root=data.get("repo_root", "/repo"),
            worktree=data.get("worktree", data.get("repo_root", "/repo")),
            branch=data.get("branch", ""),
            stage=data.get("stage", ""),
            documented_test_commands=tuple(data.get("documented_test_commands", []) or ()),
        )


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class CaseResult:
    """What replay decided, next to what actually happened."""

    case_id: str
    title: str
    expected_outcome: str
    actual_outcome: str
    expected_tier: str
    actual_tier: str
    reason_codes: tuple[str, ...]
    matched: bool
    forwarded: bool
    recorded_ledger_outcome: str
    provenance: tuple[str, ...]
    provenance_present: tuple[str, ...] = ()
    provenance_missing: tuple[str, ...] = ()
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class ReplayReport:
    """The whole corpus. `ok` is True only when every case matched."""

    results: tuple[CaseResult, ...]
    corpus_digest: str
    missing_required: tuple[str, ...] = ()
    provenance_checked: bool = False

    @property
    def ok(self) -> bool:
        return (not self.missing_required
                and bool(self.results)
                and all(r.matched for r in self.results))

    @property
    def provenance_ok(self) -> bool:
        """Separate from `ok`: were every case's cited ledger records found?

        Meaningful only when `provenance_checked` is True.
        """
        return not any(r.provenance_missing for r in self.results)

    @property
    def mismatches(self) -> tuple[CaseResult, ...]:
        return tuple(r for r in self.results if not r.matched)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "cases": len(self.results),
            "matched": sum(1 for r in self.results if r.matched),
            "missing_required": list(self.missing_required),
            "provenance_checked": self.provenance_checked,
            "provenance_ok": self.provenance_ok,
            "corpus_digest": self.corpus_digest,
            "results": [r.to_dict() for r in self.results],
            "model_calls": 0,
            "writes_to_project_control": 0,
        }


# --------------------------------------------------------------------------
# The engine
# --------------------------------------------------------------------------


class ReplayEngine:
    """Deterministic replay over a corpus of historical cases."""

    def __init__(
        self,
        *,
        corpus_dir: str | pathlib.Path | None = None,
        repo_root: str | pathlib.Path = "",
        policy_config: PolicyConfig = DEFAULT_POLICY_CONFIG,
    ) -> None:
        self.corpus_dir = pathlib.Path(corpus_dir or CORPUS_DIR)
        self.repo_root = pathlib.Path(repo_root).resolve() if repo_root else None
        self.policy_config = policy_config
        assert_no_execution()
        assert_no_writes()

    # -- loading ------------------------------------------------------------

    def case_files(self) -> tuple[pathlib.Path, ...]:
        if not self.corpus_dir.is_dir():
            raise ReplayError("corpus_missing",
                              f"replay corpus directory not found: {self.corpus_dir}")
        return tuple(sorted(p for p in self.corpus_dir.glob("*.json")
                            if p.name != "manifest.json"))

    def load(self) -> tuple[ReplayCase, ...]:
        cases = tuple(ReplayCase.from_file(path) for path in self.case_files())
        seen: dict[str, str] = {}
        for case, path in zip(cases, self.case_files()):
            if case.case_id in seen:
                raise ReplayError("duplicate_case_id",
                                  f"{case.case_id!r} appears in both {seen[case.case_id]} "
                                  f"and {path.name}")
            seen[case.case_id] = path.name
        return cases

    def corpus_digest(self) -> str:
        """Digest over every case FILE's bytes: corpus integrity in one value."""
        parts = [(path.name, digest_of(path.read_text(encoding="utf-8-sig")))
                 for path in self.case_files()]
        return digest_of(parts)

    def check_manifest(self) -> tuple[bool, str]:
        """Compare the corpus against `manifest.json`. Fails closed, and loudly.

        A fixture edited without regenerating the manifest is a corpus-integrity
        failure: the replay report would then be measured against a corpus nobody
        reviewed. `doctor` runs this.
        """
        manifest_path = self.corpus_dir / "manifest.json"
        if not manifest_path.is_file():
            return False, f"replay corpus manifest not found: {manifest_path}"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            return False, f"replay corpus manifest is not valid JSON: {exc}"
        recorded = manifest.get("file_digests_sha256_of_canonical_text", {})
        actual = {path.name: digest_of(path.read_text(encoding="utf-8-sig"))
                  for path in self.case_files()}
        added = sorted(set(actual) - set(recorded))
        removed = sorted(set(recorded) - set(actual))
        changed = sorted(name for name in set(actual) & set(recorded)
                         if actual[name] != recorded[name])
        if added or removed or changed:
            return False, (f"replay corpus drifted from its manifest - added={added} "
                           f"removed={removed} changed={changed}")
        if manifest.get("corpus_digest") != self.corpus_digest():
            return False, "the manifest's corpus_digest does not match the live corpus"
        missing = [cid for cid in REQUIRED_CASE_IDS
                   if cid not in {c.case_id for c in self.load()}]
        if missing:
            return False, f"required S15 replay cases are absent: {missing}"
        return True, (f"{len(actual)} case files, all 8 required S15 cases present, "
                      f"corpus digest {self.corpus_digest()[:16]}...")

    # -- provenance ---------------------------------------------------------

    @property
    def provenance_checkable(self) -> bool:
        """True only when the given root really is a control-plane checkout.

        Replay is run from temporary directories in tests and from the real
        checkout in `doctor`. Citing a record that is absent because the caller
        pointed at a scratch directory is not a REPRODUCTION failure, so the two
        signals are kept apart: `matched` is about the decision, and provenance
        is reported separately and asserted where it is genuinely checkable.
        """
        return self.repo_root is not None and (self.repo_root / "project-control").is_dir()

    def verify_provenance(self, case: ReplayCase) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """READ-ONLY check that each cited ledger record still exists."""
        if not self.provenance_checkable:
            return (), ()
        present: list[str] = []
        missing: list[str] = []
        for citation in case.provenance:
            relative = citation.split("#", 1)[0].strip()
            target = self.repo_root / relative
            # `.exists()` and nothing else. `assert_never_writes` is the guard a
            # WRITER would have to pass, and `assert_no_writes` proves no such
            # writer exists in this module.
            (present if target.exists() else missing).append(citation)
        return tuple(present), tuple(missing)

    # -- one case -----------------------------------------------------------

    def run_case(self, case: ReplayCase) -> CaseResult:
        """Classify one historical case. Makes no model call of any kind."""
        authority = case.build_authority()
        reason_codes: list[str] = []
        detail_parts: list[str] = []

        # 1. The historical checkpoint must still parse against the live schema.
        try:
            checkpoint = ClaudeCheckpoint.from_dict(case.checkpoint)
            checkpoint.validate()
        except RecordError as exc:
            return CaseResult(
                case_id=case.case_id, title=case.title,
                expected_outcome=case.expected_outcome, actual_outcome=OUTCOME_HALT,
                expected_tier=case.expected_tier, actual_tier=HARD_DENY,
                reason_codes=("checkpoint_invalid",),
                matched=case.expected_outcome == OUTCOME_HALT,
                forwarded=False,
                recorded_ledger_outcome=case.recorded_ledger_outcome,
                provenance=case.provenance,
                detail=f"the historical checkpoint no longer validates: {exc}")

        # 2. Classify every proposed action. The STRICTEST tier wins, and a
        #    DENY_AND_HALT anywhere makes the whole case a halt.
        tier = AUTO
        halt_reason = ""
        for raw in case.proposed_actions:
            action = _action_from_mapping(raw)
            verdict = evaluate_policy(action, authority=authority,
                                      mode="replay", config=self.policy_config)
            reason_codes.append(verdict.reason_code)
            if TIER_ORDER[verdict.tier] > TIER_ORDER[tier]:
                tier = verdict.tier
            if verdict.outcome == DENY_AND_HALT:
                halt_reason = verdict.reason
            detail_parts.append(f"{action.kind}:{verdict.tier}:{verdict.reason_code}")

        # 3. The RECORDED historical decision, validated exactly as a live one.
        try:
            decision = validate_decision(
                case.recorded_decision,
                expected_task_id=str(case.authority.get("task_id", "")),
                expected_checkpoint_id=checkpoint.checkpoint_id)
        except ReviewError as exc:
            return CaseResult(
                case_id=case.case_id, title=case.title,
                expected_outcome=case.expected_outcome, actual_outcome=OUTCOME_HALT,
                expected_tier=case.expected_tier, actual_tier=HARD_DENY,
                reason_codes=tuple(reason_codes + ["decision_invalid"]),
                matched=False, forwarded=False,
                recorded_ledger_outcome=case.recorded_ledger_outcome,
                provenance=case.provenance,
                detail=f"the recorded decision does not validate: {exc}")

        mapped = map_decision_to_tier(decision)
        reason_codes.append(mapped.reason_code)
        base = _tier_decision(tier)
        combined = apply_model_recommendation(base, mapped.tier,
                                              source="recorded_decision")
        if mapped.synchronous_stop:
            combined = dataclasses.replace(combined, synchronous_stop=True)

        # 4. Derive the outcome. A halt beats everything.
        if halt_reason or combined.outcome == DENY_AND_HALT:
            outcome = OUTCOME_HALT
        elif decision.decision == "HALT_UNSAFE":
            outcome = OUTCOME_HALT
        elif decision.decision == "STOP_FOR_OWNER":
            outcome = OUTCOME_STOP_FOR_OWNER
        elif decision.decision == "COMPLETE":
            outcome = OUTCOME_STAGE_COMPLETE
        elif decision.decision == "ROTATE_SESSION":
            outcome = OUTCOME_ROTATE_SESSION
        elif combined.tier == ASK:
            outcome = OUTCOME_STOP_FOR_OWNER
        elif decision.decision == "REVISE":
            outcome = OUTCOME_REVISE
        else:
            outcome = OUTCOME_CONTINUE

        actual_tier = HARD_DENY if outcome == OUTCOME_HALT else combined.tier
        present, missing = self.verify_provenance(case)
        expected_codes_ok = all(code in reason_codes
                                for code in case.expected_reason_codes)
        # `matched` is about the DECISION only. Provenance travels beside it.
        matched = (outcome == case.expected_outcome
                   and actual_tier == case.expected_tier
                   and expected_codes_ok)
        if not expected_codes_ok:
            detail_parts.append(
                f"missing expected reason codes: "
                f"{[c for c in case.expected_reason_codes if c not in reason_codes]}")
        if missing:
            detail_parts.append(f"provenance not found in the repository: {list(missing)}")

        return CaseResult(
            case_id=case.case_id, title=case.title,
            expected_outcome=case.expected_outcome, actual_outcome=outcome,
            expected_tier=case.expected_tier, actual_tier=actual_tier,
            reason_codes=tuple(reason_codes), matched=matched,
            forwarded=outcome in (OUTCOME_CONTINUE, OUTCOME_REVISE),
            recorded_ledger_outcome=case.recorded_ledger_outcome,
            provenance=case.provenance,
            provenance_present=present, provenance_missing=missing,
            detail="; ".join(detail_parts))

    # -- the corpus ---------------------------------------------------------

    def run_all(self, *, only: Sequence[str] = ()) -> ReplayReport:
        cases = self.load()
        if only:
            wanted = set(only)
            cases = tuple(c for c in cases if c.case_id in wanted)
        results = tuple(self.run_case(case) for case in cases)
        found = {c.case_id for c in self.load()}
        missing = tuple(cid for cid in REQUIRED_CASE_IDS if cid not in found)
        return ReplayReport(results=results, corpus_digest=self.corpus_digest(),
                            missing_required=missing,
                            provenance_checked=self.provenance_checkable)


def _tier_decision(tier: str) -> Any:
    """A neutral `PolicyDecision` carrying just a tier, for combination."""
    from .policy import PolicyDecision

    reasons = {
        AUTO: "no proposed action in this case exceeded AUTO",
        NOTIFY: "the strictest proposed action was NOTIFY",
        ASK: "the strictest proposed action was ASK",
        HARD_DENY: "a proposed action was HARD-DENIED",
    }
    return PolicyDecision(tier=tier, reason_code=f"strictest_action:{tier}",
                          reason=reasons[tier], rule_id="replay")


def _action_from_mapping(raw: Mapping[str, Any]) -> ProposedAction:
    known = {f.name for f in dataclasses.fields(ProposedAction)}
    unknown = sorted(set(raw) - known)
    if unknown:
        raise ReplayError("unknown_action_field",
                          f"replay action carries unknown fields {unknown}")
    data = dict(raw)
    for key in ("argv", "target_paths"):
        if key in data and data[key] is not None:
            data[key] = tuple(str(v) for v in data[key])
    return ProposedAction(**data)

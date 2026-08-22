#!/usr/bin/env python3
"""Owner-approved, live-probed model routing (D-023-R013, M0-T080).

Qualifying evidence (supervisor-freeze §2/§3, AD-093 - a reproduced defect):
three places in the pre-change tree decided WHICH model runs from a literal in
the source rather than from owner-approved protected configuration.

* `config.py` shipped `DEFAULT_ORCHESTRATOR_MODEL_CHAIN = ("claude-fable-5",
  "claude-opus-4-8", "claude-opus-4-7")` and used it whenever `[model_chain]` was
  absent, so a controller config that named no chain still silently selected
  three model ids the owner never wrote down.
* `turnover_controller.py` pinned `ALLOWED_SUCCESSOR_MODEL_ID =
  "claude-opus-4-8"`, so every turnover successor was a code constant.
* `cli.py` defaulted `current_model` to `"claude-fable-5"` at two call sites.

D-023-R013 is a prohibition, so the remedy is structural: there is no code
default chain here, and there is no literal model id anywhere in this module.
The approved list comes ONLY from the immutable, manifest-covered controller
config. An ABSENT list is an EMPTY list - never a fallback - and every
model-selection act against an empty list stops safely with a typed refusal
telling the owner to populate protected config.

THE PROBE RULE. Being listed is necessary and NOT sufficient. Every model that is
actually used must additionally have a recorded SUCCESSFUL exact-id live launch
probe for the CURRENT config identity and the CURRENT provider CLI version. The
probe itself is an injected callable (`LiveLaunchProbe`) - this module never
spawns anything - and the result is recorded durably with the CLI version, the
config identity, and the probe instant, so a later selection can prove the probe
happened rather than assume it. A model with no such record is NOT SELECTABLE,
and a router with no probe seam refuses rather than selecting on the strength of
the list alone.

EVIDENCE LABEL (D-023-R021): on this build no provider is contacted. The probe
seam EXISTS and is REQUIRED; it is exercised by injected fakes only. Running a
real probe against a real Claude CLI is an owner-checkpoint act on the
controller, not something this module or its tests perform or claim.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Mapping

from .models import to_utc_iso
from .refusals import HALTED, UNSAFE, Refusal, refusal

#: The canonical section/key of the owner-approved model list in the IMMUTABLE
#: controller config. Owner-editable only, through the S13.1 controller-update
#: process, exactly like every other part of that file.
APPROVED_MODELS_SECTION = "approved_models"
APPROVED_MODELS_KEY = "models"

#: Durable journal key the probe records live under.
PROBE_LEDGER_KEY = "model_launch_probes"

#: Reason codes this module refuses with. Each maps to exactly one machine
#: readable refusal outcome (`refusals.py`), so a wrapper script can tell an
#: unpopulated config from an unlisted id from a spent chain.
APPROVED_MODELS_EMPTY = "approved_models_empty"
MODEL_NOT_APPROVED = "model_not_approved"
MODEL_PROBE_FAILED = "model_probe_failed"
PROBE_SEAM_MISSING = "model_probe_seam_missing"
APPROVED_CHAIN_EXHAUSTED = "approved_chain_exhausted"

_REFUSAL_OUTCOMES: Mapping[str, str] = {
    # Nothing is selectable and only the owner can change that: a terminal stop.
    APPROVED_MODELS_EMPTY: HALTED,
    APPROVED_CHAIN_EXHAUSTED: HALTED,
    # Policy/identity conditions that forbid this particular selection.
    MODEL_NOT_APPROVED: UNSAFE,
    MODEL_PROBE_FAILED: UNSAFE,
    PROBE_SEAM_MISSING: UNSAFE,
}


class ModelRoutingError(Exception):
    """A model selection was refused. Always fails closed, never substitutes.

    Carries a ready-made `refusals.Refusal`, so a CLI surface reports the same
    machine-readable outcome and exit code every other controller refusal uses
    instead of inventing a second vocabulary.
    """

    def __init__(self, code: str, message: str,
                 detail: Mapping[str, Any] | None = None) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.detail = dict(detail or {})
        self.refusal: Refusal = refusal(
            _REFUSAL_OUTCOMES.get(code, UNSAFE),
            reason_code=code, message=message, detail=self.detail)


# --------------------------------------------------------------------------
# The owner-approved list
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ApprovedModels:
    """The ordered owner-approved model ids, read ONLY from protected config.

    `entries` may be EMPTY, and empty is the honest representation of "the owner
    has not approved anything in this config". It is never repaired, defaulted,
    or extended: `source` records which file the list came from (or stays empty
    when no section existed) so a refusal can tell the owner exactly which file
    to populate.

    Membership is EXACT string equality. Nothing here normalizes, aliases,
    trims, or resolves an id, so a listed entry can never become a different
    model and an unlisted id can never become a listed one.
    """

    entries: tuple[str, ...] = ()
    source: str = ""

    def __bool__(self) -> bool:
        return bool(self.entries)

    def __contains__(self, model: object) -> bool:
        return any(model == entry for entry in self.entries)

    def __iter__(self):
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def index_of(self, model: str) -> int:
        for position, entry in enumerate(self.entries):
            if entry == model:
                return position
        return -1

    def candidates_after(self, model: str) -> tuple[str, ...]:
        """The approved entries to try after `model`, in the owner's order.

        When `model` IS approved the walk resumes at the next entry. When it is
        not (a pin the owner never listed), the walk starts at the head but never
        re-offers the id that just failed. Either way every returned id came out
        of the approved list, so nothing outside it is ever a candidate.
        """
        position = self.index_of(model)
        if position >= 0:
            return self.entries[position + 1:]
        return tuple(entry for entry in self.entries if entry != model)

    def assert_populated(self) -> None:
        """Refuse every selection act while the approved list is empty."""
        if self.entries:
            return
        raise ModelRoutingError(
            APPROVED_MODELS_EMPTY,
            f"no model is owner-approved: the immutable controller config declares no "
            f"[{APPROVED_MODELS_SECTION}] {APPROVED_MODELS_KEY} list, so the approved chain "
            f"is EMPTY and nothing is selectable. There is deliberately no built-in default "
            f"chain (D-023-R013): populate the protected config through the S13.1 "
            f"controller-update process and restart. The run stops safely rather than "
            f"choosing a model the owner did not approve",
            {"source": self.source or "(no [%s] section)" % APPROVED_MODELS_SECTION})

    def assert_listed(self, model: str) -> None:
        """Refuse any id that is not on the owner-approved list (exact match)."""
        self.assert_populated()
        if model in self:
            return
        raise ModelRoutingError(
            MODEL_NOT_APPROVED,
            f"{model!r} is not in the owner-approved model list {list(self.entries)}; an "
            f"unlisted id is never selectable by any path - not a code default, not a "
            f"settings fallback, not a Remote Control switch, and not a provider "
            f"convenience - no matter what a model picker shows (D-023-R013)",
            {"model": model, "approved": list(self.entries), "source": self.source})


# --------------------------------------------------------------------------
# The exact-id LIVE LAUNCH PROBE seam
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ProbeOutcome:
    """What one exact-id live launch probe reported.

    `ok` False is a refusal input, never a retry hint: the router records the
    outcome and moves to the next approved entry (or stops), it never re-probes
    the same id in a loop.
    """

    ok: bool
    cli_version: str = ""
    reason_code: str = ""
    detail: str = ""


#: The injected probe seam: attempt an ACTUAL launch of this EXACT model id and
#: report what happened. Never a model-picker read (D-004-R752/R753), never a
#: capability guess. Production supplies a real launcher; tests supply a fake.
LiveLaunchProbe = Callable[[str], ProbeOutcome]


@dataclasses.dataclass(frozen=True)
class ProbeRecord:
    """A durably recorded probe result, bound to the identity it was taken under.

    The binding is the whole point: a probe that succeeded under a different
    controller config or a different provider CLI proves nothing about this one,
    so `matches` compares both before the record may authorize a selection.
    """

    model_id: str
    ok: bool
    cli_version: str
    config_identity: str
    probed_at_utc: str
    reason_code: str = ""
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ProbeRecord | None":
        if not isinstance(data, Mapping):
            return None
        try:
            return cls(
                model_id=str(data["model_id"]),
                ok=bool(data["ok"]),
                cli_version=str(data.get("cli_version", "")),
                config_identity=str(data.get("config_identity", "")),
                probed_at_utc=str(data.get("probed_at_utc", "")),
                reason_code=str(data.get("reason_code", "")),
                detail=str(data.get("detail", "")),
            )
        except (KeyError, TypeError, ValueError):
            # An unreadable record proves nothing; treat it as absent so the
            # model stays unprobed rather than becoming selectable on garbage.
            return None

    def matches(self, *, config_identity: str, cli_version: str) -> bool:
        return (self.config_identity == config_identity
                and self.cli_version == cli_version)


class ProbeLedger:
    """Durable storage for exact-id live launch probe results.

    One record per model id, replaced whenever a newer probe is taken. Reads fail
    closed: an unreadable store, a record from another config identity, and a
    record from another CLI version all read as "no probe", which makes the model
    unselectable rather than selectable-on-stale-evidence.
    """

    def __init__(self, journal: Any, *, config_identity: str,
                 cli_version: str) -> None:
        self.journal = journal
        self.config_identity = str(config_identity or "")
        self.cli_version = str(cli_version or "")

    def _raw(self) -> dict[str, Any]:
        data = self.journal.get_state(PROBE_LEDGER_KEY, {})
        return dict(data) if isinstance(data, Mapping) else {}

    def record(self, model_id: str, outcome: ProbeOutcome) -> ProbeRecord:
        """Persist one probe result under the identity it was taken with."""
        record = ProbeRecord(
            model_id=model_id,
            ok=bool(outcome.ok),
            # The probe reports the CLI it actually reached; when it reports
            # nothing the ledger's own identity is recorded, never invented.
            cli_version=str(outcome.cli_version or self.cli_version),
            config_identity=self.config_identity,
            probed_at_utc=to_utc_iso(),
            reason_code=str(outcome.reason_code or ""),
            detail=str(outcome.detail or ""),
        )
        store = self._raw()
        store[model_id] = record.to_dict()
        self.journal.set_state(PROBE_LEDGER_KEY, store)
        return record

    def recorded(self, model_id: str) -> ProbeRecord | None:
        """The recorded probe for THIS identity, or None (fail closed)."""
        record = ProbeRecord.from_dict(self._raw().get(model_id))
        if record is None:
            return None
        if not record.matches(config_identity=self.config_identity,
                              cli_version=self.cli_version):
            return None
        return record

    def successful(self, model_id: str) -> ProbeRecord | None:
        record = self.recorded(model_id)
        return record if record is not None and record.ok else None

    def all_records(self) -> tuple[ProbeRecord, ...]:
        found = [ProbeRecord.from_dict(value) for value in self._raw().values()]
        return tuple(record for record in found if record is not None)


# --------------------------------------------------------------------------
# The router
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class SelectedModel:
    """One approved, probed model plus the evidence that authorized it."""

    model_id: str
    position: int
    probe: ProbeRecord
    attempts: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "position": self.position,
            "probe": self.probe.to_dict(),
            "attempts": [dict(a) for a in self.attempts],
        }


class ModelRouter:
    """Selects a model from the owner-approved list, proved by a live probe.

    There are exactly two selection acts, `select` (this exact id) and
    `next_after` (walk the approved order from the entry after a failed one).
    Both apply the same two gates in the same order: LISTED, then PROBED. Neither
    can return an id the owner did not approve, and neither can return an id with
    no recorded successful probe for the current config identity and CLI version.
    """

    def __init__(
        self,
        *,
        approved: ApprovedModels,
        ledger: ProbeLedger,
        probe: LiveLaunchProbe | None = None,
    ) -> None:
        self.approved = approved
        self.ledger = ledger
        self._probe = probe

    # -- the probe gate ------------------------------------------------------

    def probe_record(self, model_id: str) -> ProbeRecord:
        """A SUCCESSFUL probe record for `model_id`, probing live if needed.

        Uses a recorded success when one exists for this exact identity;
        otherwise runs the injected probe ONCE and records the result. With no
        probe seam injected the model is not selectable at all - an absent seam
        is never read as "assume it launches".
        """
        recorded = self.ledger.successful(model_id)
        if recorded is not None:
            return recorded
        if self._probe is None:
            raise ModelRoutingError(
                PROBE_SEAM_MISSING,
                f"{model_id!r} has no recorded successful launch probe for this controller "
                f"config identity and no live probe seam is wired, so its availability is "
                f"UNKNOWN. An unprobed model is never selected on the strength of the "
                f"approved list alone (D-004-R752: availability is decided by an actual "
                f"launch, never by reading a model picker)",
                {"model": model_id, "config_identity": self.ledger.config_identity})
        try:
            outcome = self._probe(model_id)
        except Exception as exc:  # a probe that raised proves nothing
            outcome = ProbeOutcome(ok=False, reason_code="probe_error",
                                   detail=f"the live launch probe raised: {exc}")
        if not isinstance(outcome, ProbeOutcome):
            outcome = ProbeOutcome(
                ok=bool(outcome), reason_code="probe_shape",
                detail="the probe seam returned a non-ProbeOutcome value")
        record = self.ledger.record(model_id, outcome)
        if not record.ok:
            raise ModelRoutingError(
                MODEL_PROBE_FAILED,
                f"the exact-id live launch probe for {model_id!r} did not come up "
                f"({record.reason_code or 'no reason reported'}: "
                f"{record.detail or 'no detail'}); the model is not selectable and no "
                f"substitute is chosen for it",
                {"model": model_id, "reason_code": record.reason_code,
                 "detail": record.detail})
        return record

    # -- the two selection acts ---------------------------------------------

    def select(self, model_id: str) -> SelectedModel:
        """This EXACT id, if the owner approved it and a live probe proved it."""
        self.approved.assert_listed(model_id)
        record = self.probe_record(model_id)
        return SelectedModel(model_id=model_id,
                             position=self.approved.index_of(model_id),
                             probe=record)

    def next_after(self, model_id: str) -> SelectedModel:
        """The first approved entry after `model_id` that a live probe brings up.

        Walks the owner's order, records every attempt, and stops at the first
        success. Reaching the end of the list is `approved_chain_exhausted` - a
        typed SAFE STOP that names every id tried, never a fallback to something
        unlisted and never a silent continue on the failed model.
        """
        self.approved.assert_populated()
        attempts: list[dict[str, Any]] = []
        for candidate in self.approved.candidates_after(model_id):
            try:
                record = self.probe_record(candidate)
            except ModelRoutingError as exc:
                attempts.append({"model": candidate, "available": False,
                                 "reason_code": exc.code})
                continue
            attempts.append({"model": candidate, "available": True,
                             "reason_code": "", "probed_at_utc": record.probed_at_utc})
            return SelectedModel(model_id=candidate,
                                 position=self.approved.index_of(candidate),
                                 probe=record, attempts=tuple(attempts))
        raise ModelRoutingError(
            APPROVED_CHAIN_EXHAUSTED,
            f"no entry in the owner-approved model list {list(self.approved.entries)} came "
            f"up after {model_id!r}; the run STOPS rather than continuing on an unlisted or "
            f"substitute model (D-023-R013). Every candidate was tried by an actual launch "
            f"probe, and exhaustion of the approved chain is a safe stop, not a fallback",
            {"exhausted_model": model_id, "approved": list(self.approved.entries),
             "attempts": attempts})


def probe_report(ledger: ProbeLedger) -> list[dict[str, Any]]:
    """The recorded probe evidence, as data (`doctor` prints it)."""
    return [record.to_dict() for record in sorted(
        ledger.all_records(), key=lambda item: item.model_id)]


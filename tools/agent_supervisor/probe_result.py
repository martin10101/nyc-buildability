#!/usr/bin/env python3
"""The probe result vocabulary, and the one place the fail-closed rule lives.

Every pre-dispatch probe answers with a `ProbeResult`, and `passes` is the ONLY
place that decides what "passed" means: `ok AND known`. "I could not determine
this" is a failure, never a shrug. Keeping that judgement in one small module -
rather than in whichever file happens to hold a probe - is what lets the
repository probes, the control-plane probes, and the journal probes all be split
apart without any of them re-deciding it.

Split out of `recovery_probes.py` by the M0-T079 correction round (C8 grew the
control-plane half past the point where one module was still one responsibility).
"""
from __future__ import annotations

import dataclasses
from typing import Any, Mapping, Sequence


@dataclasses.dataclass(frozen=True)
class ProbeResult:
    """One revalidation answer, and whether it was actually established.

    `known=False` means the probe could not determine the fact. That is NOT a
    pass, and `passes` is the only place that judgement is made.
    """

    step: str
    ok: bool
    known: bool = True
    reason_code: str = ""
    detail: str = ""
    evidence: Mapping[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "evidence", dict(self.evidence or {}))

    @property
    def passes(self) -> bool:
        """A probe passes only when it is BOTH established and satisfied."""
        return bool(self.ok and self.known)

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["passes"] = self.passes
        return data


def _ok(step: str, detail: str, **evidence: Any) -> ProbeResult:
    return ProbeResult(step, True, True, "", detail, evidence)


def _fail(step: str, reason_code: str, detail: str, **evidence: Any) -> ProbeResult:
    return ProbeResult(step, False, True, reason_code, detail, evidence)


def _unknown(step: str, reason_code: str, detail: str, **evidence: Any) -> ProbeResult:
    """An UNDETERMINED fact. Fails closed exactly like a failed one."""
    return ProbeResult(step, False, False, reason_code, detail, evidence)


@dataclasses.dataclass(frozen=True)
class ProbeReport:
    """Every probe this start ran, and the revalidation map recovery consumes."""

    results: tuple[ProbeResult, ...]

    def by_step(self) -> dict[str, ProbeResult]:
        return {result.step: result for result in self.results}

    def revalidation(self, steps: Sequence[str]) -> dict[str, bool]:
        """The `{step: bool}` map for `recover_boot`, restricted to `steps`.

        A step this report has no result for is simply ABSENT, and
        `recovery.classify` already treats a missing result as a failed check -
        so an unrun probe can never be mistaken for a passed one.
        """
        answers = self.by_step()
        return {step: answers[step].passes for step in steps if step in answers}

    def failures(self) -> tuple[ProbeResult, ...]:
        return tuple(r for r in self.results if not r.passes)

    def to_dict(self) -> dict[str, Any]:
        return {"probes": [r.to_dict() for r in self.results],
                "failed": [r.step for r in self.failures()]}


def ok_probe(step: str, detail: str, **evidence: Any) -> ProbeResult:
    return ProbeResult(step, True, True, "", detail, evidence)


def fail_probe(step: str, reason_code: str, detail: str, **evidence: Any) -> ProbeResult:
    return ProbeResult(step, False, True, reason_code, detail, evidence)


def unknown_probe(step: str, reason_code: str, detail: str,
                  **evidence: Any) -> ProbeResult:
    """An UNDETERMINED fact. Fails closed exactly like a determined failure."""
    return ProbeResult(step, False, False, reason_code, detail, evidence)

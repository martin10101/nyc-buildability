#!/usr/bin/env python3
"""Fable 5 guardrail-refusal DETECTION core (M0-T093, D-024 Phase E).

Supervisor-freeze qualifying evidence: **D-024-R103** (Phase E; packet-named).

This module is the DISTINCT classifier D-024-R068 requires: it recognizes the
narrowly recognized Fable 5 guardrail-refusal shape and NOTHING else. It is
PURE DETECTION only - no process launching, no journal writes, no live provider
calls, no I/O beyond reading its committed fixture corpus, and no third-party
dependencies (mirroring `model_turnover`'s stance). Actuation lives behind the
`refusal_bridge` policy layer and is record-intent-only on this build.

R075 governs its relationship to the quota/limit policies: the guardrail-
refusal policy and the quota detect-and-hold policy keep DISTINCT triggers,
counters, states, and typed codes, and never cross-actuate IN EITHER
DIRECTION. This classifier therefore:

* delegates the quota direction to the EXISTING classifiers first - a signal
  `model_turnover.classify_exhaustion` confirms as exhaustion, or that even
  LOOKS limit/quota-shaped, is never classified as a guardrail refusal;
* REUSES `model_turnover`'s negative-guard patterns and normalization
  (D-024-R018: prove and extend, never duplicate) while owning its OWN
  recognized-shape corpus, verdict types, and condition codes.

The one rule on every path is FAIL-CLOSED (AD-025): unknown, ambiguous,
contradictory, refusal-LOOKING-but-unrecognized, unattributable, or
authorization-unproven evidence is NEVER classified as a guardrail refusal.
Only the exact recognized shape, attributable to Fable, for a PROVEN
owner-authorized task, classifies - and even then, this build only records
intent (live actuation is owner-gated: R595 activation plus a measured-live
C1 shape capture, neither of which exists here).
"""
from __future__ import annotations

import dataclasses
import enum
import json
import pathlib
import re
from typing import Any, Mapping

from .model_turnover import (
    LIMIT_HINT_PATTERN,
    TurnoverEvidence,
    classify_exhaustion,
    normalize_output_text,
    references_fable,
)
from .model_turnover import (
    PERMISSION_DENIED_PATTERN as _PERMISSION_DENIED,
)

# --------------------------------------------------------------------------
# Typed verdicts and condition codes (distinct from every quota-side code,
# D-024-R075 / R184: refusal and quota triggers remain distinct end-to-end)
# --------------------------------------------------------------------------


class RefusalClassification(enum.Enum):
    """The typed outcome of a guardrail-refusal detection decision.

    * ``GUARDRAIL_REFUSAL`` - the narrowly recognized Fable 5 guardrail-refusal
      shape, attributable to Fable, for a proven owner-authorized task. The
      ONLY value that permits even a record-intent bridge event.
    * ``NOT_A_REFUSAL`` - a recognized non-refusal condition (quota-side
      signal, permission denial, credential boundary, security-defect signal,
      unknown approval prompt, or an ordinary result). Handled by its own
      existing policy; the bridge never actuates on it.
    * ``AMBIGUOUS_FAIL_CLOSED`` - unknown, contradictory, unattributable,
      authorization-unproven, or refusal-LOOKING-but-unrecognized evidence.
      Never actuates; recorded and held for review.
    """

    GUARDRAIL_REFUSAL = "guardrail_refusal"
    NOT_A_REFUSAL = "not_a_refusal"
    AMBIGUOUS_FAIL_CLOSED = "ambiguous_fail_closed"


#: Condition codes carried on every verdict. A closed, typed vocabulary so the
#: bridge, journal entries, and tests can treat each condition mechanically.
#: None of these collides with a quota-side reason code (R075/R184).
CONDITION_RECOGNIZED = "recognized_guardrail_refusal"
CONDITION_QUOTA_POLICY = "quota_policy_owns_signal"
CONDITION_PERMISSION_DENIED = "permission_denied_not_refusal"
CONDITION_CREDENTIAL_BOUNDARY = "credential_boundary_not_refusal"
CONDITION_SECURITY_DEFECT = "security_defect_not_refusal"
CONDITION_APPROVAL_PROMPT = "unknown_approval_prompt_not_refusal"
CONDITION_REFUSAL_UNRECOGNIZED = "refusal_looking_unrecognized"
CONDITION_NOT_ATTRIBUTABLE = "not_attributable_to_fable"
CONDITION_AUTHORIZATION_UNPROVEN = "task_authorization_unproven"
CONDITION_CONTRADICTORY = "contradictory_signals"
CONDITION_ORDINARY = "ordinary_result"
CONDITION_UNINSPECTABLE = "evidence_uninspectable"


@dataclasses.dataclass(frozen=True)
class RefusalEvidence:
    """The structured evidence a refusal decision is made from.

    Mirrors `model_turnover.TurnoverEvidence`'s style (every field defaults to
    an "absent" value) but is deliberately its OWN type: R075 keeps the two
    policies' surfaces distinct so a quota evidence object can never be
    accidentally routed into the refusal policy by type confusion.
    """

    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    structured_result: Mapping[str, Any] | None = None
    model_id: str = ""


@dataclasses.dataclass(frozen=True)
class AuthorizedTaskRecord:
    """The proof that the refused request's underlying task is legitimate.

    R068 permits classification as a routing event only while "the underlying
    owner-authorized task remains legitimate". Legitimacy is NEVER inferred
    from the worker's output text: it comes from the task packet the
    controller already holds - identity, the exact authorization, and the
    exact acceptance criteria (R070 step 1 preserves all three).
    """

    task_id: str
    authorization: str
    acceptance_criteria: tuple[str, ...] = ()
    purpose: str = ""

    @property
    def proven(self) -> bool:
        """True only when identity, authorization, AND criteria are present."""
        return bool(self.task_id.strip() and self.authorization.strip()
                    and self.acceptance_criteria)


@dataclasses.dataclass(frozen=True)
class RefusalVerdict:
    """A classification plus the typed condition and the reason it was reached."""

    classification: RefusalClassification
    condition: str
    reason: str
    matched_shape: str = ""
    shape_verified_live: bool = False

    @property
    def is_recognized_refusal(self) -> bool:
        """True ONLY for the recognized refusal; every other verdict is False."""
        return self.classification is RefusalClassification.GUARDRAIL_REFUSAL


# --------------------------------------------------------------------------
# The recognized-shape corpus (documentation-confidence until the owner-gated
# C1 live capture; mirrors claude_runner's QuotaSignalFixture discipline)
# --------------------------------------------------------------------------

#: Where the committed corpus lives. Missing or malformed -> EMPTY corpus,
#: so nothing is ever recognized (fail closed), never a guess.
#: M0-T118 (D-024-R281 Amendment 13): re-pointed 2_1_248 -> 2_1_251 for the
#: deliberate 2.1.251 admission. The corpus and its (still-unverified)
#: confidence labels are carried forward unchanged; only the base CLI version
#: is updated. The 2_1_248 fixture stays committed as append-only history.
SHAPES_FIXTURE_PATH = (pathlib.Path(__file__).resolve().parent / "fixtures"
                       / "guardrail_refusal_shapes_2_1_251.json")


@dataclasses.dataclass(frozen=True)
class RefusalShapeFixture:
    """One recorded shape that MIGHT be the recognized Fable guardrail refusal.

    A shape is authoritative for LIVE actuation only when ``verified_live`` is
    True (exact bytes captured from a real refusal on the recorded
    ``cli_version`` under the owner-gated C1 canary). A ``verified_live=False``
    shape is a DOCUMENTED CANDIDATE: it may classify for record-intent
    purposes, but `refusal_bridge.assert_actuation_permitted` refuses live
    actuation on it.
    """

    name: str
    structured_value: str = ""
    structured_keys: tuple[str, ...] = ()
    text_regex: str | None = None
    cli_version: str = ""
    verified_live: bool = False
    provenance: str = ""

    def matches(self, text: str, structured_result: Mapping[str, Any] | None) -> bool:
        """True when this shape recognizes (text, structured_result).

        Fail-closed on malformed input, and an EMPTY shape (no structured
        value and no regex) matches nothing - never a catch-all.
        """
        matched_any = False
        if self.structured_value and self.structured_keys:
            if not _structured_value_present(structured_result,
                                             self.structured_keys,
                                             self.structured_value):
                return False
            matched_any = True
        if self.text_regex is not None:
            if not isinstance(text, str):
                return False
            if re.search(self.text_regex, text, re.IGNORECASE) is None:
                return False
            matched_any = True
        return matched_any


def _structured_value_present(structured_result: Any,
                              keys: tuple[str, ...], value: str) -> bool:
    """Exact typed-value scan, one nested mapping level deep (the
    `model_turnover._structured_signal` key-scan convention)."""
    if not isinstance(structured_result, Mapping):
        return False
    want = value.strip().lower()
    for key in keys:
        found = structured_result.get(key)
        if isinstance(found, str) and found.strip().lower() == want:
            return True
        if isinstance(found, Mapping):
            for nested_key in keys:
                nested = found.get(nested_key)
                if isinstance(nested, str) and nested.strip().lower() == want:
                    return True
    return False


def load_shape_corpus(
    path: pathlib.Path | str | None = None,
) -> tuple[RefusalShapeFixture, ...]:
    """Load the committed recognized-shape corpus. FAIL-CLOSED: a missing,
    unreadable, or malformed file yields the EMPTY corpus, so nothing is ever
    recognized rather than something being guessed."""
    target = pathlib.Path(path) if path is not None else SHAPES_FIXTURE_PATH
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
        shapes = raw.get("recognized_shapes", [])
        if not isinstance(shapes, list):
            return ()
        corpus: list[RefusalShapeFixture] = []
        for entry in shapes:
            if not isinstance(entry, Mapping) or not entry.get("name"):
                return ()  # one malformed entry poisons the file: refuse all
            corpus.append(RefusalShapeFixture(
                name=str(entry["name"]),
                structured_value=str(entry.get("structured_value") or ""),
                structured_keys=tuple(str(k) for k in
                                      (entry.get("structured_keys") or ())),
                text_regex=(str(entry["text_regex"])
                            if entry.get("text_regex") else None),
                cli_version=str(entry.get("cli_version") or ""),
                verified_live=entry.get("verified_live") is True,
                provenance=str(entry.get("provenance") or "")))
        return tuple(corpus)
    except Exception:
        return ()


#: The production corpus, loaded once at import from the committed fixture.
RECOGNIZED_SHAPES: tuple[RefusalShapeFixture, ...] = load_shape_corpus()

#: Derived so the flag and the corpus can never disagree (the
#: QUOTA_EXHAUSTION_SIGNAL_VERIFIED convention). False until the owner-gated
#: C1 canary captures a live shape.
REFUSAL_SHAPE_VERIFIED = any(f.verified_live for f in RECOGNIZED_SHAPES)


# --------------------------------------------------------------------------
# This module's OWN negative-guard patterns (documented conservative sets).
# The quota/limit and permission guards are REUSED from model_turnover.
# --------------------------------------------------------------------------

#: A real failing test / security-scan / defect signal - a defect, never a
#: routing event (R068 "never confuse it with a real security defect, a
#: failed test").
_SECURITY_DEFECT = re.compile(
    r"(assertionerror|traceback \(most recent call last\)|"
    r"\b\d+ (?:tests? )?failed\b|\btests? failed\b|"
    r"\bsecurity (?:test|scan|review) (?:failed|violation)\b|"
    r"\bgitleaks\b|\bvulnerabilit(?:y|ies) (?:found|detected)\b)",
    re.IGNORECASE)

#: A credential / repository-policy boundary - an access-control fact, never a
#: refusal (R068 "a credential/repository-policy boundary").
_CREDENTIAL_BOUNDARY = re.compile(
    r"(\bcredentials?\b|\bapi[- _]?key\b|\bauthentication (?:required|failed)\b|"
    r"\blogin required\b|\bunauthorized\b|\b401\b|\b403\b|\bforbidden\b|"
    r"\btoken (?:expired|invalid|missing)\b|\bbranch protection\b)",
    re.IGNORECASE)

#: An interactive approval/permission/confirmation prompt of unknown kind -
#: NEVER auto-answered (R068/R069): only the exact allowlisted continuation
#: option is ever selectable, and that selection happens in refusal_bridge,
#: not here.
_APPROVAL_PROMPT = re.compile(
    r"(do you want to (?:allow|proceed|continue)|"
    r"permission (?:request|prompt|needed)|\ballow this\b|"
    r"\(y/n\)|\[y/n\]|\byes/no\b|waiting for (?:your )?approval|"
    r"\bconfirm(?:ation)? (?:required|needed)\b)",
    re.IGNORECASE)

#: Refusal-LOOKING wording that is NOT a recognized shape. Its presence makes
#: the evidence AMBIGUOUS (held for review), never a recognized refusal
#: (D-024-R068 narrowness; scenario S3).
_REFUSAL_HINT = re.compile(
    r"(i can(?:no|')t (?:help|assist|comply)|"
    r"i(?:'m| am) (?:unable|not able) to (?:help|assist|comply|respond|continue)|"
    r"\bunable to (?:help|assist|comply|respond)\b|"
    r"declin(?:e|es|ed|ing) to|"
    r"will not (?:help|assist|comply|create|provide)|"
    r"cannot (?:help|assist|comply) with)",
    re.IGNORECASE)


def _verdict(classification: RefusalClassification, condition: str,
             reason: str, *, matched_shape: str = "",
             shape_verified_live: bool = False) -> RefusalVerdict:
    return RefusalVerdict(classification, condition, reason,
                          matched_shape=matched_shape,
                          shape_verified_live=shape_verified_live)


def classify_guardrail_refusal(
    evidence: Any,
    *,
    authorized_task: AuthorizedTaskRecord | None,
    corpus: tuple[RefusalShapeFixture, ...] | None = None,
) -> RefusalVerdict:
    """Classify evidence into a typed, fail-closed guardrail-refusal verdict.

    Decision order (fail-closed throughout; R068/R075):

    1. No/uninspectable evidence -> AMBIGUOUS.
    2. QUOTA DIRECTION FIRST (R075): evidence the existing quota classifier
       confirms as Fable exhaustion belongs to the separate live
       detect-and-hold policy -> NOT_A_REFUSAL (quota_policy_owns_signal).
    3. Recognized-shape scan against the committed corpus. A match that
       CO-OCCURS with any negative-guard signal (limit/quota wording,
       permission denial, credential boundary, defect signal, approval
       prompt) is CONTRADICTORY -> AMBIGUOUS, never trusted.
       A clean match must also be attributable to Fable AND carry a PROVEN
       owner-authorized task record; only then -> GUARDRAIL_REFUSAL.
    4. No recognized shape: each negative guard classifies to its own
       existing policy (NOT_A_REFUSAL with a typed condition); refusal-
       LOOKING wording -> AMBIGUOUS (held for review); otherwise an
       ordinary result -> NOT_A_REFUSAL.

    Never raises: any unexpected input degrades to AMBIGUOUS_FAIL_CLOSED
    (a classifier that crashed mid-decision would be a fail-open shape).
    """
    try:
        if evidence is None:
            return _verdict(
                RefusalClassification.AMBIGUOUS_FAIL_CLOSED,
                CONDITION_UNINSPECTABLE,
                "no evidence object was supplied; insufficient evidence to classify")

        stdout = normalize_output_text(getattr(evidence, "stdout", ""))
        stderr = normalize_output_text(getattr(evidence, "stderr", ""))
        exit_code = getattr(evidence, "exit_code", None)
        structured_result = getattr(evidence, "structured_result", None)
        if not isinstance(structured_result, Mapping):
            structured_result = None
        model_id = str(getattr(evidence, "model_id", "") or "")
        text = f"{stdout}\n{stderr}"

        # 2. Quota direction first (R075): confirmed exhaustion belongs to the
        # separate detect-and-hold policy and can NEVER enter this one.
        quota_verdict = classify_exhaustion(TurnoverEvidence(
            stdout=stdout, stderr=stderr, exit_code=exit_code,
            structured_result=structured_result, model_id=model_id))
        if quota_verdict.should_turn_over:
            return _verdict(
                RefusalClassification.NOT_A_REFUSAL, CONDITION_QUOTA_POLICY,
                "the existing quota classifier confirms a Fable usage-limit "
                "exhaustion; the SEPARATE live detect-and-hold quota policy owns "
                "this signal and the guardrail bridge never actuates on it "
                f"(D-024-R075): {quota_verdict.reason}")

        # 3. Recognized-shape scan.
        shapes = RECOGNIZED_SHAPES if corpus is None else corpus
        matched: RefusalShapeFixture | None = None
        for shape in shapes:
            if shape.matches(text, structured_result):
                matched = shape
                break

        if matched is not None:
            contradiction = _co_occurring_signal(text)
            if contradiction:
                return _verdict(
                    RefusalClassification.AMBIGUOUS_FAIL_CLOSED,
                    CONDITION_CONTRADICTORY,
                    f"the recognized refusal shape {matched.name!r} co-occurs "
                    f"with a {contradiction} signal; contradictory evidence is "
                    f"never trusted as a guardrail refusal")
            if not references_fable(structured_result, model_id):
                return _verdict(
                    RefusalClassification.AMBIGUOUS_FAIL_CLOSED,
                    CONDITION_NOT_ATTRIBUTABLE,
                    f"the recognized refusal shape {matched.name!r} cannot be "
                    f"attributed to the Fable model, so it cannot enter the "
                    f"Fable guardrail-refusal policy")
            if authorized_task is None or not authorized_task.proven:
                return _verdict(
                    RefusalClassification.AMBIGUOUS_FAIL_CLOSED,
                    CONDITION_AUTHORIZATION_UNPROVEN,
                    "the refusal shape is recognized but the underlying task's "
                    "owner authorization is not proven (task identity, exact "
                    "authorization, and acceptance criteria are required, "
                    "D-024-R068/R070); a possibly prohibited request is never "
                    "routed")
            return _verdict(
                RefusalClassification.GUARDRAIL_REFUSAL, CONDITION_RECOGNIZED,
                f"the narrowly recognized guardrail-refusal shape "
                f"{matched.name!r} matched ("
                f"{'measured-live' if matched.verified_live else 'documented candidate'}"
                f"), is attributable to Fable, and the owner-authorized task "
                f"{authorized_task.task_id!r} remains legitimate (D-024-R068)",
                matched_shape=matched.name,
                shape_verified_live=matched.verified_live)

        # 4. No recognized shape: route each negative guard to its own policy.
        if LIMIT_HINT_PATTERN.search(text):
            return _verdict(
                RefusalClassification.NOT_A_REFUSAL, CONDITION_QUOTA_POLICY,
                "limit/quota-looking wording is present and no refusal shape "
                "matched; the quota policies' own fail-closed handling governs "
                "this signal, never the guardrail bridge (D-024-R075)")
        if _PERMISSION_DENIED.search(text):
            return _verdict(
                RefusalClassification.NOT_A_REFUSAL, CONDITION_PERMISSION_DENIED,
                "a permission-denied signal is an ordinary access failure, "
                "never a guardrail refusal (D-024-R068)")
        if _CREDENTIAL_BOUNDARY.search(text):
            return _verdict(
                RefusalClassification.NOT_A_REFUSAL,
                CONDITION_CREDENTIAL_BOUNDARY,
                "a credential/repository-policy boundary is an access-control "
                "fact, never a guardrail refusal (D-024-R068)")
        if _SECURITY_DEFECT.search(text):
            return _verdict(
                RefusalClassification.NOT_A_REFUSAL, CONDITION_SECURITY_DEFECT,
                "a failing test / security-defect signal is a defect to fix, "
                "never a model-routing event (D-024-R068)")
        if _APPROVAL_PROMPT.search(text):
            return _verdict(
                RefusalClassification.NOT_A_REFUSAL, CONDITION_APPROVAL_PROMPT,
                "an unknown approval/permission/confirmation prompt is NEVER "
                "automatically answered; it is not a guardrail refusal and "
                "only the exact allowlisted continuation option is ever "
                "selectable (D-024-R068/R069)")
        if _REFUSAL_HINT.search(text):
            return _verdict(
                RefusalClassification.AMBIGUOUS_FAIL_CLOSED,
                CONDITION_REFUSAL_UNRECOGNIZED,
                "refusal-looking wording is present but matches no recognized "
                "shape; conservative unknown - recorded and held for review, "
                "never actuated (D-024-R068)")
        return _verdict(
            RefusalClassification.NOT_A_REFUSAL, CONDITION_ORDINARY,
            "no refusal signal is present; an ordinary result follows its "
            "ordinary handling")
    except Exception:  # pragma: no cover - defensive: unknown, never a crash
        return _verdict(
            RefusalClassification.AMBIGUOUS_FAIL_CLOSED, CONDITION_UNINSPECTABLE,
            "the evidence could not be inspected; failing closed to ambiguous")


def _co_occurring_signal(text: str) -> str:
    """Name the negative-guard signal co-occurring with a recognized shape,
    or "" when the text is clean. Any such co-occurrence is contradictory."""
    if LIMIT_HINT_PATTERN.search(text):
        return "limit/quota"
    if _PERMISSION_DENIED.search(text):
        return "permission-denied"
    if _CREDENTIAL_BOUNDARY.search(text):
        return "credential-boundary"
    if _SECURITY_DEFECT.search(text):
        return "security-defect"
    if _APPROVAL_PROMPT.search(text):
        return "approval-prompt"
    return ""

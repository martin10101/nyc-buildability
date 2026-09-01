#!/usr/bin/env python3
"""Checkpoint construction/validation + the shared runner-error base, extracted
from ``claude_runner.py`` (M0-T134 / D-024 Amendment 39 R509).

This is a genuine extraction, not a ceiling renewal: it reduces claude_runner.py
from 1432 to 1319 SLOC, back UNDER its recorded 1410 exception ceiling. The
exception entry itself is deliberately RETAINED byte-identical to 6f5d12a6 (per
R493/R500) - it is neither renewed (the ceiling is not raised) nor deleted; it now
simply sits above the file's current size and can be retired in a later governance
step. So the modularity gate passes because of the split, not a policy-file edit.

This is the "shared module" the M0-T133 exception scheduled. It holds:

* the ``RunnerError`` hierarchy (relocated here so ``cli.py``'s existing
  ``except RunnerError`` keeps working unchanged through the ``claude_runner``
  facade re-export - the base of ``CheckpointError`` had to move first so the
  checkpoint helpers could follow without a circular import), and
* the S8.3 checkpoint find / validate / extract helpers.

Behavior is byte-identical to the pre-split ``claude_runner`` definitions; this
module only relocates them. Everything Claude emits - narrative, summaries,
command output, checkpoint text - is untrusted data; these functions never derive
an action from it, they only parse and fail closed.

Import direction is one-way: ``claude_runner`` imports from here (and re-exports
these names for its consumers); this module imports only from ``.models`` and the
standard library, so no cycle can form.
"""
from __future__ import annotations

import json
import re
from typing import Any, Mapping, Sequence

from .models import ClaudeCheckpoint, RecordError, digest_of


class RunnerError(Exception):
    """The worker adapter refused to run, or the run could not be trusted."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class CheckpointError(RunnerError):
    """Output was missing, invalid, truncated, or conflicting.

    S8.3: invalid, truncated, or nonconforming output is NEVER forwarded as
    success.
    """


_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def _json_candidates(text: str) -> list[dict[str, Any]]:
    """Every JSON object embedded in a block of model text."""
    found: list[dict[str, Any]] = []
    for body in _FENCE.findall(text):
        try:
            value = json.loads(body.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            found.append(value)
    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            pass
        else:
            if isinstance(value, dict):
                found.append(value)
    return found


def _event_text(event: Mapping[str, Any]) -> str:
    """Best-effort extraction of the human-readable text an event carries."""
    parts: list[str] = []
    result = event.get("result")
    if isinstance(result, str):
        parts.append(result)
    message = event.get("message")
    if isinstance(message, Mapping):
        content = message.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, Mapping) and isinstance(block.get("text"), str):
                    parts.append(block["text"])
    return "\n".join(parts)


def find_checkpoint_candidate(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Find the ONE structured checkpoint CANDIDATE dict (S8.3); does NOT validate it.

    Accepts the checkpoint as a bare event object, inside a `result` payload, or
    fenced inside assistant text. Duplicate delivery of an identical checkpoint is
    tolerated; the same checkpoint id with different content is a conflict and is
    refused rather than being resolved by preference. V1.1 correction B-3: two or
    more DISTINCT checkpoint ids in one unit are likewise refused rather than
    resolved by "last wins" - a prompt-injected worker must not be able to bury a
    real BLOCKED checkpoint under a rosier fabricated one.
    """
    candidates: list[dict[str, Any]] = []
    for event in events:
        if "checkpoint_id" in event and "schema_version" in event:
            candidates.append(dict(event))
        text = _event_text(event)
        if text:
            candidates.extend(_json_candidates(text))

    shaped = [c for c in candidates if "checkpoint_id" in c and "schema_version" in c]
    if not shaped:
        raise CheckpointError(
            "missing_checkpoint",
            "the run produced no structured checkpoint; a missing result is never "
            "interpreted as success (S14)")

    by_id: dict[str, dict[str, Any]] = {}
    for candidate in shaped:
        key = str(candidate.get("checkpoint_id"))
        previous = by_id.get(key)
        if previous is not None and digest_of(previous) != digest_of(candidate):
            raise CheckpointError(
                "conflicting_duplicate_checkpoint",
                f"checkpoint id {key!r} was delivered twice with different content; the "
                f"supervisor refuses to choose between them")
        by_id[key] = candidate

    if len(by_id) > 1:
        # V1.1 correction B-3: refuse-rather-than-choose, consistent with the
        # conflicting-duplicate rule above. The worker is untrusted (module
        # threat model); choosing the LAST of several distinct checkpoints would
        # let injected output drive the review correlation and provenance.
        raise CheckpointError(
            "multiple_distinct_checkpoints",
            f"the unit delivered {len(by_id)} DISTINCT checkpoints "
            f"({sorted(by_id)}); a bounded unit reports exactly ONE structured "
            f"checkpoint, and the supervisor refuses to choose between them")

    return shaped[-1]


def validate_checkpoint(chosen: Mapping[str, Any]) -> ClaudeCheckpoint:
    """Parse and validate one checkpoint dict into a `ClaudeCheckpoint` (S8.3).

    Separated from `find_checkpoint_candidate` so the controller can enrich the
    candidate's controller-authoritative git-state envelope fields (M0-T133,
    D-024 Amendment 37) between finding and validating, without duplicating the
    find/dedup logic. Unknown-field, missing-field, and shape violations remain a
    fail-closed `invalid_checkpoint`.
    """
    try:
        checkpoint = ClaudeCheckpoint.from_dict(chosen)
        checkpoint.validate()
    except RecordError as exc:
        raise CheckpointError("invalid_checkpoint",
                              f"the checkpoint does not conform: {exc}") from exc
    return checkpoint


def extract_checkpoint(events: Sequence[Mapping[str, Any]]) -> ClaudeCheckpoint:
    """Find and validate the ONE structured checkpoint (S8.3) - the composition used
    where no controller-authoritative envelope enrichment applies (e.g.
    `checkpoint_question_decided`, which only needs to know whether a candidate exists)."""
    return validate_checkpoint(find_checkpoint_candidate(events))


def checkpoint_question_decided(events: Sequence[Mapping[str, Any]]) -> bool:
    """True when the drained stream already ANSWERS the checkpoint question.

    M0-T130 (D-024-R421): the reserved-final-turn demand exists to obtain a
    checkpoint that is otherwise ABSENT. Any candidate at all - valid, invalid,
    or conflicting - means one more demanded turn cannot improve the verdict (a
    further candidate could only become another conflict), so only a stream
    with NO candidate (`missing_checkpoint`) warrants the injection.
    """
    try:
        extract_checkpoint(events)
    except CheckpointError as exc:
        return exc.code != "missing_checkpoint"
    return True

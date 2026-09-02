#!/usr/bin/env python3
"""Correlation-bound runtime identity at one-shot settlement (M0-T142;
D-024 Amendment 45 R686/R687/R690/R691).

Reproduced live defect (canary-b5-02r1, 2026-09-02): the settlement refused a
schema-valid WorkerResult with ``runtime reported no model`` because the old
check required the result's ``modelUsage`` to contain exactly one key. The
owner's official corrections: ``modelUsage`` is a SESSION-WIDE AGGREGATE over
the main loop, subagents, and CLI-internal calls (R686) - the live run showed
``{claude-opus-4-8, claude-haiku-4-5-20251001, claude-opus-4-8[1m]}`` while
every assistant turn (main 15/15 + sidechains 34/34 and 19/19) ran exactly the
pinned id - and ``[1m]`` is the real 1-million-context tier of the SAME model,
not decoration (R687).

The primary model is therefore proven from the CLI's session transcript, a
runtime source this module binds by correlation (R690, explicitly added and
tested): the path derives from the launch cwd (Claude Code's project key) plus
the ``session_id`` the result object reported, and every transcript line that
carries a ``sessionId`` must equal that id - a transcript at the right path for
a different session refuses. Identity holds only when every MAIN-CHAIN
(non-sidechain) assistant turn ran the pinned model (the exact id, or the
exact id + ``[1m]`` context tier); the usage aggregate must still CONTAIN the
pinned model, and its other keys are recorded as auxiliary - never identity,
never a failure by themselves (R691). Everything else fails closed with a typed
``ContractError``: missing/unreadable/uncorrelated transcript, zero assistant
turns, a divergent top-level model, a foreign ``cwd`` on a main-chain turn, a
pinned-absent or empty usage aggregate.

Import direction: imports ``.mrl_worker_result`` only (for ``ContractError``);
nothing imports this module back except the one-shot settlement.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
from typing import Any, Mapping, NoReturn, Sequence

from .checkpoint_envelope import normalize_worktree
from .mrl_worker_result import ContractError

#: The CLI's 1-million-context tier marker; meaningful ONLY as an exact suffix
#: of the exact pinned id (R687). Any other decorated id is a different model.
CONTEXT_TIER_SUFFIX = "[1m]"


def _fail(code: str, message: str) -> NoReturn:
    raise ContractError(code, message)


def model_matches_pin(observed: str, pinned: str) -> bool:
    """True for the exact pinned id or its exact ``[1m]`` context-tier variant."""
    return observed == pinned or observed == pinned + CONTEXT_TIER_SUFFIX


def project_key(cwd: str) -> str:
    """Claude Code's on-disk project-directory key for a working directory.

    Measured mapping (bound by test to the REAL observed directory of the
    preserved canary run): every character outside ``[A-Za-z0-9-]`` becomes
    ``-``, so ``C:\\Users\\MLFLL\\Downloads\\nyc-zoning\\ctl24`` stores under
    ``C--Users-MLFLL-Downloads-nyc-zoning-ctl24``.
    """
    return "".join(ch if (ch.isascii() and (ch.isalnum() or ch == "-")) else "-"
                   for ch in str(cwd))


def config_base(child_env: Mapping[str, str]) -> pathlib.Path:
    """The Claude config dir the CHILD would have used, from its exact env."""
    override = str(child_env.get("CLAUDE_CONFIG_DIR", "") or "").strip()
    if override:
        return pathlib.Path(override)
    profile = str(child_env.get("USERPROFILE", "") or child_env.get("HOME", "") or "").strip()
    if not profile:
        _fail("transcript_unresolvable",
              "child env carries neither CLAUDE_CONFIG_DIR nor USERPROFILE/HOME; the "
              "session transcript cannot be located (fail closed)")
    return pathlib.Path(profile) / ".claude"


def transcript_path(base: pathlib.Path, cwd: str, session_id: str) -> pathlib.Path:
    return pathlib.Path(base) / "projects" / project_key(cwd) / f"{session_id}.jsonl"


@dataclasses.dataclass(frozen=True)
class RuntimeIdentityEvidence:
    """What the correlation-bound transcript + usage aggregate proved."""

    primary_model: str                    # the pinned id (verification passed)
    primary_models_observed: tuple[str, ...]  # distinct main-chain turn models, in order
    auxiliary_models: tuple[str, ...]     # usage-aggregate keys that are not the pin/tier
    assistant_turns: int
    context_tier_used: bool               # a main-chain turn or usage key carried pin+[1m]
    transcript: str
    session_id: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def read_transcript_turns(path: pathlib.Path, session_id: str,
                          expected_cwd: str) -> "tuple[list[str], dict[str, int]]":
    """(main-chain assistant-turn models in order, main-chain tool-use census).

    Fails closed on an unreadable/empty file, on ANY line whose ``sessionId``
    differs from the correlated id, and on a main-chain assistant line whose
    recorded ``cwd`` is not the launch worktree.
    """
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        _fail("transcript_missing",
              f"session transcript {path} is unreadable ({exc}); the runtime model "
              f"cannot be proven (fail closed)")
    correlated = 0
    models: list[str] = []
    tools: dict[str, int] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue  # a torn/partial line proves nothing either way
        if not isinstance(event, dict):
            continue
        line_session = event.get("sessionId")
        if line_session is not None:
            if str(line_session) != session_id:
                _fail("transcript_uncorrelated",
                      f"transcript {path} carries sessionId {line_session!r} != the "
                      f"result's session {session_id!r} (fail closed)")
            correlated += 1
        if event.get("type") != "assistant" or event.get("isSidechain"):
            continue
        event_cwd = event.get("cwd")
        if event_cwd and normalize_worktree(str(event_cwd)) != normalize_worktree(expected_cwd):
            _fail("transcript_uncorrelated",
                  f"main-chain assistant event records cwd {event_cwd!r}, not the "
                  f"launch worktree {expected_cwd!r} (fail closed)")
        message = event.get("message")
        if not isinstance(message, Mapping):
            continue
        model = str(message.get("model", "") or "")
        if model:
            models.append(model)
        content = message.get("content")
        if isinstance(content, list):
            for part in content:
                if isinstance(part, Mapping) and part.get("type") == "tool_use":
                    name = str(part.get("name", "") or "")
                    tools[name] = tools.get(name, 0) + 1
    if correlated == 0:
        _fail("transcript_uncorrelated",
              f"transcript {path} carries no line with the correlated session id "
              f"{session_id!r} (fail closed)")
    if not models:
        _fail("transcript_no_turns",
              f"transcript {path} carries no main-chain assistant turn with a model; "
              f"the runtime model cannot be proven (fail closed)")
    return models, tools


def verify_primary_model(
    *,
    expected_model: str,
    session_id: str,
    cwd: str,
    usage_models: Sequence[str],
    child_env: "Mapping[str, str] | None" = None,
    transcript_base: "pathlib.Path | None" = None,
) -> "tuple[RuntimeIdentityEvidence, dict[str, int]]":
    """Prove the pinned model ran every main-chain turn; classify the aggregate.

    Returns ``(evidence, main_tool_use_census)`` - the census feeds the unit
    record so the canary's Bash-absence criterion reads a durable,
    correlation-bound source.

    ``usage_models`` are the result object's ``modelUsage`` keys (the aggregate,
    R686). ``transcript_base`` is a test seam; production resolves the base from
    the exact env handed to the child.
    """
    if not str(expected_model).strip():
        _fail("contract_violation", "no pinned model to verify against (fail closed)")
    if not str(session_id).strip():
        _fail("contract_violation", "no session id to correlate a transcript with (fail closed)")
    base = pathlib.Path(transcript_base) if transcript_base is not None else config_base(child_env or {})
    path = transcript_path(base, cwd, session_id)
    turn_models, tools = read_transcript_turns(path, session_id, cwd)
    divergent = sorted({m for m in turn_models if not model_matches_pin(m, expected_model)})
    if divergent:
        _fail("contract_violation",
              f"top-level model(s) {divergent} != pinned {expected_model!r} "
              f"({len(turn_models)} main-chain turn(s)); fail closed (R691)")
    usage = [str(m) for m in usage_models if str(m).strip()]
    if not usage:
        _fail("contract_violation",
              "the result reported an empty model-usage aggregate; the pinned model's "
              "presence cannot be confirmed (fail closed)")
    if not any(model_matches_pin(m, expected_model) for m in usage):
        _fail("contract_violation",
              f"pinned model {expected_model!r} absent from the session usage aggregate "
              f"{sorted(usage)} (fail closed)")
    auxiliary = tuple(sorted({m for m in usage if not model_matches_pin(m, expected_model)}))
    tier_used = any(m == expected_model + CONTEXT_TIER_SUFFIX for m in [*turn_models, *usage])
    seen: list[str] = []
    for m in turn_models:
        if m not in seen:
            seen.append(m)
    return RuntimeIdentityEvidence(
        primary_model=expected_model, primary_models_observed=tuple(seen),
        auxiliary_models=auxiliary, assistant_turns=len(turn_models),
        context_tier_used=tier_used, transcript=str(path), session_id=session_id,
    ), tools


__all__ = [
    "CONTEXT_TIER_SUFFIX", "RuntimeIdentityEvidence", "config_base", "model_matches_pin",
    "project_key", "read_transcript_turns", "transcript_path", "verify_primary_model",
]

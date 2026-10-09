#!/usr/bin/env python3
"""MRL single-process one-shot transport (M0-T134 / D-024 Amendment 39 R509; C7).

The MRL replaces the queued stream-json input path with exactly ONE fresh
``claude -p`` process: one prompt written to stdin, stdin CLOSED immediately, one
schema-bound result read back, under one controller wall-clock/process budget and
one ``--max-turns`` bound. There is no API surface for a second message, a resume/
continue, a background process, a model fallback, or a provider-directed
continuation - those are refused at plan-build time or are structurally impossible
(``run_one_shot`` spawns exactly once and never loops on output).

No live launch happens in Tranche A: the spawn is injectable (``spawn=``); the
default real spawn is never invoked here.
"""
from __future__ import annotations

import dataclasses
import subprocess
from typing import Any, Callable, Sequence

from .mrl_worker_result import ContractError

#: Flags that would resume a prior session, continue, fork, or background the run.
#: The one-shot transport refuses all of them (S8.2 + owner item 7).
FORBIDDEN_FLAGS = frozenset({
    "--continue", "-c", "--last", "--resume", "--fork-session", "--background", "&",
})

#: spawn(argv, *, stdin_text, timeout) -> (returncode, stdout, stderr)
Spawn = Callable[..., "tuple[int, str, str]"]


@dataclasses.dataclass(frozen=True)
class OneShotPlan:
    """A validated plan for exactly one bounded claude -p invocation."""

    argv: tuple[str, ...]
    prompt: str
    max_turns: int
    wall_clock_seconds: float


@dataclasses.dataclass(frozen=True)
class OneShotResult:
    returncode: int
    stdout: str
    stderr: str
    spawns: int


def build_one_shot_plan(
    executable: str,
    prompt: str,
    *,
    model: str,
    max_turns: int,
    wall_clock_seconds: float,
    extra_flags: Sequence[str] = (),
) -> OneShotPlan:
    """Build and validate a one-shot plan, refusing every non-one-shot shape.

    Fail-closed on: empty executable/prompt; a missing or non-string model (no
    fallback model is permitted - exactly one model string); a non-positive
    max_turns or wall-clock budget; and any forbidden flag (resume/continue/last/
    fork/background).
    """
    if not isinstance(executable, str) or not executable.strip():
        raise ContractError("contract_violation", "one-shot executable is required")
    if not isinstance(prompt, str) or not prompt.strip():
        raise ContractError("contract_violation",
                            "exactly one non-empty prompt is required (no queued input)")
    if not isinstance(model, str) or not model.strip():
        raise ContractError("contract_violation",
                            "exactly one model is required; no fallback model is permitted")
    if isinstance(max_turns, bool) or not isinstance(max_turns, int) or max_turns < 1:
        raise ContractError("contract_violation", "max_turns must be a positive int")
    if (isinstance(wall_clock_seconds, bool)
            or not isinstance(wall_clock_seconds, (int, float)) or wall_clock_seconds <= 0):
        raise ContractError("contract_violation",
                            "a positive controller wall-clock/process budget is required")
    flags = tuple(str(f) for f in extra_flags)
    forbidden = [f for f in flags if f in FORBIDDEN_FLAGS]
    if forbidden:
        raise ContractError("contract_violation",
                            f"forbidden one-shot flag(s) {forbidden}: no resume/continue/"
                            f"fork/background is permitted in the MRL")
    argv = (str(executable), "-p", "--output-format", "json",
            "--max-turns", str(max_turns), "--model", str(model), *flags)
    if any(a in FORBIDDEN_FLAGS for a in argv):  # defensive; assembled argv is clean by construction
        raise ContractError("contract_violation", "assembled argv carries a forbidden flag")
    return OneShotPlan(argv=argv, prompt=prompt, max_turns=max_turns,
                       wall_clock_seconds=float(wall_clock_seconds))


def _default_spawn(argv: Sequence[str], *, stdin_text: str, timeout: float) -> "tuple[int, str, str]":  # pragma: no cover - never called in Tranche A
    """Real one-shot spawn: write the single prompt, CLOSE stdin, wait under timeout.

    ``subprocess.run(input=...)`` writes stdin once and closes it, so there is no
    channel for a second message. Never invoked in Tranche A (no live launch).
    """
    proc = subprocess.run(list(argv), input=stdin_text, capture_output=True,
                          text=True, timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def run_one_shot(plan: OneShotPlan, *, spawn: Spawn | None = None) -> OneShotResult:
    """Execute the one-shot plan exactly once. Never loops on provider output.

    Writes the single prompt and lets the spawn close stdin immediately; there is
    no second-message path. A spawn count other than 1 fails closed.
    """
    spawn = spawn or _default_spawn
    calls = {"n": 0}

    def _counting(argv: Sequence[str], **kwargs: Any) -> "tuple[int, str, str]":
        calls["n"] += 1
        return spawn(argv, **kwargs)

    returncode, stdout, stderr = _counting(
        plan.argv, stdin_text=plan.prompt, timeout=plan.wall_clock_seconds)
    if calls["n"] != 1:
        raise ContractError("contract_violation",
                            f"one-shot transport must spawn exactly once, spawned {calls['n']}")
    return OneShotResult(returncode=returncode, stdout=stdout, stderr=stderr, spawns=calls["n"])

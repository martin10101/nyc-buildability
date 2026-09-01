#!/usr/bin/env python3
"""Raw gate-evidence recorder (M0-T134 / D-024 Amendment 39 R510/R514; C12).

A gate's verdict must be the CHILD process's own raw exit code, never a value a
pipe, ``Tee-Object``, or ``| tail`` could rewrite. This runner therefore executes
the gate command as a DIRECT subprocess - an argv LIST, never a shell string, so
there is no pipeline whose exit could mask the child's - and records a tamper-
evident bundle: absolute argv, cwd, start/end timestamps, the repository HEAD and
tree, the executable-chain identity, the raw return code, and sha256 digests of
stdout and stderr. Human reports are GENERATED FROM that record, never authored by
hand.

R514: this is the sole MRL *acceptance-evidence* path; it is not meant to wrap every
historical command or unrelated repository workflow.

The mutation harness (``run_mutation_check`` / ``--mutation``) reports SUCCESS when a
mutant is KILLED (the gate command failed as intended); a correctly functioning
mutation test therefore does not look like a failed gate.
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
from typing import Callable, Sequence

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _git_head_tree(cwd: str) -> "tuple[str, str]":
    """Best-effort (HEAD, HEAD-tree). Empty strings when cwd is not a git repo."""
    def _rev(spec: str) -> str:
        try:
            proc = subprocess.run(["git", "-C", cwd, "rev-parse", spec],
                                  capture_output=True, text=True)
        except OSError:
            return ""
        return proc.stdout.strip() if proc.returncode == 0 else ""
    return _rev("HEAD"), _rev("HEAD^{tree}")


@dataclasses.dataclass(frozen=True)
class GateRecord:
    argv: tuple[str, ...]
    cwd: str
    started_at_utc: str
    ended_at_utc: str
    repo_head: str
    repo_tree: str
    executable_chain_sha256: str
    returncode: int
    stdout_sha256: str
    stderr_sha256: str
    stdout_bytes: int
    stderr_bytes: int

    def to_dict(self) -> dict:
        return dataclasses.asdict(self) | {"argv": list(self.argv)}


def run_gate(
    argv: Sequence[str],
    *,
    cwd: str | None = None,
    executable_chain_sha256: str = "",
    repo_facts: Callable[[str], "tuple[str, str]"] = _git_head_tree,
    clock: Callable[[], str] = _utc_now,
) -> GateRecord:
    """Run a gate command as a direct subprocess and record its raw evidence.

    ``argv`` MUST be a list, never a shell string - so no pipe/Tee-Object/tail can
    sit between the child and its recorded exit code. The child's stdout/stderr are
    captured as bytes and digested; the return code recorded is the child's own.
    """
    if isinstance(argv, (str, bytes)):
        raise ValueError("gate_runner takes an argv LIST, never a shell string "
                         "(a shell pipeline's exit could mask the child's)")
    argv = [str(a) for a in argv]
    if not argv:
        raise ValueError("empty argv")
    resolved = shutil.which(argv[0]) or argv[0]
    abs_argv = [os.path.abspath(resolved) if os.path.sep in resolved or os.path.exists(resolved)
                else resolved, *argv[1:]]
    run_cwd = os.path.abspath(cwd or os.getcwd())
    started = clock()
    proc = subprocess.run(abs_argv, cwd=run_cwd, capture_output=True)  # no shell, no pipe
    ended = clock()
    head, tree = repo_facts(run_cwd)
    stdout = proc.stdout or b""
    stderr = proc.stderr or b""
    return GateRecord(
        argv=tuple(abs_argv),
        cwd=run_cwd,
        started_at_utc=started,
        ended_at_utc=ended,
        repo_head=head,
        repo_tree=tree,
        executable_chain_sha256=executable_chain_sha256,
        returncode=proc.returncode,
        stdout_sha256=_sha256(stdout),
        stderr_sha256=_sha256(stderr),
        stdout_bytes=len(stdout),
        stderr_bytes=len(stderr),
    )


def render_report(record: GateRecord) -> str:
    """Render a human report GENERATED FROM the machine record (never hand-authored)."""
    d = record.to_dict()
    verdict = "PASS" if d["returncode"] == 0 else "FAIL"
    lines = [
        f"gate {verdict} (raw returncode {d['returncode']})",
        f"  argv: {' '.join(d['argv'])}",
        f"  cwd: {d['cwd']}",
        f"  window: {d['started_at_utc']} -> {d['ended_at_utc']}",
        f"  repo HEAD/tree: {d['repo_head'] or '(none)'} / {d['repo_tree'] or '(none)'}",
        f"  exec-chain sha256: {d['executable_chain_sha256'] or '(n/a)'}",
        f"  stdout sha256: {d['stdout_sha256']} ({d['stdout_bytes']} bytes)",
        f"  stderr sha256: {d['stderr_sha256']} ({d['stderr_bytes']} bytes)",
    ]
    return "\n".join(lines)


@dataclasses.dataclass(frozen=True)
class MutationResult:
    killed: bool
    ok: bool
    record: GateRecord


def run_mutation_check(
    argv: Sequence[str], *, expect_nonzero: bool = True, **kwargs
) -> MutationResult:
    """Run a mutation gate: a KILLED mutant (nonzero exit) is the intended outcome.

    ``ok`` is True when the observed kill/live matches ``expect_nonzero`` - so a
    correctly killed mutant is reported as success, not as a failed gate.
    """
    record = run_gate(argv, **kwargs)
    killed = record.returncode != 0
    return MutationResult(killed=killed, ok=(killed == expect_nonzero), record=record)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=None, help="write the record JSON to this path")
    parser.add_argument("--cwd", default=None)
    parser.add_argument("--exec-chain-sha256", default="")
    parser.add_argument("--mutation", action="store_true",
                        help="mutation mode: exit 0 when the mutant is killed as expected")
    parser.add_argument("--expect-zero", action="store_true",
                        help="mutation mode: the command is expected to PASS (exit 0)")
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="-- followed by the gate argv (a list, never a shell string)")
    args = parser.parse_args(argv)
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("provide the gate command after --")

    if args.mutation:
        result = run_mutation_check(command, expect_nonzero=not args.expect_zero,
                                    cwd=args.cwd, executable_chain_sha256=args.exec_chain_sha256)
        record = result.record
        payload = record.to_dict() | {"mutation": {"killed": result.killed, "ok": result.ok}}
    else:
        record = run_gate(command, cwd=args.cwd,
                          executable_chain_sha256=args.exec_chain_sha256)
        payload = record.to_dict()

    text = json.dumps(payload, indent=1)
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text + "\n")
    print(render_report(record))
    print(text)
    if args.mutation:
        return 0 if payload["mutation"]["ok"] else 1
    return record.returncode


if __name__ == "__main__":
    sys.exit(main())

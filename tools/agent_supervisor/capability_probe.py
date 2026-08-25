"""Installed-capability probe for the D-024 continuous-agent-loop campaign (M0-T086).

Runs a FIXED ALLOWLIST of non-mutating CLI probes against the locally installed
``claude`` and ``codex`` executables and emits a deterministic JSON capability
record. The record distinguishes, per D-024 Phase A item 5:

* ``supported``          -- positively detected in the installed version;
* ``not-detected-in-help`` -- the token was absent from the probed help text
                              (weaker than "unsupported": help text can omit
                              flags, so this never claims absence of behavior);
* ``absent``             -- the executable/package is not installed at all;
* ``unknown``            -- the probe failed (timeout, error) or the fact
                              requires an interactive/live harness this module
                              deliberately does not provide.

Design constraints (D-024 sections 1, 5.1, 15-A):
* every probe is read-only -- no login, no config mutation, no network calls
  beyond what ``--version``/``--help`` themselves do locally;
* absence of a repository reference proves nothing -- only live probes and
  official documentation classify a capability;
* failures degrade to ``unknown``, never to a guessed value;
* the deterministic body contains no timestamps or absolute user paths, so two
  runs on the same installation produce identical bodies (probe metadata that
  legitimately varies lives under the separate ``probe_meta`` key).

Usage:
    python -m tools.agent_supervisor.capability_probe [--out FILE]

Supervisor-freeze qualifying evidence: D-024-R099 (Phase A capability fixtures,
a requirement explicitly listed in owner directive D-024).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone

PROBE_TIMEOUT_S = 30

# Fixed allowlist of (probe_id, argv) pairs. Every entry MUST be read-only.
# Adding a mutating verb here is a policy violation (tested by
# tools/test_agent_supervisor_capability_probe.py).
PROBE_COMMANDS: list[tuple[str, list[str]]] = [
    ("claude_version", ["claude", "--version"]),
    ("claude_help", ["claude", "--help"]),
    ("codex_version", ["codex", "--version"]),
    ("codex_help", ["codex", "--help"]),
    ("codex_exec_help", ["codex", "exec", "--help"]),
]

# Flag tokens whose presence in help output is probed per executable.
CLAUDE_FLAG_TOKENS = [
    "--strict-mcp-config",
    "--mcp-config",
    "--add-dir",
    "--settings",
    "--agent",
    "--worktree",
    "--resume",
    "--continue",
    "--print",
    "--output-format",
    "--init-only",
    "--name",
]
CODEX_FLAG_TOKENS = [
    "exec",
    "--sandbox",
    "--json",
    "--output-schema",
    "resume",
    "--cd",
    "--model",
    "--profile",
]

MUTATING_TOKENS = (
    "install", "login", "logout", "set", "add", "remove", "delete", "push",
    "commit", "merge", "write", "create", "update", "enable", "disable",
)


def _run(argv: list[str]) -> dict:
    """Run one allowlisted probe; never raises."""
    exe = shutil.which(argv[0])
    if exe is None:
        return {"status": "absent", "detail": f"{argv[0]} not on PATH"}
    try:
        # Execute the RESOLVED path: bare names bypass PATHEXT under Windows
        # CreateProcess, so an npm ``.cmd`` shim (e.g. codex.cmd) would raise
        # FileNotFoundError and misclassify an installed tool as unknown.
        proc = subprocess.run(
            [exe, *argv[1:]], capture_output=True, text=True,
            timeout=PROBE_TIMEOUT_S, check=False,
        )
    except subprocess.TimeoutExpired:
        return {"status": "unknown", "detail": f"timeout after {PROBE_TIMEOUT_S}s"}
    except OSError as exc:  # e.g. broken shim
        return {"status": "unknown", "detail": f"OSError: {exc}"}
    out = (proc.stdout or "") + (proc.stderr or "")
    return {
        "status": "supported" if proc.returncode == 0 else "unknown",
        "exit_code": proc.returncode,
        "output_sha256": hashlib.sha256(out.encode("utf-8", "replace")).hexdigest(),
        "first_line": out.strip().splitlines()[0] if out.strip() else "",
        "_output": out,  # stripped before serialization; used for flag scans
    }


def classify_flags(help_text: str, tokens: list[str]) -> dict:
    """Deterministic token-presence classification over a help text."""
    result = {}
    for tok in sorted(tokens):
        result[tok] = "supported" if tok in help_text else "not-detected-in-help"
    return result


def resolve_binaries(name: str) -> list[str]:
    """All PATH resolutions for a command name (dual-install detection)."""
    paths = []
    seen = set()
    first = shutil.which(name)
    if first:
        paths.append(first)
        seen.add(first.lower())
    # shutil.which only returns the first hit; scan PATH manually for others.
    import os
    for d in os.environ.get("PATH", "").split(os.pathsep):
        for ext in ("", ".exe", ".cmd", ".bat"):
            cand = os.path.join(d, name + ext)
            if os.path.isfile(cand) and cand.lower() not in seen:
                paths.append(cand)
                seen.add(cand.lower())
    return paths


def build_record() -> dict:
    """Assemble the full probe record: deterministic body + varying metadata."""
    raw: dict[str, dict] = {}
    for probe_id, argv in PROBE_COMMANDS:
        raw[probe_id] = _run(argv)

    claude_help = raw.get("claude_help", {}).pop("_output", "")
    codex_help = raw.get("codex_help", {}).pop("_output", "")
    codex_exec_help = raw.get("codex_exec_help", {}).pop("_output", "")
    for rec in raw.values():
        rec.pop("_output", None)

    body = {
        "schema": "capability_probe/v1",
        "directive": "D-024",
        "task": "M0-T086",
        "probes": raw,
        "claude_flags": classify_flags(claude_help, CLAUDE_FLAG_TOKENS),
        "codex_flags": classify_flags(codex_help + "\n" + codex_exec_help,
                                      CODEX_FLAG_TOKENS),
        "python_runtime": {
            "local": f"{sys.version_info.major}.{sys.version_info.minor}."
                     f"{sys.version_info.micro}",
            "note": "repo CI runs Python 3.12; local sandbox may be older "
                    "(M2-T015 lesson) - this module stays 3.11-compatible",
        },
        "interactive_only_capabilities": {
            # Facts that REQUIRE a live interactive harness; the probe refuses
            # to guess them (D-024: fail to unknown, never invent).
            "UserPromptSubmit_block_erases_prompt": "unknown",
            "UserPromptExpansion_intercepts_before_expansion": "unknown",
            "subagentStatusLine_payload_shape": "unknown",
            "statusline_payload_shape": "unknown",
            "note": "documented in fixtures/capability_matrix_v1.json from "
                    "official docs; live confirmation is a Phase B/F harness "
                    "deliverable (D-024 15-B, 15-F), not guessable here",
        },
    }
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "claude_binaries": resolve_binaries("claude"),
        "codex_binaries": resolve_binaries("codex"),
        "platform": sys.platform,
    }
    return {"body": body, "probe_meta": meta}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Installed-capability probe (D-024 M0-T086)")
    parser.add_argument("--out", default=None,
                        help="write JSON here (default: stdout)")
    args = parser.parse_args(argv)
    record = build_record()
    text = json.dumps(record, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

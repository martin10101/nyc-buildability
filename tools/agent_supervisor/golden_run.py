"""Golden-run harness: disposable fixtures + fault injection (D-024 Phase H).

M0-T096 unit I (qualifying evidence D-024-R106; R115 16.9(m), R121, R186,
R222).  Everything here builds LANE-1 INJECTED evidence (Amendment 7, R223):
disposable git checkouts, scratch runtimes, and fake provider executables that
never contact a provider.  The harness exists so the golden-run test pack (and
any future disposable canary) composes the REAL production surfaces -
``cli.main(["start", ...])``, the real loop, the real rotation/recovery paths -
around injected providers, instead of re-implementing any of them.

Nothing in this module runs in a live supervised session; production code
never imports it.  It is a deliverable of the M0-T096 packet ("canary/
golden-run harnesses + fault injection under tools/agent_supervisor").
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import textwrap
from typing import Any, Mapping, Sequence

#: Marker stamped into every plan/checkpoint summary the harness produces, so
#: no record born here can read as naturally observed evidence (R223).
INJECTED_MARKER = "INJECTED-GOLDEN-RUN"

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "golden-run-fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "golden-run-fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def _git(checkout: pathlib.Path, *argv: str) -> str:
    result = subprocess.run(
        ["git", *argv], cwd=str(checkout), check=True, capture_output=True,
        text=True, env={**os.environ, **_GIT_ENV})
    return result.stdout.strip()


def build_disposable_checkout(root: pathlib.Path, *, task_id: str,
                              branch: str) -> dict[str, str]:
    """A REAL git checkout on a non-protected task branch, with a ledger record.

    The start-time probes read live git state, so a dispatching fixture must be
    a checkout they can actually read (the CliStartTests lesson).  Returns the
    identity facts the response plan needs (head SHA, branch, worktree).
    """
    root.mkdir(parents=True, exist_ok=True)
    tasks = root / "project-control" / "tasks"
    tasks.mkdir(parents=True, exist_ok=True)
    (tasks / f"{task_id}.json").write_text(
        json.dumps({"task_id": task_id, "status": "in_progress",
                    "blockers": []}), encoding="utf-8")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", f"{INJECTED_MARKER} fixture base")
    _git(root, "checkout", "-q", "-b", branch)
    return {"worktree": str(root), "branch": branch,
            "head_sha": _git(root, "rev-parse", "HEAD")}


CONFIG_TOML = """
[codex]
allowed_models = ["codex-primary"]

[claude]
allowed_models = ["claude-fable-5", "claude-opus-4-8"]

[controller]
default_mode = "shadow"

[limits]
max_review_packet_bytes = 262144
"""

SELECTION_TOML = """
[codex]
review_model = "codex-primary"
advisory_model = "codex-primary"
fallback_models = []

[claude]
model = "claude-fable-5"
fallback_models = []
"""


def write_controller_files(tmp: pathlib.Path,
                           package_root: pathlib.Path) -> dict[str, str]:
    """config.toml + model_selection.toml + a REAL recorded manifest."""
    from .manifest import generate_manifest, write_manifest
    config = tmp / "config.toml"
    config.write_text(CONFIG_TOML, encoding="utf-8")
    selection = tmp / "model_selection.toml"
    selection.write_text(SELECTION_TOML, encoding="utf-8")
    manifest = write_manifest(
        generate_manifest(package_root,
                          extra_files=(("config.toml", config),)),
        tmp / "controller_manifest.json")
    return {"config": str(config), "model_selection": str(selection),
            "manifest": str(manifest)}


# --------------------------------------------------------------------------
# The exact operator command (R121): the harness builds the argv it hands to
# ``cli.main`` from the SAME verb and flags the owner runs, and returns it so
# the evidence report can record the command verbatim.
# --------------------------------------------------------------------------


def start_argv(*, mode: str, claude_executable: str, codex_executable: str,
               task_packet: str, config: str, model_selection: str,
               manifest: str, checkout: str, runtime_base: str,
               branch: str = "", max_cycles: int | None = None,
               owner_enable_bounded_auto: bool = False,
               extra: Sequence[str] = ()) -> list[str]:
    """``python -m tools.agent_supervisor start ...`` as an argv list."""
    argv = ["start", "--mode", mode,
            "--claude-executable", claude_executable,
            "--codex-executable", codex_executable,
            "--task-packet", task_packet,
            "--config", config,
            "--model-selection", model_selection,
            "--manifest", manifest,
            "--checkout", checkout,
            "--runtime-base", runtime_base,
            "--json"]
    if branch:
        argv += ["--branch", branch]
    if max_cycles is not None:
        argv += ["--max-cycles", str(max_cycles)]
    if owner_enable_bounded_auto:
        argv += ["--owner-enable-bounded-auto"]
    argv += list(extra)
    return argv


# --------------------------------------------------------------------------
# Fake providers (INJECTED; sequenced by a JSON response plan + counter file)
# --------------------------------------------------------------------------

#: The fake producer.  Reads GOLDEN_PLAN (a JSON file of sequenced responses)
#: and GOLDEN_COUNTER (which launch this is); each response can perform a REAL
#: git commit on the disposable checkout's task branch before reporting the
#: real SHAs in its checkpoint.  Modes: "work" (UNIT_COMPLETE), "ready" (the
#: S11.3 successor checkpoint), "refusal" (typed structured refusal, no
#: checkpoint), "exhaustion" (quota signal, no checkpoint).
FAKE_CLAUDE_GOLDEN = textwrap.dedent('''
    """FAKE claude for the golden run. INJECTED-GOLDEN-RUN. No network."""
    import json, os, pathlib, subprocess, sys

    HERE = pathlib.Path(__file__).resolve().parent
    plan = json.loads((HERE / "golden_plan.json").read_text(encoding="utf-8"))
    counter = HERE / "golden_counter.txt"
    launch = int(counter.read_text()) + 1 if counter.exists() else 1
    counter.write_text(str(launch))
    responses = plan["responses"]
    step = responses[min(launch - 1, len(responses) - 1)]
    worktree = plan["worktree"]

    def git(*argv):
        env = dict(os.environ)
        env.update({"GIT_AUTHOR_NAME": "golden-run-fixture",
                    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                    "GIT_COMMITTER_NAME": "golden-run-fixture",
                    "GIT_COMMITTER_EMAIL": "fixture@example.invalid"})
        out = subprocess.run(["git", *argv], cwd=worktree, check=True,
                             capture_output=True, text=True, env=env)
        return out.stdout.strip()

    log_path = plan.get("launch_log", "")
    if log_path:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"launch": launch, "pid": os.getpid(),
                                 "argv": sys.argv[1:],
                                 "kind": step["kind"]}) + "\\n")

    session_id = step.get("session_id", f"sess-golden-{launch}")
    sys.stdout.write(json.dumps({"type": "system", "subtype": "init",
                                 "session_id": session_id}) + "\\n")

    if step["kind"] == "refusal":
        # The typed structured refusal shape (stop_reason: "refusal") plus an
        # is_error result text so the classifier evidence carries the INJECTED
        # marker (R223: harness-born records label themselves).
        sys.stdout.write(json.dumps({
            "type": "result", "subtype": "error", "uuid": "u-refusal",
            "is_error": True, "stop_reason": "refusal",
            "result": "INJECTED-GOLDEN-RUN typed refusal: I can't help "
                      "with that request."}) + "\\n")
        raise SystemExit(0)

    if step["kind"] == "exhaustion":
        # The R289 lesson: the weekly-limit phrase surfaces in STREAM events,
        # not stderr. The confirmed phrase is kept intact after the marker.
        sys.stdout.write(json.dumps({
            "type": "result", "is_error": True, "uuid": "u-exhausted",
            "result": plan.get(
                "exhaustion_text",
                "INJECTED-GOLDEN-RUN: You've reached your Fable 5 limit "
                "for the week.")}) + "\\n")
        raise SystemExit(1)

    starting_sha = git("rev-parse", "HEAD")
    current_sha = starting_sha
    commit = step.get("git_commit")
    if commit:
        target = pathlib.Path(worktree) / commit["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(commit["content"], encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", commit["message"])
        current_sha = git("rev-parse", "HEAD")

    if step.get("usage_total"):
        sys.stdout.write(json.dumps({
            "type": "assistant",
            "message": {"model": plan.get("report_model", "claude-fable-5"),
                        "usage": {"input_tokens": int(step["usage_total"]),
                                  "output_tokens": 0}}}) + "\\n")

    default_status = "READY" if step["kind"] == "ready" else "UNIT_COMPLETE"
    checkpoint = {
        "schema_version": "1.0.0", "run_id": plan["run_id"],
        "checkpoint_id": step["checkpoint_id"], "task_id": plan["task_id"],
        "claude_session_id": session_id,
        "status": step.get("status", default_status),
        "summary": "INJECTED-GOLDEN-RUN " + step.get("summary", "unit done"),
        "starting_sha": starting_sha, "current_sha": current_sha,
        "branch": plan["branch"], "worktree": worktree,
        "proposed_next_action": step.get("proposed_next_action", "continue"),
        "usage": "unknown", "context_pressure": "unknown",
    }
    sys.stdout.write(json.dumps({"type": "result", "subtype": "success",
                                 "uuid": f"u-{launch}",
                                 "result": json.dumps(checkpoint)}) + "\\n")
''')

#: The fake reviewer.  ECHOES the reviewed identity out of the packet on stdin
#: (task_id, checkpoint_id, the checkpoint's current_sha) so the identity
#: validation exercises the real code path, and forwards the next bounded unit
#: prompt from the plan - the injected stand-in for autonomous next-unit
#: selection.
FAKE_CODEX_GOLDEN = textwrap.dedent('''
    """FAKE codex for the golden run. INJECTED-GOLDEN-RUN. Read-only."""
    import json, pathlib, sys

    HERE = pathlib.Path(__file__).resolve().parent
    ARGV = sys.argv[1:]

    def flag(name):
        return ARGV[ARGV.index(name) + 1] if name in ARGV else ""

    packet = {}
    try:
        packet = json.loads(sys.stdin.read() or "{}")
    except ValueError:
        packet = {}

    head = "b" * 40
    body = ((packet.get("sections") or {}).get("claude_checkpoint") or {})
    try:
        checkpoint = json.loads(body.get("body", "") or "{}")
        head = checkpoint.get("current_sha", head)
    except ValueError:
        pass

    review_plan = HERE / "golden_review_plan.json"
    prompts = []
    if review_plan.exists():
        prompts = json.loads(review_plan.read_text(
            encoding="utf-8")).get("next_prompts", [])
    prev = HERE / "golden_review_counter.txt"
    review = int(prev.read_text()) + 1 if prev.exists() else 1
    prev.write_text(str(review))
    prompt = (prompts[min(review - 1, len(prompts) - 1)]
              if prompts else "Do the next bounded unit.")

    decision = {
        "schema_version": "1.0.0", "decision": "CONTINUE",
        "reviewed_task_id": packet.get("task_id", ""),
        "reviewed_checkpoint_id": packet.get("checkpoint_id", ""),
        "verified_repo_head": head, "verified_origin_main": head,
        "model_used": flag("-m") or "codex-primary",
        "next_claude_prompt": prompt,
        "verified_facts": [{"fact": "INJECTED-GOLDEN-RUN review",
                            "review": review}],
        "evidence_refs": [{"path": "project-control/tasks"}],
        "blocking_findings": [], "reason_codes": [], "unverified_claims": [],
        "owner_question": "", "rotation_reason": "",
    }
    out = flag("--output-last-message")
    if out:
        pathlib.Path(out).write_text(json.dumps(decision), encoding="utf-8")
    else:
        sys.stdout.write(json.dumps(decision) + "\\n")
''')


def _executable_wrapper(directory: pathlib.Path, name: str,
                        script: pathlib.Path) -> pathlib.Path:
    """A directly-executable launcher for a fake provider script.

    The CLI invokes provider executables by path (never through a shell), so
    the fake needs a real executable: a shebang script on POSIX, a ``.bat``
    wrapper on Windows.  ``sys.executable`` is baked in at materialization.
    """
    import stat
    import sys
    if os.name == "nt":
        wrapper = directory / f"{name}.bat"
        wrapper.write_text(
            f'@"{sys.executable}" "{script}" %*\r\n', encoding="utf-8")
        return wrapper
    wrapper = directory / name
    wrapper.write_text(f"#!{sys.executable}\n"
                       + script.read_text(encoding="utf-8"),
                       encoding="utf-8")
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP
                  | stat.S_IXOTH)
    return wrapper


def materialize_fakes(directory: pathlib.Path) -> dict[str, str]:
    """Write both fake provider scripts + platform-appropriate launchers.

    The scripts read their plans from files NEXT TO THEMSELVES
    (``golden_plan.json`` / ``golden_review_plan.json`` + counter files),
    because the supervisor launches children with a minimal stripped
    environment - env-var plumbing would never arrive.
    """
    directory.mkdir(parents=True, exist_ok=True)
    claude = directory / "fake_claude_golden.py"
    claude.write_text(FAKE_CLAUDE_GOLDEN, encoding="utf-8")
    codex = directory / "fake_codex_golden.py"
    codex.write_text(FAKE_CODEX_GOLDEN, encoding="utf-8")
    return {
        "claude": str(_executable_wrapper(directory, "fake_claude_golden",
                                          claude)),
        "codex": str(_executable_wrapper(directory, "fake_codex_golden",
                                         codex)),
        "claude_script": str(claude), "codex_script": str(codex),
        "plan": str(directory / "golden_plan.json"),
        "review_plan": str(directory / "golden_review_plan.json"),
        "counter": str(directory / "golden_counter.txt"),
        "review_counter": str(directory / "golden_review_counter.txt"),
    }


def write_plan(path: pathlib.Path, *, run_id: str, task_id: str,
               worktree: str, branch: str,
               responses: Sequence[Mapping[str, Any]],
               launch_log: str = "", report_model: str = "claude-fable-5",
               exhaustion_text: str = "") -> pathlib.Path:
    plan: dict[str, Any] = {
        "injected": INJECTED_MARKER, "run_id": run_id, "task_id": task_id,
        "worktree": worktree, "branch": branch,
        "responses": list(responses), "report_model": report_model,
    }
    if launch_log:
        plan["launch_log"] = launch_log
    if exhaustion_text:
        plan["exhaustion_text"] = exhaustion_text
    path.write_text(json.dumps(plan, indent=1), encoding="utf-8")
    return path


def write_review_plan(path: pathlib.Path,
                      next_prompts: Sequence[str]) -> pathlib.Path:
    path.write_text(json.dumps({"injected": INJECTED_MARKER,
                                "next_prompts": list(next_prompts)},
                               indent=1), encoding="utf-8")
    return path


def read_launch_log(path: pathlib.Path) -> list[dict[str, Any]]:
    """Launches as ANOTHER process recorded them (the model_chain pattern)."""
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def task_packet(path: pathlib.Path, *, task_id: str,
                allowed_paths: Sequence[str] = ("docs/**", "tools/**"),
                stop_conditions: Sequence[str] = ("no bypass flags",),
                ) -> pathlib.Path:
    path.write_text(json.dumps({
        "task_id": task_id,
        "allowed_paths": list(allowed_paths),
        "forbidden_paths": [".github/**"],
        "status": "in_progress",
        "stop_conditions": list(stop_conditions),
        "authorization": f"{INJECTED_MARKER} disposable canary packet",
        "objective": "golden-run disposable unit",
    }), encoding="utf-8")
    return path

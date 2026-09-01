"""M0-T132 shell-routing recapture at the 2.1.252 admission (D-024 Amendment 34/35).

Reproducible bounded routing probe, run against the SAME installed claude.exe the gate
checks (e713c5a6), on the approved worker model claude-opus-4-8 (Fable 5 was under its
seven-day usage cap; opus-4-8 is the model the loop runs under while Fable is unavailable,
R220/R221/R447/R448). Uses the routing_probe module's own functions (build_argv,
_run_assignment, build_fixture) so the code path is identical to
`python -m tools.agent_supervisor.routing_probe` except the RunnerConfig pins --model and
the digest-identity fields are stamped exactly as the M0-T120 fixture recorded them (by
file hash via executable_identity - never a provider call). Writes the fixture only when the
run is measured and native_preferred.

Run: python project-control/reports/M0-T132-routing-capture.py
"""
import json
import pathlib
import tempfile

from tools.agent_supervisor import routing_probe as rp
from tools.agent_supervisor.claude_runner import ClaudeRunner, RunnerConfig, build_argv
from tools.agent_supervisor.process import executable_identity

EXE = r"C:/Users/MLFLL/.local/bin/claude.exe"
MODEL = "claude-opus-4-8"
OUT = pathlib.Path("tools/agent_supervisor/fixtures/shell_routing_2026-09-01_m0t132_2_1_252.json")


def main() -> int:
    version_line = rp._claude_version(EXE)
    argv_shape = ("<executable>", *build_argv(
        RunnerConfig(executable=EXE, max_turns=rp.DISCOVERY_MAX_TURNS, model=MODEL))[1:])
    observations = []
    error = ""
    with tempfile.TemporaryDirectory(prefix="routing_probe_m0t132_",
                                     ignore_cleanup_errors=True) as tmp:
        root = pathlib.Path(tmp)
        rp._write_discovery_fixture(root)
        try:
            for assignment, prompt, turns in (
                ("discovery", rp.DISCOVERY_PROMPT, rp.DISCOVERY_MAX_TURNS),
                ("edit", rp.EDIT_PROMPT, rp.EDIT_MAX_TURNS),
            ):
                cfg = RunnerConfig(executable=EXE, max_turns=turns,
                                   timeout_seconds=180.0, cwd=str(root), model=MODEL)
                runner = ClaudeRunner(cfg, run_id="routing_probe_m0t132", journal=None)
                observations.append(rp._run_assignment(runner, assignment, prompt, root, turns))
        except Exception as exc:  # a probe that could not run is not routing evidence
            error = f"{type(exc).__name__}: {exc}"

    provider_calls = sum(o.max_turns for o in observations)
    measured = not error and bool(observations)
    fx = rp.build_fixture(executable=EXE, version_line=version_line, argv_shape=argv_shape,
                          observations=tuple(observations), provider_calls=provider_calls,
                          measured=measured, error=error)

    ident = executable_identity(EXE)
    fx["task"] = "M0-T132"
    fx["requirement"] = "R292/R295 recaptured at the 2.1.252 admission"
    fx["cli_identity"] = ident.digest
    fx["cli_identity_kind"] = ident.digest_kind
    fx["cli_identity_provenance"] = (
        "sha256 head+size digest of the SAME installed claude.exe the routing was measured "
        "against, computed by file hash (executable_identity) - NOT a provider call and NOT a "
        "re-run of the probe; it pins this measured routing evidence to the exact binary "
        "identity the gate checks (_claude_cli_identity).")
    fx["capture_model"] = MODEL
    fx["capture_note"] = (
        "Recaptured at the 2.1.252 admission (D-024 Amendment 34/35). Routing measured on the "
        "approved worker model claude-opus-4-8 because Fable 5 was under its seven-day usage cap "
        "(R220/R221/R447/R448); opus-4-8 is the model the loop runs under while Fable is "
        "unavailable. Routing behavior is a CLI/tool property and native_preferred reproduces the "
        "M0-T120 verdict; the digest identity is what the gate matches.")

    print("verdict:", fx["routing_summary"]["verdict"],
          "| native:", fx["routing_summary"]["native"],
          "| shell:", fx["routing_summary"]["shell"],
          "| tools:", fx["routing_summary"]["total_tool_uses"])
    print("claude_version:", fx["claude_version"], "| measured:", fx["measured"],
          "| provider_calls:", fx["provider_calls_made"],
          "| no_worker_write:", fx["no_worker_file_write_observed"])
    print("cli_identity:", fx["cli_identity"][:16], "kind:", fx["cli_identity_kind"])

    if not (fx["measured"] and fx["routing_summary"]["verdict"] == "native_preferred"):
        print("NOT WRITTEN - verdict not native_preferred / not measured:", fx.get("error"))
        return 12
    OUT.write_text(json.dumps(fx, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("WROTE", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

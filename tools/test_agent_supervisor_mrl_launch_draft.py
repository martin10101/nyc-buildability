"""Paired positive/negative tests for the launch-manifest draft tool (M0-T136 C-B5; D-024-R585, R589).

The draft binds dispatch identities the SAME way the launch verifies them; each
positive binding has a mutation or refusal twin. Git and ``--version`` are injected
for the unit tests; the ``main`` tests drive a real throwaway repository and
``sys.executable`` (whose ``--version`` really parses) so the operator entrypoint
is exercised end to end without any provider contact.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor import mrl_exec_chain as mec  # noqa: E402
from tools.agent_supervisor import mrl_launch_draft as mld  # noqa: E402
from tools.agent_supervisor import mrl_launch_manifest as mlm  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import ContractError  # noqa: E402
from tools.test_agent_supervisor_mrl_launch_manifest import build_world  # noqa: E402

SELECTION_TOML = """
[codex]
review_model = "gpt-5-codex"
advisory_model = "gpt-5-codex"
fallback_models = []

[claude]
model = "claude-opus-4-8"
fallback_models = []
"""
VERSIONS = {"claude.exe": "2.1.252 (Claude Code)", "codex.exe": "codex-cli 0.50.0"}


def fake_version(argv):
    """Canned ``<executable> --version`` answers keyed by the executable's file name."""
    assert argv[1:] == ["--version"]
    name = pathlib.Path(argv[0]).name
    if name not in VERSIONS:
        return 1, "", f"{name}: no canned version"
    return 0, VERSIONS[name], ""


@pytest.fixture
def world(tmp_path: pathlib.Path):
    w = build_world(tmp_path)
    exe = tmp_path / "bin"
    (exe / "claude.exe").write_bytes(b"claude-bytes")
    (exe / "codex.exe").write_bytes(b"codex-bytes")
    (exe / "config.toml").write_text("[controller]\n", encoding="utf-8")
    (exe / "model_selection.toml").write_text(SELECTION_TOML, encoding="utf-8")
    (exe / "controller_manifest.json").write_text("{}", encoding="utf-8")
    w["exe"] = exe
    w["inputs"] = mld.DraftInputs(
        worktree=str(w["worktree"]), task_packet=str(w["packet_path"]), mode="supervised",
        claude_executable=str(exe / "claude.exe"), codex_executable=str(exe / "codex.exe"),
        config=str(exe / "config.toml"), model_selection=str(exe / "model_selection.toml"),
        controller_manifest=str(exe / "controller_manifest.json"), base_ref="refs/heads/main",
        runtime_model_from_selection=True)
    return w


def _fill(world, inputs=None, **kw):
    return mld.fill_draft(inputs or world["inputs"], run_git=world["git"], run_version=fake_version,
                          scratch=world["tmp"] / "scratch", **kw)


# ----------------------------------------------------------------- positive contract

def test_fill_draft_binds_every_dispatch_value_the_launch_verifies(world):
    draft, remaining = _fill(world)
    assert remaining == []
    d = draft["dispatch"]
    for kind in ("claude", "codex"):
        chain = mec.resolve_chain(str(world["exe"] / f"{kind}.exe"), kind)
        assert d[f"{kind}_chain_sha256"] == mec.bind_chain_now(chain).combined_sha256
        assert d[f"{kind}_executable"] == str(world["exe"] / f"{kind}.exe")
    assert d["claude_version"] == "2.1.252"
    assert d["codex_version"] == "0.50.0"
    assert d["claude_model"] == "claude-opus-4-8"
    assert d["claude_runtime_model"] == "claude-opus-4-8"
    assert d["codex_model"] == "gpt-5-codex"
    assert d["base_ref"] == "refs/heads/main"
    assert d["max_turns"] == 12 and d["unit_timeout_seconds"] == 900
    assert draft["expected"]["mode"] == "supervised"
    assert not any(mld.is_placeholder(v) for v in d.values())
    # The draft is a LOADABLE manifest whose identity is the PREFLIGHT function's own answer.
    loaded = mlm.LaunchManifest.from_dict({k: v for k, v in draft.items() if not k.startswith("_")})
    assert loaded.base_ref() == "refs/heads/main"
    scratch = world["tmp"] / "independent"
    identity, _ = mlm.observe_profile_identity(loaded, profile_dir=scratch, ledger_path=scratch / "l.json")
    assert draft["expected"]["settings_profile_sha256"] == identity
    assert draft["_draft_bindings"]["claude"]["shape"] == mec.SHAPE_NATIVE


def test_partial_inputs_leave_reported_placeholders_and_no_identity(world):
    inputs = mld.DraftInputs(worktree=str(world["worktree"]), task_packet=str(world["packet_path"]),
                             claude_executable=str(world["exe"] / "claude.exe"))
    draft, remaining = _fill(world, inputs)
    assert "codex_chain_sha256" in remaining and "codex_executable" in remaining
    assert "claude_model" in remaining and "base_ref" in remaining
    assert "claude_chain_sha256" not in remaining
    assert remaining[-1] == "expected.settings_profile_sha256"
    assert mld.is_placeholder(draft["expected"]["settings_profile_sha256"])


def test_explicit_runtime_model_is_pinned_verbatim(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "runtime_model_from_selection": False,
                                "claude_runtime_model": "claude-fable-5"})
    draft, remaining = _fill(world, inputs)
    assert remaining == []
    assert draft["dispatch"]["claude_runtime_model"] == "claude-fable-5"
    assert draft["dispatch"]["claude_model"] == "claude-opus-4-8"


def test_custom_bounds_are_carried(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "max_turns": 3, "unit_timeout_seconds": 60})
    draft, _ = _fill(world, inputs)
    assert draft["dispatch"]["max_turns"] == 3
    assert draft["dispatch"]["unit_timeout_seconds"] == 60


# ----------------------------------------------------------------- paired negatives

def test_mutating_a_bound_executable_after_the_draft_is_detected(world):
    draft, _ = _fill(world)
    pinned = draft["dispatch"]["claude_chain_sha256"]
    exe = world["exe"] / "claude.exe"
    exe.write_bytes(b"claude-bytes-tampered")
    chain = mec.resolve_chain(str(exe), "claude")
    with pytest.raises(ContractError):
        mec.verify_chain_now(chain, pinned)


def test_dirty_tree_refuses(world):
    world["git"].answers[("status", "--porcelain", "--untracked-files=all")] = " M tools/x.py\n"
    with pytest.raises(ContractError, match="dirty tree"):
        _fill(world)


def test_missing_executable_refuses(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "codex_executable": str(world["exe"] / "nope.exe")})
    with pytest.raises(ContractError, match="not a file"):
        _fill(world, inputs)


def test_relative_executable_refuses(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "claude_executable": "bin/claude.exe"})
    with pytest.raises(ContractError, match="absolute"):
        _fill(world, inputs)


def test_unparseable_version_refuses(world):
    def banana(argv):
        return 0, "banana", ""
    with pytest.raises(ContractError, match="no MAJOR.MINOR.PATCH version"):
        mld.fill_draft(world["inputs"], run_git=world["git"], run_version=banana)


def test_nonzero_version_exit_refuses(world):
    def failing(argv):
        return 1, "2.1.252 (Claude Code)", ""
    with pytest.raises(ContractError, match="no MAJOR.MINOR.PATCH version"):
        mld.fill_draft(world["inputs"], run_git=world["git"], run_version=failing)


def test_relative_or_missing_file_inputs_refuse(world):
    for attr, value in (("config", "config.toml"), ("model_selection", str(world["exe"] / "missing.toml")),
                        ("controller_manifest", "controller_manifest.json")):
        inputs = mld.DraftInputs(**{**vars(world["inputs"]), attr: value})
        with pytest.raises(ContractError):
            _fill(world, inputs)


def test_empty_claude_model_refuses(world):
    (world["exe"] / "model_selection.toml").write_text(
        SELECTION_TOML.replace('model = "claude-opus-4-8"', 'model = ""'), encoding="utf-8")
    with pytest.raises(ContractError, match="empty claude.model"):
        _fill(world)


def test_empty_codex_model_refuses(world):
    (world["exe"] / "model_selection.toml").write_text(
        SELECTION_TOML.replace('review_model = "gpt-5-codex"', 'review_model = ""'), encoding="utf-8")
    with pytest.raises(ContractError, match="empty codex.review_model"):
        _fill(world)


def test_malformed_model_selection_is_a_typed_refusal(world):
    (world["exe"] / "model_selection.toml").write_text("[claude\nmodel = ", encoding="utf-8")
    with pytest.raises(ContractError) as info:
        _fill(world)
    assert info.value.code != "contract_violation"  # the ConfigError code is carried, not swallowed


def test_placeholder_base_ref_refuses(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "base_ref": "<fill: remote base ref>"})
    with pytest.raises(ContractError) as info:
        _fill(world, inputs)
    assert info.value.code == "launch_manifest_base_ref_missing"


def test_runtime_model_from_selection_without_selection_refuses(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "model_selection": "", "runtime_model_from_selection": True})
    with pytest.raises(ContractError, match="needs --model-selection"):
        _fill(world, inputs)


def test_both_runtime_model_choices_refuse(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "claude_runtime_model": "claude-fable-5"})
    with pytest.raises(ContractError, match="choose ONE"):
        _fill(world, inputs)


def test_unauthorized_mode_and_bad_bounds_refuse(world):
    with pytest.raises(ContractError, match="not an authorized mode"):
        _fill(world, mld.DraftInputs(**{**vars(world["inputs"]), "mode": "auto"}))
    with pytest.raises(ContractError, match="max_turns"):
        _fill(world, mld.DraftInputs(**{**vars(world["inputs"]), "max_turns": 0}))
    with pytest.raises(ContractError, match="unit_timeout_seconds"):
        _fill(world, mld.DraftInputs(**{**vars(world["inputs"]), "unit_timeout_seconds": True}))


# ----------------------------------------------------------------- subagent contract choices

def _draft_default_subagents(world) -> dict:
    return mlm.draft_manifest(str(world["worktree"]), str(world["packet_path"]), mode="supervised",
                              run_git=world["git"])["dispatch"]["subagents"]


def test_no_subagent_choice_keeps_the_draft_default_verbatim(world):
    draft, _ = _fill(world)
    assert draft["dispatch"]["subagents"] == _draft_default_subagents(world)
    assert "Agent" not in draft["dispatch"]["subagents"]["allow_rules"]  # fan-out is NOT granted by default


def test_subagent_choices_replace_the_default_and_change_the_identity(world):
    base, _ = _fill(world)
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "allow_tools": ("Read", "Grep", "Glob", "Agent"),
                                "deny_tools": ("WebFetch", "Edit", "Write", "Bash"),  # every tool pinned (R692)
                                "agent_inventory": ("Explore",),
                                "max_concurrent": 1, "max_total": 2})
    draft, remaining = _fill(world, inputs)
    assert remaining == []
    sub = draft["dispatch"]["subagents"]
    assert sub["allow_rules"] == ["Read", "Grep", "Glob", "Agent"]
    assert sub["deny_rules"] == ["WebFetch", "Edit", "Write", "Bash"]
    assert sub["agent_inventory"] == ["Explore"]
    assert sub["max_concurrent"] == 1 and sub["max_total"] == 2
    assert sub["tools_inventory"] == _draft_default_subagents(world)["tools_inventory"]  # untouched
    # The contract is part of the profile identity PREFLIGHT re-observes, so the pin moves with it.
    assert draft["expected"]["settings_profile_sha256"] != base["expected"]["settings_profile_sha256"]
    loaded = mlm.LaunchManifest.from_dict({k: v for k, v in draft.items() if not k.startswith("_")})
    contract = loaded.subagent_contract("run_x")
    assert (contract.max_concurrent, contract.max_total) == (1, 2)


def test_tool_inventory_choice_replaces_wholesale_and_dedups(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "tools_inventory": ("Read", "Grep", "Read", "Glob"),
                                "allow_tools": ("Read",), "deny_tools": ("Grep", "Glob")})
    draft, _ = _fill(world, inputs)
    assert draft["dispatch"]["subagents"]["tools_inventory"] == ["Read", "Grep", "Glob"]


def test_unpinned_inventory_tool_refuses_at_the_draft(world):
    """M0-T142 (R688/R692): a tool in the inventory but in neither rule set refuses -
    measured 2.1.252 dontAsk EXECUTES read-only commands for unlisted tools."""
    # WebFetch is outside the draft default deny list, so leaving it unpinned trips
    # the guard (Bash would inherit the default deny and pass).
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "tools_inventory": ("Read", "WebFetch"),
                                "allow_tools": ("Read",)})
    with pytest.raises(ContractError, match="neither --allow-tool nor --deny-tool"):
        _fill(world, inputs)


def test_allow_rule_outside_the_inventory_refuses(world):
    inputs = mld.DraftInputs(**{**vars(world["inputs"]), "tools_inventory": ("Read", "Grep"),
                                "allow_tools": ("Read", "Bash(git status)")})
    with pytest.raises(ContractError, match="outside the inventory"):
        _fill(world, inputs)


def test_concurrent_above_total_and_bad_limits_refuse(world):
    with pytest.raises(ContractError, match="cannot exceed max_total"):
        _fill(world, mld.DraftInputs(**{**vars(world["inputs"]), "max_concurrent": 5}))
    with pytest.raises(ContractError, match="max_total"):
        _fill(world, mld.DraftInputs(**{**vars(world["inputs"]), "max_total": 0}))
    with pytest.raises(ContractError, match="non-empty names"):
        _fill(world, mld.DraftInputs(**{**vars(world["inputs"]), "agent_inventory": ("Explore", " ")}))


# ----------------------------------------------------------------- parser contract

def test_parser_subagent_flags_map_onto_inputs():
    ns = mld.build_parser().parse_args(["--worktree", r"C:\wt", "--task-packet", r"C:\p.json",
                                        "--allow-tool", "Read", "--allow-tool", "Agent", "--deny-tool", "WebFetch",
                                        "--agent", "Explore", "--max-concurrent", "1", "--max-total", "2"])
    inputs = mld._inputs_from_args(ns)
    assert inputs.allow_tools == ("Read", "Agent") and inputs.deny_tools == ("WebFetch",)
    assert inputs.agent_inventory == ("Explore",) and inputs.tools_inventory is None
    assert (inputs.max_concurrent, inputs.max_total) == (1, 2)
    bare = mld._inputs_from_args(mld.build_parser().parse_args(["--worktree", r"C:\wt", "--task-packet", r"C:\p"]))
    assert bare.allow_tools is None and bare.max_total is None  # absent flags keep the draft default


def test_build_parser_accepts_the_runbook_shape_and_rejects_drift():
    parser = mld.build_parser()
    ns = parser.parse_args(["--worktree", r"C:\wt", "--task-packet", r"C:\p.json", "--mode", "supervised",
                            "--claude-executable", r"C:\c.exe", "--codex-executable", r"C:\x.cmd",
                            "--config", r"C:\config.toml", "--model-selection", r"C:\ms.toml",
                            "--controller-manifest", r"C:\cm.json", "--base-ref", "refs/heads/main",
                            "--claude-runtime-model-from-selection", "--out", r"C:\out.json"])
    assert ns.claude_runtime_model_from_selection is True and ns.mode == "supervised"
    with pytest.raises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
        parser.parse_args(["--worktree", r"C:\wt"])  # --task-packet is required
    with pytest.raises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
        parser.parse_args(["--worktree", r"C:\wt", "--task-packet", r"C:\p.json", "--no-such-flag"])
    with pytest.raises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
        parser.parse_args(["--worktree", r"C:\wt", "--task-packet", r"C:\p.json",
                           "--claude-runtime-model", "x", "--claude-runtime-model-from-selection"])


# ----------------------------------------------------------------- operator entrypoint (real repo)

ORIGIN = "https://github.com/martin10101/nyc-buildability.git"


def _git(root: pathlib.Path, *argv: str) -> str:
    env = {**os.environ, "GIT_AUTHOR_NAME": "supervisor-test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
           "GIT_COMMITTER_NAME": "supervisor-test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}
    return subprocess.run(["git", *argv], cwd=str(root), check=True, capture_output=True, text=True,
                          env=env).stdout


@pytest.fixture
def real(tmp_path: pathlib.Path):
    tmp = tmp_path.resolve()
    repo = tmp / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture")
    _git(repo, "remote", "add", "origin", ORIGIN)
    packet = tmp / "M0-T136.json"
    packet.write_text(json.dumps({"task_id": "M0-T136", "allowed_paths": ["tools/agent_supervisor/"]}),
                      encoding="utf-8")
    (tmp / "config.toml").write_text("[controller]\n", encoding="utf-8")
    (tmp / "model_selection.toml").write_text(SELECTION_TOML, encoding="utf-8")
    (tmp / "controller_manifest.json").write_text("{}", encoding="utf-8")
    argv = ["--worktree", str(repo), "--task-packet", str(packet), "--mode", "shadow",
            "--claude-executable", sys.executable, "--codex-executable", sys.executable,
            "--config", str(tmp / "config.toml"), "--model-selection", str(tmp / "model_selection.toml"),
            "--controller-manifest", str(tmp / "controller_manifest.json"), "--base-ref", "refs/heads/main",
            "--claude-runtime-model-from-selection", "--scratch", str(tmp / "scratch")]
    return {"tmp": tmp, "repo": repo, "packet": packet, "argv": argv, "out": tmp / "mrl" / "launch_manifest.json"}


def _main(argv) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mld.main(argv)
    return rc, out.getvalue(), err.getvalue()


def test_main_writes_a_loadable_manifest_and_refuses_to_overwrite(real):
    rc, out, _ = _main([*real["argv"], "--out", str(real["out"])])
    assert rc == 0, out
    summary = json.loads(out)
    assert summary["written"] == str(real["out"])
    assert summary["remaining_placeholders"] == []
    assert summary["task_id"] == "M0-T136" and summary["mode"] == "shadow"
    assert len(summary["settings_profile_sha256"]) == 64
    loaded = mlm.LaunchManifest.load(real["out"])
    assert loaded.dispatch["claude_executable"] == sys.executable
    assert loaded.dispatch["claude_version"] == mec.observe_version(mec.resolve_chain(sys.executable, "claude"))
    assert loaded.base_ref() == "refs/heads/main"
    assert "_draft_bindings" not in json.loads(real["out"].read_text(encoding="utf-8"))
    rc, _, err = _main([*real["argv"], "--out", str(real["out"])])
    assert rc == 3 and "already exists" in err
    rc, out, _ = _main([*real["argv"], "--out", str(real["out"]), "--force"])
    assert rc == 0


def test_main_prints_the_draft_without_out(real):
    rc, out, _ = _main(real["argv"])
    assert rc == 0
    printed = json.loads(out)
    assert printed["schema"] == mlm.MANIFEST_SCHEMA
    assert "_draft_bindings" not in printed


def test_main_relative_out_and_dirty_tree_are_rc3(real):
    rc, _, err = _main([*real["argv"], "--out", "relative.json"])
    assert rc == 3 and "absolute" in err
    (real["repo"] / "dirty.txt").write_text("x", encoding="utf-8")
    rc, _, err = _main(real["argv"])
    assert rc == 3 and "dirty tree" in err

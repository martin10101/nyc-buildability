"""Paired positive/negative tests for the MRL launch manifest (M0-T136 C-B1; D-024-R557..R560, R589).

Every R559 field has a mutation test proving the verifier refuses when ONLY that field
disagrees, and one test proves all mismatches are reported together (not first-only).
Git is driven through an injected ``run_git`` so the observations are deterministic; one
test drives the real ``git`` binary against this repository read-only.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor import mrl_launch_manifest as mlm  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import ContractError  # noqa: E402

HEAD = "a" * 40
TREE = "b" * 40
PROFILE_ID = "c" * 64
CHAIN = "d" * 64


class FakeGit:
    """Canned git answers keyed by the argv tuple; mutable so tests can perturb one value."""

    def __init__(self, worktree: pathlib.Path, common_dir: pathlib.Path):
        self.answers: dict[tuple[str, ...], str] = {
            ("rev-parse", "--show-toplevel"): f"{worktree.as_posix()}\n",
            ("rev-parse", "--path-format=absolute", "--git-common-dir"): f"{common_dir.as_posix()}\n",
            ("remote", "get-url", "origin"): "https://github.com/martin10101/nyc-buildability.git\n",
            ("rev-parse", "--abbrev-ref", "HEAD"): "candidate/D-024-mrl-option-b\n",
            ("rev-parse", "HEAD"): f"{HEAD}\n",
            ("rev-parse", "HEAD^{tree}"): f"{TREE}\n",
            ("status", "--porcelain", "--untracked-files=all"): "",
        }
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, argv, cwd):
        key = tuple(argv)
        self.calls.append(key)
        if key not in self.answers:
            raise AssertionError(f"unexpected git call {key}")
        return self.answers[key]


@pytest.fixture
def world(tmp_path: pathlib.Path):
    return build_world(tmp_path)


def build_world(tmp_path: pathlib.Path) -> dict:
    """A fake two-checkout world + one manifest that verifies clean (shared with the launch-path tests)."""
    repo_root = tmp_path / "primary"
    common = repo_root / ".git"
    common.mkdir(parents=True)
    worktree = tmp_path / "ctl24"
    worktree.mkdir()
    packet_path = tmp_path / "M0-T136.json"
    packet = {"task_id": "M0-T136", "allowed_paths": ["tools/agent_supervisor/", "docs/MRL_LAUNCH_RUNBOOK.md"]}
    packet_path.write_bytes(json.dumps(packet).encode("utf-8"))
    packet_sha = hashlib.sha256(packet_path.read_bytes()).hexdigest()
    git = FakeGit(worktree, common)
    exe = tmp_path / "bin"
    exe.mkdir()
    for name in ("claude.exe", "codex.cmd", "config.json", "model_selection.json", "controller.json"):
        (exe / name).write_text("x", encoding="utf-8")
    manifest = {
        "schema": mlm.MANIFEST_SCHEMA,
        "expected": {
            "repo_root": str(repo_root), "origin_url": "https://github.com/martin10101/nyc-buildability",
            "task_id": "M0-T136", "task_packet_sha256": packet_sha, "worktree": str(worktree),
            "branch": "candidate/D-024-mrl-option-b", "head_sha": HEAD, "tree_sha": TREE, "clean_status": True,
            "allowed_paths": ["docs/MRL_LAUNCH_RUNBOOK.md", "tools/agent_supervisor/"],
            "settings_profile_sha256": PROFILE_ID, "mode": "supervised",
        },
        "dispatch": {
            "claude_executable": str(exe / "claude.exe"), "claude_chain_sha256": CHAIN,
            "claude_model": "claude-opus-4-8", "claude_runtime_model": "claude-opus-4-8", "claude_version": "2.1.252",
            "codex_executable": str(exe / "codex.cmd"), "codex_chain_sha256": CHAIN,
            "codex_model": "gpt-5-codex", "codex_version": "0.50.0",
            "config": str(exe / "config.json"), "model_selection": str(exe / "model_selection.json"),
            "controller_manifest": str(exe / "controller.json"), "task_packet_path": str(packet_path),
            "base_ref": "refs/heads/main", "max_turns": 12, "unit_timeout_seconds": 900,
            "subagents": {"max_concurrent": 2, "max_total": 4, "agent_inventory": ["Explore"],
                          "tools_inventory": ["Read", "Grep", "Glob", "Agent"],
                          # every inventory tool is explicitly allowed or denied (M0-T142
                          # R692: an unpinned tool refuses the profile build)
                          "allow_rules": ["Read", "Grep", "Glob", "Agent"], "deny_rules": []},
        },
    }
    manifest_path = tmp_path / "launch.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return {"tmp": tmp_path, "repo_root": repo_root, "worktree": worktree, "packet_path": packet_path,
            "git": git, "manifest": manifest, "manifest_path": manifest_path}


def _verify(world, **kw):
    m = mlm.LaunchManifest.load(world["manifest_path"])
    return mlm.verify_launch(m, cli_mode=kw.pop("cli_mode", "supervised"),
                             profile_identity=kw.pop("profile_identity", PROFILE_ID), run_git=world["git"])


def _rewrite(world):
    world["manifest_path"].write_text(json.dumps(world["manifest"]), encoding="utf-8")


# ---------------------------------------------------------------- loading / shape

def test_manifest_loads_and_verifies_clean_base(world):
    v = _verify(world)
    assert v.ok and v.mismatches == ()
    assert [c.field for c in v.checks] == list(mlm.EXPECTED_FIELDS)
    assert v.to_dict()["observed"]["head_sha"] == HEAD
    assert "_status_lines" not in v.to_dict()["observed"]


def test_relative_manifest_path_refused(world):
    with pytest.raises(ContractError, match="absolute"):
        mlm.LaunchManifest.load("launch.json")


def test_missing_manifest_refused(world):
    with pytest.raises(ContractError, match="not a file"):
        mlm.LaunchManifest.load(world["tmp"] / "nope.json")


def test_invalid_json_refused(world):
    world["manifest_path"].write_text("{not json", encoding="utf-8")
    with pytest.raises(ContractError, match="valid JSON"):
        mlm.LaunchManifest.load(world["manifest_path"])


def test_wrong_schema_refused(world):
    world["manifest"]["schema"] = "mrl_launch_manifest/v0"
    _rewrite(world)
    with pytest.raises(ContractError, match="schema"):
        mlm.LaunchManifest.load(world["manifest_path"])


@pytest.mark.parametrize("field", mlm.EXPECTED_FIELDS)
def test_missing_expected_field_refused(world, field):
    del world["manifest"]["expected"][field]
    _rewrite(world)
    with pytest.raises(ContractError, match=field):
        mlm.LaunchManifest.load(world["manifest_path"])


@pytest.mark.parametrize("field", mlm.DISPATCH_FIELDS)
def test_missing_dispatch_field_refused(world, field):
    del world["manifest"]["dispatch"][field]
    _rewrite(world)
    with pytest.raises(ContractError, match=field):
        mlm.LaunchManifest.load(world["manifest_path"])


@pytest.mark.parametrize("field", mlm.SUBAGENT_FIELDS)
def test_missing_subagent_field_refused(world, field):
    del world["manifest"]["dispatch"]["subagents"][field]
    _rewrite(world)
    with pytest.raises(ContractError, match="subagents"):
        mlm.LaunchManifest.load(world["manifest_path"])


def test_clean_status_false_is_not_a_valid_manifest(world):
    world["manifest"]["expected"]["clean_status"] = False
    _rewrite(world)
    with pytest.raises(ContractError, match="clean_status must be true"):
        mlm.LaunchManifest.load(world["manifest_path"])


def test_unauthorized_mode_refused_at_load(world):
    world["manifest"]["expected"]["mode"] = "full-auto"
    _rewrite(world)
    with pytest.raises(ContractError, match="authorized mode"):
        mlm.LaunchManifest.load(world["manifest_path"])


@pytest.mark.parametrize("field,bad", [("head_sha", "abc"), ("tree_sha", "Z" * 40),
                                       ("task_packet_sha256", "x" * 63), ("settings_profile_sha256", "")])
def test_malformed_hashes_refused(world, field, bad):
    world["manifest"]["expected"][field] = bad
    _rewrite(world)
    with pytest.raises(ContractError, match=field):
        mlm.LaunchManifest.load(world["manifest_path"])


@pytest.mark.parametrize("field", ("claude_executable", "codex_executable", "config", "task_packet_path"))
def test_relative_dispatch_paths_refused(world, field):
    world["manifest"]["dispatch"][field] = "relative/path"
    _rewrite(world)
    with pytest.raises(ContractError, match=field):
        mlm.LaunchManifest.load(world["manifest_path"])


@pytest.mark.parametrize("field,bad", [("max_turns", 0), ("unit_timeout_seconds", True), ("max_turns", "12")])
def test_bad_limits_refused(world, field, bad):
    world["manifest"]["dispatch"][field] = bad
    _rewrite(world)
    with pytest.raises(ContractError, match=field):
        mlm.LaunchManifest.load(world["manifest_path"])


def test_empty_allowed_paths_refused(world):
    world["manifest"]["expected"]["allowed_paths"] = []
    _rewrite(world)
    with pytest.raises(ContractError, match="allowed_paths"):
        mlm.LaunchManifest.load(world["manifest_path"])


# ---------------------------------------------------------------- R559: one mutation per field

def _assert_only(v, field):
    assert not v.ok
    assert [c.field for c in v.mismatches] == [field], v.refusal_message()
    with pytest.raises(ContractError, match="LAUNCH REFUSED"):
        mlm.require_verified(v)


def test_mutation_repo_root(world):
    world["git"].answers[("rev-parse", "--path-format=absolute", "--git-common-dir")] = (
        (world["tmp"] / "elsewhere" / ".git").as_posix() + "\n")
    _assert_only(_verify(world), "repo_root")


def test_mutation_origin_url(world):
    world["git"].answers[("remote", "get-url", "origin")] = "https://github.com/someone-else/fork.git\n"
    _assert_only(_verify(world), "origin_url")


def test_mutation_task_id(world):
    packet = json.loads(world["packet_path"].read_text(encoding="utf-8"))
    packet["task_id"] = "M0-T999"
    world["packet_path"].write_text(json.dumps(packet), encoding="utf-8")
    world["manifest"]["expected"]["task_packet_sha256"] = hashlib.sha256(world["packet_path"].read_bytes()).hexdigest()
    _rewrite(world)
    _assert_only(_verify(world), "task_id")


def test_mutation_task_packet_sha256_same_length_edit(world):
    # Same byte length, different content: only the digest can catch it.
    data = world["packet_path"].read_bytes().replace(b"M0-T136", b"M0-T137")
    world["packet_path"].write_bytes(data)
    world["manifest"]["expected"]["task_id"] = "M0-T137"
    _rewrite(world)
    _assert_only(_verify(world), "task_packet_sha256")


def test_mutation_worktree(world):
    other = world["tmp"] / "other-worktree"
    other.mkdir()
    world["git"].answers[("rev-parse", "--show-toplevel")] = other.as_posix() + "\n"
    _assert_only(_verify(world), "worktree")


def test_mutation_branch(world):
    world["git"].answers[("rev-parse", "--abbrev-ref", "HEAD")] = "main\n"
    _assert_only(_verify(world), "branch")


def test_mutation_head_sha(world):
    world["git"].answers[("rev-parse", "HEAD")] = "e" * 40 + "\n"
    _assert_only(_verify(world), "head_sha")


def test_mutation_tree_sha_with_same_head(world):
    world["git"].answers[("rev-parse", "HEAD^{tree}")] = "f" * 40 + "\n"
    _assert_only(_verify(world), "tree_sha")


def test_mutation_clean_status_untracked_file(world):
    world["git"].answers[("status", "--porcelain", "--untracked-files=all")] = "?? scratch/note.txt\n"
    v = _verify(world)
    _assert_only(v, "clean_status")
    assert v.observed["_status_lines"] == ["?? scratch/note.txt"]


def test_mutation_allowed_paths_packet_widened(world):
    packet = json.loads(world["packet_path"].read_text(encoding="utf-8"))
    packet["allowed_paths"].append("apps/web/")
    world["packet_path"].write_text(json.dumps(packet), encoding="utf-8")
    world["manifest"]["expected"]["task_packet_sha256"] = hashlib.sha256(world["packet_path"].read_bytes()).hexdigest()
    _rewrite(world)
    _assert_only(_verify(world), "allowed_paths")


def test_mutation_settings_profile_identity(world):
    _assert_only(_verify(world, profile_identity="0" * 64), "settings_profile_sha256")


def test_mutation_mode_cli_disagrees(world):
    _assert_only(_verify(world, cli_mode="shadow"), "mode")


# ---------------------------------------------------------------- reporting + normalization

def test_all_mismatches_reported_together(world):
    world["git"].answers[("rev-parse", "HEAD")] = "e" * 40 + "\n"
    world["git"].answers[("rev-parse", "--abbrev-ref", "HEAD")] = "main\n"
    v = _verify(world, cli_mode="shadow", profile_identity="0" * 64)
    assert [c.field for c in v.mismatches] == ["branch", "head_sha", "settings_profile_sha256", "mode"]
    msg = v.refusal_message()
    assert "4 field(s) disagree" in msg and "head_sha" in msg and "mode" in msg


def test_path_comparison_is_case_and_separator_tolerant(world):
    if os.name != "nt":
        pytest.skip("case-insensitive path semantics are a Windows property")
    world["manifest"]["expected"]["worktree"] = str(world["worktree"]).upper().replace("\\", "/")
    _rewrite(world)
    assert _verify(world).ok


def test_origin_url_expected_is_normalized_before_compare(world):
    world["manifest"]["expected"]["origin_url"] = "https://github.com/martin10101/nyc-buildability.git/"
    _rewrite(world)
    assert _verify(world).ok


def test_manifest_values_never_used_as_observations(world):
    # If the observer fails, the manifest cannot fill in for it: verification raises, never passes.
    del world["git"].answers[("rev-parse", "HEAD")]
    with pytest.raises(AssertionError, match="unexpected git call"):
        _verify(world)


def test_git_failure_is_a_refusal_not_a_pass(world):
    def failing(_argv, _cwd):
        raise ContractError("contract_violation", "git rev-parse HEAD failed rc=128")
    m = mlm.LaunchManifest.load(world["manifest_path"])
    with pytest.raises(ContractError, match="rc=128"):
        mlm.verify_launch(m, cli_mode="supervised", profile_identity=PROFILE_ID, run_git=failing)


def test_packet_unreadable_refuses(world):
    world["packet_path"].unlink()
    with pytest.raises(ContractError, match="unreadable"):
        _verify(world)


def test_subagent_contract_derives_from_manifest(world):
    m = mlm.LaunchManifest.load(world["manifest_path"])
    c = m.subagent_contract("run-1")
    assert c.task_id == "M0-T136" and c.max_concurrent == 2 and c.max_total == 4
    assert c.allowed_paths == ("docs/MRL_LAUNCH_RUNBOOK.md", "tools/agent_supervisor/")


def test_profile_identity_matches_contract_builder(world, tmp_path):
    world["manifest"]["dispatch"]["managed_settings_path"] = ""  # none: deterministic across hosts
    _rewrite(world)
    m = mlm.LaunchManifest.load(world["manifest_path"])
    a, _ = mlm.observe_profile_identity(m, profile_dir=tmp_path / "p1", ledger_path=tmp_path / "p1" / "l.json")
    b, _ = mlm.observe_profile_identity(m, profile_dir=tmp_path / "p2", ledger_path=tmp_path / "p2" / "l.json")
    assert a == b and len(a) == 64
    world["manifest"]["dispatch"]["subagents"]["allow_rules"] = ["Read", "Grep"]  # a narrower policy = new identity
    world["manifest"]["dispatch"]["subagents"]["deny_rules"] = ["Glob", "Agent"]  # every tool stays pinned (R692)
    _rewrite(world)
    c, _ = mlm.observe_profile_identity(mlm.LaunchManifest.load(world["manifest_path"]), profile_dir=tmp_path / "p3",
                                        ledger_path=tmp_path / "p3" / "l.json")
    assert c != a


def test_managed_settings_default_is_platform_canonical_and_explicit_paths_are_honored(world, tmp_path):
    m = mlm.LaunchManifest.load(world["manifest_path"])
    assert m.managed_settings_path() == mlm.default_managed_settings_path()
    assert mlm.default_managed_settings_path("win32").name == "managed-settings.json"
    assert mlm.default_managed_settings_path("linux").as_posix() == "/etc/claude-code/managed-settings.json"
    world["manifest"]["dispatch"]["managed_settings_path"] = ""
    _rewrite(world)
    assert mlm.LaunchManifest.load(world["manifest_path"]).managed_settings_path() is None
    world["manifest"]["dispatch"]["managed_settings_path"] = "relative/managed.json"
    _rewrite(world)
    with pytest.raises(ContractError, match="managed_settings_path"):
        mlm.LaunchManifest.load(world["manifest_path"]).managed_settings_path()


def test_managed_policy_presence_changes_profile_identity(world, tmp_path):
    managed = tmp_path / "managed-settings.json"
    world["manifest"]["dispatch"]["managed_settings_path"] = str(managed)
    _rewrite(world)
    m = mlm.LaunchManifest.load(world["manifest_path"])
    absent, _ = mlm.observe_profile_identity(m, profile_dir=tmp_path / "a", ledger_path=tmp_path / "a" / "l.json")
    managed.write_text('{"permissions": {"deny": ["Bash"]}}', encoding="utf-8")
    present, _ = mlm.observe_profile_identity(m, profile_dir=tmp_path / "b", ledger_path=tmp_path / "b" / "l.json")
    assert absent != present  # a policy installed after the manifest was pinned refuses the launch


# ---------------------------------------------------------------- drafting entrypoint

def test_draft_manifest_from_observation(world):
    d = mlm.draft_manifest(str(world["worktree"]), str(world["packet_path"]), mode="shadow", run_git=world["git"])
    assert d["schema"] == mlm.MANIFEST_SCHEMA
    assert d["expected"]["head_sha"] == HEAD and d["expected"]["mode"] == "shadow"
    assert d["expected"]["clean_status"] is True
    assert d["dispatch"]["task_packet_path"] == str(world["packet_path"].resolve())
    assert d["dispatch"]["claude_chain_sha256"] == "<fill>"  # a draft never asserts identities it did not bind
    assert d["dispatch"]["base_ref"].startswith("<fill")  # C-B4: a draft never binds a base ref by default


# ---------------------------------------------------------------- base_ref (C-B4; R504/R505)

def test_base_ref_is_read_verbatim(world):
    m = mlm.LaunchManifest.load(world["manifest_path"])
    assert m.base_ref() == "refs/heads/main"
    world["manifest"]["dispatch"]["base_ref"] = "  refs/heads/integration/x  "
    _rewrite(world)
    assert mlm.LaunchManifest.load(world["manifest_path"]).base_ref() == "refs/heads/integration/x"


@pytest.mark.parametrize("bad", [None, "", "   ", 7, "<fill: e.g. refs/heads/main>"])
def test_base_ref_never_defaults(world, bad):
    """Absent, blank, non-string, or unfilled-draft base_ref refuses; nothing guesses origin/main."""
    if bad is None:
        del world["manifest"]["dispatch"]["base_ref"]
    else:
        world["manifest"]["dispatch"]["base_ref"] = bad
    _rewrite(world)
    m = mlm.LaunchManifest.load(world["manifest_path"])  # loading still succeeds: the field is optional at load
    with pytest.raises(ContractError) as info:
        m.base_ref()
    assert info.value.code == "launch_manifest_base_ref_missing"


def test_draft_refuses_dirty_tree(world):
    world["git"].answers[("status", "--porcelain", "--untracked-files=all")] = " M tools/x.py\n"
    with pytest.raises(ContractError, match="dirty tree"):
        mlm.draft_manifest(str(world["worktree"]), str(world["packet_path"]), mode="shadow", run_git=world["git"])


def test_observe_main_profile_subcommand(world, capsys):
    rc = mlm.main(["observe", "--worktree", str(world["worktree"]), "--task-packet", str(world["packet_path"]),
                   "--profile", str(world["manifest_path"]), "--scratch", str(world["tmp"] / "scratch")])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["settings_profile_sha256"]) == 64
    assert out["managed_settings_path"] == str(mlm.default_managed_settings_path())


def test_observe_main_reports_contract_error_rc3(world, capsys):
    rc = mlm.main(["observe", "--worktree", str(world["tmp"] / "missing"), "--task-packet", str(world["packet_path"])])
    assert rc == 3
    assert "not a directory" in capsys.readouterr().err


# ---------------------------------------------------------------- real git, read-only

def test_real_git_observation_of_this_repository():
    if subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT, capture_output=True).returncode != 0:
        pytest.skip("not a git checkout")
    packet = ROOT / "project-control" / "tasks" / "M0-T136.json"
    if not packet.is_file():
        pytest.skip("packet absent")
    obs = mlm.observe(str(ROOT), str(packet))
    assert obs["task_id"] == "M0-T136"
    assert len(obs["head_sha"]) == 40 and len(obs["tree_sha"]) == 40 and obs["head_sha"] != obs["tree_sha"]
    assert mlm.normalize_path(obs["worktree"]) == mlm.normalize_path(str(ROOT))
    assert pathlib.Path(obs["repo_root"]).is_dir()
    assert obs["origin_url"].startswith("https://github.com/") and not obs["origin_url"].endswith(".git")
    assert obs["allowed_paths"] == sorted(obs["allowed_paths"])

"""M0-T136 C-B3: bounded-subagent contract, controller ledger, restricted profile, hook
(D-024-R566..R579). Paired positive/negative cases for every contract clause."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import threading

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor import mrl_subagent_contract as msc  # noqa: E402
from tools.agent_supervisor import mrl_subagent_hook as hook  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import ContractError  # noqa: E402

HOOK = ROOT / "tools" / "agent_supervisor" / "mrl_subagent_hook.py"


def _contract(**over):
    base = dict(run_id="run-1", task_id="M0-T999", repo_root="C:/repo", allowed_paths=("tools/",),
                tools_inventory=("Read", "Grep", "Glob", "Edit", "Agent"),
                agent_inventory=("Explore", "code-reviewer"), max_concurrent=2, max_total=3)
    base.update(over)
    return msc.SubagentContract(**base)


@pytest.fixture
def ledger(tmp_path):
    return msc.SubagentLedger.create(tmp_path / "ledger.json", _contract(), primary_id="run-1.primary")


def _req(ledger, **over):
    base = dict(parent_id="run-1.primary", subagent_type="Explore", description="d", depth=1,
                background=False)
    base.update(over)
    return ledger.request(**base)


# ---------------------------------------------------------------- contract

class TestContract:
    def test_valid_contract_round_trips(self):
        c = _contract()
        assert msc.SubagentContract.from_dict(c.to_dict()) == c

    @pytest.mark.parametrize("over", [
        dict(max_depth=2),                      # depth is fixed at one (R568)
        dict(foreground_only=False),            # foreground only (R569)
        dict(writer_policy="isolated-worktrees"),  # not implemented in Tranche B -> refused
        dict(writer_policy="anything-goes"),
        dict(max_concurrent=3, max_total=2),
        dict(max_concurrent=-1),
        dict(max_total=True),
        dict(run_id=""),
        dict(allowed_paths=("tools/", "")),
        dict(tools_inventory=("Read", 3)),
    ])
    def test_invalid_contract_refuses(self, over):
        with pytest.raises(ContractError):
            _contract(**over)

    def test_malformed_dict_refuses(self):
        with pytest.raises(ContractError, match="malformed"):
            msc.SubagentContract.from_dict({"run_id": "x"})


# ---------------------------------------------------------------- ledger accounting

class TestLedger:
    def test_issue_release_and_accounting(self, ledger):
        d1 = _req(ledger)
        d2 = _req(ledger, subagent_type="code-reviewer")
        assert d1.allowed and d2.allowed and d1.child_id == "run-1.primary.c001" and d2.child_id.endswith("c002")
        acc = ledger.accounting()
        assert acc["processes_total"] == 3 and acc["subagents_live"] == 2
        ledger.release(d1.child_id)
        assert ledger.accounting()["subagents_live"] == 1
        assert ledger.accounting()["unreleased_child_ids"] == [d2.child_id]

    def test_concurrent_limit_denies_then_frees(self, ledger):
        a = _req(ledger)
        _req(ledger)
        denied = _req(ledger)
        assert not denied.allowed and "concurrent limit 2" in denied.reason
        ledger.release(a.child_id)
        assert _req(ledger).allowed

    def test_total_limit_denies_even_after_release(self, ledger):
        ids = []
        for _ in range(3):
            d = _req(ledger)
            assert d.allowed
            ids.append(d.child_id)
            ledger.release(d.child_id)
        over = _req(ledger)
        assert not over.allowed and "total limit 3" in over.reason
        assert ledger.accounting()["subagents_denied"] == 1

    @pytest.mark.parametrize("over, fragment", [
        (dict(depth=2), "depth 2 exceeds"),
        (dict(parent_id="run-1.primary.c001"), "depth>1"),
        (dict(background=True), "foreground only"),
        (dict(isolation="worktree"), "git worktree"),
        (dict(mcp=True), "MCP access is denied"),
        (dict(subagent_type="general-purpose"), "outside the controller inventory"),
        (dict(subagent_type=""), "outside the controller inventory"),
    ])
    def test_each_clause_denies(self, ledger, over, fragment):
        d = _req(ledger, **over)
        assert not d.allowed and fragment in d.reason
        assert ledger.accounting()["subagents_issued"] == 0

    def test_release_unknown_or_twice_refuses(self, ledger):
        d = _req(ledger)
        ledger.release(d.child_id)
        with pytest.raises(ContractError):
            ledger.release(d.child_id)
        with pytest.raises(ContractError):
            ledger.release("run-1.primary.c999")
        with pytest.raises(ContractError, match="no live subagent"):
            ledger.release_latest_live()

    def test_close_stops_issuance(self, ledger):
        acc = ledger.close()
        assert acc["closed"] is True
        d = _req(ledger)
        assert not d.allowed and "closed" in d.reason

    def test_bad_schema_or_missing_file_refuses(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text('{"schema": "other"}', encoding="utf-8")
        with pytest.raises(ContractError, match="schema"):
            msc.SubagentLedger(bad).accounting()
        with pytest.raises(ContractError, match="unreadable"):
            msc.SubagentLedger(tmp_path / "missing.json").accounting()

    def test_parallel_requests_never_exceed_limits(self, tmp_path):
        led = msc.SubagentLedger.create(tmp_path / "l.json", _contract(max_concurrent=2, max_total=5),
                                        primary_id="run-1.primary")
        results = []

        def worker():
            results.append(_req(led).allowed)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert results.count(True) == 2 and results.count(False) == 6

    def test_lock_timeout_fails_closed(self, ledger, monkeypatch):
        monkeypatch.setattr(msc, "_LOCK_TIMEOUT_S", 0.05)
        lock = ledger.path.with_suffix(".json.lock")
        lock.write_text("held", encoding="utf-8")
        with pytest.raises(ContractError, match="fail closed"):
            _req(ledger)


# ---------------------------------------------------------------- restricted profile

class TestRestrictedProfile:
    def _build(self, tmp_path, **over):
        # every inventory tool explicitly allowed or denied (M0-T142 R692)
        kw = dict(ledger_path=tmp_path / "ledger.json", hook_script=HOOK, allow_rules=("Read", "Grep", "Glob"),
                  deny_rules=("Edit", "Agent"), profile_dir=tmp_path / "profile", model="claude-opus-4-8")
        kw.update(over)
        return msc.build_restricted_profile(_contract(), **kw)

    def test_flags_compose_every_real_mechanism(self, tmp_path):
        p = self._build(tmp_path)
        flags = list(p.argv_flags)
        assert flags[:3] == ["--restricted", "--permission-mode", "dontAsk"]
        assert flags[flags.index("--tools") + 1] == "Read,Grep,Glob,Edit,Agent"
        assert "--strict-mcp-config" in flags and "--mcp-config" not in flags
        assert flags[flags.index("--settings") + 1] == p.profile_path
        assert "--allowedTools" in flags and "--disallowedTools" in flags
        assert flags[flags.index("--disallowedTools") + 1:] == ["Edit", "Agent", "mcp__*"]
        assert set(json.loads(flags[flags.index("--agents") + 1])) == {"Explore", "code-reviewer"}
        written = json.loads(pathlib.Path(p.profile_path).read_text(encoding="utf-8"))
        assert written["permissions"]["defaultMode"] == "dontAsk"
        assert "mcp__*" in written["permissions"]["deny"]
        pre = written["hooks"]["PreToolUse"][0]
        assert pre["matcher"] == "Agent|Task" and "--event pre" in pre["hooks"][0]["command"]
        assert str(HOOK) in pre["hooks"][0]["command"]
        assert written["hooks"]["PostToolUse"][0]["hooks"][0]["command"].endswith("--event post")
        assert written["mrl"]["allowed_paths"] == ["tools/"] and written["mrl"]["task_id"] == "M0-T999"
        assert all(a["tools"] == ["Read", "Grep", "Glob"] and a["model"] == "claude-opus-4-8"
                   for a in p.agents.values())
        assert len(p.identity_sha256) == 64

    def test_tools_alone_grants_nothing(self, tmp_path):
        p = self._build(tmp_path, allow_rules=(),
                        deny_rules=("Read", "Grep", "Glob", "Edit", "Agent"))
        assert "--tools" in p.argv_flags and "--allowedTools" not in p.argv_flags
        assert p.effective_grants() == frozenset()
        q = self._build(tmp_path, allow_rules=("Read", "Edit(tools/**)"),
                        deny_rules=("Grep", "Glob", "Agent"))
        assert q.effective_grants() == frozenset({"Read", "Edit"})

    def test_deny_beats_allow_and_inventory(self, tmp_path):
        p = self._build(tmp_path, allow_rules=("Read", "Edit"),
                        deny_rules=("Edit", "Grep", "Glob", "Agent"))
        assert p.effective_grants() == frozenset({"Read"})

    def test_unpinned_inventory_tool_refuses(self, tmp_path):
        """M0-T142 (R688/R692): 2.1.252 dontAsk EXECUTES read-only commands for a
        tool merely absent from the allow rules - so an inventory tool that is
        neither allowed nor denied refuses the profile outright."""
        with pytest.raises(ContractError, match="neither allow-ruled nor deny-ruled"):
            self._build(tmp_path, deny_rules=("Edit",))  # Agent left unpinned

    def test_bash_bare_deny_is_load_bearing(self, tmp_path):
        """AS-PB-1: the canary shape - Bash in the inventory, bare-denied - flows
        into BOTH permissions.deny and --disallowedTools."""
        p = msc.build_restricted_profile(
            _contract(tools_inventory=("Bash", "Read", "Grep", "Glob", "Agent")),
            ledger_path=tmp_path / "l.json", hook_script=HOOK,
            allow_rules=("Read", "Grep", "Glob", "Agent"), deny_rules=("Bash",),
            profile_dir=tmp_path / "p", model="claude-opus-4-8")
        flags = list(p.argv_flags)
        assert flags[flags.index("--disallowedTools") + 1:] == ["Bash", "mcp__*"]
        written = json.loads(pathlib.Path(p.profile_path).read_text(encoding="utf-8"))
        assert "Bash" in written["permissions"]["deny"]
        assert "Bash" not in written["permissions"]["allow"]
        assert p.effective_grants() == frozenset({"Read", "Grep", "Glob", "Agent"})

    def test_allow_outside_inventory_refuses(self, tmp_path):
        with pytest.raises(ContractError, match="outside the inventory"):
            self._build(tmp_path, allow_rules=("WebFetch",))

    def test_mcp_allow_refuses(self, tmp_path):
        with pytest.raises(ContractError, match="MCP"):
            msc.build_restricted_profile(_contract(tools_inventory=("Read", "mcp__x__y")),
                                         ledger_path=tmp_path / "l.json", hook_script=HOOK,
                                         allow_rules=("mcp__x__y",), profile_dir=tmp_path, model="m")

    def test_missing_hook_or_model_refuses(self, tmp_path):
        with pytest.raises(ContractError, match="hook"):
            self._build(tmp_path, hook_script=tmp_path / "nope.py")
        with pytest.raises(ContractError, match="model"):
            self._build(tmp_path, model="")

    def test_managed_policy_is_accounted_present_and_absent(self, tmp_path):
        absent = self._build(tmp_path, managed_settings_path=tmp_path / "managed-settings.json")
        assert absent.settings["mrl"]["managed_policy"] == {
            "path": str(tmp_path / "managed-settings.json"), "present": False, "sha256": None}
        (tmp_path / "managed-settings.json").write_text('{"permissions": {}}', encoding="utf-8")
        present = self._build(tmp_path, managed_settings_path=tmp_path / "managed-settings.json")
        assert present.settings["mrl"]["managed_policy"]["present"] is True
        assert present.identity_sha256 != absent.identity_sha256   # unaccounted policy changes identity

    def test_identity_changes_with_profile_bytes(self, tmp_path):
        a = self._build(tmp_path)
        b = self._build(tmp_path, allow_rules=("Read",),
                        deny_rules=("Grep", "Glob", "Edit", "Agent"))
        assert a.identity_sha256 != b.identity_sha256

    def test_identity_is_policy_not_run_dir(self, tmp_path):
        # Same policy in two different run directories -> same pinnable identity ...
        a = self._build(tmp_path, ledger_path=tmp_path / "run-a" / "ledger.json", profile_dir=tmp_path / "run-a")
        b = self._build(tmp_path, ledger_path=tmp_path / "run-b" / "ledger.json", profile_dir=tmp_path / "run-b")
        assert a.identity_sha256 == b.identity_sha256
        # ... while a modified hook script (same rules) changes it.
        edited = tmp_path / "hook_copy.py"
        edited.write_bytes(HOOK.read_bytes() + b"\n# tampered\n")
        c = self._build(tmp_path, hook_script=edited, profile_dir=tmp_path / "run-c")
        assert c.identity_sha256 != a.identity_sha256


# ---------------------------------------------------------------- hook (in-process and real subprocess)

def _payload(**over):
    base = {"hook_event_name": "PreToolUse", "tool_name": "Agent",
            "tool_input": {"subagent_type": "Explore", "description": "trace", "prompt": "x"}}
    base.update(over)
    return base


class TestHook:
    def test_pre_allows_and_post_releases(self, ledger, capsys):
        assert hook.decide(_payload(), ledger, "run-1.primary", "pre") == 0
        assert json.loads(capsys.readouterr().out)["mrl_child_id"] == "run-1.primary.c001"
        assert ledger.accounting()["subagents_live"] == 1
        assert hook.decide(_payload(hook_event_name="PostToolUse"), ledger, "run-1.primary", "post") == 0
        assert ledger.accounting()["subagents_live"] == 0

    def test_pre_from_a_subagent_is_depth_two_and_denied(self, ledger, capsys):
        assert hook.decide(_payload(agent_type="Explore"), ledger, "run-1.primary", "pre") == 2
        assert "depth 2" in capsys.readouterr().err
        assert hook.decide(_payload(agent_id="abc"), ledger, "run-1.primary", "pre") == 2

    def test_pre_out_of_inventory_background_isolation_mcp_denied(self, ledger, capsys):
        for tool_input in ({"subagent_type": "general-purpose", "description": "d"},
                           {"subagent_type": "Explore", "run_in_background": True},
                           {"subagent_type": "Explore", "isolation": "worktree"},
                           {"subagent_type": "mcp__server__agent"}):
            assert hook.decide(_payload(tool_input=tool_input), ledger, "run-1.primary", "pre") == 2
        assert hook.decide(_payload(tool_name="mcp__x__spawn"), ledger, "run-1.primary", "pre") == 2
        assert ledger.accounting()["subagents_denied"] == 5

    def test_over_limit_denied(self, ledger):
        assert hook.decide(_payload(), ledger, "run-1.primary", "pre") == 0
        assert hook.decide(_payload(), ledger, "run-1.primary", "pre") == 0
        assert hook.decide(_payload(), ledger, "run-1.primary", "pre") == 2

    def test_malformed_payload_fails_closed(self, ledger):
        assert hook.decide("not-an-object", ledger, "run-1.primary", "pre") == 2
        assert hook.decide({"tool_name": "Agent"}, ledger, "run-1.primary", "pre") == 2
        assert hook.decide({"tool_input": "str"}, ledger, "run-1.primary", "pre") == 2

    def test_post_never_blocks_even_with_nothing_live(self, ledger, capsys):
        assert hook.decide(_payload(), ledger, "run-1.primary", "post") == 0
        assert "accounting warning" in capsys.readouterr().err

    def test_real_subprocess_invocation_matches_profile_command(self, tmp_path):
        contract = _contract(max_concurrent=1, max_total=1)
        ledger = msc.SubagentLedger.create(tmp_path / "ledger.json", contract, primary_id="run-1.primary")
        profile = msc.build_restricted_profile(contract, ledger_path=ledger.path, hook_script=HOOK,
                                               allow_rules=("Read",),
                                               deny_rules=("Grep", "Glob", "Edit", "Agent"),
                                               profile_dir=tmp_path / "p", model="m")
        cmd = profile.settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        assert cmd.startswith(f'"{sys.executable}"')
        base = [sys.executable, str(HOOK), "--ledger", str(ledger.path), "--parent", "run-1.primary"]
        first = subprocess.run([*base, "--event", "pre"], input=json.dumps(_payload()), capture_output=True,
                               text=True, timeout=60)
        assert first.returncode == 0, first.stderr
        assert json.loads(first.stdout)["mrl_child_id"] == "run-1.primary.c001"
        second = subprocess.run([*base, "--event", "pre"], input=json.dumps(_payload()), capture_output=True,
                                text=True, timeout=60)
        assert second.returncode == 2 and "concurrent limit 1" in second.stderr
        post = subprocess.run([*base, "--event", "post"], input=json.dumps(_payload()), capture_output=True,
                              text=True, timeout=60)
        assert post.returncode == 0
        garbage = subprocess.run([*base, "--event", "pre"], input="{not json", capture_output=True,
                                 text=True, timeout=60)
        assert garbage.returncode == 2 and "fail closed" in garbage.stderr
        acc = ledger.accounting()
        assert acc == {"primary_id": "run-1.primary", "processes_total": 2, "subagents_issued": 1,
                       "subagents_live": 0, "subagents_denied": 1, "unreleased_child_ids": [], "closed": False}

"""Correlation-bound runtime-identity tests (M0-T142; D-024-R686/R687/R690/R691/R695).

Every fixture derives from the PRESERVED live run canary-b5-02r1 (2026-09-02):
result modelUsage {claude-opus-4-8, claude-haiku-4-5-20251001, claude-opus-4-8[1m]}
while all 68 assistant turns (main + sidechains) ran exactly the pinned
claude-opus-4-8; session 7a8f8a17-11b0-4f36-aa25-89bfb41b834d in cwd
C:\\Users\\MLFLL\\Downloads\\nyc-zoning\\ctl24 stored under project key
C--Users-MLFLL-Downloads-nyc-zoning-ctl24. The binding (cwd -> project key ->
<session_id>.jsonl, sessionId equality on every carrying line, cwd equality on
main-chain turns) is what R690 requires to be explicitly added AND tested.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor import mrl_runtime_identity as mri  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import ContractError  # noqa: E402

PIN = "claude-opus-4-8"
HAIKU = "claude-haiku-4-5-20251001"
TIER = PIN + "[1m]"
SESSION = "7a8f8a17-11b0-4f36-aa25-89bfb41b834d"
#: The live run's aggregate, verbatim (one_shot_unit.json observed_models).
CANARY_USAGE = (HAIKU, PIN, TIER)


def assistant_line(model=PIN, *, session=SESSION, cwd="", sidechain=False, tools=()):
    content = [{"type": "text", "text": "x"}]
    content += [{"type": "tool_use", "name": name, "input": {}} for name in tools]
    event = {"type": "assistant", "sessionId": session, "isSidechain": sidechain,
             "message": {"role": "assistant", "model": model, "content": content}}
    if cwd:
        event["cwd"] = cwd
    return json.dumps(event)


def queue_line(session=SESSION):
    return json.dumps({"type": "queue-operation", "operation": "enqueue", "sessionId": session})


def write_transcript(base: pathlib.Path, cwd: str, lines, session=SESSION) -> pathlib.Path:
    path = mri.transcript_path(base, cwd, session)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def verify(base, cwd, *, usage=CANARY_USAGE, expected=PIN, session=SESSION):
    return mri.verify_primary_model(expected_model=expected, session_id=session, cwd=cwd,
                                    usage_models=list(usage), transcript_base=base)


# ---------------------------------------------------------------- the R690 binding itself

def test_project_key_matches_the_real_observed_directory():
    # The preserved live run's transcript directory name, verbatim.
    assert mri.project_key(r"C:\Users\MLFLL\Downloads\nyc-zoning\ctl24") \
        == "C--Users-MLFLL-Downloads-nyc-zoning-ctl24"


def test_transcript_path_shape():
    p = mri.transcript_path(pathlib.Path(r"C:\u\.claude"), r"C:\w t\x", "sess-9")
    assert p == pathlib.Path(r"C:\u\.claude") / "projects" / "C--w-t-x" / "sess-9.jsonl"


def test_config_base_prefers_the_child_claude_config_dir(tmp_path):
    assert mri.config_base({"CLAUDE_CONFIG_DIR": str(tmp_path)}) == tmp_path
    assert mri.config_base({"USERPROFILE": r"C:\u"}) == pathlib.Path(r"C:\u") / ".claude"
    with pytest.raises(ContractError) as exc:
        mri.config_base({})
    assert exc.value.code == "transcript_unresolvable"


def test_foreign_session_id_on_any_line_refuses(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [queue_line("someone-else"), assistant_line(cwd=cwd)])
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, cwd)
    assert exc.value.code == "transcript_uncorrelated"


def test_foreign_cwd_on_a_main_chain_turn_refuses(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [assistant_line(cwd=r"C:\somewhere\else")])
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, cwd)
    assert exc.value.code == "transcript_uncorrelated"


def test_missing_transcript_refuses(tmp_path):
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, str(tmp_path / "wt"))
    assert exc.value.code == "transcript_missing"


def test_no_correlated_line_refuses(tmp_path):
    cwd = str(tmp_path / "wt")
    path = mri.transcript_path(tmp_path, cwd, SESSION)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"type": "summary"}) + "\n", encoding="utf-8")
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, cwd)
    assert exc.value.code == "transcript_uncorrelated"


def test_zero_assistant_turns_refuses(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [queue_line()])
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, cwd)
    assert exc.value.code == "transcript_no_turns"


# ---------------------------------------------------------------- R686/R691: the canary shape settles

def test_canary_b5_02r1_shape_verifies(tmp_path):
    """The EXACT live failure shape: multi-key aggregate + pinned turns -> PASS."""
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [
        queue_line(),
        assistant_line(cwd=cwd, tools=("Bash",)),
        assistant_line(cwd=cwd, tools=("Agent", "Agent")),
        assistant_line(sidechain=True, tools=("Read",)),  # sidechain turns are not primary
        assistant_line(cwd=cwd, tools=("Glob", "Glob", "Bash", "StructuredOutput")),
    ])
    evidence, tools = verify(tmp_path, cwd)
    assert evidence.primary_model == PIN
    assert evidence.primary_models_observed == (PIN,)
    # auxiliary = OTHER models only; the pin's [1m] key is the same family
    # (a distinct context tier, R687), surfaced via context_tier_used instead.
    assert evidence.auxiliary_models == (HAIKU,)
    assert evidence.assistant_turns == 3  # main-chain only
    assert evidence.context_tier_used is True  # the [1m] usage key
    assert tools == {"Bash": 2, "Agent": 2, "Glob": 2, "StructuredOutput": 1}


def test_auxiliary_usage_never_masquerades_as_primary(tmp_path):
    """Aggregate contains the pin, but a MAIN turn ran haiku -> refuse (R691)."""
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [assistant_line(cwd=cwd), assistant_line(HAIKU, cwd=cwd)])
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, cwd)
    assert HAIKU in exc.value.message and "pinned" in exc.value.message


def test_pinned_model_absent_from_aggregate_refuses(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [assistant_line(cwd=cwd)])
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, cwd, usage=(HAIKU,))
    assert "absent from the session usage aggregate" in exc.value.message


def test_empty_aggregate_refuses(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [assistant_line(cwd=cwd)])
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, cwd, usage=())
    assert "empty model-usage aggregate" in exc.value.message


def test_genuinely_different_primary_model_refuses(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [assistant_line("claude-fable-5", cwd=cwd)])
    with pytest.raises(ContractError) as exc:
        verify(tmp_path, cwd, usage=("claude-fable-5", PIN))
    assert "claude-fable-5" in exc.value.message


# ---------------------------------------------------------------- R687: the [1m] context tier

def test_pinned_context_tier_turn_is_the_same_model(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [assistant_line(TIER, cwd=cwd), assistant_line(cwd=cwd)])
    evidence, _tools = verify(tmp_path, cwd, usage=(PIN,))
    assert evidence.primary_model == PIN
    assert evidence.primary_models_observed == (TIER, PIN)
    assert evidence.context_tier_used is True


def test_tier_suffix_on_a_different_model_refuses(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, [assistant_line("claude-fable-5[1m]", cwd=cwd)])
    with pytest.raises(ContractError):
        verify(tmp_path, cwd)


def test_model_matches_pin_is_exact():
    assert mri.model_matches_pin(PIN, PIN)
    assert mri.model_matches_pin(TIER, PIN)
    assert not mri.model_matches_pin("claude-fable-5[1m]", PIN)
    assert not mri.model_matches_pin(PIN + "[2m]", PIN)
    assert not mri.model_matches_pin("x" + PIN, PIN)
    assert not mri.model_matches_pin("", PIN)


# ---------------------------------------------------------------- guard-rails

def test_missing_pin_or_session_refuse(tmp_path):
    with pytest.raises(ContractError):
        mri.verify_primary_model(expected_model="", session_id=SESSION, cwd="x",
                                 usage_models=[PIN], transcript_base=tmp_path)
    with pytest.raises(ContractError):
        mri.verify_primary_model(expected_model=PIN, session_id="", cwd="x",
                                 usage_models=[PIN], transcript_base=tmp_path)


def test_torn_lines_are_skipped_but_never_trusted(tmp_path):
    cwd = str(tmp_path / "wt")
    write_transcript(tmp_path, cwd, ['{"truncated', assistant_line(cwd=cwd)])
    evidence, _tools = verify(tmp_path, cwd)
    assert evidence.assistant_turns == 1

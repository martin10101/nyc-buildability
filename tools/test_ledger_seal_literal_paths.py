#!/usr/bin/env python3
"""Focused tests for the literal-allowed-paths seal (backlog DB-181; owner D-090-R557;
M0-T188). The seal refuses a glob/pattern allowed_paths entry at contract time, claim and
submit, because under GIT_LITERAL_PATHSPECS=1 a pattern binds NO tracked file, so the
reviewed content identity would cover less than the packet declares. Option B: patterns are
REFUSED, never EXPANDED -- the identity algorithm is byte-unchanged.

Covers: the shared detector pattern_allowed_paths() one-per-input-state (S2-S9), the frozen
grandfather allowlist, the CLI refusal helper's grandfather/new/literal/non-regime arms, the
validator static catch (c18), and the migration proof that the new check adds ZERO errors on
the real ledger (the grandfather allowlist covers every pre-existing in-regime pattern task).

Stdlib + pytest. Run: pytest -q tools/test_ledger_seal_literal_paths.py. Lifecycle (claim/
submit) refusal is proven in tools/test_project_control.py::test_s13_pattern_allowed_paths_seal.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import directive_registry as dr          # noqa: E402  (shared detector + frozen allowlist)
import project_control as pc             # noqa: E402  (CLI refusal helper)
import validate_directive_compliance as vd  # noqa: E402  (static catch c18)

BRACKET_ROUTE = "apps/web/src/app/survey/review/[documentId]/page.tsx"

# One row per input state (the producer-report table). (state_id, allowed_paths, expected
# offenders). A pattern == contains '*' or '?' or begins with ':'; '[' / ']' alone is NOT a
# pattern (the tracked Next.js bracket route binds literally under GIT_LITERAL_PATHSPECS=1).
DETECTOR_STATES = [
    ("S2_literal_file", ["tools/directive_registry.py"], []),
    ("S3_literal_folder", ["docs/measurement-basis"], []),
    ("S4_double_star", ["docs/measurement-basis/**"], ["docs/measurement-basis/**"]),
    ("S5_star_in_name",
     ["services/api/app/scenario/three_answers/result_way_bridge_*.py"],
     ["services/api/app/scenario/three_answers/result_way_bridge_*.py"]),
    ("S6_nonexistent_literal", ["tools/a_new_file_not_yet_created.py"], []),
    ("S7_mixed", ["tools/project_control.py", "services/api/**"], ["services/api/**"]),
    ("S8_empty", [], []),
    ("S9_bracket_route", [BRACKET_ROUTE], []),
]


def test_pattern_detector_one_per_state():
    for sid, allowed, expected in DETECTOR_STATES:
        assert dr.pattern_allowed_paths(allowed) == expected, f"{sid}: {allowed}"


def test_pattern_detector_question_mark_and_pathspec_magic():
    # '?' is a glob magic char; a leading ':' is pathspec magic (e.g. ':(exclude)').
    assert dr.pattern_allowed_paths(["docs/file?.md"]) == ["docs/file?.md"]
    assert dr.pattern_allowed_paths([":(exclude)services/api"]) == [":(exclude)services/api"]
    assert dr.pattern_allowed_paths([":/services"]) == [":/services"]


def test_pattern_detector_non_string_fails_closed():
    # A malformed non-string entry must NOT slip through as a bound path.
    assert dr.pattern_allowed_paths([123]) == [123]
    assert dr.pattern_allowed_paths([None]) == [None]


def test_grandfather_allowlist_shape():
    gf = dr.PATTERN_ALLOWED_PATHS_GRANDFATHERED
    assert isinstance(gf, frozenset)
    assert len(gf) == 88, f"expected 77 accepted + 11 in-flight = 88, got {len(gf)}"
    for tid in ("M5-T126", "M4-T033", "M5-T130"):   # the DB-181 named examples
        assert tid in gf, tid
    assert "M0-T188" not in gf, "M0-T188 binds literally; it must not be grandfathered"


def test_cli_refusal_helper_arms():
    in_regime = {"directive_refs": [{"directive_id": "D-x", "requirement_ids": "ALL"}]}
    # a NEW in-regime task with a pattern (plus a literal report) is refused, naming the entry.
    t_new = {**in_regime,
             "allowed_paths": ["services/api/**", "project-control/reports/x.md"]}
    err = pc._pattern_allowed_paths_check(t_new, "M9-T999-new")
    assert err and "services/api/**" in err and "literal" in err.lower()
    assert "project-control/reports/x.md" not in err  # the literal report is never named
    # a grandfathered id with the same pattern is EXEMPT (its packet is not rewritten).
    t_gf = {**in_regime, "allowed_paths": ["docs/measurement-basis/**"]}
    assert pc._pattern_allowed_paths_check(t_gf, "M5-T126") is None
    # a literal-only in-regime task is accepted.
    assert pc._pattern_allowed_paths_check(
        {**in_regime, "allowed_paths": ["tools/project_control.py"]}, "M9-T998") is None
    # a NOT-in-regime task is not checked here (regime entry is enforced earlier at claim).
    assert pc._pattern_allowed_paths_check(
        {"allowed_paths": ["services/api/**"]}, "M9-T997") is None


def _write_task(td: Path, tid: str, allowed, in_regime=True):
    obj = {"task_id": tid, "allowed_paths": allowed}
    if in_regime:
        obj["directive_regime_version"] = "1.0"
    (td / f"{tid}.json").write_text(json.dumps(obj), encoding="utf-8")


def test_validator_static_catch_c18(tmp_path):
    td = tmp_path / "tasks"
    td.mkdir()
    _write_task(td, "M9-NEW", ["services/api/**"])                 # flagged
    _write_task(td, "M5-T126", ["docs/measurement-basis/**"])      # grandfathered -> not flagged
    _write_task(td, "M9-LIT", ["tools/project_control.py"])        # literal -> not flagged
    _write_task(td, "M9-LEGACY", ["services/api/**"], in_regime=False)  # not in regime -> skip
    errs = vd._validate_pattern_allowed_paths(td)
    joined = "\n".join(errs)
    assert any("M9-NEW" in e and "services/api/**" in e for e in errs), joined
    assert "M5-T126" not in joined
    assert "M9-LIT" not in joined
    assert "M9-LEGACY" not in joined


def test_migration_proof_zero_new_flags_on_real_ledger():
    """The frozen grandfather allowlist covers every pre-existing in-regime pattern task, so
    the c18 static catch adds ZERO errors at HEAD -- i.e. validate --check stays exit 0.
    (The authoritative before/after exit-0 is recorded via the CLI in the producer report.)"""
    errs = vd._validate_pattern_allowed_paths(vd.TASKS_DIR)
    assert errs == [], f"c18 must flag nothing on the real ledger: {errs}"


def test_grandfather_allowlist_is_complete_for_real_inregime_tasks():
    """Completeness: no in-regime pattern-carrying task in the real ledger is missing from the
    frozen list (so the look-back caught them all), and the list is non-vacuous."""
    pattern_inregime = set()
    for p in sorted(vd.TASKS_DIR.glob("*.json")):
        try:
            t = json.loads(p.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError):
            continue
        tid = t.get("task_id") or p.stem
        in_regime = bool(t.get("directive_regime_version")) or bool(t.get("directive_refs"))
        if in_regime and dr.pattern_allowed_paths(t.get("allowed_paths") or []):
            pattern_inregime.add(tid)
    missing = pattern_inregime - dr.PATTERN_ALLOWED_PATHS_GRANDFATHERED
    assert not missing, f"in-regime pattern tasks missing from the frozen allowlist: {missing}"
    assert pattern_inregime, "expected a non-empty set of in-regime pattern tasks to exist"


if __name__ == "__main__":
    import tempfile
    test_pattern_detector_one_per_state()
    test_pattern_detector_question_mark_and_pathspec_magic()
    test_pattern_detector_non_string_fails_closed()
    test_grandfather_allowlist_shape()
    test_cli_refusal_helper_arms()
    with tempfile.TemporaryDirectory() as d:
        test_validator_static_catch_c18(Path(d))
    test_migration_proof_zero_new_flags_on_real_ledger()
    test_grandfather_allowlist_is_complete_for_real_inregime_tasks()
    print("OK: literal-allowed-paths seal focused tests")

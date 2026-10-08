#!/usr/bin/env python3
"""Focused tests for the literal-allowed-paths seal (backlog DB-181; owner D-090-R557;
M0-T188, round 2). The seal refuses an allowed_paths entry that binds NO tracked file under
GIT_LITERAL_PATHSPECS=1 at contract time, claim, submit AND accept, because such an entry makes
the reviewed content identity cover less than the packet declares. Option B: entries are
REFUSED, never EXPANDED -- the identity algorithm is byte-unchanged.

Round-2 corrections covered here:
  * the COMPLETE rule (note 2): one test per input state, incl. braces, bracket-range, backslash,
    '..', absolute, control char, Unicode star look-alike, and prose-annotated entries; the one
    real tracked bracket route stays accepted;
  * the frozen grandfather map freezes ENTRIES, not ids (note 3): a listed task with only its
    frozen entries passes; the same task with a NEW pattern entry is refused naming only the new
    one;
  * a non-list allowed_paths is refused by the check itself (note 4);
  * the c18 static catch and the migration proof that the new check adds ZERO errors on the real
    ledger (the frozen map covers every pre-existing in-regime offending entry).

Stdlib + pytest. Lifecycle (claim/submit/accept) refusal is proven in
tools/test_project_control.py::test_s13_* and ::test_s14_*.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import directive_registry as dr          # noqa: E402  (shared detector + frozen map)
import project_control as pc             # noqa: E402  (CLI refusal helper)
import validate_directive_compliance as vd  # noqa: E402  (static catch c18)

_HEAD, _HERR = dr.resolve_commit(ROOT, None)
assert _HERR is None, f"cannot resolve HEAD for the seal tests: {_HERR}"

BRACKET_ROUTE = "apps/web/src/app/survey/review/[documentId]/page.tsx"


def _det(allowed):
    return dr.pattern_allowed_paths(allowed, root=ROOT, commit=_HEAD)


# One row per input state (the producer-report table). (state_id, allowed_paths, expected).
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
    ("S9_bracket_route_tracked", [BRACKET_ROUTE], []),
    ("question_mark", ["docs/file?.md"], ["docs/file?.md"]),
    ("leading_colon", [":(glob)services/api"], [":(glob)services/api"]),
    ("absolute", ["/etc/passwd"], ["/etc/passwd"]),
    ("dotdot", ["a/../b.py"], ["a/../b.py"]),
    ("backslash", ["a\\b.py"], ["a\\b.py"]),
    ("brace_set", ["a/{b,c}.py"], ["a/{b,c}.py"]),
    ("bracket_range_untracked", ["a/[abc].py"], ["a/[abc].py"]),
    ("control_char_newline", ["a\nb.py"], ["a\nb.py"]),
    ("unicode_star_lookalike", ["a/＊.py"], ["a/＊.py"]),
    ("prose_annotated", ["x/y.yml (ADDITIVE 'z' only; keep green)"],
     ["x/y.yml (ADDITIVE 'z' only; keep green)"]),
]


def test_pattern_detector_one_per_state():
    for sid, allowed, expected in DETECTOR_STATES:
        assert _det(allowed) == expected, f"{sid}: {allowed!r}"


def test_bracket_route_needs_git_context_to_be_accepted():
    # Without git context an unusual-char entry cannot be proven tracked -> refused (fail closed).
    assert dr.pattern_allowed_paths([BRACKET_ROUTE]) == [BRACKET_ROUTE]
    # With git context the real tracked route is accepted; a non-existent bracket path is not.
    assert dr.pattern_allowed_paths([BRACKET_ROUTE], root=ROOT, commit=_HEAD) == []
    assert dr.pattern_allowed_paths(["apps/web/src/app/x/[nope]/p.tsx"],
                                    root=ROOT, commit=_HEAD) == ["apps/web/src/app/x/[nope]/p.tsx"]


def test_non_list_and_non_string_fail_closed():
    # note 4: a non-list allowed_paths is refused by the detector itself.
    assert _det("services/api/**") == ["services/api/**"]
    assert _det({"a": 1}) == [{"a": 1}]
    # None reads as no scope (benign; the empty-identity guard owns the zero-scope case).
    assert _det(None) == []
    # a non-string entry inside a list is refused.
    assert _det([123, None]) == [123, None]


def test_grandfather_map_shape():
    m = dr.PATTERN_ALLOWED_PATHS_GRANDFATHERED
    assert isinstance(m, dict)
    assert all(isinstance(v, frozenset) for v in m.values())
    assert len(m) == 91, f"expected 91 tasks (88 round-1 + M0-T030/M0-T031/M6-T001), got {len(m)}"
    assert sum(len(v) for v in m.values()) == 249, "expected 249 frozen (task, entry) pairs"
    assert dr.PATTERN_ALLOWED_PATHS_GRANDFATHERED["M5-T126"] == frozenset(
        {"docs/measurement-basis/**", "services/api/tests/scenario/measurement_basis/**"})
    assert "M0-T188" not in m, "M0-T188 binds literally; it must not be grandfathered"


def test_frozen_map_exempts_entries_not_ids():
    # note 3: a listed task with ONLY its frozen entries passes; a NEW pattern entry is refused.
    in_regime = {"directive_refs": [{"directive_id": "D-x", "requirement_ids": "ALL"}]}
    frozen = sorted(dr.PATTERN_ALLOWED_PATHS_GRANDFATHERED["M5-T126"])
    assert pc._pattern_allowed_paths_check({**in_regime, "allowed_paths": frozen}, "M5-T126") is None
    err = pc._pattern_allowed_paths_check(
        {**in_regime, "allowed_paths": frozen + ["services/api/new_glob_*.py"]}, "M5-T126")
    assert err and "services/api/new_glob_*.py" in err
    assert "docs/measurement-basis/**" not in err  # the frozen entries are NOT re-named


def test_cli_refusal_helper_arms():
    in_regime = {"directive_refs": [{"directive_id": "D-x", "requirement_ids": "ALL"}]}
    err = pc._pattern_allowed_paths_check(
        {**in_regime, "allowed_paths": ["services/api/**", "project-control/reports/x.md"]},
        "M9-T999-new")
    assert err and "services/api/**" in err and "literal" in err.lower()
    assert "project-control/reports/x.md" not in err  # a literal entry is never named
    # non-list allowed_paths refused (note 4).
    err2 = pc._pattern_allowed_paths_check({**in_regime, "allowed_paths": "services/api/**"}, "M9-X")
    assert err2 and "must be a list" in err2
    # literal-only accepted; a bracket route that is tracked is accepted.
    assert pc._pattern_allowed_paths_check(
        {**in_regime, "allowed_paths": ["tools/project_control.py", BRACKET_ROUTE]}, "M9-L") is None
    # not-in-regime tasks are not checked here.
    assert pc._pattern_allowed_paths_check({"allowed_paths": ["services/api/**"]}, "M9-legacy") is None


def _write_task(td: Path, tid: str, allowed, in_regime=True):
    obj = {"task_id": tid, "allowed_paths": allowed}
    if in_regime:
        obj["directive_regime_version"] = "1.0"
    (td / f"{tid}.json").write_text(json.dumps(obj), encoding="utf-8")


def test_validator_static_catch_c18(tmp_path):
    td = tmp_path / "tasks"
    td.mkdir()
    _write_task(td, "M9-NEW", ["services/api/**"])                 # flagged (glob)
    _write_task(td, "M9-BRACE", ["a/{b,c}.py"])                    # flagged (complete rule)
    _write_task(td, "M9-LIT", ["tools/project_control.py"])        # literal -> not flagged
    _write_task(td, "M9-NONLIST", "services/api/**")               # non-list -> flagged (note 4)
    _write_task(td, "M9-LEGACY", ["services/api/**"], in_regime=False)  # not in regime -> skip
    # a LISTED id carrying its frozen entry PLUS a NEW glob: only the new one is flagged
    # (entry-level freeze, note 3).
    _write_task(td, "M5-T126", ["docs/measurement-basis/**", "services/api/extra_*.py"])
    errs = vd._validate_pattern_allowed_paths(td)
    joined = "\n".join(errs)
    assert any("M9-NEW" in e and "services/api/**" in e for e in errs), joined
    assert any("M9-BRACE" in e for e in errs), joined
    assert any("M9-NONLIST" in e for e in errs), joined
    assert "M9-LIT" not in joined
    assert "M9-LEGACY" not in joined
    m5 = [e for e in errs if "M5-T126" in e]
    assert len(m5) == 1 and "services/api/extra_*.py" in m5[0], m5
    assert "docs/measurement-basis/**" not in m5[0], "a frozen entry must NOT be re-flagged"


def test_migration_proof_zero_new_flags_on_real_ledger():
    """The frozen map covers every pre-existing in-regime offending entry, so c18 adds ZERO
    errors at HEAD -- validate --check stays exit 0. (The authoritative before/after exit-0 is
    recorded via the CLI in the producer report.)"""
    errs = vd._validate_pattern_allowed_paths(vd.TASKS_DIR)
    assert errs == [], f"c18 must flag nothing on the real ledger: {errs}"


def test_frozen_map_is_complete_for_real_inregime_tasks():
    """Completeness: for every in-regime task in the real ledger, every entry the complete rule
    flags at HEAD is present in that task's frozen set (so the look-back caught them all)."""
    seen_any = False
    for p in sorted(vd.TASKS_DIR.glob("*.json")):
        try:
            t = json.loads(p.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError):
            continue
        tid = t.get("task_id") or p.stem
        in_regime = bool(t.get("directive_regime_version")) or bool(t.get("directive_refs"))
        if not in_regime:
            continue
        offenders = dr.pattern_allowed_paths(t.get("allowed_paths"), root=ROOT, commit=_HEAD)
        if not offenders:
            continue
        seen_any = True
        frozen = dr.PATTERN_ALLOWED_PATHS_GRANDFATHERED.get(tid, frozenset())
        missing = [o for o in offenders if o not in frozen]
        assert not missing, f"{tid}: offending entries missing from the frozen map: {missing}"
    assert seen_any, "expected at least one in-regime offending task to exist"


if __name__ == "__main__":
    import tempfile
    test_pattern_detector_one_per_state()
    test_bracket_route_needs_git_context_to_be_accepted()
    test_non_list_and_non_string_fail_closed()
    test_grandfather_map_shape()
    test_frozen_map_exempts_entries_not_ids()
    test_cli_refusal_helper_arms()
    with tempfile.TemporaryDirectory() as d:
        test_validator_static_catch_c18(Path(d))
    test_migration_proof_zero_new_flags_on_real_ledger()
    test_frozen_map_is_complete_for_real_inregime_tasks()
    print("OK: literal-allowed-paths seal focused tests (round 2)")

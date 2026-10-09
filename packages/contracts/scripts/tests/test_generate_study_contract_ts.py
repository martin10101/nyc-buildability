"""Study contract set .ts generation (task C-03, plan M1-09).

Companion to the other generator tests: proves the six generated files
(site_fact, study, results, report_model, export_record, benchmark_lot) are
byte-stable, match the committed files, cover every schema key, are
structurally well-formed standalone TypeScript (no Node toolchain: a stdlib
check), and that wiring them in did NOT change the five older artifacts.

Run: python -m pytest packages/contracts/scripts/tests
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
CONTRACTS_ROOT = SCRIPTS_DIR.parent
SCHEMA_DIR = CONTRACTS_ROOT / "schemas" / "v1"
GENERATED_DIR = CONTRACTS_ROOT / "generated"
OLDER_ARTIFACTS = (
    "property_profile", "rule_evaluation", "scenario", "survey_evidence", "lot_geometry",
)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN = _load("generate_ts_types")
STUDY = _load("study_contract_types")
STEMS = [contract.stem for contract in STUDY.STUDY_CONTRACTS]


def test_registry_lists_exactly_the_study_contracts() -> None:
    assert STEMS == [
        "site_fact", "study", "results", "report_model", "export_record", "benchmark_lot",
        "hidden_issue_flags", "transit_parking", "parity_data",
    ]
    for stem in STEMS:
        assert (SCHEMA_DIR / f"{stem}.schema.json").is_file()


@pytest.mark.parametrize("stem", STEMS)
def test_committed_file_is_byte_identical_to_fresh_generation(stem: str) -> None:
    committed = (GENERATED_DIR / f"{stem}.ts").read_text(encoding="utf-8")
    assert committed == GEN.generate_study_contract(stem), (
        f"packages/contracts/generated/{stem}.ts is out of date; run "
        "python packages/contracts/scripts/generate_ts_types.py and commit it."
    )


@pytest.mark.parametrize("stem", STEMS)
def test_generation_is_deterministic_lf_and_single_trailing_newline(stem: str) -> None:
    text = GEN.generate_study_contract(stem)
    assert text == GEN.generate_study_contract(stem)
    assert "\r\n" not in text
    assert text.endswith("\n") and not text.endswith("\n\n")


def test_older_artifacts_are_unchanged_by_the_study_wiring() -> None:
    """Byte-identity: the five older .ts files still equal a fresh generation
    (the shared-emitter change for unions of object literals and the new
    wiring are inert for them)."""
    fresh = {
        "property_profile": GEN.generate(),
        "rule_evaluation": GEN.generate_rule_evaluation(),
        "scenario": GEN.generate_scenario(),
        "survey_evidence": GEN.generate_survey_evidence(),
        "lot_geometry": GEN.generate_lot_geometry(),
    }
    for stem in OLDER_ARTIFACTS:
        assert (GENERATED_DIR / f"{stem}.ts").read_text(encoding="utf-8") == fresh[stem]


def test_check_mode_covers_the_study_contracts(capsys) -> None:
    assert GEN.check_study_contracts() == 0
    out = capsys.readouterr().out
    for stem in STEMS:
        assert f"OK: generated {stem} TypeScript types are up to date." in out


def test_check_mode_turns_red_on_a_stale_study_file(tmp_path, monkeypatch, capsys) -> None:
    for stem in STEMS:
        (tmp_path / f"{stem}.ts").write_text(
            (GENERATED_DIR / f"{stem}.ts").read_text(encoding="utf-8"), encoding="utf-8"
        )
    stale = tmp_path / "results.ts"
    stale.write_text(stale.read_text(encoding="utf-8") + "// hand edit\n", encoding="utf-8")
    monkeypatch.setattr(STUDY, "GENERATED_DIR", tmp_path)
    assert STUDY.check_all(GEN._study_emitter()) == 1
    err = capsys.readouterr().err
    assert "generated results TypeScript types are out of date" in err


def test_check_and_write_skip_when_the_study_schemas_are_absent(tmp_path, monkeypatch) -> None:
    """The property_profile drift harness points SCHEMA_DIR at a tmp copy of
    only the four profile schemas; the study artifacts must then be skipped
    (rc 0, nothing written), exactly like the other secondary artifacts."""
    monkeypatch.setattr(GEN, "SCHEMA_DIR", tmp_path)
    monkeypatch.setattr(STUDY, "GENERATED_DIR", tmp_path / "out")
    assert STUDY.check_all(GEN._study_emitter()) == 0
    assert STUDY.write_all(GEN._study_emitter()) == 0
    assert not (tmp_path / "out").exists()


# ---------------------------------------------------------------------------
# Coverage: every schema property key appears as a TS member
# ---------------------------------------------------------------------------


def _reachable_keys(stem: str) -> set[str]:
    schemas = {
        name: json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        for name in STUDY.load_closure(SCHEMA_DIR, f"{stem}.schema.json")
    }
    keys: set[str] = set()
    seen: set[tuple[str, str]] = set()

    def walk(node, filename: str) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item, filename)
            return
        if not isinstance(node, dict):
            return
        if "$ref" in node:
            target_file, pointer = STUDY._split_ref(node["$ref"], filename)
            if (target_file, pointer) not in seen:
                seen.add((target_file, pointer))
                target = STUDY._node_at(schemas[target_file], pointer)
                if pointer == "":
                    target = {k: v for k, v in target.items() if k != "$defs"}
                walk(target, target_file)
        keys.update(node.get("properties", {}))
        for key, value in node.items():
            if key not in ("$defs", "$ref"):
                walk(value, filename)

    root = schemas[f"{stem}.schema.json"]
    walk(root, f"{stem}.schema.json")  # includes the root file's own $defs
    return keys


@pytest.mark.parametrize("stem", STEMS)
def test_generated_types_cover_every_reachable_schema_key(stem: str) -> None:
    ts = (GENERATED_DIR / f"{stem}.ts").read_text(encoding="utf-8")
    declared = set(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\??:", ts, flags=re.MULTILINE))
    declared |= set(re.findall(r'^\s*"([^"]+)"\??:', ts, flags=re.MULTILINE))
    missing = _reachable_keys(stem) - declared
    assert not missing, f"{stem}.ts is missing schema keys: {sorted(missing)}"


# ---------------------------------------------------------------------------
# Well-formedness (stdlib stand-in for tsc: the web build never compiles these)
# ---------------------------------------------------------------------------

_TS_BUILTINS = {"true", "false", "null", "number", "string", "boolean", "unknown"}


def _strip_strings(text: str) -> str:
    return re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)


def _declarations(ts: str) -> list[tuple[str, str, str]]:
    """[(kind, name, body)] for each top-level export, comments dropped."""
    code = "\n".join(line for line in ts.splitlines() if not line.startswith("//"))
    parts = re.split(r"^export (interface|type) ([A-Za-z_]\w*)", code, flags=re.MULTILINE)
    assert parts[0].strip() == "", "code before the first export"
    return [(parts[i], parts[i + 1], parts[i + 2].strip()) for i in range(1, len(parts), 3)]


@pytest.mark.parametrize("stem", STEMS)
def test_generated_file_is_well_formed_standalone_typescript(stem: str) -> None:
    ts = (GENERATED_DIR / f"{stem}.ts").read_text(encoding="utf-8")
    decls = _declarations(ts)
    names = [name for _, name, _ in decls]
    assert len(names) == len(set(names)), f"duplicate declarations in {stem}.ts"
    for kind, name, body in decls:
        bare = _strip_strings(body)
        for open_, close in ("{}", "()", "[]"):
            assert bare.count(open_) == bare.count(close), f"{stem}.ts {name}: unbalanced {open_}"
        if kind == "interface":
            assert GEN.is_object_literal(body), f"{stem}.ts interface {name} is not one object"
        else:
            assert body.startswith("= ") and body.endswith(";"), f"{stem}.ts type {name}"
        # Every type name used is declared in this same file (standalone file).
        used = set(re.findall(r"\b([A-Z][A-Za-z0-9]*)\b", bare)) - _TS_BUILTINS
        undeclared = used - set(names)
        assert not undeclared, f"{stem}.ts {name} uses undeclared {sorted(undeclared)}"
    code = "\n".join(line for line in ts.splitlines() if not line.startswith("//"))
    assert not re.search(r"\bunknown\b", _strip_strings(code)), f"{stem}.ts emits unknown"
    assert names[-1] == next(c.interface for c in STUDY.STUDY_CONTRACTS if c.stem == stem)


def test_generated_types_pin_key_vocabularies() -> None:
    site_fact = (GENERATED_DIR / "site_fact.ts").read_text(encoding="utf-8")
    assert (
        "export type Measurement = MeasurementSurveyEntered | MeasurementCityRecords | "
        "MeasurementApproximateTaxMap | MeasurementEntered | MeasurementAssumed | "
        "MeasurementUnknown;" in site_fact
    )
    assert 'rank: "unknown";\n  label: "Unknown \\u2014 enter";' in site_fact
    assert "  value: number | string | null;\n" in site_fact
    assert "  measurement: Measurement;\n  source: Source | null;\n" in site_fact

    study = (GENERATED_DIR / "study.ts").read_text(encoding="utf-8")
    assert "  addon_selection: AddonSwitch[];\n" in study
    assert "    facts: SiteFact[];\n" in study

    results = (GENERATED_DIR / "results.ts").read_text(encoding="utf-8")
    assert "  measurement: MeasurementKnown;\n" in results
    assert "entries: (YardRequired | YardNotRequired)[];" in results
    assert "  geometry: GeometryAvailable | NotAvailable;\n" in results

    # A union of inline objects is a type alias, never an (invalid) interface.
    report = (GENERATED_DIR / "report_model.ts").read_text(encoding="utf-8")
    assert "export type DisplayValue = {" in report
    assert "export type DrawingSheet = {" in report
    assert "export interface DisplayValue" not in report

    export = (GENERATED_DIR / "export_record.ts").read_text(encoding="utf-8")
    assert "    study: Study;\n" in export
    assert "  read_only: true;\n" in export


# ---------------------------------------------------------------------------
# Unit tests for the normalization, naming and object-literal helpers
# ---------------------------------------------------------------------------


def test_normalize_maps_const_and_oneof_without_touching_the_input() -> None:
    node = {"oneOf": [{"type": "string", "const": "a"}, {"type": "null"}]}
    expected = {"anyOf": [{"type": "string", "enum": ["a"]}, {"type": "null"}]}
    assert STUDY.normalize(node) == expected
    assert node == {"oneOf": [{"type": "string", "const": "a"}, {"type": "null"}]}
    both = {"anyOf": [{"type": "null"}], "oneOf": [{"type": "string"}]}
    assert STUDY.normalize(both) == both  # an existing anyOf is never overwritten
    # A property NAMED "const"/"oneOf" and DATA values are never rewritten.
    named = {"properties": {"const": {"type": "string"}, "oneOf": {"type": "number"}}}
    assert STUDY.normalize(named) == named
    data = {"const": {"oneOf": 1}, "default": {"const": 2}}
    assert STUDY.normalize(data) == {"enum": [{"oneOf": 1}], "default": {"const": 2}}


def test_derived_names_fail_loudly_on_collision_or_builtin() -> None:
    root = {
        "properties": {
            "a": {"$ref": "#/$defs/x_y"},
            "b": {"$ref": "other.schema.json#/$defs/x_y"},
        },
        "$defs": {"x_y": {"type": "string"}},
    }
    other = {"$defs": {"x_y": {"type": "number"}}}
    with pytest.raises(ValueError, match="used by both"):
        STUDY.derive_named_defs(
            {"root.schema.json": root, "other.schema.json": other}, "root.schema.json", "Root"
        )
    builtin = {
        "properties": {"a": {"$ref": "#/$defs/date"}},
        "$defs": {"date": {"type": "string"}},
    }
    with pytest.raises(ValueError, match="shadows a built-in"):
        STUDY.derive_named_defs({"root.schema.json": builtin}, "root.schema.json", "Root")


def test_is_object_literal_distinguishes_one_object_from_a_union() -> None:
    assert GEN.is_object_literal("{\n  a: string;\n}")
    assert GEN.is_object_literal('{\n  a: "} | {";\n}')  # braces inside a string
    assert not GEN.is_object_literal("{\n  a: string;\n} | {\n  b: number;\n}")
    assert not GEN.is_object_literal("A | {\n  b: number;\n}")
    assert not GEN.is_object_literal("{\n  a: string;\n} & B")

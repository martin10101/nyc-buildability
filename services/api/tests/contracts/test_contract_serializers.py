"""Unit + regression tests for the allowlist serializers (task M2-T017).

Covers M2-T017 AS-3 (the serializer rejects unknown keys and round-trips only
documented fields; diagnostic-leak safety).

The final section is the IMPORT TRIPWIRE. Task M2-T017 froze the serializer
un-wired, so the tripwire asserted that NO production module imported it. Task
M2-T018 wired it into the profile builder's fail-closed provenance write
boundary, so the tripwire now asserts the stricter, still-load-bearing
invariant (M2-T018 AS-3): the serializer is imported at EXACTLY that one
boundary and nowhere else in ``app/**`` outside ``app/contracts/``. A second
production module reaching for it - a route serializing its own provenance, a
worker bypassing the builder - is still a regression, and so is losing the
wiring at the builder.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from app.contracts.serializers import (
    ANALYSIS_STATE_TRANSITION_SERIALIZER,
    SOURCE_FACT_SERIALIZER,
    AllowlistSerializer,
    MissingFieldError,
    UnknownFieldError,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
APP_DIR = REPO_ROOT / "services" / "api" / "app"

SERIALIZERS = {
    "source_fact": SOURCE_FACT_SERIALIZER,
    "analysis_state_transition": ANALYSIS_STATE_TRANSITION_SERIALIZER,
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Drift guard: the frozen allowlists MUST equal the canonical schema exactly.
# This is what lets the module declare the allowlists as constants (import-safe,
# no file I/O) without ever silently drifting from the closed contract.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name, serializer", SERIALIZERS.items())
def test_allowlist_matches_canonical_schema(name: str, serializer: AllowlistSerializer) -> None:
    schema = _load(SCHEMA_DIR / f"{name}.schema.json")
    assert tuple(serializer.allowed_fields) == tuple(schema["properties"]), (
        "allowed_fields must equal the schema properties in canonical order"
    )
    assert tuple(serializer.required_fields) == tuple(schema["required"]), (
        "required_fields must equal the schema required list in canonical order"
    )
    # And the contract it serializes is actually closed.
    assert schema.get("additionalProperties") is False


# ---------------------------------------------------------------------------
# serialize(): round-trip documented fields, reject unknown, require required.
# ---------------------------------------------------------------------------


def test_serialize_roundtrips_documented_fields() -> None:
    fixture = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    out = SOURCE_FACT_SERIALIZER.serialize(fixture)
    assert out == fixture  # a clean documented record round-trips unchanged
    assert out is not fixture  # a new dict


def test_serialize_output_key_order_is_canonical() -> None:
    fixture = _load(FIXTURE_ROOT / "valid" / "source_fact" / "ztldb_lineage_fact.json")
    # Feed keys in a shuffled order; output must follow canonical schema order.
    shuffled = dict(reversed(list(fixture.items())))
    out = SOURCE_FACT_SERIALIZER.serialize(shuffled)
    expected_order = [f for f in SOURCE_FACT_SERIALIZER.allowed_fields if f in fixture]
    assert list(out) == expected_order


def test_serialize_rejects_unknown_typo_key() -> None:
    fixture = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    bad = {k: v for k, v in fixture.items() if k != "units"}
    bad["unit"] = "square_feet"  # typo of the optional 'units'
    with pytest.raises(UnknownFieldError) as exc:
        SOURCE_FACT_SERIALIZER.serialize(bad)
    assert exc.value.unknown_keys == ["unit"]


def test_serialize_requires_required_fields() -> None:
    fixture = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    incomplete = {k: v for k, v in fixture.items() if k != "conflict_status"}
    with pytest.raises(MissingFieldError) as exc:
        SOURCE_FACT_SERIALIZER.serialize(incomplete)
    assert exc.value.missing_keys == ["conflict_status"]


def test_serialize_does_not_mutate_input() -> None:
    fixture = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    snapshot = json.loads(json.dumps(fixture))
    SOURCE_FACT_SERIALIZER.serialize(fixture)
    assert fixture == snapshot


def test_serialize_rejects_non_mapping() -> None:
    with pytest.raises(TypeError):
        SOURCE_FACT_SERIALIZER.serialize([("provenance_id", "p")])  # type: ignore[arg-type]


def test_is_serializable_boolean() -> None:
    fixture = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    assert SOURCE_FACT_SERIALIZER.is_serializable(fixture) is True
    assert SOURCE_FACT_SERIALIZER.is_serializable({**fixture, "leaked": 1}) is False


def test_analysis_state_transition_serialize_and_reject() -> None:
    fixture = _load(
        FIXTURE_ROOT / "valid" / "analysis_state_transition" / "address_resolution.json"
    )
    assert ANALYSIS_STATE_TRANSITION_SERIALIZER.serialize(fixture) == fixture
    with pytest.raises(UnknownFieldError) as exc:
        ANALYSIS_STATE_TRANSITION_SERIALIZER.serialize({**fixture, "resason": "typo"})
    assert exc.value.unknown_keys == ["resason"]


# ---------------------------------------------------------------------------
# Diagnostic-leak safety: a rejected record's VALUE never travels out through
# the exception (only the key NAME does).
# ---------------------------------------------------------------------------


def test_unknown_field_error_never_echoes_the_value() -> None:
    secret = "Traceback: token=SUPER_SECRET_abc123 at line 42"
    fixture = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    with pytest.raises(UnknownFieldError) as exc:
        SOURCE_FACT_SERIALIZER.serialize({**fixture, "_debug_stacktrace": secret})
    message = str(exc.value)
    assert "_debug_stacktrace" in message  # the key name is named
    assert "SUPER_SECRET" not in message  # the value is NOT leaked
    assert secret not in message


def test_multiple_unknown_keys_reported_sorted_names_only() -> None:
    fixture = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    with pytest.raises(UnknownFieldError) as exc:
        SOURCE_FACT_SERIALIZER.serialize({**fixture, "zeta": "v1", "alpha": "v2"})
    assert exc.value.unknown_keys == ["alpha", "zeta"]  # sorted, names only
    assert "v1" not in str(exc.value) and "v2" not in str(exc.value)


# ---------------------------------------------------------------------------
# IMPORT TRIPWIRE (M2-T018 AS-3): the serializer is imported at EXACTLY the
# intended profile write boundary and nowhere else in app/** outside
# app/contracts/. Amended from the M2-T017 "not imported anywhere" form, whose
# premise (the serializer is un-wired) M2-T018 deliberately retired.
# ---------------------------------------------------------------------------

# THE one production module allowed to import the serializer: the profile
# builder, whose ``_closed_provenance`` is the fail-closed provenance write
# boundary. Repo-relative POSIX path so the assertion message is identical on
# Windows and on the Linux CI runner.
BOUNDARY_MODULE = "services/api/app/profile/builder.py"


def _production_modules() -> list[Path]:
    """Every module under ``app/`` EXCEPT the contracts package that defines
    the serializer (it is allowed to reference itself)."""
    return [
        py
        for py in sorted(APP_DIR.rglob("*.py"))
        if not (py.parent.name == "contracts" and py.parent.parent.name == "app")
    ]


def _repo_path(py: Path) -> str:
    return py.relative_to(REPO_ROOT).as_posix()


def _imports_app_contracts(tree: ast.AST) -> bool:
    """True when the module really IMPORTS from ``app.contracts`` (AST, so a
    mention inside a docstring or comment is not mistaken for wiring)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").startswith("app.contracts"):
                return True
        elif isinstance(node, ast.Import):
            if any(alias.name.startswith("app.contracts") for alias in node.names):
                return True
    return False


def test_serializer_imported_exactly_at_the_profile_write_boundary() -> None:
    """Exactly one production module imports the serializer, and it is the
    profile builder. Fewer means the fail-closed boundary was lost; more means
    a second component is serializing provenance outside the single boundary
    (both are M2-T018 regressions)."""
    importers = [
        _repo_path(py)
        for py in _production_modules()
        if _imports_app_contracts(ast.parse(py.read_text(encoding="utf-8")))
    ]
    assert importers == [BOUNDARY_MODULE], (
        "the allowlist serializer must be imported at exactly the profile "
        f"write boundary ({BOUNDARY_MODULE}); found: {importers}"
    )


def test_no_other_production_module_even_references_the_serializer() -> None:
    """Textual companion to the AST check: catches a dynamic
    ``importlib.import_module('app.contracts.serializers')`` or any other
    string-based reach for the serializer from outside the boundary."""
    referencing = [
        _repo_path(py)
        for py in _production_modules()
        if "app.contracts" in (text := py.read_text(encoding="utf-8"))
        or "contracts.serializers" in text
    ]
    assert referencing == [BOUNDARY_MODULE], (
        "only the profile write boundary may reference the serializer; "
        f"found: {referencing}"
    )


def test_boundary_imports_only_the_source_fact_serializer() -> None:
    """The builder takes the narrowest possible dependency: the one serializer
    it needs, not the package or the error classes it never raises itself."""
    tree = ast.parse((REPO_ROOT / BOUNDARY_MODULE).read_text(encoding="utf-8"))
    imported = sorted(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith("app.contracts")
        for alias in node.names
    )
    assert imported == ["SOURCE_FACT_SERIALIZER"]


def test_serializer_is_used_only_inside_the_closed_provenance_boundary() -> None:
    """Within the builder, the serializer is referenced ONLY inside
    ``_closed_provenance``. A second call site elsewhere in the builder would
    mean provenance can enter the array through a path this test does not
    pin."""
    tree = ast.parse((REPO_ROOT / BOUNDARY_MODULE).read_text(encoding="utf-8"))
    boundary = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_closed_provenance"
    )
    inside = {id(node) for node in ast.walk(boundary)}
    stray = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "SOURCE_FACT_SERIALIZER"
        and id(node) not in inside
    ]
    assert stray == [], (
        "SOURCE_FACT_SERIALIZER is used outside _closed_provenance at "
        f"line(s) {stray}; the write boundary must stay single"
    )

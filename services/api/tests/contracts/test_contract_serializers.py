"""Unit + regression tests for the frozen allowlist serializers (task M2-T017).

Covers AS-3 (the serializer rejects unknown keys and round-trips only documented
fields; diagnostic-leak safety) and AS-4 (the serializer is a FROZEN interface -
not imported by any production route/builder in this task).
"""

from __future__ import annotations

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
# AS-4: FROZEN interface - not wired into any production route/builder here.
# ---------------------------------------------------------------------------


def test_serializer_not_imported_by_any_production_module() -> None:
    """No module under services/api/app (other than the contracts package that
    DEFINES it) may import the serializer in this task; wiring is deferred to a
    later controller-contracted integration task (FIRST-WAVE-INTEGRATION-
    CONTRACT.md lane 3 downstream integration). This test is the regression that
    keeps the interface frozen until then."""
    offenders: list[str] = []
    for py in APP_DIR.rglob("*.py"):
        # The contracts package is allowed to reference itself.
        if py.parent.name == "contracts" and py.parent.parent.name == "app":
            continue
        text = py.read_text(encoding="utf-8")
        if "contracts.serializers" in text or "from app.contracts" in text:
            offenders.append(str(py.relative_to(REPO_ROOT)))
    assert not offenders, (
        "the allowlist serializer must NOT be wired into production in M2-T017; "
        f"found import(s) in: {offenders}"
    )

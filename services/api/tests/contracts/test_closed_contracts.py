"""Contract-hardening acceptance pack for the CLOSED provenance/audit contracts.

Task M2-T017 (DF-4/DF-5, whole-system trust replan Area G). Offline and
deterministic. Proves both contracts are now closed with
``additionalProperties:false`` and that the close is load-bearing:

- every valid fixture still validates (positives, incl. the four documented
  connector-lineage keys the accepted connectors already emit);
- every invalid fixture is rejected for an undocumented/typo/diagnostic-leak
  key (negatives);
- ``additionalProperties:false`` is present and CAUSAL - a record that the
  closed contract rejects is accepted by an otherwise-identical OPEN variant
  (so the rejection is due to the close, not an incidental violation);
- the ``source_fact`` runtime-bundled copy stays byte-identical to canonical.

Uses jsonschema with a referencing registry so the cross-file ``$ref`` set
(common / analysis_state) resolves - the same way the API loads the contracts.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

# services/api/tests/contracts/test_*.py -> parents[4] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
BUNDLE_DIR = REPO_ROOT / "services" / "api" / "app" / "_contract_schemas" / "v1"

SOURCE_FACT_SCHEMA = SCHEMA_DIR / "source_fact.schema.json"
AST_SCHEMA = SCHEMA_DIR / "analysis_state_transition.schema.json"

# The four connector-lineage keys M2-T017 documented so the record could be
# closed without rejecting real accepted-connector output (DF-4 evidence).
DOCUMENTED_LINEAGE_KEYS = (
    "dataset_id",
    "request_url",
    "input_vintages",
    "source_rows_updated_at",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _registry() -> Registry:
    resources = []
    for schema_file in sorted(SCHEMA_DIR.glob("*.schema.json")):
        doc = _load(schema_file)
        resources.append(
            (doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012))
        )
    return Registry().with_resources(resources)


def _validator(schema: dict) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(schema, registry=_registry())


def _fixtures(expectation: str, stem: str) -> list[Path]:
    return sorted((FIXTURE_ROOT / expectation / stem).glob("*.json"))


# ---------------------------------------------------------------------------
# Both contracts are closed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("schema_path", [SOURCE_FACT_SCHEMA, AST_SCHEMA], ids=lambda p: p.name)
def test_contract_is_closed(schema_path: Path) -> None:
    """DF-4/DF-5: the record no longer silently accepts undocumented keys."""
    schema = _load(schema_path)
    assert schema.get("additionalProperties") is False, (
        f"{schema_path.name} must be closed with additionalProperties:false"
    )


def test_source_fact_documents_all_connector_lineage_keys() -> None:
    """Regression: the keys accepted connectors emit must stay DOCUMENTED, or
    closing the record would reject real production output (or silently drop a
    documented key)."""
    props = _load(SOURCE_FACT_SCHEMA)["properties"]
    for key in DOCUMENTED_LINEAGE_KEYS:
        assert key in props, f"{key} must be a documented optional source_fact property"


# ---------------------------------------------------------------------------
# Positive fixtures validate
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture", _fixtures("valid", "source_fact"), ids=lambda p: p.name)
def test_valid_source_fact_fixture_validates(fixture: Path) -> None:
    _validator(_load(SOURCE_FACT_SCHEMA)).validate(_load(fixture))


@pytest.mark.parametrize(
    "fixture", _fixtures("valid", "analysis_state_transition"), ids=lambda p: p.name
)
def test_valid_ast_fixture_validates(fixture: Path) -> None:
    _validator(_load(AST_SCHEMA)).validate(_load(fixture))


def test_valid_source_fact_fixture_exercises_lineage_keys() -> None:
    """At least one valid fixture proves the documented lineage keys are
    ACCEPTED (the close does not over-reject real connector output)."""
    seen: set[str] = set()
    for fixture in _fixtures("valid", "source_fact"):
        seen |= set(_load(fixture)) & set(DOCUMENTED_LINEAGE_KEYS)
    assert seen == set(DOCUMENTED_LINEAGE_KEYS), (
        f"valid fixtures must collectively exercise every lineage key; missing "
        f"{set(DOCUMENTED_LINEAGE_KEYS) - seen}"
    )


# ---------------------------------------------------------------------------
# Negative fixtures rejected (and each documents its intended defect)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture", _fixtures("invalid", "source_fact"), ids=lambda p: p.name)
def test_invalid_source_fact_fixture_rejected(fixture: Path) -> None:
    instance = _load(fixture)
    assert "_expected_failure" in instance, "invalid fixture must document its defect"
    assert list(_validator(_load(SOURCE_FACT_SCHEMA)).iter_errors(instance)), (
        f"{fixture.name} unexpectedly validated against the closed source_fact"
    )


@pytest.mark.parametrize(
    "fixture", _fixtures("invalid", "analysis_state_transition"), ids=lambda p: p.name
)
def test_invalid_ast_fixture_rejected(fixture: Path) -> None:
    instance = _load(fixture)
    assert "_expected_failure" in instance, "invalid fixture must document its defect"
    assert list(_validator(_load(AST_SCHEMA)).iter_errors(instance)), (
        f"{fixture.name} unexpectedly validated against the closed transition"
    )


# ---------------------------------------------------------------------------
# The close is CAUSAL: an undocumented/typo key is rejected only because of
# additionalProperties:false (an OPEN variant of the same schema accepts it).
# This is the DF-4/DF-5 proof, independent of the _expected_failure marker.
# ---------------------------------------------------------------------------


def _open_variant(schema: dict) -> dict:
    variant = copy.deepcopy(schema)
    variant.pop("additionalProperties", None)
    variant["$id"] = variant["$id"].replace(".schema.json", ".open-variant.schema.json")
    return variant


def test_source_fact_typo_of_optional_field_only_caught_by_close() -> None:
    base = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    closed = _load(SOURCE_FACT_SCHEMA)
    typo = {k: v for k, v in base.items() if k != "units"}
    typo["unit"] = "square_feet"  # a typo of the OPTIONAL 'units' field
    assert not list(_validator(_open_variant(closed)).iter_errors(typo)), (
        "the OPEN contract silently accepts the typo (the DF-4 defect)"
    )
    errors = list(_validator(closed).iter_errors(typo))
    assert errors, "the CLOSED contract must reject the typo"
    assert any("unit" in e.message for e in errors)


def test_source_fact_diagnostic_field_only_caught_by_close() -> None:
    base = _load(FIXTURE_ROOT / "valid" / "source_fact" / "pluto_full_lineage_fact.json")
    closed = _load(SOURCE_FACT_SCHEMA)
    leaked = dict(base)
    leaked["_debug_internal"] = "Traceback secret token=abc"
    assert not list(_validator(_open_variant(closed)).iter_errors(leaked))
    assert list(_validator(closed).iter_errors(leaked)), "closed contract rejects the leak"


def test_ast_unknown_key_only_caught_by_close() -> None:
    base = _load(FIXTURE_ROOT / "valid" / "analysis_state_transition" / "address_resolution.json")
    closed = _load(AST_SCHEMA)
    unknown = dict(base)
    unknown["actor_ip"] = "203.0.113.7"
    assert not list(_validator(_open_variant(closed)).iter_errors(unknown))
    assert list(_validator(closed).iter_errors(unknown)), "closed contract rejects unknown key"


def test_ast_actor_enum_unchanged_by_close() -> None:
    """Closing the record must not alter its semantics: still exactly
    system/user, deliberately no 'ai' actor (PRD section 32.1)."""
    assert _load(AST_SCHEMA)["properties"]["actor"]["enum"] == ["system", "user"]


# ---------------------------------------------------------------------------
# Runtime bundle byte-identity for source_fact (the sync script guards it too;
# this is the belt-and-suspenders test twin - source_fact IS in the sync
# SCHEMA_FILES tuple, so both this and sync_contract_schemas.py --check cover it)
# ---------------------------------------------------------------------------


def test_source_fact_runtime_bundle_is_byte_identical() -> None:
    canonical = SOURCE_FACT_SCHEMA.read_bytes()
    bundled = (BUNDLE_DIR / "source_fact.schema.json").read_bytes()
    assert bundled == canonical, (
        "services/api/app/_contract_schemas/v1/source_fact.schema.json is out of sync "
        "with the canonical packages/contracts source; run "
        "python services/api/scripts/sync_contract_schemas.py and commit."
    )

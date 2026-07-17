"""Tests for .github/scripts/validate_contracts.py (task M1-T006).

Covers the contract-1.1.0 additions: the extended provenance referential-
integrity invariant (zoning.mapped_features + the three zoning provenance
maps), the intended failure reason of every new invalid fixture, the S6
ground-truth conformance of the accepted M1-T005 builder output, and the
legacy jsonschema RefResolver path (the LIVE path on the CI runner's
jsonschema 4.10.3), including its fail-closed remote-$ref guard.

Run from the repository root:  python -m pytest .github/scripts/tests -q
Stdlib + pytest only; the jsonschema-dependent tests skip cleanly when the
package is not importable (mirroring the validator's own graceful degrade).
"""

from __future__ import annotations

import json
import subprocess
import sys
import warnings
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_contracts as vc  # noqa: E402  (path bootstrap above)

REPO_ROOT = SCRIPTS_DIR.parents[1]
SCHEMA_DIR = REPO_ROOT / "packages" / "contracts" / "schemas" / "v1"
VALID_DIR = REPO_ROOT / "packages" / "contracts" / "fixtures" / "valid" / "property_profile"
INVALID_DIR = REPO_ROOT / "packages" / "contracts" / "fixtures" / "invalid" / "property_profile"


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def contract_registry() -> dict:
    docs = [load(p) for p in sorted(SCHEMA_DIR.glob("*.json"))]
    return {doc["$id"]: doc for doc in docs}


REGISTRY = contract_registry()
PROFILE_SCHEMA = load(SCHEMA_DIR / "property_profile.schema.json")


def schema_errors(instance: dict) -> list[str]:
    return vc.validate_instance(instance, PROFILE_SCHEMA, PROFILE_SCHEMA["$id"], REGISTRY)


def minimal_profile(**overrides) -> dict:
    profile = {
        "profile_version": {
            "contract_version": "1.1.0",
            "profile_revision": 1,
            "generated_at": "2026-07-16T12:00:00Z",
        },
        "identity": {"bbl": "1000477501"},
        "lot_facts": {},
        "existing_building_facts": {},
        "zoning": {},
        "project_intent": {},
        "provenance": [],
        "missing_inputs": [],
        "conflicts": [],
        "user_confirmations": [],
    }
    profile.update(overrides)
    return profile


def provenance_record(provenance_id: str) -> dict:
    return {
        "provenance_id": provenance_id,
        "source_id": "test-fixture-synthetic",
        "original_field_name": "zonedist1",
        "original_value": "R6",
        "normalized_value": "R6",
        "retrieved_at": "2026-07-16T12:00:00Z",
        "dataset_version": "synthetic-fixture-v1",
        "effective_date": None,
        "bbl": "1000477501",
        "confidence": 1,
        "user_confirmed_or_overridden": "none",
        "conflict_status": "none",
    }


# ---------------------------------------------------------------------------
# profile_provenance_invariant: contract-1.1.0 sites (task M1-T006)
# ---------------------------------------------------------------------------


class TestProvenanceInvariantDistrictMaps:
    def test_resolving_linkage_passes(self):
        profile = minimal_profile(
            zoning={
                "districts": ["R6"],
                "district_provenance": {"R6": ["prov-1"]},
            },
            provenance=[provenance_record("prov-1")],
        )
        assert vc.profile_provenance_invariant(profile) == []

    def test_dangling_district_ref_fails(self):
        profile = minimal_profile(
            zoning={
                "districts": ["R6"],
                "district_provenance": {"R6": ["prov-missing"]},
            },
            provenance=[provenance_record("prov-1")],
        )
        errors = vc.profile_provenance_invariant(profile)
        assert len(errors) == 1
        assert "district_provenance['R6']" in errors[0]
        assert "prov-missing" in errors[0]
        assert "does not resolve" in errors[0]

    def test_orphan_map_key_fails(self):
        profile = minimal_profile(
            zoning={
                "districts": ["R6"],
                "district_provenance": {"C1-9": ["prov-1"]},
            },
            provenance=[provenance_record("prov-1")],
        )
        errors = vc.profile_provenance_invariant(profile)
        assert len(errors) == 1
        assert "key 'C1-9' is not a member" in errors[0]

    @pytest.mark.parametrize(
        ("array_key", "map_key"),
        vc.ZONING_PROVENANCE_MAPS,
    )
    def test_all_three_maps_are_checked(self, array_key, map_key):
        profile = minimal_profile(
            zoning={
                array_key: ["X1"],
                map_key: {"X1": ["prov-missing"]},
            },
            provenance=[],
        )
        errors = vc.profile_provenance_invariant(profile)
        assert any(map_key in err and "does not resolve" in err for err in errors)

    def test_mapped_features_dangling_ref_fails(self):
        profile = minimal_profile(
            zoning={
                "mapped_features": [
                    {"feature": "splitzone", "value": True, "provenance_ref": "prov-missing"}
                ],
            },
            provenance=[],
        )
        errors = vc.profile_provenance_invariant(profile)
        assert len(errors) == 1
        assert "mapped_features[0]" in errors[0]
        assert "does not resolve" in errors[0]

    def test_broken_shapes_do_not_crash_the_invariant(self):
        # Shape errors are the schema layer's job; the invariant must degrade
        # without raising on non-list refs, non-string entries, or non-string
        # array members.
        profile = minimal_profile(
            zoning={
                "districts": ["R6", {"not": "a string"}],
                "district_provenance": {"R6": "not-a-list"},
                "commercial_overlay_provenance": {"R6": [{"not": "a string"}]},
                "mapped_features": [{"provenance_ref": {"not": "a string"}}, "not-a-dict"],
            },
            provenance=[provenance_record("prov-1")],
        )
        errors = vc.profile_provenance_invariant(profile)  # must not raise
        assert any("mapped_features[0]" in err for err in errors)

    def test_v1_0_profile_without_maps_is_untouched(self):
        profile = minimal_profile(zoning={"districts": ["R6"]})
        profile["profile_version"]["contract_version"] = "1.0.0"
        assert vc.profile_provenance_invariant(profile) == []


# ---------------------------------------------------------------------------
# New fixtures fail (or pass) for exactly the intended reason
# ---------------------------------------------------------------------------


class TestFixtureIntendedReasons:
    def test_bad_coverage_status_enum_fails_on_enum(self):
        errors = schema_errors(load(INVALID_DIR / "bad_coverage_status_enum.json"))
        assert any(
            ".coverage_status" in err and "'approved'" in err and "enum" in err for err in errors
        )

    def test_bad_data_completeness_enum_fails_on_enum(self):
        errors = schema_errors(load(INVALID_DIR / "bad_data_completeness_enum.json"))
        assert any(
            "$.data_completeness" in err and "'partial'" in err and "enum" in err
            for err in errors
        )

    def test_reproducibility_missing_subfield_fails_on_required(self):
        errors = schema_errors(load(INVALID_DIR / "reproducibility_missing_correlation_id.json"))
        assert any(
            "$.reproducibility" in err and "missing required property 'correlation_id'" in err
            for err in errors
        )

    def test_contract_version_unknown_fails_on_closed_enum(self):
        errors = schema_errors(load(INVALID_DIR / "contract_version_unknown.json"))
        assert any("contract_version" in err and "'1.2.0'" in err for err in errors)

    def test_dangling_district_linkage_is_schema_clean_but_fails_integrity(self):
        instance = load(INVALID_DIR / "district_provenance_dangling_ref.json")
        assert schema_errors(instance) == []  # rejected by the invariant, NOT by shape
        errors = vc.profile_provenance_invariant(instance)
        assert any("prov-does-not-exist" in err and "does not resolve" in err for err in errors)

    def test_orphan_district_linkage_is_schema_clean_but_fails_membership(self):
        instance = load(INVALID_DIR / "district_provenance_orphan_value.json")
        assert schema_errors(instance) == []
        errors = vc.profile_provenance_invariant(instance)
        assert any("key 'C1-9' is not a member" in err for err in errors)

    def test_s6_builder_output_validates_without_modification(self):
        # Ground truth: the accepted M1-T005 builder's exact output
        # (contract_version 1.0.0 + the three additive keys) against v1.1.
        instance = load(VALID_DIR / "builder_output_m1_t005.json")
        assert instance["profile_version"]["contract_version"] == "1.0.0"
        assert "data_completeness" in instance and "reproducibility" in instance
        assert schema_errors(instance) == []
        assert vc.profile_provenance_invariant(instance) == []

    def test_v1_0_regression_fixture_has_no_additive_keys_and_passes(self):
        instance = load(VALID_DIR / "full_example.json")
        assert instance["profile_version"]["contract_version"] == "1.0.0"
        assert "data_completeness" not in instance
        assert "reproducibility" not in instance
        assert "district_provenance" not in instance.get("zoning", {})
        assert schema_errors(instance) == []

    def test_v1_1_full_example_exercises_every_additive_key(self):
        instance = load(VALID_DIR / "full_example_v1_1.json")
        assert instance["profile_version"]["contract_version"] == "1.1.0"
        assert schema_errors(instance) == []
        assert vc.profile_provenance_invariant(instance) == []
        zoning = instance["zoning"]
        for _, map_key in vc.ZONING_PROVENANCE_MAPS:
            assert map_key in zoning
        assert instance["reproducibility"]["dataset_version"] is None  # nullable branch


# ---------------------------------------------------------------------------
# End-to-end: the full validator run stays green with exit code 0
# ---------------------------------------------------------------------------


def test_full_validator_run_exits_zero():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "validate_contracts.py")],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )
    assert proc.returncode == 0, f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    assert "0 failure(s)" in proc.stdout


# ---------------------------------------------------------------------------
# Legacy jsonschema RefResolver path (LIVE on the CI runner: jsonschema
# 4.10.3 has no 'referencing' package). Forcing ImportError exercises the
# exact code branch the CI runner takes, on whatever jsonschema is local.
# ---------------------------------------------------------------------------


jsonschema = pytest.importorskip("jsonschema")


@pytest.fixture()
def legacy_validator_factory(monkeypatch):
    # None in sys.modules makes 'from referencing import ...' raise
    # ImportError, forcing make_validator onto the RefResolver branch.
    monkeypatch.setitem(sys.modules, "referencing", None)
    _, _, make_validator = vc.load_jsonschema_engine()
    assert make_validator is not None

    def factory(schema):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            return make_validator(schema, list(REGISTRY.values()))

    return factory


class TestLegacyRefResolverPath:
    @pytest.mark.parametrize(
        "fixture_name",
        ["full_example.json", "full_example_v1_1.json", "builder_output_m1_t005.json"],
    )
    def test_v1_1_refs_resolve_on_the_legacy_path(self, legacy_validator_factory, fixture_name):
        validator = legacy_validator_factory(PROFILE_SCHEMA)
        instance = load(VALID_DIR / fixture_name)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            errors = [e.message for e in validator.iter_errors(instance)]
        assert errors == []

    def test_enum_rejection_works_on_the_legacy_path(self, legacy_validator_factory):
        validator = legacy_validator_factory(PROFILE_SCHEMA)
        instance = load(INVALID_DIR / "bad_coverage_status_enum.json")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            errors = [e.message for e in validator.iter_errors(instance)]
        assert errors, "legacy path must reject the bad coverage_status enum value"

    def test_remote_ref_fails_closed_on_the_legacy_path(self, legacy_validator_factory):
        rogue = {
            "$id": "https://github.com/martin10101/nyc-buildability/rogue.schema.json",
            "type": "object",
            "properties": {"x": {"$ref": "https://example.invalid/never-loaded.schema.json"}},
        }
        validator = legacy_validator_factory(rogue)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            with pytest.raises(Exception, match="remote \\$ref fetch blocked"):
                list(validator.iter_errors({"x": 1}))

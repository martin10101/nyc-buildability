"""TypeScript type-generation determinism + coverage (task M2-T003, S5).

These tests run WITHOUT any Node toolchain (stdlib Python only), matching the
thin-client policy. They prove:

- regenerating is byte-identical to the committed output (the CI drift check);
- --check passes against the committed file;
- the generated types cover 100% of the property_profile schema keys (every
  top-level and nested object key appears as a TS member).

Run: python -m pytest packages/contracts/scripts/tests
"""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
CONTRACTS_ROOT = SCRIPTS_DIR.parent
SCHEMA_DIR = CONTRACTS_ROOT / "schemas" / "v1"
GENERATED = CONTRACTS_ROOT / "generated" / "property_profile.ts"


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "generate_ts_types", SCRIPTS_DIR / "generate_ts_types.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEN = _load_generator()


def test_committed_output_is_byte_identical_to_fresh_generation() -> None:
    fresh = GEN.generate()
    committed = GENERATED.read_text(encoding="utf-8")
    assert committed == fresh, (
        "packages/contracts/generated/property_profile.ts is out of date; run "
        "python packages/contracts/scripts/generate_ts_types.py and commit it."
    )


def test_generation_is_deterministic_across_runs() -> None:
    assert GEN.generate() == GEN.generate()


def test_output_uses_lf_and_single_trailing_newline() -> None:
    text = GENERATED.read_text(encoding="utf-8")
    assert "\r\n" not in text
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def _schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def _collect_object_keys(node: dict, schemas: dict, seen: set[int] | None = None) -> set[str]:
    """All property keys reachable in the property_profile schema graph,
    following $refs across the four contract files."""
    if seen is None:
        seen = set()
    if id(node) in seen or not isinstance(node, dict):
        return set()
    seen.add(id(node))
    keys: set[str] = set()

    if "$ref" in node:
        ref = node["$ref"]
        if ref.startswith("#/"):
            filename, pointer = "property_profile.schema.json", ref[1:]
        elif "#" in ref:
            filename, pointer = ref.split("#", 1)
        else:
            filename, pointer = ref, ""
        target = schemas[filename]
        for part in [p for p in pointer.split("/") if p]:
            target = target[part]
        keys |= _collect_object_keys(target, schemas, seen)

    for key, prop in node.get("properties", {}).items():
        keys.add(key)
        keys |= _collect_object_keys(prop, schemas, seen)

    additional = node.get("additionalProperties")
    if isinstance(additional, dict):
        keys |= _collect_object_keys(additional, schemas, seen)

    items = node.get("items")
    if isinstance(items, dict):
        keys |= _collect_object_keys(items, schemas, seen)

    return keys


def test_generated_types_cover_100_percent_of_schema_keys() -> None:
    schemas = {
        name: _schema(name)
        for name in (
            "property_profile.schema.json",
            "source_fact.schema.json",
            "common.schema.json",
            "coverage_status.schema.json",
        )
    }
    schema_keys = _collect_object_keys(schemas["property_profile.schema.json"], schemas)
    assert schema_keys, "no keys collected from schema"

    ts = GENERATED.read_text(encoding="utf-8")
    # Member declarations look like `  key: ...` or `  key?: ...` or quoted.
    declared = set(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\??:", ts, flags=re.MULTILINE))
    declared |= {
        m for m in re.findall(r'^\s*"([^"]+)"\??:', ts, flags=re.MULTILINE)
    }

    missing = schema_keys - declared
    assert not missing, f"generated TS is missing schema keys: {sorted(missing)}"


def test_generated_types_pin_the_closed_contract_version_enum() -> None:
    ts = GENERATED.read_text(encoding="utf-8")
    assert '"1.0.0" | "1.1.0" | "1.2.0" | "1.3.0"' in ts
    # No unpublished version leaks into the generated union.
    assert '"1.4.0"' not in ts


def test_check_mode_passes_against_committed_file() -> None:
    # Invoke main(--check) in-process; it must return 0. Since M2-T010 this
    # covers BOTH managed artifacts: property_profile.ts and the client
    # SUPPORTED_CONTRACT_VERSIONS block in apps/web/src/lib/contract.ts.
    import sys

    argv = sys.argv
    try:
        sys.argv = ["generate_ts_types.py", "--check"]
        rc = GEN.main()
    finally:
        sys.argv = argv
    assert rc == 0


# ---------------------------------------------------------------------------
# Task M2-T010: client SUPPORTED_CONTRACT_VERSIONS derivation + drift red path
# ---------------------------------------------------------------------------

WEB_CONTRACT = GEN.WEB_CONTRACT_PATH


def _run_check_main() -> int:
    import sys

    argv = sys.argv
    try:
        sys.argv = ["generate_ts_types.py", "--check"]
        return GEN.main()
    finally:
        sys.argv = argv


def test_schema_enum_is_closed_at_1_3_0() -> None:
    """CT-S5 guard: the canonical enum ends at 1.3.0 - this task publishes
    NOTHING after it."""
    enum = GEN.contract_version_enum(GEN.load_schemas())
    assert enum == ["1.0.0", "1.1.0", "1.2.0", "1.3.0"]


def test_committed_client_block_is_byte_identical_to_fresh_derivation() -> None:
    """CT-S1: the committed SUPPORTED_CONTRACT_VERSIONS block in contract.ts
    equals a fresh derivation from the canonical schema enum, byte for byte
    (read_text universal-newline translation makes this EOL-safe, matching
    the property_profile.ts check discipline)."""
    committed = GEN.extract_client_block(WEB_CONTRACT.read_text(encoding="utf-8"))
    fresh = GEN.client_versions_block(GEN.load_schemas())
    assert committed == fresh, (
        "apps/web/src/lib/contract.ts SUPPORTED_CONTRACT_VERSIONS block is out "
        "of date; run python packages/contracts/scripts/generate_ts_types.py"
    )


def test_client_block_derivation_is_deterministic() -> None:
    schemas = GEN.load_schemas()
    assert GEN.client_versions_block(schemas) == GEN.client_versions_block(schemas)


def _publish_simulated_version(tmp_path, version: str):
    """Copy the four canonical schemas into tmp and append a simulated
    published version to the property_profile contract_version enum."""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    for name in (
        "property_profile.schema.json",
        "source_fact.schema.json",
        "common.schema.json",
        "coverage_status.schema.json",
    ):
        (schema_dir / name).write_text(
            (SCHEMA_DIR / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    profile = json.loads(
        (schema_dir / "property_profile.schema.json").read_text(encoding="utf-8")
    )
    profile["properties"]["profile_version"]["properties"]["contract_version"][
        "enum"
    ].append(version)
    (schema_dir / "property_profile.schema.json").write_text(
        json.dumps(profile, indent=2) + "\n", encoding="utf-8"
    )
    return schema_dir


def test_drift_schema_published_version_missing_from_client_turns_check_red(
    tmp_path, monkeypatch, capsys
) -> None:
    """CT-S2 (negative drift regression, THE CI-red path): simulate the schema
    publishing 1.4.0 while the committed client block still ends at 1.3.0.

    The generated-artifact half of --check is satisfied against a fresh
    generation from the mutated schema (tmp OUTPUT_PATH), isolating the CLIENT
    block check: it must fail loudly (rc 1 + explicit message), proving a
    schema-published version can never be silently omitted from the client
    runtime list."""
    schema_dir = _publish_simulated_version(tmp_path, "1.4.0")
    monkeypatch.setattr(GEN, "SCHEMA_DIR", schema_dir)

    # Satisfy the property_profile.ts byte-identity half against the mutated
    # schema so the failure below is attributable to the CLIENT block alone.
    fresh_output = tmp_path / "property_profile.ts"
    fresh_output.write_text(GEN.generate(), encoding="utf-8", newline="\n")
    monkeypatch.setattr(GEN, "OUTPUT_PATH", fresh_output)

    rc = _run_check_main()
    err = capsys.readouterr().err
    assert rc == 1
    assert "SUPPORTED_CONTRACT_VERSIONS block" in err
    assert "out of date" in err


def test_drift_end_to_end_check_fails_when_schema_moves_ahead(
    tmp_path, monkeypatch,
) -> None:
    """CT-S2 companion: with NO tmp substitution of the generated artifact,
    the very same simulated 1.4.0 publication also turns the committed
    property_profile.ts check red (rc 1) - drift cannot pass EITHER half of
    the contracts-typegen CI job."""
    schema_dir = _publish_simulated_version(tmp_path, "1.4.0")
    monkeypatch.setattr(GEN, "SCHEMA_DIR", schema_dir)
    assert _run_check_main() == 1


def test_client_block_check_red_when_client_ahead_of_schema(
    tmp_path, monkeypatch, capsys
) -> None:
    """Reverse drift: a version present in the client block but absent from
    the schema enum (hand-edited block) must also fail."""
    contract_text = WEB_CONTRACT.read_text(encoding="utf-8")
    committed = GEN.extract_client_block(contract_text)
    mutated_block = committed.replace('  "1.3.0",', '  "1.3.0",\n  "9.9.9",')
    assert mutated_block != committed
    fake_contract = tmp_path / "contract.ts"
    fake_contract.write_text(
        contract_text.replace(committed, mutated_block, 1),
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(GEN, "WEB_CONTRACT_PATH", fake_contract)

    rc = GEN.check_client_block(GEN.load_schemas())
    assert rc == 1
    assert "out of date" in capsys.readouterr().err


def test_client_block_check_red_when_markers_are_mangled(
    tmp_path, monkeypatch, capsys
) -> None:
    """A deleted/duplicated marker must fail the check, never pass silently."""
    contract_text = WEB_CONTRACT.read_text(encoding="utf-8")
    fake_contract = tmp_path / "contract.ts"
    fake_contract.write_text(
        contract_text.replace(GEN.CLIENT_BLOCK_END, "// mangled", 1),
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(GEN, "WEB_CONTRACT_PATH", fake_contract)

    rc = GEN.check_client_block(GEN.load_schemas())
    assert rc == 1
    assert "exactly one generated" in capsys.readouterr().err


def test_write_mode_updates_stale_client_block_from_schema(
    tmp_path, monkeypatch,
) -> None:
    """Publication flow (on tmp copies): after the schema publishes 1.4.0,
    write mode regenerates the client block automatically - no manual client
    edit - and the refreshed tree passes --check. Idempotent second run."""
    schema_dir = _publish_simulated_version(tmp_path, "1.4.0")
    monkeypatch.setattr(GEN, "SCHEMA_DIR", schema_dir)

    fake_output = tmp_path / "property_profile.ts"
    fake_contract = tmp_path / "contract.ts"
    fake_contract.write_text(
        WEB_CONTRACT.read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
    )
    monkeypatch.setattr(GEN, "OUTPUT_PATH", fake_output)
    monkeypatch.setattr(GEN, "WEB_CONTRACT_PATH", fake_contract)

    import sys

    argv = sys.argv
    try:
        sys.argv = ["generate_ts_types.py"]
        assert GEN.main() == 0  # write
        first = fake_contract.read_text(encoding="utf-8")
        assert '"1.4.0",' in GEN.extract_client_block(first)
        sys.argv = ["generate_ts_types.py", "--check"]
        assert GEN.main() == 0  # regenerated tree is clean
        sys.argv = ["generate_ts_types.py"]
        assert GEN.main() == 0  # idempotent
        assert fake_contract.read_text(encoding="utf-8") == first
    finally:
        sys.argv = argv

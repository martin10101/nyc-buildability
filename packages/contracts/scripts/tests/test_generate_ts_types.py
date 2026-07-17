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
    # Invoke main(--check) in-process; it must return 0.
    import sys

    argv = sys.argv
    try:
        sys.argv = ["generate_ts_types.py", "--check"]
        rc = GEN.main()
    finally:
        sys.argv = argv
    assert rc == 0

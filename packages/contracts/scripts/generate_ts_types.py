#!/usr/bin/env python3
"""Deterministic TypeScript type generator for the canonical property-profile
contract (task M2-T003 item E, scenario S5).

WHY A STDLIB PYTHON GENERATOR: the owner PC is a thin client
(docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md) - no new heavy Node toolchain
may be installed locally. This generator uses ONLY the Python standard library
(already present for the API), takes NO network, and produces byte-stable
output. CI regenerates and diffs it; the committed file must be byte-identical
to a fresh run (the drift check in .github/workflows/ci.yml).

WHAT IT GENERATES: TypeScript interfaces/types covering 100% of the keys in
packages/contracts/schemas/v1/property_profile.schema.json, resolving cross-
file $refs into common.schema.json, source_fact.schema.json, and
coverage_status.schema.json. It replaces any hand-written client type
representation (the competing representation removed when M2-T002 migrates the
web client). String enums, unions, nullable keys, required-vs-optional, and
additionalProperties maps are all honored so the emitted types match the
schema's structural contract.

USAGE (also the exact CI command):
    python packages/contracts/scripts/generate_ts_types.py --check   # diff only
    python packages/contracts/scripts/generate_ts_types.py           # write

The output path is packages/contracts/generated/property_profile.ts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas" / "v1"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "generated" / "property_profile.ts"

# The four contract documents a property_profile $ref registry must load.
SCHEMA_FILES = (
    "property_profile.schema.json",
    "source_fact.schema.json",
    "common.schema.json",
    "coverage_status.schema.json",
)

# ---------------------------------------------------------------------------
# Schema loading + $ref resolution across the four files
# ---------------------------------------------------------------------------


def load_schemas() -> dict[str, dict]:
    """Return {filename: parsed schema}. Filenames (not $ids) are the keys the
    cross-file $refs use (e.g. "common.schema.json#/$defs/bbl")."""
    return {
        name: json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        for name in SCHEMA_FILES
    }


class Resolver:
    """Resolves the exact $ref forms used in these contracts:

    - local:      "#/$defs/fact_value"
    - cross-file: "common.schema.json#/$defs/bbl"
    - whole file: "source_fact.schema.json"
    """

    def __init__(self, schemas: dict[str, dict], current_file: str) -> None:
        self.schemas = schemas
        self.current_file = current_file

    def for_file(self, filename: str) -> Resolver:
        return Resolver(self.schemas, filename)

    def resolve(self, ref: str) -> tuple[dict, str, str]:
        """Return (node, defining_file, pointer) for a $ref."""
        if ref.startswith("#/"):
            filename, pointer = self.current_file, ref[1:]
        elif "#" in ref:
            filename, fragment = ref.split("#", 1)
            pointer = fragment
        else:
            filename, pointer = ref, ""
        doc = self.schemas[filename]
        node = doc
        for part in [p for p in pointer.split("/") if p]:
            node = node[part]
        return node, filename, pointer


# ---------------------------------------------------------------------------
# TypeScript emission
# ---------------------------------------------------------------------------

# Named TS aliases minted for reused $defs so the output reads like the schema
# and stays small. Keyed by (defining_file, pointer) -> TS type name.
NAMED_DEFS: dict[tuple[str, str], str] = {
    ("common.schema.json", "/$defs/bbl"): "Bbl",
    ("common.schema.json", "/$defs/bin"): "Bin",
    ("common.schema.json", "/$defs/borough_code"): "BoroughCode",
    ("common.schema.json", "/$defs/borough_name"): "BoroughName",
    ("common.schema.json", "/$defs/zip_code"): "ZipCode",
    ("common.schema.json", "/$defs/date_time"): "DateTime",
    ("common.schema.json", "/$defs/date"): "DateOnly",
    ("common.schema.json", "/$defs/non_empty_string"): "NonEmptyString",
    ("common.schema.json", "/$defs/digest_sha256"): "DigestSha256",
    ("coverage_status.schema.json", ""): "CoverageStatus",
    ("coverage_status.schema.json", "/$defs/data_completeness"): "DataCompleteness",
    ("source_fact.schema.json", ""): "SourceFact",
    ("property_profile.schema.json", "/$defs/fact_value"): "FactValue",
    ("property_profile.schema.json", "/$defs/provenance_ref_list"): "ProvenanceRefList",
    ("property_profile.schema.json", "/$defs/district_provenance_map"): "DistrictProvenanceMap",
}


def ts_scalar(schema_type: str) -> str:
    return {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "null": "null",
    }.get(schema_type, "unknown")


def type_expr(node: dict, resolver: Resolver, indent: int) -> str:
    """Return a TS type expression for a schema node (inline)."""
    if "$ref" in node:
        target, filename, pointer = resolver.resolve(node["$ref"])
        named = NAMED_DEFS.get((filename, pointer))
        if named is not None:
            return named
        # Unnamed ref: inline the resolved target under the defining file.
        return type_expr(target, resolver.for_file(filename), indent)

    if "enum" in node:
        return " | ".join(json.dumps(value) for value in node["enum"])

    node_type = node.get("type")

    if isinstance(node_type, list):
        parts = [ts_scalar(t) for t in node_type]
        return " | ".join(parts)

    if node_type == "object" or "properties" in node or "additionalProperties" in node:
        return object_expr(node, resolver, indent)

    if node_type == "array":
        items = node.get("items", {})
        inner = type_expr(items, resolver, indent) if items else "unknown"
        # Parenthesize unions inside array element position.
        if " | " in inner and not inner.startswith("{"):
            inner = f"({inner})"
        return f"{inner}[]"

    if node_type in ("string", "integer", "number", "boolean", "null"):
        return ts_scalar(node_type)

    # No type keyword and no properties: an "any JSON value" node
    # (e.g. fact_value.value, original_value). Model as unknown - the safest
    # TS analogue that still forces a narrowing check at the use site.
    return "unknown"


def object_expr(node: dict, resolver: Resolver, indent: int) -> str:
    """Emit an inline object type literal for a schema object node."""
    props = node.get("properties", {})
    required = set(node.get("required", []))
    pad = "  " * (indent + 1)
    close_pad = "  " * indent
    lines: list[str] = ["{"]

    for key in props:  # preserve schema key order (deterministic)
        prop = props[key]
        optional = "" if key in required else "?"
        expr = type_expr(prop, resolver, indent + 1)
        lines.append(f"{pad}{json_prop_key(key)}{optional}: {expr};")

    additional = node.get("additionalProperties")
    if isinstance(additional, dict):
        value_expr = type_expr(additional, resolver, indent + 1)
        lines.append(f"{pad}[key: string]: {value_expr};")

    lines.append(f"{close_pad}}}")
    return "\n".join(lines)


def json_prop_key(key: str) -> str:
    """A valid TS identifier is emitted bare; anything else is quoted."""
    if key.isidentifier():
        return key
    return json.dumps(key)


def emit_named_defs(schemas: dict[str, dict]) -> list[str]:
    """Emit the named alias/interface for each reused $def, in a fixed order."""
    blocks: list[str] = []
    for (filename, pointer), name in NAMED_DEFS.items():
        resolver = Resolver(schemas, filename)
        doc = schemas[filename]
        node = doc
        for part in [p for p in pointer.split("/") if p]:
            node = node[part]
        expr = type_expr(node, resolver, 0)
        if expr.startswith("{"):
            blocks.append(f"export interface {name} {expr}\n")
        else:
            blocks.append(f"export type {name} = {expr};\n")
    return blocks


def generate() -> str:
    schemas = load_schemas()
    profile = schemas["property_profile.schema.json"]
    resolver = Resolver(schemas, "property_profile.schema.json")

    header = (
        "// GENERATED FILE - DO NOT EDIT BY HAND.\n"
        "// Source of truth: packages/contracts/schemas/v1/property_profile.schema.json\n"
        "// (+ common, source_fact, coverage_status). Regenerate with:\n"
        "//   python packages/contracts/scripts/generate_ts_types.py\n"
        "// CI fails if this file diverges from a fresh generation (task M2-T003, S5).\n"
        "//\n"
        "// These types replace any hand-written client property-profile\n"
        "// representation; all modules exchange this one canonical contract\n"
        "// (PRD section 32.3). Every schema key is covered.\n"
    )

    body: list[str] = [header]
    body.extend(emit_named_defs(schemas))

    root_expr = object_expr(profile, resolver, 0)
    body.append(f"export interface PropertyProfile {root_expr}\n")

    # LF newlines, single trailing newline; byte-stable across platforms.
    return "\n".join(block.rstrip("\n") for block in body) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero if the committed file would change",
    )
    args = parser.parse_args()

    generated = generate()

    if args.check:
        if not OUTPUT_PATH.exists():
            sys.stderr.write(
                f"ERROR: {OUTPUT_PATH} is missing; run the generator and commit it.\n"
            )
            return 1
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != generated:
            sys.stderr.write(
                "ERROR: generated TypeScript types are out of date.\n"
                "Run: python packages/contracts/scripts/generate_ts_types.py\n"
                "and commit packages/contracts/generated/property_profile.ts.\n"
            )
            return 1
        sys.stdout.write("OK: generated TypeScript types are up to date.\n")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(generated, encoding="utf-8", newline="\n")
    sys.stdout.write(f"wrote {OUTPUT_PATH}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

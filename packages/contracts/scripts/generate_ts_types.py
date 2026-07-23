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

SECOND MANAGED ARTIFACT (task M2-T010): the web client's runtime
SUPPORTED_CONTRACT_VERSIONS array in apps/web/src/lib/contract.ts is a
GENERATED marker-delimited block derived from the canonical schema's
profile_version.contract_version enum. This makes the schema enum the SINGLE
source of truth for the published-version list on the client: publishing a
contract version is a schema change plus regeneration, and a version present
in the schema but absent from the client list is impossible to merge (the
--check mode, run by the contracts-typegen CI job, byte-compares the block
and fails loudly on any divergence). The block lives INSIDE contract.ts (not
a separate generated module) so the Next.js bundle keeps compiling only files
within apps/web - the M2-T002 type-only-import discipline is preserved.

USAGE (also the exact CI command):
    python packages/contracts/scripts/generate_ts_types.py --check   # diff only
    python packages/contracts/scripts/generate_ts_types.py           # write

The output paths are packages/contracts/generated/property_profile.ts and the
managed block within apps/web/src/lib/contract.ts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas" / "v1"
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "generated" / "property_profile.ts"

# The web client file carrying the generated SUPPORTED_CONTRACT_VERSIONS
# block (task M2-T010). parents[3] is the repository root.
WEB_CONTRACT_PATH = (
    Path(__file__).resolve().parents[3] / "apps" / "web" / "src" / "lib" / "contract.ts"
)

# Marker lines delimiting the managed block inside contract.ts. Each must
# appear EXACTLY once; everything between them (inclusive) is generated.
CLIENT_BLOCK_BEGIN = (
    "// BEGIN GENERATED: SUPPORTED_CONTRACT_VERSIONS (generate_ts_types.py)"
)
CLIENT_BLOCK_END = "// END GENERATED: SUPPORTED_CONTRACT_VERSIONS"

# The four contract documents a property_profile $ref registry must load.
SCHEMA_FILES = (
    "property_profile.schema.json",
    "source_fact.schema.json",
    "common.schema.json",
    "coverage_status.schema.json",
)

# SECOND GENERATED TS ARTIFACT (task M4-T005): the rule_evaluation contract.
# Generated INDEPENDENTLY of property_profile.ts so property_profile.ts stays
# byte-identical (owner constraint). rule_evaluation only $refs coverage_status
# and common (never property_profile - the evaluated input is identified by
# reference, never embedded).
RULE_EVAL_OUTPUT_PATH = (
    Path(__file__).resolve().parents[1] / "generated" / "rule_evaluation.ts"
)
RULE_EVAL_SCHEMA_FILES = (
    "rule_evaluation.schema.json",
    "coverage_status.schema.json",
    "common.schema.json",
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

# Named aliases for the rule_evaluation artifact (task M4-T005). A SEPARATE map
# so the property_profile emission (which iterates NAMED_DEFS) is untouched and
# property_profile.ts stays byte-identical. Shared scalars are re-declared in
# rule_evaluation.ts so each generated file is standalone.
RULE_EVAL_NAMED_DEFS: dict[tuple[str, str], str] = {
    ("common.schema.json", "/$defs/bbl"): "Bbl",
    ("common.schema.json", "/$defs/non_empty_string"): "NonEmptyString",
    ("common.schema.json", "/$defs/digest_sha256"): "DigestSha256",
    ("coverage_status.schema.json", ""): "CoverageStatus",
    ("coverage_status.schema.json", "/$defs/data_completeness"): "DataCompleteness",
    ("rule_evaluation.schema.json", "/$defs/coverage_status_draft"): "DraftCoverageStatus",
    ("rule_evaluation.schema.json", "/$defs/input_provenance"): "InputProvenance",
    ("rule_evaluation.schema.json", "/$defs/evaluated_input"): "EvaluatedInput",
    ("rule_evaluation.schema.json", "/$defs/spatial_context"): "SpatialContext",
    ("rule_evaluation.schema.json", "/$defs/base_district_candidate"): "BaseDistrictCandidate",
    ("rule_evaluation.schema.json", "/$defs/spatial_uncertainty"): "SpatialUncertainty",
    ("rule_evaluation.schema.json", "/$defs/family_coverage"): "FamilyCoverage",
    ("rule_evaluation.schema.json", "/$defs/competing_rule"): "CompetingRule",
    ("rule_evaluation.schema.json", "/$defs/rule_conflict"): "RuleConflict",
    ("rule_evaluation.schema.json", "/$defs/computation_step"): "ComputationStep",
    ("rule_evaluation.schema.json", "/$defs/citation"): "Citation",
    ("rule_evaluation.schema.json", "/$defs/evaluation_trace"): "EvaluationTrace",
}


def ts_scalar(schema_type: str) -> str:
    return {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "null": "null",
    }.get(schema_type, "unknown")


def type_expr(node: dict, resolver: Resolver, indent: int, named_defs: dict | None = None) -> str:
    """Return a TS type expression for a schema node (inline).

    ``named_defs`` selects which named-alias map to honor; it defaults to
    ``NAMED_DEFS`` so the property_profile emission is byte-for-byte unchanged.
    The rule_evaluation artifact passes ``RULE_EVAL_NAMED_DEFS`` (task M4-T005).
    """
    if named_defs is None:
        named_defs = NAMED_DEFS
    if "$ref" in node:
        target, filename, pointer = resolver.resolve(node["$ref"])
        named = named_defs.get((filename, pointer))
        if named is not None:
            return named
        # Unnamed ref: inline the resolved target under the defining file.
        return type_expr(target, resolver.for_file(filename), indent, named_defs)

    if "enum" in node:
        return " | ".join(json.dumps(value) for value in node["enum"])

    node_type = node.get("type")

    if isinstance(node_type, list):
        parts = [ts_scalar(t) for t in node_type]
        return " | ".join(parts)

    if node_type == "object" or "properties" in node or "additionalProperties" in node:
        return object_expr(node, resolver, indent, named_defs)

    if node_type == "array":
        items = node.get("items", {})
        inner = type_expr(items, resolver, indent, named_defs) if items else "unknown"
        # Parenthesize unions inside array element position.
        if " | " in inner and not inner.startswith("{"):
            inner = f"({inner})"
        return f"{inner}[]"

    if node_type in ("string", "integer", "number", "boolean", "null"):
        return ts_scalar(node_type)

    # Pure combiner nodes (no type/properties/$ref/enum): anyOf -> union,
    # allOf -> intersection. property_profile has no such node reaching here
    # (its allOf/anyOf always sit on an object node caught above), so this
    # branch is exercised only by the rule_evaluation artifact (task M4-T005:
    # nullable $ref unions and the coverage_status_draft narrowing) and cannot
    # change property_profile.ts. Only concrete branch types are combined;
    # "unknown" branches are dropped so a union/intersection stays meaningful.
    for combiner, joiner in (("anyOf", " | "), ("allOf", " & ")):
        if combiner in node:
            parts: list[str] = []
            for sub in node[combiner]:
                expr = type_expr(sub, resolver, indent, named_defs)
                if expr == "unknown" or expr in parts:
                    continue
                if " | " in expr and not expr.startswith("{"):
                    expr = f"({expr})"
                parts.append(expr)
            if parts:
                return joiner.join(parts)

    # No type keyword and no properties: an "any JSON value" node
    # (e.g. fact_value.value, original_value). Model as unknown - the safest
    # TS analogue that still forces a narrowing check at the use site.
    return "unknown"


def object_expr(node: dict, resolver: Resolver, indent: int, named_defs: dict | None = None) -> str:
    """Emit an inline object type literal for a schema object node."""
    if named_defs is None:
        named_defs = NAMED_DEFS
    props = node.get("properties", {})
    required = set(node.get("required", []))
    pad = "  " * (indent + 1)
    close_pad = "  " * indent
    lines: list[str] = ["{"]

    for key in props:  # preserve schema key order (deterministic)
        prop = props[key]
        optional = "" if key in required else "?"
        expr = type_expr(prop, resolver, indent + 1, named_defs)
        lines.append(f"{pad}{json_prop_key(key)}{optional}: {expr};")

    additional = node.get("additionalProperties")
    if isinstance(additional, dict):
        value_expr = type_expr(additional, resolver, indent + 1, named_defs)
        lines.append(f"{pad}[key: string]: {value_expr};")

    lines.append(f"{close_pad}}}")
    return "\n".join(lines)


def json_prop_key(key: str) -> str:
    """A valid TS identifier is emitted bare; anything else is quoted."""
    if key.isidentifier():
        return key
    return json.dumps(key)


def emit_named_defs(schemas: dict[str, dict], named_defs: dict | None = None) -> list[str]:
    """Emit the named alias/interface for each reused $def, in a fixed order."""
    if named_defs is None:
        named_defs = NAMED_DEFS
    blocks: list[str] = []
    for (filename, pointer), name in named_defs.items():
        resolver = Resolver(schemas, filename)
        doc = schemas[filename]
        node = doc
        for part in [p for p in pointer.split("/") if p]:
            node = node[part]
        expr = type_expr(node, resolver, 0, named_defs)
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


# ---------------------------------------------------------------------------
# rule_evaluation artifact (task M4-T005)
# ---------------------------------------------------------------------------


def load_rule_eval_schemas() -> dict[str, dict]:
    """Return {filename: parsed schema} for the rule_evaluation $ref set
    (rule_evaluation + coverage_status + common). Uses SCHEMA_DIR so the
    generator honors a monkeypatched schema dir consistently; callers guard the
    missing-file case (the property_profile drift-test harness copies only the
    four profile schemas)."""
    return {
        name: json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))
        for name in RULE_EVAL_SCHEMA_FILES
    }


def generate_rule_evaluation() -> str:
    """Generate the rule_evaluation.ts source. Independent of generate() so
    property_profile.ts stays byte-identical."""
    schemas = load_rule_eval_schemas()
    root = schemas["rule_evaluation.schema.json"]
    resolver = Resolver(schemas, "rule_evaluation.schema.json")

    header = (
        "// GENERATED FILE - DO NOT EDIT BY HAND.\n"
        "// Source of truth: packages/contracts/schemas/v1/rule_evaluation.schema.json\n"
        "// (+ common, coverage_status). Regenerate with:\n"
        "//   python packages/contracts/scripts/generate_ts_types.py\n"
        "// CI fails if this file diverges from a fresh generation (task M4-T005).\n"
        "//\n"
        "// One canonical rule-evaluation result contract shared by API, workers,\n"
        "// scenarios, and reports (PRD section 32.3). coverage_status is the\n"
        "// canonical vocabulary narrowed to exclude 'verified' - a draft result\n"
        "// is never Verified. The evaluated input is identified by reference\n"
        "// (bbl + profile contract version + provenance + fingerprint), never by\n"
        "// an embedded profile copy.\n"
    )

    body: list[str] = [header]
    body.extend(emit_named_defs(schemas, RULE_EVAL_NAMED_DEFS))

    root_expr = object_expr(root, resolver, 0, RULE_EVAL_NAMED_DEFS)
    body.append(f"export interface RuleEvaluation {root_expr}\n")

    return "\n".join(block.rstrip("\n") for block in body) + "\n"


def check_rule_evaluation() -> int:
    """--check half for rule_evaluation.ts: exit non-zero unless the committed
    file is byte-identical to a fresh generation. Skips (rc 0) when the active
    schema dir has no rule_evaluation.schema.json - the property_profile drift-
    test harness copies only the four profile schemas, and real CI always has
    the file (so drift is always caught there)."""
    if not (SCHEMA_DIR / "rule_evaluation.schema.json").exists():
        return 0
    generated = generate_rule_evaluation()
    if not RULE_EVAL_OUTPUT_PATH.exists():
        sys.stderr.write(
            f"ERROR: {RULE_EVAL_OUTPUT_PATH} is missing; run the generator and commit it.\n"
        )
        return 1
    if RULE_EVAL_OUTPUT_PATH.read_text(encoding="utf-8") != generated:
        sys.stderr.write(
            "ERROR: generated rule_evaluation TypeScript types are out of date.\n"
            "Run: python packages/contracts/scripts/generate_ts_types.py\n"
            "and commit packages/contracts/generated/rule_evaluation.ts.\n"
        )
        return 1
    sys.stdout.write("OK: generated rule_evaluation TypeScript types are up to date.\n")
    return 0


def write_rule_evaluation() -> int:
    """Write mode for rule_evaluation.ts. Skips when the active schema dir has
    no rule_evaluation.schema.json (see check_rule_evaluation)."""
    if not (SCHEMA_DIR / "rule_evaluation.schema.json").exists():
        return 0
    RULE_EVAL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RULE_EVAL_OUTPUT_PATH.write_text(
        generate_rule_evaluation(), encoding="utf-8", newline="\n"
    )
    sys.stdout.write(f"wrote {RULE_EVAL_OUTPUT_PATH}\n")
    return 0


# ---------------------------------------------------------------------------
# Client SUPPORTED_CONTRACT_VERSIONS block (task M2-T010)
# ---------------------------------------------------------------------------


def contract_version_enum(schemas: dict[str, dict]) -> list[str]:
    """The CLOSED published contract-version enum, read from the canonical
    schema. Fails loudly if the schema shape ever stops exposing it - the
    generator must never silently guess a version set."""
    try:
        enum = schemas["property_profile.schema.json"]["properties"][
            "profile_version"
        ]["properties"]["contract_version"]["enum"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "property_profile.schema.json no longer exposes the "
            "profile_version.contract_version enum; cannot derive "
            "SUPPORTED_CONTRACT_VERSIONS"
        ) from exc
    if not enum or not all(isinstance(v, str) for v in enum):
        raise ValueError(
            "profile_version.contract_version enum must be a non-empty list "
            f"of strings; got {enum!r}"
        )
    return list(enum)


def client_versions_block(schemas: dict[str, dict]) -> str:
    """The full generated block (markers included, LF-joined, no trailing
    newline) for apps/web/src/lib/contract.ts. Byte-deterministic: derived
    only from the schema enum, in schema order."""
    versions = contract_version_enum(schemas)
    lines = [
        CLIENT_BLOCK_BEGIN,
        "// Derived from packages/contracts/schemas/v1/property_profile.schema.json",
        "// (profile_version.contract_version enum) - the SINGLE canonical source",
        "// of published contract versions. DO NOT EDIT BY HAND. Regenerate with:",
        "//   python packages/contracts/scripts/generate_ts_types.py",
        "// The contracts-typegen CI job runs --check and fails loudly if this",
        "// block diverges from the schema enum (task M2-T010 drift protection).",
        "export const SUPPORTED_CONTRACT_VERSIONS = [",
        *[f"  {json.dumps(version)}," for version in versions],
        "] as const satisfies readonly ContractVersion[];",
        CLIENT_BLOCK_END,
    ]
    return "\n".join(lines)


def extract_client_block(contract_text: str) -> str:
    """Return the committed block (markers included) from contract.ts text.

    Raises ValueError when the markers are missing, duplicated, or out of
    order - a mangled block must fail the check, never pass silently."""
    begin_count = contract_text.count(CLIENT_BLOCK_BEGIN)
    end_count = contract_text.count(CLIENT_BLOCK_END)
    if begin_count != 1 or end_count != 1:
        raise ValueError(
            "apps/web/src/lib/contract.ts must contain exactly one generated "
            "SUPPORTED_CONTRACT_VERSIONS block "
            f"(found {begin_count} BEGIN / {end_count} END markers)"
        )
    start = contract_text.index(CLIENT_BLOCK_BEGIN)
    end = contract_text.index(CLIENT_BLOCK_END)
    if end < start:
        raise ValueError(
            "SUPPORTED_CONTRACT_VERSIONS block markers are out of order in "
            "apps/web/src/lib/contract.ts"
        )
    return contract_text[start : end + len(CLIENT_BLOCK_END)]


def check_client_block(schemas: dict[str, dict]) -> int:
    """--check half for the client block: exit non-zero unless the committed
    block is byte-identical to a fresh derivation from the schema enum. This
    is the CI-red path when the schema publishes a version the client list
    omits (or the block is hand-edited)."""
    if not WEB_CONTRACT_PATH.exists():
        sys.stderr.write(f"ERROR: {WEB_CONTRACT_PATH} is missing.\n")
        return 1
    current = WEB_CONTRACT_PATH.read_text(encoding="utf-8")
    try:
        committed = extract_client_block(current)
    except ValueError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1
    expected = client_versions_block(schemas)
    if committed != expected:
        sys.stderr.write(
            "ERROR: the client SUPPORTED_CONTRACT_VERSIONS block in "
            "apps/web/src/lib/contract.ts is out of date with the canonical "
            "schema's profile_version.contract_version enum.\n"
            "A published contract version MUST NOT be missing from the client "
            "runtime list (task M2-T010 drift protection).\n"
            "Run: python packages/contracts/scripts/generate_ts_types.py\n"
            "and commit apps/web/src/lib/contract.ts.\n"
        )
        return 1
    sys.stdout.write(
        "OK: client SUPPORTED_CONTRACT_VERSIONS block matches the schema enum.\n"
    )
    return 0


def write_client_block(schemas: dict[str, dict]) -> int:
    """Write mode: splice a fresh block between the markers in contract.ts."""
    if not WEB_CONTRACT_PATH.exists():
        sys.stderr.write(f"ERROR: {WEB_CONTRACT_PATH} is missing.\n")
        return 1
    current = WEB_CONTRACT_PATH.read_text(encoding="utf-8")
    try:
        committed = extract_client_block(current)
    except ValueError as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return 1
    expected = client_versions_block(schemas)
    if committed == expected:
        sys.stdout.write(f"unchanged {WEB_CONTRACT_PATH}\n")
        return 0
    updated = current.replace(committed, expected, 1)
    WEB_CONTRACT_PATH.write_text(updated, encoding="utf-8", newline="\n")
    sys.stdout.write(f"wrote {WEB_CONTRACT_PATH}\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit non-zero if the committed file would change",
    )
    args = parser.parse_args()

    schemas = load_schemas()
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
        rc_client = check_client_block(schemas)
        rc_rule = check_rule_evaluation()
        return rc_client or rc_rule

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(generated, encoding="utf-8", newline="\n")
    sys.stdout.write(f"wrote {OUTPUT_PATH}\n")
    rc_client = write_client_block(schemas)
    rc_rule = write_rule_evaluation()
    return rc_client or rc_rule


if __name__ == "__main__":
    raise SystemExit(main())

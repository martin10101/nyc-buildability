"""TypeScript types for the Wave-0 study contract set (task C-03, plan M1-09).

WHAT: the six v1 contracts added by M5-T125 (site_fact, study, results,
report_model, export_record, benchmark_lot) each get one generated file,
packages/contracts/generated/<stem>.ts, emitted by the SAME shared emission
functions generate_ts_types.py uses for its other artifacts (Resolver,
emit_named_defs, object_expr) and checked by the same --check / write halves.

WHY A SIBLING MODULE: generate_ts_types.py is at its modularity baseline
(tools/modularity_baseline.json). It loads this module by path and passes its
emission functions in (an "emitter" namespace built at call time), so a test
that monkeypatches generate_ts_types.SCHEMA_DIR is honored here too and no
circular import exists.

HOW THE SIX DIFFER FROM THE OLDER ARTIFACTS:
- The schemas use ``oneOf`` and ``const``, which the shared emitter does not
  read. Instead of changing the shared emitter (the five older .ts files must
  stay byte-identical), each schema is NORMALIZED before emission: ``const: X``
  becomes ``enum: [X]`` (a literal type) and ``oneOf`` becomes ``anyOf`` (a TS
  union; TS unions are never exclusive anyway). Combiners on object nodes are
  cross-field constraints; object_expr ignores them, as it always has.
- The named-alias map is DERIVED from the $ref graph instead of hand-written:
  every $def (and whole-file $ref) reachable from the root gets a PascalCase
  name; common.schema.json keeps the names the older artifacts use. A name
  collision or a TS built-in name fails loudly, never silently.

Stdlib only, no network, byte-stable output (LF, single trailing newline).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import NamedTuple

# Where the generated .ts files live. Deliberately NOT derived from the
# emitter's SCHEMA_DIR (tests point that at a tmp copy of a few schemas).
GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"


class StudyContract(NamedTuple):
    stem: str  # schema file stem, e.g. "site_fact"
    interface: str  # root TS interface name
    summary: str  # one plain-English line for the file header


# Emission order is fixed (and is the order check/write report in).
STUDY_CONTRACTS: tuple[StudyContract, ...] = (
    StudyContract(
        "site_fact", "SiteFact",
        "One site value of a study: known (rank + source) or unknown (never 0).",
    ),
    StudyContract(
        "study", "Study",
        "One shared study per property: lots, site facts, options as add-on selections.",
    ),
    StudyContract(
        "results", "Results",
        "The answers computed for one option of one study revision.",
    ),
    StudyContract(
        "report_model", "ReportModel",
        "What every export renders, bound to one results document.",
    ),
    StudyContract(
        "export_record", "ExportRecord",
        "One historical export: its inputs, sources and rule versions.",
    ),
    StudyContract(
        "benchmark_lot", "BenchmarkLot",
        "A benchmark, pilot or golden lot with sourced expected values.",
    ),
)

# common.schema.json names, identical to the names the older artifacts use
# (generate_ts_types.NAMED_DEFS) so the same scalar reads the same everywhere.
COMMON_NAMES: dict[str, str] = {
    "bbl": "Bbl",
    "bin": "Bin",
    "borough_code": "BoroughCode",
    "borough_name": "BoroughName",
    "zip_code": "ZipCode",
    "date_time": "DateTime",
    "date": "DateOnly",
    "non_empty_string": "NonEmptyString",
    "digest_sha256": "DigestSha256",
}

# Global TS/DOM type names a generated alias must never shadow.
_RESERVED_NAMES = frozenset({
    "Array", "Boolean", "Date", "Error", "Function", "Map", "Number", "Object",
    "Partial", "Pick", "Promise", "Readonly", "Record", "RegExp", "Required",
    "Set", "String", "Symbol", "Omit", "Exclude", "Extract", "Node", "Element",
    "Document", "Event", "Location", "Range", "Selection", "Text", "Window",
})

_COMMON_FILE = "common.schema.json"


# Keywords whose value maps NAMES to subschemas (a property may be called
# "const") and keywords whose value is DATA, never a schema: neither is renamed.
_NAME_MAPS = frozenset({"properties", "$defs", "patternProperties"})
_DATA_KEYWORDS = frozenset({"enum", "default", "examples"})


def normalize(node):
    """Return a copy of a schema node the shared emitter can read:
    ``const: X`` -> ``enum: [X]`` and ``oneOf`` -> ``anyOf`` (when the node has
    no ``anyOf`` of its own). Key order is preserved otherwise."""
    if isinstance(node, list):
        return [normalize(item) for item in node]
    if not isinstance(node, dict):
        return node
    out: dict = {}
    for key, value in node.items():
        if key in _NAME_MAPS and isinstance(value, dict):
            out[key] = {name: normalize(sub) for name, sub in value.items()}
        elif key in _DATA_KEYWORDS:
            out[key] = value
        elif key == "const" and "enum" not in node:
            out["enum"] = [value]
        elif key == "oneOf" and "anyOf" not in node:
            out["anyOf"] = normalize(value)
        else:
            out[key] = normalize(value)
    return out


def _split_ref(ref: str, current_file: str) -> tuple[str, str]:
    """(file, pointer) for the three $ref forms the contracts use."""
    if ref.startswith("#"):
        return current_file, ref[1:]
    if "#" in ref:
        filename, pointer = ref.split("#", 1)
        return filename, pointer
    return ref, ""


def _iter_refs(node):
    """Every $ref string under a node, in schema key order."""
    if isinstance(node, dict):
        if "$ref" in node:
            yield node["$ref"]
        for value in node.values():
            yield from _iter_refs(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_refs(item)


def _node_at(doc: dict, pointer: str):
    node = doc
    for part in [p for p in pointer.split("/") if p]:
        node = node[part]
    return node


def load_closure(schema_dir: Path, root_file: str) -> dict[str, dict]:
    """{filename: normalized schema} for the root file and every file its
    $refs reach (transitively), in discovery order."""
    schemas: dict[str, dict] = {}
    pending = [root_file]
    while pending:
        filename = pending.pop(0)
        if filename in schemas:
            continue
        doc = json.loads((schema_dir / filename).read_text(encoding="utf-8"))
        schemas[filename] = normalize(doc)
        for ref in _iter_refs(schemas[filename]):
            target_file, _ = _split_ref(ref, filename)
            if target_file not in schemas and target_file not in pending:
                pending.append(target_file)
    return schemas


def _pascal(snake: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in snake.split("_") if part)


def _interface_for_file(filename: str) -> str:
    stem = filename.removesuffix(".schema.json")
    for contract in STUDY_CONTRACTS:
        if contract.stem == stem:
            return contract.interface
    return _pascal(stem)


def _name_for(filename: str, pointer: str) -> str | None:
    """The alias for a $ref target, or None to inline it (a pointer that is
    neither a whole file nor a top-level $def)."""
    if pointer == "":
        return _interface_for_file(filename)
    parts = [p for p in pointer.split("/") if p]
    if len(parts) != 2 or parts[0] != "$defs":
        return None
    if filename == _COMMON_FILE:
        if parts[1] not in COMMON_NAMES:
            raise ValueError(f"no TS name registered for common.schema.json#/$defs/{parts[1]}")
        return COMMON_NAMES[parts[1]]
    return _pascal(parts[1])


def _refs_of_target(schemas: dict[str, dict], filename: str, pointer: str):
    """$refs inside one target. A whole file is walked WITHOUT its $defs block:
    a $def counts only when something reaches it."""
    node = _node_at(schemas[filename], pointer)
    if pointer == "":
        node = {key: value for key, value in node.items() if key != "$defs"}
    return _iter_refs(node)


def derive_named_defs(schemas: dict[str, dict], root_file: str, root_name: str) -> dict:
    """Ordered {(file, pointer): TS name}: every $def of the root file (its
    public vocabulary) plus every other-file $ref target reachable from it.
    Order: common first (COMMON_NAMES order), then each file in closure order
    (whole-file target first, then its $defs in declaration order). Raises
    ValueError on a duplicate name or a reserved name."""
    root_defs = [(root_file, f"/$defs/{name}") for name in schemas[root_file].get("$defs", {})]
    reached: set[tuple[str, str]] = set(root_defs)
    stack = [(root_file, ""), *root_defs]
    visited: set[tuple[str, str]] = set()
    while stack:
        filename, pointer = stack.pop()
        if (filename, pointer) in visited:
            continue
        visited.add((filename, pointer))
        for ref in _refs_of_target(schemas, filename, pointer):
            target = _split_ref(ref, filename)
            if _name_for(*target) is not None:
                reached.add(target)
            stack.append(target)

    ordered: list[tuple[str, str]] = [
        (_COMMON_FILE, f"/$defs/{name}") for name in COMMON_NAMES
        if (_COMMON_FILE, f"/$defs/{name}") in reached
    ]
    for filename in schemas:
        if filename == _COMMON_FILE:
            continue
        candidates = [(filename, "")] + [
            (filename, f"/$defs/{name}") for name in schemas[filename].get("$defs", {})
        ]
        # The root file's own whole-file target is the root interface itself.
        ordered.extend(key for key in candidates if key in reached and key != (root_file, ""))

    named: dict[tuple[str, str], str] = {}
    used = {root_name: (root_file, "")}
    for key in ordered:
        name = _name_for(*key)
        if name in _RESERVED_NAMES:
            raise ValueError(f"generated TS name {name!r} for {key} shadows a built-in type")
        if name in used and used[name] != key:
            raise ValueError(f"generated TS name {name!r} is used by both {used[name]} and {key}")
        used[name] = key
        named[key] = name
    return named


def _header(contract: StudyContract, schemas: dict[str, dict], root_file: str) -> str:
    others = ", ".join(f.removesuffix(".schema.json") for f in schemas if f != root_file)
    return (
        "// GENERATED FILE - DO NOT EDIT BY HAND.\n"
        f"// Source of truth: packages/contracts/schemas/v1/{root_file}\n"
        f"// (+ {others}). Regenerate with:\n"
        "//   python packages/contracts/scripts/generate_ts_types.py\n"
        "// CI fails if this file diverges from a fresh generation (task C-03).\n"
        "//\n"
        f"// {contract.summary}\n"
        "// Types only: cross-field rules (oneOf/allOf constraints such as rank vs\n"
        "// source kind) are enforced by the JSON Schema on the server, not here.\n"
    )


def generate(emitter, stem: str) -> str:
    """The <stem>.ts source. ``emitter`` carries generate_ts_types' SCHEMA_DIR,
    Resolver, emit_named_defs and object_expr."""
    contract = next(c for c in STUDY_CONTRACTS if c.stem == stem)
    root_file = f"{stem}.schema.json"
    schemas = load_closure(emitter.SCHEMA_DIR, root_file)
    named = derive_named_defs(schemas, root_file, contract.interface)
    resolver = emitter.Resolver(schemas, root_file)

    body: list[str] = [_header(contract, schemas, root_file)]
    body.extend(emitter.emit_named_defs(schemas, named))
    root_expr = emitter.object_expr(schemas[root_file], resolver, 0, named)
    body.append(f"export interface {contract.interface} {root_expr}\n")
    return "\n".join(block.rstrip("\n") for block in body) + "\n"


def output_path(stem: str) -> Path:
    return GENERATED_DIR / f"{stem}.ts"


def check_all(emitter) -> int:
    """--check half: every study contract .ts must equal a fresh generation.
    Runs all six (no short-circuit) so every stale file is reported."""
    rc = 0
    for contract in STUDY_CONTRACTS:
        rc |= emitter.check(
            f"{contract.stem}.schema.json",
            lambda stem=contract.stem: generate(emitter, stem),
            output_path(contract.stem),
            contract.stem,
        )
    return rc


def write_all(emitter) -> int:
    rc = 0
    for contract in STUDY_CONTRACTS:
        rc |= emitter.write(
            f"{contract.stem}.schema.json",
            lambda stem=contract.stem: generate(emitter, stem),
            output_path(contract.stem),
        )
    return rc

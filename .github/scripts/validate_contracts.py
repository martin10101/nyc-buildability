#!/usr/bin/env python3
"""Validate canonical contract schemas and fixtures (task M0-T009, defect D3).

Validation layers (never silently weakened; the run banner reports the mode):

1. Baseline: every schema under packages/contracts/schemas parses as JSON and
   declares $schema / $id / title / description; $schema is exactly the
   draft 2020-12 meta-schema URI; $id ends with the file name and contains
   the version directory (e.g. /v1/).
2. Structural meta-schema layer (stdlib, ALWAYS runs): keyword allowlist
   (catches typo keywords such as 'requird', which the draft 2020-12
   meta-schema deliberately ignores), valid 'type' values, 'required' lists
   that reference sibling-defined properties (house rule), enum shapes,
   pattern compilation, numeric keyword sanity, and $ref resolvability
   across the contract set.
3. Engine meta-schema layer: jsonschema.Draft202012Validator.check_schema
   when the 'jsonschema' package is importable. The CI contracts job installs
   nothing, so this layer degrades gracefully to layer 2 alone; which engines
   ran is printed either way.
4. Fixture validation: every fixture under packages/contracts/fixtures/valid/
   <schema>/ must validate against schemas/v1/<schema>.schema.json; every
   fixture under fixtures/invalid/<schema>/ must FAIL validation (an invalid
   fixture that passes is itself a build failure). Instance validation always
   runs on a stdlib mini-validator covering the documented keyword subset;
   when jsonschema is available it runs additionally and any verdict
   disagreement fails the build.
5. Expected-failure meta cases: every schema under
   fixtures/invalid_schemas/ must fail the meta-schema layers.
6. Property-profile invariant (PRD sections 9/19): every fact_value
   provenance_ref in a property_profile fixture must resolve to a
   provenance_id in that profile's provenance array.

Standard library is sufficient; jsonschema only strengthens the run.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = REPO_ROOT / "packages" / "contracts" / "schemas"
FIXTURE_ROOT = REPO_ROOT / "packages" / "contracts" / "fixtures"
REQUIRED_KEYS = ("$schema", "$id", "title", "description")
DRAFT_2020_12 = "https://json-schema.org/draft/2020-12/schema"

# Marker used by the fail-closed legacy $ref guard (M0-T005-R1 item 10) so the
# fixture loop can distinguish a blocked remote fetch from an engine hiccup.
REMOTE_REF_BLOCK_MSG = "remote $ref fetch blocked (fail-closed): target not in the loaded contract store"


# ---------------------------------------------------------------------------
# Shared output-sanitization helper. Kept textually identical in
# .github/scripts/secret_scan.py and .github/scripts/validate_contracts.py:
# both are standalone stdlib scripts and the task scope forbids adding a
# shared module (M0-T005 G5 finding F1 + M0-T009 G5 finding F2).
# ---------------------------------------------------------------------------
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def sanitize_for_log(text: str) -> str:
    """Replace control characters (newline, CR, ESC, NUL, ...) with '?' so a
    hostile filename or value can never start a new log line and forge a
    GitHub workflow command (::notice / ::add-mask / ::error ...)."""
    return _CONTROL_CHARS_RE.sub("?", str(text))


def emit(message: str, *, err: bool = False) -> None:
    """Print one sanitized line to stdout (or stderr)."""
    print(sanitize_for_log(message), file=sys.stderr if err else sys.stdout)

# Keyword allowlist for THIS repository's contracts (subset of draft 2020-12).
# Extending the subset is an additive change: add the keyword here and to the
# mini-validator below in the same commit.
KNOWN_KEYWORDS = {
    "$schema", "$id", "$ref", "$defs", "$comment",
    "title", "description", "default", "examples", "deprecated",
    "type", "enum", "const", "format",
    "pattern", "minLength", "maxLength",
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "required", "properties", "additionalProperties",
    "items", "minItems", "maxItems",
    "anyOf", "allOf", "oneOf",
}
JSON_TYPES = {"object", "array", "string", "number", "integer", "boolean", "null"}
NO_RECURSE_VALUES = {"enum", "const", "default", "examples"}
APPLICATOR_LISTS = ("anyOf", "allOf", "oneOf")


# --------------------------------------------------------------------------
# Optional jsonschema engine
# --------------------------------------------------------------------------

def load_jsonschema_engine():
    """Return (module, version, registry_factory) or (None, reason, None)."""
    try:
        import jsonschema  # type: ignore
    except ImportError as exc:
        return None, f"jsonschema not importable ({exc})", None

    def make_validator(schema, all_docs):
        try:
            from referencing import Registry, Resource  # type: ignore

            resources = [
                (doc["$id"], Resource.from_contents(doc))
                for doc in all_docs
                if isinstance(doc, dict) and "$id" in doc
            ]
            registry = Registry().with_resources(resources)
            return jsonschema.Draft202012Validator(schema, registry=registry)
        except ImportError:
            # Legacy path: jsonschema < 4.18 has no 'referencing' package.
            # This is the LIVE path on the GitHub CI runner (jsonschema
            # 4.10.3, M0-T009 G4 evidence). The stock RefResolver attempts a
            # NETWORK FETCH (requests.get/urlopen) whenever a $ref misses the
            # local store. This contract set has zero remote $refs, so any
            # store miss is a defect in the schemas, never a reason to fetch:
            # resolve_remote() -- the single choke point every scheme funnels
            # through in jsonschema's RefResolver -- is overridden to raise
            # instead (M0-T005-R1 item 10, fail closed).
            class _LocalOnlyRefResolver(jsonschema.RefResolver):
                def resolve_remote(self, uri):
                    raise RuntimeError(f"{REMOTE_REF_BLOCK_MSG}: '{uri}'")

            global _LEGACY_RESOLVER_NOTE_PRINTED
            if not _LEGACY_RESOLVER_NOTE_PRINTED:
                _LEGACY_RESOLVER_NOTE_PRINTED = True
                emit("NOTE: legacy jsonschema RefResolver in use ('referencing' not importable); "
                     "remote $ref fetching is blocked -- any store miss fails closed.")
            store = {
                doc["$id"]: doc
                for doc in all_docs
                if isinstance(doc, dict) and "$id" in doc
            }
            resolver = _LocalOnlyRefResolver(
                base_uri=schema.get("$id", ""), referrer=schema, store=store
            )
            return jsonschema.Draft202012Validator(schema, resolver=resolver)

    return jsonschema, getattr(jsonschema, "__version__", "unknown"), make_validator


_LEGACY_RESOLVER_NOTE_PRINTED = False


# --------------------------------------------------------------------------
# Structural meta-schema layer (stdlib, always on)
# --------------------------------------------------------------------------

def structural_check(doc, base_id, loc, errors, refs):
    """Recursively check one schema object against the house keyword rules."""
    if isinstance(doc, bool):
        return
    if not isinstance(doc, dict):
        errors.append(f"{loc}: schema must be an object or boolean, got {type(doc).__name__}")
        return

    for key in doc:
        if key not in KNOWN_KEYWORDS:
            errors.append(f"{loc}: unknown/unsupported keyword '{key}' (typo? see allowlist in validate_contracts.py)")

    if "type" in doc:
        tval = doc["type"]
        tlist = tval if isinstance(tval, list) else [tval]
        if not tlist or not all(isinstance(t, str) and t in JSON_TYPES for t in tlist):
            errors.append(f"{loc}: invalid 'type' value {tval!r} (must be one of {sorted(JSON_TYPES)})")

    if "enum" in doc:
        if not isinstance(doc["enum"], list) or not doc["enum"]:
            errors.append(f"{loc}: 'enum' must be a non-empty array")

    if "pattern" in doc:
        if not isinstance(doc["pattern"], str):
            errors.append(f"{loc}: 'pattern' must be a string")
        else:
            try:
                re.compile(doc["pattern"])
            except re.error as exc:
                errors.append(f"{loc}: 'pattern' does not compile: {exc}")

    if "required" in doc:
        req = doc["required"]
        if not isinstance(req, list) or not all(isinstance(r, str) for r in req):
            errors.append(f"{loc}: 'required' must be an array of strings")
        else:
            if len(set(req)) != len(req):
                errors.append(f"{loc}: 'required' contains duplicates")
            if "properties" in doc and isinstance(doc["properties"], dict):
                for name in req:
                    if name not in doc["properties"]:
                        errors.append(
                            f"{loc}: required property '{name}' is not defined in sibling 'properties' (house rule)"
                        )

    for kw in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"):
        if kw in doc and (isinstance(doc[kw], bool) or not isinstance(doc[kw], (int, float))):
            errors.append(f"{loc}: '{kw}' must be a number")
    for kw in ("minItems", "maxItems", "minLength", "maxLength"):
        if kw in doc and (isinstance(doc[kw], bool) or not isinstance(doc[kw], int) or doc[kw] < 0):
            errors.append(f"{loc}: '{kw}' must be a non-negative integer")

    if "format" in doc and not isinstance(doc["format"], str):
        errors.append(f"{loc}: 'format' must be a string")

    if "$ref" in doc:
        if not isinstance(doc["$ref"], str):
            errors.append(f"{loc}: '$ref' must be a string")
        else:
            refs.append((base_id, doc["$ref"], loc))

    if "properties" in doc:
        if not isinstance(doc["properties"], dict):
            errors.append(f"{loc}: 'properties' must be an object")
        else:
            for name, sub in doc["properties"].items():
                structural_check(sub, base_id, f"{loc}/properties/{name}", errors, refs)

    if "$defs" in doc:
        if not isinstance(doc["$defs"], dict):
            errors.append(f"{loc}: '$defs' must be an object")
        else:
            for name, sub in doc["$defs"].items():
                structural_check(sub, base_id, f"{loc}/$defs/{name}", errors, refs)

    if "items" in doc:
        structural_check(doc["items"], base_id, f"{loc}/items", errors, refs)

    if "additionalProperties" in doc and not isinstance(doc["additionalProperties"], bool):
        structural_check(doc["additionalProperties"], base_id, f"{loc}/additionalProperties", errors, refs)

    for kw in APPLICATOR_LISTS:
        if kw in doc:
            if not isinstance(doc[kw], list) or not doc[kw]:
                errors.append(f"{loc}: '{kw}' must be a non-empty array of schemas")
            else:
                for i, sub in enumerate(doc[kw]):
                    structural_check(sub, base_id, f"{loc}/{kw}/{i}", errors, refs)


def resolve_ref(ref, base_id, registry):
    """Resolve a $ref against the loaded contract set. Raises KeyError."""
    if ref.startswith("#"):
        target_base, frag = base_id, ref[1:]
    else:
        uri, _, frag = ref.partition("#")
        target_base = urljoin(base_id, uri)
    if target_base not in registry:
        raise KeyError(f"$ref '{ref}': target document '{target_base}' is not a loaded contract")
    node = registry[target_base]
    if frag:
        for raw in frag.split("/")[1:]:
            part = raw.replace("~1", "/").replace("~0", "~")
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                raise KeyError(f"$ref '{ref}': fragment '#{frag}' not found in '{target_base}'")
    return node, target_base


# --------------------------------------------------------------------------
# Stdlib mini instance validator (documented keyword subset)
# --------------------------------------------------------------------------

def json_eq(a, b):
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    return a == b


def type_ok(value, t):
    if t == "object":
        return isinstance(value, dict)
    if t == "array":
        return isinstance(value, list)
    if t == "string":
        return isinstance(value, str)
    if t == "boolean":
        return isinstance(value, bool)
    if t == "null":
        return value is None
    if t == "integer":
        if isinstance(value, bool):
            return False
        return isinstance(value, int) or (isinstance(value, float) and value.is_integer())
    if t == "number":
        return not isinstance(value, bool) and isinstance(value, (int, float))
    return False


def validate_instance(instance, schema, base_id, registry, path="$"):
    """Return a list of error strings (empty = valid)."""
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: schema 'false' permits nothing"]
    if not isinstance(schema, dict):
        return [f"{path}: unusable schema node"]

    errors = []

    if "$ref" in schema:
        try:
            target, target_base = resolve_ref(schema["$ref"], base_id, registry)
        except KeyError as exc:
            return [f"{path}: {exc}"]
        errors.extend(validate_instance(instance, target, target_base, registry, path))

    if "type" in schema:
        tlist = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(type_ok(instance, t) for t in tlist):
            errors.append(f"{path}: expected type {tlist}, got {type(instance).__name__} ({instance!r})")

    if "enum" in schema and not any(json_eq(instance, v) for v in schema["enum"]):
        errors.append(f"{path}: value {instance!r} is not one of the allowed enum values {schema['enum']!r}")

    if "const" in schema and not json_eq(instance, schema["const"]):
        errors.append(f"{path}: value {instance!r} does not equal const {schema['const']!r}")

    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: string {instance!r} does not match pattern {schema['pattern']!r}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: string longer than maxLength {schema['maxLength']}")

    if not isinstance(instance, bool) and isinstance(instance, (int, float)):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} is less than minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} is greater than maximum {schema['maximum']}")
        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: {instance} is not greater than exclusiveMinimum {schema['exclusiveMinimum']}")
        if "exclusiveMaximum" in schema and instance >= schema["exclusiveMaximum"]:
            errors.append(f"{path}: {instance} is not less than exclusiveMaximum {schema['exclusiveMaximum']}")

    if isinstance(instance, dict):
        for name in schema.get("required", []):
            if name not in instance:
                errors.append(f"{path}: missing required property '{name}'")
        props = schema.get("properties", {})
        for name, sub in props.items():
            if name in instance:
                errors.extend(validate_instance(instance[name], sub, base_id, registry, f"{path}.{name}"))
        if "additionalProperties" in schema:
            ap = schema["additionalProperties"]
            extras = [k for k in instance if k not in props]
            if ap is False and extras:
                errors.append(f"{path}: additional properties not allowed: {extras}")
            elif isinstance(ap, dict):
                for k in extras:
                    errors.extend(validate_instance(instance[k], ap, base_id, registry, f"{path}.{k}"))

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: array has fewer than minItems {schema['minItems']}")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: array has more than maxItems {schema['maxItems']}")
        if "items" in schema:
            for i, element in enumerate(instance):
                errors.extend(validate_instance(element, schema["items"], base_id, registry, f"{path}[{i}]"))

    for kw in APPLICATOR_LISTS:
        if kw not in schema:
            continue
        sub_results = [
            validate_instance(instance, sub, base_id, registry, path) for sub in schema[kw]
        ]
        passes = sum(1 for r in sub_results if not r)
        if kw == "anyOf" and passes == 0:
            errors.append(f"{path}: does not satisfy any schema in anyOf")
        elif kw == "allOf" and passes != len(sub_results):
            for r in sub_results:
                errors.extend(r)
        elif kw == "oneOf" and passes != 1:
            errors.append(f"{path}: satisfies {passes} schemas in oneOf (exactly 1 required)")

    return errors


# --------------------------------------------------------------------------
# PRD s19 invariant for property profiles
# --------------------------------------------------------------------------

def profile_provenance_invariant(instance):
    """Every fact_value.provenance_ref must match a provenance_id (PRD s9/s19)."""
    errors = []
    if not isinstance(instance, dict):
        return errors
    ids = {
        rec.get("provenance_id")
        for rec in instance.get("provenance", [])
        if isinstance(rec, dict)
    }
    for section in ("lot_facts", "existing_building_facts"):
        facts = instance.get(section)
        if not isinstance(facts, dict):
            continue
        for name, fact in facts.items():
            if isinstance(fact, dict) and "provenance_ref" in fact:
                if fact["provenance_ref"] not in ids:
                    errors.append(
                        f"$.{section}.{name}: provenance_ref '{fact['provenance_ref']}' does not resolve "
                        "to any provenance_id in the profile's provenance array (PRD s19)"
                    )
    return errors


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def meta_validate_schema(doc, path, base_id, registry, jsonschema_mod, under_schema_root):
    """Run baseline + structural (+ engine) meta checks. Returns error list."""
    errors = []
    refs = []

    if not isinstance(doc, dict):
        return [f"top-level schema must be a JSON object, got {type(doc).__name__}"]

    missing = [key for key in REQUIRED_KEYS if key not in doc]
    if missing:
        errors.append(f"missing top-level keys {missing}")
    if doc.get("$schema") != DRAFT_2020_12:
        errors.append(f"$schema must be '{DRAFT_2020_12}', got {doc.get('$schema')!r}")
    schema_id = doc.get("$id")
    if isinstance(schema_id, str):
        if not schema_id.endswith(path.name):
            errors.append(f"$id must end with the file name '{path.name}', got '{schema_id}'")
        if under_schema_root:
            version_dir = path.relative_to(SCHEMA_ROOT).parts[0]
            if f"/{version_dir}/" not in schema_id:
                errors.append(f"$id must contain the version directory '/{version_dir}/'")
    else:
        errors.append("$id must be a string")

    structural_check(doc, base_id, "#", errors, refs)
    for ref_base, ref, loc in refs:
        try:
            resolve_ref(ref, ref_base, registry)
        except KeyError as exc:
            errors.append(f"{loc}: {exc}")

    if jsonschema_mod is not None:
        try:
            jsonschema_mod.Draft202012Validator.check_schema(doc)
        except jsonschema_mod.exceptions.SchemaError as exc:
            errors.append(f"meta-schema (jsonschema): {exc.message}")

    return errors


def main() -> int:
    failures = 0

    if not SCHEMA_ROOT.is_dir():
        emit(f"ERROR: schema root not found: {SCHEMA_ROOT}", err=True)
        return 1
    schema_files = sorted(SCHEMA_ROOT.rglob("*.json"))
    if not schema_files:
        emit(f"ERROR: no schema files found under {SCHEMA_ROOT}", err=True)
        return 1

    jsonschema_mod, jsonschema_note, make_validator = load_jsonschema_engine()
    if jsonschema_mod is not None:
        emit(f"meta-schema engines : stdlib-structural + jsonschema {jsonschema_note}")
        emit(f"instance engines    : stdlib mini-validator + jsonschema {jsonschema_note} (cross-checked)")
    else:
        emit(f"meta-schema engines : stdlib-structural ONLY ({jsonschema_note})")
        emit("instance engines    : stdlib mini-validator ONLY")
        emit("NOTE: degraded mode is still strict (allowlist + required/properties + $ref + pattern checks).")

    # ---- load all contract schemas and index by $id -----------------------
    docs = {}
    registry = {}
    for schema_file in schema_files:
        try:
            doc = load_json(schema_file)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            emit(f"FAIL {schema_file.relative_to(REPO_ROOT)}: does not parse as JSON: {exc}", err=True)
            failures += 1
            continue
        docs[schema_file] = doc
        if isinstance(doc, dict) and isinstance(doc.get("$id"), str):
            if doc["$id"] in registry:
                emit(f"FAIL {schema_file.relative_to(REPO_ROOT)}: duplicate $id '{doc['$id']}'", err=True)
                failures += 1
            registry[doc["$id"]] = doc

    # ---- phase 1+2+3: meta-validate every contract schema -----------------
    for schema_file, doc in docs.items():
        rel = schema_file.relative_to(REPO_ROOT)
        base_id = doc.get("$id") if isinstance(doc, dict) else None
        errors = meta_validate_schema(doc, schema_file, base_id or "", registry, jsonschema_mod, True)
        if errors:
            failures += 1
            for err in errors:
                emit(f"FAIL {rel}: {err}", err=True)
        else:
            emit(f"OK   {rel} ({doc['title']})")

    # ---- phase 4: fixtures -------------------------------------------------
    def schema_for_stem(stem):
        path = SCHEMA_ROOT / "v1" / f"{stem}.schema.json"
        return path if path in docs else None

    def run_instance_validation(instance, schema_doc, all_docs):
        mini_errors = validate_instance(instance, schema_doc, schema_doc.get("$id", ""), registry)
        engine_errors = None
        if jsonschema_mod is not None and make_validator is not None:
            try:
                validator = make_validator(schema_doc, list(all_docs))
                engine_errors = [e.message for e in validator.iter_errors(instance)]
            except Exception as exc:  # noqa: BLE001 - degrade loudly, never crash the gate
                if REMOTE_REF_BLOCK_MSG in str(exc):
                    # Fail-closed $ref guard tripped: this is a real error in
                    # the contract set, not an engine hiccup -- surface it as
                    # an engine verdict so the fixture loop records a failure.
                    engine_errors = [f"fail-closed $ref guard: {exc}"]
                else:
                    engine_errors = None
                    emit(f"NOTE: jsonschema instance engine unavailable for this schema ({exc}); "
                         "stdlib mini-validator verdict used.")
        return mini_errors, engine_errors

    for expectation in ("valid", "invalid"):
        base = FIXTURE_ROOT / expectation
        if not base.is_dir():
            continue
        for fixture in sorted(base.rglob("*.json")):
            rel = fixture.relative_to(REPO_ROOT)
            stem = fixture.parent.name
            schema_path = schema_for_stem(stem)
            if schema_path is None:
                emit(f"FAIL {rel}: no schema 'schemas/v1/{stem}.schema.json' for fixture directory", err=True)
                failures += 1
                continue
            try:
                instance = load_json(fixture)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                emit(f"FAIL {rel}: does not parse as JSON: {exc}", err=True)
                failures += 1
                continue

            schema_doc = docs[schema_path]
            mini_errors, engine_errors = run_instance_validation(instance, schema_doc, docs.values())

            if engine_errors is not None and bool(engine_errors) != bool(mini_errors):
                failures += 1
                emit(f"FAIL {rel}: validator disagreement — mini={mini_errors!r} jsonschema={engine_errors!r}",
                     err=True)
                continue

            all_errors = list(mini_errors)
            if stem == "property_profile":
                all_errors.extend(profile_provenance_invariant(instance))

            if expectation == "valid":
                if all_errors:
                    failures += 1
                    for err in all_errors:
                        emit(f"FAIL {rel}: {err}", err=True)
                else:
                    emit(f"OK   {rel} (valid fixture passes {stem})")
            else:
                if all_errors:
                    emit(f"OK   {rel} (invalid fixture correctly rejected: {all_errors[0]})")
                else:
                    failures += 1
                    emit(f"FAIL {rel}: fixture in 'invalid/' unexpectedly PASSED validation against {stem}",
                         err=True)

    # ---- phase 5: expected-failure meta-schema cases -----------------------
    invalid_schemas_dir = FIXTURE_ROOT / "invalid_schemas"
    if invalid_schemas_dir.is_dir():
        for schema_file in sorted(invalid_schemas_dir.glob("*.json")):
            rel = schema_file.relative_to(REPO_ROOT)
            try:
                doc = load_json(schema_file)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                emit(f"OK   {rel} (broken schema correctly rejected: does not parse: {exc})")
                continue
            base_id = doc.get("$id", "") if isinstance(doc, dict) else ""
            local_registry = dict(registry)
            if base_id:
                local_registry[base_id] = doc
            errors = meta_validate_schema(doc, schema_file, base_id, local_registry, jsonschema_mod, False)
            if errors:
                emit(f"OK   {rel} (broken schema correctly rejected: {errors[0]})")
            else:
                failures += 1
                emit(f"FAIL {rel}: schema in 'invalid_schemas/' unexpectedly PASSED meta validation", err=True)

    emit(f"Checked {len(schema_files)} schema file(s); {failures} failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

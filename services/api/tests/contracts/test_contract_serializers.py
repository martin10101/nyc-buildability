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
import re
import textwrap
from pathlib import Path

import pytest

from app.contracts.serializers import (
    ANALYSIS_STATE_TRANSITION_SERIALIZER,
    SOURCE_FACT_SERIALIZER,
    AllowlistSerializer,
    ContractSerializationError,
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


# Request E-2 scoped both guards to the SERIALIZER. The M2-T018 form matched
# any ``app.contracts`` import or text, so a producer calling the C-03 study
# validators (``app.contracts.study_contracts``) turned them red without ever
# touching the serializer. Only a proven serializer-free contracts submodule is
# exempt; everything else that could yield the serializer still fails closed:
# ``app.contracts.serializers``, the ``app.contracts`` package object itself
# (its public interface IS the serializer re-export), a star import of it, any
# serializer name imported from any module, and any unproven submodule.
CONTRACTS_PACKAGE = "app.contracts"
CONTRACTS_DIR = APP_DIR / "contracts"

# Everything ``app.contracts`` re-exports from ``serializers.py`` (pinned
# against both files by test_serializer_names_are_the_package_reexports).
SERIALIZER_NAMES = frozenset(
    {
        "AllowlistSerializer",
        "ContractSerializationError",
        "UnknownFieldError",
        "MissingFieldError",
        "SOURCE_FACT_SERIALIZER",
        "ANALYSIS_STATE_TRANSITION_SERIALIZER",
    }
)
_SERIALIZER_NAME_RE = re.compile(r"\b(?:" + "|".join(sorted(SERIALIZER_NAMES)) + r")\b")


def _package_of(py: Path) -> str:
    """The ``__package__`` of a module under ``app/`` (for relative imports)."""
    parts = py.relative_to(APP_DIR.parent).with_suffix("").parts
    return ".".join(parts[:-1])


def _resolve(node: ast.ImportFrom, package: str) -> str:
    """The absolute module an ``ImportFrom`` reads from, resolving relative
    levels against the importing module's package as the import system does."""
    if not node.level:
        return node.module or ""
    base = package.split(".")[: len(package.split(".")) - (node.level - 1)]
    return ".".join([*base, *([node.module] if node.module else [])])


def _yields_serializer(dotted: str, allowed: frozenset[str]) -> bool:
    """True for an import target that can hand over the serializer: the
    ``app.contracts`` package itself, or any submodule of it not in
    ``allowed`` (``serializers`` never is; unknown ones fail closed)."""
    if dotted == CONTRACTS_PACKAGE:
        return True
    if not dotted.startswith(CONTRACTS_PACKAGE + "."):
        return False
    return dotted[len(CONTRACTS_PACKAGE) + 1 :].split(".")[0] not in allowed


def _imports_serializer(tree: ast.AST, package: str, allowed: frozenset[str]) -> bool:
    """True when the module really IMPORTS the serializer (AST, so a mention
    inside a docstring or comment is not mistaken for wiring)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = _resolve(node, package)
            names = [alias.name for alias in node.names]
            if SERIALIZER_NAMES.intersection(names):
                return True  # a serializer name, whichever module re-exports it
            if "*" in names:
                # A star import of app.contracts (or of an ancestor that binds it).
                if CONTRACTS_PACKAGE.startswith(module + ".") or _yields_serializer(
                    module, allowed
                ):
                    return True
                continue
            targets = [f"{module}.{name}" for name in names]
        else:
            continue
        if any(_yields_serializer(target, allowed) for target in targets):
            return True
    return False


def _docstring_ids(tree: ast.AST) -> set[int]:
    return {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    }


def _references_serializer(source: str, allowed: frozenset[str]) -> bool:
    """Textual companion to the import check. Whole text (docstrings and
    comments included, as in M2-T018): ``contracts.serializers`` anywhere, and
    ``app.contracts`` anywhere unless it names an allowed submodule - catches a
    dynamic ``importlib.import_module('app.contracts.serializers')``. Code only:
    a serializer name as an identifier, attribute or non-docstring string
    (``getattr(mod, "SOURCE_FACT_SERIALIZER")``); a docstring that merely names
    it, like ``app/profile/wave_integration.py``'s, is not a use."""
    exempt = "|".join(re.escape(stem) for stem in sorted(allowed))
    package_re = r"app\.contracts" + (
        # ``.<exempt>``, or a whole-line ``import <exempt> [as name]`` (so
        # ``import study_contracts, serializers`` still matches).
        rf"(?!\.(?:{exempt})\b|[ \t]+import[ \t]+(?:{exempt})(?:[ \t]+as[ \t]+\w+)?[ \t]*(?:#.*)?$)"
        if exempt
        else ""
    )
    if "contracts.serializers" in source or re.search(package_re, source, re.MULTILINE):
        return True
    tree = ast.parse(source)
    docstrings = _docstring_ids(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            words = [node.id]
        elif isinstance(node, ast.Attribute):
            words = [node.attr]
        elif isinstance(node, ast.alias):
            words = [node.name.rsplit(".", 1)[-1], node.asname or ""]
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstrings and _SERIALIZER_NAME_RE.search(node.value):
                return True
            continue
        else:
            continue
        if SERIALIZER_NAMES.intersection(words):
            return True
    return False


def _non_serializer_contract_modules(contracts_dir: Path = CONTRACTS_DIR) -> frozenset[str]:
    """The ``app.contracts`` submodules production code may import: every
    module except ``__init__`` (re-exports the serializer) and ``serializers``,
    minus any that reaches the serializer itself or through a sibling that
    does, so an exempt module can never launder it past the guard. Iterated
    to a fixpoint: dropping one module can expose a sibling that imports it."""
    sources = {
        py.stem: py.read_text(encoding="utf-8")
        for py in sorted(contracts_dir.glob("*.py"))
        if py.stem not in {"__init__", "serializers"}
    }
    allowed = frozenset(sources)
    while True:
        kept = frozenset(
            stem
            for stem in allowed
            if not _imports_serializer(ast.parse(sources[stem]), CONTRACTS_PACKAGE, allowed)
            and not _references_serializer(sources[stem], allowed)
        )
        if kept == allowed:
            return allowed
        allowed = kept


def test_serializer_imported_exactly_at_the_profile_write_boundary() -> None:
    """Exactly one production module imports the serializer, and it is the
    profile builder. Fewer means the fail-closed boundary was lost; more means
    a second component is serializing provenance outside the single boundary
    (both are M2-T018 regressions)."""
    allowed = _non_serializer_contract_modules()
    importers = [
        _repo_path(py)
        for py in _production_modules()
        if _imports_serializer(ast.parse(py.read_text(encoding="utf-8")), _package_of(py), allowed)
    ]
    assert importers == [BOUNDARY_MODULE], (
        "the allowlist serializer must be imported at exactly the profile "
        f"write boundary ({BOUNDARY_MODULE}); found: {importers}"
    )


def test_no_other_production_module_even_references_the_serializer() -> None:
    """Textual companion to the AST check: catches a dynamic
    ``importlib.import_module('app.contracts.serializers')`` or any other
    string-based reach for the serializer from outside the boundary."""
    allowed = _non_serializer_contract_modules()
    referencing = [
        _repo_path(py)
        for py in _production_modules()
        if _references_serializer(py.read_text(encoding="utf-8"), allowed)
    ]
    assert referencing == [BOUNDARY_MODULE], (
        "only the profile write boundary may reference the serializer; "
        f"found: {referencing}"
    )


# --- E-2: the scoped guard, proven on synthetic modules -------------------

# Where a synthetic module notionally lives (the E-01 drawing kit's package).
_SYNTHETIC_PACKAGE = "app.drawings.kit"


def test_serializer_names_are_the_package_reexports() -> None:
    """SERIALIZER_NAMES is exactly what ``app.contracts`` re-exports, and each
    is a serializer or serializer error defined in ``serializers.py``: a new
    re-export must be added here before it can slip past the guard."""
    import app.contracts
    from app.contracts import serializers

    init_tree = ast.parse((CONTRACTS_DIR / "__init__.py").read_text(encoding="utf-8"))
    reexported = {
        alias.name
        for node in ast.walk(init_tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert reexported == set(app.contracts.__all__) == SERIALIZER_NAMES
    for name in SERIALIZER_NAMES:
        value = getattr(serializers, name)
        assert isinstance(value, AllowlistSerializer) or (
            isinstance(value, type)
            and issubclass(value, (AllowlistSerializer, ContractSerializationError))
        ), name


def test_study_contracts_is_the_proven_non_serializer_submodule() -> None:
    # The contract-validation / bridge modules (study_contracts C-03, evaluator_inputs
    # C-07, compare_rows C-09, study_setup_bridge C-07 adapter) never reach the
    # provenance serializer; they are the proven exempt submodules.
    assert _non_serializer_contract_modules() == {
        "study_contracts",
        "evaluator_inputs",
        "compare_rows",
        "study_setup_bridge",
    }


def test_a_contracts_submodule_that_reaches_the_serializer_is_not_exempt(
    tmp_path: Path,
) -> None:
    """Directly, relatively, by name, or through a sibling that does."""
    modules = {
        "__init__": "from app.contracts.serializers import AllowlistSerializer\n",
        "serializers": "class AllowlistSerializer: ...\n",
        "clean": "def validate(doc):\n    return doc\n",
        "direct": "from .serializers import SOURCE_FACT_SERIALIZER as S\n",
        "by_name": "import app\nWRITE = app.SOURCE_FACT_SERIALIZER\n",
        "via_sibling": "from app.contracts.direct import S\n",
        "via_sibling_of_sibling": "from . import via_sibling\n",
    }
    for stem, source in modules.items():
        (tmp_path / f"{stem}.py").write_text(source, encoding="utf-8")
    assert _non_serializer_contract_modules(tmp_path) == {"clean"}


_ALLOWED_SOURCES = {
    "study_contracts_from_import": '''
        """Validates through
        :func:`app.contracts.study_contracts.validate_results_document`."""
        from app.contracts.study_contracts import StudyContractError, validate_results_document
    ''',
    "study_contracts_submodule": "from app.contracts import study_contracts  # C-03\n",
    "study_contracts_submodule_as": "from app.contracts import study_contracts as sc\n",
    "study_contracts_import_as": "import app.contracts.study_contracts as sc\n",
    "study_contracts_relative": "from ...contracts.study_contracts import StudyContractError\n",
    "study_contracts_importlib": """
        import importlib
        importlib.import_module("app.contracts.study_contracts")
    """,
    "serializer_named_in_docstring_only": '''
        """Its records pass the frozen ``SOURCE_FACT_SERIALIZER`` in the builder."""
        # comments naming UnknownFieldError are not uses either
    ''',
}


@pytest.mark.parametrize("source", _ALLOWED_SOURCES.values(), ids=_ALLOWED_SOURCES.keys())
def test_a_non_serializer_contracts_import_passes_both_guards(source: str) -> None:
    source = textwrap.dedent(source)
    allowed = _non_serializer_contract_modules()
    assert not _imports_serializer(ast.parse(source), _SYNTHETIC_PACKAGE, allowed)
    assert not _references_serializer(source, allowed)


# route -> (source, caught by the import guard, caught by the reference guard).
# Every route the M2-T018 guard caught is caught by the same guard(s) here; the
# relative, ``from app import contracts`` and laundering rows were blind spots.
_SERIALIZER_ROUTES = {
    "serializers_module_from": ("from app.contracts.serializers import X\n", True, True),
    "serializers_module_import": ("import app.contracts.serializers as s\n", True, True),
    "serializers_submodule": ("from app.contracts import serializers\n", True, True),
    "serializers_beside_exempt": (
        "from app.contracts import study_contracts, serializers\n",
        True,
        True,
    ),
    "package_star": ("from app.contracts import *\n", True, True),
    "ancestor_star": ("from app import *\ncontracts.SOURCE_FACT_SERIALIZER\n", True, True),
    "package_import": ("import app.contracts\n", True, True),
    "package_alias_attribute": ("import app.contracts as c\nc.AllowlistSerializer\n", True, True),
    "package_from_app": ("from app import contracts\ncontracts.UnknownFieldError\n", True, True),
    "unproven_submodule": ("from app.contracts.new_module import f\n", True, True),
    "reexport_via_exempt_submodule": (
        "from app.contracts.study_contracts import AllowlistSerializer\n",
        True,
        True,
    ),
    "laundered_through_boundary": (
        "from app.profile.builder import SOURCE_FACT_SERIALIZER\n",
        True,
        True,
    ),
    "relative_serializers_from": (
        "from ...contracts.serializers import SOURCE_FACT_SERIALIZER\n",
        True,
        True,
    ),
    "relative_serializers_submodule": ("from ...contracts import serializers\n", True, False),
    "relative_package": ("from ... import contracts\n", True, False),
    "importlib_serializers": (
        'import importlib\nimportlib.import_module("app.contracts.serializers")\n',
        False,
        True,
    ),
    "importlib_package": (
        'import importlib\nimportlib.import_module("app.contracts")\n',
        False,
        True,
    ),
    "importlib_relative": (
        'import importlib\nimportlib.import_module(".serializers", "app.contracts")\n',
        False,
        True,
    ),
    "getattr_string": (
        'import sys\ngetattr(sys.modules["app.contracts.study_contracts"], "MissingFieldError")\n',
        False,
        True,
    ),
}


@pytest.mark.parametrize(
    "source, by_import, by_reference", _SERIALIZER_ROUTES.values(), ids=_SERIALIZER_ROUTES.keys()
)
def test_every_serializer_import_route_still_fails_the_guard(
    source: str, by_import: bool, by_reference: bool
) -> None:
    allowed = _non_serializer_contract_modules()
    assert _imports_serializer(ast.parse(source), _SYNTHETIC_PACKAGE, allowed) is by_import
    assert _references_serializer(source, allowed) is by_reference


@pytest.mark.parametrize("name", sorted(SERIALIZER_NAMES))
@pytest.mark.parametrize("module", ["app.contracts", "app.contracts.serializers"])
def test_each_serializer_name_fails_both_guards(module: str, name: str) -> None:
    source = f"from {module} import {name} as renamed\n"
    allowed = _non_serializer_contract_modules()
    assert _imports_serializer(ast.parse(source), _SYNTHETIC_PACKAGE, allowed)
    assert _references_serializer(source, allowed)


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

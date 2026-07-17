"""Regression guard for the M2-T003 rework: the property API must load its
canonical contract schemas from PACKAGE DATA (importlib.resources), NOT from a
repo-relative ``packages/contracts`` filesystem walk.

The original defect (CI web-e2e job): the API is installed non-editable
(``pip install ./services/api``); ``app/`` then lives in site-packages with no
sibling ``packages/`` directory, so ``Path(__file__).parents[4] / "packages"``
raised ``FileNotFoundError`` at import of ``app.profile.contract``. These tests
prove the schema now loads the way an installed package loads it, and that no
``packages/``-relative runtime path remains in the module.
"""

from __future__ import annotations

import ast
from importlib import resources
from pathlib import Path

from app.profile import contract as contract_module
from app.profile.contract import SUPPORTED_CONTRACT_VERSIONS

_BUNDLED_PACKAGE = "app._contract_schemas.v1"
_SCHEMA_FILES = (
    "property_profile.schema.json",
    "source_fact.schema.json",
    "common.schema.json",
    "coverage_status.schema.json",
)


def test_all_four_schemas_load_via_importlib_resources() -> None:
    """Load each schema the way the INSTALLED package does — through the
    importlib.resources traversable, not a repo-relative path. This is the path
    the harness/production runtime uses; if it works here it works in
    site-packages."""
    root = resources.files(_BUNDLED_PACKAGE)
    for name in _SCHEMA_FILES:
        text = root.joinpath(name).read_text(encoding="utf-8")
        assert text.strip().startswith("{"), f"{name} is not JSON"


def test_supported_versions_populated_without_packages_relative_access() -> None:
    """``SUPPORTED_CONTRACT_VERSIONS`` is computed at import from the bundled
    schema. It must be populated, proving import succeeded without any
    ``packages/``-relative filesystem access."""
    assert SUPPORTED_CONTRACT_VERSIONS == ("1.0.0", "1.1.0", "1.2.0", "1.3.0")


def test_module_helper_loads_bundled_schema() -> None:
    """The private loader resolves via importlib.resources and returns the
    parsed canonical schema (has the profile_version.contract_version enum)."""
    schema = contract_module._load_bundled_schema("property_profile.schema.json")
    enum = schema["properties"]["profile_version"]["properties"]["contract_version"]["enum"]
    assert enum == ["1.0.0", "1.1.0", "1.2.0", "1.3.0"]


def test_contract_module_has_no_packages_relative_runtime_path() -> None:
    """Static guard: the module source must not resolve schemas via a
    repo-relative ``__file__`` walk into ``packages/contracts``. This is the
    specific regression - a RUNTIME read of a sibling packages/ directory that
    does not exist in a non-editable install."""
    source = Path(contract_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Collect docstring nodes (module + every function/class): prose may
    # legitimately explain the canonical packages/contracts authority. We guard
    # against CODE that reads it at runtime, not documentation of the design.
    docstring_nodes: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            doc = ast.get_docstring(node, clean=False)
            if doc is not None and node.body:
                first = node.body[0]
                if (
                    isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)
                ):
                    docstring_nodes.add(id(first.value))

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstring_nodes
        ):
            assert "packages/contracts" not in node.value, (
                "contract.py must not reference packages/contracts in a runtime "
                "string; schemas are loaded from bundled package data"
            )
        # No repo-relative filesystem walk to locate schemas.
        if isinstance(node, ast.Attribute) and node.attr == "parents":
            raise AssertionError(
                "contract.py must not use Path(...).parents[...] to locate "
                "schemas; use importlib.resources on the bundled package"
            )

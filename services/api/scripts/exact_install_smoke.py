#!/usr/bin/env python3
"""Exact-production-install smoke (task M0-T018).

Proves the EXACT Render production dependency set (installed via
`pip install -r requirements.txt`) can:

  1. import and create the real FastAPI app (app.main.create_app), and
  2. run app/profile/contract.py::validate_profile on a committed valid
     property-profile fixture.

Because contract.py imports ``jsonschema`` lazily *inside* validate_profile,
merely creating the app or hitting /health does NOT exercise the runtime
dependency. This smoke calls validate_profile directly so a missing runtime
jsonschema fails LOUDLY.

Modes
-----
  (default)   POSITIVE: validate_profile must SUCCEED. Exit 0 on success.
  --expect-missing-jsonschema
              NEGATIVE: jsonschema must be absent, so validate_profile must
              FAIL with ModuleNotFoundError('jsonschema'). Exit 0 only when the
              expected failure occurs; exit 1 if validate_profile unexpectedly
              succeeds (which would mean the smoke does not actually exercise
              the runtime import).

The negative mode is what proves the CI gate genuinely tests validate_profile
rather than just a health endpoint.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Repo layout: <repo>/services/api/scripts/exact_install_smoke.py
API_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = API_DIR.parents[1]
FIXTURE = (
    REPO_ROOT
    / "packages"
    / "contracts"
    / "fixtures"
    / "valid"
    / "property_profile"
    / "full_example.json"
)


def _load_fixture() -> dict:
    if not FIXTURE.exists():
        print(f"SMOKE ERROR: fixture not found: {FIXTURE}", file=sys.stderr)
        sys.exit(2)
    with FIXTURE.open(encoding="utf-8") as fh:
        return json.load(fh)


def run_positive() -> int:
    # 1. import + create the real app (exercises fastapi/starlette/uvicorn deps)
    from app.main import create_app

    app = create_app()
    assert app is not None, "create_app() returned None"

    # 2. call validate_profile on a committed valid fixture (exercises the
    #    lazy runtime `import jsonschema` at contract.py).
    from app.profile.contract import validate_profile

    profile = _load_fixture()
    validate_profile(profile)  # raises on any defect; None on success

    print("SMOKE OK (positive): create_app() built the app and "
          "validate_profile() accepted the valid fixture "
          f"({FIXTURE.name}). jsonschema runtime import exercised.")
    return 0


def run_negative() -> int:
    """jsonschema must be ABSENT; validate_profile must raise ModuleNotFoundError."""
    try:
        import jsonschema  # noqa: F401
    except ModuleNotFoundError:
        pass
    else:
        print("SMOKE FAIL (negative): jsonschema is importable, but this mode "
              "requires it to be uninstalled to prove the gate exercises the "
              "runtime import.", file=sys.stderr)
        return 1

    from app.profile.contract import validate_profile

    profile = _load_fixture()
    try:
        validate_profile(profile)
    except ModuleNotFoundError as exc:
        if "jsonschema" in str(exc):
            print("SMOKE OK (negative): with jsonschema removed, "
                  "validate_profile() raised ModuleNotFoundError as expected "
                  f"-> {exc!r}. This proves the exact-install gate genuinely "
                  "exercises validate_profile (not just a health endpoint).")
            return 0
        print(f"SMOKE FAIL (negative): unexpected ModuleNotFoundError: {exc!r}",
              file=sys.stderr)
        return 1
    else:
        print("SMOKE FAIL (negative): validate_profile() SUCCEEDED without "
              "jsonschema installed. The smoke does NOT exercise the runtime "
              "import, or jsonschema is bundled elsewhere. This is the exact "
              "defect the gate must catch.", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expect-missing-jsonschema",
        action="store_true",
        help="negative mode: require jsonschema absent and validate_profile to fail",
    )
    args = parser.parse_args()
    return run_negative() if args.expect_missing_jsonschema else run_positive()


if __name__ == "__main__":
    raise SystemExit(main())

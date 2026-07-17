"""Runtime-bundled canonical contract schemas (package data).

These JSON files are BUILD ARTIFACTS copied byte-for-byte from the canonical
source ``packages/contracts/schemas/v1/*.schema.json`` by
``services/api/scripts/sync_contract_schemas.py`` and kept provably in sync by
the ``contracts-schema-bundle`` CI drift check. They are shipped inside the
installed ``app`` package so a non-editable install (web-e2e CI, production
image) can load them via ``importlib.resources`` WITHOUT a sibling
``packages/`` directory. Do not hand-edit; regenerate with the sync script.
"""

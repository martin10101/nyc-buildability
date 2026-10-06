"""Zoning-rule review register (M4-T023, D-090 source-042).

A permanent, structured record of every zoning rule the program implements: the
law it rests on, where it applies and its exceptions, the program's plain-English
interpretation, one worked example (inputs, the independently-worked expected
answer with its basis, and the answer the program actually gives), the code and
tests, a revision, an append-only history, and a human-verdict field that only a
named human reviewer's own answer may fill.

- ``register.json`` is the authored source (fixed field names and value sets, a
  stable ``entry_id`` equal to the rule id, so it can move into a database table
  later - no database work now).
- ``render_review_register.py`` renders the Markdown under
  ``docs/zoning-rule-review/`` (``--write``) and validates the data (``--check``).
- ``check_review_register.py`` is the stdlib validator used by ``--check`` and by
  the test suite.

This is a review record, not a sign-off gate: nothing in the program waits for a
verdict (ADR-007).
"""

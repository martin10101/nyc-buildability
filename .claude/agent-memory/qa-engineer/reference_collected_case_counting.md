---
name: collected-case-counting
description: How to statically recompute pytest collected-case counts (parametrize expansion) during a G4 wave without running pytest
metadata:
  type: reference
---

Recomputing a pack's collected-case count by AST (the read-only way to verify a
producer's red/green numbers under ADR-005, since reviewers must not run pytest):

- Walk `ast.parse(src).body` for `FunctionDef` whose name starts with `test_`; base count 1 each.
- For each decorator that is an `ast.Call` whose unparsed func contains `parametrize`,
  the case multiplier = `len(argvalues)` (the 2nd positional arg).
- TRAP: `ast.literal_eval` of the argvalues FAILS when they reference module-level
  names (e.g. `list(_FLAT_RULES)`, or a list of tuples containing a name like
  `_CONDITIONAL_RULE`). A naive literal_eval-only counter silently counts those as x1
  and UNDERCOUNTS. Fix: `eval(ast.unparse(argvalues), {}, ns)` with `ns` binding the
  referenced module-level names (read them from the same module's assignments).
- Cross-check against the producer's RED `-k` record: (selected + deselected) must
  equal the module's total collected cases.

Worked example (M4-T009, 2026-09-11, HEAD 032dffe7): main pack
`test_r1_r12_residential_far.py` = 15 (no parametrize); provenance pack
`test_r1_r12_residential_far_provenance.py` = 17 (three parametrized tests: x4 over
`list(_FLAT_RULES)`, and x2, x2 over tuple lists naming `_CONDITIONAL_RULE`). The 17
reconciled the addendum's RED "1 selected + 16 deselected". A literal_eval-only counter
reported 12 — the undercount trap above.

Related: [[git-show-frozen-sha-review]].

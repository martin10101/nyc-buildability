---
paths:
  - "services/**/*.py"
  - "tools/**/*.py"
  - "packages/**/*.py"
  - "apps/web/src/**/*.ts"
  - "apps/web/src/**/*.tsx"
---
# Code architecture — permanent modularity rule (M0-T073; policy: docs/CODE_MODULARITY_POLICY.md)

Auto-loads when editing handwritten production source. Compact by design;
depth, examples, thresholds, and the exception process live in the policy doc.

Before adding substantial code:

1. **Inspect the target file first** — its size, responsibilities, dependencies.
2. **Identify the owning responsibility and module boundary**; do not append
   unrelated behavior merely because a convenient file exists.
3. **Separate** domain logic, persistence, serialization, external I/O, API/CLI
   wiring, and presentation when they change for different reasons.
4. **Extract with tests**: add focused tests for behavior you move, preserve
   existing public interfaces (thin compatibility facades where appropriate),
   and avoid circular dependencies.
5. **No dumping grounds**: no giant `utils.py`, `helpers.py`, `common.ts`, or
   miscellaneous modules.
6. **Crossing a threshold?** (warn 600 / justify 750 / hard 1,000 SLOC): record
   WHY the file remains cohesive in the review, or split it. New files above
   the hard threshold fail CI without a reviewed, expiring, path-exact
   exception (`tools/modularity_exceptions.json`).
7. **Run the checker before submitting a checkpoint**:
   `python tools/modularity_check.py --check` (report view: `--report`).

Line count is a signal, never a verdict — and a passing count never excuses
responsibility mixing or hidden coupling; reviewers judge the actual diff.

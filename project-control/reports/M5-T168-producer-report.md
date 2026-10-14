# M5-T168 producer report — ruff reads the rules coverage renderer (DB-240)

Task: make `cd services/api && python -m ruff check .` (the api CI job's first step) read
`services/api/app/rules/coverage/render_coverage_matrix.py`, and fix its two findings
(F841 unused `column_order` at :70; E501 at :94) with no change in behaviour.

Builder: backend-engineer. Worktree:
`/root/project/nyc-buildability/.claude/worktrees/agent-ae883906a992ffbb3`.
Claim head: `aac892fcde5dc035848af9bf99f7cea0bc8edec2` (`task/wave24-report-v3`).
Ruff used for evidence: `/root/project/lanes-runtime/venv/bin/ruff` (ruff 0.13.0, satisfies
`ruff>=0.6,<1`); pytest 9.0.3 from the same venv.

## Which file was changed and why: `services/api/pyproject.toml` ([tool.ruff]), NOT `.gitignore`

I added `respect-gitignore = false` to `[tool.ruff]`. `.gitignore` is left byte-unchanged.

Root cause (measured, not assumed). The root `.gitignore` has `coverage/` (line 20, an
unanchored basename rule matching any dir named `coverage` at any depth) and
`!services/api/app/rules/coverage/` (line 22). Git honours the re-include and tracks the
folder. Ruff does not, and the reason is specific: when `ruff check .` runs from the
`services/api` cwd, ruff relativises the repo-root `.gitignore` rules to its walk root and
**basename-matches `coverage`**, so the tracked source dir `app/rules/coverage/` is pruned.

I proved `.gitignore` cannot fix this without breaking S4:

- `!services/api/app/rules/coverage/` and `!services/api/app/rules/coverage/**` — ruff still
  prunes (a negation cannot un-prune a matched directory in ruff's ignore handling).
- Anchored `/services/api/coverage/` (and `services/api/coverage/`, `/services/api/coverage`)
  — all still prune the source. Discriminators: `/zzz/qqq/coverage/` does **not** prune, and
  `services/api/foobar/` does **not** prune. So the trigger is a rule under the `services/api/`
  walk-root prefix whose leaf is `coverage` (the source's own leaf): ruff strips the
  `services/api/` prefix, leaving the basename `coverage` → prune.
- S4 requires `services/api/coverage/` to stay git-ignored. Every root-`.gitignore` rule that
  keeps it ignored (generic `coverage/`, or anchored `services/api/coverage/`) reduces to the
  basename `coverage` for ruff and therefore also prunes the sibling source. So S1 (ruff reads
  the source) and S4 (git still ignores `services/api/coverage/`) cannot both hold via
  `.gitignore`. The fix must live in `pyproject.toml`.

Why `respect-gitignore = false` and not a narrower ruff key:

- `extend-include = ["app/rules/coverage/*.py"]` does **not** override gitignore pruning
  (tested: still NOT listed).
- `respect-gitignore = false` is the only ruff lever that makes ruff read the folder. Measured
  breadth: ruff's discovered-file list grew from 703 to 704 — the single added file is exactly
  `render_coverage_matrix.py`. Nothing else is un-ignored in this checkout; ruff's built-in
  excludes still cover `venv`/`__pycache__`/`build`/`dist`/`.*_cache`, and real coverage-tool
  output contains no `.py`.
- I deliberately did NOT add `extend-exclude` to re-exclude coverage dirs: ruff's exclude
  matching is basename/anchor-surprising (`coverage` excludes the source too; `/coverage/` did
  not exclude the artefact; only the fragile `coverage/` form happened to work here). A
  wrong-direction change there would silently re-exclude the source and re-break the gate —
  exactly the DB-240 failure. `respect-gitignore = false` alone guarantees every tracked `.py`
  is read, which is the gate's purpose.

## The two findings (no behaviour change)

- F841: removed the unused `column_order = matrix["column_order"]` (only occurrence; grep-confirmed).
- E501 (:94, 113 chars): wrapped the `lines.append(...)` string header into two adjacent string
  literals that concatenate to the identical text.

Behaviour proof — rendered matrix byte-identical before and after:

- committed `COVERAGE_MATRIX.md` sha256 = `42120957dc6b5668df62da2a5cfe7a227a0b0bfe9198800efef0cdb1de3560c5`
- `render_markdown(load_matrix())` sha256 BEFORE fix = `42120957...` (same)
- `render_markdown(load_matrix())` sha256 AFTER fix  = `42120957...` (same)

## Checks (direct exit codes)

- S1a `ruff check --show-files . | grep render_coverage_matrix` → listed, `exit=0`.
- S1b `ruff check .` → `All checks passed!`, `exit=0`.
- S3a rendered output sha256 = `42120957...` after fix, `exit=0`.
- S3b `pytest -q tests/rules/test_coverage_matrix.py` → `15 passed`, `exit=0`.
- S3c `pytest -q tests/rules` → `1114 passed in 61.24s`, `exit=0`.
- S4 `git status --ignored --porcelain` with `coverage/`, `services/api/coverage/`,
  `apps/web/coverage/` dummies present: the same three dirs are ignored before and after
  (`.gitignore` byte-unchanged); the source folder stays tracked. Dummies removed.
- S5 `git diff --stat`: only `services/api/pyproject.toml` and the renderer changed;
  `.gitignore` unchanged (`git diff --quiet .gitignore` → unchanged).
- Mutation proof: removing `respect-gitignore = false` → `grep render_coverage_matrix` `exit=1`
  (NOT listed); restoring → `exit=0` (listed). The config line is load-bearing.
- S2 (git-archive, no `.git`): see commit section — ruff check passes in the archived copy.

## Scope / limitations

- Only `services/api/pyproject.toml` ([tool.ruff]) and the renderer changed; `.gitignore`
  untouched. No other file required changes.
- `respect-gitignore = false` means ruff no longer defers file discovery to `.gitignore`; it now
  relies on ruff's own excludes. In this checkout the net effect is exactly +1 linted file (the
  intended source). If someone later places a `.py` inside a coverage-output dir under
  `services/api`, ruff would lint it — harmless and in line with DB-240's goal (lint more, not
  less). The api CI job runs ruff as its first step, before any coverage output exists.

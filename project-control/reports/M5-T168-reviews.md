# M5-T168 reviews (every return kept unchanged)

- G3 code-reviewer: PASS at 5a8228c1 (1 advisory: a narrower .ignore file might also work, untested; the chosen fix is correct and bounded).
- G4 qa-engineer: PASS at 5a8228c1 (1 advisory: a stray .py placed in a coverage-output folder under services/api would now be linted; nil risk in CI, which generates no coverage output before ruff).

Every reviewer is an AI agent; none is a human or professional review.

## G3

G3 GATE REPORT — M5-T168 (lint gap DB-240) — reviewer: code-reviewer (independent; did not produce)

VERDICT: PASS

Reviewed at pinned head 5a8228c14 (task/wave24-report-v3, worktree /root/project/w-wave20; `git rev-parse HEAD` = 5a8228c147...). Diff touches only: services/api/pyproject.toml (added `respect-gitignore = false` to [tool.ruff]), services/api/app/rules/coverage/render_coverage_matrix.py (F841 + E501 fixes), and the producer report. .gitignore NOT in the diff.

SCENARIOS (ruff 0.13.0 from the lanes venv; all --no-cache to avoid repo writes; run from services/api):
- S1 PASS. `ruff check --show-files .` lists the renderer (.../render_coverage_matrix.py), and `ruff check .` -> "All checks passed!" exit 0.
- S2 PASS (by config semantics, see "could not check"). The renderer is clean (it is in the linted set and the full check passes); `respect-gitignore=false` makes .git presence irrelevant, so an archive copy lints the same clean tree and passes.
- S3 PASS. `pytest -p no:cacheprovider tests/rules/test_coverage_matrix.py` -> 15 passed. Rendered output byte-identical before vs after: I exec'd the renderer from aac892fc and from 5a8228c14 against the committed coverage_matrix.json — both sha256 = 42120957dc6b...3560c5, equal to the committed COVERAGE_MATRIX.md; coverage_matrix.json and the .md are byte-unchanged between the two commits. No behaviour change confirmed, matching the producer's sha.
- S4 PASS. `git diff --quiet aac892fc 5a8228c14 -- .gitignore` -> UNCHANGED; ignore behaviour is identical by construction.
- S5 PASS. Of the two config files, only services/api/pyproject.toml changed; .gitignore untouched.

BREADTH (point 2) — verified: with the setting ruff discovers 704 files, without it (CLI `--config respect-gitignore=true`) 703; the single added file is exactly render_coverage_matrix.py (diff of the two sorted lists shows only that path). The CI api job runs `ruff check .` after `pip install --no-deps .`, which creates nyc_buildability_api.egg-info/. I inspected three real *.egg-info dirs on disk: all contain only PKG-INFO/SOURCES/top_level text, ZERO .py files, so egg-info adds no lintable file. build/dist/.*_cache/__pycache__/venv/site-packages are in ruff's built-in excludes (nothing under those is currently listed). So in the CI disk state the lint set still grows by exactly the renderer.

FINDINGS:
- ADVISORY A1 (point 6): I confirmed the builder's claim — `extend-include=["app/rules/coverage/*.py"]` and an `include` override BOTH fail to recover the gitignore-pruned folder (grep count 0 each) because gitignore pruning happens during traversal before include patterns; `respect-gitignore = false` is the only working ruff lever. It disables gitignore deferral for ALL of services/api (broader than the one folder), relying on ruff's built-ins. Verified harmless today (+1 file; egg-info has no .py). A narrower, untested alternative is a `.ignore` file (ruff honours `.ignore` above `.gitignore`) with a negation for just that folder. Not required: the chosen fix is correct, verified, bounded, and documented.
- Point 7: no .pre-commit-config.yaml; the ONLY [tool.ruff] table in the repo is services/api/pyproject.toml; the ONLY ruff invocation is the CI api job `ruff check .`. No other tool reads the table, so no collateral effect.

MODULARITY: trivial change (one deleted line, one wrapped string, one config key); renderer ~252 lines, no growth concern. No finding.

D-093: this task changes no property fact, rule applicability, calculation input, result, or certainty label (output proven byte-identical). I AGREE it is out of scope for research/verification.

DIRECTIVE D-090-R639: the change closes the gap where a tracked production .py escaped the lint gate, directly serving R639; authoritative requirement verification is the directive-compliance-verifier's pass.

COULD NOT CHECK: S2 by literal `git archive` extraction (the read-only guard blocks shell file-writes/tar extraction) — covered instead by the config-semantics proof above plus the verified clean renderer. Full `ruff check .`/`pytest -q` on a real GitHub runner with egg-info present was not executed; substituted real-egg-info inspection + current ruff discovery. These are adequately covered; CI at the accept head remains the authoritative confirmation (R639).

END-OF-REPORT

## G4

G4 REVIEW — M5-T168 (DB-240 lint gap). Reviewer: qa-engineer (independent; did not produce). Verdict: **PASS**.

Reviewed at pinned material commit 5a8228c14 (worktree HEAD had moved to 209498e1e, so I extracted `git archive 5a8228c14` into scratch and tested there). Tooling: ruff 0.13.0 + pytest 9.0.3 from /root/project/lanes-runtime/venv — ruff version is byte-for-byte what CI pins (`ruff==0.13.0` in requirements-tools.lock). Change diff = only pyproject.toml (`respect-gitignore = false` + comment in [tool.ruff]), the renderer (removed unused `column_order`; wrapped one 113-char string into two adjacent literals), and the producer report. .gitignore byte-unchanged.

Scenario | How tested | Result | exit
S1 | In a repo (so .gitignore is honoured, as in CI), from services/api: `ruff check --show-files .` and `ruff check .` | renderer listed; 704 files; "All checks passed!" | 0 / 0
S2 | Plain export (no VCS metadata), `ruff check .` from services/api | "All checks passed!"; renderer also listed (704) | 0
S3 | Rendered output of pre-fix vs fix renderer over the identical coverage_matrix.json (sha256), + tests | pre, fix, and committed COVERAGE_MATRIX.md all = 42120957dc6b…; `pytest -q tests/rules/test_coverage_matrix.py` 15 passed; `pytest -q tests/rules` 1114 passed | all 0
S4 | Both trees as repos with dummies (coverage/, services/api/coverage/, apps/web/coverage/, services/api/.coverage, + a stray .py); `git status --ignored --porcelain` before vs after, caches cleaned | byte-identical; check-ignore: the 3 coverage/ dirs ignored by .gitignore:20, source folder NOT ignored and tracked | diff exit 0
S5 | The diff | of {.gitignore, pyproject.toml} exactly one (pyproject.toml) changed; .gitignore absent from diff | 0

Mutation proof: removing `respect-gitignore = false` → renderer NOT listed, file count 703 (grep exit 1); restoring → renderer listed again. Load-bearing confirmed.

Findings
- ADVISORY (not a defect; matches producer's documented limitation): with the setting, ruff WOULD lint a stray .py dropped into a coverage-output dir under services/api (I confirmed services/api/coverage/stray.py gets linted). But the risk is nil in CI: the only [tool.ruff] config in the repo is services/api/pyproject.toml; no root ruff config, no pre-commit config; the sole ruff run is the api job's `ruff check .` from services/api; ruff runs BEFORE pytest; the tooling lock has no pytest-cov, so no coverage output is ever generated; checkout is fresh. Net effect is "lint more, not less," aligned with DB-240.
- Note: services/api/.coverage (a file) is not matched by any .gitignore rule — pre-existing, identical before/after, so S4 holds.
- `python tools/modularity_check.py --check` passes (exit 0); the renderer is not flagged.
- Config key parses with zero stderr warnings under the CI-pinned ruff 0.13.0.
- Directive D-090-R639: the change makes the api CI ruff step actually read the tracked renderer, closing the gap where CI green did not cover it — consistent with R639 intent.

Research/verification (D-093): I agree the change touches no property fact, rule applicability, calculation input, result, or certainty label — the render output is byte-identical and the only code edits are an unused-var removal and a behaviour-identical string wrap.

Could not check (not blocking): the live GitHub Actions run at the accept head (orchestrator's R639 read; I verified the mechanism locally with the exact CI ruff version and the exact `ruff check .` invocation from services/api); and the formal per-requirement directive pass, which is the separate directive-compliance-verifier reviewer's lane.

END-OF-REPORT

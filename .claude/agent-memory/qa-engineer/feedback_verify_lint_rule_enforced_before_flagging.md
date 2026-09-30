---
name: verify-lint-rule-enforced-before-flagging
description: Before flagging a lone line-length / lint violation as a gate defect, scan the whole ruff-scoped dir to confirm the rule is actually enforced (avoids false FAIL)
metadata:
  type: feedback
---

When a static check (e.g. a >100-char line vs ruff `line-length=100`) looks like a
defect, do NOT flag it on the config alone. First scan EVERY file in the same
ruff-scoped directories (services/api/app/api + services/api/tests/api) for the same
violation.

**Why:** ruff E501 has a single-word/URL exception and per-file-ignores can silently
disable a rule; flagging on config-reading alone risks a false FAIL. If literally
every already-accepted file conforms and the new file is the sole outlier, that is
strong empirical proof the rule IS enforced and the violation is real and
task-introduced. (M2-T022 G4: line 361 = 107 chars was the ONLY >100 line across
both dirs — confirmed E501 enforced, contradicted the producer's "ruff clean" claim.)

**How to apply:** discipline forbids running ruff/pytest in the gate. Substitute:
(a) read the nearest pyproject.toml `[tool.ruff]` (line-length, select, per-file-ignores);
(b) `python -c` scan the scoped dirs for the violation; (c) if the new file is the
sole outlier among accepted files, treat it as a reproducible defect. Also prove
jsonschema fact-validation is non-vacuous by rebuilding the test's Registry in a
`python -c` probe and confirming a bad value (e.g. malformed bbl) is actually rejected
(a broken registry raises Unresolvable, not a pattern-mismatch message).

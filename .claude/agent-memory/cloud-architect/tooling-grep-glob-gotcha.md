---
name: tooling-grep-glob-gotcha
description: On this Windows repo, Grep-tool brace globs mixing root files and subdir patterns (e.g. {render.yaml,docs/adr/*.md}) silently return zero matches - use direct paths per file/dir instead
metadata:
  type: project
---

Grep tool brace-glob patterns that mix a root-level file with subdirectory patterns (e.g. `glob: {render.yaml,docs/adr/*.md,docs/DEPLOYMENT_AND_ROLLBACK.md}`) returned "No matches found" even for strings that verifiably existed (confirmed 2026-07-15 during M0-T006 rework: `autoDeployTrigger` was present in render.yaml but the brace-glob search found nothing; the same pattern with `path` pointed directly at the file or directory found all matches).

**Why:** unknown (Windows path/glob handling in the Grep tool); the failure is silent, which makes it dangerous for self-check evidence - a "pattern removed" claim could be a false negative.

**How to apply:** for self-check greps over a known small file set, run one Grep call per file/directory with `path` set directly and no `glob`. Never trust an all-files-in-one brace-glob "no matches" result as removal evidence without a positive control (grep for a string you know exists using the same parameters).

Related: producer sandboxes here deny Bash entirely (including read-only python), so Grep/Read are the only self-check instruments; executable evidence (yaml.safe_load etc.) is captured by the orchestrator per ADR-005.

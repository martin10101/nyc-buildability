# M0-T021 — G0 readiness

- **Task:** M0-T021 — Repair lock-verifier reproducibility check (blank-temp → seeded committed lock).
- **Milestone:** M0. **Depends on:** M0-T020 (accepted; the lock tooling this repairs).
- **Producer:** cloud-architect. **Reviewers (independent):** security-reviewer (G5 dependency-security),
  code-reviewer (G3), qa-engineer (G4) — all distinct from the producer.
- **Base:** clean main `f5ab631`; worktree `.claude/worktrees/M0-T021-lock-verifier`,
  branch `task/M0-T021-lock-verifier`.

## Readiness checklist
- **Root cause established** (see `M0-T021-diagnosis.md`): both `--check` verifiers compile into a blank
  `mktemp`, so uv resolves to latest instead of using the committed lock as existing-output preferences.
- **Requirement refs named:** `.claude/ORCHESTRATION_POLICY.md §G` (dependency-security, no waiver),
  `.claude/rules/deployment.md`, `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`.
- **Evidence files named** (packet `inputs`): the two verifier scripts, the age gate (read-only), the
  existing age-gate test, both manifest+lock pairs (read-only), `ci.yml`, and the captured diagnosis.
- **Exclusive write scope** (`allowed_paths`): `lock_tools.sh`, `lock_requirements.sh`,
  `scripts/tests/**`, `.github/workflows/ci.yml`. **Forbidden:** `dependency_age_gate.py`, both lock
  files, both `.in` manifests, `app/**`, `packages/**`, any M4 path/worktree. No overlap with the open
  M4-T002 PR #79 scope (which touches only `app/rules/**` + rules tests + its own reports).
- **Acceptance scenarios AS-1..AS-6** recorded in the packet (primary, repo-wide-deadlock regression,
  genuine-drift failure, tamper failure, age-gate-preserved, mirror-both-scripts boundary).
- **Security invariants to preserve** (dependency-security §G): exact pins+hashes; separate prod/tooling
  locks; fail on genuine drift; fail on tampered/missing hashes; 7-day age gate unchanged
  (`dependency_age_gate.py` byte-identical); no silent updates; no `--upgrade`, no re-lock, no certifi bump.
- **No unresolved blockers.** Owner directive 2026-07-22 authorizes this bounded corrective task and
  forbids re-locking / upgrading certifi / weakening the age gate / modifying M4-T002.

**G0 verdict: PASS (ready to claim).**

# GATE REPORT — M0-T086 — G5 independent security review

Reviewer: security-reviewer (read-only). Producer: orchestrator.
Frozen identity: `372b4f7ec6b734251ff765d0f4a06ac6ca065756` (verified == HEAD).
**Result: PASS** (PASS-with-findings — all minor/nit, none blocking).

## Acceptance criteria reproduced
AS-1..AS-6 all PASS (probe reproduced to scratchpad, exit 0, schema/vocabulary/unknown-preservation
verified; matrix vocabulary + cross-check; reconciliation report; absent-tool boundary; freeze
amendment scope; 13-file diff with no control-flow/hook/settings/policy change; 16/16 tests re-run).

## Security-scoped requirement verdicts (all PASS at 372b4f7)
D-024-R001, R009, R099, R100, R124, R125/R126/R127, §12 credential non-exposure, §2 read-only role
boundary, 16.1 no-side-effect-install — each re-derived from source-001.md and reproduced (full table
in reviewer session record).

## Independently executed
HEAD verification; `git show --stat` (no dependency manifest, no .claude/hooks, no settings, no
ORCHESTRATION_POLICY change); all in-scope files read; 16/16 tests re-run; probe re-run (exit 0,
body clean of user paths); import-graph check (only the test imports the new module); secret scan of
fixtures (only benign schema field-names match "token"); gitleaks pre-commit hook confirmed present in
the common git dir.

## Dimension verdicts
1. **Command execution safety — PASS.** Fixed read-only allowlist; MUTATING_TOKENS guard + structural
   test; argv never attacker-influenced (hardcoded constants; no env/config/fixture feeds argv);
   shell=False everywhere; 30s timeout; failures → unknown.
2. **Data exposure — PASS (S-1 below).** Body stores sha256+first_line only; no credentials, no user
   paths, no terminal escapes in the deterministic body (test-enforced).
3. **Dependency security — PASS.** stdlib-only; no manifest/lockfile change; suite installs nothing.
4. **Freeze amendment — PASS (S-3).** Requires the SPECIFIC D-024-R### id in BOTH task packet and
   commit message (both present: R099); no new approval path; R595/SHADOW-ONLY unchanged.
5. **Docs staleness — PASS.** Docs facts labelled official-docs with fetch date, separated from
   measured-live; interactive facts unknown.
6. **No autonomy broadening — PASS.** No hooks/settings/policy touched (all in forbidden_paths);
   standalone read-only module wired into no control flow.

## Findings (non-blocking)
- **S-1 (minor/informational)** — probe_meta.claude_binaries/codex_binaries and the matrix binary
  notes commit the operator's absolute install paths (username MLFLL + home layout). Reviewer judged
  acceptable-if-private and asked the orchestrator to confirm visibility.
  **Orchestrator adjudication (recorded at gate time): `gh repo view` shows the repository is
  PUBLIC — the reviewer's privacy assumption was WRONG. Adjudicated as accepted residual anyway,
  with grounds: (a) identical absolute paths are already pervasive throughout the committed public
  history (task-file `worktree` fields, session handoffs, reports across D-001..D-023), so the
  marginal new exposure is nil; (b) no credential content is involved (gitleaks-scanned); (c) the
  deterministic body remains clean (test-enforced). Remediation queued, not skipped: home-prefix
  redaction of probe_meta joins the M0-T088 (Phase B) hardening bundle, where the telemetry
  redaction subsystem is built. Repo visibility itself is an owner decision; not altered.**
- **S-2 (nit)** — executing the shutil.which-resolved path trusts the operator's PATH exactly as
  running the CLIs normally does; read-only verbs only; documented in module + matrix. Accepted residual.
- **S-3 (nit)** — the amendment relies on the standard gates (G5 + DCV) to check that a cited
  D-024-R### is actually RELEVANT to a given supervisor change, matching the pre-existing D-010
  clause posture. Reviewers must verify relevance, not mere id presence, at future supervisor gates.
  Recorded as a standing reviewer duty.

## Required rework
None.

**Reviewer conclusion: PASS.** Read-only allowlist-bounded stdlib-only probe; no injection surface;
no secrets; no new dependency; no autonomy broadening; no control-flow change; docs-vs-measured facts
correctly distinguished.

# M0-T005-R1 — G2 producer self-check evidence (orchestrator-verified)

- **Task:** M0-T005-R1 — scanner + validator hardening
- **Gate:** G2 (permits submission only)
- **Recorded by:** orchestrator (producer = backend-engineer)
- **Date:** 2026-07-16
- **Producer evidence:** `.claude/worktrees/M0-T005-R1` commit `1caa972` on `task/M0-T005-R1-scanner-hardening`; full packet at `project-control/reports/M0-T005-R1-producer-report.md` (in the worktree commit).

## Producer results (all 11 items DONE; S1–S6 all PASS, executed live in producer sandbox)

Highlights: S2 17/17 planted findings incl. UTF-16 file; S3 justified pragma suppressed WITH visible notice / empty pragma exit 1; S5 non-repo exit 2 + injection desk test; S6 nine original classes byte-identical to the M0-T005 G2 baseline; validate_contracts identical output in normal AND forced-legacy modes, RefResolver guard proven with all sockets monkeypatched (zero network attempt on store miss).

## Orchestrator independent spot-check (2026-07-16, worktree)

```
python .github/scripts/secret_scan.py        → PASS -- no findings, EXIT=0
                                                (3 path-exact ALLOWLISTED PATH notices, content-scan wording present)
python .github/scripts/validate_contracts.py → Checked 6 schema file(s); 0 failure(s). EXIT=0
```

## Producer disclosures for G3/G5 adjudication

1. **S4b transient forbidden-path touch:** the content check keys on the exact path `services/api/.env.example`, so the producer appended one line transiently and reverted via `git checkout --` in the same block (git status clean afterward). Flagged for reviewer adjudication.
2. Placeholder hints extended with `"..."` and `"user:pass"` to avoid false positives on six doc-example lines in unmodifiable historical gate reports; residual suppression risk documented in report §2.
3. Policy §5's pattern-class list and "basename allowlist" wording now stale (packet authorized only the one-sentence change) — orchestrator doc touch-up recommended post-acceptance.
4. Report's own PEM header literal was caught by the final self-scan (live demonstration), then defanged; final self-scan PASS.

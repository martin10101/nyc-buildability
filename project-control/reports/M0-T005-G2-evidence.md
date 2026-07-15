# M0-T005 G2 self-check evidence (orchestrator-captured)

Producer: backend-engineer (isolated worktree, branch `task/M0-T005-secret-scan`, commit 4886551, pushed to origin). Producer sandbox denied all python execution (4 denial forms recorded in the producer report §4); per the 2026-07-15 evidence-capture rule the orchestrator executed the producer's section-5 unblock commands from the worktree root on 2026-07-15.

## S1/S3 — clean-tree scan

```
python .github/scripts/secret_scan.py   -> exit 0
secret-scan: scanned 176 files in 0.49s
ALLOWLISTED PATH apps/web/.env.example -- names-only template; contains no values by policy
ALLOWLISTED PATH services/api/.env.example -- names-only template; contains no values by policy
ALLOWLISTED PATH apps/web/package-lock.json -- npm sha512 integrity hashes are high-entropy base64 lookalikes
secret-scan: PASS -- no findings
```

## S2 — planted fake credentials (scratch_fake_creds.txt, 10 fakes + 1 pragma line)

```
python .github/scripts/secret_scan.py   -> exit 1
secret-scan: FAIL -- 9 potential credential(s) found:
  scratch_fake_creds.txt:2  [render-api-key]               rnd_...1234
  scratch_fake_creds.txt:3  [supabase-access-token]        sbp_...4567
  scratch_fake_creds.txt:4  [jwt]                          eyJh...3456
  scratch_fake_creds.txt:5  [service-role-assignment]      fake...2345
  scratch_fake_creds.txt:6  [pem-private-key]              ----...----
  scratch_fake_creds.txt:9  [aws-access-key-id]            AKIA...FAKE
  scratch_fake_creds.txt:10 [github-token]                 ghp_...0123
  scratch_fake_creds.txt:11 [slack-token]                  xoxb...oken
  scratch_fake_creds.txt:12 [generic-credential-assignment] Zq7p...6Ws1
```

All values masked to first/last 4 chars as specified. Line 13 (`allowed_token` with `# secretscan:allow` pragma) was correctly NOT flagged.

Cleanup: `Remove-Item scratch_fake_creds.txt` → rerun → `secret-scan: PASS -- no findings`, exit 0; `git status --short` showed only the six deliverables + agent memory (all now committed).

## S6 — timing

`Measure-Command { python .github/scripts/secret_scan.py }` → **0.62 s** (budget: 60 s).

## Deviations from producer expectations (for reviewers)

1. The producer predicted an explicit `ALLOWLISTED LINE ...:13` notice for the inline pragma; the scanner suppressed the finding but printed NO visible notice (only path-allowlist skips are echoed). Scenario S3's "allowlist usage must be visible in output" is therefore only partially met for inline pragmas. G3/G5 reviewers should decide whether this is a defect (recommended: add a visible pragma notice) or acceptable.
2. **Checkout SHA mislabel found and corrected (orchestrator, evidence-backed):** the producer pinned `actions/checkout@08c6903c... # v4.2.2`, taking the SHA verbatim from the M0-T004 G5 report example (disclosed assumption — no network in its sandbox). Orchestrator verification: `git ls-remote https://github.com/actions/checkout refs/tags/v4.2.2` → `11bd71901bbe5b1630ceea73d27597364c9af683`; `git ls-remote --tags | grep 08c6903` → `refs/tags/v5.0.0`. So 08c6903 is the v5.0.0 commit mislabeled as v4.2.2 (the mislabel originates in the G5 report example — reviewers of future tasks should not reuse it). Corrected on the task branch to `11bd719... # v4.2.2` with an explanatory comment. Reviewers: re-verify the mapping and note the same mislabel exists in `project-control/reports/M0-T004-G5-security-review.md` Defect 1 remediation text (historical record — do not edit; just do not copy it).
3. Everything else matched the producer's predicted outputs exactly.

## Disposition

Producer's requested `blocked` status is superseded by this capture (the producer's own stated unblock condition is met). M0-T005 moves to `awaiting_gate`. Pending gates: G3 (code-reviewer), G5 (security-reviewer) — reviewer focus list is in the producer report §"Recommended reviewer focus" plus deviation 1 above; also verify actions/checkout tag→SHA mapping via `git ls-remote https://github.com/actions/checkout v4.2.2` (orchestrator to capture if reviewer sandbox lacks network).

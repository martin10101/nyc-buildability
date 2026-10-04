# Duplicate CI runs — inspection and one optimization proposal (2026-10-04)

Owner directive D-090-R104/R105: inspect the duplicate CI runs, identify what each actually
validates, and bring back **one** concrete optimization that preserves the required coverage.

This is an inspection record only. It changes **no** workflow. A `.github/workflows` edit is a
Tier B hot-file change (Lane C owns `.github/**`) and waits for the owner's decision on the
proposal in the last section.

Base: branch `task/ci-duplicate-runs-inspection-2026-10-04` at `09641f4e86562a5abfd9a0aec20585a60c5123cc`.
All run data is from real GitHub Actions runs on 2026-10-03 (`gh run list`/`gh run view`, read-only).

---

## 1. The duplicate, in one sentence

`ci.yml` triggers on bare `push:` **and** bare `pull_request:`. Its concurrency group is
`ci-${{ github.ref }}`. On a `push` event `github.ref` = `refs/heads/<branch>`; on a
`pull_request` event `github.ref` = `refs/pull/<N>/merge`. Those two refs differ, so the
concurrency group does **not** dedupe a push run against the PR run of the same commit — it only
cancels an older push when the branch is re-pushed. Result: every commit on a branch that has an
open PR gets **two full CI runs at once** (21 jobs each). `secret-scan.yml` and
`context-budget.yml` duplicate the same way for the same reason.

---

## 2. Workflow trigger table

| Workflow | `push` | `pull_request` | `schedule` | `workflow_dispatch` | `concurrency` (cancel-in-progress) | Duplicates per push? |
|---|---|---|---|---|---|---|
| `ci.yml` | all branches (bare) | all (bare) | — | — | `ci-${{ github.ref }}` (yes) | **Yes** — push + PR run together |
| `secret-scan.yml` | all (bare) | all (bare) | — | — | `secret-scan-${{ github.workflow }}-${{ github.ref }}` (yes) | **Yes** (cheap) |
| `context-budget.yml` | all (bare) | all (bare) | — | — | `context-budget-${{ github.ref }}` (yes) | **Yes** (cheap) |
| `scheduled-audit.yml` | — | paths: api dep artifacts | `17 6 * * *` | yes | `scheduled-audit-${{ github.ref }}` (yes) | No (no `push`) |
| `scheduled-web-audit.yml` | — | paths: web dep artifacts | `41 6 * * *` | yes | `scheduled-web-audit-${{ github.ref }}` (yes) | No (no `push`) |
| `generate-lockfile.yml` | — | — | — | yes | — | No (dispatch only) |

Only the three bare-`push:`+`pull_request:` workflows duplicate. The two scheduled audits have no
`push` trigger (they run on schedule, on PRs that touch their dependency paths, and on manual
dispatch), so they are not part of the duplication. `generate-lockfile.yml` is manual only.

---

## 3. `ci.yml` job table (21 jobs)

Durations from the real `acae9028` push run `37157302795` (full green run; `gh run view --json jobs`).
"Depends on" = whether the job's result is a function of the checked-out tree only (branch head) or
of the merge result. Every `ci.yml` job checks out whatever ref triggered it and runs the same
steps either way, so each job's *result* depends only on the tree it is handed — the raw head on a
`push` run, the head-merged-into-base tree on a `pull_request` run.

| Job | Runner | Validates (one line) | ~Dur |
|---|---|---|---|
| web | ubuntu | npm ci + lint + typecheck + `next build` | 1.4m |
| web-e2e | ubuntu | vitest + Playwright journeys vs the real FastAPI recorded-fixture harness | 4.8m |
| web-dependency-security | ubuntu | npm audit (all sev) + committed-lock age gate + npm-CLI advisory, fail-closed | 0.8m |
| codex-cli-dependency-security | ubuntu | same dep-security suite for `tools/codex_cli` lock | 0.5m |
| api | ubuntu | ruff + pytest on the hash-pinned trees | 1.9m |
| api-lock-verify | ubuntu | `requirements.txt` is a byte-identical fresh uv lock | 0.3m |
| api-tooling-lock-verify | ubuntu | tooling lock byte-identical + age-gate unit tests | 0.3m |
| exact-production-install | ubuntu | Render pip path + `validate_profile` smoke + dual pip-audit + age gate + full pytest | 1.6m |
| contracts | ubuntu | JSON-Schema validation + render.yaml YAML parse | 0.2m |
| contracts-typegen | ubuntu | generated TS types byte-identical (drift) + generator tests | 0.3m |
| contracts-schema-bundle | ubuntu | runtime-bundled schemas byte-identical to canonical | 0.1m |
| control-plane | ubuntu | ADR-005 project-control regression + directive-compliance + MCP policy + dispatch guard + lane-path check | 5.4m |
| product-map | ubuntu | owner-dashboard product-map integrity vs ledger | 0.1m |
| code-graph | ubuntu | code-graph determinism `--check` + fixture tests | 0.3m |
| context-index-a1 | ubuntu | repo fingerprint + cache + baseline + incremental index tests | 0.7m |
| supervisor-bridge | **windows** | supervisor command-doc check + `test_agent_supervisor_*` suite | 6.1m |
| supervisor-linux-containment | ubuntu | systemd cgroup / POSIX session isolation proof | 0.5m |
| modularity | ubuntu | size/responsibility regression gate + proof tests | 0.1m |
| model-routing | ubuntu | frozen routing corpus + allowlist boundary tests | 0.1m |
| context-pipeline | ubuntu | Units B–F suites + integration/adversarial + clean-checkout e2e benchmark | 0.8m |
| validation-suite | ubuntu | orphaned contracts-validator + residential + gate-runner + authority suites | 0.5m |

Sum of job-minutes per full run ≈ **27 job-min** (push) / **29** (PR). `supervisor-bridge` runs on
`windows-latest`, which GitHub bills at **2×** — so billed runner-minutes per full run ≈ **33–35**.
GitHub bills each job **rounded up to the whole minute** before applying that Windows 2× multiplier,
and this run has 21 jobs (many well under a minute), so the ≈33–35 billed figure is a **lower bound** —
the true billed total is higher. Wall-clock per run ≈ 7–9 min (the long jobs run in parallel).

---

## 4. Duplicate-pair table (real head SHAs, 2026-10-03)

"wall" = `updatedAt − createdAt` of each run. Both runs of a pair start within ~2 seconds of each
other and run **simultaneously** (confirmed below) — the concurrency group does not serialize them.

| head SHA | branch (PR) | push run id · wall · concl | PR run id · wall · concl |
|---|---|---|---|
| 265635a8 | lane-b (#368) | 37153603034 · 6.7m · failure | 37153605150 · 8.2m · failure |
| 4da71299 | lane-b (#368) | 37155763496 · 10.7m · failure | 37155765136 · 10.9m · failure |
| acae9028 | lane-b (#368) | 37157302795 · 7.8m · success | 37157304906 · 7.7m · success |
| 39c63d8b | lane-c (#370) | 37155213134 · 6.7m · success | 37155215327 · 7.8m · success |
| 42ef2bad | lane-c (#371) | 37155679486 · 6.9m · success | 37155681612 · 8.2m · success |
| 83a64029 | task M0-T181 (#372) | 37154894334 · 5.9m · **cancelled** | 37154896211 · 5.2m · failure |
| 58b88988 | task M0-T181 (#372) | 37155541432 · 7.7m · success | 37155544286 · 5.9m · success |
| 36922a6a | task M0-T181 (#372) | 37156663166 · 7.2m · success | 37156666832 · 7.2m · success |
| aeccada5 | lane-e (#268) | 37153763150 · 8.7m · success | 37153765994 · 8.6m · success |
| 032cf320 | lane-c (#376) | 37158605162 · 6.8m · success | 37158607748 · 8.3m · success |
| 91a60c11 | lane-d (#378) | 37159098260 · 11.3m · success | 37159100022 · 8.0m · success |

**Aggregate for 2026-10-03** (`gh run list --workflow ci.yml --limit 400`; the fetched page spans
`createdAt` **2026-10-02T08:41:20Z → 2026-10-04T00:58:30Z**, which fully brackets the whole
2026-10-03 UTC day on both ends, then filtered to `createdAt` on 2026-10-03 UTC. An earlier
`--limit 150` page truncated the day and undercounted these aggregates by ~15%; the per-row table
above is exact and unchanged):

- **165** ci.yml runs that day = **99** `push` + **66** `pull_request`.
- **65** distinct PR-branch head SHAs had **both** a `push` and a `pull_request` ci.yml run.
- **58** of those 65 pairs had both runs complete; **7** had one run cancelled by a re-push.
- Redundant PR-branch **push**-run wall that day ≈ **522 min**; the paired PR-run wall ≈ **531 min**
  (they are near-identical, as expected — same jobs, same tree size).
- **31** more ci.yml push runs that day were on the integration branch `candidate/D-024-mrl-option-b`
  itself — these have **no** PR and are **not** duplicates (they are the post-merge validation).

**Simultaneity / correctness (DB-111).** The pairs run at the same time, not back-to-back:
`acae9028` push 22:06:25→22:14:13 and PR 22:06:27→22:14:06 fully overlap and both completed.
`83a64029` push and PR started 2 s apart and one was cancelled mid-flight. The Windows
`supervisor-bridge` job (named-pipe IPC, Job Objects) is sensitive to a second run of the **same
head** starting seconds later — the DB-111 flake. So the duplication costs **correctness**, not
only minutes: two concurrent runs of one commit can collide on the Windows job.

---

## 5. Which run is load-bearing

- **`push` run** — `github.ref = refs/heads/<branch>`, `github.sha =` the branch tip. Checks out
  the **raw branch head exactly as pushed**. It does **not** reflect a merge with the current base.
- **`pull_request` run** — `github.ref = refs/pull/<N>/merge`. GitHub checks out the **test-merge of
  the branch head into the current base** (`refs/pull/N/merge`). This is the state that approximates
  what lands on the base after `gh pr merge`, which is why its check runs attach to the PR head and
  show in `statusCheckRollup`.

**Verification that the PR run is what the orchestrator reads.** `gh pr view 368
--json statusCheckRollup` lists **every** ci.yml job (and secret-scan, context-budget) **twice**,
all against head `acae9028` — one copy from the push run, one from the pull_request run. Drop the
push copy and each job still appears **once, green, against the head**. The Option B merge decision
(`gh pr merge --merge --match-head-commit <head>`, "a different reviewer's PASS at the exact head +
all checks green") is therefore driven by the **pull_request** run. The push run is a second,
redundant copy that additionally tests a *non-merge* state (the raw head), which — when the base has
advanced — is a state that will never exist on the base.

**"Merge base in when stale" rule.** When the base advances, the PR's `refs/pull/N/merge` recomputes
and the pull_request run re-validates the fresh merge; merging the base into the branch produces a
new head whose pull_request run again validates the merged tree. If the PR cannot be merged
(conflicts), GitHub produces **no** merge ref and **no** pull_request run, so `statusCheckRollup`
shows missing checks and the fail-closed orchestrator cannot call it green — which is correct. The
**pull_request** run is load-bearing for this rule too; the push run adds nothing to it.

**No branch protection exists.** `gh api .../branches/main/protection` and
`.../branches/candidate/D-024-mrl-option-b/protection` both return **404 "Branch not protected"**.
So there are no GitHub-enforced *required checks*; Option B is a manual process gate that reads
`statusCheckRollup`. This matters for the proposal: a trigger change cannot break a required-check
contract because none is configured — the only consumer is the orchestrator's manual "all green"
read, which the pull_request run fully satisfies.

---

## 6. Required coverage this proposal must preserve

- **Dependency security — "audited on every change AND on a schedule", fail-closed, never
  warning-only** (CLAUDE.md principle 15; `docs/DEPENDENCY_SECURITY_POLICY.md` §1.5;
  `.claude/ORCHESTRATION_POLICY.md` §G). Jobs: `web-dependency-security`,
  `codex-cli-dependency-security`, `exact-production-install` (dual pip-audit + age gate),
  `api-lock-verify`, `api-tooling-lock-verify`, plus the daily `scheduled-audit` /
  `scheduled-web-audit`.
- **Control-plane / ADR-005 workflow regression** — `control-plane` job (also carries
  directive-compliance, MCP default-deny, dispatch guard, lane-path check).
- **Modularity gate** — `modularity` job.
- **Supervisor** — `supervisor-bridge` (Windows) and `supervisor-linux-containment` (Linux).
- **Lane / Option B process** (`docs/LEAN_OPERATING_PROCESS.md`) — nothing merges without a PR; the
  orchestrator reads all-checks-green at the exact head before `gh pr merge`.

Everything the permanent principles call "on every change" must still run on every change **that can
merge**. The proposal keeps all of them on the pull_request (merge-ref) run before merge, on the
integration-branch push after merge, and on the daily schedule.

---

## 7. Proposal (one change): scope the `push:` trigger to merge-target branches

Make `ci.yml` run on `push` **only** for the integration branch(es) and `main`, and keep
`pull_request` for everything. Feature/lane/task branches are then validated by their
**pull_request** run (the load-bearing merge-ref run) instead of a redundant second push run. Apply
the identical two-line `branches:` block to `secret-scan.yml` and `context-budget.yml`, which
duplicate the same way. `scheduled-*.yml` and `generate-lockfile.yml` are untouched (no bare
`push:`).

### YAML sketch (`ci.yml`; same block for secret-scan.yml and context-budget.yml)

```yaml
on:
  push:
    branches:
      - main
      - 'candidate/**'   # integration branches, e.g. candidate/D-024-mrl-option-b
  pull_request:
```

`concurrency: ci-${{ github.ref }}` with `cancel-in-progress: true` stays as-is — it still cancels a
superseded push on the integration branch and a superseded PR sync.

### What it saves

- **Per push to a PR branch:** one entire ci.yml run — **~27 job-minutes** (**≥ ~33 billed
  runner-minutes** — a lower bound, since GitHub rounds each job up to the whole minute before the
  Windows `supervisor-bridge` 2× multiplier) and **~8–9 min of wall clock**. Plus the redundant
  second copy of `secret-scan` and `context-budget` (cheap).
- **Scaled to 2026-10-03:** ~65 eliminated full runs ≈ **~522 wall-minutes** and ≈ **~1,755
  job-minutes (≥ ~2,100 billed runner-minutes)** in one day, with no loss of merge-gating coverage.

### What coverage it keeps, and why

Every job still runs **on the pull_request merge ref before merge** (the load-bearing run — the one
`statusCheckRollup` and Option B already rely on) **and on the `candidate/**` + `main` push after
merge** (post-merge validation of the integration branch) **and on the daily `scheduled-audit` /
`scheduled-web-audit`**. So "audited on every change / on every change that can merge" holds:
pre-merge (PR) + post-merge (integration push) + schedule. `control-plane` (ADR-005), `modularity`,
`supervisor-bridge`, `supervisor-linux-containment`, and all dependency-security jobs still run on
every PR and every integration push. No gate is weakened, suppressed, or made warning-only; all stay
fail-closed.

### What it stops validating (exact)

A branch **pushed without an open PR** no longer gets a heavy CI run (today the bare `push:` gives it
one). Under Option B such a branch **cannot merge** and therefore cannot affect the shared tree;
opening the PR (`gh pr create`) immediately triggers the pull_request run. The only real gap is the
seconds-to-minutes window between first push and PR creation. The literal phrase "on every push" in
the dependency policy is thereby narrowed to "every push to a merge-target branch + every pull
request + the daily schedule" — this is the one wording point the owner must bless (Tier B).

### Risks

1. Literal "on every push" reading of the dep policy — owner decision (Tier B). Intent ("every change
   that can affect the tree") is preserved.
2. A feature-branch push shows no CI until its PR is opened; mitigated because the process always
   opens a PR and nothing merges without one.
3. Relies on pull_request-run checks attaching to the head (verified in §5 via `statusCheckRollup`).
4. A PR with merge conflicts yields no pull_request run → orchestrator sees missing checks → fails
   closed (correct; not a regression).

**Bonus (correctness):** with `push` gone on PR branches there is exactly **one** ci.yml run per PR
head, so the DB-111 same-head Windows race (two concurrent runs of one commit) cannot occur.

### How it is reviewed

Tier B hot-file change to `.github/workflows` (Lane C owns `.github/**`). A different reviewer
confirms the `branches:` filter matches every merge-target branch pattern actually in use (`main`,
`candidate/**`) and that no lane/task branch is ever a merge target; the owner blesses the narrowed
"on every push" wording; the orchestrator merges via the normal Option B flow. Branch protection is
absent, so no required-check contract is affected.

---

## 8. What the other candidates would have saved, and why not chosen

- **(b) Head-keyed `concurrency` with `cancel-in-progress` across both events** (e.g. group on
  `github.event.pull_request.head.sha || github.sha`). This would make the push and PR runs of the
  same head cancel each other. Rejected: `cancel-in-progress` is **non-deterministic about which run
  survives** — it can cancel the load-bearing pull_request (merge-ref) run and keep the raw-head push
  run, the *less* correct one. A cancelled run also leaves a "cancelled" check on the PR that the
  fail-closed orchestrator must treat as not-green → re-push churn. It saves **fewer** minutes than
  (a) (the first run gets partway before cancel) and still does not deterministically leave one
  correct run. Lower savings, higher correctness risk.
- **(c) Path filters to skip `web-e2e` / Windows jobs on docs-only changes.** Saves minutes only on
  docs-only PRs — a minority; most PRs carry code and would see no saving. It also introduces a
  "which check is required / skipped = ok" ambiguity: with no branch protection to translate a
  skipped job into a neutral status, the orchestrator's manual `statusCheckRollup` read would have to
  interpret absence as success, which runs against the fail-closed culture. A mis-scoped filter could
  skip e2e/Windows that a shared-fixture "docs" change actually needs. Smaller common-case savings,
  higher risk of under-testing. Lost.

**(a) wins** on minutes-saved-to-risk: it removes a whole redundant run per PR push
(~27 job-min / ≥ ~33 billed), deterministically leaves the one load-bearing run, preserves every gate
on the merge ref + integration push + schedule, and as a bonus removes the DB-111 same-head race. Its
single cost — no heavy CI on a PR-less branch push — touches only states that cannot merge.

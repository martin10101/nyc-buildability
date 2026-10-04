# Duplicate CI runs — inspection and one optimization proposal (2026-10-04)

Owner directive D-090-R104/R105: inspect the duplicate CI runs, identify what each actually
validates, and bring back **one** concrete optimization that preserves the required coverage.

This is an inspection record only. It changes **no** workflow. A `.github/workflows` edit is a
Tier B hot-file change (Lane C owns `.github/**`) and waits for the owner's decision on the
proposal in the last section.

Base: branch `task/ci-duplicate-runs-inspection-2026-10-04` at `09641f4e86562a5abfd9a0aec20585a60c5123cc`.
All run data is from real GitHub Actions runs on 2026-10-03 (`gh run list`/`gh run view`, read-only).

**Revision (D-090-R112, 2026-10-04):** this edit tightens the proposal. It separates the **measured**
duplication (§4) from the **unproven** claim that the duplication caused the Windows supervisor-bridge
failures (now isolated in §4a, "Hypothesis, not demonstrated"). It states exactly which runs disappear
and which remain (§7, "Exactly which runs disappear, and which remain"), and maps each required-testing
and security-policy obligation to the run that still satisfies it after the change (§7 coverage table).
The measured tables (§3, §4) and the YAML sketch (§7) are unchanged.

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

**Simultaneity (measured fact).** The two runs of a pair run concurrently, not back-to-back:
`acae9028` push 22:06:25→22:14:13 and PR 22:06:27→22:14:06 fully overlap and both completed;
`83a64029` push and PR started 2 s apart and one run was cancelled mid-flight. This overlap is the
measured consequence of the per-`github.ref` concurrency group (§1): a `push` ref and a
`pull_request` ref never share a group, so the two runs of one commit are never serialized against
each other.

---

## 4a. Hypothesis, not demonstrated — did the duplication cause the DB-111 Windows flakes?

This subsection holds the **only** claim in this record that is not directly measured, so it is kept
separate from the data above and does **not** support the proposal.

**The hypothesis.** The Windows `supervisor-bridge` job uses named-pipe IPC and Job Objects, which
are process-/host-global. One could suppose that when two runs of the **same head** start seconds
apart (as the duplication makes possible), the two Windows jobs collide on a shared named pipe or
Job Object and one flakes — the pattern recorded as DB-111.

**Why this is correlation, not demonstrated causation.** The strongest datum here is the `83a64029`
pair starting 2 s apart — a **timing correlation**, not a shown mechanism. In that very pair the
failing job was `control-plane` (a real test failure present in *both* runs), while the push run's
`supervisor-bridge` was merely **cancelled**, not flaked. So the cited example does not itself
exhibit a `supervisor-bridge` collision; it only shows two same-head runs overlapping. No run log in
this inspection was traced to a named-pipe / Job-Object contention signature.

**What would prove or disprove it.** A controlled experiment: trigger the `supervisor-bridge` job
**alone** versus **paired with a second concurrent run of the identical head**, N times each (e.g.
N ≈ 30–50), and compare the flake rates; a materially higher flake rate in the paired arm, together
with a run-log signature of pipe / Job-Object contention, would support causation, and
statistically equal rates would refute it. **No such test was run for this record.** Until it is,
the duplication is at most a *plausible* contributor to DB-111, not a proven one.

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

**"Merge base in when stale" rule.** When the base advances, GitHub recomputes the PR's
`refs/pull/N/merge` ref, **but it does NOT fire a new `pull_request` run** — a run fires only on a
push to the PR branch (the `synchronize` activity of the bare `pull_request:` trigger, `ci.yml`
`on:` block, lines 8–10), never when the base moves on its own. (Observed: #369's PR run stayed at
its old merge ref while the integration branch advanced.) Fresh-base testing is therefore **not
automatic**; it is enforced by the manual Option B rule: a stale PR has the integration branch
**merged into it** — a new head, which triggers a fresh `synchronize` `pull_request` run on the
merged tree — and the merge is proved empty before merge. If the PR cannot be merged (conflicts),
GitHub produces **no** merge ref and **no** `pull_request` run, so `statusCheckRollup` shows missing
checks and the fail-closed orchestrator cannot call it green — which is correct. The **pull_request**
run is load-bearing for this rule too, but it revalidates a fresh base only when a push gives it a
new head — a process rule, not a workflow guarantee. This proposal does not change any of this (it
touches only the `push` trigger).

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

### Exactly which runs disappear, and which remain

**Disappear.** Only the **`push`-event** runs of the three bare-trigger workflows — `ci.yml`,
`secret-scan.yml`, `context-budget.yml` — **on every branch other than `main` and `candidate/**`**
(the `lane-*` and `task/*` PR branches). No `pull_request` run disappears; no run on `main` or on an
integration branch disappears; no `schedule` or `workflow_dispatch` run is affected.

2026-10-03 counts (`gh run list --workflow <wf> --limit 400`, fetched window
2026-10-02T08:41 → 2026-10-04T00:58 UTC, filtered to `createdAt` on 2026-10-03 UTC). All three
workflows share the identical bare `push:`+`pull_request:` shape, so their counts coincide:

| Workflow | push runs that day | remain (on `main`/`candidate/**`) | **disappear** (other branches) | pull_request runs (all remain) |
|---|---|---|---|---|
| `ci.yml` | 99 | 31 (all `candidate/**`; 0 `main`) | **68** | 66 |
| `secret-scan.yml` | 99 | 31 | **68** | 66 |
| `context-budget.yml` | 99 | 31 | **68** | 66 |

"99 push runs" is the day's **total** push count per workflow; of those, **68** are on
non-merge-target branches and disappear, and **31** (all on `candidate/D-024-mrl-option-b`) remain.
The 68 disappearing `ci.yml` push runs break down by branch prefix as `task/*` 29, `lane-c` 12,
`lane-d` 11, `lane-a` 9, `lane-b` 6, `lane-e` 1.

**Remain.** The **pull_request** runs (66 that day per workflow — the load-bearing merge-ref runs);
the **integration-branch pushes** (31 that day on `candidate/**`, the post-merge validation); the
**daily scheduled audits** (`scheduled-audit.yml` 06:17 UTC, `scheduled-web-audit.yml` 06:41 UTC);
and every **`workflow_dispatch`** run. Nothing that validates a mergeable change is removed.

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
merge** (post-merge validation of the integration branch). The **daily** scheduled runs do **not**
re-run the whole suite: `scheduled-audit.yml` (06:17 UTC) runs only the Python dependency audit —
pip-audit over `services/api/requirements.txt` and the tooling lock plus the release-age gate — and
`scheduled-web-audit.yml` (06:41 UTC) runs only the web npm audit + committed-lockfile age gate +
npm-CLI advisory check and the `tools/codex_cli` re-audit. No `web-e2e`, `control-plane`,
`supervisor-*`, `api`, or other ci.yml job runs on the schedule. So the dependency-security
obligation is met pre-merge (PR) + post-merge (integration push) + daily schedule, while every other
gate — `control-plane` (ADR-005), `modularity`, `supervisor-bridge`, `supervisor-linux-containment` —
is met on every PR and every integration push. No gate is weakened, suppressed, or made
warning-only; all stay fail-closed.

### Coverage table — each requirement → the run that satisfies it after the change

Every obligation below is still met on **every change that can merge**: the pull_request (merge-ref)
run before merge, the `candidate/**` push after merge, and — for dependency security — the daily
schedule. Policy wording is quoted exactly.

| Requirement (exact quote) | Source | Satisfying run(s) after the change |
|---|---|---|
| "audits run on every change and on a schedule; all gates FAIL CLOSED on any outage/missing/malformed/ambiguous evidence and are never warning-only" | CLAUDE.md principle 15 | `web-dependency-security`, `codex-cli-dependency-security`, `exact-production-install` (dual pip-audit + age gate), `api-lock-verify`, `api-tooling-lock-verify` — on every pull_request run and every `candidate/**` push; plus `scheduled-audit` / `scheduled-web-audit` daily |
| "Audited on every change AND on a schedule. A blocking advisory audit runs on every push and pull request that can affect the tree, and again on a daily schedule so an advisory disclosed AFTER a lock lands turns the run red without any code change." | DEPENDENCY_SECURITY_POLICY §1.5 item 5 | Same jobs. "every push … that can affect the tree" = pushes to `main`/`candidate/**` (the only trees that can merge or deploy), still covered; "pull request" = every PR run, still covered; "daily schedule" = the two scheduled audits, untouched |
| "Fail closed on unavailable, missing, malformed, ambiguous, or unmatched registry/integrity evidence." | ORCHESTRATION_POLICY §G | Unchanged — the identical job steps run on the pull_request run and the integration push; no step is weakened or made warning-only |
| ADR-005 control-plane workflow regression | `control-plane` job (ci.yml) | Every pull_request run + every `candidate/**` push |
| Modularity gate | `modularity` job | Every pull_request run + every `candidate/**` push |
| Supervisor containment (Windows + Linux) | `supervisor-bridge`, `supervisor-linux-containment` | Every pull_request run + every `candidate/**` push |
| Web lint/typecheck/build + e2e | `web`, `web-e2e` | Every pull_request run + every `candidate/**` push |
| Contract schema / typegen / bundle drift | `contracts`, `contracts-typegen`, `contracts-schema-bundle` | Every pull_request run + every `candidate/**` push |
| API ruff lint + pytest on the hash-pinned trees | `api` | Every pull_request run (merge ref) + every `candidate/**` or `main` push |
| Owner-dashboard product-map integrity vs the ledger | `product-map` | Every pull_request run (merge ref) + every `candidate/**` or `main` push |
| Code-graph determinism (`--check`) + fixture tests | `code-graph` | Every pull_request run (merge ref) + every `candidate/**` or `main` push |
| Repo fingerprint + crash-safe cache + baseline + incremental index tests | `context-index-a1` | Every pull_request run (merge ref) + every `candidate/**` or `main` push |
| Frozen model-routing corpus + allowlist boundary tests | `model-routing` | Every pull_request run (merge ref) + every `candidate/**` or `main` push |
| Context-pipeline Units B–F suites + integration/adversarial + clean-checkout e2e benchmark | `context-pipeline` | Every pull_request run (merge ref) + every `candidate/**` or `main` push |
| Orphaned contracts-validator + residential + gate-runner + authority suites | `validation-suite` | Every pull_request run (merge ref) + every `candidate/**` or `main` push |
| Repository credential scan | `secret-scan.yml` | Every pull_request run + every `candidate/**` push |
| Automatic-context-load budget guard | `context-budget.yml` | Every pull_request run + every `candidate/**` push |

### What it stops validating (exact)

**Two coverage changes, stated exactly.**

**(1) A branch pushed with no open PR loses its heavy CI run.** Today the bare `push:` gives such a
branch a full CI run; after the change it gets none until a PR exists. This cannot affect a mergeable
change, because under Option B **nothing reaches `main` or an integration branch except through a
PR**: the orchestrator merges only via `gh pr merge --merge --match-head-commit <head>`, which
requires an open PR, and only after reading all-checks-green on that PR's head (`statusCheckRollup`).
A branch with no PR therefore cannot merge and cannot alter the shared tree. The moment a PR is
opened (`gh pr create`) the pull_request run fires, so the only gap is the seconds-to-minutes window
between first push and PR creation.

**(2) An open PR's branch loses its raw-head push run; only the merge-ref (pull_request) run
remains.** Today a commit on a PR branch gets two runs — the raw-head push run and the
`refs/pull/N/merge` run (§4); after the change only the merge-ref run survives. The merge-ref run is
the load-bearing one Option B reads (§5), but the raw head and the merge ref are different trees once
the base has advanced. So a failure that would appear **only on the raw head and not on the merge
ref** is no longer caught at push time; it would surface only after the change merges, on the
post-merge `candidate/**` push run (which still runs every job). This is a real reduction in
pre-merge coverage of the raw-head tree, not merely a redundant copy removed.

### Policy change required (not just a trigger tweak)

The dependency-security policy currently requires (DEPENDENCY_SECURITY_POLICY §1.5 item 5, quoted
exactly): "**Audited on every change AND on a schedule.** A blocking advisory audit runs on every
push and pull request that can affect the tree, and again on a daily schedule so an advisory
disclosed AFTER a lock lands turns the run red without any code change." This proposal **narrows**
that literal wording — from "every push … that can affect the tree" to "every push **to a
merge-target branch** + every pull request + the daily schedule." It therefore does **not** preserve
coverage unchanged: per change (2) above, the raw-head push run on PR branches is dropped. Adopting
it requires the policy text to be **amended** and the owner to **accept the disclosed coverage/policy
change** (Tier B) — not merely bless a wording point.

### Risks

1. Literal "on every push" reading of the dep policy is **narrowed**, so the policy text must be
   amended and the owner must accept it as a policy change (Tier B — see "Policy change required").
   The intent ("every change that can affect the tree before it can merge") is preserved, but
   raw-head coverage on PR branches is reduced (loss (2)).
2. A feature-branch push shows no CI until its PR is opened; mitigated because the process always
   opens a PR and nothing merges without one.
3. Relies on pull_request-run checks attaching to the head (verified in §5 via `statusCheckRollup`).
4. A PR with merge conflicts yields no pull_request run → orchestrator sees missing checks → fails
   closed (correct; not a regression).

**Structural side effect (not a demonstrated fix):** with `push` gone on PR branches there is exactly
**one** ci.yml run per PR head, so the "two concurrent runs of the same commit" condition no longer
arises. Whether that condition *caused* the DB-111 Windows flakes is an unproven hypothesis (§4a);
the case for this proposal rests on the measured minutes saved and the preserved merge-gating
coverage (with the disclosed raw-head narrowing — see "Policy change required"), not on that
hypothesis.

### How it is reviewed

Tier B hot-file change to `.github/workflows` (Lane C owns `.github/**`). A different reviewer
confirms the `branches:` filter matches every merge-target branch pattern actually in use (`main`,
`candidate/**`) and that no lane/task branch is ever a merge target; the owner **accepts the
narrowed "on every push" wording as a policy change** and DEPENDENCY_SECURITY_POLICY §1.5 item 5 is
amended accordingly; the orchestrator merges via the normal Option B flow. Branch protection is
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
(~27 job-min / ≥ ~33 billed), deterministically leaves the one load-bearing run, and preserves every
gate on the merge ref + integration push + schedule. As a structural side effect it leaves exactly
one ci.yml run per PR head (whether that bears on the DB-111 Windows flakes is an unproven
hypothesis, §4a, that this proposal does not rely on). Its single cost — no heavy CI on a PR-less
branch push — touches only states that cannot merge.

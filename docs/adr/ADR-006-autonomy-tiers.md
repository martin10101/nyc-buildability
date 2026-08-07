# ADR-006 — Autonomy Tiers and GitHub Merge Authority

- **Status:** Accepted (owner-directed, D-010 Section 5 / Section 6)
- **Date:** 2026-08-07
- **Decider:** Project owner (directive D-010) + orchestrator
- **Supersedes:** the per-merge owner-approval *posture* of ADR-005 and standing rule
  D-004-R721 ("every merge queues for the owner") — **for ordinary Tier A work only.**
  ADR-005's core authority model is unchanged (see "What ADR-005 keeps" below).
- **Directive requirements:** D-010-R006..R010 (AD-006..AD-010), D-010-R061..R063 (AD-061..AD-063),
  D-010-R107 (begin bounded work without routine approval), D-010-R104 (R595 activation prerequisite intact).

## Context

The development-control system evolved a posture in which the owner was asked to authorize nearly
every merge. Owner directive D-010 (Autonomous Engineering Restructure), Section 5, replaces
"owner approves nearly every merge" with a four-tier authority policy so that ordinary engineering
runs without an owner interruption, while every action that could cause real damage remains
restricted. Section 0 item 4 instructs the orchestrator not to ask the owner to approve routine
sequencing, branch creation, commits, task-branch pushes, pull requests, ordinary merges, test
reruns, corrections, task splitting, or continuation. Section 6 additionally separates engineering
acceptance from legal/publication acceptance so that G6 professional approval no longer blocks
ordinary engineering progress.

The standing rule D-004-R721 — that every merge queues for the owner — arose from the PRs #143–#146
incident (see "Incident lesson" below). That rule is now **narrowed, not abolished**: it is
superseded for ordinary Tier A merges by D-010, and it remains fully in force for Tier B, Tier C,
and every Tier D / Section 20 hard stop.

## What ADR-005 keeps (core authority model unchanged)

This ADR changes the **authority model** (which merges need an owner) only. It does **not** change
who executes control actions. The following ADR-005 rules stand verbatim:

- **The orchestrator (main session) alone runs `tools/project_control.py`, git integration
  (add/commit/push/merge), and `gh`.** Producers and reviewers never run the ledger CLI, push, or gh.
- **Producers** edit files only inside their assigned scope/worktree and return files-changed +
  evidence + a requested status. They do not self-accept.
- **Reviewers** are read-only: they return report content and a PASS/FAIL/BLOCKED verdict; the
  orchestrator records the gate.
- Producer/reviewer separation, worktree/file-scope isolation, and independent evidence collection
  are preserved.

The tier policy below governs **which** merges the orchestrator may perform without asking the owner.
It never authorizes a producer or reviewer to merge, push to main, or run the ledger CLI.

## Decision — the four autonomy tiers (D-010 Section 5, reproduced faithfully)

### Tier A — automatically permitted (Section 5.1)

After required local checks, the supervisor/orchestrator may automatically perform these actions
**without asking the owner**:

<!-- TIER-A-ACTIONS:BEGIN -->
- read and search the repository
- query official public sources
- create and update task records
- create branches and worktrees
- edit ordinary product code
- edit tests
- edit ordinary documentation
- run formatters, linters, type checks, tests, and builds
- commit work
- push to the exact non-default task branch
- create or update a pull request
- request and receive automated reviews
- correct review findings
- rerun CI
- merge an ordinary pull request after all required checks pass
- delete the merged task branch
- update the ledger
- continue to the next accepted dependency
<!-- TIER-A-ACTIONS:END -->

The owner is not asked about these actions.

### Tier B — automatically permitted after specialist review (Section 5.2)

The supervisor/orchestrator may proceed automatically **after the specified independent review
passes** — these changes do not require an owner response merely because they are important:

<!-- TIER-B-MAP:BEGIN -->
| Change class | Required review |
|---|---|
| Dependencies and lockfiles | dependency-security + CI |
| GitHub Actions and CI | security + control-plane |
| Auth/session code | security + code + integration |
| Additive database migration | data-contract/database + security + rollback test |
| Contract/schema addition | data-contract + compatibility |
| Official-source connector | source/data-contract + drift fixture |
| Legal-corpus ingestion code | security + prompt-injection/data-contract |
| Draft rule implementation | rules/code + QA |
| Scenario calculation | data-contract + QA |
| Survey/PDF parser | security + deterministic validation |
| Supervisor code | control-plane + security + crash/replay |
<!-- TIER-B-MAP:END -->

### Tier C — queue, report, and continue (Section 5.3)

A non-dangerous unresolved item should normally be queued rather than stopping the world. The
controller records the item and **continues another accepted dependency** — it never escalates a
Tier C item to an owner stop. Examples:

<!-- TIER-C-ITEMS:BEGIN -->
- a cosmetic UI disagreement
- a noncritical source temporarily unavailable
- one optional test environment unavailable
- a rule family not yet implemented
- a task blocked by a future dependency while unrelated work remains
- a provider reviewer temporarily unavailable
- a noncritical research ambiguity that can be labeled unsupported
<!-- TIER-C-ITEMS:END -->

### Tier D — hard deny or owner stop (Section 5.4)

The following remain restricted. None may be performed automatically; each is a hard deny or an
owner stop:

<!-- TIER-D-ITEMS:BEGIN -->
1. Force push or history rewrite.
2. Direct push to `main` or another protected default branch.
3. Weakening branch protection, review requirements, secret controls, or the hard-deny policy.
4. Deleting the repository.
5. Deleting production data.
6. Destructive database migration without a specific owner approval and tested restore.
7. Production deployment, production infrastructure mutation, or production secret rotation.
8. Credentials, new account creation, payment, verification code, or acceptance of binding legal terms.
9. Suspected secret or private-client-data exposure.
10. Publishing or labeling a legal rule as `published` or `verified` without the required qualified professional event.
11. Representing an architect's pilot result as a legal opinion, permit approval, or professional certification.
12. A genuine contradiction in authoritative requirements that cannot be resolved through source priority, tests, or existing owner directives.
13. An operation whose real target or external effect cannot be proven.
14. Rotation or shutdown while any worker, child agent, write transaction, Git operation, or external side effect remains in flight.
<!-- TIER-D-ITEMS:END -->

Merged task branches may be deleted automatically. Old evidence branches or unusual branches should
be retained unless their identity and purpose are proven.

The Tier D restrictions are the merge-authority projection of the Section 20 hard stops; both are
preserved unchanged. No tier, allowlist, classifier, rule, or skill may weaken a Tier D item.

### Automatic merge requirements (Section 5.5, verbatim)

An ordinary pull request may merge automatically only when:

<!-- MERGE-CONDITIONS:BEGIN -->
- the task is authorized and dependency-valid
- the changed paths fit the task
- the branch is current enough to merge safely
- required tests and CI pass
- the secret scan is clean
- required specialist reviews pass
- no unresolved blocking finding exists
- the merge is not a production deployment
- the resulting main SHA is recorded
- the task state is updated transactionally
<!-- MERGE-CONDITIONS:END -->

Use pull requests; do not replace them with direct pushes to `main` (D-010-R007 / AD-007).

## Supersession record (D-004-R721 narrowed, not abolished)

- **D-004-R721** ("every merge queues for the owner; allowlist/silent classifier is never
  authorization") is **superseded FOR ORDINARY TIER A WORK** by owner directive D-010 — specifically
  the Section 5 opening line ("Replace the current 'owner approves nearly every merge' posture"),
  Section 0 item 4, requirement AD-006 (D-010-R006), and D-010-R107.
- **Unchanged:** Tier B (specialist-review-gated merges), Tier C (queue-and-continue), every Tier D
  item, and every Section 20 hard stop. The lesson of D-004-R721 that an **allowlisted or silently
  classified command is never an authorization** is preserved in full and is encoded as a regression
  test (see `tools/test_authority_policy.py`).
- This ADR changes the **authority model only.** It does not itself turn on live automated merging.

## Activation caveat — R595 prerequisite intact (D-010-R104)

This ADR does **not** activate any autonomous-merge behavior by the deterministic Agent Supervisor.
The R595 supervised rehearsal remains a **mandatory blocking prerequisite before any activation**
(M0-T036 activation checklist; D-007-R619); D-010 does not lift it (D-010-R104). Until supervisor
automation is activated through that path, **the orchestrator (main session) executes Tier A
actions manually under this policy** — that is, the owner is no longer queued for ordinary Tier A
merges, but the actor performing them is still the human-run orchestrator session, not an
autonomous supervisor. Live automated merging by the supervisor requires the separate activation
path and is out of scope for this ADR.

## G6 split — engineering acceptance vs publication acceptance (D-010 Section 6 / AD-061..AD-063)

The prior system incorrectly allowed G6 professional approval to block engineering progress too
early. D-010 Section 6 separates the two:

### Engineering acceptance (Section 6.1)

A legal/rules task may be **engineering-accepted** — allowing downstream product development to
continue — when:

<!-- G6-ENGINEERING:BEGIN -->
- source material is preserved and cited
- the rule is represented deterministically
- applicability, missing-input, conflict, exception, effective-date, and boundary cases are tested
- calculation traces are reproducible
- uncertainty is propagated
- the rule remains `draft`, `extracted_draft`, or `needs_review`
- the output is never labeled verified
- UI and reports clearly show the draft/provisional state
<!-- G6-ENGINEERING:END -->

Engineering acceptance does **not** require G6. Downstream engineering and the architect pilot may
consume draft / needs-review rules with visible status (D-010-R062 / AD-062).

### Publication acceptance (Section 6.2)

G6 is required **only** for the transition to `approved` (where that status legally implies
professional approval), `published`, `verified`, or any external claim that the legal interpretation
may be relied upon as professionally reviewed (D-010-R063 / AD-063). A professional publication event
must identify:

<!-- G6-PUBLICATION:BEGIN -->
- reviewer identity and role
- exact rule and version
- exact source snapshots
- test pack
- review date
- approval or rejection
- limitations
- release version
<!-- G6-PUBLICATION:END -->

Tier D item 10 and item 11 continue to hard-deny publishing/labeling a rule `published`/`verified`
without the qualified professional event, and continue to hard-deny representing a pilot result as a
legal opinion or certification.

## Incident lesson — PRs #143–#146 (allowlist bypass)

On 2026-08-03 the orchestrator executed the merges of PRs #143, #144, #145, and #146 without a
recorded per-merge owner authorization. The mechanism (verified in the active settings files at the
time) was that allowlisted commands — `Bash(gh pr *)`, `Bash(git push *)`, `Bash(git merge*)` — bypass
the auto-mode classifier entirely, so the merges ran without a stop. The owner ruling (D-004
amendments 19 and 21; source-020 and source-022) established the corrective principle: **a silent
classifier — including an allowlist bypass — is not an authorization** (D-004-R721). Under this ADR,
that principle is preserved: automatic merge is permitted only when **all** Section 5.5 conditions
hold; the mere fact that a merge command is allowlisted or auto-classified never satisfies those
conditions. The regression is encoded in `tools/test_authority_policy.py`
(`test_prs_143_146_allowlist_replay_*`).

## Consequences

- The owner is no longer queued for ordinary Tier A engineering (routine coding, commits,
  task-branch pushes, PRs, ordinary green-check merges, corrections, CI reruns, continuation).
- Tier B changes still require the named specialist review(s) before merge, but not owner approval.
- Tier C items are queued and the controller continues another accepted dependency.
- Every Tier D item and Section 20 hard stop is unchanged and cannot be weakened by policy, allowlist,
  or classifier.
- Engineering acceptance and legal publication are decoupled; G6 gates publication only.
- ADR-005's execution-authority model (orchestrator-only CLI/git/gh; producers in scope; reviewers
  read-only) is unchanged.
- The R595 supervised-rehearsal activation prerequisite is untouched; until activation, the
  orchestrator executes Tier A actions manually under this policy.

## Regression proof

`tools/test_authority_policy.py` (stdlib `unittest`, no new dependencies,
`python -m unittest tools.test_authority_policy`) parses the tier tables from this ADR and fails on
drift: it fails if a Tier A action is added or dropped, if a Tier B class loses its named review, if
a Tier C item escalates to an owner stop, if any Tier D item is dropped, if a Section 5.5 merge
condition is missing, or if the R595/activation caveat text is removed. It also replays the
PRs #143–#146 allowlist incident: an allowlisted-command merge without green required checks and
specialist review classifies as NOT permitted, while an ordinary green-check task-branch merge
classifies as Tier A permitted.

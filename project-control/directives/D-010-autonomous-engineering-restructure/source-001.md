# OWNER DIRECTIVE — Autonomous Engineering Restructure and NYC Buildability Pilot Acceleration

**Document purpose:** This is the authoritative implementation directive for restructuring the Claude Code–Codex development system so it can continue building NYC Buildability with minimal owner involvement, while preserving the full New York City product scope and preventing a destructive “big bang” refactor.

**Primary repository:** `martin10101/nyc-buildability`

**Execution posture:** Implement this directive through controlled, reviewable phases. Do not turn it into one enormous pull request. Do not stop after producing another plan. After the initial read-only reconciliation and task breakdown, continue executing the phases autonomously under the authority model in this document.

---

## 0. Immediate instruction to the orchestrator

1. Run the normal start-of-session reconciliation:
   - read `CLAUDE.md`;
   - run `python tools/project_control.py status`;
   - run `python tools/current_state.py` if present;
   - read the current `docs/SESSION_HANDOFF.md`;
   - inspect `origin/main`, active branches, worktrees, CI, open pull requests, active tasks, blockers, and unfinished gates;
   - confirm the exact state of `M0-T036`, the D-009/M0-T019/M2-T014 batch, and any work that advanced after this directive was written.

2. Capture this document as **one canonical owner directive**. Do not mechanically convert every explanatory sentence into a separate requirement row. The normative requirements are the numbered `AD-*` requirements in Section 22. Preserve all of them exactly. Explanatory text supplies design intent and interpretation.

3. Create one parent initiative and a dependency-ordered set of bounded implementation tasks. Use the next available task IDs. The logical task names in this document are not preassigned ledger IDs.

4. Do not ask the owner to approve routine sequencing, branch creation, commits, task-branch pushes, pull requests, ordinary merges, test reruns, corrections, task splitting, or continuation to the next accepted dependency.

5. Stop synchronously only for the hard-stop conditions in Section 20.

6. Do not remove or narrow:
   - five-borough coverage;
   - any zoning district, overlay, special district, rule family, exception family, or source family required for the complete NYC product;
   - missing-information handling;
   - property data provenance;
   - uncertainty and conflict handling;
   - survey, plan, document, legal-corpus, rules, scenario, report, massing, or future Revit capabilities already within product scope.

7. Prioritizing one architect pilot is an **execution-order decision**, not a product-scope reduction. The citywide architecture and backlog remain intact.

8. Do not physically move the supervisor into another repository until the in-repository supervisor is accepted, behaviorally frozen, and proven through the extraction gates in Section 14.

9. Do not delete, rename, or relocate existing files merely because they look old. First complete the repository inventory and classification process in Section 15.

10. After Phase 0 reconciliation, proceed through the authorized phases without waiting for another owner response unless a Section 20 hard stop occurs.

---


# 0A. BINDING AMENDMENT — Codex Efficiency and Control-Plane Completion Ceiling

This amendment is part of the same owner directive and is binding. It preserves every earlier requirement. Where an earlier passage permits multiple implementation choices, this amendment chooses the safer and more efficient default for the owner’s ChatGPT Plus usage and the present stage of the project.

## 0A.1 Codex is ephemeral by default

Codex must **not** normally remain alive as a second long-running 400,000-token development conversation beside Claude Code.

The required default architecture is:

```text
durable Python supervisor
        |
        | starts one bounded Claude implementation unit
        v
Claude Code worker
        |
        | checkpoint + independently collected evidence
        v
fresh ephemeral Codex reviewer
        |
        | one structured decision
        v
Codex exits
        |
        v
supervisor records decision and continues
```

The durable Python supervisor remembers the project. Codex does not need to preserve conversational memory between reviews.

Every normal Codex review must:

1. start as a fresh process;
2. receive a bounded role-specific context packet;
3. run read-only;
4. review one exact task/checkpoint/repository identity;
5. return one schema-valid decision;
6. exit;
7. leave the decision, evidence references, model identity, usage telemetry, and digest in durable supervisor state.

A normal Codex review must never receive:

- the complete Claude transcript;
- the full directive registry;
- every historical report;
- the entire repository by default;
- unrelated task packets;
- all logs;
- a full code-graph dump;
- or any material that is not required to judge the current checkpoint.

## 0A.2 Persistent Codex controller is experimental only

A persistent Codex controller session is **not authorized as the default mode**.

It may be tested only after:

- ephemeral review mode is fully working;
- two real product tasks complete successfully;
- input-token and plan-usage measurements exist;
- the experiment uses a separate bounded task;
- it proves lower total usage or materially better outcomes than ephemeral mode;
- and it does not delay the architect pilot.

Until those requirements are met, the supervisor must create fresh Codex reviews and must not maintain a continuously growing Codex controller thread.

If a persistent-controller experiment does not produce a measured advantage, close it and retain ephemeral mode.

## 0A.3 Codex review cadence

Codex should review meaningful checkpoints, not every keystroke, command, or ordinary commit.

Default review points:

- end of a bounded implementation unit;
- before merge;
- after a material correction;
- after a security-sensitive change;
- after an architectural interface change;
- when deterministic evidence conflicts;
- when the supervisor cannot classify the safe next action.

Do not invoke Codex merely to restate a passing formatter, linter, or unit-test result that deterministic code already proves.

Batch small related corrections into one checkpoint when doing so remains reviewable and safe.

## 0A.4 Codex context-pack budget

The context-pack builder must enforce a configurable Codex review budget.

Default policy:

```text
target review packet: <= 32,000 estimated input tokens
ordinary hard ceiling: <= 64,000 estimated input tokens
relative hard ceiling: <= 20% of the reported Codex model context window
effective hard ceiling: the lower of the ordinary and relative ceilings
```

These numbers are initial engineering policy, not claims about provider billing.

If a material review packet exceeds the effective ceiling:

1. split the task or review;
2. replace full logs with deterministic summaries and exact artifact references;
3. include only relevant changed hunks and authoritative source excerpts;
4. use bounded code-graph queries;
5. never silently omit a material requirement;
6. never solve the overflow by opening a giant persistent Codex conversation.

The packet builder must record estimated tokens, bytes, included sources, omissions, and truncation status.

## 0A.5 Codex implementation fallback

Codex may become a writable implementation worker only when:

- Claude is unavailable, quota-limited, or objectively unsuitable for the bounded unit;
- the task has explicit writable scope;
- the Codex worker uses an isolated branch/worktree;
- a separate independent review process is used afterward;
- and the supervisor records that Codex was acting as a worker rather than reviewer.

When Codex is the worker, its context is governed by the same provider-aware percentage thresholds and safe-seam rotation rules as any implementation agent.

Codex worker usage is an exception. It must not silently become a duplicate full-time builder while Claude is also performing the same work.

## 0A.6 Claude and Codex must not duplicate the same reasoning

The controller must prevent wasteful duplication.

Claude normally owns:

- source reading needed to implement its bounded unit;
- code changes;
- worker tests;
- checkpoint explanation.

Codex normally owns:

- independent verification of material claims;
- review of the diff and evidence;
- detection of missing requirements, unsafe behavior, and design defects;
- structured next-action judgment.

Codex may reopen authoritative source where necessary to verify the worker, but must not reproduce the entire implementation investigation without a reason.

The evidence packet should let Codex challenge Claude without inheriting Claude’s entire context.

## 0A.7 Plus-plan usage budget

Because subagents and reviews consume shared provider allowance:

- default maximum concurrent inference agents remains two;
- default maximum agent nesting remains one;
- only one primary implementation worker should write a given bounded unit;
- Codex review should normally run after the worker checkpoint, not continuously in parallel;
- duplicate full-repository scans are prohibited;
- usage per completed product task must be measured;
- the controller should prefer deterministic tools over model calls when deterministic tools can answer reliably.

Track at minimum:

- Claude input/output/cache usage where available;
- Codex input/output/cached usage where available;
- number of Codex reviews;
- packet size per review;
- subagent count;
- completed task units;
- merged product PRs;
- provider resets or quota failures.

Use these measurements to reduce waste. Do not optimize so aggressively that review quality becomes unreliable.

## 0A.8 Control-plane completion ceiling

The autonomy restructuring is a **bounded enablement project**, not the new main product.

Only the following control-plane capabilities may block the return to product development:

1. accept and freeze the current M0-T036 supervisor;
2. safe durable state and restart;
3. safe Claude session rotation;
4. fresh ephemeral Codex review;
5. bounded context packets;
6. child-agent/process quiescence before rotation;
7. provider quota detection, pause, fallback, and resume;
8. automatic ordinary commit, task-branch push, PR, CI, merge, and ledger continuation;
9. preservation of hard-stop actions;
10. emergency stop and crash reconciliation;
11. proof through two real product-task lifecycles.

Once these minimum capabilities are proven, the system must immediately resume the NYC product dependency chain.

The following become **non-blocking backlog work** after minimum autonomy is proven:

- physical extraction of the supervisor to another repository;
- full Code Graph V2 beyond relationships immediately needed for context packs;
- extensive legacy cleanup;
- additional remote-approval mechanisms;
- additional audit anchoring;
- additional replay examples not tied to a demonstrated defect;
- commercialization of the supervisor;
- enterprise-generalization work;
- aesthetic supervisor dashboards;
- speculative provider integrations;
- optimization that has not been shown to save meaningful usage or prevent a real defect.

They may run alongside product work only when they do not block it.

## 0A.9 Mandatory product-capacity allocation

After `limited-auto` has completed two real product tasks successfully:

- at least 80% of autonomous engineering capacity must be allocated to product milestones;
- no more than 20% may be allocated to supervisor maintenance, context efficiency, graph improvements, or extraction work;
- supervisor work above 20% requires a demonstrated safety defect, provider breakage, data-loss risk, or product-blocking reliability failure.

Measure this over a rolling set of ten completed bounded task units, not by subjective narrative.

A “product task” changes or directly validates:

- property intelligence;
- source connectors;
- legal corpus;
- rules;
- scenarios;
- document ingestion;
- architect review UI;
- reports;
- pilot workflow;
- massing;
- Revit;
- or golden-property validation.

A control-plane task changes only development machinery.

## 0A.10 No speculative supervisor features

No new supervisor task may be created merely because a feature would be:

- nicer;
- more complete;
- enterprise-ready;
- reusable by others;
- future-proof;
- elegant;
- or theoretically safer.

A new supervisor task requires at least one of:

- a reproduced defect;
- a failed acceptance scenario;
- a demonstrated security risk;
- provider CLI/API drift;
- a measured context or usage problem;
- an unresolved crash/recovery problem;
- inability to complete an authorized product task;
- or a requirement explicitly listed in this directive.

Every new supervisor task must cite the evidence that qualifies it.

## 0A.11 Automatic transition to product work

The controller must enforce this transition:

```text
minimum autonomy capabilities pass
        |
        v
two real product tasks complete in limited-auto
        |
        v
freeze nonessential supervisor expansion
        |
        v
resume highest-priority accepted NYC product dependency
        |
        v
continue address-to-report architect pilot
```

Do not return to the owner asking whether to begin product work. Begin it automatically.

The next product sequence remains:

1. resolve active dependency/security/survey batch;
2. secure survey/PDF ingestion;
3. architect correction and review workflow;
4. legal-corpus expansion;
5. systematic zoning-rule expansion;
6. scenario-engine expansion;
7. architect-facing evidence and reporting;
8. five-borough golden-property validation.

## 0A.12 Completion report must expose self-improvement balance

The consolidated implementation report must include:

- number of control-plane tasks completed;
- number of product tasks completed;
- percentage of autonomous capacity spent on each;
- number and total estimated tokens of Codex review packets;
- number of times Codex acted as worker;
- number of persistent Codex-controller sessions, which should be zero unless an authorized experiment ran;
- whether the 80/20 allocation was met;
- any supervisor task created under the demonstrated-defect exception;
- exact product task that followed the autonomy work.


# 1. Executive intent

NYC Buildability has a strong technical foundation in data provenance, contracts, source research, deterministic calculations, uncertainty handling, testing, and development governance. However, the development-control system has become disproportionately elaborate compared with the architect-facing product.

The target is not to throw away the safeguards. The target is to keep the safeguards that prevent real damage, remove the approval steps that merely interrupt ordinary engineering, and redirect engineering capacity toward the complete product.

The future system should work as follows:

```text
Durable repository state and deterministic policy
                    |
                    v
        Primary autonomous controller
             Codex when available
                    |
          assigns bounded work units
                    |
                    v
       Claude Code or Codex worker
                    |
         tests + evidence collection
                    |
                    v
     fresh independent review process
                    |
                    v
 deterministic policy decides outcome
                    |
       +------------+-------------+
       |            |             |
       v            v             v
   continue       correct     hard-stop owner
```

No language model is above the deterministic policy. Codex is the primary autonomous controller and reviewer, but the policy engine is the constitution. Claude Code is a primary implementation engine and fallback controller where authorized. Either provider may temporarily perform implementation work when the other is unavailable, but no provider may override hard-deny rules.

The owner should normally be absent from the loop. The system should continue until:

- it needs a credential, account action, verification code, or payment;
- it needs a legal or professional publication/sign-off;
- it proposes a production deployment or destructive production operation;
- it detects suspected secret exposure;
- it reaches a genuine contradiction that cannot be resolved from authoritative sources;
- or both providers are unavailable and no safe degraded work remains.

---

# 2. Product scope that must remain intact

## 2.1 Five-borough scope

The product remains a citywide New York City development-feasibility platform covering:

- Manhattan;
- Bronx;
- Brooklyn;
- Queens;
- Staten Island.

Do not redesign the product as an R5-only tool, one-borough tool, one-client tool, or one-property tool. The pilot may begin with a bounded set of properties and a prioritized rule slice, but all interfaces, contracts, source registries, legal-corpus structure, rules architecture, and scenario architecture must remain capable of citywide expansion without replacement.

## 2.2 Zoning and legal scope

Retain the planned capability for all applicable:

- zoning districts;
- commercial overlays;
- special-purpose districts;
- split lots;
- limited-height districts;
- landmark and historic-district interactions;
- flood and coastal flags;
- pending land-use actions;
- use regulations;
- FAR and zoning floor area;
- density;
- height and setback;
- base-height and street-wall rules;
- yards, courts, lot coverage, and open space;
- parking and loading;
- MIH and other affordability-related provisions;
- transit-zone modifications;
- exceptions, alternatives, waivers, authorizations, and special permits;
- effective dates, amendments, supersession, and rule priority;
- basic practical building-feasibility constraints;
- future schematic massing and Revit integration.

No item may be removed merely to make the first pilot faster. It may be marked unsupported, draft, provisional, or future coverage until implemented.

## 2.3 Property completeness

Do not reduce the property profile to a small set of easy fields. Continue building the complete property-intelligence layer with:

- canonical address, BBL, BIN, and geometry;
- PLUTO and MapPLUTO;
- mapped zoning features;
- DOB and DOF records;
- ACRIS metadata;
- landmarks;
- flood information;
- pending zoning and land-use changes;
- conflicts between sources;
- missing critical and noncritical facts;
- staleness and drift;
- user confirmation and correction;
- per-fact provenance.

Missing information must remain explicit. It must never be replaced by hidden assumptions.

## 2.4 Document and survey scope

Retain the plan for:

- born-digital PDFs;
- vector PDFs;
- scanned PDFs;
- TIFF;
- PNG and JPEG;
- future validated DXF conversion;
- future licensed and sandboxed DWG handling if approved;
- survey evidence;
- site plans;
- architectural drawings;
- proposed plans;
- historical filing attachments;
- tax maps and tax-lot geometry as separate evidence classes.

The inability to retrieve many plans automatically from City websites does not remove this capability. It means the initial product must support secure user upload and provenance-preserving review.

---

# 3. Current architectural strengths to preserve

The following are valuable and must not be weakened:

1. **Canonical contracts.** Property profiles, source facts, rule definitions, evaluation traces, scenarios, and future survey evidence must remain versioned and closed where appropriate.

2. **Per-fact provenance.** Every material value must retain its source, original field or document location, retrieval time, source version, normalization, correction history, and confidence or review state.

3. **Deterministic calculations.** Arithmetic, geometry checks, rule evaluation, scenario constraints, and report values must be performed by deterministic code rather than by a model’s free-form answer.

4. **Fail-closed uncertainty.** Missing or conflicting critical information must produce a typed unresolved result rather than a guessed conclusion.

5. **Independent evidence.** The development controller must collect Git, test, CI, and changed-path evidence itself rather than trusting a worker’s statement that everything passed.

6. **Read-only review.** Review agents should not modify the work they are reviewing.

7. **Exact arithmetic where material.** Preserve rational/decimal safeguards and strict JSON handling.

8. **Source authority and legal versioning.** Preserve source snapshots, effective dates, section-level citations, and rule lifecycle state.

9. **Worktree and file-scope isolation.** Writing agents must not edit overlapping areas concurrently.

10. **Crash recovery and durable state.** A restart must reconstruct what was in progress and must not blindly repeat ambiguous external effects.

11. **Code-navigation graph.** Preserve the deterministic in-house graph and its honesty labels. Enhance it carefully rather than replacing it with guessed relationships.

---

# 4. Target operating model

## 4.0 Required Codex operating mode

The binding default is **persistent deterministic supervisor + ephemeral Codex review**.

Do not interpret “Codex primary controller/reviewer” to mean that Codex must carry a continuously growing project conversation. The supervisor makes the durable scheduling and policy decisions. Codex supplies a fresh bounded judgment at checkpoints.

A persistent Codex thread is experimental only under Section 0A.2.


## 4.1 The deterministic supervisor is the actual controller

The supervisor, not Claude and not Codex, owns:

- durable run state;
- active task selection;
- task dependency checks;
- branch and worktree identity;
- active provider-session registry;
- active child-agent registry;
- context telemetry;
- provider-usage telemetry;
- policy classification;
- evidence collection;
- approval bindings;
- external-effect journal;
- crash recovery;
- scheduling;
- emergency stop;
- audit records.

Codex supplies planning, review, and next-action judgment. Claude or Codex supplies implementation. Their recommendations are inputs to policy, not substitutes for policy.

## 4.2 Default role allocation

Use this default:

- **Codex primary controller/reviewer:** selects the next bounded unit from accepted dependencies, reviews checkpoints, challenges architecture, and determines `CONTINUE`, `REVISE`, `ROTATE_SESSION`, `COMPLETE_STAGE`, `QUEUE_FOR_LATER_REVIEW`, or `HALT_UNSAFE`.

- **Claude Code primary implementation worker:** performs scoped coding, research, tests, documentation, and corrections in an isolated worktree.

- **Codex implementation fallback:** when Claude is unavailable, Codex may perform ordinary implementation in a separate writable worker session.

- **Claude review fallback:** when Codex is quota-unavailable, a fresh isolated Claude reviewer may review ordinary work. Sensitive work remains unmerged until Codex or another truly independent approved reviewer is available.

- **Deterministic test/evidence lane:** runs continuously regardless of provider availability.

This is a default, not a rigid identity rule. The supervisor may assign a task to the provider best suited and available, but it must preserve reviewer independence at the process and evidence level.

## 4.3 Bounded work units

Never give a model the instruction “finish the entire program.” Every unit must identify:

- objective;
- acceptance criteria;
- exact or bounded paths;
- authoritative inputs;
- forbidden behavior;
- tests and evidence;
- expected checkpoint;
- risk class;
- whether a specialist review is required;
- maximum concurrency;
- rollback point.

The controller may split an oversized task without asking the owner. Splitting is mandatory when a diff is not realistically reviewable.

Suggested split triggers—not owner gates—include:

- more than approximately 25 materially changed files;
- more than approximately 1,500 non-generated changed lines;
- changes spanning more than two major architectural domains;
- mixed product and supervisor refactoring;
- mixed migration, auth, deployment, and business-logic changes;
- any task whose evidence packet cannot stay bounded.

Generated artifacts and mechanical lockfile changes are counted separately.

---

# 5. New autonomy and GitHub authority policy

Replace the current “owner approves nearly every merge” posture with the following.

## 5.1 Tier A — automatically permitted

After required local checks, the supervisor may automatically:

- read and search the repository;
- query official public sources;
- create and update task records;
- create branches and worktrees;
- edit ordinary product code;
- edit tests;
- edit ordinary documentation;
- run formatters, linters, type checks, tests, and builds;
- commit work;
- push to the exact non-default task branch;
- create or update a pull request;
- request and receive automated reviews;
- correct review findings;
- rerun CI;
- merge an ordinary pull request after all required checks pass;
- delete the merged task branch;
- update the ledger;
- continue to the next accepted dependency.

The owner is not asked about these actions.

## 5.2 Tier B — automatically permitted after specialist review

The supervisor may proceed automatically after the specified independent review passes:

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

These changes do not require an owner response merely because they are important.

## 5.3 Tier C — queue, report, and continue

A non-dangerous unresolved item should normally be queued rather than stopping the world. Examples:

- a cosmetic UI disagreement;
- a noncritical source temporarily unavailable;
- one optional test environment unavailable;
- a rule family not yet implemented;
- a task blocked by a future dependency while unrelated work remains;
- a provider reviewer temporarily unavailable;
- a noncritical research ambiguity that can be labeled unsupported.

The controller records the item and continues another accepted dependency.

## 5.4 Tier D — hard deny or owner stop

The following remain restricted:

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
11. Representing an architect’s pilot result as a legal opinion, permit approval, or professional certification.
12. A genuine contradiction in authoritative requirements that cannot be resolved through source priority, tests, or existing owner directives.
13. An operation whose real target or external effect cannot be proven.
14. Rotation or shutdown while any worker, child agent, write transaction, Git operation, or external side effect remains in flight.

Merged task branches may be deleted automatically. Old evidence branches or unusual branches should be retained unless their identity and purpose are proven.

## 5.5 Automatic merge requirements

An ordinary pull request may merge automatically only when:

- the task is authorized and dependency-valid;
- the changed paths fit the task;
- the branch is current enough to merge safely;
- required tests and CI pass;
- the secret scan is clean;
- required specialist reviews pass;
- no unresolved blocking finding exists;
- the merge is not a production deployment;
- the resulting main SHA is recorded;
- the task state is updated transactionally.

Use pull requests; do not replace them with direct pushes to `main`.

---

# 6. Separate engineering acceptance from legal publication

The present system incorrectly allows G6 professional approval to block engineering progress too early.

## 6.1 Engineering acceptance

A legal/rules task may be engineering-accepted when:

- source material is preserved and cited;
- the rule is represented deterministically;
- applicability, missing-input, conflict, exception, effective-date, and boundary cases are tested;
- calculation traces are reproducible;
- uncertainty is propagated;
- the rule remains `draft`, `extracted_draft`, or `needs_review`;
- the output is never labeled verified;
- UI and reports clearly show the draft/provisional state.

Engineering acceptance allows downstream product development to continue.

## 6.2 Publication acceptance

G6 is required only for the transition to:

- `approved` where that status legally implies professional approval;
- `published`;
- `verified`;
- or any external claim that the legal interpretation may be relied upon as professionally reviewed.

A professional publication event must identify:

- reviewer identity and role;
- exact rule and version;
- exact source snapshots;
- test pack;
- review date;
- approval or rejection;
- limitations;
- release version.

## 6.3 Architect pilot

The pilot architect may use:

- official property profiles;
- draft rules;
- provisional calculations;
- conditional scenarios;
- exact citations;
- unsupported coverage indicators;
- conflict and missing-information indicators.

Every pilot screen and report must clearly say that results are experimental, draft, and require professional review before reliance. This permits real-world validation without pretending that the product is legally verified.

---

# 7. Memory model: the repository remembers, not the chat

No model should be expected to retain the entire program in one conversation.

The durable memory hierarchy is:

1. Git history and exact repository SHA.
2. `project-control/` authoritative state.
3. Active task packet and acceptance criteria.
4. Structured checkpoint and evidence packet.
5. Current handoff.
6. Provider session transcript.
7. Model-internal conversational memory.

Items 1–5 must be sufficient to restart from zero conversational memory.

## 7.1 Required session-start packet

Every new primary session receives a bounded orientation packet containing:

- repository identity;
- branch and worktree;
- `origin/main` SHA;
- active task ID and task digest;
- objective and acceptance criteria;
- allowed and forbidden paths;
- current checkpoint;
- unresolved blockers relevant to this task;
- changed-file list;
- latest test and CI results;
- exact next action;
- authoritative source paths;
- code-graph query results where useful;
- previous session handoff digest;
- provider/model identity;
- whether any work is queued for later independent review.

The model must verify the repository facts itself before emitting `READY`.

## 7.2 Session handoff schema

A handoff must contain machine-readable fields, not only prose:

```json
{
  "schema_version": "1",
  "provider": "claude|codex",
  "session_id": "...",
  "model": "...",
  "repo": "owner/repo",
  "branch": "...",
  "worktree": "...",
  "repo_head": "...",
  "origin_main": "...",
  "task_id": "...",
  "task_digest": "...",
  "checkpoint_id": "...",
  "completed_units": [],
  "incomplete_unit": null,
  "active_children": [],
  "pending_external_effects": [],
  "pending_reviews": [],
  "known_failures": [],
  "next_action": "...",
  "required_files": [],
  "evidence_refs": [],
  "context_telemetry": {},
  "quota_telemetry": {},
  "created_at": "...",
  "digest": "..."
}
```

A new session must reject a handoff when its digest, repository SHA, task identity, or external-effect state does not reconcile.

---

# 8. Context-window and plan-usage telemetry

There are two different limits and they must never be confused.

## 8.1 Conversation context

Context is the information currently visible to one model thread. It is separate for:

- the Claude primary session;
- each Claude subagent;
- a persistent Codex controller thread;
- each Codex subagent;
- each fresh Codex review.

Starting a new session resets that thread’s context but does not reset subscription usage.

## 8.2 Subscription usage or rate limit

Plan usage is shared account capacity. It can be consumed by multiple sessions and subagents. Starting a new thread does not restore it.

The supervisor must record both:

```text
session context health
account/provider usage health
```

They are separate state dimensions.

## 8.3 Codex review sessions

The existing read-only Codex reviewer uses a fresh ephemeral process per review. Preserve that pattern.

An ephemeral review:

- receives a bounded packet;
- performs one review;
- returns one structured decision;
- exits.

It does not need a 400,000-token rotation threshold because it should never become a long-lived conversation. If one review packet is large enough to threaten the context window, the packet builder is defective and must split or summarize the evidence deterministically.

## 8.4 Persistent Codex controller telemetry

If Codex is used as a persistent primary controller, use the Codex **app-server interface** rather than relying on a human-only slash command.

Implementation must capability-probe the installed Codex version and consume machine-readable token/context events. Current Codex implementations expose token-count information through richer event/session interfaces, including:

- last-turn/live-context usage;
- cumulative usage;
- model context window;
- compaction events;
- and, when available, rate-limit status.

Do not assume the field names remain stable across upgrades. Preflight must prove the exact event shape and write a fixture before live use.

### Critical calculation rule

Do not use cumulative lifetime token usage as the live context size.

Use the provider’s live-context measurement, currently represented conceptually as:

```text
live_context_tokens / reported_model_context_window
```

where `live_context_tokens` comes from the most recent context-bearing usage event, not the sum of all prior turns.

After compaction, cumulative usage can continue increasing while live context becomes smaller. Summing total usage would rotate at the wrong time.

## 8.5 Claude telemetry

Continue using machine-readable Claude stream events and capability probes. Do not require a human to type `/context`.

The controller must record:

- reported context window;
- current context usage where available;
- cumulative usage;
- compaction/summary events;
- checkpoint count;
- adherence failures;
- largest packet size;
- provider limit signals.

When exact usage is unavailable, represent it as `unknown`; never treat unknown as zero.

## 8.6 Rotation thresholds

Replace one universal absolute threshold with provider- and model-aware thresholds.

Default policy:

```text
warning:             60% of reported context window
rotation_pending:    70%
no new LARGE unit:   72%
rotate at next seam: 75%
hard no-dispatch:    80%
```

Allow provider-specific configuration.

An optional absolute ceiling may also apply, but the effective threshold is:

```text
minimum(configured absolute ceiling,
        configured percentage × reported context window)
```

Therefore, `400,000` may remain an absolute ceiling for a 1M-context Claude model, but it cannot be the trigger for a Codex model whose entire window is approximately 400,000.

If the model window is unknown:

- do not dispatch a large or unknown-size unit after elevated signals;
- rotate after a configurable number of checkpoints;
- rotate after any compaction event before the next large unit;
- rotate when the packet or transcript becomes oversized;
- prefer a fresh session over relying on repeated compaction.

## 8.7 Safe-seam rule

Context pressure alone may never interrupt a bounded unit in progress.

During a unit:

```text
pressure detected
→ set rotation_pending
→ allow current unit to reach checkpoint
→ collect and review evidence
→ quiesce children
→ rotate before next unit
```

Security, secret exposure, destructive external effects, or process-containment failures may interrupt immediately.

---

# 9. Child-agent and subprocess lifecycle

The supervisor must never rotate or terminate a parent while a child remains active.

## 9.1 Separate context accounting

Each child has its own context record:

```json
{
  "agent_id": "...",
  "provider": "...",
  "parent_session_id": "...",
  "task_unit": "...",
  "context_tokens": 0,
  "context_window": 0,
  "context_ratio": 0.0,
  "cumulative_usage": 0,
  "status": "starting|running|waiting|completed|failed|closing|closed|orphaned",
  "process_id": null,
  "worktree": "...",
  "last_heartbeat": "...",
  "result_digest": null
}
```

Do not add child context totals to the parent context percentage. They are separate windows.

Do aggregate provider/account usage for quota budgeting.

## 9.2 Plus-plan concurrency policy

Subagents consume additional plan usage. Default to:

- maximum two concurrently running inference agents;
- maximum depth one;
- no nested subagents unless a task explicitly proves the benefit;
- sequential execution when tasks touch related files;
- bounded context packets rather than full parent-history inheritance.

The controller may raise concurrency only after measuring that it improves completed work per unit of usage.

## 9.3 Rotation quiescence barrier

Before rotation or shutdown:

1. Set `dispatch_frozen=true`.
2. Stop creating new child agents.
3. List all children from the durable registry.
4. Ask running children to finish the current bounded operation and return a checkpoint.
5. Wait for a bounded grace period.
6. Collect and digest each final result.
7. Close each child through the provider’s supported lifecycle call.
8. Verify provider state shows no running/waiting child.
9. Verify the operating-system process tree shows no live descendant that can write.
10. Verify no worktree lock, Git operation, test process, CI dispatch, upload, push, merge, migration, or external-effect transaction remains unresolved.
11. Mark each child `closed`.
12. Write the parent handoff with `active_children: []`.
13. Only then terminate or rotate the parent.

## 9.4 Orphan handling

If a child cannot be closed:

- do not start the new primary session as if the old one ended cleanly;
- classify the child as `orphaned`;
- revoke or remove its write capability;
- terminate its process tree through the controller where safe;
- inspect the worktree and external-effect journal;
- recover to a known checkpoint;
- pause only if the effect remains ambiguous.

Closing must be idempotent. “Already closed” is success, not a new failure.

## 9.5 Child result contract

A child may not merely say “done.” It returns:

- task unit ID;
- files read;
- files changed;
- commands executed;
- tests run;
- result;
- unresolved items;
- exact worktree SHA;
- whether any external effect occurred;
- context and usage telemetry;
- final status.

The parent verifies these claims independently.

---

# 10. Provider and model fallback

## 10.1 Context exhaustion is not provider exhaustion

When Codex context is high:

- finish the unit;
- create a handoff;
- start a fresh Codex controller session;
- continue with Codex.

Do not switch to Claude merely because one Codex thread filled its context.

When Claude context is high, do the equivalent Claude rotation.

## 10.2 Codex quota unavailable

When Codex account usage is temporarily unavailable:

1. Record the provider reset signal if machine-readable.
2. Schedule a Codex retry.
3. Continue safe work using Claude where possible.
4. Queue completed work for Codex review.
5. Ordinary low/medium-risk work may merge after:
   - deterministic tests;
   - a fresh independent Claude review;
   - all normal specialist gates;
   - no sensitive change class.
6. The following remain unmerged until Codex or another approved independent reviewer is available:
   - auth/security boundary changes;
   - dependency and workflow security changes;
   - destructive migrations;
   - supervisor policy changes;
   - production/deployment changes;
   - legal publication;
   - secret-handling changes.
7. When Codex returns, back-review the queued batch and record the result.

The project must not sit idle merely because Codex is temporarily unavailable.

## 10.3 Claude quota unavailable

When Claude is unavailable:

- Codex may implement ordinary tasks in a writable isolated worker process;
- use a separate fresh reviewer process with no shared transcript;
- prefer a different approved model for review when available;
- preserve all evidence and task boundaries;
- queue sensitive merges if meaningful independence cannot be achieved.

## 10.4 Model unavailable

Use configured allowlisted model chains. Every model selection must record:

- requested model;
- actual model;
- reason for fallback;
- capabilities probed;
- context window reported;
- usage/rate-limit signal;
- task risk class.

Never silently substitute a weaker model for a critical review.

## 10.5 Both providers unavailable

Run deterministic work that does not need inference:

- CI;
- regression tests;
- connector health checks;
- source freshness checks;
- lockfile validation;
- report assembly;
- queue reconciliation;
- code-graph regeneration;
- audit verification.

Then wait and resume automatically. Do not fabricate completion.

---

# 11. Codex-native repository instructions

Add a concise Codex instruction hierarchy.

## 11.1 Root `AGENTS.md`

Create a short root `AGENTS.md` that tells Codex:

- product mission;
- authoritative state location;
- session-start routine;
- never-guess rule;
- deterministic calculation boundary;
- full five-borough scope;
- task and path discipline;
- evidence requirements;
- autonomy authority;
- hard-stop conditions;
- on-demand routing to detailed documents;
- how to use the code graph and context-pack tool;
- how to report a checkpoint.

Do not copy all of `CLAUDE.md` into `AGENTS.md`. Repetition wastes context and creates drift.

## 11.2 Path-scoped files

Add focused instructions where useful:

```text
apps/web/AGENTS.md
services/api/AGENTS.md
packages/contracts/AGENTS.md
project-control/AGENTS.md
tools/agent_supervisor/AGENTS.md
tools/code_graph/AGENTS.md
```

Each file should contain only rules specific to that subtree.

## 11.3 Shared canonical policy

Do not maintain conflicting Claude and Codex policy text.

Create one canonical machine-readable policy source, then generate or validate the concise provider-facing instructions against it. Provider files may differ in syntax but not authority.

Add a drift test that fails when:

- a hard stop appears in one provider’s instructions but not the other;
- one provider is granted broader destructive authority;
- full NYC scope is accidentally omitted;
- G6 boundaries differ;
- graph trust language differs.

---

# 12. Bounded context-pack builder

Build a context-pack tool that produces the smallest complete packet for a task.

Suggested command:

```bash
python tools/context_pack.py \
  --task <TASK_ID> \
  --role worker|reviewer|controller \
  --provider claude|codex \
  --max-bytes <BOUND> \
  --out <DIR>
```

## 12.1 Inputs

The builder uses:

- task packet;
- current ledger state;
- Git diff;
- changed paths;
- code graph;
- authoritative routing table;
- relevant contracts;
- latest checkpoint;
- relevant blockers;
- latest CI;
- explicit source files;
- previous handoff.

## 12.2 Exclusions

Do not include by default:

- the entire PRD;
- the entire directive registry;
- every historical report;
- old session transcripts;
- unrelated task packets;
- full generated artifacts;
- full city datasets;
- the whole code graph.

## 12.3 Output

Produce:

```text
context.md
context.meta.json
evidence/
```

`context.meta.json` must record:

- every included file and digest;
- every omitted file category;
- graph queries used;
- byte and estimated-token bounds;
- task and repository SHA;
- whether any source was truncated;
- whether the packet is sufficient for the role.

A reviewer packet must include enough primary source to verify the worker, not merely the worker’s summary.

## 12.4 Packet overflow

If the packet exceeds its bound:

- split the task;
- replace large logs with deterministic summaries plus exact artifact references;
- include only failing test excerpts and commands;
- include changed hunks rather than entire unrelated files;
- never silently truncate a material source.

---

# 13. Code-navigation graph V2

Preserve V1 and extend it additively.

## 13.1 V1 remains valid

Keep:

- deterministic generation;
- artifacts outside the repository;
- source fingerprints;
- integrity hashes;
- exact/derived/partial/unresolved labels;
- no guessed relationships;
- actual-source verification requirement;
- selective use.

## 13.2 V2 relationship types

Add, where they can be proven:

1. API route → handler.
2. Handler → service.
3. Schema/contract → producer.
4. Schema/contract → consumer.
5. Source module → directly associated tests.
6. Environment variable → configuration reader → consumer.
7. Task allowed path → owned subsystem.
8. Rule definition → evaluator operation.
9. Rule result → scenario consumer.
10. Property-profile field → rule input consumer.
11. Report field → originating scenario/constraint.
12. UI component → API client call.
13. Migration → affected table/domain.
14. Exact caller → callee edges only where compiler/static resolution proves them.
15. Partial caller → callee edges where the relationship is real but not fully resolved.

## 13.3 Caller/callee caution

Do not add a regex-based “call graph” that pretends every matching function name is a real call.

Use:

- Python AST plus conservative module/symbol resolution;
- TypeScript compiler/language-service information in CI or a controlled tooling environment;
- exact and partial confidence labels;
- unresolved output when dynamic behavior cannot be proven.

No call edge may become authoritative evidence without source verification.

## 13.4 New bounded queries

Add commands such as:

```text
context <task-id>
why <from> <to>
tests <path-or-symbol>
routes <endpoint>
consumers <schema-or-field>
producers <schema-or-field>
config <env-var>
blast-radius <path> --depth 2
pilot-flow <address-to-report stage>
```

Every query must remain bounded.

## 13.5 Incremental operation

Avoid full regeneration when only a few source files changed if deterministic incremental regeneration can be proven. Otherwise retain full deterministic generation.

Do not claim token savings until measured.

## 13.6 Benchmark

Benchmark V2 on at least ten historical tasks:

- time to locate relevant files;
- files opened;
- incorrect dependency claims;
- context-pack size;
- provider input tokens;
- defects caught;
- wall-clock time.

Keep V2 only where it improves correctness or efficiency.

---

# 14. Supervisor repository separation

The supervisor should eventually become a separate reusable repository, but the extraction must use a strangler pattern rather than a destructive move.

## 14.1 First create a clean internal boundary

Inside the current repository, divide:

```text
tools/agent_supervisor/core/
tools/agent_supervisor/providers/
tools/agent_supervisor/platform/
tools/agent_supervisor/adapters/nyc_buildability/
```

Conceptually:

- `core`: state machine, policy interfaces, audit, recovery, scheduling;
- `providers`: Claude and Codex adapters;
- `platform`: OS process containment and GitHub interfaces;
- `adapters/nyc_buildability`: task ledger, gates, context-pack rules, path classes, code graph, product-specific evidence.

Do not move files merely to match this shape unless imports, tests, and rollback remain controlled. A logical boundary may be established before physical moves.

## 14.2 Freeze public interfaces

Define and test the adapter interfaces:

- task source;
- evidence collector;
- policy extension;
- graph/navigation provider;
- Git provider;
- CI provider;
- notification provider;
- provider-session telemetry;
- worktree manager.

## 14.3 Extraction readiness gate

Before creating a separate repository:

- current M0-T036 accepted;
- all supervisor tests green;
- live context rotation proven;
- live child-quiescence proven;
- ordinary task-branch push proven;
- automatic PR flow proven;
- crash restore proven;
- two real shadow lifecycles completed;
- no product module imports supervisor internals;
- NYC-specific code isolated behind the adapter.

## 14.4 Copy-first extraction

When ready:

1. Create a new private supervisor repository if existing GitHub authentication permits it. If account authentication is required, stop under the credentials rule.
2. Copy the generic core; do not delete the original.
3. Preserve history where practical.
4. Establish semantic versioning.
5. Run the complete test suite in both locations.
6. Have NYC Buildability consume a pinned supervisor release or commit.
7. Run dual-mode parity against the same recorded lifecycle corpus.
8. Run two live shadow tasks.
9. Switch the product repository to the external supervisor.
10. Retain the in-repo copy for one rollback window.
11. Delete the duplicate only in a dedicated cleanup PR after parity is proven.

## 14.5 Code graph location

Keep the NYC product code graph in the NYC Buildability repository. It is product-layout-specific.

The generic supervisor may expose a navigation-provider interface, but it must not own the NYC graph implementation.

---

# 15. Repository inventory and legacy-file safety

No cleanup may begin with deletion.

## 15.1 Inventory outputs

Create:

```text
docs/REPOSITORY_ARCHITECTURE_MAP.md
docs/LEGACY_ASSET_REGISTER.md
docs/SUPERVISOR_PRODUCT_BOUNDARY.md
```

Classify every tracked path or path family as:

- active product source;
- active supervisor source;
- active test;
- canonical contract;
- generated artifact;
- current operational document;
- historical evidence—immutable;
- migration history—immutable;
- accepted legal/source snapshot—immutable;
- legacy but referenced;
- duplicate candidate;
- obsolete candidate;
- unknown—retain.

## 15.2 Evidence for an obsolete candidate

A file may become a deletion candidate only when:

- no code-graph dependency remains;
- repository search finds no material reference;
- no task, gate, report, contract, migration, or audit record requires its path;
- Git history identifies its replacement;
- tests pass without it;
- a reviewer confirms the replacement;
- rollback is possible.

## 15.3 Historical control records

Do not move or delete accepted:

- task packets;
- gates;
- checkpoints;
- blocker records;
- directives;
- verification records;
- legal/source snapshots;
- migrations;
- report evidence referenced by accepted work.

Their volume may be reduced in everyday context through routing and indexes, not by destroying evidence.

## 15.4 Deprecation before deletion

For active code:

1. mark deprecated;
2. route callers to replacement;
3. add a test proving no old path is used;
4. observe through at least one release or pilot cycle where appropriate;
5. remove in a dedicated PR.

---

# 16. Autonomous activation plan

Do not jump directly from shadow-only to unrestricted automation.

## 16.1 Mode definitions

### `shadow`

- observe;
- produce decisions;
- no external mutation beyond test artifacts.

### `supervised-auto`

- code, test, commit, push task branches, create PRs;
- ordinary merges still simulated or manually invoked by the controller under a temporary gate;
- hard stops remain.

### `limited-auto`

- automatic ordinary merges;
- next-task continuation;
- Tier B specialist review enforcement;
- no production deploy;
- no legal publication;
- no destructive data operations.

### `full-development-auto`

- all Tier A and Tier B development actions;
- automatic batching and continuation;
- owner contacted only for Tier D.

“Full-development-auto” is not permission for production deployment or legal publication.

## 16.2 Promotion evidence

Promote one mode at a time after:

- tests;
- replay;
- crash simulation;
- context rotation;
- child cleanup;
- GitHub push/PR/merge;
- stale-SHA rejection;
- secret scan;
- branch-protection verification;
- rollback;
- owner-touch count.

## 16.3 Emergency stop

Provide:

- one local kill command;
- one durable pause flag;
- one remote-safe pause path where authentication is already configured;
- process-tree termination;
- prevention of new dispatch;
- recovery report.

Emergency stop must not leave child agents or write processes running.

---

# 17. Product execution priority after control stabilization

This is prioritization, not scope reduction.

## 17.1 Finish the active control work

- reconcile and complete M0-T036;
- finish the live rotation capture;
- complete final verification;
- accept it;
- resolve and merge the D-009/M0-T019/M2-T014 batch where still pending;
- freeze new supervisor features except this directive and defects.

## 17.2 Complete survey and plan ingestion

Implement the accepted M2-T014 findings through:

1. secure upload;
2. MIME and content validation;
3. immutable original storage design;
4. digest and provenance;
5. extraction routing:
   - vector PDF objects;
   - embedded PDF text;
   - OCR only for raster text;
   - line/symbol detection for raster geometry;
6. deterministic checks:
   - address/BBL match;
   - units;
   - scale;
   - orientation;
   - boundary closure;
   - segment sums;
   - calculated area vs. stated area;
   - contradictory dimensions;
   - geometry validity;
   - elevations where present;
   - tax-lot geometry comparison without overriding a licensed survey;
7. per-fact page and bounding-box/object references;
8. visible unresolved conditions;
9. architect correction workflow;
10. rerun dependent calculations after correction;
11. immutable original plus correction history.

Do not claim that every PDF can be read with 100% certainty. Build a system that can prove what it extracted, validate it, show uncertainty, and allow correction.

## 17.3 Complete the legal corpus

Continue full NYC legal-corpus work:

- complete official Zoning Resolution hierarchy;
- definitions;
- tables;
- cross-references;
- effective versions;
- amendments;
- source snapshots;
- source diffs;
- prompt-injection defenses;
- retrieval;
- evidence viewer.

## 17.4 Expand deterministic rules

Systematically implement all required rule families. Use coverage matrices and rule-family priorities, not random one-off calculators.

Draft rules may drive the pilot provisionally. Publication remains G6-gated.

## 17.5 Complete scenario generation

Expand beyond the current draft FAR-cap foundation to include, when rule/data coverage supports it:

- use;
- FAR by use;
- density;
- height and base height;
- street wall;
- setbacks;
- yards and courts;
- lot coverage/open space;
- parking/loading;
- practical core and efficiency assumptions;
- dwelling-unit ranges;
- conditional alternatives;
- special-district modifications;
- objective-weighted scenario diversity;
- full calculation and citation trace.

Never fill an unsupported constraint with an invisible default.

## 17.6 Complete the pilot workflow

The pilot architect must be able to:

```text
enter address/BBL
→ confirm property
→ see official facts, conflicts, and missing data
→ upload a survey/plan when available
→ review extracted dimensions
→ choose objectives and answer unresolved questions
→ receive multiple materially distinct scenarios
→ inspect calculations and exact sources
→ see draft/unsupported/professional-review labels
→ export a reproducible report
```

## 17.7 Golden-property validation

Build a golden-property library across all five boroughs, including:

- ordinary lots;
- split lots;
- corner and through lots;
- irregular lots;
- overlays;
- special districts;
- landmarks;
- flood conditions;
- existing buildings;
- enlargement/conversion cases;
- missing and conflicting data;
- survey-provided geometry;
- properties with known architect analyses.

For every difference between the architect and program, record:

- property;
- expected result;
- actual result;
- source inputs;
- rule/version;
- calculation trace;
- reason for difference;
- correction;
- regression test.

---

# 18. Detailed implementation phases

## 18.0 Phase-execution ceiling

Phases 1–4 contain the minimum autonomy work that may block the product. Phase 5 must be limited to graph capabilities directly required by bounded context packs and safe impact review. Phase 6 logical boundary work may proceed, but physical extraction is non-blocking. Phase 9 must not delay the architect pilot.

After two successful real product tasks in `limited-auto`, apply the 80/20 product-capacity rule in Section 0A.9.


## Phase 0 — Read-only reconciliation and baseline

Deliver:

- exact repository/branch/worktree/CI state;
- current task and blocker map;
- test baseline;
- supervisor branch comparison;
- D-009 batch comparison;
- architecture inventory;
- risk register;
- phase task breakdown;
- rollback plan.

Do not modify product behavior in this phase.

Proceed automatically to Phase 1 unless a hard contradiction is found.

## Phase 1 — Close and freeze the current supervisor version

- finish M0-T036 remaining proofs;
- merge/accept through normal gates;
- tag or otherwise record the frozen behavior identity;
- prohibit feature additions unrelated to this directive;
- create a defect-only maintenance lane.

## Phase 2 — Autonomy policy simplification

- update the authority policy;
- update ADR-005 or successor;
- remove per-merge owner requirements for ordinary work;
- implement automatic task-branch push, PR, CI, and ordinary merge;
- preserve hard-deny actions;
- add policy tests for every tier;
- replay historical incidents under the new policy.

## Phase 3 — Context, quota, and child lifecycle

- implement provider-session registry;
- implement app-server Codex telemetry capability probe;
- separate live context from cumulative usage;
- implement percentage-based thresholds;
- track every child independently;
- implement quiescence barrier;
- implement orphan recovery;
- prove fresh-session handoff for Claude and persistent Codex controller;
- prove that no rotation occurs with active children.

## Phase 4 — Codex instructions and context packs

- create root and path-scoped `AGENTS.md`;
- establish shared canonical policy validation;
- implement bounded context-pack builder;
- add packet digests and overflow splitting;
- benchmark input-token reduction.

## Phase 5 — Code graph V2

- add exact relationship adapters;
- add bounded context and blast-radius queries;
- add test/config/contract/route edges;
- add conservative call edges;
- benchmark and retain only proven improvements.

## Phase 6 — Supervisor/product boundary

- isolate generic core from NYC adapter;
- define stable interfaces;
- remove product imports from generic core;
- add package/version metadata;
- complete extraction-readiness tests;
- do not physically extract until gates pass.

## Phase 7 — Autonomous activation

- shadow;
- supervised-auto;
- limited-auto;
- full-development-auto.

Use real bounded tasks for promotion. Record owner-touch count and failures.

## Phase 8 — Architect pilot vertical slice

- merge survey research;
- implement secure document ingestion and review;
- advance legal corpus;
- advance rule families;
- complete scenarios;
- complete evidence/report flow;
- validate against real properties.

## Phase 9 — Physical supervisor extraction

Only after Phase 6 and successful autonomous pilot lifecycles:

- create separate repository;
- copy-first;
- parity test;
- dual-run;
- pinned integration;
- rollback window;
- cleanup.

## Phase 10 — Continue full NYC roadmap

Continue systematic expansion through all boroughs, all planned source families, all required zoning/legal families, complete client validation, reporting, massing, and later Revit.

---

# 19. Testing and acceptance requirements

## 19.1 Context telemetry tests

Prove:

- current context is not calculated from cumulative lifetime usage;
- compaction does not falsely increase live context;
- unknown usage is not treated as zero;
- model-window changes update thresholds;
- a 400k absolute ceiling does not override a smaller model window;
- an ephemeral reviewer never carries context between reviews.

## 19.2 Child lifecycle tests

Prove:

- parent cannot rotate with a running child;
- completed child is closed and capacity released;
- already-closed is idempotent;
- child timeout becomes structured failure;
- orphan write capability is revoked;
- OS descendants are terminated;
- child result is collected before close;
- no nested children by default;
- parent and child context percentages remain separate.

## 19.3 Provider fallback tests

Prove:

- Codex context rotation starts fresh Codex;
- Codex quota outage activates degraded Claude work;
- sensitive PRs wait for Codex review;
- Claude outage allows Codex worker;
- model fallback records actual model;
- both-provider outage schedules safe resume;
- queued reviews run when provider returns.

## 19.4 GitHub automation tests

Prove:

- ordinary task branch push auto-passes;
- main push hard-denies;
- force push hard-denies;
- PR creation works;
- ordinary green PR auto-merges;
- secret finding blocks;
- stale remote SHA blocks or reconciles;
- workflow/dependency changes require specialist review but not owner approval;
- branch cleanup is safe;
- crash during push/merge is reconciled without blind retry.

## 19.5 G6 tests

Prove:

- draft rule engineering may be accepted;
- draft rule never emits `verified`;
- pilot scenario may consume draft rule with visible status;
- only qualified approval can publish;
- removing a professional approval downgrades the release;
- report wording cannot imply legal certification.

## 19.6 Repository safety tests

Prove:

- no bulk file deletion;
- every deleted file has inventory evidence;
- historical evidence paths remain stable;
- generated and canonical files are distinguished;
- supervisor extraction retains behavior;
- rollback works.

## 19.7 Product pilot tests

Prove end to end:

- address resolution;
- property profile;
- missing/conflict display;
- document upload;
- extraction evidence;
- deterministic validation;
- correction and rerun;
- draft rule evaluation;
- scenario comparison;
- exact citations;
- report reproduction.

---

# 20. Hard-stop conditions

Stop and ask the owner only when:

1. A new credential, account, verification code, payment, paid license, or acceptance of binding terms is required.
2. A qualified legal, zoning, architectural, engineering, or other professional sign-off is required to publish or represent work as verified.
3. A production deployment, production infrastructure mutation, production secret rotation, or destructive production operation is proposed.
4. Suspected secret/private-client-data exposure is detected.
5. A force push, history rewrite, direct protected-branch push, branch-protection weakening, or repository deletion would be required.
6. A destructive migration or deletion of production/customer data is required.
7. Two authoritative owner requirements directly conflict and cannot be reconciled.
8. The actual target repository, branch, account, payment, or external effect cannot be proven.
9. A child/process/external effect cannot be safely quiesced or reconciled.
10. Continuing would require falsely claiming legal verification, data certainty, test success, or completed work.

Do not stop for:

- routine coding choices;
- task splitting;
- branch creation;
- ordinary commits;
- task-branch pushes;
- PR creation;
- ordinary merges;
- test failures that can be corrected;
- CI reruns;
- noncritical source outages;
- unsupported rule families;
- draft/provisional pilot work;
- choosing the next accepted dependency.

When stopping, provide:

- plain-English reason;
- exact affected task;
- what has already been safely completed;
- what remains paused;
- safe alternatives;
- exact line the owner must type.

---

# 21. Required final return after implementation

Return one consolidated report containing:

1. Phases completed.
2. Tasks and PRs.
3. Main and release SHAs.
4. New authority matrix.
5. Exact remaining hard stops.
6. Context telemetry evidence.
7. Child-quiescence evidence.
8. Provider fallback evidence.
9. Automatic GitHub workflow evidence.
10. G6 engineering/publication split evidence.
11. Code-graph V2 benchmark.
12. Context-pack benchmark.
13. Supervisor extraction readiness.
14. Product pilot progress.
15. Owner-touch count.
16. Any deferred items with reasons.
17. Exact next autonomous task.

Do not return after each phase merely to ask whether to continue. Continue automatically unless Section 20 applies.

---

# 22. Normative requirements

The following are the atomic requirements for directive capture.

## Scope and preservation

- **AD-001:** Preserve the full five-borough NYC product scope.
- **AD-002:** Preserve all planned zoning, legal, source, property, uncertainty, survey, scenario, reporting, massing, and Revit capabilities.
- **AD-003:** Treat the one-architect pilot as execution priority, not scope reduction.
- **AD-004:** Never replace missing or conflicting property information with hidden assumptions.
- **AD-005:** Preserve per-fact and per-calculation provenance.

## Autonomy

- **AD-006:** Remove owner approval from routine coding, commits, task-branch pushes, PRs, ordinary merges, corrections, and sequencing.
- **AD-007:** Keep pull requests and protected-main workflow.
- **AD-008:** Allow Tier B sensitive development changes after specialist review without routine owner approval.
- **AD-009:** Keep the Section 20 hard stops.
- **AD-010:** Continue another accepted dependency when a noncritical item is blocked.

## Controller architecture

- **AD-011:** Make deterministic supervisor state/policy authoritative over both models.
- **AD-012:** Use Codex as primary autonomous controller/reviewer when available.
- **AD-013:** Use Claude Code as primary implementation worker and authorized fallback.
- **AD-014:** Allow Codex implementation fallback.
- **AD-015:** Preserve independent evidence collection and read-only reviews.
- **AD-016:** Use bounded work units and autonomous task splitting.

## Memory and context

- **AD-017:** Make repository state sufficient to restart without conversational memory.
- **AD-018:** Add a structured, digest-verified session handoff.
- **AD-019:** Add a provider-session registry.
- **AD-020:** Separate thread context from provider/account usage.
- **AD-021:** Use machine-readable telemetry rather than requiring `/context`.
- **AD-022:** Capability-probe Codex app-server telemetry at runtime.
- **AD-023:** Never calculate live context from cumulative lifetime token usage.
- **AD-024:** Replace a universal 400k trigger with model-window percentage thresholds plus optional absolute ceilings.
- **AD-025:** Treat unknown telemetry conservatively.
- **AD-026:** Rotate only at a safe checkpoint except immediate safety events.
- **AD-027:** Keep Codex reviews fresh and ephemeral.

## Child lifecycle

- **AD-028:** Track each child’s context and status separately.
- **AD-029:** Aggregate child usage only for quota budgeting, not parent context.
- **AD-030:** Default to maximum two concurrent inference agents and depth one on Plus.
- **AD-031:** Prohibit parent rotation while any child or write process is active.
- **AD-032:** Implement a durable quiescence barrier.
- **AD-033:** Implement idempotent close and orphan recovery.
- **AD-034:** Require structured child results and independent verification.

## Provider fallback

- **AD-035:** On context pressure, rotate to a fresh session of the same provider.
- **AD-036:** On Codex quota outage, continue safe Claude work and queue review.
- **AD-037:** Prevent sensitive merges during degraded reviewer independence.
- **AD-038:** On Claude outage, allow isolated Codex implementation where safe.
- **AD-039:** Schedule automatic resume when providers recover.
- **AD-040:** Record actual models and fallback reasons.

## Instructions and context efficiency

- **AD-041:** Add concise root and path-scoped `AGENTS.md` files.
- **AD-042:** Avoid duplicating full `CLAUDE.md` content.
- **AD-043:** Establish one canonical policy source and drift tests.
- **AD-044:** Build a bounded context-pack generator.
- **AD-045:** Digest every included context source.
- **AD-046:** Split tasks rather than silently truncating material context.

## Code graph

- **AD-047:** Preserve V1 trust and determinism.
- **AD-048:** Add proven route, contract, test, config, task, and data-flow relationships.
- **AD-049:** Add caller/callee edges only with honest static resolution.
- **AD-050:** Add bounded context/blast-radius queries.
- **AD-051:** Benchmark correctness and token efficiency before claiming savings.
- **AD-052:** Keep the NYC graph in the product repository.

## Supervisor separation and cleanup

- **AD-053:** Establish a generic-core/NYC-adapter boundary.
- **AD-054:** Freeze interfaces before physical extraction.
- **AD-055:** Complete extraction-readiness gates before creating the separate runtime dependency.
- **AD-056:** Use copy-first, dual-run, parity, and rollback for extraction.
- **AD-057:** Inventory all files before cleanup.
- **AD-058:** Do not delete or move historical evidence.
- **AD-059:** Require proof and a dedicated PR for deletion.
- **AD-060:** Do not perform a big-bang refactor.

## Legal-review boundary

- **AD-061:** Separate engineering acceptance from professional publication.
- **AD-062:** Permit downstream engineering to use draft/needs-review rules with visible status.
- **AD-063:** Require G6 only for publication/verified claims.
- **AD-064:** Keep pilot outputs clearly experimental and non-certified.

## Product priority

- **AD-065:** Finish and freeze M0-T036 before further supervisor expansion.
- **AD-066:** Resolve the active dependency/security/survey batch.
- **AD-067:** Implement secure survey/PDF ingestion and architect correction workflow.
- **AD-068:** Continue full legal-corpus work.
- **AD-069:** Systematically expand all required zoning rule families.
- **AD-070:** Complete the full scenario engine without hidden defaults.
- **AD-071:** Complete the address-to-report architect pilot.
- **AD-072:** Build a five-borough golden-property validation library.
- **AD-073:** Continue the complete NYC roadmap after the pilot.

## Activation and evidence

- **AD-074:** Promote automation through shadow, supervised-auto, limited-auto, and full-development-auto.
- **AD-075:** Maintain emergency-stop and crash recovery.
- **AD-076:** Prove no rotation occurs with active children.
- **AD-077:** Prove automatic safe GitHub flow.
- **AD-078:** Measure owner-touch count.
- **AD-079:** Continue automatically between phases unless a hard stop applies.
- **AD-080:** Return the consolidated implementation report in Section 21.

---


## Codex efficiency and control-plane ceiling amendment

- **AD-081:** Use fresh ephemeral Codex review as the default.
- **AD-082:** Do not maintain a persistent Codex controller without a measured, authorized experiment.
- **AD-083:** Do not give Codex the full Claude transcript or unrelated repository history.
- **AD-084:** Invoke Codex at meaningful checkpoints rather than every commit or deterministic check.
- **AD-085:** Enforce the Codex review-packet token and relative-context ceilings in Section 0A.4.
- **AD-086:** Split oversized reviews instead of opening a giant persistent Codex session.
- **AD-087:** Prevent Claude and Codex from duplicating the same implementation investigation without cause.
- **AD-088:** Treat Codex writable implementation as a bounded fallback role, not the normal duplicate builder.
- **AD-089:** Measure provider usage per completed product task.
- **AD-090:** Complete only the minimum control capabilities listed in Section 0A.8 before returning to product work.
- **AD-091:** Make physical supervisor extraction, extensive Code Graph V2, legacy cleanup, remote approvals, extra replay, and enterprise generalization non-blocking after minimum autonomy.
- **AD-092:** Allocate at least 80% of autonomous capacity to product work after two successful limited-auto product tasks.
- **AD-093:** Create no speculative supervisor feature without qualifying evidence.
- **AD-094:** Automatically resume the NYC product dependency chain after the minimum autonomy proof.
- **AD-095:** Report Codex review count, packet usage, worker fallbacks, persistent-controller experiments, and product/control allocation.
- **AD-096:** Do not ask the owner whether to begin product development after the autonomy ceiling is reached.


# 23. Definition of success

This directive succeeds when:

- the owner is no longer asked to approve routine development activity;
- Codex and Claude can continue the project through context rotations and temporary provider limits;
- no session rotates while children are active;
- the repository—not chat memory—fully restores work;
- Codex receives bounded, high-quality context;
- the code graph improves navigation without inventing relationships;
- the supervisor has a clean extraction boundary;
- professional approval no longer blocks draft engineering;
- the full five-borough product scope remains intact;
- one architect can complete the real address-to-report pilot workflow;
- and the system can continue expanding citywide without replacing the architecture again.

Additional mandatory success conditions from the binding amendment:

- Codex normally closes after each bounded review instead of accumulating a parallel giant session.
- Codex review packets remain bounded and measured.
- Two real product tasks complete through the autonomous pipeline.
- Product work automatically resumes after the control-plane ceiling.
- The rolling product/control allocation meets the 80/20 rule.
- No speculative supervisor task displaces an available architect-pilot task.


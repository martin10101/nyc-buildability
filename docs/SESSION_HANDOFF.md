# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

## Where main is
- **Accepted-task count = 53** (latest: **M0-T033**, the governance-orchestrator unblock-roster fix).
  Latest checkpoint **CP-0035**. Main advanced through PRs **#131–#133** this window
  (D-004 amendments 9+10, M0-T033 implementation, M0-T033 acceptance).
- On resume `git fetch` and take the current `origin/main`.

## THE ONE THING TO DO NEXT — M0-T027 Phase 3/4 (owner-AUTHORIZED, not started)
M0-T027 is `blocked` at 75% with **complete, merged evidence**. Its only obstacle — the over-broad
`invalid_unblock_roster` guard — is now **fixed and accepted** (M0-T033). The owner has already
authorized Phases 3 and 4; they simply have not been executed.

- **Phase 3 — two truth-preserving packet clarifications, nothing else:**
  - **AS-1** must stop demanding the obsolete literal total of **128** locked directive requirements.
    Keep 128 as the *contract-time baseline*, but require the **current append-only total** (now 420),
    matching digests, and a green validator. **Do not rewrite directive history.**
  - **AS-6** must **preserve the historical Step-1 sentinel FAILURE exactly as recorded**. It may be
    satisfied only across the owner-sequenced remediation arc, by citing the later **M0-T028**
    fresh-session Phase-8 proof of guard denial and independently verified sentinel absence.
    **Never claim the original Step-1 sentinel passed.**
- **Phase 4 — closeout:** unblock via the normal CLI (the M0-T033 guard now admits it *by packet
  shape alone*); freeze the identity; **regenerate the evidence map through the canonical resolver**
  (its recorded map is stale — **97 ids recorded vs 150 derived**; do not preserve the old count);
  dispatch all required independent reviewers on **explicit Opus 5**; preserve every reviewer return
  **verbatim**; run final independent directive verification; stop on anything blocking or ambiguous;
  then submit → merge through protected main → verify merged identity → accept → checkpoint only if
  policy requires it.

## Active directives (regime ON — every new/reclaimed task must cite directive_refs)
- **D-001** active — Owner Directive Compliance System.
- **D-002 / D-003** active — first wave complete and integrated; second wave **not contracted**.
- **D-004** active — Agent-Teams runtime adoption, STAGED. **420 requirements, 11 sources**
  (`source-011-amendment.md` = amendment 10). Steps 1, 2, 3, 4 **all done and accepted**.
  **Amendment 8 (D-004-R307) TEMPORARY MODEL EXCEPTION IS ACTIVE:** Fable 5 is unavailable, so the
  lead **and every gate reviewer/verifier run explicit Opus 5**, and the actual model must be
  disclosed honestly. This supersedes the old "Fable 5 reviewers / Opus 4.8 producers" rule until the
  owner restores Fable 5. **Never write an effort key anywhere**; never modify `teammateDefaultModel`.
- **D-005** active — Graphify = owner-ratified **WAIT**. In-house code graph accepted (M0-T030/T031),
  **SELECTIVE use only**, never universal graph-first; reserved surfaces each need a separate GO.

## What now works (new since last handoff)
- **M0-T033 — `invalid_unblock_roster` corrected generally.** The reserved `orchestrator` may stand as
  `producer_agent` when leaving `blocked` **only** when all four hold: `task_type == "governance"`;
  ≥1 required gate in `INDEPENDENT_GATES` (G1/G3/G4/G5/G6); ≥1 usable independent reviewer; and every
  other control unchanged. No task-id hard-coding, no bypass flag/env/CLI option. `gate()`, `submit()`,
  `accept()` and directive verification are **byte-unchanged**. Test group **S10** (registered in
  `ALL_TESTS`) proves it: `10/10 blocks executed, 118 assertion cases`.
- **A real pre-existing fail-open was closed (F-1).** The old `task.get("reviewer_agents") or []`
  iterated a bare string character-wise, so a malformed packet — including
  `reviewer_agents: "orchestrator"`, naming *only* the reserved identity — **passed** the roster check.
  New `_roster_strings` fails closed on both list fields.
- **B-015 and B-016 are RESOLVED.** The read-only guard now fires correctly for teammates.

## Milestone reality
- **M0** active — M0-T028 and M0-T033 accepted. Still open: **M0-T027 (blocked, the next action
  above)**, M0-T025 (LOW-1 backlog), M0-T026 (backlog), M0-T032 (backlog, **not authorized**),
  M0-T019 (claimed; B-013 age exception DECLINED), M0-T007/T008 (blocked by B-001).
  **M0-T029 does not exist** — reserved for D-004 Step 5, **not authorized**.
- **M1** complete. **M2** active (M2-T014/15/16 survey HELD). **M3** planned — M3-T002 next, blocked by
  B-001. **M4** active — T001..T006 merged DRAFT, G6-gated (0 published). **M5/M6/M7** planned.

## Holds / blockers (ALL still standing unless the ledger says otherwise)
- **G6** legal approval blocks all M4 rule acceptance/publication. Open blockers: **B-001** Supabase
  token, **B-002** Render, **B-003** Vercel, **B-004** Geoclient, **B-010** benchmark, **B-011**
  construction-code scope, **B-012** deploy hold, **B-013** frontend age exception DECLINED.
  **LOW-1** (M0-T025). Expansion-planning hold (`.claude/rules/expansion-agent-dispatch-hold.md` §2)
  and the survey hold remain. Graphify WAIT.
- **NOT AUTHORIZED:** Step 5 / M0-T029, M0-T032, M0-T025, further producer waves,
  `teammateDefaultModel` or effort changes, deployment/G6/Graphify/expansion/survey/hold releases.

## Hard-won operational lessons (cost real cycles — do not relearn)
- **Spawn writing producers UNNAMED.** A spawn `name` lands in `agent_type`, so
  `.claude/hooks/readonly_agent_guard.py` cannot resolve the roster role and fails closed — every
  write is denied. Reviewers may be named; producers must not.
- **Worktree-isolated agents do not start at your branch.** They get a fresh worktree off main and
  **cannot** check out a branch already checked out in the primary checkout. Give them the frozen
  **SHA**, expect a `worktree-agent-*` branch name, fast-forward their worktree yourself, and port
  the diff back with blob-hash proof.
- **`.gitattributes` pins `project-control/directives/** text eol=lf`.** Python's default text-mode
  write emits CRLF on Windows and silently breaks the recorded digests on a fresh checkout. Write LF
  bytes explicitly and keep the repo's `indent=2` so registry diffs stay pure appends.
- **Commit the CLI submit record** (`project-control/reports/<TASK>.json`). `accept()` reads it **from
  disk**; if untracked it fails on any fresh checkout. Same for the evidence map — list **both** in
  `allowed_paths` at contracting time.
- **`accept()` needs a `task_verification` row for every CITED directive**, even one with zero
  applicable requirements. Record an honest **empty-set** row; never drop the citation.
- **Derive applicable requirement ids through the canonical resolver**, never from a hand-picked range
  and never from a report. Ranges leak in ids scoped to other sentinels.

## Non-blocking follow-ups (logged, not tasked)
- M0-T033 carried observations: `accept()` enforces zero gates on a falsy `required_gates` and raises
  `TypeError` on a non-iterable; `claim()` still accepts `--agent orchestrator` for any task type;
  reserved-identity comparison is case-sensitive; S10 block 6 asserts `"amend"` rather than
  `"malformed"`; `task_type` is strip-normalized so `' governance '` is admissible.
- D-004 registry hygiene for the next amendment (append-only): document the `D-004-OPTIONB` sentinel
  in `manifest.applicability_note`.
- Evidence-hygiene convention: **new** reviewer reports should cite **repository-relative** paths.
  ~59 tracked files already carry absolute machine paths and 56 are long-public; retrofitting them is
  a separate owner decision and was explicitly **not** undertaken.
- Older: M4-T007 G5 LOW; M2-T017 G5 LOW; stale `source_fact` comments in `pluto_soda`/`ztldb_soda`;
  M3-T001 check-script docstring path; code-graph INFO items; orphaned `.claude/worktrees` husks
  (cleanup NOT authorized).

## Next action
**M0-T027 Phase 3/4 as specified at the top of this file** — it is authorized and is the only work
queued. Everything else (Step 5/M0-T029, M0-T032, M0-T025, second-wave lanes, code-graph reserved
surfaces, owner-only unblocks B-001/B-002/B-011 and the G6 reviewer) needs a fresh owner GO.
Do not begin untracked work; contract via `/start-controlled-task` with `directive_refs`.

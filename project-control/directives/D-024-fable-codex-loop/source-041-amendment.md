# D-024 Amendment 41 — Controller-update source-binding repair (owner directive, 2026-09-02)

**Kind:** amendment (append-only) · **Amends:** source-001.md · **Sequence:** 41
**Recorded_at:** 2026-09-02T06:00:00+00:00 · **Actor:** orchestrator (source-binding follow-up producer session)
**Base identity at capture:** root/worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
`candidate/D-024-mrl-option-b` (LOCAL ONLY — no upstream, nothing pushed), HEAD
`e60192edc2b451b2d39fc92fc2efb315dd06cfcd` (M0-T136 formally accepted), frozen production candidate
`1489879e1f6787a9d53ed74db4524b24039e03a2` (tree `0babc469a07fc9109e5f7ce18ea73bf932952801`;
`tools/agent_supervisor` subtree `79af11a2c7fa33c8f5c1bf85c17e310736bf30a3`); stale local
`origin/main` = `d8b3899f61efa6620e18a26541ced96020f5bef9` (lacks Tranche B and
`mrl_launch_draft.py` — verified by `git cat-file -e`); clean working tree.

This amendment rejects the manual command-substitution shortcut and orders ONE bounded blocking
follow-up under D-024: repair the canonical controller-update source binding (immutable accepted
candidate `1489879e…`) before any controller update or canary. It is not Tranche C, does not
reopen accepted M0-T136, and does not interpret owner-only R603–R605. It adds R607 onward; every
prior hold (no push, no PR, no merge, no live loop, no Tranche C, PR #241 untouched) remains.

---

## Verbatim owner directive

> OWNER DECISION: Reject the manual command-substitution shortcut. Repair the canonical controller-update source binding before any controller update or canary.
>
> You are the producer for exactly one bounded blocking follow-up under D-024. This is not Tranche C and must not reopen accepted M0-T136 or interpret owner-only R603–R605.
>
> Bootstrap Gate 0:
>
> * Root C:\Users\MLFLL\Downloads\nyc-zoning\ctl24
> * Branch candidate/D-024-mrl-option-b
> * Starting HEAD e60192ed
> * Frozen production candidate 1489879e1f6787a9d53ed74db4524b24039e03a2
> * Clean working tree
> * M0-T136 accepted
> * /mcp empty
>
> If any value differs, report every discrepancy together and stop.
>
> Read durable evidence using targeted line ranges: CLAUDE.md, SESSION_HANDOFF.md, CONTROLLER_UPDATE_RUNBOOK §§3–8, MRL_LAUNCH_RUNBOOK.md, M0-T136-canary-package.md, M0-T136 producer/DCV reports, the command-document validator and tests, controller-manifest record/verify implementation and tests, and the applicable Amendment 40 requirements. The ledger wins over prose.
>
> First perform one consolidated trace of the complete controller-update chain before editing. Gather every consumer and test first. Use read-only foreground subagents for independent tracing where useful.
>
> Root cause to close:
>
> * CONTROLLER_UPDATE_RUNBOOK §4 uses mutable stale origin/main from nyc-development-feasibility-claude-pack.
> * origin/main lacks Tranche B and mrl_launch_draft.py.
> * The present post-install manifest can certify a self-consistent but incorrect installation because it is generated from whatever was copied.
> * A manually reconstructed command would bypass the checked-in command-document contract.
>
> Required result:
>
> 1. The sole checked-in controller-update procedure must source the installation from the immutable accepted production candidate SHA 1489879e1f6787a9d53ed74db4524b24039e03a2—not origin/main, HEAD, a branch name, or another mutable ref.
>
> 2. Before copying, it must independently verify:
>
>    * The source repository and normalized origin identity.
>    * The full 40-character commit exists.
>    * Its tree identity matches the accepted evidence.
>    * The required Tranche-B modules, including mrl_launch_draft.py, exist at that exact commit.
>    * The source worktree is detached at the exact commit.
>
> 3. After copying, the procedure must prove the installed controller files match the exact accepted source by content digest or complete source-to-destination comparison. Merely recording a new manifest from the destination is not sufficient evidence of correct provenance.
>
> 4. The controller manifest/update evidence must bind the immutable source commit/tree and installed-file digests, or the existing mechanism must be demonstrated by adversarial tests to provide equivalent fail-closed binding.
>
> 5. The exact PowerShell 5.1 commands presented to the owner must be checked in, concrete, parse-tested, and covered by the command-document tooth. No hand-edited placeholder or undocumented substitution is permitted.
>
> 6. Add negative/mutation coverage proving all of these are rejected before any provider or canary:
>
>    * origin/main or another mutable ref used as source.
>    * Wrong commit that is internally self-consistent.
>    * Missing Tranche-B module.
>    * Accepted SHA/tree mismatch.
>    * Destination file changed after copying.
>    * Manifest recorded from the wrong installed tree.
>
> 7. Update the canary prerequisite and handoff so there is exactly one consistent owner command. Remove every stale origin/main instruction from the active controller-update path.
>
> Prefer the smallest documentation/validator/test repair if it can satisfy all seven requirements honestly. If existing production code cannot bind source provenance fail-closed, do not quietly expand scope: stop after the consolidated trace and report the exact minimal production changes and tests required.
>
> Use targeted Edit operations, not whole-file rewrites. Do not raise modularity limits or create exceptions.
>
> Run the complete focused and affected tests, PowerShell command-document tests, relevant mutations, Ruff scope, modularity, and governance validators with raw exit codes. Gather all failures before correcting them.
>
> Do not update C:\SupervisorController, run any canary or provider, push, create a PR, merge, modify workflows, begin Tranche C, or alter R603–R605.
>
> Use canonical project-control mechanics to create and complete exactly one minimal follow-up task. Make one local implementation/evidence commit sequence as required by the regime, submit it awaiting independent review, and stop. Do not self-accept.
>
> Return the exact changed files, source-binding design, positive and mutant results, candidate SHA, final status, and one terminal token:
>
> CONTROLLER_UPDATE_SOURCE_BINDING_SUBMITTED

---

## Decomposition note

Decomposed into atomic requirements D-024-R607 … D-024-R621 (see `requirements.json`,
`amendment_sequence` 41), applicability bound to follow-up task `M0-T138`. Forward trace: the
OWNER DECISION headline → R607/R615; Bootstrap Gate 0 + evidence-reading discipline → R621;
consolidated-trace / method / verification-context instructions → R618; the four root-cause
bullets → context bound into R608–R611; required results 1–7 → R608–R614; smallest-repair /
stop-and-report boundary → R617; the prohibition paragraph → R616; project-control mechanics +
no self-acceptance → R619; the return-report items and terminal token → R620. No prior
requirement is superseded; owner-only rows R603–R605 are untouched and uninterpreted.

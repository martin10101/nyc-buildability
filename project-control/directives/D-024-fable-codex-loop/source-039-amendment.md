# D-024 Amendment 39 — Tranche-A conditional authorization (owner directive, 2026-09-01)

**Kind:** amendment (append-only) · **Amends:** source-001.md · **Sequence:** 39
**Recorded_at:** 2026-09-01T17:42:46+00:00 · **Actor:** orchestrator
**Base identity at capture:** frozen origin/main `d8b3899f61efa6620e18a26541ced96020f5bef9`;
work branch `stabilization/D-024-mrl` created from `ad22e4dc2f1846d88fcc842ef95b7c37e54f0421`
(the exact current control head); control branch and its five commits preserved unmodified as
historical evidence; working tree clean; `/mcp` empty at capture.
**Session:** session_01Bc5Kqa74kPZ4h6nJaXM63k.

This amendment conditionally authorizes **Tranche A only** of the Minimum Reliable Loop (MRL) under the
corrections below. It does not authorize Tranche B, any push/PR/merge, integration-branch creation, or
any live supervisor journey. It supersedes no prior requirement; it adds R489–R514.

---

## Verbatim owner authorization

> Owner decision: do not produce another rewritten plan. Tranche A is conditionally authorized under the corrections below. Work locally only. No push, PR, merge, integration branch, live supervisor journey, Tranche B work, or contact with PR #241.
>
> 1. PRESERVE HISTORY AND CREATE THE WORK BRANCH
>
> Verify the current tree is clean at exactly ad22e4dc2f1846d88fcc842ef95b7c37e54f0421.
>
> Create a new local stabilization branch from that exact current HEAD:
>
> stabilization/D-024-mrl
>
> Do not reset, revert, squash, rewrite, delete or move the existing control branch. The existing branch and its five commits remain the historical evidence. If the stabilization branch already exists or HEAD/status differs, stop before mutation with BLOCKED.
>
> 2. GOVERNANCE CORRECTION BEFORE CODE
>
> Capture this authorization as the next D-024 amendment using the repository's canonical tooling and replan M0-T134 as the Tranche-A task.
>
> In one separate governance correction:
>
> * Restore tools/modularity_exceptions.json byte-for-byte to its 6f5d12a6 version, removing the forbidden renewal.
> * Keep tools/modularity_baseline.json byte-for-byte unchanged and remove it from Tranche-A allowed_paths.
> * Do not regenerate the modularity baseline.
> * Classify the old docs/SESSION_HANDOFF.md version as historical orientation only. Generate a current handoff from actual state after Tranche A; do not reapply the old wording as current.
> * Mark LAUNCH_CONTRACT_MATRIX.md and STABILIZATION_REPAIR_PLAN.md prominently SUPERSEDED/HISTORICAL.
> * Give M0-T134 exact code, schema, test and report allowed_paths matching this authorization.
> * Separate orchestrator-owned task/ledger updates from producer-owned code paths.
>
> If the canonical directive tooling would rewrite unrelated historical records or produce unrelated mass formatting churn, stop and report the exact proposed diff. Do not hand-edit registry digests.
>
> Run the directive/task validators after this governance commit. They must pass before code work begins.
>
> 3. HONEST STARTING MODULARITY EVIDENCE
>
> The initial modularity gate is EXPECTED TO FAIL solely because claude_runner.py is 1432 against the existing 1410 exception.
>
> Record that exact initial failure through an unpiped command. Do not require or claim exit 0 at the start.
>
> If the initial gate reports any additional failure, stop before code implementation.
>
> The final committed Tranche-A candidate must produce exit 0 because claude_runner.py was split—not because either modularity policy file changed.
>
> 4. EXACT PROVIDER SCHEMAS
>
> WorkerResult has exactly these required fields and no others:
>
> * outcome: one of "COMPLETED", "BLOCKED", "NEEDS_OWNER"
> * summary: string, 1–4096 characters
> * requested_next_action: string, 0–1024 characters
>
> ReviewVerdict has exactly these required fields and no others:
>
> * verdict: one of "APPROVE", "REVISE", "HALT"
> * rationale: string, 1–4096 characters
> * evidence_ref_ids: unique array of 1–64 strings, each 1–128 characters and each required to match a controller-issued evidence ID
>
> Both schemas require additionalProperties=false. Unknown fields, wrong types, invalid enums, excess lengths, duplicate references and non-controller evidence IDs must fail closed.
>
> APPROVE is only an untrusted reviewer opinion. It must never itself produce COMPLETE. The controller may construct COMPLETE only after every factual invariant and gate passes.
>
> 5. OPTION-B-NEUTRAL GIT BINDING
>
> Do not hard-code origin/main into the new MRL decision contract.
>
> The controller-owned MRL envelope must bind:
>
> * normalized remote URL
> * expected base ref
> * freshly observed base SHA
> * task branch
> * task HEAD SHA
> * observation timestamp
>
> Legacy verified_origin_main behavior may remain for the disabled legacy path, but it must not be repurposed to mean an integration branch.
>
> 6. NARROW TRANCHE-A CODE SCOPE
>
> Remove these from Tranche-A production allowed_paths:
>
> * tools/modularity_baseline.json
> * tools/agent_supervisor/next_task.py
> * tools/agent_supervisor/cli.py
> * tools/agent_supervisor/loop.py
>
> Queue selection and CLI/loop launch wiring belong to later tranches. Tranche A has no live launch.
>
> Before the first code edit, print a requirement → production file → test mapping. Every allowed production file must close a named Tranche-A requirement and have a named test. Remove every unmapped path. Do not expand allowed_paths during implementation; an indispensable missing path is a typed BLOCKED result, not permission for scope growth.
>
> 7. FINAL EVIDENCE
>
> Because modularity_check.py uses git ls-files, its final result does not count while new production files are untracked.
>
> After all new files are tracked and the candidate implementation is committed:
>
> * require a clean working tree;
> * rerun the complete Tranche-A suite through gate_runner;
> * rerun the unpiped modularity gate and require raw exit 0;
> * prove tools/modularity_baseline.json and tools/modularity_exceptions.json match their required reference bytes;
> * run every listed mutation test;
> * independently verify gate_runner's direct-process and PowerShell behavior;
> * generate reports only from captured machine records.
>
> "gate_runner is the sole evidence path" applies to MRL acceptance evidence, not every historical command or unrelated repository workflow.
>
> Stop after Tranche A. Do not start Tranche B. Return:
>
> * branch and exact candidate HEAD;
> * governance correction commit;
> * implementation commit(s);
> * changed-file list;
> * positive and mutation results with raw exits;
> * initial expected modularity failure and final modularity success;
> * byte comparisons for both modularity policy files;
> * remaining limitations;
> * confirmation that nothing was pushed and PR #241 was untouched.
>
> End exactly with either:
>
> TRANCHE_A_READY_FOR_INDEPENDENT_REVIEW
>
> or
>
> BLOCKED: followed by one precise blocking fact.
>
> Do not implement anything after producing the response.

---

## Decomposition anchors

- #item1-branch — preserve history; create stabilization/D-024-mrl from ad22e4dc; BLOCKED if exists/differs.
- #item2-governance — one governance commit; canonical tooling; no digest hand-edit; churn/historical-rewrite stop rule; validators pass before code.
- #item3-modularity-honesty — record exact initial expected failure unpiped; stop on any additional failure; final exit 0 from the split, not policy-file edits.
- #item4-schemas — exact WorkerResult / ReviewVerdict fields, types, enums, lengths; additionalProperties=false; APPROVE never itself COMPLETE.
- #item5-executable-identity — complete SHA-256 immediately before every spawn; no size/mtime cache; full dispatch-chain binding; DISABLE_AUTOUPDATER=1; runtime model/version; preserved-size+restored-mtime replacement still rejected.
- #item6-narrow-scope — remove baseline/next_task/cli/loop from production scope; print requirement→file→test mapping; no allowed_paths growth; missing path = BLOCKED.
- #item7-final-evidence — track files then commit; clean tree; suite via gate_runner; unpiped modularity exit 0; byte comparisons; every mutation test; gate_runner direct+PowerShell; reports from machine records; gate_runner = sole MRL acceptance-evidence path.
- #controller-owns-git — controller (not Claude) owns commit/push/PR.
- #option-b-topology — Option B planning topology; integration branch created later from a clean stabilized head, not now.
- #return — return list + terminal token; stop after Tranche A.

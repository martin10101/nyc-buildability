# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA here as still-current.** This
file is orientation only. Rules/gates/workflow routes live in `CLAUDE.md`. Old blocks via
`git log -p docs/SESSION_HANDOFF.md`. Keep CURRENT-ONLY: the `context-budget` CI check fails > ~4000 tok.

## SESSION 18 END — steps 1-2 done (accepted 84, on main); M0-T056 code+gates DONE; live-proof + accept remain

Refreshed **2026-08-11 (session 18 rotation; `claude-opus-4-8`)**. **Accepted = 84.** origin/main =
**`0d42953`** (M0-T062 + M0-T047 + #220 all merged). Integration branch for the go-live phase =
**`control/session16-codex-golive`** (PR #221), worktree `.claude/worktrees/session15-acc`, HEAD ≈ `67cf95f`
(verify live; pushed). Owner go-live authz = **D-011 amendment-004** + D-010 source-030/031 (R595 build).
The ledger wins.

### Done this session (on main)
- **M0-T062 ACCEPTED (83)** — drained inert M0-T056 grandfather entry + O1 path_free_justification tests.
- **M0-T047 ACCEPTED (84)** — nanoid 3.3.17 (GHSA-2v37-7h3g-55p8), D-009; #219 merged. **Selective-citation:**
  the resolver forced citing holds **D-010-R233** (age-eligible on/after 2026-08-10T10:39:22Z) + **R246**
  (don't bypass age gate) — both `hold` class (not deferrable) verified PASS directly; D-009 subset empty.
- **PR #220 MERGED → main** (`0d42953`; all 8 required checks green; merge-tree dry-run clean).

### M0-T056 (R595 actuation) — CODE BUILT + ALL CODE GATES PASS; NOT yet accepted
- Reviewed code identity = **`a90ac19`** on session16 (6 allowed_paths files: worker_turnover/loop/cli/claude_runner
  + `test_agent_supervisor_r595_actuation.py` (19 tests) + producer report; turnover_controller/adapters/model_turnover
  REUSED UNCHANGED). HEAD `67cf95f` only ADDED gate reports + narrowed allowed_paths — the 6 code files are
  byte-unchanged since a90ac19, so the material identity is stable.
- **Gates PASS (verbatim reports saved):** G3 code + G5 security at 8196039; **G3 delta + G5 delta at a90ac19**
  (`M0-T056-G3-code-review.md`, `-G5-security-review.md`, `-G3-delta-review.md`, `-G5-delta-review.md`). Findings
  **B** (M0-T060 branch regression test — added, teeth confirmed) + **C** (docstring) CLOSED; **A/P1** reconciled
  = already closed by accepted M0-T058 (`claude_runner.py:1300-1349` captures killed=terminate_all()+bounded wait+
  distinct orphan-alive code; all 5 terminate_all sites audited SAFE, no termination change). Freeze **1528/0** full
  glob / **1191/0** 20-module baseline (verify CI supervisor-bridge green on 67cf95f).

### NEXT — finish M0-T056, then R595 (ordered; strictly sequenced)
3a. **Finish M0-T056 accept** (in session15-acc worktree): claim `ready`→claimed, progress, G2 self-check, submit with
   an **evidence-map over the applicable set R344-R357** (14 reqs; `evaluate_task_refs` ok:True, D-010:ALL). Record
   **G3 + G5 at --sha a90ac19** (reuse the delta reports as the gate reports; reviewed code identity is a90ac19).
   Then the **DCV of R344-R357** (directive-compliance-verifier ≠ producer). **R349/AS-5 (isolated live-proof) is
   PENDING the owner** — it needs a Windows/job_object host (C1 gate hard-refuses on POSIX); the DCV verifies R349
   against the owner's live-proof evidence. So: **OWNER TOUCHPOINT #1** = run the AS-5 live-proof per the exact runbook
   in `M0-T056-producer-report.md` §7 (A-D) on an isolated non-product Windows checkout; capture the sealed evidence
   dir + JSON payloads. After the owner returns that evidence → complete the DCV → **accept M0-T056**. Then update the
   M0-T036 checklist to mark P1 resolved by M0-T058 (stale line refs 1283-1298).
4. **Activate R595 + accept allowlist** — ONLY after M0-T056 accepted. Flip `default_actuation_authorization` live +
   `default_mode` off shadow. **OWNER TOUCHPOINT #2** = the accept-allowlist is an owner settings change (widen the
   auto-mode classifier so the supervisor runner may run `accept`/`git push`/`gh` unattended — producer report §7-E);
   never bypass the classifier (R354). Hand the owner the exact allow-rule + confirm the live proof host satisfies C1.

### Accept mechanics (proven session 18; reuse)
- Reviewed content commit FIRST (code + producer report); keep gate/DCV/accept evidence UNCOMMITTED until after
  `accept` (HEAD stays the reviewed sha; material identity = allowed_paths manifest, stable across control-plane
  commits). Fill DCV `reviewed_manifest_sha256` from the G3/G5 gate `content_manifest_sha256`.
- **Empty-set cited directive** still needs a `task_verifications` row (verifier ≠ producer). Non-empty applicable
  reqs each need `{id,state:PASS,evidence,note}`. `hold`-class reqs are NOT deferrable → verify PASS directly.
- Producers auto-isolate off origin/main; guard EVERY producer git write with `git rev-parse --show-toplevel` must
  contain `.claude/worktrees/agent-`. Reviewers read-only IN session15-acc; give ABSOLUTE worktree paths + `git -C`.
  Natural-completion producers resume via SendMessage (worktree persists); never resume a TaskStop-killed one.
- CI `control-plane` runs validate_directive_compliance + test_directive_compliance; `supervisor-bridge` runs the
  FULL `pytest tools/test_agent_supervisor_*.py`. `project-control/**` LF; stage exact paths; commit+push per accept.
  Reviewer/orchestrator `claude-opus-4-8` xhigh; producers UNNAMED.

### Still in force
deployment/G6/Graphify/expansion holds; `default_mode=shadow` until R595 flips; a failed gate / reproduced defect /
unresolvable contradiction STOPS and returns to the owner. Codex model-fallback RESOLVED (non-sticky). M0-T059
correctly NOT triggered (no concurrent recorder added); if a future task adds one, harden recovery.py RMW.

# M0-T107 cycle-2 live journey (R320) — POST-DISPATCH COUNTED STOP at S14; rotation-at-seam DID NOT OCCUR

Recorded by the orchestrator 2026-08-30 (campaign seq 38 → 39). Owner-typed acts, in order,
per the certified handover: (1) `owner-restart` — **WORKED LIVE, first certified use**:
HALTED → IDLE, exactly one transition (13→14), durable audited record (audit 33→35, chain
verified), no flags cleared, nothing dispatched. (2) The certified item-3 start (no repin,
forward-slash paths) — **DISPATCHED** (all probes passed, `run_budget_resumed`,
containment job_object), then **stopped fail-closed**: `no_valid_checkpoint`, exit 11,
**owner touch counted (S14, 1 this start)**, journal parked at PAUSED_RECOVERY.

## 1. Verbatim outcome (owner-typed start)

```
DISPATCHED in limited-auto mode. cycles=1 final_state=PAUSED_RECOVERY stopped=no_valid_checkpoint
forwarded message ids: (none)
owner touches counted: 1 of budget 2 (within budget: True)
run budget: UNLIMITED (no owner wall-clock limit), elapsed 9745.3s (RESUMED)
REFUSED (unsafe, exit 11): no_valid_checkpoint
```

## 2. R320 journey scorecard (what the live evidence actually exercised)

| Leg | Result |
|---|---|
| Owner restart | **ACHIEVED** — the M0-T121 surface worked live on the real preserved journal (first certified use; exactly-once + audit proven in production) |
| Preflight | **ACHIEVED** — all probes passed at the certified identity; dispatched |
| **Fresh Fable rotation** | **DID NOT OCCUR** — see §3, the defect |
| Independent Codex review | NOT REACHED (upstream failure) |
| Actual M0-T107 advancement | NOT REACHED |

## 3. Root cause (primary evidence: audit chain + worker transcripts; read-only)

**The certified rotation at the seam did not fire.** The M0-T113 record and campaign
seq 34–38 all expected it: the worker session had crossed the 400k rotation ceiling at
**604,772 tokens**, and per S11.2 "the NEXT start rotates at the seam." Instead:

1. Audit seq 40 (`claude_unit_completed`): **`context_tokens: 640224`** — the worker ran
   with the OLD session's full context (604,772 grown to 640k+), i.e. the start RESUMED
   the over-ceiling session rather than rotating to a fresh worker. `observed_models:
   ['claude-fable-5']` (a live Fable 5 worker, `model_mismatch: false`), 134 stream
   events, `permission_decisions: []`, `timed_out: false`, `cancelled: false`,
   `malformed_lines: 0`, `checkpoint_contract_appended: true`, **`returncode: 1`**.
2. **Second defect dimension — resume cwd:** cycle 1's worker transcript lives under the
   `wt-m0t107` project slug (session `02b014ee…`, correct isolated worktree). The cycle-2
   resumed worker's transcript (session `798d2f00…`) lives under the **`ctl24`** project
   slug with `cwd: C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` on every record — the
   resumed worker ran in the ORCHESTRATOR'S PRIMARY CONTROL CHECKOUT, not its isolated
   worktree. (No repository write occurred: zero brokered permission decisions; the run
   was read-only discovery — Reads/Greps of campaign/recert control-plane files,
   consistent with a resumed session re-orienting in an unexpected cwd.)
3. **Terminal failure shape:** the worker streamed normally (36 assistant events this
   run) and the transcript ENDS mid-work at 05:44:12Z with no result record; the CLI
   exited **rc=1**. With cumulative context at 640k+ and growing per request, the
   probable terminal event is a provider context-limit rejection on the next request
   (the exact class of failure the 400k rotation ceiling exists to prevent — D-010
   R113/R114). No error record reached the transcript (a CLI-side stderr exit), so the
   provider-side cause is inferred, honestly labeled as such; what is PROVEN is: no
   rotation + 640k context + rc=1 + no structured checkpoint.
4. **The fail-closed discipline worked exactly as certified:** S14 refused to interpret
   the missing checkpoint as success; one synchronous stop counted; PAUSED_RECOVERY;
   nothing forwarded; no external effect; audit chain intact (head 43, verified).

## 4. Protocol determination (R316/R317/R300/R321/R322 — ENFORCED)

* **This IS a post-dispatch counted stop** (audit seq 43 `owner_touch_recorded`,
  basis S14, counted true). The ONE permitted cycle-2 attempt (R316) is **consumed**.
* **NO restart** (R317/R300). None was attempted; none will be.
* **Everything preserved untouched** (R321): journal at PAUSED_RECOVERY (transitions 18,
  audit 43, 0 pending effects, 0 open asks), `wt-m0t107` untouched, both worker
  transcripts untouched, no journal edit, no retry.
* **Touch-budget excess (S16.7):** this start's own counter reads "1 of budget 2", but
  the campaign's standing determination (seq 34) was that the run's owner-touch budget
  stood at 2/2 AT CAP after cycle 1 (S14 + S9), and that "a further counted stop is ALSO
  an excess needing S16.7 disposition." Cumulatively this is the third counted stop of
  the run → **the S16.7 excess condition fires; disposition is the owner's.** Both
  readings are recorded honestly.
* **No full-autonomy claim** (R322/R319): the journey proved the restart channel and the
  fail-closed stop discipline live; it did NOT prove continuous operability — the
  rotation leg failed. No operability claim is made.

## 5. Proposed disposition (owner decision at this seam)

A separate bounded **AD-093 defect task** (Amendment-15 lane; qualifying evidence:
reproduced defect — this report §3) to diagnose and fix **the rotation-at-seam failure**:
why the certified start resumed the over-ceiling session (640k tokens) instead of
rotating to a fresh worker at the seam (S11.2), including the second dimension — the
resumed launch's cwd landing on the primary checkout instead of the producer worktree
(isolation risk; no write occurred this time). Honest naming note: Amendment 15's R301
named "the independent Codex review failure" as the diagnosis target because that was
cycle 1's stop; the actual cycle-2 failure is UPSTREAM of the review (rotation/resume
seam). The condition that fires the lane (a cycle-2 counted stop) HAS fired; the target
differs from R301's wording — recorded transparently for the owner's authorization
rather than silently reinterpreted. Any fix touches `tools/agent_supervisor/**` →
invalidates the fourth certification → re-triggers R247 (fifth recert window) before any
further start. The S16.7 excess disposition is likewise the owner's.

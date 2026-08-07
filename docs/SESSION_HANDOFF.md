# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-05 (late)** after a long session. **The block below supersedes the older
"Where things are" sections further down** (kept only as history); the ledger wins on any conflict.

## CURRENT STATE (2026-08-05 late — confirm against the ledger + git)

- **`task/M0-T036-supervisor-bridge`** — **M0-T036 ACCEPTED (shadow-only) 2026-08-06; MERGED to `main`
  2026-08-07T00:06:56Z (owner-authorized).** accepted count **56**. Delta re-gate V1.2.3 at `4ff4d88`
  all PASS (G3/G4/G5 + DCV); 585-req independent `verification.json` (584 PASS + R593 NA); acceptance
  commit `9d7573f`. **PR #154 MERGED → `main` = `cec785f9ac1037df1fb2e1b114260eb106b7de0`** via the
  repository-required **merge-commit** method (no bypass; branch not deleted). The merged head was a
  **content-empty trigger commit `57ccb44`** (git tree `67e97dda` — byte-identical to acceptance head
  `4f8c1d2`); it existed ONLY to emit a push/PR event so the **8 required checks** could run during the
  **2026-08-06 GitHub Actions major outage** (15:22 UTC; webhooks throttled) — no file content changed.
  All 8 required checks PASS on `57ccb44` (plus 8 non-required, 16/16 green). **SHADOW-ONLY; nothing
  activated.** ⛔ **R595 supervised rehearsal remains a MANDATORY BLOCKING prerequisite before ANY
  activation** (R619; `project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md`).
  - D-007 amendments 13–14 captured (`source-014`/`source-015`): **R609** = the Fable-hold override
    (done — reviews ran on `claude-opus-4-8` xhigh); **R615/R616/R617** = build R207+R593, re-verify, accept.
  - **Independent 577-req D-007 verification recorded** (`reports/M0-T036-D007-verification-577.json`):
    575 PASS, **2 gating UNVERIFIABLE → R207 and R593**. (9-cluster workflow; worst-of dedup.)
  - **R207 BUILT** (4 missing limit knobs; suite 1157/2; commit `c6a2c59`).
  - **R593 — RESOLVED via owner Option A (2026-08-06, D-007-R618).** The live rotation-seam actuation
    (QA-gap-4) is structurally infeasible as a synthetic probe under R594, so it is an **explicitly
    accepted RESIDUAL deferred to the R595 supervised rehearsal** — recorded `NOT_APPLICABLE` (never
    PASS, R621), independent approver = directive-compliance-verifier. **NOT waived.** ⛔ **R595 is a
    MANDATORY BLOCKING prerequisite before ANY activation** (supervised-auto / limited-auto / auto
    product-task / any "live rotation proven" claim) — R619; see `project-control/reports/M0-T036-ACTIVATION-CHECKLIST.md`.
    The `resume-pending-prompt` command (`b1ab12b`) is a built, gate-reviewed operator affordance that
    the future R595 rehearsal will use (G5 flagged one LOW pre-R595 hardening: consume/clear the
    `pending_prompt` record on resume). 2 of 3 V1.2 live legs proven; rotation leg unit/real-process-proven,
    not live-actuated.
- **`control/D-009-depsec-and-m0t019-dispatch`** (batch branch, `…/ctl` worktree) local tip **`a953d0d`**
  (origin at `eb80a4d`, **ahead 1 — not pushed**). M0-T019 transitive-advisory remediation applied
  (sharp 0.35.3 + brace-expansion 1.1.18 overrides; +8 tests → 40; stricter `total==0` audit step).
  **A/B AGE DECISION RESOLVED → OPTION B** (scoped FE-S9 age exception): a **CONCURRENT session**
  (`session_01SQGGRo6sqwzHFhk2gbMTFT`, NOT this one) captured **D-009 amendment 1** (`e96d718`) +
  rebound M0-T019 `blocked→ready→claimed` (`a953d0d`) and is running the exception increment on worktree
  **`…/t19x`** (`task/M0-T019-fes9-exception @ e96d718`). **That session owns this workstream — do NOT
  touch/merge/push it from here.** B-017 stays open until the regenerated-lock CI evidence lands.

## NEXT SESSION — resume checklist (2 owner-gated workstreams)

Start-of-session: `python tools/project_control.py status` + reconcile git/CI. Both branches are on
origin. Reviewers still run `claude-opus-4-8` + `xhigh` (Fable out).

1. **M0-T036 — ACCEPTED (shadow-only), DONE this session.** No further acceptance work. Forward items
   (all owner/activation-gated, NOT acceptance blockers): (i) **R595 supervised rehearsal** — the
   deferred live rotation-seam evidence; **mandatory blocking prerequisite before ANY activation**
   (R619); owner-authorized + independently reviewed when the owner elects to activate. (ii) Before that
   rehearsal, the G5 **LOW hardening**: consume/clear the `pending_prompt/<run_id>` record on a
   successful `resume-pending-prompt` (or record+check the WAIT trigger) so a stale record can't be
   re-approved. (iii) **Follow-up (integrity):** M0-T036's `allowed_paths` carry parenthetical
   annotations, so the content-identity matcher covers no code (identity `08f8db0e` is stable across
   code changes) — worth a control-plane fix so future supervisor edits are identity-tracked.
2. **M0-T019 — OWNED BY THE CONCURRENT SESSION** (`session_01SQGGRo…`), do NOT act on it here. A/B
   resolved → **Option B** (scoped FE-S9 exception; D-009 amendment 1 `e96d718`, batch tip `a953d0d`,
   worktree `…/t19x`). Its remaining path: FE-S9 scoped exception + lockfile regen via
   `generate-lockfile.yml` → CI green → submit → G2/G3/G4/G5 → batch accept (M0-T019 + M2-T014); B-017
   clears with the regenerated-lock CI evidence. Ref `reports/M0-T019-transitive-advisory-blocker-2026-08-05.md`.
- **Reviewers run `claude-opus-4-8` + effort `xhigh`** (Fable out; reviewer-model-fallback). The 5
  flipped reviewer agent files are uncommitted in the working tree — **revert to `claude-fable-5`
  (no effort key) when the owner says "Fable is back."**
- **Nothing accepted/merged/activated this session** (accepted count **55**). M0-T036 stays SHADOW-ONLY;
  limited-auto never activated.
- Environment note: the API was flaky this session (agent stalls / ENOTFOUND); workflow synthesis of
  577 rows exceeds a single agent's 64k output — assemble verification.json in the orchestrator from
  the workflow journal (worst-of dedup, since re-runs can flip a stricter verdict to PASS).

---

_History (pre-this-session, may be stale):_ Refreshed earlier 2026-08-05 at the **D-009 + M0-T019 +
M2-T014 batch-in-flight** point (owner stood the session down after the reviewer-model/fresh-session
decision was surfaced).

## Where things are

| | |
|---|---|
| `origin/main` | `d5d9b50` (owner merged PR #153 = D-008 capture) |
| **active batch branch** | `control/D-009-depsec-and-m0t019-dispatch` — pushed at **`ea5d172`**, **NOT merged**; carries D-009 + M0-T019 + M2-T014 (ledger + both producers' deliverables) |
| task branch (held) | `task/M0-T036-supervisor-bridge` tip `39c90a6` — Fable-5 re-review still held, unchanged |
| accepted tasks | **55** (unchanged — nothing accepted or merged this session) |
| worktrees | `…/ctl` (batch/control), `…/t19` (M0-T019 code @ `2e31711`), `…/t14` (M2-T014 @ `ed12721`) |

**Full resume detail:** `project-control/reports/BATCH-RESUME-2026-08-05.md` (on the batch branch).

## 1. OWNER-GATED RIGHT NOW (do not act without a fresh owner instruction)

- **Reviewer model / fresh-session decision (blocks M0-T019 gates).** Fable 5 hit its usage limit
  mid-batch; every Fable-5-pinned gate reviewer fails on it. Per owner rule 2026-08-05 the reviewers
  fall back to **`claude-opus-4-8` + `effort: xhigh`** while Fable is out (do NOT wait) — but **agent
  pins are cached at session start**, so the 5 flipped reviewer files only take effect on a **FRESH
  session**. Owner's pending choice: **start a fresh session** (recommended — loads 4.8 exactly, resume
  from this branch) *or* **run this batch's reviewers on Opus 5 now** (override; not 4.8). Until then
  M0-T019's G3/G4/G5 cannot run.
- **Nothing merges or accepts without the owner's typed line (D-004-R721).** The whole batch
  (D-009 + M0-T019 + M2-T014) awaits one owner accept pass; nothing was merged in the owner's absence.
- **M0-T036 Fable-5 re-review** remains held (D-007-R607), unchanged this session.
- Standing holds unchanged: deployment/G6/Graphify/expansion. Survey hold **lifted** by the owner
  2026-08-04 (that is why M2-T014 dispatched).

## 2. The batch (main active work — on `control/D-009-depsec-and-m0t019-dispatch`)

- **D-009** — fresh **owner-activated** dependency-security governance directive (2026-08-04; NOT a
  reconstruction). Governance-scoped (`task_types: governance`, `task_ids: M0-T019`) so
  `covers_governance(M0-T019)=True`; authorizes M0-T019's `.github/workflows/` + `CLAUDE.md` edits.
  Registry validates clean. (This unblocked the s19/D-001-R118 governance-path claim guard, which had
  blocked M0-T019 — the CLAUDE.md AND the CI workflows are both governance paths.)
- **M2-T014** (survey Packet A, research): **gate-complete — G0 ✓ G2 ✓ G3 ✓**, `awaiting_gate`.
  data-contract-verifier PASS, independently live-verified every claim (DTM FeatureServer, ACRIS
  307/bandwidth-policy, dataset schemas). 3 **non-blocking** cosmetic corrections in its G3 report
  (col-count 17→16; FeatureServer org provenance note; §11 additivity confirm at merge). Rostered
  security-reviewer leg was covered inside the G3 review (Fable-5 agent couldn't run). **Accept blocked
  only by dependency M0-T019 + owner batch accept.**
- **M0-T019** (frontend security, FULL scope): `claimed`, **G0 ✓**; G2/G3/G4/G5 not yet recorded.
  Producer done (`2e31711`): exact pins (next 15.5.21 / react·react-dom 19.1.2 / eslint-config-next
  15.5.21 / override **postcss 8.5.23**), age-gate script + 32 passing tests, 3 CI workflows, policy
  doc, CLAUDE.md rule. **Flag for G5:** packet said `postcss 8.5.10`, but 8.5.10 is advisory-hit
  (GHSA-6g55/r28c/fxqj); producer chose 8.5.23 = minimum advisory-free AND ≥7-day-old — a
  packet-mandated re-verification, **not a waiver**.
- **Lockfile CI wrinkle (M0-T019):** the committed `apps/web/package-lock.json` is still the pre-patch
  15.3.4 tree (thin-client — no local npm). `.github/workflows/generate-lockfile.yml` regenerates it,
  but it is `workflow_dispatch` and **not on `main`**, so it can't be triggered until it reaches main.
  **Order:** get the workflow onto main → dispatch on the branch → regenerate + validate the lock →
  ci.yml on the regenerated lock → THEN submit M0-T019 + record G2/G3/G4/G5 (so their content-identity
  isn't stale). Do NOT record M0-T019 gates before the lock is final.

## 3. Standing rules / discipline (carry forward)

- **Reviewer model fallback (owner 2026-08-05):** Fable 5 → `claude-opus-4-8` + `effort: xhigh` when
  Fable is unavailable; do NOT wait. The 5 reviewer agent files (`code-reviewer`, `security-reviewer`,
  `qa-engineer`, `control-plane-verifier`, `directive-compliance-verifier`) are flipped in the primary
  working tree (**uncommitted**; loads on next fresh session). **REVERT them to `model: claude-fable-5`
  (no effort key) the moment the owner says "Fable is back."** `data-contract-verifier` is already
  non-Fable; the `orchestrator` agent was left as-is (main session already Opus 4.8). Memory:
  `reviewer-model-fallback`. Record a D-004 amendment as the durable governance trail.
- **Owner escalation boundary (D-008, merged to main):** stop-and-ask ONLY for (1) credentials/
  accounts/payment or (2) legal/professional sign-offs, plus a genuine unresolvable contradiction;
  otherwise walk the accepted-dependency chain forward under standard gates. When stopping, give plain
  English + the exact line to type.
- **Batching (owner 2026-08-04):** don't pause for owner approval between tasks; accumulate finished
  tasks at submit; surface the whole batch once with the exact accept lines.
- **Producers ran clean on `claude-opus-4-8`** (frontend-engineer, official-source-researcher) — the
  Fable-5 problem is reviewer-only.
- **Branch model that works:** each task's ledger ops AND its producer deliverables must sit on ONE
  branch so the in-regime submit's content-identity stamps at HEAD (learned the hard way — the batch
  branch consolidates deliverables via `git merge <task-branch>` before submit).
- Ledger writes go through `tools/project_control.py` only; directive registry must validate clean;
  write `project-control/directives/**` with explicit LF (the eol=lf/CRLF digest trap). Task files
  under `project-control/tasks/**` are CRLF — preserve on edit.

## 4. Session-end status

Nothing merged, nothing accepted, no owner gate closed in the owner's absence. Everything is committed
and pushed on the batch branch (`ea5d172`); the batch is intact and resume-safe. The next action is the
owner's: pick the reviewer-model/fresh-session path (§1), after which a resuming session loads the
Opus-4.8 reviewer pins, drives M0-T019's lockfile CI and G2–G5, and surfaces the whole batch
(D-009 + M0-T019 + M2-T014) for one accept pass. The 5 reviewer-pin edits sit uncommitted in the
primary working tree by design (temporary Fable fallback) — do not discard them; revert to Fable when
told Fable is back.

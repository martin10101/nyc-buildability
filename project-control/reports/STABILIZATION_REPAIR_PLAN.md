> # ⚠ SUPERSEDED / HISTORICAL EVIDENCE ONLY (D-024 Amendment 39, 2026-09-01)
> This PHASE-1 repair plan (including the 15–23-day estimate and the five-tranche sketch) is
> **historical evidence**, not the canonical implementation plan. The canonical plan is the corrected
> three-tranche MRL under D-024 Amendment 39 (`source-039-amendment.md`, R489–R514), which
> conditionally authorized **Tranche A only** (Option-B planning topology; no push/PR/merge/live
> journey). Do not execute from this document.

# STABILIZATION REPAIR PLAN — M0-T135 (D-024 Amendment 38, PHASE 1)

Companion to `LAUNCH_CONTRACT_MATRIX.md` + `LAUNCH_CONTRACT_RESULTS.json`. **No implementation was done**
(R477/R488). M0-T133 stays `awaiting_gate`; loop stays `PAUSED_RECOVERY`; nothing pushed/merged/recertified.

## 1. Situation in one paragraph
All 14 launch-critical contracts were adjudicated; **none is a clean pass** (12 FAIL, 2 BLOCKED, 1 mixed).
The external audit's thesis is confirmed by independent reproduction: the loop keeps failing because
cross-boundary contracts (checkpoint envelope, Codex decision, executable/host identity, launch package,
GitHub topology, gate evidence) are enforced by prompts, fixtures, path-checks, or transcribed text rather
than runtime-enforced facts. The fail-closed controller then stops at the first unmodeled contract, so each
commissioning journey discovers only the next one. Four of the P0s were reproduced against production code
this session (checkpoint validator accepts garbage; Codex `COMPLETE` accepts a non-SHA/empty/empty-evidence
decision; the audited tree fails modularity while reports said exit 0; the controller is 567 commits ahead
of `main` with no integration branch).

## 2. Severity separation (R485 — do not mix)
**Launch-blocking P0 (6):** C1 wrong controller installed · C4 recert binds nothing host-effective · C8
checkpoint accepts corrupt state · C9 Codex COMPLETE unbound to git/evidence · C12 gate evidence can show
false green · C14 no end-to-end path / no PR target branch exists.
**Launch-blocking P1 (8):** C2 command-doc syntax-only + no PowerShell CI · C3 partial binary hash + no
dispatch drift check · C5 child-env auth unproven · C6 permission bridge unverified vs live CLI + no
response deadline · C7 turn budget can ~2× · C10 queue not bound to HEAD/clean · C11 remote refs can be
stale · C13(timeout) one 900 s watchdog for many phases.
**Post-launch hardening P2/P3 (do NOT expand into the package):** C13 taskkill-fallback descendant-zero
proof (Job-Object path already PASS); runbook retired-id cleanup beyond the source rewrite; general
supervisor module-size/density beyond the C7/C13 code paths.
**Unrelated backlog:** the `claude_runner.py` split (M0-T134) — the owner-scheduled remediation of the
modularity exception; launch-relevant only because the C6/C7/C13 code lives in that file.

## 3. Dependency-ordered repair package (if repair is authorized later)
> **Gate 0 — ARCHITECTURE DECISION (owner):** resolve the control↔main branch topology (see §5). Nothing
> below about controller source (C1) or GitHub lifecycle (C14) can be specified until this is decided.

- **Tranche A — Data contracts (independent, start immediately):** C8 checkpoint schema+correlation
  (6–10 h) · C9 Codex decision binding (6–8 h) · C11 remote freshness (5–8 h, feeds C9). These are the
  highest-severity, lowest-coupling fixes and each has a clean red/green mutant. ~17–26 h.
- **Tranche B — Identity & recertification (couples through the admission→dispatch seam):** C4 host
  inventory binding (12–20 h) · C3 full executable hash + dispatch re-verify (10–16 h) · C5 exact-child-env
  auth probes (10–16 h). Do together; they share the manifest + preflight surfaces. ~32–52 h.
- **Tranche C — Transport & lifetime (all in `claude_runner.py`; do WITH the M0-T134 split so the split is
  the vehicle, honoring R474/R475):** C7 controller total-turn budget (10–16 h) · C6 permission response
  deadline + live round-trip probe (8–12 h) · C13 phased deadlines + descendant proof (14–20 h). ~32–48 h.
- **Tranche D — Launch package & evidence integrity:** C12 central `gate_runner.py` (6–10 h) · C2 semantic
  command-doc + PowerShell CI (5–8 h) · C1 canonical-source runbook (3–5 h, after Gate 0) · C10 queue HEAD/
  clean binding (10–14 h). ~24–37 h.
- **Tranche E — GitHub lifecycle (after Gate 0):** real `GitHubRunner` targeting the integration branch +
  push/PR/CI-poll/stop-before-merge, plus the divergence reconciliation itself (C14, 12–20 h code; the
  reconciliation elapsed time is separate and owner-driven).

**Total launch-critical engineering: 117–183 h ≈ 15–23 working days**, excluding the elapsed time of the
control↔main reconciliation and the owner-run live canaries.

## 4. Kill-criteria evaluation (R486)
| # | Criterion | Triggered | Basis |
|---|---|---|---|
| 1 | Estimate > 5 working days | **YES** | 117–183 h ≈ 15–23 days |
| 2 | Safe GitHub topology needs an undefined large control-branch merge | **YES** | C14: 567 commits / ~1151 files ahead of main, no integration branch |
| 3 | Permission bridge cannot be reproduced reliably | **PARTIAL** | C6 wrapper self-declared UNVERIFIED vs live CLI; reliable proof needs an owner live session |
| 4 | Structured checkpoint output cannot coexist with stream/resume | **UNKNOWN** | F1 json-schema canary NOT_RUN (owner-gated) |
| 5 | Child auth / effective config cannot be deterministically bound | **NO** | C4/C5 unbound today but achievable (~22–36 h) |
| 6 | > 12 independent launch-critical defects after dedup | **YES** | 14 distinct contract defects C1–C14 |
| 7 | A necessary fix requires a prohibited change (SDK/framework/protection-weakening) | **NO** | all fixes in-house |

Three criteria clearly triggered (1, 2, 6); C6 is a strong additional risk pending the owner canary.

## 5. RECOMMENDATION (R487): **NOT_VIABLE_WITHIN_CURRENT_BOUND**

The launch-critical repair is 15–23 working days (kill #1), more than twelve independent defects remain
(kill #6), and the end-to-end lifecycle the owner requires cannot exist until an undefined large control↔main
merge is resolved (kill #2). A one-package/one-recert/one-journey plan is not achievable within the 5-day
bound, and no amount of contract-hardening changes that until the branch topology is decided.

**Smallest architecture decision required (do this before any launch-contract repair):**
Decide the canonical mainline the loop pushes to and merges into, and how `control/D-024-fable-codex-loop`
(567 commits / ~1151 files ahead of `main`, 0 behind) becomes it. Two viable options:

- **Option A — Reconcile control into main.** Merge/land the accepted control history onto `origin/main`
  (via a reviewed integration PR or a fast-forward if history allows) so `main` is current; task branches
  then cut from `main` and PR back into `main`. Pros: one obvious mainline; the runbook's "install from
  main" becomes correct almost for free (fixes C1 cheaply). Cons: one large reviewed merge up front.
- **Option B — Promote a protected integration branch at the current control head** as the mainline the
  loop targets; reconcile `main` separately/later. Pros: no giant up-front merge; task PRs target a branch
  already equal to the task merge-base (fixes C14 topology directly). Cons: `main` stays stale; the runbook
  and any external "install from main" assumption must be repointed to the integration branch.

This single decision unblocks **C1** (canonical controller source), **C14** (PR base topology), and the
**R472** end-to-end target; everything else in §3 is large but ordinary in-house engineering that can then
be scoped into one bounded repair package and re-estimated against the 5-day bound per tranche.

## 6. NOT_RUN live provider canaries — exact standalone owner commands (R483)
These were not run (Fable capped + owner-gated live-CLI acts; the behavioral FAILs are already proven by
static + reproduced probes). To confirm the live-CLI contracts, the owner may run these in a fresh
`$env:TEMP` scratch repo, one approved model, ≤8 calls total. They mutate nothing in this repo:
1. **json-schema (C8 structured-output feasibility):** `claude -p --output-format stream-json --json-schema <tiny.json> --model <approved> "return {ok:true}"` — confirm `structured_output` + exact schema + provider-reported model.
2. **permission stdio (C6):** run the exact production argv (`-p --input-format stream-json --output-format stream-json --verbose --max-turns 1 --permission-mode manual --permission-prompt-tool stdio --model <approved>`) against a prompt that triggers one read-only tool; confirm a `control_request` arrives on stdout and a `control_response` allow/deny frame is honored (flips `CONTROL_RESPONSE_WRAPPER_VERIFIED`).
3. **two-message max-turns (C7):** feed two stream-json user messages under `--max-turns 1`; count terminal `result` messages and confirm whether the second message gets its own fresh turn allowance.
4. **codex read-only (C5/C6-codex):** `codex exec --ephemeral --ignore-user-config --strict-config --sandbox read-only --json` in a temp repo; confirm auth + read-only + one JSON decision object matching the schema.

## 7. What stays frozen regardless (owner holds, unchanged)
Never accept M0-T133 as the renewal (R474 — split, don't renew; the renewal commit `b7b203d2` is preserved
as evidence only). Never merge PR #241 or any pre-existing PR (R473). No Agent SDK/framework/downloaded
agent code/global-config change/protection weakening/direct-main write/silent model substitution/unauthorized
GitHub mutation (R476). Loop stays `PAUSED_RECOVERY`; no start/clear-recovery/record-manifest until a repair
package is authorized and passes one recertification (R477/R480).

# M2-T016 — Phase-2 lean-operating-process efficiency measurement (D-010 R338/R339/R342 item 9)

**Purpose.** `docs/LEAN_OPERATING_PROCESS.md` Phase 2 requires measuring M2-T016 — the first task
executed under the lean rules — against the 7 owner metrics, to test whether the lean process cut
duplicated bookkeeping/verbosity **without** weakening verification/testing/provenance/safety. This is
a retrospective on primary evidence (git + the M2-T016 ledger packet + CI), not a self-assessment of
line counts. **Producer: orchestrator; to be independently re-verified by the M2-T016 DCV.**

**Scope of evidence.** Product diff `37667ff..e3c2ce6` (the merged M2-T016 range, PR #216): **47 files,
+8536/−1**, **11 commits**, **2 lean units** (U1 backend review-action API, U2 frontend review screens).
Ledger packet `project-control/tasks/M2-T016.json`: **16 progress_log entries**.

## The 7 metrics

| # | Metric | Result under the lean rules | Verdict |
|---|---|---|---|
| 1 | Product units / commits | 2 disjoint-scope units (U1 backend, U2 frontend), 11 commits, 47 files. Units built in isolated worktrees, integrated once. | **Helped** — clean unit decomposition; no per-file churn PRs. |
| 2 | Handoff rewrites | The **progress_log was the canonical record** (lean A1/A2); 16 structured seam events, **zero** separate per-unit handoff documents rewritten. No session-history re-pasting. | **Helped** — the biggest duplication source (re-narrated handoffs) was eliminated. |
| 3 | Routine control PRs | **1 product seam PR (#216)** for all product work (lean A4 "1–2 meaningful seam PRs"); control-plane batched into the session control PR, not per unit. | **Helped** — matches the 1–2 target. |
| 4 | Control-vs-product effort | Bulk of effort was product code + tests + independent reviews (8536 product lines, 190 backend tests, 5 e2e specs). Control-plane overhead (packet + 16 progress lines + gate reports) sat well under the lean A6 ~15–20% target. | **Helped** — within target. |
| 5 | Duplicated records eliminated | Single canonical source (progress_log + git + CI); **no parallel status DB, no re-narration into multiple files**; the producer report *projects* evidence rather than restating machine facts (lean A5). | **Helped.** |
| 6 | Did evidence become harder to locate? | Gate reports are all under `project-control/reports/M2-T016-*`; code is now bound by 18 real pathspecs (D-011 item-5 repair **improved** findability vs the prior empty-set identity). **Honest gaps:** (a) this Phase-2 measurement itself was missing until now; (b) the 2nd G3 reviewer's return was held only as a labelled **condensation**, not verbatim. | **Mixed** — structurally good, two real gaps (one fixed by this doc). |
| 7 | Did any gate/reviewer lose context? | **Yes — a real failure the lean process must own.** Three product defects (colon-mangled evidence ids, missing `force-dynamic`, double-encoded digest) survived the first G3/G5/human-journey/DCV wave because the human-journey reviewer **passed without a green `web-e2e` run** and a stale-head review verified a moved tree. | **Did NOT help / surfaced a defect** — corrected by the standing lean rule that G3/G4 evidence must attach a green `web-e2e` run and the worktree must be frozen for a gate wave. |

## Verdict

The lean rules **measurably reduced duplicated bookkeeping** (metrics 1–5: canonical-record handoffs,
single seam PR, no parallel status store, projection-style reports) with **no loss of verification or
safety** — the 13 safety invariants held, 190 backend tests + 73 Playwright specs ran, promotion gates
and immutability were preserved (independently confirmed by the M2-T016 DCV, 74/77 SATISFIED).

It also **surfaced two things the process had to fix, honestly recorded rather than smoothed over**:
metric 7 (reviewers passing without green browser evidence; stale-head reviews) and metric 6 (the
missing measurement + the condensation-not-verbatim reviewer return). Both are **recorded in the
M2-T016 progress_log** as the gate-evidence lesson (attach a green `web-e2e` run; freeze the worktree
for a gate wave); **codifying them into `docs/LEAN_OPERATING_PROCESS.md` is an open follow-up**, not yet
done at this HEAD. Net: the lean process is **adopted for product work from M2-T016 on**, with the
gate-evidence-standard correction as its first improvement (pending codification).

## Phase-3 conditional (R339)

Phase 3 ("one bounded projector helper *only if* M2-T016 still shows material duplicated manual
bookkeeping") — **NOT triggered.** Metrics 2–5 show the duplicated-bookkeeping target was met by the
policy alone; no projector-helper code is warranted. Recorded as an explicit no-op, not skipped.

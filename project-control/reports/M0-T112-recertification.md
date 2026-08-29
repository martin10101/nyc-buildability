# M0-T112 — Final golden re-certification at the frozen post-addition identity

Task: M0-T112 (unit M; D-024 Amendment 8, rows R231/R232/R246/R247/R248/R249).
Recorded by: orchestrator (fable-orchestrator-session), 2026-08-28, campaign seq 25.
Supervisor-freeze qualifying evidence: **D-024-R247**.

## 1. Why this re-certification exists (R247)

Any supervisor or operator-channel change after a golden-run identity invalidates the
affected final certification. After the M0-T096 (unit I) certification, TWO owner-required
capabilities landed: **M0-T110** (unit K, `/loop-codex` Codex discussion channel — accepted,
deliverables `ba25516`+`c8b38ba`) and **M0-T111** (unit L, one-way Telegram sink — accepted,
deliverable `c9b3b9a`, corrections `8574c58`). Both touched `tools/agent_supervisor/**` and
the operator channel. This unit re-runs the full certification AT the final frozen
post-addition identity. Only after this unit is accepted may the R187/R595 activation
package be PRESENTED (R232/R246); presentation and activation remain owner-gated.

## 2. The FINAL frozen post-addition identity (what was certified)

* Certification run head: **`a4f94b7`** (branch `control/D-024-fable-codex-loop`; working
  tree clean on all code paths during every run; only pre-declared control-plane files
  changed at this seam).
* Supervisor material identity: `tools/agent_supervisor/**` last moved at **`8574c58`**
  (the accepted M0-T111 correction round); directory tree object at the run head:
  `132e698c15a9f9412d53905e45ce0ae0724abe15`.
* Golden-run pack: `tools/test_agent_supervisor_golden_run.py` last moved at **`635fac5`**
  (unit-I correction round; 1,040 lines, 40 tests), blob
  `d2946392f1c14ba086d63c60f2e125db6863bc10` at the run head. **Not edited by this unit** —
  re-run only (the allowed_paths listing existed solely in case a re-run exposed an
  identity-stamp defect; none did).
* Every commit between the unit-I certification and this head that touched supervisor code
  is one of: unit-K deliverables, unit-L deliverables, or their accepted correction rounds —
  i.e., the post-addition identity is exactly "unit-I system + accepted K + accepted L".

## 3. Re-run evidence (all executed at the identity above, foreground, this seam)

| Pack | Command scope | Result |
|---|---|---|
| FULL golden-run pack | `tools/test_agent_supervisor_golden_run.py` | **40 passed, 0 failed** (23.49s) |
| Affected packs | operator_channel + codex_channel (K) + telegram_sink (L) + adversarial + endurance + phase1 + reviewer | **493 passed, 0 failed** (112.20s) |
| WHOLE supervisor suite (freeze baseline) — chunk 1/4 (files 1–15, `adversarial`…`endurance`) | 59-file suite, alphabetical 4-way split | 677 passed |
| — chunk 2/4 (files 16–30, `ephemeral_review`…`operator_channel`) | | 724 passed (0:02:51) |
| — chunk 3/4 (files 31–45, `os_acl`…`reviewer`) | | 683 passed, 2 skipped |
| — chunk 4/4 (files 46–59, `rotation`…`turnover_live_signal`) | | 610 passed |
| **Whole-suite total** | 2,696 collected | **2,694 passed, 2 skipped, 0 failed** |

The golden-run pack re-confirmed at this identity the observed complete loop: the two-unit
golden run from the exact owner `start` command crossing one safe rotation (three launches,
zero human continuation, exactly-once forwards), the injected-controller-restart resume
without duplicate work, and the injected refusal/quota/fallback/ambiguous-effect scenarios
all failing closed — all lane-1 INJECTED (Amendment 7); the natural-event lane stays
`pending_live_observation` and gates only the 4.8 bridge's live actuation (R228).

**Baseline reconciliation (freeze rule):** the last recorded full-suite figure (seq 24,
pre-correction run) was 2,690 passed + 2 skipped = 2,692; this run collects 2,696. The +4
delta is exactly the four L-pack tests added by the accepted `8574c58` correction round
(authorized-canary-no-env, task_id dedup, queue-growth, identifier redaction+cap). No test
was removed, no unexplained drift.

* **CI (confirming whole-suite run on the pushed SHA):** the standard 20-check CI runs on
  the pushed certification tip (this report + the activation-package refresh commit). The
  exact tip SHA and its 20/20 conclusion are pinned in the M0-T112 `progress_log` at the
  submit seam and are independently verifiable via the check-runs API. Prior tip `a2aec11`
  was 20/20 green at this seam's start.

## 4. Activation-package refresh (REFRESH-ONLY, items 10–12)

`project-control/reports/M0-T096-activation-package.md` items 10 (identity and evidence),
11 (independent review verdicts), and 12 (golden-run evidence) now cite the post-addition
identity and this re-certification; the Amendment-8 sequencing banner is updated to record
that M0-T112 re-certification evidence exists, while presentability continues to require
M0-T112 ACCEPTANCE. No other item changed; the package still activates nothing
(DEFAULT-OFF; R187/R595 owner-gated).

## 5. Known non-blocking residuals carried into the certified identity (disposition)

Unanimously judged non-blocking at the T111 delta re-attestations; NOT fixed here because
supervisor source is outside this packet's allowed_paths and certification must not mutate
what it certifies:

1. `_already_queued` digest normalization — compares the STORED post-builder summary digest
   vs the RAW notify-time digest, so outage growth suppression is best-effort for
   redaction/truncation-altered summaries (inherited S13.10 queue behavior; at-least-once
   delivery preserved).
2. Unit-I `live_observation.py:296` raw `source_record_key` one-liner.
3. Unit-K boundary queue write-only/inert notes + report line-count nit.

Recommended follow-up: one small bounded task after this unit. **By rule (R247), any such
supervisor change re-invalidates this certification and re-triggers a re-run** — the owner
may prefer to weigh that at the activation decision.

## 6. Prohibition compliance (R248)

No continuous-mode activation, no live 4.8 bridge enablement, no PR #241 touch, no Agent
SDK admission, no new MCP servers/channels, no global Claude settings modification, no
owner-boundary crossing occurred in this unit. Supervisor remains SHADOW-ONLY. The unit
wrote only: this report, the G0 readiness report, the activation-package items-10–12
refresh, and control-plane records.

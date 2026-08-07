# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA written here as still-current.**
This file is orientation only. Operating rules, gates, and workflow routes live in `CLAUDE.md`.

Refreshed **2026-08-07 (session 5, CP-0042)**. **The block below supersedes the older sections**
(pruned per the context-budget guard); the ledger wins on any conflict.

## CURRENT STATE (2026-08-07, session 5 — confirm against the ledger + git)

**Dormant batch CLOSED; accepted count 66.** The D-009/M0-T019/M2-T014 batch was reconciled onto
main (merge of `a953d0d`, two additive-union conflict resolutions) and closed on
`control/D-009-batch-close` (PR #176):

- **M0-T019 ACCEPTED** — frontend security tree final (next 15.5.21 / react+react-dom 19.1.2;
  overrides postcss 8.5.23 / sharp 0.35.3 / brace-expansion 1.1.18 / js-yaml 4.3.1). The D-009 am.1
  FE-S9 exception went **MOOT BY TIME LAPSE — never implemented; gate ships byte-unchanged, no
  exception path** (R009 NOT_APPLICABLE approved by DCV; R021 satisfied-by-reconciliation after a
  real G3 FAIL→reconcile→PASS cycle over pre-edited scenario text). Round-2 advisory js-yaml
  CVE-2026-59870 remediated (4.3.1, ≥7d, advisory-free, no exception). Lock regenerated + validated
  by CI (run 31211311419, bot commit `1d678fd`); PR #176 checks 33/33 green. Gates G0/G2/G3/G4/G5
  PASS at identity `46e4d83e`; DCV 19 PASS + 1 NA. **B-017 + B-012 + B-013 resolved** (the standing
  owner deployment/G6 hold is separate and REMAINS IN FORCE).
- **M2-T014 ACCEPTED** — survey research Packet A; gates G0/G2/G3 at stable identity `73b36e60`;
  its findings now feed the (HELD) survey-ingestion product tasks.
- **D-010 amendments captured:** am.11 = session-5 launch [R121] (PR #175); **am.12 = OWNER
  PRE-ACTIVATION DECISION [R122–R133]** (PR #177); am.13 = R121 binding correction. Registry
  validates clean.
- G5 non-blocking residue: **LOW-1 evaluate `ignore-scripts=true` for apps/web** (defense-in-depth;
  fold into future dep-sec work). G4 LOW observations recorded in the reports.

## NEXT SESSION — resume checklist (session 5 → 6)

1. Start-of-session: `python tools/project_control.py status` + reconcile git/CI (origin/main should
   contain the PR #176 merge; checkpoint CP-0042). Machine-readable handoff:
   `project-control/reports/session-handoff-2026-08-07-5.json`
   (digest `c3b545b210d46e159fcd96cda0ca456b425522826b25d841bf3eb5aaf73a01f5`) — verify: sha256
   over `json.dumps(doc, sort_keys=True)` with `digest=""`.
2. **NEXT UNIT (owner am.12, R123–R130): the PRE-ACTIVATION task.** Contract ONE narrowly bounded
   task (fresh M0-Txxx via /start-controlled-task, bind D-010 refs incl. R122–R133) containing ONLY:
   (a) M0-T045 G5 LOW-1 fix — bind forwarded prompt bytes to the OPERATOR-NAMED approval digest at
   approval time + adversarial tests; (b) M0-T045 G4 estop-fork follow-up — regression test locking
   the fail-closed forked-audit-chain behavior per the owner acknowledgement (R126 verbatim);
   (c) Windows OS-ACL hardening of the immutable controller config per the R128 boundary (read-only
   to the unelevated process, parent-dir protection, UAC elevation, digest verification retained,
   bounded unelevated probes). NO service/daemon/enterprise identity/separate infra/redesign (R129).
   Normal G3/G4/G5 + DCV gates (R130).
3. **After that task is accepted:** mechanically reconcile ALL remaining
   `M0-T036-ACTIVATION-CHECKLIST.md` items as satisfied, then **present the owner the exact
   supervised-auto activation decision line** (R131/R132). ⛔ Do NOT activate without the owner's
   typed decision. ⛔ **M2-T015/M2-T016 stay HELD until supervised-auto activation** (R133) — they
   are the supervised-auto proof tasks.
4. Carried rules: task branches from origin/main in the orch worktree (`…/orch`); spawn PRODUCERS
   UNNAMED; classifier denial ⇒ try exact-path staging first, else STOP and surface the `!` line;
   `project-control/directives/**` explicit LF; task files CRLF-tolerant via CLI; ADR-006 Tier A
   merges after green checks; commits stage exact paths (no directory adds).
5. **Reviewer models:** gate reviewers run `claude-opus-4-8` + `xhigh` (standing fallback; the 5
   flipped agent files remain uncommitted in the PRIMARY checkout — revert to `claude-fable-5` pins
   when the owner says "Fable is back"). Orchestrator ran `claude-fable-5`. Primary checkout now
   sits on `main` (synced this session; flips preserved).
6. Standing holds unchanged: deployment/G6/Graphify/expansion; SHADOW-ONLY posture intact; R595
   activation boundary now governed by am.12 (R131).

---

_History: superseded session blocks (sessions 1–4 = CP-0037..CP-0041; the 2026-08-05 batch states)
are pruned per the context-budget guard — recover with `git log -p docs/SESSION_HANDOFF.md`; the
ledger remains authoritative._

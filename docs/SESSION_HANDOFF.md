# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and reconcile against the remote: **origin may have
advanced; no SHA here is guaranteed current.** This file is orientation only. Operating rules,
gates, and workflow routes live in `CLAUDE.md`.

## Handoff - seq 99: 184 accepted; M5-T016 (address Packet 2) BUILT + PUSHED, CI in flight; wave next

Generated 2026-09-12 ~03:15 ET by session `5967607e-525a-430f-b258-e908e6db62e6` (owner ran
`/session-handoff`, no reason stated). Root `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, branch
`candidate/D-024-mrl-option-b`, HEAD `49bd086b` **pushed** (a handoff/state commit follows).
Dirty at generation: `project-control/state.json` (timestamp-only, committed with this handoff);
untracked `.claude/agent-memory/qa-engineer/*` + `scratchpad/` (left per policy). `main` untouched
at `d8b3899f`. PR #241 OPEN — NEVER merge.

## STATE (verify live; ledger wins)

1. **Accepted = 184.** This session landed SEVEN acceptances (177→184): M2-T021, M4-T010, M4-T009,
   M4-T011, M2-T022, M5-T014, **M5-T015** (address-entry UI Packet 1, full arc: 4-gate wave →
   required-correction rework → delta attestations → DCV → accept `c9c4ce16`). Owner decision
   D-039 removed the M4-T010/T009 dependency edge to G6-parked M4-T001; the G6 hold is UNTOUCHED.
2. **M5-T016 (address Packet 2) — claimed, producer material PUSHED, CI UNCONFIRMED.** Ledger 70%
   `in_progress`. Packet `ffaa85dc` (G0 PASS admin); producer commit `65d72bfd`; progress record
   `49bd086b` = HEAD. Built: `AddressConfirmCard` (ZoLa link via the CONFIRMED
   `https://zola.planning.nyc.gov/bbl/<canonical>` route — research preserved at
   `docs/design/zola-deeplink-url-confirmation.md`; both hrefs built ONLY from
   `validateBblInput`-passing BBL; provenance disclosure with endpoint HOST only + not-verified
   posture); `AddressOutcomeCards` extraction (screen now 264 lines, modularity warn gone);
   additive `address-api` view fields; 10-test confirm pack + strengthened resolution pack
   (per-state body copy, hostile-resolved + hostile-BBL fixtures). Carried M5-T015 findings
   discharged in-code except G5 F-1 (flag-name divergence `INTERNAL_RULE_EVAL_UI` vs
   `INTERNAL_RULE_EVAL_ENABLED`) — a report-only OWNER note (deploy-affecting rename).
3. **CI on `49bd086b` was IN PROGRESS at handoff** (run visible via
   `gh run list --branch candidate/D-024-mrl-option-b --workflow CI --limit 1`). The session's CI
   monitor died with the session — CHECK IT LIVE FIRST. Expected: everything green except the two
   standing owner-gated reds (web-dependency-security = npm audit/Next.js RCE authorization;
   control-plane = CRLF digest normalization decision).
4. **Campaign-continuity tool fails closed** (exit 1: legacy D-032 records invalid — pre-existing;
   the active D-024 record's NEXT is STALE vs the D-038 product queue). Per the profile: fall back
   to the ledger + git; do not hand-edit campaign records.
5. Sub-agents: NONE live. This session's four M5-T015 reviewers, the DCV verifier, and the ZoLa
   researcher all completed and their returns are preserved under `project-control/reports/` and
   `docs/design/`. Spawn FRESH reviewers for the M5-T016 wave.

## NEXT ACTION (in order)

1. Confirm CI on `49bd086b`: if `web` + `web-e2e` green → capture
   `project-control/reports/M5-T016-ci-evidence.txt` (mirror the M5-T015 file: run id, job ids,
   vitest counts, the two owner-gated reds noted), write the empty-applicable evidence map
   (`M5-T016-evidence-map.json`, `{"requirements": {}}` + note), commit, `submit` at that HEAD,
   push. If red: fix bounded (test-mechanics posture: 1 repair commit max, then re-CI).
2. Dispatch the four-reviewer wave at the pushed head: G1 code-reviewer, G3
   **human-journey-reviewer** (the packet's roster — Packet 2 carries the journey walkthrough),
   G4 qa-engineer, G5 security-reviewer. Reviewer briefs: packet S1–S8 +
   `M5-T016-producer-report.md` §2–4 (href discipline is the core risk) + the ZoLa research doc.
3. Then the proven M5-T015 flow: preserve reports verbatim → corrections (if any) as ONE bounded
   commit + delta attestations → record gates ONCE at live HEAD → `awaiting_gate→rework→resubmit`
   restamp if producer content moved after submit → independent DCV (empty-applicable expected) →
   accept → handoff/memory update.
4. After M5-T016: next queue item per the ledger (nothing else mid-flight). Packet 3 (lot
   outline/MapLibre) stays on the owner-review expansion hold — do not plan it.

## STANDING RESTRICTIONS (unchanged)

NEVER merge PR #241. Supervisor frozen/SHADOW-ONLY (changes need cited D-024-R###). Expansion hold
(`.claude/rules/expansion-agent-dispatch-hold.md`). No bare `git stash`. No new packages
(dependency policy; no waiver of advisories ever). No hosted web deploy before the Next.js RCE fix
(owner-gated). API URL private; Geoclient key ONLY in owner env + Render dashboard. Thin client
(no local node_modules/DBs/bulk data; CI is the executable authority for apps/web). G6 on M4-T001
= owner-only Section 20/Tier D. Stop-and-ask only for credentials/payments/legal (D-008).
Bootstrap Gate 0 before any write: cwd must BE this worktree root; `/mcp` must report no servers.

## AUTHORITATIVE FILES (smallest set)

`project-control/state.json` + `tasks/M5-T016.json` (live task truth) · `tasks/M5-T015.json` +
`reports/M5-T015-*` (the completed-arc pattern) · `reports/M5-T016-producer-report.md` +
`reports/M5-T016-G0.md` · `docs/design/address-entry-confirm-design-spec.md` +
`docs/design/zola-deeplink-url-confirmation.md` · `CLAUDE.md` · this file.

## COPY INTO THE NEW SESSION

resume from handoff seq 99: work from durable repository evidence, not assumptions about the prior
conversation. Verify root/branch/HEAD (`git rev-parse --show-toplevel`, expect
C:/Users/MLFLL/Downloads/nyc-zoning/ctl24 on candidate/D-024-mrl-option-b), Bootstrap Gate 0
(cwd = worktree root, /mcp empty), read CLAUDE.md + docs/SESSION_HANDOFF.md, run
`python tools/project_control.py status`, reconcile handoff vs live git/CI (ledger and CI win;
origin may have advanced). Campaign tool fails closed — use the ledger. Then execute the handoff's
NEXT-ACTION list starting at item 1 (M5-T016 CI check → evidence → submit → four-reviewer wave).
Report READY TO RESUME or BLOCKED before changing anything. Stop only for owner-only items
(credentials/payments/legal/PR #241/expansion hold/G6).

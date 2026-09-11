# Session Handoff - NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume read it live -
`python tools/project_control.py status` - and reconcile; no SHA here is guaranteed current.
Orientation only; rules/gates live in `CLAUDE.md`. CURRENT-ONLY: `context-budget` CI fails > ~4000 tok.

## Handoff - seq 96: M5-T004 FAIL 4-1 -> PASS 5-0; two ZR snapshots captured; loop ran and died on a timeout

1. **Identity.** Root `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`, branch
   `candidate/D-024-mrl-option-b`, HEAD **`b3fbcd97`**, origin
   `https://github.com/martin10101/nyc-buildability.git`. **11 commits UNPUSHED.** `main`
   UNTOUCHED at `d8b3899f`. Repo is PUBLIC. **Accepted: 176** (M5-T004 submitted, not yet accepted).

2. **OWNER-FACING WORKING LIST: `docs/MVP_AGENDA.md`.** Written this session from the owner
   product conversation. Twelve sections: build order, pre-demo list, post-demo work, flags the
   program cannot yet surface, corpus ingestion, the AMI prerequisite chain, the source-of-truth
   ranking, UI risks, owner actions, the Geoclient key setup, and **two carry-forward defects (C1/C2)
   found by the M5-T004 gate wave**. Read it before planning product work.

3. **M5-T004 (Compare UI) - the full arc.** First gate wave at `84815a76`: **FAIL 4-1** on a silent
   projection (19 schema-required fields never rendered). Rework across 6 commits. Re-review at
   `9b417875`: **PASS 5-0** (G1/G3/G4/G5/DCV). Measured: leaf transport **191/515 -> 656/665**, 0
   authored legal/numeric values, constraint leaves **0/96 -> 96/96** on the conflict fixture, 45/45
   schema leaves rendering, tests ~13 -> 57+. Gates recorded PASS with the FAIL preserved in
   `history`. Evidence: `project-control/reports/M5-T004-rereview.md` + the five first-round reports.
   **Status: `awaiting_gate`, submitted with `M5-T004-evidence-map.json`.**
   **Acceptance is BLOCKED on the D-038 `task_verification` row** (producer != verifier, fail-closed).
   An independent directive-compliance verification was dispatched; if it is not recorded, re-dispatch
   it. Do NOT write that row as the orchestrator - the orchestrator authored the evidence map.

4. **NOT CI-VERIFIED.** Last CI run was `34557953219` on `0c810887`, **before any of the rework**.
   `node_modules` is absent everywhere (thin-client policy), so neither producer nor any reviewer
   executed the documented test commands. **NO GREEN IS CLAIMED.** G4's static prediction (both
   `web` and `web-e2e` PASS) is the only pre-merge signal, and it is unusually well-founded: G4
   transcribed `validateScenarioDocument` into Python and ran all four committed fixtures through it
   (4/4). Push and watch CI before trusting anything here.

5. **TWO ZR SOURCE SNAPSHOTS CAPTURED (commits `23ca629d`, `17e8eb78`).** Both byte-verified from raw
   portal HTML, both cross-checked against owner-supplied PDFs - every row, value, footnote and the
   2024-12-05 amendment date match.
   - `zr-23-22` (R6-R12) was **missing entirely**.
   - `zr-23-21` was **PARTIAL** - 4 R5-only rows under an "R1 Through R5" title; R1-R4 never captured.
     The recapture found a **defect**: ZR 23-21 footnote 1 (the 0.60 per-dwelling-unit cap) is
     attached to the FIRST TABLE ROW's value only (`0.75<sup>1</sup>`), not to R5. The existing
     `r5_residential_far.rule.json` carries it on R5, where the source does not impose it.
   - **Four districts are NOT flat lookups**: R6, R7-1, R7-2 and R8 each appear twice; the higher
     value applies only within 100 ft of a #wide street#, and footnote 1 says "or portions thereof",
     so a lot can split. A rule MUST NOT return the higher value without a wide-street determination.
     `#wide street#` is already captured in `zr-12-10` ("75 feet or more in width").

6. **M4-T009 contracted and claimed** (`e1cb45ad`) - R1-R12 flat-district FAR, worktree `wt-m4t009`,
   branch `task/M4-T009-r1r12-far`. Its 9 acceptance scenarios were written against the M5-T004
   lesson (see item 9): AS-1 forbids tautological tests, AS-2 requires coverage to be **computed**,
   AS-3 forbids the conditionals returning the higher value, AS-9 fixes the footnote defect.
   **`allowed_paths` carries DUAL-FORM entries deliberately** - `policy.py path_matches` (worker
   write approval) needs `**` globs or every write defers; `git ls-tree` (content identity) returns
   ZERO for `/**` and 7 for the plain directory. Both forms are required. Measured, not guessed.

7. **THE LOOP RAN AND DIED - orchestrator parameter error.** Run `persistent-local-30` launched
   clean (preflight PASS, limited-auto, PID 16700), then stopped at **exactly 1500.1s** on
   `--unit-timeout 1500`, which was copied from the owner-pinned `autostart-launch.ps1` sized for
   M5-T003 (one endpoint). M4-T009 is ~30 districts plus tests. Exit 11, `no_valid_checkpoint` /
   `missing_checkpoint` - the controller correctly refused to call an unfinished unit a success.
   **The work survived**: 355 lines across 4 new rule files (`r1_r2_r3`, `r2x_r4`, `r6_r12`,
   `r6_r7_r8_wide_street_conditional`), 3 test files updated, plus the R5 footnote fix - all
   uncommitted in `wt-m4t009`. Loop is back in `PAUSED_RECOVERY`. **Relaunch needs a much larger
   `--unit-timeout` (suggest 4500).** Launch script: `scratchpad/relaunch_m4t009.ps1`.
   **Owner normally starts the loop; the orchestrator monitors.** Hand the restart back.

8. **FABLE NOT APPLIED.** `model_selection.toml` still pins `claude-opus-4-8`; the file is unmodified
   since Sep 7, so run `persistent-local-30` used **Opus** (confirmed from the run's own preflight:
   `"expected_model":"claude-opus-4-8"`). The revert is pre-authorized and documented in the file
   itself (D-036-R001/R002). `set-claude-model` requires typing back a challenge token derived from
   the request digest - a deliberate human-at-the-keyboard gate. **Do NOT hand-edit the TOML**: a
   change arriving by any other path is refused and pauses per S4.5. On the next launch pass
   `--expected-worker-model claude-fable-5` so it refuses rather than silently falling back.

9. **ACCEPTANCE-CRITERIA FINDING (process, not code).** All 8 of M5-T004's acceptance scenarios
   PASSED at `84815a76` while four of five gates FAILED. The criteria under-specified the honesty
   bar. Both DCV and G3 said so independently. Write future packets against this.

10. **Reviewer self-corrections - the review worked in both directions.** G1 withdrew a HIGH (the
    DRAFT label does NOT vanish - there is an unconditional static prefix); G3 withdrew "no test was
    ever executed" (they run in CI); G5 corrected the orchestrator's own reasoning twice. The
    producer improved on orchestrator instructions four times and was right each time. Do not treat
    a reviewer finding or an orchestrator instruction as final without checking it.

11. **Standing restrictions (unchanged).** NEVER merge PR #241; R595/autostart/continuous-mode
    owner-only; supervisor changes need a cited `D-024-R###`; expansion-planning hold; Bootstrap
    Gate 0 (cwd = this worktree root, `/mcp` empty/allowlisted) before any write; launch the
    supervisor ONLY from `wt-controller-src`; no bare `git stash`; no new packages outside
    `docs/DEPENDENCY_SECURITY_POLICY.md`; Tier D (credentials/payment/production/legal) stops for the
    owner. **`main` stays untouched.** The D-024 campaign NEXT pointer is STALE and the five
    `D-032-*.json` campaign files are INVALID - **the ledger + git win**.

## EXACT NEXT ACTION (ordered; do NOT broaden)
1. Land the D-038 `task_verification` row for M5-T004 (independent verifier), then `accept` -> 177.
2. Push the branch and watch CI - 11 commits and the whole rework are unverified there.
3. Relaunch the loop on M4-T009 with `--unit-timeout 4500` (owner starts it). Fable first if wanted.
4. Then the pre-demo list in `docs/MVP_AGENDA.md` §B: overbuilt-lot check, confirm screen, Geoclient.

## COPY INTO THE NEW SESSION

Resume from durable evidence only. Bootstrap Gate 0: primary cwd must BE
`C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` and `/mcp` empty or allowlisted BEFORE any write. Verify
root/worktree/branch/HEAD/origin/upstream first. Read `CLAUDE.md`, `docs/SESSION_HANDOFF.md`, and
**`docs/MVP_AGENDA.md`** (the owner-facing working list - build order, carry-forward defects C1/C2,
Geoclient setup); then `python tools/project_control.py status` and reconcile - **the ledger and git
win over all prose.** 176 accepted. **M5-T004 is submitted and PASSED 5-0 on re-review but is NOT yet
accepted** - it needs a D-038 `task_verification` row from an INDEPENDENT verifier (never the
orchestrator, which authored the evidence map). **11 commits are UNPUSHED and the entire M5-T004
rework is CI-UNVERIFIED** - last CI ran before it. `main` untouched at `d8b3899f`; repo PUBLIC. The
loop is DOWN in `PAUSED_RECOVERY`: run `persistent-local-30` died at exactly `--unit-timeout 1500`,
a value sized for a one-endpoint task; M4-T009 needs ~4500. Its work SURVIVED uncommitted in
`wt-m4t009` (4 rule files + 3 test files). Fable was NOT applied - the loop ran Opus; the switch
needs the owner to type a challenge token and the TOML must never be hand-edited. **The owner starts
the loop; you monitor.** Do NOT: push or merge `main`, merge PR #241, activate continuous/autostart,
ask the owner for a secret in chat, commit any secret, deploy the web app before the Next.js RCE is
fixed, install any package outside `docs/DEPENDENCY_SECURITY_POLICY.md`, answer worker asks against a
live run, launch the supervisor from ctl24 cwd, or claim the code graph saves tokens.
Report READY TO RESUME or BLOCKED.

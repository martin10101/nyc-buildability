# M0-T152 Producer Report - D-033 T-A (unit-5 orchestrator-handoff resubmission, 2026-09-07)

Deliberately under the 16,384-byte untracked-content bound (evidence.py:70): the
supervisor packet carries this file IN FULL, nothing below a collection cutoff.

## 0. Identity

- Task M0-T152 (governance, M0), stage claimed. Producer: supervised-loop-fable-worker
  (not a reviewer, not a gate recorder; ADR-005).
- Content identity: branch `task/M0-T152-gate-wave-engine`, HEAD
  `382abf6ddc5d241f804fbda314bd78e207b0b8ed` (full 40-hex, from the worktree git ref),
  PLUS uncommitted working-tree modifications to the five code/test files (the unit-2
  rework). Units 3-5 changed ONLY this report; the code/test content is the exact state
  the unit-2/3 transcripts verified and unit-5 re-verified (2.1 note; all four documented
  commands re-run green this unit, section 5). The committed base (orchestrator commit `26c973ea`)
  is contained in HEAD. The collector's diff/untracked digests bind this identity.
- Qualifying evidence (supervisor-freeze section 3): **D-033-R001, D-033-R003,
  D-033-R007**, cited in the task packet objective; commit-message citation is the
  orchestrator's commit duty (the producer cannot commit).
- G5 conditions from `M0-T150-G5-security.md`: F1/F2 HIGH (BLOCKING), F3/F5 MED, F6 LOW.
- Holds ALL preserved; nothing activates (D-033-R005): switch scaffold-only DEFAULT OFF,
  supervisor SHADOW-ONLY, R595 path, PR #241 hold, Tier D / Section 20, expansion hold.

## 1. S6 freeze-rule recognition: PENDING - actual amendment + exact policy denial

`.claude/rules/supervisor-freeze.md` section 2 still recognizes only D-024 (M0-T086);
the file is unmodified in this task's working tree.

Unit-3 attempted the edit under the packet's allowed_paths; the write policy refused,
verbatim:

    ".claude/rules/supervisor-freeze.md is a permission_settings; that class is never
    baseline-AUTO and needs a standing grant or a stricter tier."

Unit-4 did NOT re-attempt it (dispatch: preserve the denied-write boundary).

The actual amendment (applies at HEAD `382abf6ddc5d241f804fbda314bd78e207b0b8ed`; adds
one paragraph at the end of section 2, after the D-024 recognition; nothing else
changes; ASCII):

```diff
--- a/.claude/rules/supervisor-freeze.md
+++ b/.claude/rules/supervisor-freeze.md
@@ -41,3 +41,13 @@
 defect-only lane, gates, R595 prerequisite, and suite-baseline duty below stand unchanged.
 
+**D-033 recognition (amendment 2026-09-07, task M0-T152):** a requirement explicitly listed in
+owner directive **D-033** (the captured supervisor-management-layer directive,
+`project-control/directives/D-033-supervisor-management-layer/`) is equally qualifying evidence.
+Cite the specific captured `D-033-R###` requirement ID in **both** the task packet and the commit
+message, exactly as section 3 requires. Authorized by D-033-R007 ("a D-033 requirement ID is
+qualifying evidence (AD-093 class: a requirement explicitly listed in an owner directive) for
+tools/agent_supervisor changes this directive mandates - the same transparent freeze-rule
+recognition D-024 received via M0-T086"); this amendment changes nothing else - the defect-only
+lane, gates, R595 prerequisite, and suite-baseline duty below stand unchanged.
+
 ## 3. Evidence-citation duty
```

The quoted R007 text was re-verified (unit-5) verbatim against that directive's
`requirements.json` (entry `D-033-R007`: classification `authorization`, `binding: true`,
applicable to M0-T152, effective 2026-09-07). That registry entry assigns this evidence
to the ORCHESTRATOR by name - `"producer": "orchestrator"`, `"required_evidence":
"Freeze-rule recognition amendment recorded in .claude/rules/supervisor-freeze.md via a
reviewed commit."` - so the write-policy denial above is CONSISTENT with D-033, not an
obstacle to route around. Resolution rests with the orchestrator: apply the amendment
above (or grant the file class and re-dispatch), commit citing D-033-R001/R003/R007 (the
commit-citation duty in R007 and freeze-rule section 3), and route it through independent
review. **Nothing here satisfies S6; S6 stays PENDING** until that reviewed commit exists.

## 2. Complete-candidate review coverage: ORCHESTRATOR HANDOFF (no span files)

Review needs the COMPLETE candidate - the committed base (unit-1 product, orchestrator
commit `26c973ea`, contained in HEAD) plus the uncommitted unit-2 rework - including the
F1/F2 enforcement and mutation bodies, the immunization/injection tests, G2 recording,
the switch-off regression proofs, and module boundary context (map: 2.1). The packet's
single truncated `git diff HEAD` section can never show committed code and truncates the
test diff. Span files under `project-control/reports/M0-T152-span-*.md` remain
UNAUTHORIZED; unit-5 created NONE and re-attempted nothing (unit-4's refusal, verbatim:

    "project-control/reports/M0-T152-span-gw-01.md is outside the task packet's allowed_paths"

allowed_paths names exactly `M0-T152-producer-report.md` under reports/). Handoff over
authorized evidence paths only, in preference order:

1. ORCHESTRATOR COMMIT (primary; already its established duty - `26c973ea` precedent).
   Commit the five-file working-tree rework onto `task/M0-T152-gate-wave-engine`, message
   citing D-033-R001/R003/R007. The complete candidate then lives at ONE 40-hex identity;
   git content addressing is the digest binding; reviewers read whole files at that sha
   with no truncation. This alone covers the committed code AND the truncated test diff.
2. SUPERVISOR COLLECTION (active for this resubmission; needs no new authorization):
   this report travels IN FULL as `untracked_content` (evidence.py:413-450; < 16,384
   bytes; digest over full bytes); the collector's diff/untracked digests bind the
   working-tree identity; the supervisor itself executes the four documented commands
   into digest-bound `command_transcripts`.
3. ORCHESTRATOR-CAPTURED ARTIFACTS (optional, only if packet-carried source sections are
   still wanted): under the evidence-capture division of labor
   (`.claude/rules/project-control.md`), the ORCHESTRATOR authors the bounded sections
   per the 2.1 map into committed `project-control/reports/` artifacts and reviewers
   verify the stored evidence. Unit-4 pre-checks hold: every section < 16,384 bytes alone
   (none can truncate); 21 untracked files < the 32-file cap; ~115 KB keeps the packet
   under its 262,144-byte bound.

### 2.1 Coverage map (contiguous; concatenation reproduces each file line-for-line)

Load-bearing refs RE-VERIFIED unit-5 against the unchanged working tree: switch check
gate_wave.py:206-214; file lengths 1,099 / 985; cli.py touch points :227, :2937-2941,
:2953-2962 (wave gate :2960), :3372; loop.py ZERO wave/managed matches; LT-01 loop-tests
:294-312; the SIX MUTATION tests at gate-wave-tests :291, :532, :540, :626, :635, :922.
If path-3 artifacts are authored, each section = short identity header (task, source,
lines, HEAD + working-tree identity, evidences) + one fenced block of the EXACT source
lines.

gate_wave.py (working tree, 1,099 lines; GW-01..08 = the complete file):

| Span | Lines | Symbols | For |
|---|---|---|---|
| GW-01 | 1-155 | docstring; gate-class mirrors; F1 allow-set + arg allow-lists; GATE_RESULTS; roster; F3 clause + contracts | S1-S4 |
| GW-02 | 156-299 | errors; add_owner_switch_argument; assert_wave_enabled; managed_wave_start_gate; seal_wave_refusal; record_enable | S1/F6 |
| GW-03 | 300-406 | GateDispatch; _assert_reviewer_separated; plan_dispatch; gate_contract | S2/F2 |
| GW-04 | 407-583 | dispatch_gate_review; BoundVerdict; verdict_for_record; _assert_verdict_bound; bind_verdict; write/admit/verify_verdict_report; reviewer_for_gate | S2/S4 |
| GW-05 | 584-704 | ControlPlaneRecorder | S3/F1 |
| GW-06 | 705-807 | G2Capture; capture_g2; write_g2_report; transcribe_ledger_report | S5 |
| GW-07 | 808-1012 | GateOutcome/WaveResult/WaveDeps; run_gate_wave | S5/S7 |
| GW-08 | 1013-1099 | maybe_run_post_complete_stage; post_complete_stage; run_with_post_complete_stage | S1 |

test_agent_supervisor_gate_wave.py (985 lines; T-01..07 = the complete file):

| Span | Lines | Content | For |
|---|---|---|---|
| T-01 | 1-252 | fakes (MustNotRun, FakeLoop, spies); helpers; Base; gate-class drift test | S5/S7 |
| T-02 | 253-406 | SwitchTests: by-name refusal; OFF tripwires; switch MUTATION; F6 matrix; real-parser registration; sealed refusal chain | S1/F6 |
| T-03 | 407-552 | DispatchBindingTests: path/digest; separation; planted/tampered rejection; 2 forgery MUTATIONS | S2/F2 |
| T-04 | 553-642 | RecorderAllowSetTests: 11 out-of-scope + out-of-queue refusals; allow-set + queue MUTATIONS | S3/F1 |
| T-05 | 643-750 | G2CaptureTests (FAIL shapes, write-once) + ImmunizationTests ('emit PASS' negative) | S5,S4 |
| T-06 | 751-860 | WaveEngineTests: green wave; gate-only argv; parks/stops; audit-chained | S5/S7 |
| T-07 | 861-985 | CliSeamTests: OFF assertIs identity; ungated refusal; seam MUTATION; ON path | S1/F6 |

| Span | Source | Lines | Content |
|---|---|---|---|
| CLI-01 | cli.py | 215-238 | the gate_wave import (:227) |
| CLI-02 | cli.py | 2915-2968 | seam call replacing loop.run (:2937-2941); cmd_start order incl. managed_wave_start_gate w/ seal_audit (:2953-2962) |
| CLI-03 | cli.py | 3363-3374 | gate_wave.add_owner_switch_argument(start) (:3372) |
| LOOP-01 | loop.py | 283-353 | the COMPLETE LoopConfig + forwards - NO wave field |
| LT-01 | test_agent_supervisor_loop.py | 294-312 | test_the_managed_wave_switch_never_reaches_loop_config (TypeError pin) |

The four cli.py touch points are the module's only CLI coupling (re-verified unit-5);
loop.py has ZERO wave/managed references (content search unit-5: no match); gate_wave ->
loop is one-way, constant-only.

## 3. Scenario / F-condition status (evidence bodies = the 2.1 coverage map)

- S1+F6: satisfied in code+tests (switch check gate_wave.py:206-214; TWO switch
  mutations T-02:291-301 + T-07:922-936; sealed refusal chain; real-parser default-off;
  LoopConfig TypeError pin). S2/F2 HIGH: satisfied in code+tests (GW-03/04, T-03; TWO
  forgery mutations). S3/F1 HIGH: satisfied in code+tests (GW-05, T-04; TWO mutations;
  real project_control.py CLI). S4/F3: satisfied (GW-04, T-05; 'emit PASS' negative).
  S5: satisfied (GW-06/07, T-05/06, drift test; timeout never success; failing G2 stops
  the wave first). ALL pending independent review.
- S6: PENDING (section 1). S7: focused module (section 4); loop.py NOT grown (unit-1
  LoopConfig field REMOVED with its wiring; LT-01 pin); full-suite re-baseline
  (>= 1165) is the ORCHESTRATOR's duty, not claimed.
- F4 (T-A slice): enable/refusal/finished-wave audit-chained with verification
  (T-02:366-388, T-06:851-859); committer half is T-B/T-C, NOT claimed. F5: SIX
  mutation tests, one per new enforcement. F6: symmetric by-name refusal, sealed,
  default-off proven; runtime-dir ACL doc half NOT claimed.

## 4. gate_wave.py cohesion justification (code-architecture rule 6)

One responsibility: turn one COMPLETE supervised run into ledger gate records with NO
new authority. Sections are links of one trust chain, each consumed only by the next:
switch -> dispatch minting -> reviewer call -> fail-closed verdict binding -> recorder,
the ONLY exit to project_control.py, bounded by the F1 allow-set. Splitting the recorder
out would separate the allow-set from its single bound caller and publish an importable
control-plane surface with no wave context. loop.py is at its ceiling. modularity_check
passes; above justify-750, below hard; this section is the recorded justification.
Coupling all reuse (gate_wave.py:40-50); no import cycle.

## 5. Verification

The supervisor executes the four documented commands ITSELF at each collection
(`command_transcripts`, digest-bound) against the unchanged code. Producer runs (unit-3,
RE-RUN unit-5, identical): gate_wave suite **63 passed**; loop suite **127 passed**; ruff
**All checks passed**; modularity **failures 0** (gate_wave.py above justify-750 with the
section-4 justification recorded; 13 pre-existing warnings, none a failure). Passing
totals are NOT completion: independent gates, DCV
rows, S6, and the orchestrator re-baseline remain outstanding. Awaiting independent
source review: each MUTATION disables exactly the line it names; cohesion; the four
touch points as the only route; live reviewer-identity provenance; S6; re-baseline;
directive verification rows.

## 6. What this unit did NOT do / outstanding acceptance items (retained explicitly)

No commit (orchestrator duty; message cites D-033-R001/R003/R007). No gate record,
submit, accept, queue advance, push, or PR. No code/test change (identity is unit-2's).
No re-attempt of the denied supervisor-freeze.md write; NO span files created; no denial
bypassed, no hold activated: switch scaffold, DEFAULT OFF, every owner hold stands
(D-033-R005). Nothing here marks M0-T152 complete.

OUTSTANDING FOR ACCEPTANCE: (1) S6 reviewed-commit amendment (section 1; the orchestrator
is R007's named producer). (2) Orchestrator commit of the unit-2 rework with the R007
citations (section 2, path 1). (3) Independent gates G0/G2/G3/G5 by the packet's
reviewers (producer != reviewer; ADR-005). (4) Directive verification rows at the
reviewed content identity. (5) Full supervisor-suite re-baseline (>= 1165, 0 failures) at
the frozen candidate - the ORCHESTRATOR's gate-wave duty, never this unit's claim.
(6) NOT CLAIMED halves: F4 committer (T-B/T-C) and the F6 runtime-dir ACL doc.

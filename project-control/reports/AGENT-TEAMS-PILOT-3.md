# AGENT-TEAMS-PILOT-3 — D-004 Step 4: two-producer pilot (evidence, redacted)

Owner GO 2026-07-30 (D-004 amendment 7, source-008, rows R297–R306). Frozen base for both
producers: `84c1bf29243bb862d344c909099c9bd9a3f6a766` (post PR #125). Producer model: explicit
Opus 5 (owner ceiling, D-004-R298); spawns UNNAMED so the roster identity is resolvable by the
read-only guard; gate-class reviewers stay explicit Fable 5. Orchestrator performs all git
integration (D-004-R303/R072).

## Section-C matrix (recorded before dispatch, D-004-R068/R301)

| Item | M2-T018 | M4-T008 |
|---|---|---|
| Task | Wire M2-T017 allowlist serializer into property-profile builder | DF-6: exception predicates with missing optional inputs → indeterminate/PRR |
| Producer (roster type, unnamed spawn) | backend-engineer | rules-engineer |
| Branch | `task/M2-T018-serializer-wiring` | `task/M4-T008-df6-exceptions` |
| Worktree | `.claude/worktrees/M2-T018-serializer-wiring` | `.claude/worktrees/M4-T008-df6-exceptions` |
| Base SHA | `84c1bf29243bb862d344c909099c9bd9a3f6a766` | `84c1bf29243bb862d344c909099c9bd9a3f6a766` |
| Allowed paths | per packet `M2-T018.json` (contracts serializer pair, profile modules, contracts/profile/api tests, source_fact schema pair, generated TS, own report) | per packet `M4-T008.json` (rules/**, tests/rules/**, own report) |
| Forbidden paths | rules/**, api/**, connectors/**, scripts, .claude/, tools/, docs/ | profile/**, api/**, contracts/**, connectors/**, packages/contracts/**, _contract_schemas/**, non-rules tests, .claude/, tools/, docs/ |
| Expected shared files | **none** (disjointness verified by import graph + ledger fences) | **none** |
| Merge order | 1st | 2nd (orchestrator rebases surviving branch after merge 1 if needed) |
| Attestation | required before any write (D-004-R302) | required before any write (D-004-R302) |

## Pre-dispatch state

- G0 PASS recorded for both tasks at the frozen base (reports `M2-T018-G0-readiness.md`,
  `M4-T008-G0-readiness.md`); both tasks CLI-claimed (backend-engineer / rules-engineer).
- Pre-dispatch dirt sweep: primary checkout dirt = expected machine-local state + this report +
  the two G0 readiness reports + CLI claim updates to the two task files and state.json (all
  control-plane lifecycle artifacts to be committed in the wrap-up control PR). Both pilot
  worktrees clean at the frozen base. Sentinel `PILOT_SENTINEL.tmp` absent.

## Attestation event 1 — harness worktree isolation vs pre-created worktrees (recorded openly)

The first M4-T008 producer spawn STOPPED at attestation with ZERO writes (D-004-R302 honored —
this is the harness working as designed): the agent runtime auto-provisions every writing
producer its own isolated worktree (`.claude/worktrees/agent-<id>` on branch
`worktree-agent-<id>`) at the then-current main HEAD, and hard-refuses commands that reach any
other tree — including the orchestrator-pre-created task worktree. 3/4 expected values
mismatched; the base SHA matched (`84c1bf2`, correct frozen base). The producer returned
`blocked` plus a read-only defect verification (DF-6 fail-open confirmed at evaluator.py line
234; contract-safe notes-only PRR design sketched). Its untouched worktree was auto-cleaned on
completion.

**Adaptation (deviation disclosure, judged at the Step-4 STOP):** D-004-R067's letter
("orchestrator pre-creates worktrees for the producers") is mechanically unsatisfiable in this
runtime — the harness always isolates writing producers into its own worktrees; this is the
SAME mechanism M0-T028's accepted evidence ratified (D-004-R061: producer isolated in a harness
worktree at the identical base + orchestrator exact-diff port review before integration).
Adapted attestation, single-pass: the producer verifies hard invariants itself before any write
— HEAD == frozen base EXACTLY; pwd == toplevel == its own fresh `agent-*` worktree (not the
primary checkout, not a task worktree); branch matches its worktree id; clean tree — records
all four values as the FIRST content of its in-scope producer report, and stops on any
violation. The orchestrator then ratifies the binding post-return, verifies containment against
the packet `allowed_paths` by exact diff, and ports the diff onto the pre-created task branch
(`task/M2-T018-serializer-wiring` / `task/M4-T008-df6-exceptions`), which remain the
integration branches. Recorded in both task progress logs; the owner judges this deviation in
the Step-4 evidence presentation before any Step-5 decision.

## Producer evidence (appended after returns)

Both producers ran UNNAMED at explicit Opus 5 (owner ceiling, D-004-R298) in harness-isolated
worktrees at the frozen base `84c1bf2`; neither ran git/gh/control-CLI; both returned evidence +
requested status `awaiting_gate`. Full producer reports are merged repository artifacts:
`M2-T018-producer-report.md` (PR #126), `M4-T008-producer-report.md` (PR #127).

**M2-T018 (backend-engineer).** First spawn proceeded in its harness worktree with the deviation
DISCLOSED (guard honored — the harness refused Edit/Write and git against the assigned worktree
and the producer deliberately did not circumvent via raw Bash; assigned-worktree values verified
via shared git metadata; the ten in-scope files proven byte-identical across both trees at the
base). Delivered the fail-closed provenance boundary; key finding: all four connector lineage
keys were ALREADY documented by M2-T017, so no contract artifact changed. Self-checks 243
targeted / 1048 full suite / ruff clean / drift checks rc=0.

**M4-T008 (rules-engineer).** FIRST spawn STOPPED at attestation with ZERO writes (3/4 mismatch —
the R302 harness working; see attestation event 1) and returned a read-only defect verification.
RE-DISPATCH under the adapted single-pass attestation: 4/4 PASS recorded as the first report
content. Delivered the three-valued `_apply_exceptions` (unsupplied-input exceptions →
indeterminate/PRR with deterministic name-only notes; contracts byte-unchanged). Two disclosures
correctly left for review: the skip-only scope (vs blanket) with measured evidence, and a stale
sentence in `r5_height.rule.json` (legal artifact — not edited; routed to a qualified-reviewer
follow-up). Self-checks 328 rules / 1066 full suite / ruff clean.

## Orchestrator integration and independent review

- Exact-diff ports (agent worktree → task branch, orchestrator-committed, tree-identical 0-line
  diffs): M2-T018 → `756f60164e5cf27c56082166047ffc119a5f3d02`; M4-T008 →
  `2122cd27a49511df079e0bf30baf5093d384a012`. Orchestrator sanity reruns green (243 / 328).
- Independent reviews (unnamed spawns, explicit Fable 5, at the frozen branch SHAs):
  M2-T018 G3 **PASS** + G5 **PASS**; M4-T008 G3 **PASS** (producer deviation ACCEPTED — DF-6
  closed as contracted; blanket semantics would override a documented legal-authoring decision)
  + G5 **PASS**. Verbatim reports: `M2-T018-G3-report.md`, `M2-T018-G5-report.md`,
  `M4-T008-G3-report.md`, `M4-T008-G5-report.md`.
- Sequential merges per the section-C order: PR #126 (M2-T018) then PR #127 (M4-T008), each
  28/28 checks green; no rebase needed (disjoint file sets confirmed at merge). Merged main:
  `31226481a62170477c0d6973a3d51bd215751505`.
- Lifecycle: both tasks CLI-submitted `awaiting_gate` with evidence maps covering the five
  applicable D-004 conduct rows each ({R298, R301, R302, R303, R306}, derived at the merged
  identities `f2f28cf5…` / `c6a8ec04…`); G2/G3/G5 recorded PASS; independent per-task directive
  verification and acceptance follow in this session's wrap-up records.
- Follow-up items recorded (non-blocking, from reviews): stale `r5_height.rule.json` limitations
  sentence (qualified-legal-reviewer wording fix); predicate-schema tightening (require `input`
  on leaves, additionalProperties); `coverage.most_severe` typing widening; serializers.py
  docstring "NOT WIRED" header amendment; non-mapping-record boundary test; D-002-R038
  verification-evidence supersession recording (the retired tripwire test is cited there).

## Step-4 outcome (orchestrator summary)

The two-producer pilot ran end-to-end under the merged confinement stack: dispatch guard and
readonly guard fired throughout (reviewers denied on write attempts in prior phases; producers
passed through as unnamed roster identities); worktree isolation held (one attestation STOP
proving the mismatch path, zero unexpected artifacts in any sweep); producers returned honest
evidence including measured pushback on orchestrator design guidance; all four independent
reviews PASS with zero blocking defects; both changes merged green. Cost split held: producers on
Opus 5, orchestrator + all reviewers on Fable 5. STOP after Step 4 per D-004-R305 — Step 5
requires a separate owner GO.

## Session-model disclosure (recorded for owner judgment)

After all Step-4 production, review, verification, acceptance, and checkpoint work was complete
and recorded, the OWNER changed the session model from Fable 5 to Opus 5 via `/model` (the
lead-model clause of D-004-R298 records "the main has to stay fable 5"). Every gate-class
reviewer spawn and the entire lead-side judgment of this pilot ran on Fable 5 as required and is
recorded at frozen SHAs; the only work performed after the change is this disclosure plus the
mechanical commit/merge of the already-produced lifecycle records and the owner-facing Step-4
presentation. No gate, verdict, acceptance decision, or evidence was produced or altered on the
new model. Disclosed rather than passed over silently; the owner's own action governs, and any
standing preference for the lead model is the owner's to restate.

# M0-T142 directive-compliance verification (independent DCV, 2026-09-02/03)

Saved VERBATIM by the orchestrator from the verifier's agent-return channel (transport
entity-decoding only; harness banner and neutralized angle brackets restored;
report-preservation rule 2026-07-16). Verifier: foreground read-only
`directive-compliance-verifier`; producer = orchestrator (identities differ). TWO parts:
the full verification at submitted head `f2e79cc5` (14/14 PASS), then the re-verification
at the resubmitted head `57dce1a5` after the in-scope review-wave delta. Basis of the
M0-T142 entry in `verification.json`.

## Part 1 — verification at f2e79cc5 (condensed to the load-bearing content; full table verdicts preserved)

**OVERALL VERDICT: PASS.** All 14 resolver-confirmed applicable requirements (R685–R696,
R698, R699) independently SATISFIED at the frozen head on reproduced primary evidence.
Preconditions: HEAD/tree clean; applicability re-derived independently (exactly 14 IDs
list M0-T142; R684/R697 correctly M0-T140-only); intake completeness (source-045's three
verbatim owner messages map atomically to R684–R699); validator exit 0; control-plane
harness re-run (120+23-group+12 tests OK); full supervisor suite 3591/2/0 reproduced;
focused 200; modularity 0 failures. Prohibited-action evidence: task awaiting_gate (not
self-accepted); no upstream/push/merge; runtime mrl dir only the three preserved run dirs;
audit.jsonl 36 records; model_selection.toml still claude-opus-4-8. Per-ID: R685 one
bounded task; R686 aggregate policy + helper deleted; R687 exact-tier handling; R688 guard
cites the measured behavior verbatim; R689 bare-deny flow-through + changed criterion;
R690 normal-settlement consumption with the binding added AND tested (real project-key);
R691 settle-valid/refuse-divergent with version pin retained; R692 both build sites +
default deny; R693 durable reader fields exist (MINOR: reader encoded in the
post-acceptance owner script per the AS-ER-1/R697 split — by directive design); R694
forbidden paths empty over the task's own span; R695 fixture families (MINOR: family 6 =
documentation + durable-field existence); R696 one-suite discipline reproduced; R698
return plan; R699 exact-id discipline (no claude-fable-5-1, no bare fable id, no live
launch). Cross-checks: R684/R697 correctly NOT claimed by this task. Findings: two MINOR
(above), zero BLOCKING.

## Part 2 — re-verification at 57dce1a5 (verbatim)

**RE-VERIFY: PASS.** The one in-scope delta (`f2e79cc5..57dce1a5`) is strictly fail-closed
hardening plus two added tests plus SHA-carrier rebind. No requirement semantics changed;
four IDs are strengthened/re-confirmed; none regressed. M0-T142 remains `awaiting_gate`
(not self-accepted).

Delta re-verification (reproduced): delta scope = 1 code file (`mrl_runtime_identity.py`
+5/-1), 2 test files, 4 allowed-path carriers, control-plane records; forbidden/preserved
paths EMPTY. Code delta: `read_transcript_turns` catches `(OSError, UnicodeDecodeError)` —
a torn multibyte transcript raises typed `ContractError("transcript_missing")` instead of
escaping `_settle` uncaught (UnicodeDecodeError is a ValueError, not OSError — previously
unhandled); strictly stronger fail-closed posture. Both new tests reproduced PASSED
individually. SHA carriers: binding `commit_sha=f8f0f0c8…`/`commit_tree_sha=23af20d5…`,
runbook §4, ps_test `$pinnedSha`, freeze.md — all agree and match
`git rev-parse f8f0f0c8^{tree}` and `f8f0f0c8:tools/agent_supervisor` (`ffbde3b6…`).
Resubmission: reviewed_sha `00c3541a`, applicable = exactly the 14 IDs; content identity
stable to HEAD. No provider contact: audit.jsonl still 36 records; only the three
preserved run dirs; model_selection.toml still `claude-opus-4-8`. Harness at v4: four
focused files **202 passed**; full supervisor suite **3593 passed, 2 skipped, 0 failed**;
validator exit 0.

14-row confirmation: R685 PASS (unchanged) · R686 PASS (unchanged) · R687 PASS (unchanged;
AS-SI-1 prose divergence disclosed and dispositioned — implementation is the MORE faithful
R687 reading) · R688 PASS (unchanged) · R689 PASS (unchanged) · **R690 PASS (IMPROVED**:
torn-transcript typed refusal) · **R691 PASS (IMPROVED**: no-checkpoint via typed refusal,
never an uncaught exception) · R692 PASS (unchanged) · R693 PASS (unchanged) · R694 PASS
(unchanged) · **R695 PASS (IMPROVED**: family-7 now a DIRECT executable fixture) · **R696
PASS (RE-CONFIRMED**: 3593/2/0 reproduced at the new candidate) · R698 PASS (unchanged) ·
R699 PASS (unchanged).

Findings: MINOR-1 (AS-SI-1 prose vs implementation — not a directive violation; packet
prose immutable post-claim; disclosed in producer report s8). No BLOCKING findings.

Recommendation: re-stamp G-directive-compliance = PASS for M0-T142 at reviewed head
`57dce1a5`; frozen candidate `f8f0f0c8` with all three SHA carriers agreeing; no forbidden
path touched; no provider contact; task not self-accepted.

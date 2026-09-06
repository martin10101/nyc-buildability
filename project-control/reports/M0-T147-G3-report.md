# M0-T147 G3 reports (verbatim reviewer returns, both rounds)

Saved VERBATIM by the orchestrator from the code-review agent-return channel (2026-09-06;
transport entity-decoding only). ROUND 1 reviewed 3360cceb → **PASS** (one MEDIUM advisory +
LOW items + two required process actions); ROUND 2 (delta) reviewed dee758f4 → **PASS**
(prior PASS carries forward; G5 corrections verified; dispositions accepted).

Key round-1 substance (full text preserved in the session record):

- **Verdict PASS.** Fix targets the correct module: `ROTATE_SESSION`/`rotation_reason` exist
  only in the CodexReviewer decision schema; the MRL one-shot verdict enum {APPROVE, REVISE,
  HALT} structurally cannot emit it — so the failing path is exactly the one fixed.
- Reproduced: reviewer suite 94 passed; affected-suite battery 425 passed; ruff clean;
  modularity 0 failures; diff scoped to exactly the three allowed tool files.
- (a) Completeness PASS: packet now carries every fact the contract asks the reviewer to
  judge; no residual live-verify duty. (b) Safety PASS: untrusted-checkpoint discipline,
  HALT_UNSAFE reservation, honest truncation weighting, stdin determinism all preserved;
  legitimate ROTATE_SESSION (oversized session) still fully available via the schema and
  tier mapping. (c) Boundedness PASS: diff_content rides `_execute`→`bound_text`
  (16,384-byte section cap, explicit marker, packet-size STOP_FOR_OWNER unchanged).
  (d) Guard PASS: enumerated tail exact; test calls the guard fail-closed. (e) Tests PASS:
  anchors load-bearing; mutation tooth real (two-way RED). (f) No other module changed.
- **MEDIUM advisory (dispositioned):** the sibling `mrl_one_shot_review.py` carries its own
  REVIEW_INSTRUCTIONS still promising read-only repository inspection — same false-execution
  premise, outside this packet's scope, structurally unable to produce the documented
  failure. Disposition: the authorized live-closure rerun uses the legacy CodexReviewer loop
  (all failing runs were that path), so the fix is sufficient for the rerun; MRL contract
  alignment recorded as a tracked backlog follow-up.
- LOW items: diff_content covers uncommitted changes only (inherits the existing
  changed_files/diff_summary convention; validate empirically in the closure rerun);
  pre-existing guard permissiveness on wider diff forms lives in policy.py (out of scope);
  a direct oversized-collector truncation test would strengthen S1 (machinery-covered).
- Required process actions: full freeze-baseline at the reviewed SHA (recorded: **3635
  passed / 2 skipped / 0 failed at dee758f4**, and 3635/2/0 at 3360cceb) + the MRL
  disposition above.

Round-2 delta substance:

- `git diff 3360cceb dee758f4 -- tools/` = exactly the two described changes, three files.
- Change 1 (G5 M-1 packet-wide injection immunization): strengthens the safety posture;
  closes the exact prompt-injection surface raw worker patch text opens; both new anchors
  load-bearing and green.
- Change 2 (G5 LOW-2 driver-independent collection): `assert_read_only_git` admits the new
  4-token tail; the dangerous enabling inverses `--ext-diff`/`--textconv` remain refused;
  "a genuine correctness improvement, not just neutral"; mutation tooth intact.
- Suite 94 passed at dee758f4. **PASS at dee758f4.**

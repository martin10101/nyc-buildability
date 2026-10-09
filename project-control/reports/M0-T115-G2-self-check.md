# M0-T115 — G2 producer self-check

Task: M0-T115 (unit O; rows R272/R273/R274). Producer: fable-orchestrator-session.
Supervisor-freeze qualifying evidence: **D-024-R270/R272**.

1. **Scope:** deliverable commit `91664bb` touches EXACTLY the packet's allowed_paths
   (broker.py, recovery_probes.py, the two test packs, the repair record); `cli.py`
   forbidden and untouched; no dependency, schema, policy, or hook change. Control
   commit `be5e09a` carries only G0/claim records.
2. **Method (reliability standard):** §3.1 red recorded (4 failed / 6 guard-passed
   against unchanged code, exact command+output in the repair record) → fix → green
   (117/117 both packs) → §3.4 revert-proof recorded (stash → 4 FAIL → pop → 4 PASS).
   §2 smallest fitting change: both fixes are the owning functions' own existing
   patterns (revoke_all's resolve_ask; cli.py's reconciliation predicate mirrored
   exactly); no new abstraction; pre-existing unused imports NOT drive-by-cleaned.
3. **R273:** zero runtime-journal writes; pre-fix journals handled read-time only;
   proven by the read-only probe test asserting the raw row stays unanswered.
4. **Gate not weakened:** five guard tests keep the blocking behavior for pending
   records, missing records, non-broker asks, and refused (digest-mismatch) answers.
5. **Affected packs:** 353/353; `modularity_check --check` EXIT=0 (broker.py 785 SLOC —
   +14 cohesive lines inside its existing responsibility; recorded per rule 6).
6. **Consequence acknowledged:** supervisor material identity has MOVED — the R247
   certification is invalidated by design; M0-T116 recertifies at the ONE frozen final
   identity after M0-T114 also lands (R275); no resume before R276 conditions pass.

Self-check verdict: **PASS** — ready for independent G3/G4/G5 + DCV at the frozen tip.

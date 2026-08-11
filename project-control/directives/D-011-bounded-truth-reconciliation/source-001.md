# D-011 — Bounded truth reconciliation (owner correction)

- Channel: owner_typed_instruction
- Captured: 2026-08-11
- Frozen baseline: origin/main = 7cc1fed7ea66df8abe952e48bfea2451469f93ac
- Model in session: claude-opus-4-8 (owner switched model to `claude-opus-4-8` immediately before this directive)

## Verbatim owner text

OWNER CORRECTION — bounded truth reconciliation only. Do not start M0-T056, do not activate R595, and do not request or add the broad accept allowlist yet.

I independently inspected the live repository. Correct the following without creating a broad supervisor redesign or beginning another multi-day control-plane project:

1. Do not describe PR #217 or PR #218 as fully green. Their functional/required checks passed, but the workflow conclusion is red because web-dependency-security still detects the known nanoid advisory.

2. Refresh SESSION_HANDOFF.md to current repository truth:
- main = 7cc1fed7ea66df8abe952e48bfea2451469f93ac
- PR #216 is merged
- M2-T016 product code is merged but the task is not accepted
- PRs #217 and #218 remain open
- M0-T053 producer work and G3/G5 reviews have returned
Do not claim Opus 5 authorship unless durable evidence supports it.

3. Correct the R595 blocker classification:
- P1, P2, and P3 are required engineering corrections before M0-T056 live actuation.
- P6 is a deterministic reviewer-timeout/retry/pause requirement.
- P4 and P5 are recommendations, not mandatory blockers.
- P7 is a wording/interpretation correction.
- P8 is a Windows-only deployment constraint.
Do not describe all eight as equivalent blockers.

4. Verify and state explicitly that project_control.py accept already fails closed when a required gate has no PASS record. Reviewer silence therefore cannot become acceptance. P6 should add bounded timeout detection, one controlled retry/re-dispatch, and then PAUSE/STOP with visible evidence; do not duplicate the existing acceptance gate.

5. Repair the in-flight M2-T016 and M0-T055 allowed_paths so their acceptance identities bind the actual implementation files instead of the empty-set hash. Invalidate and rerun only the final identity-bound DCV/gate evidence that this repair legitimately invalidates. Do not attempt to remediate every historical empty-identity packet in this update.

6. Implement the smallest M0-T057 fail-closed guard so future non-path-free tasks cannot freeze an empty file identity accidentally. Keep this bounded.

7. For PR #218:
- remove or split the .claude/agent-memory/** files from the M0-T053 task diff unless a lawful, explicitly gate-proven carve-out exists;
- correct "doctor parity" to the truthful statement: doctor and the launch gate share a containment source, but their verdicts are not equivalent;
- update the PR description and lifecycle state to reflect the returned G3/G5 reports;
- preserve P1–P3 as required before M0-T056 actuation.

8. Complete M0-T047's now-eligible exact nanoid 3.3.17 remediation through the approved lockfile/CI workflow. No waiver, no audit suppression, and no unrelated dependency upgrades.

9. Preserve the valid exact-head M2-T016 review. Clearly label the missing second verbatim reviewer return as outstanding; do not represent its condensation as equivalent verbatim evidence.

After these bounded corrections, return one concise truth table containing:
- task/PR;
- exact current SHA;
- merged/open state;
- functional CI result;
- security-check result;
- identity binds real files: yes/no;
- gates complete: yes/no;
- safe to accept: yes/no;
- remaining required blocker.

Do not begin M0-T056 or another supervisor improvement task. The immediate goal is to make the existing evidence truthful, safely finish acceptance, and return to product delivery.

## Trailing context (prior-session handoff text the owner pasted for reconciliation — NOT a new directive)

> check handoff.md this was thee last text from last season Accepted. The permission works. Let me verify and land it.
> [prior session's M0-T055 acceptance narrative: pushed to control/session14-m0t055-accept; count 74 -> 75; M0-T055 accepted; M2-T016 and M0-T053 not yet accepted; R595 eight-item pin list remains; main at 7cc1fed; PRs #217 and #218 open and "green" — the "green" claim is exactly what item 1 corrects.]

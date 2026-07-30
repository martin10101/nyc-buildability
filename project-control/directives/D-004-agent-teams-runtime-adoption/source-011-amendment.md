# D-004 — source-011 (owner amendment 10, verbatim)

Captured verbatim per `.claude/skills/directive-compliance` §1 (amendments are new append-only
files; committed sources are never edited). Channel: owner_message. Amends `source-001.md`.
Frozen baseline unchanged: `421265709f81a40e20f3d890609907ed932967dd`.
Head at capture time: local `task/M0-T033-unblock-roster-semantics` =
`170478efc34e52f3479d9bb0ac914ad0c364b245`; `origin/main` =
`abb89b821d3cb7beacc916784c92c9d5570122e0` (post PR #131).

Requirement IDs added by this amendment start at `D-004-R410`; no existing source file or
requirement row is edited. The owner states that **no new owner decision is required** — this
amendment adds binding EVIDENCE and REVIEW requirements to the already-authorized OPTION B
sequence (amendment 9, `source-010-amendment.md`), and does not re-open any decision. It tightens
D-004-R374: M0-T027 stays untouched until M0-T033 is merged **and accepted**, not merely until the
implementation ends.

---

Continue under the corrected frozen-base dispatch. No new owner decision is required.

Preserve the original attestation stop and corrected resume honestly in the producer evidence. Do not waive or silently resolve either carried item:

- Prove that every test relied upon for M0-T033 acceptance is actually registered and executed. If the S10 body is never invoked, it cannot count as passing evidence and must be corrected within scope or returned as a blocker.
- Preserve the required_gates/task_type validation asymmetry for an explicit independent-review ruling against R352 and R368.

After the producer returns, perform the contracted exact-diff containment review and tree-identical port. Then proceed through the authorized M0-T033 gates only. Keep M0-T027 untouched until M0-T033 is merged and accepted. No Step 5, M0-T032, or unrelated work.

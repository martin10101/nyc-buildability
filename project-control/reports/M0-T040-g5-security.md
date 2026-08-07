# M0-T040 G5 security review — verdict preserved verbatim

**Reviewer:** security-reviewer (independent, read-only). **Recorded by:** orchestrator (producer backend-engineer ≠ reviewer).
**Reviewed:** deliverable `b841b4f` vs base `b1a9186`. **Result: PASS. Harness security warning: JUSTIFIED-AND-RESOLVED.**

---

# G5 SECURITY GATE REPORT — M0-T040 (Authority-Policy Simplification, ADR-006)

- **Change class:** Tier B — authority/permission-model modification (security-sensitive)
- **VERDICT: PASS.** The diff grants no authority beyond D-010's verbatim text, preserves every Tier D / Section 20 hard stop, encodes the anti-injection "allowlist ≠ authorization" principle, and touches zero mechanical enforcement surfaces. The three abuse scenarios classify exactly as required. No secrets/PII.

## Scope of change (reproduced)

14 files; declarative policy (ADR/docs) + stdlib test suite + ledger artifacts only. NOT touched: `.claude/settings*.json`, `.claude/hooks/**` (incl. agent_dispatch_guard.py), `.github/**`, `tools/agent_supervisor/**`, `tools/project_control.py`, `tools/directive_registry.py`, `.npmrc`, `package*.json`. The change alters documented policy, not any executable permission gate.

## Per-check findings (all PASS)

1. **Authority-widening bounds:** Tier A/B/C/D/§5.5 set/sequence-equal to D-010 §5.1–5.5 (test-enforced, 22/22 green). CLAUDE.md narrows the owner merge-queue FOR TIER A ONLY and adds nothing. No language authorizes production deploy, secret handling, force push/history rewrite, branch-protection changes, destructive migration, legal publication, or payments. No hold/R595 lift.
2. **Hard-stop preservation:** all 14 Tier D items verbatim and in order; CLAUDE.md human-only list preserved verbatim; "the Tier D hard stops" ADDED to the override clause (strengthened).
3. **Self-modification / injection surface:** new text states the OPPOSITE of injection — ADR incident lesson: "the mere fact that a merge command is allowlisted or auto-classified never satisfies those conditions"; rules: ADR-006 "does not relax ADR-005 execution authority… reviewers stay read-only"; no text tells future sessions to bypass gates, ignore classifier denials, or skip owner stops.
4. **Abuse scenarios:** (a) workflows PR + green CI + no specialist review → Tier B, NOT permitted ✓; (b) direct main push → Tier D#2 hard-denied ✓; (c) ordinary green docs PR, no owner response → PERMITTED_TIER_A ✓ — confirmed in ADR text AND the test suite.
5. **Governance trail:** supersession honestly scoped (Tier A only; R718–R724 lineage cited; R721 stands outside Tier A); source-003 verbatim, sha256 `6c55718f9a746c56df597f9a8f50261bb87f38e9d61498cac2a05ca264e48342` == manifest; validator exit 0.
6. **R595/activation:** "does not activate any autonomous-merge behavior… R595 remains a mandatory blocking prerequisite before any activation (D-010-R104); until then the orchestrator executes Tier A actions manually" — echoed in CLAUDE.md + rules; test-enforced; supervisor untouched.
7. **Secrets/PII:** full-diff pattern scan → policy-concept references only; no secret values, credentials, or client PII.

## Disposition of the harness security warning

**JUSTIFIED-AND-RESOLVED.** The flag was correct: editing the session's own instruction surfaces to narrow the owner merge-queue is a genuine permission-model self-modification that always warrants a human decision; the two classifier denials were the correct fail-safe. It is resolved because the widening is exactly and only what D-010 §5 / AD-006 authorizes verbatim; every hard stop is preserved verbatim; the allowlist≠authorization lesson is preserved and test-encoded; and the owner supplied an explicit typed authorization (D-010 source-003, digest-verified) and executed the commit personally, mandating this independent G3/G5/DCV sequence before merge. The denial was resolved by obtaining owner authorization — NOT by treating any mechanical surface as authorization. Textbook application of the PRs #143–#146 lesson the ADR itself codifies.

## Findings by severity

Critical/High/Medium/Low: none. Informational: (1) Tier D item 11 ASCII-apostrophe normalization (disclosed, semantically identical, drift tests still bind); (2) R111/R112 pending status in requirements.json — expected; DCV fills state at accept; this G5 satisfies the security-verification leg of R112.

## Pre-merge note

R112 requires independent G3 + G5 + directive-compliance verification before any merge. This report clears G5; merge must await the recorded G3 pass and the DCV verification row at the current identity.

**Verdict: PASS.**

---
name: m0-t013-g3-carryforward
description: M0-T013 expansion-agent ADR-005 conformance G3 PASS @61a768a; residuals for B-007 closure and first expansion-agent dispatch
metadata:
  type: project
---

M0-T013 (expansion-agent ADR-005 conformance) G3 PASS at 61a768a on task/M0-T013-agent-conformance, 2026-07-17. All S1-S6 verified; S1/S5 independently re-executed (frontmatter parse ALL 5 PASS exit 0; guard 15/15 exit 0; secret scan exit 0; contracts validator 6 schemas 0 failures exit 0). ADR-005 sections byte-identical to cloud-architect (producers) and security-reviewer/code-reviewer (visual-quality-reviewer); temporal qualifier "during final review" removed. Rule items 11/13 only lines changed in 3d-ui-expansion.md.

**Why:** closes the conformance precondition of B-007; the five expansion agents become dispatchable only after acceptance + B-007 closure + G5 re-check.

**How to apply (residuals to recheck later):**
- Acceptance requires G5 re-check per B-007/dispatch-hold rule; hold retirement must occur in the same checkpoint that closes B-007. If I see these agents dispatched without that checkpoint, it is a defect.
- Producer's S1 evidence cited an uncommitted temp script (%TEMP%\check_frontmatter_m0t013.py); assertions were fully described and I reproduced them independently — pattern acceptable, but prefer committed check scripts in future evidence.
- visual-quality-reviewer keeps Bash+Write with prose-enforced read-only discipline (same as roster reviewers) — verify at its first real dispatch that it wrote only under its own agent-memory dir.
- product-design-director deliberately has no Bash (least privilege, producer disclosure 3) — do not "fix" this as an inconsistency later.
- Producer session had FULL write/exec lockdown (Bash+Edit+Write all denied); work delivered via agent-return channel and orchestrator transplant per report-preservation rule — valid precedent, related [[m0-t010-g3-carryforward]].

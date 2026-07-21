---
paths:
  - "packages/rules/**"
  - "services/api/app/rules/**"
  - "services/api/app/legal/**"
  - "**/*.rule.json"
---
# Legal / rules rule — loads only for rule-DSL, evaluator, and legal-corpus work

(Forward-looking: these paths appear at M4 — "Rule engineering and professional-review system".)

- **Rule lifecycle:** `discovered → extracted_draft → needs_review → approved → published →
  (suspended | superseded | rejected)`. Only a `published` rule may produce a **Verified** result.
- **No rule is `published`** without exact source linkage + version, deterministic tests
  (positive/negative/boundary/exception), independent review, and **qualified-human approval (G6)**.
  Agent consensus can never substitute for G6. AI may draft a rule; AI may never silently publish one.
- Keep AI-drafted rules strictly separate from published rules. Rules are versioned JSON DSL; keep
  legal text out of UI components. Every result carries exactly one coverage status
  (`verified | conditional | professional_review_required | data_conflict | unsupported |
  not_applicable`) plus a data-completeness status.
- Full lifecycle + required rule fields: `PRD.md` §10–§12; DSL: `PRD.md` §11; publication gate:
  `docs/GATES_AND_CHECKPOINTS.md` (G6); legal-rule acceptance pack:
  `docs/ACCEPTANCE_SCENARIO_STANDARD.md`.

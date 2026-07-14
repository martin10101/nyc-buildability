# Risk Register

Maintained by the orchestrator. Review at every replanning event.

| ID | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R-01 | Cloud credentials (Supabase/Render/Geoclient) not provided promptly, stalling M0/M1 critical path | Medium | High | Blockers B-001..B-004 with exact minimal actions; all non-blocked work continues (research, contracts, migrations-as-code, CI, Blueprint authoring) | Owner + orchestrator | Open |
| R-02 | Local disk exhaustion (true headroom ~1.9 GB above the 4 GB floor) | Medium | High | Storage budget doc; G0 disk estimates; all dependency-heavy work routed to GitHub Actions/Codespaces/Render; no local installs by default | Orchestrator | Open |
| R-03 | AI-extracted legal rules published without qualified human approval (legal exposure) | Low | Critical | G6 gate hard-blocks publication; rule lifecycle states; `verified` label only from published+approved rules; audit trail | Orchestrator + human reviewer | Structural control in place |
| R-04 | Government API schema drift breaks connectors silently | High | Medium | Source registry with versioning, contract tests, schema-drift detection jobs, connector health dashboard (M1) | data-contract-verifier | Open |
| R-05 | Geoclient v1 deactivation ("deprecated, no date published") while platform depends on it | Medium | Medium | Build on v2 from the start (M0-T002 recommendation); GeoSearch v2 fallback | official-source-researcher | Mitigated by design |
| R-06 | Cross-tenant data leakage via missing/wrong RLS | Low | Critical | RLS on every tenant-facing table via migrations; G5 security gate with cross-tenant denial tests; service-role key never client-side | security-reviewer | Structural control planned |
| R-07 | Prompt injection from ingested government pages steering extraction | Medium | High | Source content treated as untrusted; strict structured-output schemas; restricted tools in extraction workers; injection test cases in AI pipeline pack | ai-pipeline-engineer | Structural control planned |
| R-08 | Ledger/repo divergence (progress claims without evidence) | Medium | Medium | project_control.py authority rules + sync_state fix; progress-auditor recurring audits; evidence-first gates | progress-auditor | Mitigated (first audit passed) |
| R-09 | Project subagent types not natively registered in current session (registry snapshot predates agent copy) | Certain (this session) | Low | Agents proven operational via parameterized workers bound to definition files + ledger identities; native registration on next session start; no restart needed to continue | Orchestrator | Mitigated |
| R-10 | Supabase MCP points at a project that may not be intended for this product | Medium | High | No writes until owner confirms project identity (HUMAN_ACTIONS #1); dedicated dev project option prepared | Owner | Open |
| R-11 | Scenario engine produces plausible-but-illegal envelopes (hard-rule violations) | Medium | Critical | Deterministic evaluator only; published-rule hard-constraint rejection; golden-property tests; G6 | rules-engineer + qa-engineer | Structural control planned |
| R-12 | Windows PowerShell 5.1 BOM/encoding corrupting JSON artifacts | Medium | Low | utf-8-sig tolerance in control plane; standing instruction to agents to use the Write tool, not Set-Content | Orchestrator | Mitigated (defect found and fixed) |
| R-13 | Free-tier service limits (Render sleep, Supabase pausing) degrade dev/staging reliability | Medium | Medium | Documented in architecture ADRs; owner decision on paid tiers deferred until services are actually deployed | cloud-architect | Open |

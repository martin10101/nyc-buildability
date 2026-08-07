# M0-T036 Supervisor Bridge — Activation Checklist

**Status: SHADOW-ONLY. Not activated. Acceptance of M0-T036 does NOT activate anything.**

M0-T036 is accepted as a **shadow-only** pilot (owner decision, keep-shadow-only). This checklist
lists the prerequisites that MUST be satisfied before the supervisor moves beyond shadow mode. It is
owner-gated at every step; nothing here is authorized by M0-T036's acceptance.

## BLOCKING PREREQUISITES before ANY activation

### ⛔ R595 supervised rehearsal — MANDATORY BLOCKING (owner directive 2026-08-06, D-007-R619)
The **live context-threshold rotation-seam actuation** (R593 third live leg / QA-gap-4) was recorded
as an **accepted residual** (Option A) because it is **structurally infeasible as a synthetic probe
under R594** (the seam needs a real forward; R594 keeps shadow-only in force / nothing forwards). The
requirement is **NOT waived — deferred in time.** A **supervised rehearsal (R595)** that actually
actuates the rotation seam live and preserves its audit evidence is a **mandatory blocking prerequisite
BEFORE any of:**
- [ ] **supervised-auto activation**
- [ ] **limited-auto activation**
- [ ] **automatic product-task execution**
- [ ] **any claim that live session rotation has been proven**

Until R595 is satisfied and independently reviewed, none of the above may proceed, and R593 must
**never** be represented as fully live-proven (D-007-R621).

### Other standing activation prerequisites (from the Phase-5 decision packet + gate findings)
- [ ] Live-CLI account-quota exhaustion **classifier wired** (`QUOTA_EXHAUSTION_SIGNAL_VERIFIED=False`
      today → the model-chain switch fail-closes to PAUSE; disclosed by `doctor`). Needs its own
      security look (G3-A1 / G5-L-1 / G4-A1).
- [ ] Activation-blocking G3 B-rows (B-1..B-4) fixed and re-gated.
- [ ] Single-account Windows OS-ACL enforcement of the immutable controller config (G5-L-2), if the
      manifest-detection posture is deemed insufficient at activation.
- [ ] Live resource **sampling** wired into the loop for the R207 limit set (config/circuit-breaker
      knobs exist + are fail-closed today; live sampling is the documented Phase-2/3 boundary).
- [ ] Owner authorization at each activation tier (supervised → limited-auto → …).

## Accepted residual (visible per D-007-R620)
- **R593 / QA-gap-4** — live rotation-seam actuation: **ACCEPTED RESIDUAL, deferred to R595.** 2 of 3
  V1.2 live legs proven (allow round-trip, model-mismatch detection); the rotation leg is unit- and
  real-process-proven but **not live-actuated**. Owner directive D-007-R618 (Option A), 2026-08-06.


---

## M0-T042 G5 additions (2026-08-07) — pre-R595 hardening items

Registered at M0-T042 acceptance (G5 security review, PASS with pinned residuals; see
`project-control/reports/M0-T042-g5-security.md`). All three are MUST-RESOLVE before any
activation, alongside the existing checklist items:

1. **L-1 (must-fix-before-activation):** `parse_usage_telemetry` (codex_reviewer.py) must catch
   non-`JSONDecodeError` `ValueError` from `json.loads` on a >4300-digit integer in the untrusted
   `--json` stream (reproduced), so a pathological usage line yields USAGE_UNKNOWN / a sealed
   refusal record instead of crashing the review.
2. **I-1:** the AD-083 prohibited-content guard is structural (key-name/flag) detection only —
   add a semantic/size check or re-confirm `evidence.build_packet` remains the sole packet source
   at activation (concurs with M0-T042 G3 INFO-1).
3. **I-3:** bound the child-process stdout capture (process.py `communicate()`, pre-existing)
   before the ephemeral reviewer runs against a live untrusted Codex process.


---

## M0-T044 G3 additions (2026-08-07) - pre-activation items for the GitHub flow

Registered at M0-T044 gating (G3 code review PASS with pinned MINOR findings; see
`project-control/reports/M0-T044-g3-code-review.md`). Both are MUST-RESOLVE before the
automatic GitHub flow is wired into any live path (R595-gated activation):

1. **MINOR-1 (fail-open Tier B detection):** `github_flow.py` change-class detection derives only
   3 of the 11 Section 5.2 classes (workflow, lockfile/dependency-manifest, supervisor-code path);
   the 8 semantic classes (auth/session, additive DB migration, contract/schema addition,
   official-source connector, legal-corpus ingestion, draft-rule, scenario-calc, survey/PDF parser)
   and `deploy_definition` are not derivable from `policy.file_class` and would route Tier A
   (auto-permit) - fail-open. Before live wiring: make undetected-but-sensitive classes fail
   TOWARD review, or wire a semantic classifier. (Scoped AS-3 - workflow/dependency - is proven;
   the full 5.2 table is present as data.)
2. **MINOR-2 (defense-in-depth):** `authorize_push` inherits push_policy's empty-`authorized_branch`
   fall-through (non-main branch allowed when the grant's authorized_branch is ""). main/master/
   force remain hard-denied regardless. Before live wiring: assert a non-empty `authorized_branch`
   in `authorize_push`.


---

## M0-T044 G5 additions (2026-08-07) - pre-activation items (SEC-1/SEC-2/SEC-3/INFO-1)

Registered at M0-T044 gating (G5 security review PASS shadow-only; see
`project-control/reports/M0-T044-g5-security.md`). All MUST-RESOLVE before any live-path/R595
activation of the GitHub flow or the effect journal:

1. **SEC-1 (MEDIUM):** guard the live-path `ExternalEffectJournal.extra_specs` override channel -
   reject keys colliding with MODELED_EFFECTS, reject destructive extra specs, add a test that
   every live journal constructs with empty extra_specs, and extend the invariant-9 lock to
   instance extra_specs (today it inspects only the module-level registry).
2. **SEC-2 (MEDIUM, BROADENS the M0-T044 G3 MINOR-1 entry above):** the Tier B fail-open covers
   more than the 8 semantic classes + deploy_definition - detectable SECURITY_RELEVANT_CLASSES
   (permission_settings, hook, secret_bearing, launcher_script, submodule_config,
   attributes_filter) also route Tier A. Remediation is a CATCH-ALL: any file_class in
   SECURITY_RELEVANT_CLASSES not explicitly routed (and specifically permission/hook
   configuration per Section 5.4 item 3) must fail TOWARD security/control-plane review or
   Tier-D owner-stop, with tests. Treat the MINOR-1 entry as remediation spec ONLY together
   with this broadening.
3. **SEC-3 (LOW):** redaction discipline - require redacted descriptors in
   `MergeRequest.secret_scan_findings`; route caller-side logging of MergeEvaluation.conditions
   through redaction.py.
4. **INFO-1:** the live caller must audit every `FlowResult`, including refusals (this module
   journals only performed effects).

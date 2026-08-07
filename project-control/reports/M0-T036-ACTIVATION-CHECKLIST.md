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

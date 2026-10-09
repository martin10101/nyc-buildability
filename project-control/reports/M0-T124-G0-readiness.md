# M0-T124 — G0 readiness (orchestrator, administrative)

Recorded 2026-08-30. VERDICT: **PASS — dependency satisfied, ready to claim.**

1. **Dependency:** M0-T123 ACCEPTED (20-row DCV ALL PASS at `a71bd65`; gates + 3 delta
   attestations; CI 20/20). The certification was invalidated by the T123 supervisor
   change by design; this task restores it (fifth window) and then STOPS per R347.
2. **Authority:** D-024 Amendment 19 rows R330/R346/R347. In-regime `D-024:ALL`
   (resolver: 5 applicable rows — R328, R330, R345, R346, R347).
3. **Scope:** allowed_paths = the recertification report + the activation package only;
   forbidden `tools/**` and the live runtime dir. No code changes; the preserved journal
   is read-only (doctor/verify read it; record-manifest writes outside the repo).
4. **The ONE final identity:** supervisor material `16e1b3b`, tree `a72a53b8…`, golden
   blob `c54fd0d2` (unchanged since T119), launch-seam blob `1a77b904` (64 tests), CLI
   `d6f6c29a…` undrifted. Full-suite evidence already dual-sourced at this identity
   (2,889/2/0 twice).
5. **The R347 stop is the packet's terminal state:** after certification + the recorded
   preflight commitment, the live-start package is PRESENTED (report §4) and nothing
   executes. The R316 one-attempt consumption stands; R345 prohibitions bind.

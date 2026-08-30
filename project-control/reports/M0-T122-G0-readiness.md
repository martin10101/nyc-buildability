# M0-T122 — G0 readiness (orchestrator, administrative)

Recorded 2026-08-30 at HEAD `96362c0` (the M0-T121 acceptance commit; local == origin).
VERDICT: **PASS — ready to claim; dependency satisfied.**

1. **Dependency:** M0-T121 ACCEPTED this session (19-row DCV ALL PASS, gates G0/G2/G3/G4/G5,
   CI 20/20 at `6edf820`) — the sole `depends_on` entry is satisfied. The certification was
   INVALIDATED by the T121 supervisor change by design (R247/R314); this task restores it.
2. **Authority:** D-024 Amendment 16 rows R302/R314 (the authorized recertification window)
   + Amendment 17 rows R315..R322 protocol recording. In-regime `D-024:ALL` (resolver:
   ok=true, 10 applicable rows R302, R314–R322).
3. **Scope sanity:** allowed_paths = the recertification report + the activation package
   (anchor refresh) only; forbidden: `tools/**` and the live runtime dir — this task
   changes NO code and NEVER touches the preserved journal.
4. **The ONE final identity to certify:** supervisor material = work commits
   `668c824`+`6432d2d` (last supervisor-touching commit `6432d2d`); the byte-identity of
   `tools/agent_supervisor/**` + the test pack at HEAD equals the gate-wave/DCV-reviewed
   identity (verified by the DCV: `git diff 6432d2d..HEAD` over those paths is empty).
   Certification inputs already queued: full-suite re-run at this identity (in flight),
   golden pack, controller manifest re-record (outside the repo), verify-controller,
   doctor, drift tooth at the admitted CLI 2.1.251 (digest `d6f6c29a…`, NO repin).
5. **Sequencing:** the R315 hold is recorded on this packet — no R276 rerun and no cycle-2
   command handover before this task is ACCEPTED. AS-4 requires the handover text and the
   R316–R322 one-attempt/live-journey protocol recorded verbatim in the recert report.

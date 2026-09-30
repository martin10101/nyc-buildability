---
name: m0t120-routing-tooth-gate
description: QA method for verifying the D-024 Amendment-14 shell-routing drift tooth (M0-T120) and its supervisor-recert siblings
metadata:
  type: project
---

M0-T120 (D-024 Amdt-14, R292/R294/R295) added a pre-dispatch shell-routing drift tooth to the agent-supervisor. G4 QA verified PASS at material identity 7d8195b (2026-08-29).

**Why:** the tooth blocks a changed/un-re-measured Claude CLI from silently entering a certified (limited-auto) run; the gate lives as a one-line AND-fold in `start_gate.live_revalidation` (`cli_capability_manifest AND answers["shell_routing"].passes`), scoped to `mode == MODE_LIMITED_AUTO`.

**How to apply (verification levers that actually catch a fake pass):**
- Confirm the committed fixture `fixtures/shell_routing_*.json` `cli_identity` equals the REAL installed binary digest: `executable_identity(r'C:\Users\MLFLL\.local\bin\claude.exe', name='claude').digest` (read-only hash, no provider call). At review time both = `d6f6c29a8ac6b3cf1b76e53cca2faadf784bf5114230c815d55327dbae889ed8`. This proves production is a genuine no-op, not a tautology.
- Over-seeding check: `probe_shell_routing_evidence` matches on EXACT digest equality (version only as fallback when no digest); `record_routing_evidence` dedups per-identity; golden harness seeds ONLY its own fake exe digest in setUp. No wildcard/all-identity seed anywhere. The tooth is NOT live-to-live: recorded journal/fixture digest vs file-hashed pinned identity.
- Removal-sensitivity: `golden_run.clear_routing_evidence` + `TwoUnitGoldenRunTests::test_the_routing_tooth_bites_a_certified_start_without_evidence` → limited-auto start refuses (dispatched False, 0 provider calls, UNSAFE_OR_DRIFTED, cli_capability_manifest failed).
- No-bypass: dispatchable limited-auto → `live_revalidation` (fold applies); non-dispatchable → `unprobed_revalidation` sets all STEP_PROBES False → refuse. Every limited-auto start re-probes fresh, so a prior supervised run cannot carry stale routing past a later limited-auto start.

**Gotchas found:**
- Report count-drift: producer-report file-list says routing_probe.py "27 tests" and routing-evidence §3/§4 show "2775 collected / +49" — both STALE. Authoritative final = §6b + producer self-check = 2782 collected / 2780 passed / 2 skipped / +56. Actual per-module: routing_probe 35, recovery_probes 88, command_authority 45, golden_run 42, bounded_mode 91. +56 = 35(new)+2+13+5+1.
- Mode-scoping fold hardcodes `== MODE_LIMITED_AUTO` not `in OWNER_GATED_MODES` (today equivalent — limited-auto is the sole owner-gated mode); a future certified mode would silently escape the gate. Forward-looking maintenance note.
- F1 (`| sh` pipe-to-interpreter) and F2 (`powershell -Command "Remove-Item -Recurse"`) classify ASK not HARD_DENY — recorded-not-fixed per R293 (classifier frozen), captured as `test_finding_f1/f2_*` asserting current ASK behavior. F-LIVE-1: 2.1.251 reports permissionMode=default despite `--permission-mode manual`, but mutating tools still brokered+DENIED (Edit denied, no write). Out of R293 scope.
- Golden blob moves with these edits (R296); final identity joins the single M0-T119 recertification.

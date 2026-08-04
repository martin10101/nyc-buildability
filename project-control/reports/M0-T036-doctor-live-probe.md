# M0-T036 — doctor --live control-response probe (owner-authorized, D-007-R588)

- Run: 2026-08-04, orchestrator, on the controller checkout `C:\SupervisorController` (at f68f578).
- Authorization: owner message 2026-08-04 (D-007 amendment 9, R588) — exactly ONE bounded probe;
  shadow config untouched; nothing forwarded to any real task; evidence preserved verbatim;
  report and stop. This closes the control-response live-verification residual and gates the V1.2
  unit (R739/R582).
- Command: `python -m tools.agent_supervisor doctor --live --claude-executable
  C:\Users\MLFLL\.local\bin\claude.exe --config config.toml --model-selection model_selection.toml`
  (config/model-selection read-only; not modified). Overall doctor result: **PASS**.

## Result: control_response_live_probe VERIFIED (deny leg)

**PASS — VERIFIED (live run, executable sha256_head:9d22d0d348ba14a2):** the installed CLI accepted
the exact control_response bytes this build emits, denied the tool, and echoed our deny message back
in `permission_denials`. The wrapper shape is confirmed against the live CLI. This closes the
Phase-2 residual (`control_response_shape` had been UNVERIFIED-live).

### Recorded probe evidence (verbatim from the controller runtime journal)

Runtime dir: `%LOCALAPPDATA%\NYCBuildabilitySupervisor\9aca7075…` (keyed to the controller checkout
path; outside every repo).

```json
{
 "name": "control_response_round_trip",
 "status": "VERIFIED",
 "ran_live": true,
 "executable_identity": "sha256_head:9d22d0d348ba14a2",
 "recorded_at_utc": "2026-08-04T17:01:27.547Z",
 "detail": "the installed CLI accepted the exact control_response bytes this build emits, denied the tool, and echoed our deny message back in permission_denials. The wrapper shape is confirmed against the live CLI.",
 "evidence": {
  "argv_flags": ["-p","--input-format","stream-json","--output-format","stream-json","--verbose","--max-turns","1","--permission-mode","manual","--permission-prompt-tool","stdio"],
  "control_request_seen": true,
  "response_sent": {"type":"control_response","response":{"subtype":"success","request_id":"2d13bed1-bdd4-4e34-b9ad-7d4557fe41ef","response":{"behavior":"deny","message":"preflight: deterministic broker denied (control-response probe)"}}},
  "deny_message_echoed": true,
  "permission_denials": 1,
  "target_file_created": false,
  "cli_protocol_error": false,
  "events": 7,
  "returncode": 1,
  "probed_at_utc": "2026-08-04T17:01:27.528Z"
 }
}
```

Key facts: `control_request_seen=true` (the CLI issued the `can_use_tool` control_request), the
supervisor answered with a `deny` control_response, `deny_message_echoed=true`, `permission_denials=1`,
and **`target_file_created=false`** — the denied Write tool did NOT execute. Deny round-trip proven
end-to-end against the live binary.

## Honest scope note — ALLOW leg NOT exercised

The built-in `doctor --live` probe (`control_response_round_trip` in `preflight.py`) is **deny-only
by construction**: it instructs the worker to Write a file, then sends a `deny` control_response and
verifies the file was not created. It does not exercise an **allow** round-trip. The owner's request
named an "allow-and-deny round-trip"; this probe delivers the **deny** leg only.

The **allow** leg (a real in-scope tool call permitted through the live CLI, tool executes) is exactly
QA gap 1 from the Phase 5 decision packet. It is not something the current probe can perform without
new code, and building an allow-capable probe is V1.2 broker-wiring work (G3 V-1: the approval broker
is not yet wired into the assembled loop). It is therefore surfaced here, not fabricated: **the deny
leg is live-verified; the allow leg remains open for the V1.2 unit.**

## Boundaries honored

Shadow config untouched (read-only load); nothing forwarded to any real task (throwaway workdir,
single denied Write); exactly one probe; full evidence preserved verbatim above. Per R588 the
orchestrator now STOPS and reports; the supervised single-forward rehearsal remains NOT authorized
(R590) and returns to the owner.

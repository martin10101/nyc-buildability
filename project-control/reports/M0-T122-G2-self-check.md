# M0-T122 — G2 self-check (orchestrator)

Recorded 2026-08-30 at control head `acf6505`. VERDICT: **PASS.**

Because the orchestrator is the producer of record for this governance packet, the G2
self-check enumerates exactly which claims are executed-command outputs from this session
(every one is; nothing carried as prose) and defers ALL judgment to the independent
G3/G4/G5 wave + DCV — producer ≠ reviewer discipline holds at every gate that matters.

| # | Claim in the recert report | Source (this session) |
|---|---|---|
| 1 | Whole suite 2,814 passed / 2 skipped / 0 failed at the final identity | background pytest over every `tools/test_agent_supervisor*.py`, completed exit 0 (425.8 s) |
| 2 | Pre-delta cross-check 2,811 (= 2,780+31) | earlier same-session background run, exit 0 |
| 3 | Golden blob `c54fd0d2` byte-identical to T119; restart pack blob `d3e23087`; tree `d3db9f3c`; material `668c824` | `git rev-parse HEAD:<path>` / `git log -1 -- tools/agent_supervisor/` outputs |
| 4 | CLI digest `d6f6c29a…` exact, `sha256_head+size`, size 217,360,032 | `executable_identity()` (the supervisor's own function) executed live |
| 5 | Drift tooth green | explicit `pytest -k version_matches_catalog` → 1 passed |
| 6 | Manifest 120 files digest `7f9991cb…`, config bound, round-trip verified | `record-manifest` output verbatim |
| 7 | verify-controller PASS; doctor overall PASS (audit 33 verified, journal HALTED/13 transitions, OS-ACL PROTECTED) | both commands executed, outputs quoted |
| 8 | CI 20/20 at `6edf820` | DCV-confirmed check-runs API poll; the certification tip `acf6505` re-runs the same 20 checks |
| 9 | Handover command + R315/R316–R322 protocol recorded verbatim (AS-4) | recert report §4 (release gated on acceptance) |
| 10 | Preserved journal untouched | every command against it read-only; doctor confirms unchanged state (HALTED, transitions 13, audit head 33 — the 31→33 growth is the refused-start audit events from seq 35, pre-window) |

Scope check: deliverables are exactly the two allowed_paths files; no code changed; the
task packet's forbidden paths untouched. Resolver: 10 applicable rows, ok=true.

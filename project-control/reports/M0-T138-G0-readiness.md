# M0-T138 G0 readiness (Bootstrap Gate 0 — D-024-R621)

Recorded by the orchestrator at task creation (2026-09-02). Administrative gate: verifies the
owner-stated bootstrap values and contract completeness before the producer claim. Every value
was re-measured live; none differs from the owner's Gate-0 statement.

| Check | Owner-stated | Measured | Verdict |
|---|---|---|---|
| Root | `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24` | `git rev-parse --show-toplevel` = same | PASS |
| Branch | `candidate/D-024-mrl-option-b` | `git branch --show-current` = same | PASS |
| Starting HEAD | `e60192ed` | `git rev-parse HEAD` = `e60192edc2b451b2d39fc92fc2efb315dd06cfcd` | PASS |
| Frozen production candidate | `1489879e1f6787a9d53ed74db4524b24039e03a2` | `git cat-file -t` = `commit`; tree `0babc469a07fc9109e5f7ce18ea73bf932952801`; `tools/agent_supervisor` subtree `79af11a2c7fa33c8f5c1bf85c17e310736bf30a3` | PASS |
| Clean working tree | clean | `git status --porcelain` empty at bootstrap | PASS |
| M0-T136 | accepted | `project-control/tasks/M0-T136.json` status `accepted` (accepted_at 2026-09-02T04:30:27Z) | PASS |
| /mcp | empty | no MCP servers configured in the session | PASS |

Root-cause evidence measured before contracting (consolidated trace, D-024-R618):

- `docs/CONTROLLER_UPDATE_RUNBOOK.md` §4 (lines 62–78) resolves the copy source as
  `git -C $repo rev-parse origin/main` — a mutable ref.
- Local `origin/main` = `d8b3899f61efa6620e18a26541ced96020f5bef9`;
  `git cat-file -e origin/main:tools/agent_supervisor/mrl_launch_draft.py` fails (rc 128) —
  origin/main lacks Tranche B and `mrl_launch_draft.py`.
- `record-manifest` (`tools/agent_supervisor/cli.py::cmd_record_manifest` →
  `manifest.generate_manifest(PACKAGE_ROOT, …)`) hashes whatever is installed at the destination;
  no input anywhere binds a source commit or tree, so a self-consistent but wrong installation
  would certify (`manifest.py::manifest_is_stale` documents self-consistency ≠ authenticity).
- The command-document tooth (`tools/supervisor_command_doc_check.py`, DEFAULT_DOCS =
  `docs/CONTROLLER_UPDATE_RUNBOOK.md`) validates only supervisor-invoking commands, and its
  invocation markers include `agent_supervisor/mrl_launch_draft.py` — so the repaired §4 must keep
  module paths out of fenced blocks (checked-in script indirection), or the tooth mis-validates.

Contract completeness: packet carries objective, inputs, outputs, allowed/forbidden paths,
6 executable acceptance scenarios (AS-SB-1…6), gates G0/G2/G3/G4, reviewer roster
(code-reviewer, qa-engineer, directive-compliance-verifier ≠ producer), directive_refs
`D-024:ALL` binding Amendment 41 rows R607–R621.

**G0 verdict: PASS — ready for producer claim.**

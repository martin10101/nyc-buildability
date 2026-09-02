# M0-T142 — frozen corrected controller candidate v3 (D-024 Amendment 45)

Supersedes the M0-T141 candidate `2245de74` (and M0-T136's `1489879e`) as the controller
install source. The installer's printed identity must equal this record.

| Identity | Value |
|---|---|
| Frozen corrected candidate commit | `65e43491129893fcfa49bbe7e7d4463b83336c0b` |
| Commit tree | `672f00d63c9050369939bc1f404c70a124e9853b` |
| `tools/agent_supervisor` subtree tree | `35fa19763c13f903bfc20c23b30ae1dd05abcf0f` |
| Supersedes (install source only) | `2245de74…` (subtree `edf026b3`), `1489879e…` (subtree `79af11a2`) |
| Branch | `candidate/D-024-mrl-option-b` (local only; nothing pushed, R520/R521) |

## Delta from the superseded candidate (the ONLY subtree changes)

- `mrl_runtime_identity.py` — NEW: correlation-bound runtime identity at settlement
  (cwd→project-key transcript binding, sessionId/cwd correlation, main-chain
  primary-model evidence + tool-use census, `[1m]` context tier of the exact pin,
  aggregate-usage policy; typed fail-closed refusals).
- `mrl_one_shot.py` — settlement wiring only: the new verification replaces the
  exactly-one-`modelUsage`-key check; unit record gains `runtime_identity` +
  `main_tool_uses`; `model_mismatch`/`mismatch_detail` derive from the verified outcome;
  `session_id_missing` check moved before identity; `transcript_base` test seam.
- `mrl_subagent_contract.py` — `build_restricted_profile` refuses an inventory tool that
  is neither allow-ruled nor deny-ruled (R688/R692).
- `mrl_exec_chain.py` — `observed_model_from_result` deleted (contract disproven, R686).
- `mrl_launch_manifest.py` — draft default subagents now deny `Edit/Write/Bash/Agent`
  explicitly (every inventory tool pinned).
- `mrl_launch_draft.py` — the same explicitness check at draft time (typed refusal
  naming `--allow-tool`/`--deny-tool`); help text updated.

The Draft-7 provider-schema hotfix, canonical `schemas/`, `mrl_worker_result.py`,
`mrl_transport.py`, containment, and updater-disablement surfaces are byte-identical to
the superseded candidate (R694 preserved; forbidden paths).

## Verification at this identity (R696: focused while editing, ONE affected-suite run)

- Focused suites (runtime-identity + one-shot + review + subagent-contract + exec-chain
  + launch trio): **402+ tests green** during editing.
- Mutation proof: N1 tier-suffix loosened, N2 divergent-turn tolerated, N3 correlation
  dropped, N4 aggregate-pin not required, N5 settlement identity skipped (fabricated
  pass-through), N6 profile guard removed — **all DETECTED**; modules restored
  byte-identical.
- ONE affected-suite verification: full supervisor set `pytest tools/test_agent_supervisor*.py`
  = **3591 passed, 2 skipped, 0 failed** (raw exit 0).
- `ruff check` on all changed files: clean. `modularity_check --check`: 0 failures.
  `validate_directive_compliance.py --check`: exit 0.

## Source binding rebind (this reviewed commit)

`tools/controller_update/source_binding.json` pins the three SHAs above;
`required_modules` += `mrl_runtime_identity.py` + `mrl_subagent_contract.py`; runbook §4
and `ps_tests/test_runbook_parse.ps1` `$pinnedSha` carry the same commit. Long hashes
live only here and in the binding contract (R636).

Qualifying evidence (supervisor-freeze AD-093, cited in packet + commit): reproduced live
defect + provider CLI drift + D-024-R684..R699 — preserved causal trace
`project-control/reports/M0-T140-canary-b502r1-causal-trace.md`.

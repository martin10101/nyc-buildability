# M0-T134 cross-SHA provenance record (D-024 Amendment 40, Cluster B0)

Canonical record mapping the accepted M0-T134 (MRL Tranche A) governance state from the
archive branch onto the clean candidate branch. It exists because Amendment 40 (D-024-R542)
requires an explicit cross-SHA provenance record "rather than pretending the old reviewed
SHA is the new SHA". Nothing in this record re-attests review; it records WHAT was carried,
FROM WHERE, and proves by content identity that the reviewed material is byte-identical.

## 1. Identities

| Role | Ref | SHA |
|---|---|---|
| Archive/evidence branch (preserved unchanged, no upstream) | `stabilization/D-024-mrl` | `76c4edff3175f0d185c136e52e1329e3a5cf8199` |
| Reviewed commit named in every M0-T134 gate + DCV record | `ad770ad4` (parent of 76c4edff) | `ad770ad48a2d040c129d9e8d3c1b2bd6cf0fb0f4` |
| Accepted Tranche-A code tree (19-file tools delta) | `5e89175d` | `5e89175de3a793f26dc0655a55bcce5357789028` |
| Clean base (== `origin/control/D-024-fable-codex-loop`) | `6f5d12a6` | `6f5d12a6203c2c89390a982657fa8d66a91a0c3d` |
| Candidate branch, tools reapply commit (B0 step 5) | `candidate/D-024-mrl-option-b` @ `2f3ab124` | `2f3ab124bcb391b41bfeb69c94f0e239f3c222d3` |
| Reviewed content identity (M0-T134 G0/G2/G3/G4 + DCV row) | `content_manifest_sha256` | `1c3078c62692b26b3054c4239d51a2c79dec5da8f6ad8b9f6aad7ac051a6f23e` |
| `origin/main` (untouched) | | `d8b3899f61efa6620e18a26541ced96020f5bef9` |

The candidate branch does NOT contain `ad770ad4` or `76c4edff` in its ancestry (B0 step 7:
abandoned ancestry is not copied). The `reviewed_sha` fields inside the carried gate records,
`project-control/reports/M0-T134.json`, and the D-024 `verification.json` row therefore still
name `ad770ad4…` — the commit the independent reviewers actually reviewed. They are deliberately
NOT rewritten to a candidate SHA: the binding that survives the branch move is the CONTENT
identity below, which is a function of the reviewed blobs and not of any commit id
(`tools/directive_registry.py::frozen_git_identity` hashes `(path, mode, type, blob-id)` entries;
the commit only selects the tree).

## 2. Content-identity reproduction on the candidate tree

Computed with the canonical functions (`git_tree_manifest` + `control_plane_entries` +
`_hash_manifest_entries`, the same composition `project_control._task_git_identity` uses) over
the 22 `allowed_paths` of `project-control/tasks/M0-T134.json` at the staged candidate tree
`800a9ed3c4b98cc286117cab9a8202a7d6eb3ef4` (`git write-tree` of the governance set immediately
before this record file was staged; this record is not among the 22 paths, so the identity is
unaffected by it — the clean post-commit re-verification at HEAD is recorded in the M0-T136
packet-creation commit):

```
entries: 19 (tools)  control-plane: 3 (project-control/reports/M0-T134-*)
identity: 1c3078c62692b26b3054c4239d51a2c79dec5da8f6ad8b9f6aad7ac051a6f23e   == archive value
```

Per-path blob comparison, reviewed commit `ad770ad4` vs candidate tree (first 12 hex of the git
blob id; "identical" means the same content-addressed object):

| Path | `ad770ad4` blob | candidate blob | Result |
|---|---|---|---|
| `project-control/reports/M0-T134-G2-self-check.md` | `480883f6ab5c` | `480883f6ab5c` | identical |
| `project-control/reports/M0-T134-producer-report.md` | `63af50fe3857` | `63af50fe3857` | identical |
| `project-control/reports/M0-T134-tranche-a-evidence.json` | `4c8273f03c83` | `4c8273f03c83` | identical |
| `tools/agent_supervisor/checkpoint_extraction.py` | `7cc06a435efe` | `7cc06a435efe` | identical |
| `tools/agent_supervisor/claude_runner.py` | `9532fbbe150f` | `9532fbbe150f` | identical |
| `tools/agent_supervisor/mrl_codex_decision.py` | `db416e4265f9` | `db416e4265f9` | identical |
| `tools/agent_supervisor/mrl_exec_identity.py` | `43a24a74d7f8` | `43a24a74d7f8` | identical |
| `tools/agent_supervisor/mrl_remote.py` | `efbd3700a3e5` | `efbd3700a3e5` | identical |
| `tools/agent_supervisor/mrl_transport.py` | `91083fddb7d5` | `91083fddb7d5` | identical |
| `tools/agent_supervisor/mrl_worker_result.py` | `a470fb3180b9` | `a470fb3180b9` | identical |
| `tools/agent_supervisor/schemas/mrl_claude_checkpoint.schema.json` | `c19baad6de56` | `c19baad6de56` | identical |
| `tools/agent_supervisor/schemas/mrl_codex_decision.schema.json` | `525661492698` | `525661492698` | identical |
| `tools/agent_supervisor/schemas/review_verdict.schema.json` | `cd5a5c2826d3` | `cd5a5c2826d3` | identical |
| `tools/agent_supervisor/schemas/worker_result.schema.json` | `e9765fce19bb` | `e9765fce19bb` | identical |
| `tools/gate_runner.py` | `b99041275211` | `b99041275211` | identical |
| `tools/test_agent_supervisor_checkpoint_extraction_split.py` | `f0db5f31bc9d` | `f0db5f31bc9d` | identical |
| `tools/test_agent_supervisor_mrl_codex_decision.py` | `0bfbf898010b` | `0bfbf898010b` | identical |
| `tools/test_agent_supervisor_mrl_exec_identity.py` | `9fec7119ad02` | `9fec7119ad02` | identical |
| `tools/test_agent_supervisor_mrl_remote.py` | `3814127c3f47` | `3814127c3f47` | identical |
| `tools/test_agent_supervisor_mrl_transport.py` | `6402442370c1` | `6402442370c1` | identical |
| `tools/test_agent_supervisor_mrl_worker_result.py` | `3e813593791e` | `3e813593791e` | identical |
| `tools/test_gate_runner.py` | `db0e07e27af0` | `db0e07e27af0` | identical |

Re-verification command (any later HEAD; must print the identity above while the 22 paths are
unchanged):

```
python - <<'EOF'
import json,sys; sys.path.insert(0,'.')
from pathlib import Path
from tools import directive_registry as dr, project_control as pc
t=json.load(open('project-control/tasks/M0-T134.json',encoding='utf-8'))
print(pc._task_git_identity(dr, t, None))
EOF
```

## 3. Governance records carried (byte-identical from `76c4edff`, explicit paths only)

- `project-control/gates/M0-T134-G0.json`, `-G2.json`, `-G3.json`, `-G4.json`
- `project-control/reports/M0-T134-DCV.md`, `-G0-readiness.md`, `-G2-self-check.md`,
  `-G3-code-review.md`, `-G4-qa-review.md`, `-evidence-map.json`, `-producer-report.md`,
  `-tranche-a-evidence.json`, `M0-T134.json`
- `project-control/reports/LAUNCH_CONTRACT_MATRIX.md`, `LAUNCH_CONTRACT_RESULTS.json`,
  `STABILIZATION_REPAIR_PLAN.md` (the M0-T135 `allowed_paths`; without them the M0-T135
  packet fails validator check c17)
- `project-control/tasks/M0-T134.json` (accepted), `project-control/tasks/M0-T135.json` (backlog)
- `project-control/state.json` (delta vs base is exactly `+M0-T134` in `accepted_tasks` +
  `updated_at`, i.e. what `project_control.sync_state()` produces)
- `project-control/directives/D-024-fable-codex-loop/source-038-amendment.md`,
  `source-039-amendment.md` (digests re-verified against `manifest.sources`)

Registry files were NOT copied; only their semantic deltas were appended onto the base-formatted
files (no reserialization churn — every removed line in `git diff` is a necessarily updated
count/digest/timestamp field):

- `requirements.json`: rows `D-024-R472..R514` (amendments 38/39) appended verbatim, followed by
  the Amendment-40 rows `D-024-R515..R606`.
- `manifest.json`: sources 038/039/040, three audit entries, `amendments`, `locked_requirement_ids`
  (append-only; equals the ordered id list), `scope.task_ids` `+M0-T134` (archive delta)
  `+M0-T136 +M0-T137` (Amendment 40), recomputed id/content digests.
- `verification.json`: the M0-T134 `task_verifications` row appended verbatim (its
  `reviewed_sha`/`reviewed_manifest_sha256` are the archive values, per Section 1).

## 4. Deliberately NOT carried (with reasons)

| Archive change | Reason |
|---|---|
| `project-control/tasks/M0-T133.json`, `reports/M0-T133-G2-self-check.md`, `reports/M0-T133-producer-report.md`, `reports/M0-T133.json`, `reports/M0-T133-recertification.md` | Abandoned M0-T133 renewal-state narrative (D-024-R474 forbids the renewal; R480 keeps M0-T133 unaccepted). The base packet already holds M0-T133 in `rework`. |
| `docs/SESSION_HANDOFF.md` (archive seq-52 narrative) | Obsolete handoff claims; regenerated only at the final frozen Tranche-B candidate (D-024-R594). |
| Campaign record `next_action` pointing at "renew the claude_runner.py modularity exception" | Stale current-work pointer; advanced canonically to the Tranche-B state via `campaign_continuity.advance()` (seq 71). |
| Branch ancestry `ad22e4dc..76c4edff` | B0 step 7. |

## 5. Validators (run on the staged candidate tree before the continuity commit)

- `python tools/validate_directive_compliance.py --check` -> the only error was
  `c17 M0-T135 allowed_paths resolve to ZERO tracked files at HEAD`, which is the pre-commit
  state (c17 resolves at HEAD, and the three LAUNCH_CONTRACT/STABILIZATION files were staged, not
  committed). The post-commit result is recorded in the M0-T136 packet creation commit.
- `python tools/validate_mcp_policy.py` -> exit 0
- `python tools/validate_product_map.py` -> exit 0
- `python -m tools.agent_supervisor.campaign_continuity --status` -> exit 0
- `python tools/project_control.py status` -> loads (M0-T134 accepted)

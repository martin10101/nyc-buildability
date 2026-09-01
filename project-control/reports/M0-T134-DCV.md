# M0-T134 DCV — independent directive-compliance verification (D-024)

**Verifier:** directive-compliance-verifier (read-only; producer ≠ verifier) · **Directive:** D-024
**Reviewed HEAD:** `ad770ad4` · **Content identity (reviewed_manifest_sha256):** `1c3078c6…`
**Applicable requirement set (derived via `evaluate_task_refs`): 10 —** R500, R501, R502, R503, R504,
R505, R509, R510, R511, R514. (Governance R489–R499/R506–R508/R512–R513 are not accept-applicable to
this production-code task.) **All 10 independently verified PASS.** See `verification.json`
task_verifications[M0-T134] for the per-requirement evidence rows.

## Independent reproduction (not a summary of the producer report)
- **Git/candidate binding (trap C):** `git diff 5e89175d..ad770ad4 -- tools` is empty; `tools/` subtree
  identical at both (`1fb85dc8`); machine record bound to `repo_head 5e89175d` / `repo_tree f8d3bbd4`
  (== `5e89175d^{tree}`). Acceptance rests on tests run at the exact reviewed code tree.
- **Modularity (trap A, R500):** the immutable owner text (Amendment 39 item 2 / R493 / AS-1) requires
  `modularity_exceptions.json` **byte-restored** to its `6f5d12a6` form (retaining the 1410
  `claude_runner.py` file exception), with the gate passing **because of the split**. Verified: current
  git blob sha256 `dba91e16…1792c7` == `6f5d12a6`; `modularity_baseline.json` `8830a47d…731ca5` ==
  `6f5d12a6`; the forbidden M0-T133 renewal (1435/1432, exp 2026-11-30) was reverted by the
  orchestrator governance commit `f5ed116d` only; producer code commits touched **zero** forbidden
  paths; unpiped `modularity_check.py --check` → raw exit 0 (`claude_runner.py` 1319 ≤ 1410).
  **Adjudication:** restoration/no-renewal — NOT exception removal + 1000-line compliance. The retained
  exception **is load-bearing** (1319 > 1000 hard, > 1258 baseline). Its expiry **2026-11-25** can break
  the gate if the file is still > 1000 then; this is a disclosed future governance obligation (producer
  report §6), owner-directed, and NOT a Tranche-A defect. Wording is unambiguous; no owner
  interpretation required.
- **Scope (trap B):** exec-chain/transport/remote are additive primitives; executable-chain supply,
  live model/version probe, and CLI/loop dispatch are Tranche B — deferred and disclosed. No acceptance
  statement treats a primitive as live runtime closure.
- **Lineage (trap D):** the branch descends from control head `ad22e4dc` (which descends from
  `6f5d12a6`); it is **not** an Option-B integration branch. Read-only evidence: no
  `origin/stabilization/D-024-mrl` ref, no push/fetch in reflog, control branch `control/D-024-fable-codex-loop`
  preserved at `ad22e4dc`. Nothing pushed; PR #241 untouched. See the clean-reapply manifest in the
  acceptance return.

## Reviewer independence
Producer identity (code) = the prior engineering/producer session (`producer_agent` = mrl-tranche-a-producer);
G3 = code-reviewer, G4 = qa-engineer, DCV verifier = directive-compliance-verifier — all distinct from
the producer. Test-coverage genuineness was cross-checked by a second independent read-only agent.

**DCV verdict: PASS on all 10 applicable requirements at identity `1c3078c6…` / reviewed_sha `ad770ad4`.**

# M5-T049 DCV — directive-compliance verification (directive-compliance-verifier, saved VERBATIM from the two agent returns)

## Return 1 (primary; transport-truncated at the tail — the truncated sentence completed in Return 2)

Verification complete. All primary evidence reproduced independently at the frozen identity. Here is my return.

---

## DCV RETURN — M5-T049 (D-001 regime; applicable requirement D-066-R001 only)

### RESTAMP PRE-AUTHORIZATION (stated up front)
My verification was performed at frozen submit head `f3bf4fd3d65ff8db17d91aba48e4b83c2670cff2`. It **carries to any restamp target sha `<T>`** iff ALL of these hold, checkable per-commit:

1. `git diff f3bf4fd3d65ff8db17d91aba48e4b83c2670cff2..<T> -- <each of the 7 allowed_paths>` is **empty** (byte-stable material identity). The 7 paths are the three `services/api/app/rules/named_street_override{,_table,_matching}.py`, the three `services/api/tests/rules/test_named_street_override{,_table,_matching}.py`, and `project-control/reports/M5-T049-producer-report.md`.
2. `evaluate_task_refs(M5-T049)` still returns `ok=true` with `applicable_ids == cited_ids == ["D-066-R001"]`.
3. `python tools/validate_directive_compliance.py --check` still exits 0 at `<T>`.
4. **Disjoint-peer tolerance:** peer commits landing between `f3bf4fd3` and `<T>` are permitted PROVIDED they touch only control-plane/docs/other-task material (ledger, `project-control/directives/**` audit-log appends, gate/report/state files, Tier-2 docs, or the M5-T048/M5-T050 lanes' own task/report/directive/docs files) and do NOT alter any of the 7 allowed_paths (guaranteed by condition 1). D-066-R001 is an orchestrator packet/graph obligation with no code in the 7 paths, so peer edits elsewhere cannot regress it.

Note on the manifest digest below: `manifest.json`'s `audit_log` is append-only and gains an entry each time a new task binds to D-066 (last entry at capture time: M5-T050 bind, 2026-09-19T10:03). If further binds land before accept, the manifest digest shifts but R001's **text** is governed by `requirements_content_digest_sha256 = a92a984b801e9946a9f2f968bbc0e9a37b238968d53882fe16f164dc656b15d7`, which I confirmed stable and matching.

### APPLICABILITY (self-verified)
`reg.evaluate_task_refs(M5-T049)` → `ok=true`, `applicable_ids=["D-066-R001"]`, `cited_ids=["D-066-R001"]`, `missing/invalid/unresolved` all empty. Digests match manifest: requirements.json `a92a984b…` == `requirements_content_digest_sha256`; source-001.md `4cb05c94…` == `sources[0].content_digest_sha256`.

### D-066-R001 — SATISFIED
Obligation: at every contract seam regenerate the code graph, embed a graph-derived nav block (key consumers / dependencies / impact set) in the packet, instruct the producer to use `query.py --no-regen` before broad sweeps, graph stays advisory / verified in source. Primary evidence I reproduced:

- **Nav block present, graph-derived** — `project-control/tasks/M5-T049.json` inputs[3] ("CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated at this seam, 747 files/15766 nodes)") names all four depth-1 consumers with line anchors (`named_street_override_status.py:33`, `wide_street_live_provider.py:104`, `tests/rules/test_named_street_override.py:29`, `tests/rules/test_wide_street_wiring.py:68`), the depth-2 set (`wide_street_wiring.py`, `rule_evaluation.py` route, api tests), and the M5-T043 precedent. I ran the packet-instructed `python tools/code_graph/query.py --no-regen impact services/api/app/rules/named_street_override.py` (exit 0, cache served) and it returned **exactly that consumer set** — the nav block is graph-derived and current.
- **Producer instruction present** — inputs[3]: "Run `python tools/code_graph/query.py --no-regen impact <path>` before any sweep; graph is ADVISORY - verify in source."
- **Graph regenerated at the seam** — `manifest.json` audit_log entry 2026-09-19T08:15:16 ("matcher-extraction packet contracted with a regenerated-graph nav block"); graph cache present (served `--no-regen`, exit 0).
- **Advisory + verified in source (my own reproduction, not the producer's claim)** — at frozen head `f3bf4fd3`, all four consumer imports exist at the exact claimed line numbers, each importing from the f[…truncated in transport; the sentence continues: facade, which the extraction preserved — see Return 2 for the verdict tail]

## Return 2 (the requested tail, verbatim)

Resending only the missing tail.

**(1) VERDICT: PASS**

**(2) Validator:** `python tools/validate_directive_compliance.py --check` → **exit 0**

**(3) v2 task_verifications row fields:**
- `reviewed_manifest_sha256`: `69add60fc7fe9a5bf5d1e60f014c6dbc4cbb227dc5f1162e0fea210340dd73c6`
- `producer`: `backend-engineer`
- `verifier`: `directive-compliance-verifier`

## Return 3 (post-accept confirmation of the field-sourcing correction, verbatim)

No dispute - your correction is right, and I reproduced the facts it rests on.

- **The corrected field value is correct.** All four gate records G2-G5 carry `content_manifest_sha256 = 15de365781f870d3db9503ab32a96281094fa413f944ed9c7a987c0f40e53455` (reviewed at `aa8e2f53`), which is byte-stable to the frozen head and to the accept target on the allowed_paths. This matches the documented v2-assembly pattern (`reviewed_manifest_sha256` sourced from the gate records, not the directive registry). My `69add60f...` was the D-066 directive-manifest digest - the wrong artifact for that CLI field (I followed the prompt's original naming); it is correctly preserved as the directive-registry identity I verified.

- **Accept target `0c7b17f1` satisfies my carry conditions.** Condition 1 reproduced: `git diff f3bf4fd3..0c7b17f1` is empty on all 7 allowed_paths. `evaluate_task_refs` was ok/applicable==cited at freeze and depends on task refs, not head. Validator was exit 0.

- **One precision note on condition 4 (not a dispute).** The peer commits between `f3bf4fd3` and `0c7b17f1` include actual M5-T048 code (`services/api/app/scenario/contract.py`, `proposal.py`, `packages/contracts/**`), which is broader than the literal "task/report/directive/docs files" phrasing I used for the M5-T048 lane. The carry still holds on the operative guard: none of it touches M5-T049's 7 allowed_paths (condition 1 empty), the M5-T048 scenario package is entirely outside M5-T049's blast radius (the impact query's consumer set is rules/spatial/api-rule-evaluation, never scenario), and D-066-R001 has no code in the allowed_paths at all - so disjoint M5-T048 code cannot regress it. The rest of the changed set is M5-T049's own gate/report/state/task control-plane records plus `docs/WORKING_KNOWLEDGE.md`, exactly as anticipated.

The row stands as recorded. M5-T049 (231st) accept at `0c7b17f1` confirmed under the pre-authorization; verdict remains **PASS** for D-066-R001.

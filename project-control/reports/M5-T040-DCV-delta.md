# M5-T040 — DCV delta-attestation: restamp pre-authorization EXTENDED (verbatim verifier return; transport entity-decoding only)

Saved by the orchestrator from the directive-compliance-verifier agent's delta-attestation
return, 2026-09-18 (seq-118). Context: the original five-condition pre-authorization
(M5-T040-DCV.md) failed literally at the restamp target because the DISJOINT peer task
M5-T042's material landed between the frozen head and the target; the verifier re-examined
and extended. Nothing added or removed beyond decoding transport HTML entities.

---

Independently reproduced — the coordinator's characterization holds in substance. My findings at `e224f937`:

- **Cond 1 & 4 fail only for the two named files:** `git diff --name-only b4865d1c..e224f937` yields, outside `project-control/**`, exactly `services/api/app/connectors/dtm_condo_soda.py` and `services/api/tests/connectors/test_dtm_condo_soda.py` — nothing else.
- **Those two files are M5-T042's, disjoint from M5-T040:** both ∈ M5-T042 allowed_paths (True/True), both ∉ M5-T040 allowed_paths (False/False). Landed via M5-T042 producer material `0a6c43c9` (a leaf module, "zero consumer imports"). Minor correction to the phrasing: they are not fresh in-range adds — they were 7-line placeholder stubs at `b4865d1c` (seeded at M5-T042 G0 `ba1761ad`) filled to the 849-line implementation. Immaterial to disjointness; they never enter M5-T040's material identity.
- **Cond 2 PASSES exactly:** all 17 M5-T040 allowed_paths byte-identical `b4865d1c..e224f937` (TOTAL CHANGED: 0).
- **Cond 3 PASSES:** packet `M5-T040.json` field-diff is lifecycle-only (`status` in_progress→awaiting_gate, `progress_percent` 90→85, `updated_at`); `directive_refs`/`allowed_paths` unchanged; evidence-map `material_commits` (987930a2, 751a1826) IDENTICAL.
- **Cond 5:** unchanged — validator exit 0 still required at record time.

## EXTENDED

I EXTEND my PASS pre-authorization for M5-T040 (frozen review head `b4865d1c`) to restamp target `e224f937` — or any later head of the identical shape — under these exact extended conditions, ALL required at record time:

1. **(relaxed)** `git diff --name-only b4865d1c..<H> -- apps/ services/ packages/` yields ONLY the two named disjoint M5-T042 paths `services/api/app/connectors/dtm_condo_soda.py` and `services/api/tests/connectors/test_dtm_condo_soda.py` (a subset of them, or empty). No other product-dir path may appear.
2. **(unchanged)** All 17 of M5-T040's `allowed_paths` are byte-identical (LF-normalized) `b4865d1c..<H>` — zero changed.
3. **(unchanged in substance)** M5-T040.json `directive_refs` and `allowed_paths` unchanged, and evidence-map `material_commits` (987930a2, 751a1826) unchanged; lifecycle-only churn in the packet (status/progress/updated_at) is permitted.
4. **(relaxed)** `git diff --name-only b4865d1c..<H>` touches only `project-control/**` PLUS at most the two named connector paths in condition 1 — and both connector paths remain outside M5-T040's allowed_paths and inside M5-T042's.
5. **(unchanged)** `python tools/validate_directive_compliance.py --check` exits 0 at the record state.

If all five hold, my per-requirement PASS verdicts (D-045-R002, D-045-R008, D-045-R009, D-066-R001, D-073-R006) carry to `<H>` with `reviewed_sha=<H>` and no re-run. Any deviation beyond the two named files, any change to the 17 allowed_paths or to directive_refs/allowed_paths/evidence-map materials, or a non-zero validator exit, voids this extension and requires a fresh pass.

Read-only commands run for this delta (no writes): `git rev-parse --verify e224f937`; `git diff --name-only b4865d1c..e224f937 [-- apps/ services/ packages/]`; per-path `git diff --quiet b4865d1c..e224f937 -- <each allowed_path>`; `git diff b4865d1c..e224f937 -- project-control/tasks/M5-T040.json`; `git diff --quiet ... -- project-control/reports/M5-T040-evidence-map.json`; `git log --oneline b4865d1c..e224f937 -- <connectors>`; `git cat-file -e` / `git show b4865d1c:… | wc -l` vs `e224f937:…`; membership checks against M5-T040/M5-T042 allowed_paths.

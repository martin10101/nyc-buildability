# M5-T088 — directive-compliance verification (directive-compliance-verifier "dcv-t088", read-only)

> Transmission history: pinned at fa7e5fae, delivered as four SendMessage parts (1/4..4/4) ending with END-OF-REPORT;
> no truncation. Part 1 carries the blob-level restamp predicate (3 blobs 42545728 / c55e2cd7 / b4c1b025, max_envelope.py
> f0abf884, requirements.txt 7da554cf / requirements.in bf38a09e, no production importer). Joined verbatim by the
> orchestrator (transport wrapper tags removed only). Validator EXIT 0. F-HIGH-1 (proposal.py all-pairs simplicity
> check) is outside this packet and is now contracted as M5-T095.

---

M5-T088 DCV — PART 1/4: restamp pre-auth + frozen identity + gates. PINNED HEAD at start = fa7e5fae8c9d0ae63851481f5f0a21c32cafa2aa.

RESTAMP PRE-AUTHORIZATION (blob-level). My PASS holds at any future accept-head H with NO re-review, and the orchestrator MAY add my verifier rows to verification.json at H, provided at H:
(1) the 3 allowed-path blobs equal the frozen blobs — massing_model.py=4254572804f0a3513cfad8247561db473fb0f75d, test_massing_model.py=c55e2cd76c964a11714c04943065462b9030cfec, M5-T088-producer-report.md=b4c1b0254cf7b154b6b6dbc069793dfb5a421885 (equivalently recomputed content_manifest_sha256=327ef492bd5a7b37284dbf5f7870639d4ff879028a01f43f5686bf88cc48fc86);
(2) max_envelope.py blob=f0abf88479d078d8ec7e88d4c2b1942fd69c040d;
(3) requirements.txt=7da554cf, requirements.in=bf38a09e unchanged;
(4) massing_model.py still has no production importer outside its test.
DISJOINT-PEER TOLERANCE: broad — H may contain any disjoint peer commits (other lanes' material, control-plane/ledger/state/gate/report writes, directive captures/amendments); none void this. Only a change to the 3 frozen blobs (manifest != 327ef492) voids it and forces re-review.

FROZEN IDENTITY: independently recomputed 327ef492…fc86 from git plumbing (ls-tree the 3 paths at 9f355fe1 → the _hash_manifest_entries encoding) — MATCH. It equals reports/M5-T088.json AND all four post-submit gate stamps (G2/G3/G4/G5=327ef492). G0 stamps e569b4fa at the pre-work seam 5e9dbd07 (administrative) — legitimately different. The 3 blobs are byte-identical at producer 353b919d = material 9f355fe1 = HEAD fa7e5fae (cherry-pick preserved identity).

GATES (all PASS; producer=3d-massing-engineer is none of them): G0 orchestrator/administrative @5e9dbd07; G2 orchestrator/self_check; G3 geospatial-engineer (independent); G4 qa-engineer (independent); G5 security-reviewer (independent). Each independent-review reviewer is listed in reviewer_agents. Applicability check: reg.evaluate_task_refs → ok=True, applicable_ids == cited == {D-066-R001, D-087-R001/R002/R003/R009}, reasons=[].

---

M5-T088 DCV — PART 2/4: requirement rows (1 of 2).

D-066-R001 (navigation block) — SATISFIED. Packet M5-T088.json input #17 carries the code-graph navigation block: names massing_model.py's only importer (its test), FORBIDS max_envelope.py + every scenario module, names the GLB writer (M5-T092) as the later generic consumer, instructs `tools/code_graph/query.py --no-regen impact` before sweeps, states graph regenerated-at-seam + advisory. Verified in source: grep of services/api/app finds NO production importer of massing_model (only its own test) — the block's key claim is TRUE.

D-087-R001 (use today's capacity via gated packets) — SATISFIED. M5-T088 is a fully gated ledger unit: G0 contract seam 5e9dbd07 (adds tasks/M5-T088.json + producer-report placeholder), claim seam 114e5e56 ("G0 PASS x5 at 5e9dbd07; claimed FULL worktree path + progress 20"), material submit 9f355fe1, then G2/G3/G4/G5 all PASS — gates/M5-T088-G{0,2,3,4,5}.json all present. Produced concurrently with the disjoint T089/T090/T091/T092. No state or gate skipped; normal gated process intact.

D-087-R002 (no interference / pairwise-disjoint scopes) — SATISFIED. M5-T088 allowed_paths {massing_model.py, tests/scenario/test_massing_model.py, reports/M5-T088-producer-report.md} are pairwise DISJOINT from T089 {connectors/building_footprints_arcgis.py, its test, tests/fixtures/building_footprints/**}, T090 {apps/web/package.json, package-lock.json}, T091 {cad/pdf_sheet_writer.py, its test}, T092 {cad/glb_writer.py, its test} — read from each packet's allowed_paths. Isolated worktree wt-m5t088 (packet.worktree). Material 9f355fe1 name-status = exactly the 3 allowed files, zero forbidden.

---

M5-T088 DCV — PART 3/4: requirement rows (2 of 2). Primary evidence in services/api/app/scenario/massing_model.py.

D-087-R003 (3D released; made safe for real geometry, DB-054 a-j) — SATISFIED. Canonical EPSG:2263 (L91-92); typed MassingModelError (L134). Bounds, each a typed refusal raised BEFORE the heavy work it guards: coordinate magnitude MAX_COORD_ABS=1e8 (L123) → coordinate_out_of_range before any shapely (L225-229); triangulation budget MAX_TRIANGULATION_WORK=2_000_000 (L129) + up-front least-work refusal (L283-287, 598) → triangulation_budget_exceeded (L277-280); output ceiling MAX_TOTAL_MESH_VERTICES=100_000 (L126) → over_cap_output_vertices (L579-584); floor cap MAX_TOTAL_FLOORS=2000 (L116) → over_cap_floors, message "the floor stack has {total} floors" (names floors), raised before ring prep (L515-518); fail-closed containment footprint_outside_lot tol 1e-6 (L119, L693-705); local-origin volume conditioning (L383-410); CCW normalization + collinear collapse in _prepare_ring (L199-260). Tests: 41 funcs/54 cases — non-star U/comb (COMB L94), CW rings (cw_lot/footprint/both L640), exact collinear, ~0.5-ft-outside + on-lot-line, non-integer coords, keyhole_lot_ring (L494), honesty labels (L567/L575). Independently confirmed mutation-sensitive: G3 byte-level re-derivation PASS (loaded accepted blob 255de6ec, to_json byte-equal); G4 all 14 producer mutants RED + 6 own weakenings PASS.

D-087-R009 (unchanged boundaries / zero deps / unwired) — SATISFIED. requirements.txt (7da554cf) + requirements.in (bf38a09e) byte-identical base↔HEAD; no lockfile change; material 9f355fe1 touches NONE of the forbidden paths (name-status = only the 3 allowed); max_envelope.py blob f0abf884 byte-identical 9f355fe1^↔HEAD (byte-untouched); module unwired; PR #241 unmerged (named only in capture-commit messages as staying unmerged); gates G0-G5 all stand.

---

M5-T088 DCV — PART 4/4: F-HIGH-1 ruling, sweep, harness, verdict.

F-HIGH-1 RULING — leaves NO cited requirement unsatisfied. F-HIGH-1 is the UPSTREAM proposal.py validate_proposed_massing / _ring_is_simple O(n^2) DoS (runs first at massing_model.py:675-676, before every massing bound). It is (a) in proposal.py — OUTSIDE this packet's allowed_paths (uneditable here); (b) NOT part of DB-054 (a)-(j) — it is producer Discovery 1, a new finding; (c) unreachable in production — module UNWIRED, and D-087-R003 explicitly scopes this hardening to "before any wiring"; (d) RECORDED as an OPEN wiring precondition: DISCOVERY_BACKLOG.md DB-034(a) (proposal-validator GLOBAL vertex budget, disposition "bind as PRECONDITION on the first packet that wires editor input to the validator, B1/B3") plus the G5 report's explicit "must gate the WIRING packet" disposition. G3 and G5 independently confirmed the module's OWN bounds are complete and fire before heavy work — exactly what R003 requires of the truth object. So R003 (and all cited reqs) SATISFIED; F-HIGH-1 is correctly deferred. NOTE (non-blocking): keep it recorded through the accept seam — it already is (DB-034(a) OPEN + G5).

G4 survivors MD (y-only magnitude test gap) / ME (scan-charge order): advisory only — source L225 checks abs(x) OR abs(y) (correct today), and AS-4's required M6 remove-bound mutation reddens; non-blocking.

PROHIBITED-ACTION SWEEP — clean: status awaiting_gate (NOT accepted); no verification.json row for M5-T088; no accept/merge commit (only submit/gate); nothing deployed / installed (no requirements change) / purchased / closed; module unwired; PR #241 unmerged.

HARNESS: `validate_directive_compliance.py --check` → EXIT 0 (run once, direct exit code, from services/api). CI: HEAD fa7e5fae pushed to origin/candidate/D-024-mrl-option-b; CI workflow (control-plane job included) = success at fa7e5fae (and f6116a5c, 6c79cd88). The two scheduled dependency-audit failures are on an unrelated older head d8b3899f, not this task's chain.

M5-T088 DCV VERDICT: PASS 5/5

END-OF-REPORT

# M5-T182 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `32a11ed4b0925a1c3d636180bcecd3b987c5b15c` (branch `task/wave26-envelope-constraints`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R044, R092.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. Three advisories are already recorded for the wiring task M5-T172 (no symmetric lot_depth<=0 guard; the docstring word "exactly" for sub-cent floor-area inputs; the disjoint-peer identity note from other wave-26 tasks). None changes a value and none blocks this task.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-15T06:46:09Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

````
All checks reproduced. The validator passed with a direct exit code 0 at the frozen head, corroborated by the green control-plane CI job at the exact frozen head. Here is my verification return.

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T182 (directive D-094, 2 rows)
VERDICT: PASS

I am an AI agent; this is an independent read-only verification, not a human or professional review. I produced none of this work or its records. I reproduced each item from primary evidence (the owner's words in the directive sources, the task files at the frozen head, git objects, the registry helper, the schema, the focused tests, and CI at the exact head).

(1) HEAD VERIFIED
 - I read the frozen head 32a11ed4b0925a1c3d636180bcecd3b987c5b15c on task/wave26-envelope-constraints in /root/project/w-wave20, via git plumbing.
 - HEAD was unchanged before and after my checks (git rev-parse HEAD both times = 32a11ed4; base main 2bcdb05a).
 - The five allowed-path files are blob-identical at db590413 (reviewed), 86ae6cbb (gate-recorded/submit) and 32a11ed4 (frozen head), so G1–G4 apply at one content identity.

(2) ROWS
ROW D-094-R044 — PASS
 - The footprint outline in placement.py is built by compute_placement_geometry from derived figures only: plan_depth = plate_full/frontage (round half up), and every ring vertex is an arithmetic expression of the 0-ft lot-line touches and the computed frontage/depth — no coordinate is typed in.
 - The outline area is re-measured from the vertices by the shoelace formula and must reconcile to the plate within 0.5 sq ft or build_placement raises; I reproduced 6716.66 vs plate 6716.67 (0.01 apart), matching placement-building-b.json row footprint-tax-map.
 - The withheld branch (placed=False, or any fact None read by `is None`, or a 0 frontage that fails closed) carries no outline key; the schema withheld oneOf (additionalProperties:false) rejects one; test_s3 and the 4-way missing-fact test pass (54 focused tests green).
 - Stays open: R044 also governs the actual drawing (M5-T173) and the wired report's "every drawn shape traces to result geometry"; this task is not wired, so that live drawing-vs-result check remains for M5-T172/M5-T173.
ROW D-094-R092 — PASS
 - Both modules carry measure const "residential_floor_area" (byte-equal to schema $defs.area_measure), the same measure the preliminary apartment estimate uses; area_allocation applies the one stated 0.60 share to the residential floor area 20,150 (apartment 12,090.00 + other 8,060.00 = total 20,150.00), matching row area-allocation.
 - Every output carries the conversion_statement const "plate = zoning floor area per storey; no gross-up, exclusions or wall-thickness conversion worked" (byte-equal to $defs.plate_conversion_statement); test_s7 pins all three consts against the bundled schema and I reproduced it.
 - The plate (zoning floor area per storey, 6716.67) and the physical floor plate are kept distinct — "the physical floor plate (gross-up, exclusions, wall thickness)" is in not_checked and the plate is never returned or labelled as the physical plate (test_s8 reproduced).
 - Stays open: R092's required evidence names the register entry and its wired worked example, and its harness is a wired test that fails if ZFA is used as plate area without a stated conversion; this task delivers the compatible-measure modules+tests but the register entry and the wiring belong to M5-T172 (R092 also depends on R088, the two-zone authorization, outside this task).

(3) BINDING B1–B5
 - B1 PASS: contract commit 007bc2f1 appended "M5-T182" to applicability.task_ids of R044 and R092; the only other requirements.json change was updated_at; git show shows no removed/edited requirement-text line, so no row text changed.
 - B2 PASS: directive_registry.sha256_text_artifact(requirements.json) = c6ea97fcce7c7f5539277e68ecd2c7c486f3d517c6ee0dff7d6c8ee602230301 equals manifest.requirements_content_digest_sha256 (computed and matched).
 - B3 PASS: verification.json has exactly one M5-T182 row, applicable_requirement_ids [D-094-R044, D-094-R092], both requirement states "pending", verifier "" (empty), producer backend-engineer.
 - B4 PASS: reg.evaluate_task_refs(packet) = {ok: True, applicable_ids [R044,R092] == cited_ids [R044,R092], missing/invalid/unresolved all empty}.
 - B5 PASS: no uncited applicable requirement; manifest.affected_tasks includes M5-T182; the full validator at the frozen head (flock, python tools/validate_directive_compliance.py --check) exited 0 quiet, and the control-plane (ADR-005) CI job is success at the exact head 32a11ed4.
 - Gate records PASS at one content identity: gates/M5-T182-{G0..G4}.json all result=PASS — G0 orchestrator @007bc2f1; G1 data-contract-verifier, G2 orchestrator, G3 code-reviewer, G4 qa-engineer all @86ae6cbb. Producer backend-engineer ≠ G1/G3/G4 reviewers. Focused tests 54 passed; ruff clean on all 4 files; modularity_check --check exit 0 (neither new file 340/114 lines flagged); CI run 38693074838 at 32a11ed4 = 21/21 jobs success (incl. api and control-plane).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head without a new review while BOTH hold. (a) Blob-level predicate: the five allowed-path files (services/api/app/scenario/three_answers/placement.py, area_allocation.py; services/api/tests/scenario/three_answers/test_placement.py, test_area_allocation.py; project-control/reports/M5-T182-producer-report.md) keep their exact blob ids as at 32a11ed4, and the R044/R092 row text plus their M5-T182 applicability binding are unchanged.
 - (b) Broad disjoint-peer tolerance: later commits may touch any other file (other tasks' files under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports/directive bindings, new rows appended to D-094, ledger state), plus this task's own acceptance records, plus a merge of the main line that changes none of the predicate's files.

(5) REQUIRED CORRECTIONS
 - None. Three advisories are already recorded for the wiring task M5-T172 (no symmetric lot_depth<=0 guard; the docstring word "exactly" for sub-cent floor-area inputs; the disjoint-peer identity note from other wave-26 tasks). None changes a value and none blocks this task.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The two underlying step-P8 hand readings (return-independent-hand-calculation-17.md/-18.md) themselves; I checked the module values against the settled case placement-building-b.json, not the readings' own derivation (and agreement of two AI readings is not proof).
 - The live wiring into the results document, website, review register and benchmark; out of scope by design (M5-T172 wires them after M5-T169/M5-T170), so no rendered page exists to verify.
 - The whole api suite and the full tools/test_directive_compliance.py (forbidden by this brief); I relied on the api + control-plane CI jobs green at the exact frozen head 32a11ed4 plus the 54 focused tests I ran, and the direct validator exit 0 at the frozen head.
END-OF-REPORT
```
````

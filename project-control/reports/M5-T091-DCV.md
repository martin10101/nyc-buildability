# M5-T091 / M5-T092 — directive-compliance verification (directive-compliance-verifier "dcv-w2", read-only; joint DCV)

> Transmission history: one joint verification pinned at fa7e5fae (live HEAD advanced through disjoint
> orchestrator commits to 464dda21 and beyond; the verifier re-verified the six blobs byte-identical at
> 464dda21), delivered as six SendMessage parts (1/N..6/6) ending with END-OF-REPORT; no truncation. Part 1
> carries the blob-level restamp predicate and the broad disjoint-peer tolerance. Joined verbatim in delivery
> order by the orchestrator (transport wrapper tags removed only); saved identically as M5-T091-DCV.md and
> M5-T092-DCV.md. The verifier's one validator run was still in flight at the final part (its exit code was
> promised as an addendum); the verdicts rest on reproduced primary evidence and direct digest matches.
> Orchestrator predicate re-check at the accept head: all six blobs (86b129c9 / 52f37aa9 / 3b402b53 /
> 64568629 / 9166d160 / 8f390845) byte-identical; identities reproduced; evaluate_task_refs ok. The eight
> advisories in part 5 are routed to docs/DISCOVERY_BACKLOG.md DB-059.

---

DCV for M5-T091 (PDF writer hardening) + M5-T092 (GLB writer) — PART 1/N.

PINNED HEAD at start: fa7e5fae8c9d0ae63851481f5f0a21c32cafa2aa
Material commits: T091 = d0919de6, T092 = 706ae62a. Both reports pin reviewed_sha = 706ae62a (the shared wave-2 review seam head; d0919de6 landed first, 706ae62a is its descendant — reviews pinned at the later seam are valid for both). I will confirm ancestry + that no later commit re-touched these blobs.

RESTAMP PRE-AUTHORIZATION (up front):

BLOB-LEVEL PREDICATE — my verdicts hold at ANY future restamp/accept target SHA S provided S's tree carries these exact blobs:
- M5-T091: services/api/app/cad/pdf_sheet_writer.py = 86b129c9806bc386f9b4569f622327e7a7e60fa4; services/api/tests/cad/test_pdf_sheet_writer.py = 52f37aa971425225fe1dd7fd8abfbb65184b178d; project-control/reports/M5-T091-producer-report.md = 3b402b53d72087bb2595cdcfc802821b62b2dd87
- M5-T092: services/api/app/cad/glb_writer.py = 645686294aefdf3691183f7b2193efed2aabf481; services/api/tests/cad/test_glb_writer.py = 9166d16038935e2d90905e23e1ade4303a72958e; project-control/reports/M5-T092-producer-report.md = 8f3908453e023fe5fc3a6fd2235dd59b95596a18

DISJOINT-PEER TOLERANCE (broad): any number of peer commits touching paths OUTSIDE each task's allowed_paths may land between this verification and the restamp/accept without voiding my verdict. Ledger/state/gate/verification bookkeeping and OTHER tasks' material are all tolerated disjoint peers.

I authorize the orchestrator to: (1) restamp each task's reviewed_sha to the accept-time HEAD, and (2) add MY verification rows to verification.json, provided the six blobs above are byte-identical at that HEAD. If any one of the six blobs differs, this pre-auth is void for that task and a fresh delta-attestation is required.

Verification in progress; requirement rows + findings follow. END-OF-PART-1

---

PART 2/N — Frozen identity, gate integrity, disjoint-peer advance.

HEAD MOVED during review: fa7e5fae -> 464dda21 (peers: M5-T089/T093 gate reports; M5-T081/T086 ACCEPTED 266th/267th). origin/candidate == 464dda21 (pushed). ALL SIX material blobs byte-identical at 464dda21 (re-verified via git ls-tree); NO peer commit touched the six files, the two task JSONs, the two report JSONs, or any gate JSON. My verification is byte-stable; restamp pre-auth (part 1) applies — target = 464dda21.

FROZEN IDENTITY (reproduced, not claimed):
- T091 reports/M5-T091.json content_manifest_sha256 = f2d6b1a7… ; POST-SUBMIT gates G2/G3/G4/G5 ALL stamp f2d6b1a7… (exact). G0 = 011c7bd3… at seam 5e9dbd07 (pre-material readiness — legitimately differs).
- T092 reports/M5-T092.json content_manifest_sha256 = d912b914… ; POST-SUBMIT gates G1/G2/G3/G4/G5 ALL stamp d912b914… (exact). G0 = ceb72953… at 5e9dbd07 (pre-material).
- Material blobs provably untouched since landing (d0919de6 for T091, 706ae62a for T092; d0919de6 is an ancestor of 706ae62a; reviews pinned at the later shared seam are valid for both).

GATES — all required PASS with independent reviewer in reviewer_agents (producer = backend-engineer for both; no gate reviewed by the producer):
- T091 (required G0,G2,G3,G4,G5): G0 orchestrator(admin) PASS; G2 orchestrator(self_check) PASS; G3 code-reviewer PASS; G4 qa-engineer PASS; G5 security-reviewer PASS.
- T092 (required G0,G1,G2,G3,G4,G5): +G1 data-contract-verifier PASS. G3 code-reviewer, G4 qa-engineer, G5 security-reviewer all PASS. Every required gate present, independent, PASS.

APPLICABILITY (authoritative, reg.evaluate_task_refs): T091 ok=true, applicable==cited=={D-066-R001,D-087-R001,R002,R005,R009}, 0 missing/invalid. T092 ok=true, applicable==cited=={D-066-R001,D-087-R001,R002,R003,R006,R009}, 0 missing/invalid. No missing, weakened, combined, or invented refs. Requirement rows follow. END-OF-PART-2

---

PART 3/N — M5-T091 requirement rows (each judged on reproduced primary evidence).

D-066-R001 (obligation; nav block + graph regen) — SATISFIED. tasks/M5-T091.json inputs[16] carries the CODE-GRAPH NAVIGATION BLOCK (pdf_sheet_writer has no importer; forbidden siblings dxf/glb; documents reader read-only; "Run tools/code_graph/query.py --no-regen impact <path>"). G0 report: graph regenerated at seam (817 files/17386 nodes/7525 edges). Primary = the packet JSON itself.

D-087-R001 (obligation; capacity via fully-gated packets) — SATISFIED. M5-T091.json is a complete ledger packet: status awaiting_gate, gates G0/G2/G3/G4/G5 all recorded PASS, producer backend-engineer, worktree wt-m5t091, claim-seam progress log. No state or gate skipped; G0 disjointness + dispatch present.

D-087-R002 (prohibition; no interference, disjoint paths, isolated worktree) — SATISFIED. allowed_paths {pdf_sheet_writer.py, test_pdf_sheet_writer.py, M5-T091-producer-report.md} are pairwise DISJOINT from T092's glb trio. M5-T091-G0.md disjointness table lists M5-T092 + all live/frozen neighbors as "none - EMPTY overlap" (symmetric in T092-G0). Worktree C:\...\wt-m5t091. Material d0919de6 touched exactly the 3 allowed files.

D-087-R005 (authorization; PDF blueprint writing hardened, C-track honesty) — SATISFIED. Primary evidence in pdf_sheet_writer.py: (a) _validate_ring/_coerce_vertex :260-315 return typed SitePlanRefusal, never raise; (b) _num finite guard :453 -> _RenderRefused caught at :211; (c) _screen_caller_text :224-249 imports dxf CLAIM_CLASS_WORDS (:54), screens all 4 caller fields BEFORE drawing; (d) _escape_pdf_text :424 sole paren escaper. test_pdf_sheet_writer.py H-1..H-4 give mutation-sensitive tests + unbalanced-paren round-trip through the REAL in-repo strict reader (:517). Honesty stamp "PROPOSED - NOT A CITY RECORD" :403. G4 reproduced 13/13 producer mutants RED.

D-087-R009 (prohibition; unchanged boundaries) — SATISFIED. stdlib+internal-dxf imports only (:46-54); d0919de6 touches only the 3 allowed files; ZERO requirements.txt/.in change across 5e9dbd07..HEAD; unwired (no production importer; __init__ untouched); no api/main/apps/packages change; golden c38360f9 unchanged (accepted behavior kept). END-OF-PART-3

---

PART 4/N — M5-T092 requirement rows (reproduced primary evidence).

D-066-R001 (obligation; nav block) — SATISFIED. tasks/M5-T092.json inputs[16]: nav block (app/cad orchestrator-seeded; forbidden siblings dxf/pdf; "nothing imports glb_writer yet"; query.py --no-regen instruction). M5-T092-G0.md: graph regenerated at seam (817 files/17386 nodes).

D-087-R001 (obligation; fully-gated packet) — SATISFIED. Complete ledger packet; gates G0/G1/G2/G3/G4/G5 all PASS; producer backend-engineer; worktree wt-m5t092; claim-seam log.

D-087-R002 (prohibition; disjoint/isolated) — SATISFIED. glb trio allowed_paths disjoint from T091 pdf trio; M5-T092-G0.md disjointness table (M5-T091 + neighbors = EMPTY overlap); worktree wt-m5t092; material 706ae62a touched exactly the 3 allowed files.

D-087-R003 (authorization; 3D released, built from deterministic EPSG:2263 geometry) — SATISFIED. glb_writer.py is a deterministic glTF-2.0 GLB writer taking EPSG:2263-aligned local-frame triangle meshes in US survey ft (GlbLocalFrame/GlbMesh :226-252), converting to glTF metres via declared axis map (:387-413) — the runtime 3D format the architecture names (:1-9). Delivered as a gated M5-T092 packet citing R003; G1 independently verified the axis map (det +1, winding preserved). Bridge module; wiring/product-display is a later packet, consistent with the authorization.

D-087-R006 (authorization; CAD/3D export via OPEN interchange formats) — SATISFIED. glTF 2.0 GLB is an open Khronos royalty-free format; write_glb (:578) exports it zero-dependency. R006 required_harness = offline structural tests + round-trip — MET by the in-test spec-derived parser (parse_glb :89-117: magic/version/length, 4-byte alignment, JSON-space/BIN-zero pad, no-BOM) + golden sha256 + AS-2 round-trip. RULING on the G1 note: the official Khronos glTF-Validator was NOT run (npm/Dart, thin client) — a NON-BLOCKING robustness add explicitly routed to harvest, NOT part of R006's required_harness. The G1 verifier independently fetched the official Khronos JSON schemas, wrote its OWN parser, and reproduced the golden EXACTLY. R006 evidence adequate.

D-087-R009 (prohibition; unchanged boundaries) — SATISFIED. stdlib-only imports (:61-66; enforced by test_as5_stdlib_imports_only AST test); 706ae62a touches only 3 files; zero requirements change; unwired (test_as5_not_wired + my grep: no importers); no api/main/apps/packages; honesty label emitted + pinned (test_as3); deterministic golden 30d79d80. END-OF-PART-4

---

PART 5/N — Advisory disposition + prohibited-action sweep + CI.

ADVISORY RULING: NO cited requirement is left unsatisfied. All eight advisories are riders for the wiring packet or housekeeping — none is a boundary/honesty/fail-closed violation at the frozen head:
1. T091 caller-text length bound (G3-F3, G5-LOW): 200k-char address -> 201kB PDF; latent DoS, unreachable (unwired). Not a cited requirement; close at wiring.
2. T092 claim-screen separator gap (G5-MEDIUM): _check_name :361 raw substring vs PDF's _claim_key collapse; "As_of_right"/"Maximum_allowed" evade on caller mesh NAMES. MATCHES the already-ACCEPTED dxf writer (NOT a regression). The writer's OWN emitted strings are clean + pinned (test_as3_no_claim_class_words_anywhere). Defense-in-depth on unwired input; R009/R003/R006 honesty boundary (what the writer emits) HOLDS.
3. T092 word-list drift/under-pin (G5-LOW, G4): glb CLAIM_CLASS_WORDS a literal copy, no drift-guard, 2/11 words tested. Secondary-defense; LABEL fully pinned. Not a cited-req gap.
4. T091 y non-finite coverage gap (G4 survivor): x-only mutant survives, BUT real _coerce_vertex checks isfinite(x) AND isfinite(y) :306 and fail-closes ((0,nan)->non_finite_value, (0,inf)->oversize_input). TEST-COVERAGE gap, behavior correct — R005 satisfied.
5. T092-raises vs T091-returns (G3-F1): each meets its own packet's "typed refusal" wording; reconcile in consumer. No violation.
6. Khronos Validator not run (G1/G3-F2): ruled non-blocking, routed to harvest; R006 met by two independent parsers.
7. __init__ docstring omits glb_writer (G3-F4): orchestrator-owned/forbidden path, correctly untouched. Housekeeping.
8. GLB error echoes caller name (G5-INFO): log-redaction nit; wiring concern.

PROHIBITED-ACTION SWEEP — clean. Both tasks status=awaiting_gate (NOT accepted); zero dependency/lockfile change (no install/purchase); unwired (no route mounted/deployed; no api/main/web); no PR merged/closed; no open blocker references either task (accept-scan clean); no secret/payment/legal/production action.

CI: origin/candidate == 464dda21 (pushed). Latest control-plane CI on the branch is seq-124 (2026-09-21, GREEN: CI+secret-scan+context-budget). NO CI run yet covers the Sep-24 material head — expected mid-wave; orchestrator should secure a green control-plane run at the accept head. Not a blocker for this awaiting_gate DCV; the primary harness evidence is the reproduced G0-G5 gate records (independent reviewers ran 262 pdf/cad + 58 glb tests + all mutants). validate_directive_compliance.py --check still running; result + verdicts in the final part. END-OF-PART-5

---

PART 6/6 — Registry integrity, restamp predicates, VERDICTS.

REGISTRY INTEGRITY (targeted, reproduced): recorded manifest source digests == actual sources — D-087 source-001 34c3dd64 MATCH, source-002-amendment 4eea66c6 MATCH (amendment reflected; R011/R012 present); D-066 source-001 LF 4cb05c94 MATCH (CRLF file, LF-normalized). Cited requirement texts present, binding, classified, with both task_ids in applicability. No missing/weakened/combined/invented in either cited set.

HARNESS: validate_directive_compliance.py --check launched ONCE (background, grown-registry ~12min wall); still running at send — exact exit code to follow in a one-line addendum on completion. It does not change these per-requirement verdicts (registry integrity already corroborated above by direct digest match; the authoritative one-per-seam full validator + a green control-plane CI at the accept head remain the orchestrator's to record at acceptance). I did NOT run test_directive_compliance.py (prohibited).

RESTAMP PRE-AUTH (restated, blob-level): verdicts hold at target 464dda21 (verified byte-stable) and any future SHA whose tree carries the six blobs — T091: pdf_sheet_writer.py 86b129c9 / test 52f37aa9 / report 3b402b53; T092: glb_writer.py 64568629 / test 9166d160 / report 8f390845. Broad disjoint-peer tolerance (ledger/state/gate/verification bookkeeping + other tasks' material). Orchestrator authorized to restamp reviewed_sha to accept-HEAD and add MY verification rows while those six blobs are byte-identical. Void for a task only if one of its blobs differs.

Every cited requirement judged individually on reproduced primary evidence (source lines, deterministic tests, gate records, git objects, registry). No VIOLATED, BLOCKED, or UNVERIFIABLE. Advisories are wiring-packet riders/housekeeping only — none blocks completion. Producer (backend-engineer) ≠ verifier; every required gate PASS with an independent reviewer.

M5-T091 DCV VERDICT: PASS 5/5
M5-T092 DCV VERDICT: PASS 6/6

END-OF-REPORT

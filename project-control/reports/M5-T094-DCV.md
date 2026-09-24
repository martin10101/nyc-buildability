# M5-T094 — directive-compliance verification (directive-compliance-verifier "dcv-t094", read-only)

> Transmission history: pinned at 49dcdbd2 (HEAD advanced through disjoint orchestrator commits; the five reviewed blobs
> and identity df266133 were reproduced), delivered as four SendMessage parts (1/4..4/4) ending with END-OF-REPORT; no
> truncation. Part 1 carries the blob-level restamp predicate with broad disjoint-peer tolerance. Joined verbatim by the
> orchestrator (transport wrapper tags removed only). F2: the local validator exceeded 15 min and was backgrounded; harness
> evidence = CI run 36053257566 (18/18 incl. control-plane) + hand-reproduced LF-normalized digests. Findings F1-F3 are info.

---

PART 1/4 - M5-T094 DCV (directive-compliance-verifier), D-087 PDF-1c architect-sheet reader split.

PINNED HEAD: 49dcdbd2 at start; advanced to c4d27e1e during review (peer commit c4d27e1e "seq 129 wave 3" records OTHER tasks' gates; touches 0 M5-T094 allowed paths). Content identity stable at df266133 across it.

RESTAMP PRE-AUTHORIZATION (blob-level predicate). I authorize restamping my verification rows to any HEAD H' for which BOTH hold:
(1) these 5 blobs are byte-identical at H':
- project-control/reports/M5-T094-producer-report.md = ce2eaecf65dcf3aeff80cdfd4efe42c079c694db
- services/api/app/drawings/sheet_interpreter.py = e71266bff56346dd540568b32cf3e0e512967d82
- services/api/app/drawings/sheet_objects.py = 1f69f5582beb8798eb1fe73e09bf492ce8b0a289
- services/api/app/drawings/sheet_reader.py = e3606e0f5e80395fc6f28998d46474ecb4b78f2d
- services/api/tests/drawings/test_sheet_reader_split_equivalence.py = fba20c0a00309e24b302b1e839fd217ddf5bdf3b
(2) _task_git_identity(dr, M5-T094) at H' == df266133cf8597decc00e603e7418d7b6f578f2e69c22cd352ca37a65a78e01c.

DISJOINT-PEER TOLERANCE (broad). The predicate holds regardless of, and I explicitly tolerate at H', any of: other tasks' files/gates/material commits; other directives' registry binds and digest resyncs; the orchestrator appending MY verification rows to D-087 and D-066 verification.json with the matching directive_registry digest resyncs and audit_log entries; docs/DISCOVERY_BACKLOG.md rows and contract-seam sweep lines; and lifecycle-only changes to the M5-T094 packet (status/progress/gate stamps) that leave the 5 blobs and df266133 intact. None of these moves the reviewed content identity.

---

PART 2/4 - Requirement rows (primary evidence I reproduced myself).

APPLICABILITY (authoritative): directive_registry.load_registry().evaluate_task_refs(M5-T094) -> ok=True; applicable_ids == cited_ids == [D-066-R001, D-087-R001, D-087-R002, D-087-R005, D-087-R009]; missing=[], invalid=[], unresolved=[], reasons=[]. No missing binding, no selective/invented citation. Cross-checked against requirements.json applicability.task_ids: no other D-087 requirement lists M5-T094.

D-087-R001 (use today's capacity; obligation) - SATISFIED. tasks/M5-T094.json: G0 contract seam 5cb3ca94 (gates/M5-T094-G0.json reviewed_sha), claimed at the wave-4 seam (progress_log[0]) with the FULL worktree path C:\...\wt-m5t094; produced by an orchestrator-dispatched subagent (producer_agent=backend-engineer); producer commit 25879734 (parent a749d995) cherry-picked to 89128c62. Every state present (G0 -> claim -> submit -> G2 -> G3/G4/G5); no state or gate skipped. Note: B-026 (open) affects "D-087-R001 (loop-lane share)" but names task M0-T132, NOT M5-T094 (word-bounded grep of blockers/ for M5-T094 = empty), and B-026's own workaround explicitly authorizes this subagent-producer path; not blocking for M5-T094.

D-087-R002 (no interference; prohibition) - SATISFIED. reports/M5-T094-G0.md disjointness table: EMPTY overlap vs all 24 active tasks. One isolated worktree wt-m5t094 (tasks/M5-T094.json:99). git diff --name-status 89128c62^..89128c62 = exactly the 5 allowed paths (all M). No shared writable file with any live or frozen packet; git log 89128c62..HEAD on the 4 code files = EMPTY (no later overlap).

---

PART 3/4 - Requirement rows (continued).

D-087-R005 (PDF reading released; C-track honesty binds) - SATISFIED. Behaviour-preserving split preparing C1; claims NO new reading capability. Primary evidence: (a) two independent reviewers (G3 cr-t094, G4 qa-t094) each reconstructed the PRE-split monolith from 89128c62^ (=eccca03e; sheet_reader.py 1096-line monolith, the two new modules only seeded placeholders blob 3a724a09) and reproduced ALL 62 pinned golden per-case digests + overall 767766eb exactly -> post==pre byte-identical across curves/CTM/q-Q/forms(cycle,depth,memo)/images/text/every refusal class/every budget; (b) M5-T093 (accepted) producer-report: "read_sheet reads none of the six real corpus files ... cross-reference streams block 6/6 real files" - a byte-identical split cannot change this. No honesty rule weakened; unwired, so no route is reached.

D-087-R009 (unchanged boundaries; prohibition) - SATISFIED. Imports in all 3 modules are stdlib (zlib/math/dataclasses/typing) + in-repo app.* only - zero third-party deps (grep ^(import|from)); requirements.txt/.in byte-untouched (git diff 89128c62^..HEAD empty). Not wired: no importer of the 3 modules outside app/drawings (grep of services/api/app), main.py 0 sheet refs, __init__.py untouched. Max-envelope route stays UNMOUNTED (main.py include_router list has no max_envelope). sheet_primitives.py + app/documents byte-untouched (git diff 89128c62^..HEAD empty). PR #241 OPEN/unmerged. No lockfile change.

D-066-R001 (code-graph navigation block; obligation) - SATISFIED. tasks/M5-T094.json inputs[7]: a graph-derived block ("graph REGENERATED at this contract seam, 821 files / 17652 nodes / 7589 edges") naming the key consumer fact (sheet_reader.py has no production importer, only its test), the forbidden neighbours (app/documents/extraction, sheet_primitives.py) and the instruction to run `query.py --no-regen impact <path>` before sweeps, marked ADVISORY. Reviewers verified conclusions in actual source.

---

PART 4/4 - Frozen identity, gates, harness, sweep, findings, verdict.

FROZEN IDENTITY: _task_git_identity(dr, M5-T094) at HEAD == df266133cf8597decc00e603e7418d7b6f578f2e69c22cd352ca37a65a78e01c (err=None) == reports/M5-T094.json content_manifest_sha256 == the G2/G3/G4/G5 stamps. G0 carries the contract-seam identity 383e59ea at 5cb3ca94 (expected). Cherry-pick blob-identical: all 5 blobs at 89128c62 == at wt commit 25879734 == the G2 record. Working tree clean for task paths.

GATES (gates/M5-T094-*.json): G0 PASS (orchestrator/administrative, 5cb3ca94), G2 PASS (orchestrator/self_check, 89128c62), G3 PASS (code-reviewer), G4 PASS (qa-engineer), G5 PASS (security-reviewer) - the 3 independent stamps all df266133; none is the producer backend-engineer. Two reviewers independently reproduced the pre-split golden (AS-2 non-vacuous).

HARNESS: CI at origin head 83f86ce0 (contains pushed material 89128c62) run 36053257566 = success, all 18 jobs green incl. control-plane (ADR-005), api (ruff+pytest), modularity; a612652b likewise green. Local validate_directive_compliance.py --check exceeded 15 min and was backgrounded (F2); I instead reproduced the LF-normalized source digests by hand: D-087 source-001 34c3dd64, source-002-amendment 4eea66c6, D-066 source-001 4cb05c94 - all == manifest content_digest_sha256; both amendments reflected; locked_requirement_ids complete (D-087 R001-R012, D-066 R001-R004).

PROHIBITED-ACTION SWEEP: not accepted (status awaiting_gate); no M5-T094 row in D-087 or D-066 verification.json (grep count 0); not on main (89128c62 not ancestor of origin/main); PR #241 untouched (OPEN, updated 2026-08-20); no open blocker names M5-T094 (B-026 confirmed - names M0-T132 + D-087-R001, not M5-T094).

FINDINGS:
- F1 (info): HEAD advanced 49dcdbd2 -> c4d27e1e via a disjoint peer commit; identity stable - covered by the predicate.
- F2 (method, not a defect): local validator backgrounded >15 min (known slow-registry behavior); harness evidence taken from the green CI control-plane job + hand digest reproduction per DCV guidance. Background run may still land; a transient c14 from straddling is pre-resolved by the hand digest match above.
- F3 (info): all reviewer advisories non-blocking / inherited / pre-existing (G3 A1-A3; G4 A-1/A-2; G5 A1/A2) -> route to DISCOVERY_BACKLOG at the accept seam.

No VIOLATED, no UNVERIFIABLE.

M5-T094 DCV VERDICT: PASS 5/5
END-OF-REPORT

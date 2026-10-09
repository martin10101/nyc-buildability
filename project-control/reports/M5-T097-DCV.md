# M5-T097 — directive-compliance verification (directive-compliance-verifier "dcv-t097", read-only)

> Transmission history: pinned at 75e75e55, settled at 2aeeafc5 (four disjoint orchestrator commits; the four reviewed blobs
> and identity 88431c2d byte-stable), delivered as five SendMessage parts (1/5..5/5) ending with END-OF-REPORT; no
> truncation. Part 1 carries the blob-level restamp predicate with broad disjoint-peer tolerance. Joined verbatim by the
> orchestrator (transport wrapper tags removed only). The local validator exceeded its budget; digests hand-verified MATCH
> and CI (851c4e63, contains e04c2b5b) green incl. api on Linux 3.12 and control-plane. F1-F3 are non-blocking.

---

M5-T097 DCV report (part 1/5): verdict PASS 6/6; restamp predicate up front.

PINNED at start: HEAD 75e75e55 (280 accepted). NOTE: the shared branch advanced during review to live HEAD 2aeeafc5 (282 accepted) via 4 DISJOINT peer commits (M5-T096 accept #281, M5-T101/T102 contract+claim, M5-T095 accept #282); the path-scoped diff for M5-T097's 4 allowed paths across 75e75e55..2aeeafc5 is EMPTY and e04c2b5b is an ancestor of 2aeeafc5. Every check below was re-confirmed at live HEAD.

RESTAMP PRE-AUTHORIZATION — blob-level predicate. M5-T097 stays verified PASS at any live HEAD where these 4 reviewed blobs equal e04c2b5b and the identity holds:
- services/api/app/drawings/dxf_reader.py = 94895927
- services/api/tests/drawings/test_dxf_reader.py = 78b4a278
- services/api/tests/drawings/test_dxf_roundtrip.py = f301eed4
- project-control/reports/M5-T097-producer-report.md = e6816ad0
identity _task_git_identity = 88431c2d5bd5fe8db88e987e1831f2dd3edd82ca1652a5a1528be329f8eb5a08; evaluate_task_refs ok, applicable == cited {D-066-R001, D-087-R001/R002/R006/R007/R009}.

DISJOINT-PEER TOLERANCE (broad): the PASS stands across any peer commits that do NOT modify those 4 blobs — other tasks' files/gates/material and new contract seams for other packets; other directives' registry binds; the orchestrator appending my M5-T097 verification rows to the D-087 and D-066 verification.json with the matching requirements-digest resyncs + audit entries; DISCOVERY_BACKLOG rows/sweeps; and lifecycle-only packet changes (status/progress, gate reviewed_sha restamps). Assemble the v2 rows with reviewed_sha = the live HEAD at accept time, reviewed_manifest_sha256 = 88431c2d (from the gate records), and accept back-to-back.
(continued 2/5)

---

M5-T097 DCV (part 2/5): requirement rows R001/R002/R006 — SATISFIED.

D-087-R001 (obligation; today's capacity via the normal gated process) SATISFIED. It is a contracted, claimed, fully-gated ledger packet: G0 at contract seam 64fce622 ("D-087 wave-5 contract seam: M5-T096/T097/T098 + M0-T160"), claimed at 2e0b2351 (progress 20, full worktree path), run concurrently in wave-5; all 5 required gates recorded, no state or gate skipped. R001.applicability.task_ids includes M5-T097; evaluate_task_refs ok at live HEAD.

D-087-R002 (prohibition; no interference / pairwise-disjoint + worktree isolation) SATISFIED. G0 report (reports/M5-T097-G0.md) disjointness table shows every active task "EMPTY overlap"; one isolated worktree wt-m5t097 (packet.worktree matches the G2 claim-seam record). Both producer commits touch ONLY the 4 allowed paths (git show --stat: 9a281517 = 4 files; e04c2b5b = 3 files, round-trip test unchanged in round 2). Forbidden neighbor app/cad/dxf_writer.py (owned by M5-T096) is untouched.

D-087-R006 (CAD read/write via open formats; DXF in-path + the missing round-trip harness) SATISFIED, judged on the source I read at HEAD. Reader services/api/app/drawings/dxf_reader.py: single-pass re.compile(r"\r\n|\r|\n") splitter (L540/571), streaming max_lines/max_line_chars enforced before the full list (L579-584), clamp-DOWN hard ceilings in DxfLimits.__post_init__ (L214-221), str-path binary-sentinel+isascii (L515-527), INSUNITS 22/23/24 = us_survey_inches/yards/miles (L159-161), math.isfinite refusal (L336), non-zero bulge refused on LWPOLYLINE (L406) and VERTEX (L482), closed-flag &1 mask (L369; 128->open, 129->closed). Round trip tests/drawings/test_dxf_roundtrip.py imports the accepted writer READ-ONLY and asserts lot+building rings exact & closed (lot.vertices==_LOT), units 21/us_survey_feet/header source, AC1009, layer names, per-type entity counts, honesty texts; TABLES skipped-not-pinned; the mutation moves ONE vertex and asserts only it changed (L168-171). CI api (ruff+pytest) GREEN at 851c4e63 on Linux 3.12; writer blob 6f57cdc4 byte-stable to live HEAD.
(continued 3/5)

---

M5-T097 DCV (part 3/5): R007, R009, D-066-R001 — SATISFIED.

D-087-R007 (hold; no native DWG library / no license decision) SATISFIED. dxf_reader.py imports are stdlib only (enum, math, re, collections.abc.Iterator, dataclasses — L71-75); the module docstring records that the DWG path stays an owner decision (D-087-R007, L5-6). No DWG library import anywhere; no lockfile touched (requirements.txt/.in are forbidden_paths; --stat shows only the 4 allowed files). G5 (security-reviewer) independently confirmed "no DWG library, no new import."

D-087-R009 (unchanged boundaries) SATISFIED. Zero new dependencies (stdlib only; no lockfile change). Unwired: grep of services/api/app, apps/, packages/ for dxf_reader/read_dxf returns ONLY self-references inside dxf_reader.py — no production importer. No route/main.py/web change (allowed_paths = 4 files; app/api/, app/main.py, apps/, packages/ are forbidden_paths; --stat confirms only 4 files), so this packet does not mount the max-envelope route. PR #241: gh pr view 241 -> state OPEN, mergedAt null, title "DO NOT MERGE". e04c2b5b is not on main. All gates enforced; modularity + control-plane CI green at 851c4e63.

D-066-R001 (obligation; code-graph navigation block present in the packet) SATISFIED. tasks/M5-T097.json inputs carry the "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph regenerated, 825 files / 17656 nodes / 7589 edges)" naming consumers (dxf_reader.py has no production importer, only its test), forbidden neighbors (app/cad/dxf_writer.py read-only, owned by M5-T096; sheet_* owned by M5-T094), and the `query.py --no-regen impact` instruction. D-066-R001.applicability.task_ids includes M5-T097 (obligation, 68 ids). I reproduced its factual claims myself: grep found no production importer, and test_dxf_roundtrip.py imports the writer read-only (import only).
(continued 4/5)

---

M5-T097 DCV (part 4/5): frozen identity, gates, prohibited-action sweep, digests, harness.

FROZEN IDENTITY: I directly reproduced _task_git_identity(dr, task) at live HEAD = 88431c2d…5a08 (error None) == reports/M5-T097.json content_manifest_sha256 == the CURRENT G2/G3/G4/G5 stamps (all 88431c2d). The 4 allowed-path blobs are byte-identical at e04c2b5b and at live HEAD 2aeeafc5. First-round stamps sit in each gate record's history.

GATES — all required PASS, independent reviewers, none the producer (backend-engineer):
- G0 orchestrator/administrative PASS (64fce622)
- G2 orchestrator/self_check PASS
- G3 code-reviewer PASS (round-1 FAIL B1)
- G4 qa-engineer PASS (round-1 PASS, ADVISORY-1 folded in)
- G5 security-reviewer PASS (round-1 FAIL Finding 1)
Genuine FAIL->rework->delta cycle: G3 and G5 INDEPENDENTLY found the same O(n^2) double-find splitter DoS; round-2 e04c2b5b replaced it with the single-pass regex; the SAME reviewers delta-re-reviewed and PASSED (reports M5-T097-G3/G4/G5-rework.md). Not a skipped gate.

PROHIBITED-ACTION SWEEP (clean): status = awaiting_gate (not accepted); 0 rows with task_id==M5-T097 in D-087 and D-066 task_verifications; e04c2b5b not on main; PR #241 OPEN/unmerged; no open blocker file names M5-T097.

DIGESTS (hand-verified at live HEAD via dr.sha256_text_artifact): requirements.json = 91e98339… == manifest (resynced in the wave-7 rebind; the ca5ba8eb I first read was the pre-rebind value); source-001 = 34c3dd64…; source-002 = 4eea66c6…; all MATCH. Amendment source-002 reflected (R011/R012 present; audit_log "amended" entry). The requirements.json diff across the rebind is additive only (M5-T101/T102 into other requirements' applicability) — no requirement TEXT changed and M5-T097's bindings are intact.

HARNESS: CI at 851c4e63 (contains e04c2b5b) — api (ruff+pytest) success on Linux 3.12, control-plane (ADR-005 workflow regression) success, modularity success, all jobs green.
(continued 5/5)

---

M5-T097 DCV (part 5/5): findings + verdict.

FINDINGS — no blocking findings.
F1 (informational): the review ran on a live-moving branch (HEAD 75e75e55 -> 2aeeafc5, +4 disjoint peer commits). M5-T097's 4 blobs and identity 88431c2d are byte-stable throughout; covered by the part-1 predicate. Not a defect.
F2 (informational): the local `validate_directive_compliance.py --check` run exceeded the ~12-min budget and did not return; per the DCV protocol I stopped relying on it and hand-verified all committed digests via the registry's own sha256_text_artifact (all MATCH) plus the green control-plane CI job at 851c4e63. Not a defect.
F3 (advisory, non-blocking, correctly deferred by the reviewers): G5 A1-A4 (output control-char sanitization, bounded refusal-detail reflection, group-code digit cap, bytes-only input) and the import-route off-thread-timeout residual belong to the later wiring packet; dxf_reader.py sits in the modularity WARN band (~603 SLOC; <750 justify, <1000 hard) with DISC-1 routing a future lexer/model split. None block this tested-module-only packet.

All 6 applicable requirements SATISFIED on primary evidence I reproduced myself (source files, deterministic tests, git objects, control-plane records, CI). No VIOLATED or UNVERIFIABLE result.

M5-T097 DCV VERDICT: PASS 6/6

END-OF-REPORT

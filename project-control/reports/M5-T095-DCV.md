# M5-T095 — directive-compliance verification (directive-compliance-verifier "dcv-t095", read-only)

> Transmission history: pinned at 481e51ff (HEAD advanced through disjoint orchestrator commits; the three reviewed blobs
> and identity d51ff82d were reproduced), delivered as five SendMessage parts (1/5..5/5) ending with END-OF-REPORT, plus a
> one-line CLARIFICATION requested by the orchestrator because part 5's verdict line still carried the template's '| FAIL'
> alternative; the clarification is appended last. Joined verbatim (transport wrapper tags removed only). Validator EXIT 0
> (one run, straddled commits; digests hand-verified MATCH). Findings F1-F3 are non-blocking.

---

M5-T095 DCV PART 1/5: restamp pre-authorization (UP FRONT) + frozen identity d51ff82d + all 5 gates PASS.

PINNED start HEAD 481e51ff; HEAD advanced during my read-only review to e04c2b5b → 851c4e63 → 75e75e55 (active accept window: M5-T094 #278 + M5-T099 #279 accepts, M5-T097 rework, wave-6/7 seams). No writes performed.

RESTAMP PRE-AUTHORIZATION — blob-level predicate. This PASS holds at any accept HEAD where M5-T095's three reviewed blobs are byte-unchanged:
- services/api/app/scenario/proposal.py = d00b1728f1592c62ce0458eac81c552d67b5c5fe
- services/api/tests/scenario/test_proposal_validation_budget.py = e25d19bb4c1f455e748dfebddcab01502769842e
- project-control/reports/M5-T095-producer-report.md = eeb81b3a28cbf61dd9149b36bdcb0552315a6d05
Equivalently: _task_git_identity(HEAD) == d51ff82d96bbdc6ffd7907911d32059e187b002e6ca38bf6c4d51177545e4827.

Broad disjoint-peer tolerance (all pre-authorized, NO re-review needed): other tasks' files/gates/material; other directives' registry binds; the orchestrator adding my M5-T095 verification rows to D-066/D-076/D-087 verification.json with matching digest resyncs + audit_log entries; DISCOVERY_BACKLOG rows + sweep lines; lifecycle-only packet changes (status/progress/updated_at). Verified empirically: identity stayed d51ff82d across 481e51ff → e04c2b5b → 851c4e63 (peer commits touched none of the 3 blobs).

FROZEN IDENTITY — CONFIRMED. Independently computed _task_git_identity == d51ff82d == reports/M5-T095.json content_manifest_sha256 == the G2/G3/G4/G5 gate stamps (all d51ff82d). G0 stamp 7860d579 @ 5cb3ca94 is the pre-material contract-seam administrative gate (expected, not the material identity). Material a2dcc60f = cherry-pick of wt-m5t095 3be80a1d; `git diff --name-only a2dcc60f^..a2dcc60f` = exactly the 3 allowed paths, zero forbidden paths.

GATES — all PASS; reviewers ≠ producer (backend-engineer):
- G0 orchestrator/administrative PASS (5cb3ca94)
- G2 orchestrator/self_check PASS (d51ff82d)
- G3 code-reviewer PASS — advisories A1–A5 non-blocking; independent 520k adversarial probe @EPSG:2263 magnitudes, 0 disagreements
- G4 qa-engineer PASS — 8/10 mutants caught, 2 proven EQUIVALENT via independent 120k–320k divergence searches
- G5 security-reviewer PASS — M5-T088 F-HIGH-1 verified CLOSED (worst request <=119ms, was ~597s), independent 30k fuzz 0 disagreements; F-LOW-1/2 non-blocking

Continues 2/5.

---

M5-T095 DCV PART 2/5: requirements D-087-R001, R002, R003 — all SATISFIED on reproduced primary evidence.

Applicability reproduced independently: registry.evaluate_task_refs(task) → ok=true, applicable_ids == cited_ids == {D-066-R001, D-076-R002, D-087-R001, D-087-R002, D-087-R003, D-087-R009}, missing=[], invalid=[]. All 3 directives load active, errors=[]. No selective citation.

D-087-R001 (obligation — capacity via contracted/claimed/gated packets, no state or gate skipped) — SATISFIED. Primary: gates/M5-T095-{G0,G2,G3,G4,G5}.json all PASS; full lifecycle present with no skip (G0@5cb3ca94 → claim@a749d995 full worktree path → progress → submit@a2dcc60f → G2/G3/G4/G5). Orchestrator-dispatched subagent producer backend-engineer; a normal gated ledger unit run concurrently. Capacity added by a disjoint packet, not by skipping a state/gate.

D-087-R002 (prohibition — no interference; pairwise-disjoint allowed_paths, isolated worktree, G0 overlap recorded) — SATISFIED. Primary: task.worktree = C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t095 (single isolated worktree); allowed_paths = exactly 3 files; reports/M5-T095-G0.md disjointness table shows "none — EMPTY overlap" for EVERY active neighbor (checked vs all state.json active_tasks, DB-057(p)); material a2dcc60f touches exactly the 3 allowed paths, zero forbidden. Peer commits during review (git diff 481e51ff..HEAD) touched none of the 3 blobs — no live interference.

D-087-R003 (authorization — 3D released; deterministic, fail-closed geometry) — SATISFIED. Primary (proposal.py @ blob d00b1728):
- Request-level MAX_TOTAL_OUTLINE_POSITIONS=20000 (line 89) charged in _check_total_positions (481–504), called in validate_proposed_massing at line 518 BEFORE _validate_outline at 520 — an oversized request is refused with typed ProposedMassingError(field="proposed_massing") before any geometry (G4 spy: zero simplicity calls; boundary 20000 passes / 20001 refuses).
- _ring_is_simple (153–190) keeps O(n) cond1 zero-length (180–181) + cond2 reversal-spike (182–187) byte-identical; delegates cond3 to _ring_boundary_is_simple (129–150) using shapely Polygon.is_valid (GEOS ~O(n log n)), replacing the O(n^2) all-pairs scan.
- Fail-closed: except (GEOSException, ValueError) → False (149–150) → typed "self-intersecting" refusal (286–291); never escapes untyped. Deterministic; 597s→53–87ms (producer) / <=119ms (G5). Closes the M5-T088 wiring precondition.

Continues 3/5.

---

M5-T095 DCV PART 3/5: requirements D-087-R009, D-076-R002, D-066-R001 — all SATISFIED.

D-087-R009 (prohibition — unchanged boundaries) — SATISFIED. Primary:
- Zero new deps: shapely==2.0.7 already admitted (requirements.in:51, requirements.txt:508); a2dcc60f touches NO requirements file (git diff confirms).
- No route/main.py/web change: diff = 3 files only; app/main.py untouched; the max-envelope router is NOT in main.py's include_router list — the max-envelope route stays UNMOUNTED.
- Route-level defence NOT claimed closed: producer report DISCOVERY #2 keeps the cancellable-job + per-request wall-clock timeout + rate limit (M5-T088 G5 fix (b) / DB-034(a) / DB-061(i)) OPEN as an exposure precondition; the G5 report independently confirms it is "correctly recorded, NOT claimed closed."
- D-051 fail-closed preserved (fail-closed to "not simple" → typed refusal); all gates ran; PR #241 never merged (sweep in part 4).

D-076-R002 (obligation — honesty; measurement/rule through deterministic code) — SATISFIED. Primary:
- validate_proposed_massing docstring (proposal.py:510): "Performs NO derivation and computes NO allowance (D-076-R002)" — a pure deterministic validator; every rule/measurement comparison runs through tested code; nothing labelled a city record/approval.
- Refusals stay typed (ProposedMassingError, field-named).
- Decision identity proven and independently reproduced: producer 360k probe + committed 24,159-ring corpus (0 disagreements, both True/False exercised) + G3 independent 520k probe + G5 independent 30k fuzz — all 0 disagreements. Public surface unchanged (only MAX_TOTAL_OUTLINE_POSITIONS added to __all__).

D-066-R001 (obligation — code-graph navigation block in the packet) — SATISFIED. Primary: task.inputs carries the "CODE-GRAPH NAVIGATION BLOCK (D-066-R001; graph REGENERATED at this contract seam, 821 files / 17652 nodes / 7589 edges)" naming every proposal.py consumer (proposal_validation, proposal_checks_api, max_envelope_api, contract, derivation, massing_model, max_envelope, proposal_input_gate) as FORBIDDEN, plus the `query.py --no-regen impact` instruction and the "graph advisory — verify in source" clause. reports/M5-T095-G0.md §"Code graph regenerated at this seam" corroborates. Producer verified in source (removed helpers confirmed unused; derivation.py keeps its own copies).

Continues 4/5.

---

M5-T095 DCV PART 4/5: prohibited-action sweep clean + harness evidence (validator exit 0).

PROHIBITED-ACTION SWEEP — all clean:
- NOT accepted: task.status = awaiting_gate (progress 95); state.json accepted_tasks does NOT contain M5-T095 (accepted count 279).
- NO verification row: task_verifications in D-087, D-076, D-066 verification.json carry no M5-T095 entry (re-checked at 481e51ff and at the post-peer HEAD). The single "M5-T095" string in D-087 verification.json is a FORWARD-REFERENCE inside M5-T088's evidence ("F-HIGH-1 (upstream proposal.py) ... QUEUED as M5-T095"), not a verification row.
- NOT on main: `git merge-base --is-ancestor a2dcc60f main` = false; a2dcc60f lives on candidate/D-024-mrl-option-b (+ two peer task branches), not main.
- PR #241 untouched: gh → state OPEN, mergedAt null, headRefName task/M5-T002-scenario-endpoint, headRefOid 4174a3b2, updatedAt 2026-08-20 (pre-dates this task); unrelated to a2dcc60f.
- NO open blocker names M5-T095 (grep project-control/blockers/ empty).
- Nothing deployed/installed/purchased/dispatched-to-prod: pure offline validator change, zero new deps, no requirements/lockfile change.

HARNESS EVIDENCE:
- validate_directive_compliance.py --check: run ONCE (backgrounded), DIRECT exit code = 0 (PASS). It straddled commits (HEAD_BEFORE=59737e43 → HEAD_AFTER=75e75e55, active accept window) yet exited 0 with no c14/integrity error emitted.
- BY-HAND c14 cross-check (sha256_text_artifact vs manifest, per your straddle instruction): D-087 source-001.md MATCH + source-002-amendment.md MATCH (amendment reflected); D-076 source-001.md MATCH; D-066 source-001.md MATCH. All 3 directives load with errors=[] (loader validates source digests + locked_requirement_ids). c14 holds at the committed HEAD.
- CI control-plane job GREEN at a verified pushed head: run 36056296954, workflow "CI", conclusion success, headSha 481e51ff (secret-scan + context-budget runs also success).
- test_project_control.py + test_directive_reminder.py: local runs exceeded the ~15-min budget and were backgrounded; covered by the green CI control-plane run above. NOT blocking. (test_directive_compliance.py deliberately NOT run — 16h prohibition honored.)

Continues 5/5.

---

M5-T095 DCV PART 5/5: findings + VERDICT PASS 6/6.

FINDINGS (all non-blocking):
- F1 (informational): my single validator run straddled the active accept window (59737e43 → 75e75e55); it still exited 0, and I corroborated with the by-hand digest check (all MATCH) + green CI control-plane run at 481e51ff. Not a defect.
- F2 (clarifying): the lone "M5-T095" hit in D-087 verification.json is M5-T088's forward-reference, not a premature verification row — the sweep stays clean.
- F3 (non-blocking, already routed by the gates): G3-A1 notes a stale docstring at forbidden-path proposal_input_gate.py:18 and that total-count logic is now triplicated (proposal.py + proposal_input_gate + derivation); G4 notes cond2 (reversal spike) is redundant behind GEOS validity; G5 F-LOW-1 (add an O(1) level-count ceiling before the walk) and F-LOW-2 (broaden the catch to shapely.errors.ShapelyError). All are forbidden-path or defence-in-depth items, correctly routed to follow-up DISCOVERIES; none reintroduces F-HIGH-1.

Basis: every applicable requirement was judged on PRIMARY evidence I reproduced myself (source blobs, gate JSON records, the directive registry, git objects, the validator exit code) — not the producer's compliance matrix or self-attestation. All 6 requirements SATISFIED. Frozen identity d51ff82d confirmed at three HEADs and equal to the frozen manifest and every material gate stamp. All required gates (G0,G2,G3,G4,G5) PASS with independent reviewers ≠ producer, and every advisory is non-blocking. Prohibited-action sweep clean. No VIOLATED, no UNVERIFIABLE, no BLOCKED requirement.

Requirement tally: D-087-R001 SATISFIED, D-087-R002 SATISFIED, D-087-R003 SATISFIED, D-087-R009 SATISFIED, D-076-R002 SATISFIED, D-066-R001 SATISFIED.

M5-T095 DCV VERDICT: PASS 6/6 | FAIL

END-OF-REPORT

---

M5-T095 DCV VERDICT: PASS 6/6

Restamp predicate CONFIRMED holding at current HEAD 442b2dd2: the three reviewed blobs are byte-unchanged — services/api/app/scenario/proposal.py = d00b1728, services/api/tests/scenario/test_proposal_validation_budget.py = e25d19bb, project-control/reports/M5-T095-producer-report.md = eeb81b3a (equivalently _task_git_identity == d51ff82d). The "| FAIL" in my prior line was leftover template text; the sole ruling is PASS 6/6.

END-OF-REPORT

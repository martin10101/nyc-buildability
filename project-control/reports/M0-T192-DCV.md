# M0-T192 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `5df3f09f504b2bac659d1f79beec4a953e9bde83` (branch `task/wave23-density-zoning-lot`, review copy `git plumbing at the frozen head`). Directives D-093. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R075.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. All review findings are low/advisory and non-blocking: G3 A1 (professional_review.date still validated only as a non-empty string — conforms to packet scope), G3 A3 (fractional-seconds regex, immaterial on Python 3.11+), G5 F1 (out-of-range calendar values recovered fail-closed by fromisoformat), G5 F2 (disjoint M5-T158 peer commits in the review range, correctly excluded). The single G4 advisory (non-Z offset unpinned) was closed by the added offset test at c9e292a7 and re-confirmed by G4/G5 delta PASS.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-11 08:17 UTC, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M0-T192 (directive D-093, 1 row)
VERDICT: PASS

I am an AI agent (directive-compliance-verifier). This is an automated, read-only reproduction of primary evidence — NOT a human or professional review. I produced none of this work. I read everything via git plumbing at the frozen head, ran only the two permitted stdlib commands, and recomputed digests myself.

(1) HEAD VERIFIED
 - `git -C /root/project/w-wave20 rev-parse HEAD` == 5df3f09f504b2bac659d1f79beec4a953e9bde83 on branch task/wave23-density-zoning-lot; `git cat-file -t` confirms the object.
 - Working tree clean (`git status --short` empty); working-tree blobs of tools/research_record_check.py (2fbd970c) and tools/test_research_record_check.py (d4002a7e) equal the frozen-head blobs, so local runs reflect the frozen content.

(2) ROWS
ROW D-093-R075 — PASS
 - Governing-review selection is date-format-independent: at the frozen head `derive()` picks `max(enumerate(reviews), key=_review_sort_key)`, and `_review_sort_key` returns `(reviewed_revision, parsed-UTC-timestamp, index)` with `_parse_review_instant` mapping a date-only "YYYY-MM-DD" to 00:00 UTC — so the highest revision governs, ties by parsed time then list order, and a same-day date-only entry can never make a newer review read older (research_record_check.py blob 2fbd970c, lines 95-119, 513-534).
 - Malformed review dates are refused: `_validate_review` emits a structural error when `_parse_review_instant` is None, and `REVIEW_DATE_RE = ^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d+)?)?Z)?$` admits only a date or a UTC ...Z date-time (lines 90, 451-453); a non-Z offset (even +00:00) and a space separator are refused — a stricter-than-literal but non-weakening reading, matched by packet S3 and the tests.
 - Harness reproduced by me at the frozen head: `python3 tools/research_record_check.py --check` → exit 0, PASS, all six records NB-01..NB-06 read review_state=current; `python3 tools/test_research_record_check.py` → "Ran 38 tests ... OK" exit 0, including `test_nb01_case_date_only_higher_revision_governs` (timed rev-2 + date-only rev-3 reads current — the NB-01 shape R075 names) and the GoverningReview(4)/MalformedReviewDate(5) cases; G3/G4 reproduced the red/green mutation proving the test is load-bearing.
 - Stays open for later work: backlog DB-238 is still WATCH at the frozen head (docs/DISCOVERY_BACKLOG.md line 368) — its update is an orchestrator step at the merge seam, and the "control-plane CI job passes" clause is evidence at the wave's PR head; both are post-this-head/merge items outside this task's diff, so they stay open and are not this task's share to close.

(3) BINDING B1–B5
 - B1 PASS: R075 was captured at commit be410508 with applicability.task_ids=['D-093-BOOTSTRAP'] and body sha ace14f48bc036c3d; at contract commit 0b748681 the task_ids became ['D-093-BOOTSTRAP','M0-T192'] with the body sha unchanged (ace14f48...); frozen head identical. No row text changed on binding.
 - B2 PASS: I recomputed `dr.sha256_text_artifact(requirements.json)` = d6c314ee... == manifest.requirements_content_digest_sha256; sorted-id sha256 = a9156a61... == manifest.requirements_id_digest_sha256; all three source digests MATCH (source-001 f0cb7376, source-002 d5cd38ee, source-003-amendment a215a417). 75 requirements, last id D-093-R075. source-003-amendment.md carries the owner's verbatim "I logged it why cant u fix it permanently?" mapped to R075.
 - B3 PASS: verification.json has exactly one M0-T192 task row: applicable_requirement_ids=['D-093-R075'], verifier="" (empty), requirements[0] = R075 state "pending", reviewed_sha null (producer field "backend-engineer", the material producer).
 - B4 PASS: `reg.load().evaluate_task_refs(M0-T192.json)` → ok=true, applicable_ids=['D-093-R075'], cited_ids=['D-093-R075'], missing_ids=[], invalid_refs=[], unresolved=[]; applicable == cited.
 - B5 PASS: the registry loaded all 92 directives and `derive_applicable` across the full set yields only D-093-R075 with missing_ids=[] — nothing else applies to this task uncited. Gates: G0 PASS @ contract 0b748681 (orchestrator); G2 PASS (orchestrator self-check), G3 PASS (code-reviewer), G4 PASS (qa-engineer), G5 PASS (security-reviewer) all recorded @ submit head 033775776d23a6bd68a1087c86cb240164a1fd2a — one content identity. The allowed-path blobs at that submit head equal the frozen-head blobs (research_record_check.py 2fbd970c, test d4002a7e, report 5affcc51); the submit→frozen diff touches only gate JSONs, the M0-T192 report, state.json and the task file (ledger only). `python3 tools/validate_directive_compliance.py --check` → exit 0 (quiet on success; I corroborated via the direct digest recompute above).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while a blob-level predicate holds: the packet's allowed-path files keep their frozen blob ids — tools/research_record_check.py = 2fbd970c, tools/test_research_record_check.py = d4002a7e, project-control/reports/M0-T192-producer-report.md = 5affcc51 — and R075's body (sha ace14f48...) plus its M0-T192 applicability binding and the three D-093 source digests stay unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits MAY touch any other file (other wave tasks' files under services/, apps/, packages/, docs/ including other evidence records, their packets, gates, reports, directive bindings of other tasks, and ledger state.json), plus this task's own acceptance records (its gates/report/task/state rows), and a merge of the main line that changes none of the three predicate blobs. Any such commit does not void this verdict.

(5) REQUIRED CORRECTIONS
 - None. All review findings are low/advisory and non-blocking: G3 A1 (professional_review.date still validated only as a non-empty string — conforms to packet scope), G3 A3 (fractional-seconds regex, immaterial on Python 3.11+), G5 F1 (out-of-range calendar values recovered fail-closed by fromisoformat), G5 F2 (disjoint M5-T158 peer commits in the review range, correctly excluded). The single G4 advisory (non-Z offset unpinned) was closed by the added offset test at c9e292a7 and re-confirmed by G4/G5 delta PASS.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - The control-plane CI job on the wave's PR head: CI/orchestrator responsibility, not reproducible read-only here; the two documented test commands and the two permitted validators all PASS locally at the frozen head.
 - The full api suite and tools/test_directive_compliance.py: forbidden by brief (hours-long); they are CI's job.
 - Legal/professional correctness of the NB-01..NB-06 record contents: out of scope — the tool and this task change no legal reading/fact/calculation input/label (D-093; nothing here is a professional verification).
 - DB-238's merge-seam update: an orchestrator action at merge, not in this diff; it stays open (WATCH) and is correctly deferred.
 - Observation (not a finding): the real committed NB-01 record at the frozen head still carries a TIMED revision-3 review stamp (2026-10-11T07:26Z) — the prior workaround — so it reads current trivially (revision match). This is harmless and outside this task's forbidden-paths (docs/research/evidence-records/); R075's date-only NB-01 shape is proven by the dedicated unit test rather than by the live record, which satisfies the requirement's test clause.
END-OF-REPORT
```

# M5-T203 - directive-compliance verification (directive-compliance-verifier, read-only)

Frozen head verified: `06278fe458568bc0a2746db45f83c10c05cba399` (branch `task/wave29-scenario-drawings`, review copy `git plumbing at the frozen head`). Directives D-094. The verifier is an AI agent; it was not the producer and wrote none of the records.
Applicable rows for this task (`evaluate_task_refs`: applicable == cited): R287.

## Verdict: PASS for every row, each for this task's share.

Each row's last evidence sentence says what of the row stays open for later work; the rows stay bound in the registry to the tasks that do that work.
Required corrections, in the verifier's words: - None. The three independent reviewers' shared ADVISORY (docstring/NB-01 call the memo "per-request" when it is a process-wide bounded LRU partitioned by the per-request correlation id) is wording-only, non-blocking, and does not affect R287.
Its carry-forward condition (item 4) is the rule for stamping this verdict at a later head; the orchestrator's script checks it at the live head before writing the verification row.
What it could not check itself is its item 6.

Transmission: the verifier's return arrived in one part, received 2026-10-16T01:15:09Z, ending with its own line END-OF-REPORT. It follows unchanged (copied from the session transcript by script).

---

```
DIRECTIVE-COMPLIANCE VERIFICATION — ledger task M5-T203 (directive D-094, 1 rows)
VERDICT: PASS

I am an AI agent performing an independent, read-only directive-compliance verification. This is NOT a human or professional review. I produced none of the work or records under review; I re-derived each item from primary evidence (the owner's words in the directive source, the task files at the frozen head, the gate records, the git objects, and the registry helpers). I ran no write command; I ran `validate_directive_compliance.py --check` once (exit 0) and read CI read-only.

(1) HEAD VERIFIED
 - Frozen head read: `06278fe458568bc0a2746db45f83c10c05cba399` on branch `task/wave29-scenario-drawings` in `/root/project/w-wave29`; `git rev-parse HEAD` confirms it and the working tree is clean (disk == frozen head).
 - This is the M5-T203 submit commit; `git diff --stat 57f4ee7f..06278fe4` shows it adds only gate records, reports, state.json and the task packet — the 5 allowed-path files are byte-identical to the reviewed head 57f4ee7f.
 - The packet's single directive requirement is D-094-R287 (`directive_refs` in M5-T203.json); the brief's "R102" in its return-format line is a template placeholder and names no row of this task.

(2) ROWS
ROW D-094-R287 — PASS
 - Source is primary: `source-028-amendment.md` line 311 (owner verbatim) "Run the required existing gates and targeted tests that address the remaining risks. Do not substitute large counts of redundant tests for checking the real output." and the matrix line 478 maps it to R287 (harness); requirements.json R287 text reproduces both quoted sentences without softening.
 - Required gates all recorded PASS: G0 (orchestrator, f334b273 scope-correction head), G2 (orchestrator self-check), G3 (code-reviewer), G4 (qa-engineer), G5 (security-reviewer); G2–G5 sit at ONE content identity (content_manifest 933a3cdd…, reviewed_sha 57f4ee7f), matching the packet's required_gates [G0,G2,G3,G4,G5] and producer≠reviewer.
 - Tests are targeted, not padded: I read `test_study_street_window_single_fetch.py` at the frozen head — 4 focused functions (S1 fetch-count = one window not two; S2 object-for-object SiteGeometry/StreetData equality vs both the composition reference and the un-shared two-fetch result; S3 both providers surface None and the failure is not memoised; S4 flag-off builds zero shared fetches, flag-on exactly one) plus the S5 mutation (`assert 4==2`) recorded and independently re-reproduced by G3/G4/G5; these check real output, so the "no redundant bulk" clause holds. DB-273 (backlog line 403) is exactly this remaining risk (same window fetched twice when LIVE_SPATIAL_PROVIDER_ENABLED is on; off by default).
 - Stays open: nothing stays open for THIS TASK'S SHARE — the row's gates and targeted tests for M5-T203 are complete. R287 is a standing harness rule and remains applicable to future tasks via D-094-BOOTSTRAP; that continuing applicability is not an M5-T203 debt.

(3) BINDING B1–B5
 - B1 PASS: R287's applicability.task_ids went from ['D-094-BOOTSTRAP'] at fb7acb78~1 to ['D-094-BOOTSTRAP','M5-T203'] at the frozen head; `git show fb7acb78` proves the M5-T203 append was in the contract commit; R287's text is byte-identical across fb7acb78^..06278fe4 (the only other requirements.json changes in range are M5-T204/M5-T205 appends to two OTHER rows — disjoint peers).
 - B2 PASS: `directive_registry.sha256_text_artifact(requirements.json)` = 9ed95b1792e22ed1ee627872e56f184145662f86624c434df557d093de140ad5 equals manifest.requirements_content_digest_sha256 (identical value).
 - B3 PASS: verification.json has exactly one M5-T203 task_verifications row, applicable_requirement_ids ['D-094-R287'], verifier "" (empty), requirements[0] {id D-094-R287, state "pending", reviewed_sha null}.
 - B4 PASS: `reg.evaluate_task_refs(M5-T203.json)` → ok=True, applicable_ids=['D-094-R287'], cited_ids=['D-094-R287'], missing=[], invalid=[], unresolved=[] (applicable == cited).
 - B5 PASS: the registry loaded 92 active directives; derive_applicable across all of them returns only D-094-R287, so nothing else applies to M5-T203 uncited. `validate_directive_compliance.py --check` exit 0 with HEAD still at 06278fe4 (no transient c14).

(4) CARRY-FORWARD CONDITION
 - This PASS may be stamped at a later head WITHOUT a new review while this blob-level predicate holds: the 5 allowed-path files keep their git blob ids at the stamping head — study_live_geometry.py c65a83b85327d21adef5635edb98160d27bf8717, study_inputs.py 1a774f5f374b20bc53f0d4b1e5150c2e779923fd, test_study_street_window_single_fetch.py 2649d770844fbc30dbd0963573b4925430657cdd, M5-T203-producer-report.md 2ca75fddc017c2b7a55a8e45e0f92f515aa0f007, NB-01-zoning-lot-instruments.json a9ed69e4e60b3332c15381efbb1bf9e9b68d5356 (equivalently LF sha256 c58e6073…/6c743470…/3397c2ca…/88bfcdb4… for the three source/test/record files) — AND R287's text plus its M5-T203 binding stay unchanged.
 - BROAD DISJOINT-PEER TOLERANCE: later commits may touch any other file (other wave-29 tasks' sources under services/, apps/, packages/, docs/, .claude/, their packets/gates/reports, other tasks' directive bindings, new rows appended to D-094, ledger state), plus this task's own acceptance records (its gate/report/state/task files) and a merge of the main line that changes none of the predicate's five files — none of these voids this verdict.

(5) REQUIRED CORRECTIONS
 - None. The three independent reviewers' shared ADVISORY (docstring/NB-01 call the memo "per-request" when it is a process-wide bounded LRU partitioned by the per-request correlation id) is wording-only, non-blocking, and does not affect R287.

(6) WHAT I COULD NOT INDEPENDENTLY CHECK
 - I did not run the full services/api suite or test_directive_compliance.py (both forbidden by the brief); I relied on CI run 38832424311 (CI job "completed success", 8m29s) at the content-identity head 57f4ee7f, which I read read-only, plus the G2 self-check log claim (10120 passed, 8 skipped).
 - The CI "CI" job for the frozen submit head 06278fe4 (run 38833405646) was still "in_progress" at my read (its secret-scan and context-budget were success); because the 5 task files are byte-identical between 57f4ee7f and 06278fe4, the api result cannot differ, but per R639 the orchestrator must read the CI green at the actual accept/merge head before accepting.
 - I did not re-execute the targeted pytest or the S5 mutation myself (to avoid heavy-run-lock contention and stay read-only); I verified them by static read of the test file and by the three independent reviewers' reproduced "27 passed" and "assert 4==2" red/green.
 - Live behaviour with LIVE_SPATIAL_PROVIDER_ENABLED on against the real city DCM service was never exercised (flag off by design); it stays UNKNOWN. I did not re-derive the R6B reference-case figures (not implicated by this row).
END-OF-REPORT
```

# M5-T203 reviews (every return kept unchanged)

- Two producer rounds (backend-engineer, worktrees): round 1 510632bb (the shared street-window fetch: shared_street_window_fetch in study_live_geometry.py, wired in study_inputs.py; test_study_street_window_single_fetch.py) and, after scope correction 1 (NB-01 joins the allowed paths; G0 re-recorded at a3fa709c), round 2 8c354af7 (NB-01 revision 11: study_inputs.py code identity and one dependency-assessment entry). Integrated as the cherry-picks 45d1492d and 57f4ee7f on task/wave29-scenario-drawings (5 files, all inside the allowed paths; LF sha256 equal to the builder returns).
- G2 orchestrator self-check at 57f4ee7f: the whole api suite passed on the increment (10120 passed, 8 skipped; api-suite-M5-T203.log); research record check PASS with no NB-01 drift; lane coverage PASS; the flag (LIVE_SPATIAL_PROVIDER_ENABLED) stays off by default.
- G3 code-reviewer PASS, G4 qa-engineer PASS (added a cross-request isolation and cache-bound probe), G5 security-reviewer PASS (cache key and lifetime, thread safety, no cross-request leakage: the key carries the server-minted per-request correlation id; failures never memoised; flag off byte-identical). Shared advisory (all three): the docstring and NB-01's note call it a 'per-request memo'; it is a process-wide bounded LRU (256) whose reuse is partitioned by the per-request correlation id. Wording only; recorded for the next edit of that file.

Every reviewer is an AI agent; none is a human or professional review.

## G3 (code-reviewer)

VERDICT: PASS — G3 code review of ledger task M5-T203 (DB-273: one shared street-window fetch behind the live spatial flag). I am an AI agent; this is not a human or professional review.

REVIEWED IDENTITY
- Branch head 57f4ee7f8e30b114e6122bcf3c0808a0e6a88161 (round 2) whose parent is 45d1492d (round 1), in worktree /root/project/w-wave29. I did not modify that worktree; I reviewed from `git archive 57f4ee7f` extracted into /tmp/claude-0/code-reviewer/repo.
- LF sha256 at 57f4ee7f (tr -d '\r' | sha256sum), all matching the builder returns and the NB-01 pin:
  - study_inputs.py            6c743470ec38d79160f2711d91985f049fb85f10e792b872bab868ecc1d270a3
  - study_live_geometry.py     c58e607396299da4567fec2ee21f119689f719d28809d469e802f72e1ccc4427
  - test_study_street_window_single_fetch.py  3397c2ca3c66f39101af0f7a1fa931a4c0d47c127cfdc2a337fb06c1360f8cbb
- Scope: the diff touches only the 5 allowed_paths (study_live_geometry.py, study_inputs.py, the new test, the producer report, and NB-01 after scope correction 1). Nothing outside scope changed.

WHAT I INDEPENDENTLY REPRODUCED (commands + outputs)
1. Targeted suite (the packet's documented command), under flock /root/project/lanes-runtime/heavy-run.lock, lanes venv, PYTHONPATH=.../services/api:
   pytest -q tests/api/test_study_live_geometry.py tests/api/test_study_inputs_live.py tests/api/test_study_street_window_single_fetch.py tests/api/test_study_live_outline_provider.py
   -> 27 passed in 3.73s, exit 0. Confirms S1-S4 as integration tests plus the existing regressions.
2. ruff check on the three changed source files -> "All checks passed!", exit 0 (api CI's first step).
3. tools/research_record_check.py --check -> exit 0; "PASS: every record is structurally valid..."; NB-01 status=access_blocked, code_current=True, NO NB-01 drift note. (NB-04 code_current=False is PRE-EXISTING and unrelated: I confirmed NB-04's code_identity lists neither study_inputs.py nor study_live_geometry.py, so this task cannot have caused it; it is reported-not-failed and out of scope.)
4. Disconfirming probe of app.api.v1.study_live_geometry.shared_street_window_fetch (inline python, injected counting/raising fakes, no network):
   - same (url, correlation_id) twice -> fetched once, SAME object returned (within-request dedup works);
   - same url, DIFFERENT correlation_id -> re-fetched, not aliased (cross-request isolation: no request's window leaks into another);
   - different url -> re-fetched;
   - a raising fetch across 3 attempts -> 3 calls (a failure is NEVER memoised; both providers still fail closed independently).
5. NB-01 refresh verified against actual bytes: implementation/code_identity (13 paths) now pins study_inputs.py to 6c743470... which equals the recomputed LF sha256 of the file; study_inputs.py is the ONLY code_identity path that drifted. study_live_geometry.py is pinned by NO evidence-record code_identity (it appears in NB-01 only as prose in the new Revision 11 entry) and by NO review_register entry, so no register/record resync is owed for it. The two `ebc38eeab6...` study_inputs.py hashes elsewhere in NB-01 are historical review/reviewed_code_identity snapshots (frozen past-review records) and are correctly left unchanged. The review-register-pinned three_way_document.py is untouched by this task.

CODE-REVIEW JUDGEMENTS (my lane: quality, test adequacy, contract/backward-compat, provenance, modularity)
- Correctness of the fix: _live_study_inputs_provider builds one shared_street_window_fetch() only when LIVE_SPATIAL_PROVIDER_ENABLED is on and hands the SAME wrapper to both live_geometry_provider(fetch_streets=...) and live_street_data_provider(fetch_streets=...). Both providers derive the same lot -> same envelope -> same URLs, and both call fetch as fetch(url, correlation_id) (verified default_fetch signature and all call sites: dcm_street_centerline_arcgis.py:666,1044 and _recording_fetch in dcm_street_centerline_geometry.py:515), so the memo key (url, correlation_id) correctly dedupes the window within one request. DcmTransport is @dataclass(frozen=True) with only str/int fields, so sharing one transport between providers is safe (no aliasing mutation hazard).
- Flag-off path: shared_streets stays None and both providers stay None; byte-identical, no fetch. Confirmed in code and by S4.
- Fail-closed preserved: a raised fetch is not memoised; the geometry provider catches UpstreamError via DCMConnectorError in _GEOMETRY_UNAVAILABLE_ERRORS; S3 and my probe confirm both providers reach the failure and return None.
- Thread safety / no deadlock: the OrderedDict is only touched under a threading.Lock; the fetch runs OUTSIDE the lock; no nested/re-entrant acquisition. Benign same-key race stores identical frozen bytes.
- Backward compatibility: both factories already accepted fetch_streets before this task (study_live_geometry.py:100 default_fetch default; study_inputs.py:580 None default resolved internally). The pre-existing flag test (test_study_live_geometry.py:205-220) uses **kwargs spies that absorb the new kwarg; it still passes (in the 27).
- Test adequacy vs directive D-094-R287 (harness: run targeted tests addressing the remaining risks; do not pad with redundant tests): the 4 tests are each tied to a distinct risk and S2 compares the ACTUAL derived SiteGeometry/StreetData object-for-object against both the accepted-composition reference and the two-fetch result (real output, not just counts). S5 red/green is recorded in the producer report (body -> `return fetch` makes S1 fail `assert 4 == 2`; per_window=2 for the Northern pack). No redundant-count padding. Consistent with R287. (The formal verification.json verdict for D-094-R287 is the independent directive-compliance-verifier's to record, producer != verifier.)
- Modularity: thresholds WARN=600 / JUSTIFY=750 / HARD=1000 SLOC. study_inputs.py ~570 logical SLOC (756 physical lines incl. blanks/comments) is below WARN; study_live_geometry.py ~210 SLOC. The new function is a single focused responsibility placed beside the other live-provider factories; __all__ updated; no giant function, no dumping ground, no new circular import (study_inputs imports shared_street_window_fetch locally inside the function, matching the existing pattern). I could NOT run tools/modularity_check.py --check in the extracted tree (no .git -> `git ls-files` exits 128); the SLOC is well under WARN and CI must run it green at the accepted head (R639).
- No tests touch the live network: all fetch seams are injected fakes/replays (_fake_lot, _recorded_streets, _CountingFetch, _raising_streets, monkeypatched get_pluto_fetcher/version probe); default_fetch is never invoked.

FINDINGS
- REQUIRED: none.
- ADVISORY-1 (study_live_geometry.py:81-125, docstring wording): because _live_study_inputs_provider is @lru_cache(maxsize=1), shared_street_window_fetch() is built ONCE per process, so the memo cache LIFETIME is process-wide (bounded LRU, _SHARED_STREET_WINDOW_CACHE_MAX=256), while the reuse SCOPE is correctly one request (the key includes correlation_id, so no cross-request reuse is possible — confirmed by my probe). The docstring phrase "scoped to one request" accurately describes reuse scope but could be misread as the cache lifetime; optional one-line clarification. Not a defect; does not block.
- ADVISORY-2 (memory, flag-on only): with the flag on, up to 256 frozen DcmTransport bodies (each bounded by _MAX_BODY_BYTES) can be retained across requests until LRU eviction. Bounded and off-by-default, so acceptable for this latent-cost fix; noted for the eventual production switch.

WHAT I DID NOT CHECK
- Live behaviour with LIVE_SPATIAL_PROVIDER_ENABLED on against the real city DCM service (UNKNOWN and staying unknown; never switched on here; no network touched).
- Full `pytest -q` of services/api and the web/e2e suites, and tools/modularity_check.py --check as a git-backed run — these are CI's job and must be read green at the exact accepted/merged head (R639).
- The formal security verdict (cache key/lifetime, thread safety, cross-request data, failure behaviour, no-network) and the directive verification.json — those belong to the security-reviewer and directive-compliance-verifier; my independent checks above corroborate but do not substitute for them.

Reproduction root: /tmp/claude-0/code-reviewer/repo (archive of 57f4ee7f). Recommend the orchestrator record G3 = PASS for M5-T203 and gate CI green at the accept head before acceptance.

END-OF-REPORT

## G4 (qa-engineer)

VERDICT: PASS — G4 (qa-engineer) gate for ledger task M5-T203 (DB-273: one shared street-window fetch behind the live spatial flag).

I am an AI agent; this is an independent, read-only evidence gate, not a human or professional review. I reproduced the scenarios on a clean scratch copy at the frozen reviewed identity; I did not change the w-wave29 worktree, ran no ledger/git/gh write command, and wrote only under /tmp/claude-0/qa-g4-m5t203/.

# Gate Report
- Gate ID: G4
- Task ID: M5-T203
- Reviewer: qa-engineer (independent, read-only)
- Producer: backend-engineer
- Result: PASS
- Clean environment: git archive of 57f4ee7f extracted to /tmp/claude-0/qa-g4-m5t203/repo; lanes venv; tests under flock /root/project/lanes-runtime/heavy-run.lock.

## Content identity (frozen reviewed SHA 57f4ee7f8e30b114e6122bcf3c0808a0e6a88161, branch task/wave29-scenario-drawings)
Recomputed LF sha256 (tr -d '\r' | sha256sum) on the extracted copy — all match the builder's reported values exactly:
- services/api/app/api/v1/study_live_geometry.py  c58e607396299da4567fec2ee21f119689f719d28809d469e802f72e1ccc4427
- services/api/app/api/v1/study_inputs.py          6c743470ec38d79160f2711d91985f049fb85f10e792b872bab868ecc1d270a3
- services/api/tests/api/test_study_street_window_single_fetch.py  3397c2ca3c66f39101af0f7a1fa931a4c0d47c127cfdc2a337fb06c1360f8cbb
- docs/research/evidence-records/NB-01-zoning-lot-instruments.json 88bfcdb4f06cbedf4f90c1db9a24d3a766b7749df12e19ce56932155b430636c
The 6c743470 study_inputs.py hash equals the value NB-01 revision 11 now pins (S6).

## Scope compliance
git diff --stat a0c22eaf..57f4ee7f: exactly 5 files changed — NB-01 json, M5-T203-producer-report.md, study_inputs.py, study_live_geometry.py, test_study_street_window_single_fetch.py. All are in the packet allowed_paths; nothing outside; working tree clean at head.

## Steps independently executed (actual outputs)
1. Four focused tests under the lock (packet's documented command):
   `pytest -q tests/api/test_study_live_geometry.py test_study_inputs_live.py test_study_street_window_single_fetch.py test_study_live_outline_provider.py`
   → `27 passed, 1 warning in 4.66s` (exit 0). Reproduces the builder's "27 passed".
2. Mutation reproduction (S5): changed `return memoised_fetch` → `return fetch` (sharing disabled) and ran S1:
   → FAILED `AssertionError: assert 4 == 2` (4 = 2 providers × 2 window URLs: the FeatureServer/0 metadata URL + the envelope query URL). Restored pristine module → S1 `1 passed`. Red/green independently reproduced; the test genuinely catches the mutation.
3. Added input state the builder did NOT test — cross-request isolation + cache bound (my own probe file, run under the lock): `4 passed in 1.30s`:
   - R1: one shared fetch instance (the process-wide shape _live_study_inputs_provider holds via @lru_cache(maxsize=1)); request A (cid "req-A") then request B (cid "req-B") through the SAME instance. Request B re-fetched the whole window (2 fresh transports, all carrying cid req-B); total 2×per_window. Proves NO data from one request reaches another — the correlation_id in the key is what scopes reuse to one request.
   - R2: distinct URLs under one cid are distinct keys (each fetched); a repeated (url,cid) returns the identical cached object. No false reuse across windows.
   - R3: inserting (bound+5) distinct keys never exceeds the 256-entry LRU; the oldest key is evicted (re-fetches, never a stale/error hit); a recently-used key stays cached. Bounded memory confirmed.
   - R4: _SHARED_STREET_WINDOW_CACHE_MAX is a positive int.
4. research_record_check.py --check → PASS (exit 0). NB-01 status=access_blocked, code_current=True, NO drift NOTE for NB-01 → S6 satisfied. The only drift NOTE is NB-04 (code_current=False), which is pre-existing and out of scope: I confirmed NB-04's 3 code_paths reference neither study_inputs.py nor study_live_geometry.py.
5. modularity_check.py --check (on an identical-content throwaway-git scratch, since git archive strips .git) → PASS (exit 0). Neither edited module is in the 33 warnings. study_live_geometry.py 259 lines; study_inputs.py 756 lines (SLOC under the policy line — not flagged).

## Static review of the shared fetch (security/thread-safety/memory — brief item 3)
shared_street_window_fetch builds a closure over an OrderedDict + threading.Lock. memoised_fetch: hit returns the cached DcmTransport; on miss the fetch runs OUTSIDE the lock (so a raised fetch propagates and is never stored → both providers re-reach a failure independently, matching S3), then stores under the lock with move_to_end and evicts beyond 256. All cache mutations are lock-guarded; there is no nested locking → no deadlock. A same-key race would only double-fetch and store identical bytes (harmless; idempotent). Key = (url, correlation_id): the URL identifies the window, the correlation id scopes reuse to one request and also prevents any stale cross-request reuse (a later request for the same lot carries a new cid → cache miss → fresh fetch). Flag-off path (LIVE_SPATIAL_PROVIDER_ENABLED default off): shared_streets=None and both providers None — byte-identical to the pre-task branch (confirmed by the diff and by S4, which asserts zero shared fetches constructed with the flag off and exactly one with it on). No live network is touched by any test (recorded 215-16 Northern pack via offline replay).

## Directive requirement (in-regime; directive_refs D-094-R287)
D-094-R287 (classification harness, binding, applies to M5-T203): "Run the required existing gates and targeted tests that address the remaining risks… Do not substitute large counts of redundant tests for checking the real output." From my vantage this is satisfied: S1–S6 are focused tests aimed at the real risks (duplicate street-window transport, flag-off byte-identity, failure surfacing in both providers, cross-request isolation, NB-01 provenance) and check real output (fetch count, object-for-object equality of SiteGeometry/StreetData, None surfacing), not a redundant bulk count. Note: the formal verification.json row for D-094-R287 is the directive-compliance-verifier's to record (producer=orchestrator, independent_verifier=DCV); I do not record it. My G4 contributes the "targeted tests + review notes on test adequacy" evidence R287 asks for.

## Findings
- No REQUIRED findings.
- ADVISORY 1 (study_live_geometry.py / NB-01 rev-11 note; wording only): the memo instance is process-wide — held by the @lru_cache(maxsize=1) _live_study_inputs_provider for the process lifetime and bounded by the 256-entry LRU — not literally torn down per request. The round-1 return and NB-01's rev-11 note call it a "per-request memo"; behaviorally correct (I verified no cross-request reuse and bounded memory), but the phrase could mislead a future reader. NB-01's parenthetical "keyed by the request URL and correlation id" is accurate, so this is a low-priority clarity note, not blocking.

## What I did NOT check (kept as unknowns)
- Live behavior with the flag ON against the real city DCM service — never switched on here (brief item 4); stays unknown.
- Full services/api pytest and web/e2e suites — CI's job at the accepted head (R639). I ran only the targeted four files + my probes. I observed the orchestrator's full api-suite-M5-T203 run and tests/drawings+tests/cad runs queued/running under the same lock; their green result must be read at the accepted head before acceptance.
- True multi-threaded concurrency stress: assessed by code inspection (lock discipline sound) plus single-threaded cross-request behavior (R1). I ran no live thread-race test (it would be non-deterministic).

## Reviewer conclusion
The feature does exactly what DB-273 asks: with the flag on, the geometry provider and the street-data provider share one fetch of the same street window per request (one transport, not two), the merged result is object-for-object identical to the two-fetch behaviour, a failing fetch surfaces None in both and is not memoised, the flag-off path is byte-identical, and NB-01's provenance is refreshed with no reading/warning/figure/status change. Red/green independently reproduced; my added cross-request input state confirms no data crosses requests and memory is bounded. Scope and modularity clean. PASS.

Evidence paths (scratch): /tmp/claude-0/qa-g4-m5t203/extra.out (mutation+cross-request), focused-run log /tmp/claude-0/-root-project-nyc-buildability/f3a4a686-fb58-4cf9-9dc1-56dcc8d8fba7/tasks/byzmb5281.output, rrc.out, mod2.out; my probe file /tmp/claude-0/qa-g4-m5t203/repo/services/api/tests/api/test_g4_reviewer_cross_request.py (reviewer-only, NOT part of the delivered change).

END-OF-REPORT

## G5 (security-reviewer)

VERDICT: PASS

G5 security review of M5-T203 (DB-273: one shared street-window fetch when the live spatial provider is on). Reviewer: security-reviewer (AI agent; this is not a human or professional review). Read-only. Slice reviewed per dispatch: the per-request cache (key + lifetime), thread safety, cross-request data leakage, external-call failure behaviour, the flag-off default. Frozen reviewed SHA 57f4ee7f8e30b114e6122bcf3c0808a0e6a88161 (worktree /root/project/w-wave29; HEAD == 57f4ee7f, confirmed).

No REQUIRED (blocking) findings. Two ADVISORY findings (wording/hardening only). Recommend integrate.

=== WHAT I REPRODUCED (verified facts, commands + outputs) ===

File identity at the frozen SHA (LF sha256, tr -d '\r' | sha256sum) matches the builder's claims exactly:
- study_live_geometry.py = c58e6073...4427
- study_inputs.py        = 6c743470...0a3
- test_study_street_window_single_fetch.py = 3397c2ca...8fbb

1. Focused tests, my own run on a git-archive copy of 57f4ee7f (lanes venv, under flock heavy-run.lock):
   pytest -q tests/api/test_study_street_window_single_fetch.py test_study_live_geometry.py test_study_inputs_live.py test_study_live_outline_provider.py => 27 passed in 4.42s, exit 0. (S1-S4 plus both sibling provider suites.)
2. Full api suite at the EXACT frozen head: the orchestrator-launched run from /root/project/w-wave29/services/api (HEAD==57f4ee7f) logged 10120 passed, 8 skipped in 558s (api-suite-M5-T203.log). I confirmed the worktree HEAD is byte-identical to 57f4ee7f for all three code/test files.
3. research_record_check.py --check on the frozen copy: NB-01 code_current=True, NO NB-01 drift NOTE, overall PASS, exit 0. (The one NB-04 NOTE is pre-existing at the dispatch head and NB-04 references neither file this task touched — out of scope.)
4. modularity_check.py --check in the worktree: exit 0, 0 failures; neither study_inputs.py nor study_live_geometry.py appears in any failure or warning.
5. Direct memo probe (my own, imported app.api.v1.study_live_geometry.shared_street_window_fetch from the frozen copy, no network):
   - dedup: same (url, cid) twice => underlying fetch called ONCE, same frozen object returned.
   - cross-cid isolation: same url, different cid => TWO underlying fetches, distinct objects (a different correlation id never reuses another's entry).
   - raise-not-memoised: a raising fetch => raises on BOTH attempts, nothing stored.
   - LRU bound: after 306 distinct keys the cache held exactly 256, oldest evicted, newest present.
   - thread safety: 16 threads x 200 ops => zero exceptions, cache stayed within the 256 bound.
   - S5 mutation: a no-memo passthrough re-doubled the underlying calls (2 vs the fixed 1), confirming the sharing is load-bearing.

=== SECURITY DIMENSIONS (my dispatch slice) ===

A. Cache key + lifetime — VERIFIED SAFE (with one wording caveat, finding 1).
   Key = (url, correlation_id). url is server-built from the lot envelope (build_*_url); correlation_id is the request id. DcmTransport is @dataclass(frozen=True) (immutable), so returning the same cached object to both providers cannot cross-contaminate. The cache is a bounded LRU (_SHARED_STREET_WINDOW_CACHE_MAX = 256, study_live_geometry.py:79), evicting oldest first — memory is bounded; no unbounded growth. NOTE the true lifetime is process-wide, not per-request (finding 1).

B. Thread safety — VERIFIED SAFE.
   study_live_geometry.py:108-124: all OrderedDict reads/mutations (get, move_to_end, __setitem__, popitem) happen under a single threading.Lock; the fetch (I/O) runs OUTSIDE the lock, so no deadlock and no lock held across network I/O. A same-key race at worst fetches twice and stores identical bytes (url fully determines content). move_to_end is always called with a key proven present in the same lock acquisition (no KeyError). My 16-thread probe raised nothing and stayed within bound.

C. Cross-request / cross-tenant data leakage — VERIFIED NONE.
   correlation_id is a fresh server-minted uuid.uuid4().hex per request: results_read.py:280 and study_read.py:425. It is NOT read from any inbound header — X-Correlation-ID appears only as an OUTBOUND response header (results_read.py:150, study_read.py:217). So a client cannot guess or control it. A request therefore can never produce the (url, correlation_id) key of a prior request, so it can never be served another request's cached window. Even in the astronomically unlikely uuid4 collision, the key also pins url, i.e. the same lot's same official window = identical data; no mismatched data can cross. My cross-cid probe confirmed a different cid forces a fresh fetch.

D. External-call failure behaviour — VERIFIED SAFE / unchanged.
   A raised fetch is never memoised (the store runs only after fetch returns), so each provider independently re-attempts and fails closed: live_geometry_provider catches _GEOMETRY_UNAVAILABLE_ERRORS -> None; live_street_data_provider catches the same typed set -> None. The route's own fail-safe (study_inputs.py: StudyInputsUnavailableError pass-through / 503 wrap) is unchanged. My S3 reproduction and raise-not-memoised probe both confirm both providers see the failure and return None, as before. Disconfirming check on an UNTESTED input state: metadata-success-then-page-failure — I reasoned it through (geometry memoises metadata, fails on the page -> None; street-data reuses metadata, re-fetches + fails on the page -> None). Outcome is still None in both; sharing never turns a failure into a spurious success. No defect.

E. Flag-off default — VERIFIED byte-identical.
   study_inputs.py:704-722: when live_spatial is False, shared_street_window_fetch() is NOT called (shared_streets=None) and geometry_provider / street_data_provider are None exactly as before. S4 asserts the spy is never constructed with the flag off and constructed exactly once with it on; passed. The only flag-off delta is the new local import name, which is inert.

F. SSRF / injection — no new surface. The fetch URL is server-built from the lot envelope (BBL validated via BBLValidationError before I/O); no user free-text reaches the URL. default_fetch is a single bounded GET (timeout=30s, body cap). The memo keys on that server-built URL; it introduces no new outbound target and only removes a duplicate of an already-made call.

G. Log redaction — no new risk. The new code logs nothing; the providers log only the failure CLASS + correlation_id, never the payload/body/URL. No secret or PII added to logs.

H. Service-role secrecy, private storage, upload controls, prompt-injection defenses, least privilege — N/A to this change (a pure in-process fetch-deduplication behind an off-by-default flag; it touches none of these surfaces).

=== PROVENANCE (S6 / NB-01) — VERIFIED ===
NB-01 revision 10->11, last_changed 2026-10-15->2026-10-16; code_identity["...study_inputs.py"] resynced 8f70a61c... -> 6c743470... (equals the frozen file's LF sha256); one additive Revision 11 dependency_assessment note describing the shared fetch behind LIVE_SPATIAL_PROVIDER_ENABLED (default off). No finding, warning, figure, status, or zoning-lot reading changed; research_status stays access_blocked. research_record_check PASS, no NB-01 drift. Consistent with S6.

=== FINDINGS ===

1. ADVISORY — study_live_geometry.py:88,96-99 (docstring) + NB-01 Revision 11 note + builder returns. The memo is described as a "per-request memo" and "nothing is cached across requests." Because _live_study_inputs_provider is @lru_cache(maxsize=1) (study_inputs.py:646), the shared_street_window_fetch wrapper and its OrderedDict are built ONCE and live process-wide; entries ARE physically retained across requests (precisely why the 256-entry LRU bound and eviction exist). What is correctly per-request is the REUSE, because the key carries the per-request uuid4 correlation_id. Correction: reword to "a process-wide bounded LRU (256) partitioned by the per-request correlation id" so a future reader does not assume the dict is discarded per request. Behaviour is correct and safe; wording only. Not blocking.

2. ADVISORY — isolation depends on correlation_id being a fresh, server-minted, client-uncontrollable uuid4 (verified today at results_read.py:280 / study_read.py:425). If any future caller of _live_study_inputs_provider / default_study_inputs_provider were to pass a fixed or client-supplied correlation_id, two distinct requests with the same correlation_id AND same url could share a cached window (same official data, but a staleness window within the LRU lifetime). Correction (hardening): add a short note or assertion that the correlation_id must be server-minted per request; optionally a regression test pinning that. Not blocking.

=== WHAT I DID NOT CHECK ===
- Live behaviour with LIVE_SPATIAL_PROVIDER_ENABLED on against the real city service — never switched on here; remains UNKNOWN by design.
- The broad api regression was taken from the orchestrator-launched full-suite log at the verified frozen head (10120 passed); I independently ran only the four focused files (27 passed) and the direct memo probe myself.
- Web/e2e and the full-suite-in-CI green at the accept/merge head are the orchestrator's pre-merge read (R639), not mine.

VERDICT: PASS (no blocking findings; two advisory items above).
END-OF-REPORT

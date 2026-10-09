# M5-T044 — directive-compliance verification (verbatim verifier return; transport entity-decoding only)

Saved by the orchestrator from the directive-compliance-verifier agent return, 2026-09-19
(seq-118 wave, frozen head 20c597c1). Nothing added or removed beyond decoding transport
HTML entities.

---

All evidence reproduced. The pluto precedent anchor in the nav block is accurate real source (retrieved_at stamped after the successful response in pluto_soda.py at the frozen head), confirming the advisory-graph "verified in source" clause.

Here is my complete verdict, returned verbatim to the orchestrator.

---

# GATE REPORT — M5-T044 directive-compliance verification (D-066 regime)

**Reviewer:** directive-compliance-verifier (read-only, producer ≠ verifier)
**Frozen head:** `20c597c1` on `candidate/D-024-mrl-option-b` | **Material:** `1fd07e9a` | **Combined CI head:** `a380a956`
**Cited refs:** exactly `D-066:D-066-R001` | **Checkout HEAD at review:** `11bed5f7` (child of frozen; M5-T044's 3 files byte-identical there)

## Applicability (loaded registry)
`load_registry(project-control/directives).evaluate_task_refs(M5-T044.json)` → `ok=True`, `applicable_ids=['D-066-R001']`, `cited_ids=['D-066-R001']`, missing/invalid/unresolved all empty, **applicable == cited**. D-066 status `active` (index.json line 873). D-066-R001 is the ONLY applicable+cited requirement for M5-T044 (R002/R003/R004 apply only to D-066-BOOTSTRAP/M5-T033). No missing directive requirement.
(Note: a first invocation `DirectiveRegistry('...')` without `.load()` falsely reported "D-066 does not exist"; that is an invocation artifact — the registry object requires `.load()`/`load_registry`. Corrected call is authoritative.)

## Requirement verdict

**D-066-R001 — obligation (nav block embedded + query.py instruction + advisory/verified-in-source) — SATISFIED**

Primary evidence I personally reproduced:

- **(a) Packet carried the nav block** — `project-control/tasks/M5-T044.json` inputs[3] "CODE-GRAPH NAVIGATION BLOCK (D-066-R001)" carries all five required elements verbatim: leaf status ("dtm_condo_soda.py is a LEAF (zero consumer imports)"), two-file surface ("stays inside those two files + the report"), pluto post-response precedent anchor ("pluto_soda.py ~:654-657"), query.py instruction ("Run `python tools/code_graph/query.py --no-regen impact <path>` before any sweep"), advisory clause ("graph is ADVISORY - verify in source"). Corroborated by `M5-T044-G0.md` lines 14-16.
- **(b) Material diff = exactly 3 allowed files** — `git show 1fd07e9a --name-only` = `project-control/reports/M5-T044-producer-report.md`, `services/api/app/connectors/dtm_condo_soda.py`, `services/api/tests/connectors/test_dtm_condo_soda.py` — no others. **Zero consumer imports** of dtm_condo_soda under `services/api/app/` at frozen head: `git grep dtm_condo_soda 20c597c1 -- services/api/app/` returns only two self-references inside the module itself (logger name L102, log_label L421); import-form grep exits 1 (no matches). Leaf claim in the nav block **verified in actual source**.
- **(c) Suites green — independently reproduced (not trusted from claim):** at working tree (== material for both code files), `python -m ruff check` = "All checks passed!"; `pytest tests/connectors/test_dtm_condo_soda.py -q` = **54 passed**; `pytest tests/connectors -q` = **880 passed** (no consumer regression, leaf isolation). M5-T044's 3 files **byte-identical** material→`a380a956`→`20c597c1` (both `git diff --stat` empty). Combined head `a380a956` is bookkeeping-only over material (`git diff 1fd07e9a..a380a956 -- apps/ services/ packages/` empty). Disjoint peer M5-T043 material `f6e88222` (rules/spatial/web files) has **empty intersection** with M5-T044's allowed_paths. CI run **35412920210 = success at a380a956** is orchestrator-captured in `M5-T044-ci-evidence.md` (gh/network unavailable to a read-only reviewer); I verified it is consistent with the frozen head via the byte-identity and bookkeeping-only checks above.
- **(d) Deliberate scope boundaries honored** — no source_registry record (`SOURCE_ID` line carries comment "source_registry record deferred to the wiring packet"; material touches no registry file); no official fixture capture (no fixture files in the 3-file diff; tests use offline transport stubs — no `httpx.get`/`requests.get`/`urlopen`); no consumer wiring (zero imports; no `app/` file other than the connector changed). All wiring-era (DB-029 b/c) boundaries respected.
- **(e) Advisory-graph "verified in source" clause honored** — nav-block precedent anchor is accurate: `pluto_soda.py` at frozen head ~L654 carries "# G3 D3: stamp retrieved_at AFTER the successful response" / `retrieved_at = _rfc3339(clock())`.

Producer report + evidence-map (`M5-T044-evidence-map.json`) are CLAIMS; every underlying fact above was reproduced directly from git objects, source, the loaded registry, and re-run suites.

## VERDICT: PASS

D-066-R001 = **SATISFIED**. No VIOLATED / UNVERIFIABLE / BLOCKED results. The one applicable+cited requirement for M5-T044 is verified against primary evidence at the frozen head.

## Conditional restamp pre-authorization (peer-tolerant)

For a later head `<H>` I pre-authorize restamping `reviewed_sha` to `<H>` WITHOUT re-review when ALL five conditions hold:
1. `git diff 1fd07e9a <H> -- services/api/app/connectors/dtm_condo_soda.py services/api/tests/connectors/test_dtm_condo_soda.py project-control/reports/M5-T044-producer-report.md` is EMPTY (LF-normalized) — M5-T044's own 3 files byte-identical to material.
2. `evaluate_task_refs(M5-T044.json)` on the loaded registry at `<H>` still returns `ok=True`, applicable == cited == `['D-066-R001']`; allowed_paths still exactly the 3 files.
3. D-066 remains `active` and D-066-R001 unamended/unweakened (source-001 digest unchanged; no amendment softening R001).
4. Zero production-consumer imports of `dtm_condo_soda` under `services/api/app/` at `<H>` (still a LEAF); ruff clean + 54 focused / 880 connectors-wide green at `<H>`'s content; CI success at `<H>` (live or orchestrator-captured conclusion).
5. The packet's D-066-R001 five-element navigation block is still present in the M5-T044 packet at `<H>`.

**Explicit peer tolerance:** disjoint peer-task product commits (e.g., M5-T043 `f6e88222`, or any other task's material) landing between `20c597c1` and `<H>` are TOLERATED and do NOT invalidate this verification, PROVIDED none of them touch any of M5-T044's 3 allowed_paths and M5-T044's 3 files stay byte-identical to `1fd07e9a` (conditions 1 + 4). Bookkeeping-only control-plane commits are likewise tolerated.

## Exact read-only commands run
- `git rev-parse HEAD` ; `git branch --show-current` ; `git log --oneline -8`
- `git show 1fd07e9a --name-only`
- `python -c "load_registry(Path('project-control/directives')); reg.evaluate_task_refs(json.load(M5-T044.json))"` (+ `reg.get('D-066').status`)
- `git grep -n dtm_condo_soda 20c597c1 -- services/api/app/` ; `git grep -nE "import .*dtm_condo_soda|from .*dtm_condo_soda" 20c597c1 -- services/api/app/`
- `git diff --stat 1fd07e9a a380a956 -- <3 files>` ; `git diff --stat 1fd07e9a 20c597c1 -- <3 files>` ; `git diff --stat 1fd07e9a -- <2 code files>` (working-tree parity)
- `git show f6e88222 --name-only` + `comm -12` intersection with M5-T044 allowed_paths
- `git diff --stat 1fd07e9a..a380a956 -- apps/ services/ packages/`
- `git show 1fd07e9a:services/api/app/connectors/dtm_condo_soda.py | grep -nE "source_registry|register_source|SourceRegistry|httpx\.get|requests\.get|urlopen"`
- `cd services/api && python -m ruff check app/connectors/dtm_condo_soda.py tests/connectors/test_dtm_condo_soda.py`
- `cd services/api && python -m pytest tests/connectors/test_dtm_condo_soda.py -q` (54 passed)
- `cd services/api && python -m pytest tests/connectors -q` (880 passed)
- `git show 20c597c1:services/api/app/connectors/pluto_soda.py | sed -n '650,660p'` ; `git cat-file -e 20c597c1:services/api/app/connectors/pluto_soda.py`

Relevant absolute paths: `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M5-T044.json`, `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\directives\D-066-code-graph-loop-wiring\{source-001.md,requirements.json}`, `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\{M5-T044-G0.md,M5-T044-ci-evidence.md,M5-T044-evidence-map.json}`, `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\connectors\dtm_condo_soda.py`, `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\connectors\test_dtm_condo_soda.py`.

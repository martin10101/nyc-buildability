<!-- Verbatim reviewer return (agent-return channel; agentId a633f546047542aff, code-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Verdict: FAIL (D1 HIGH provenance-narrative defect, D2/D3 MEDIUM documentation corrections). Rework is documentation reconciliation only; fixtures retained as-is. -->

# G3 Gate Report — M1-T008 (DOB-wide legacy source research)

- **Task:** M1-T008 — BIS/DOB-wide legacy source research (research-only)
- **Gate:** G3 independent walkthrough / consistency / discipline review (code-reviewer, per ADR-005 read-only protocol)
- **Producer:** official-source-researcher
- **Reviewer:** code-reviewer (independent; did not produce any reviewed artifact)
- **Review target:** branch `task/M1-T008-dob-legacy-research` @ `b28d9d0` (task commit `4535b18`; `b28d9d0` is the merge of hardened main / M0-T014), worktree `.claude/worktrees/M1-T008`
- **Date:** 2026-07-17
- **Method:** read packet + binding directives first; walked the research document as its consumer (future connector engineer); cross-checked every checkable claim against the 43 committed fixtures; diffed `d61c9b6..4535b18` for scope and naming discipline; verified merge `4535b18..b28d9d0` left all three deliverable paths byte-identical (empty diff).

## 1. Findings table

| # | Check | Expected | Actual | Evidence |
|---|---|---|---|---|
| F1 | Scope discipline: task commit touches only allowed paths | doc + fixtures dir + own report only | CONFIRMED — `git show --stat 4535b18`: exactly `docs/research/dob-legacy-sources.md`, `services/api/tests/fixtures/dob_legacy/**`, `project-control/reports/M1-T008-producer-report.md`. No app code, no contracts, no connector smuggled in | commit 4535b18 stat |
| F2 | Merge commit contains only legitimate M0-T014 files; deliverables unaltered by merge | empty diff on deliverable paths | CONFIRMED — `git diff 4535b18..b28d9d0 -- <3 deliverable paths>` is empty; merge brings `tools/project_control.py`, tests, workflows, M0-T014 ledger only | diff output |
| F3 | Naming rule: bf97-mjsy never associated with BIS | zero BIS associations in entire diff | CONFIRMED — every bf97 mention in the diff says "DOB Incident Database"; terminology guard at doc line 7; official metadata for bf97 contains 0 "BIS" occurrences | `git diff d61c9b6..4535b18 | grep -in bf97`; `views_metadata_extract_17_datasets.json` datasets.bf97-mjsy |
| F4 | Spot-check: BBL-pollution grouped query | 884,315 len-7 of 2,715,651 (32.6%) + 29,120 null | CONFIRMED — `[{"len":"10","n":"1802216"},{"len":"7","n":"884315"},{"n":"29120"}]`; sums exactly to 2,715,651; 884315/2715651 = 32.56%. Same-job pollution pair confirmed: `bbl:"1006014"` and `bbl:"1004410016"` on job 103208002 | `query_ic3t-wcy2_bbl-length-distribution.json:1-3`; `query_ic3t-wcy2_bin1006014_bbl-pollution.json:1-2` |
| F5 | Spot-check: 855j composite-key derivation / 3h2n duplication | `040618LBLVIO00614` = 3h2n `20180406`+`LBLVIO`+`00614` | CONFIRMED — 3h2n row 3: number `00614`, date `20180406`, type LBLVIO, ACTIVE; 855j: `040618LBLVIO00614`, 2018-04-06, LBLVIO, Active, same BBL 1004410016 | `query_3h2n-5cm9_bin1006014_positive.json:3`; `query_855j-jady_bin1006014_dup-of-3h2n.json:1` |
| F6 | Spot-check: empty e98g-f8hy | `[]` and count 0 | CONFIRMED — `sample_e98g-f8hy_empty.json` = `[]`; `cnt_e98g-f8hy` = 0 in counts log | `sample_e98g-f8hy_empty.json:1`; `query_log_counts_and_ranges.txt:17-20` |
| F7 | Spot-check: HTTP-400 drift signature | `query.soql.no-such-column` with column enumeration | CONFIRMED — errorCode `query.soql.no-such-column`, full 60-column enumeration in error body | `query_ipu4-2q9a_bad-column_http400.json:1` |
| F8 | Spot-check: mixed date formats in ipu4 `issuance_date` | min MM/DD/YYYY, max ISO | CONFIRMED — `[{"lo":"01/01/2007","hi":"2020-06-05"}]` | `query_ipu4-2q9a_minmax_issuance-date_mixed-formats.json:1` |
| F9 | Spot-check: cross-channel BIN 1006014 join | positive hits in ipu4/ic3t/3h2n/6bgk/eabe/855j, `[]` in bs8b/bf97 | CONFIRMED — counts log: ic3t 2, ipu4 1, eabe 17, 3h2n 3, 6bgk 6, 855j 1, bs8b 0, g76y 0; all per-dataset positive/no-match fixtures agree | `query_log_cross_channel_bin1006014.txt:12-51` |
| F10 | §2.2 identity table vs committed metadata | col counts + rowsUpdatedAt match | CONFIRMED for all 12 in-scope + 5 candidates (e.g. ic3t 95 cols, bty7 frozen 2018-08-07, g76y frozen 2023-04-18, iz2q 2024-01-02, nyis 2024-01-03) — **except the eabe anchor, see D1** | `views_metadata_extract_17_datasets.json` |
| F11 | S1 completeness as a consumer document | dataset ID, schema inventory, cadence, limits, quirks, coverage labels, priority per family | CONFIRMED — §2.2 identity, §3 per-source field evidence with observed samples, §5 auth/pagination, §6 per-family channel-coverage table with residual-gap column, §7 staged priority, §10 open-questions ledger. A connector engineer could build Stage A/B from this without guessing; unknowns are ledgered (OQ-1..7), not glossed | `docs/research/dob-legacy-sources.md` §2–§10 |
| F12 | Directive §2–§5 conformance (structure, not claims) | connector model, parser expectations, staged priority, channel labels | CONFIRMED — §7 Stage A parser-hardening list extends directive §3 with observed legacy hazards (7-char-BBL rejection, 5/5 vs 5/4 vs unpadded padding, TEST-record quarantine, future-date window, computed-region exclusion); §6 implements directive §5 labeling incl. "complete DOB records remains impossible"; §7 stages tied to directive §4 trio | doc §6 line 141, §7 lines 145–150 |
| F13 | S2/bf97 C1v2 disposition | secondary/future, M2 risk stage, values match M1-T007 | CONFIRMED — 1,326 rows, 2024-01-03→2026-07-14, matches memory of the M1-T007 C1v2 live re-check exactly | doc §3.3; `query_log_counts_and_ranges.txt:27-30,107-110` |
| F14 | S6 rejections evidence-backed | ≥1 rejection with reasons | CONFIRMED — 4 rejections; freshness/shape claims match committed candidate metadata and samples (ndq3 7 cols no property keys; t8hj licensee-keyed; iz2q/nyis frozen 2024-01 contradicting stated Daily); honest "NOT verified/recorded as unknown" on the ic3t-overlap question | doc §8; views extract; `sample_ndq3-kuef.json`, `sample_t8hj-ruu2.json` |
| F15 | Fixture hygiene: credentials/tokens | none | CONFIRMED — grep for token/authorization/bearer/api-key/secret over the fixtures dir: zero hits; all recorded URLs tokenless | grep output |
| F16 | Low-storage | KB-scale total | CONFIRMED in substance — 146,865 bytes of fixtures (~143 KB). No bulk artifacts. **But the stated "~77 KB / 26 files" is wrong — see D2** | `du`/byte-sum over fixtures dir |
| F17 | Producer report AOS §6 packet | files, commands, expected-vs-actual, assumptions, limitations, security, next tasks | CONFIRMED structurally — all sections present; §5 "surprises disclosed" is genuinely good practice. **But S3/S7 rows repeat the D1/D2 misstatements** | `M1-T008-producer-report.md` |
| F18 | Doc retrieval-timestamp claims vs committed evidence | claims match machine-dated artifacts | **CONTRADICTED — see D1** | see D1 |
| F19 | Doc claims vs its own committed logs (silent uncertainty) | no committed evidence contradicting doc statements | **CONTRADICTED — see D3** | see D3 |
| F20 | README lists every fixture accurately | complete URL-per-file inventory | **INCOMPLETE — see D2** | see D2 |

## 2. Defects

### D1 — Retrieval-timestamp/provenance narrative contradicted by the committed evidence (HIGH, BLOCKING)

The doc header states "**All retrievals:** 2026-07-17, 16:15–16:21 UTC" with a "server-time anchor: `eabe-havv` metadata `rowsUpdatedAt` epoch 1784304931 = 2026-07-17T16:15:31Z, refreshed seconds before capture" (doc line 5). The README header and producer report repeat the 16:15–16:21 window; §2.2/§3.3/§4/§8/§11 assert per-step times of 16:16–16:21 UTC throughout. Every machine-dated committed artifact contradicts this:

- `catalog_dob_sweep_extract.json` `_retrieved_utc`: **2026-07-17T10:55Z**
- `views_metadata_extract_17_datasets.json` `_retrieved_utc`: **2026-07-17T10:56Z**
- `query_log_counts_and_ranges.txt`: **11:01:25 / 11:01:58 UTC**
- `query_log_key_probes.txt`: **11:02:53 / 11:03:03 UTC**
- `query_log_cross_channel_bin1006014.txt`: **11:03:54 UTC**
- `response_headers_3h2n-5cm9_count.txt` `Date:` header: **11:04:48 GMT**

The eabe anchor itself is unevidenced: the committed views extract records eabe `rowsUpdatedAt` = **2026-07-16T16:49:33Z**, not 2026-07-17T16:15:31Z; no committed artifact contains epoch 1784304931. Likewise §2.1's discovery claims (`q=DOB&limit=100` → resultSetSize **82**, on both endpoints, "identical ID set") do not match the committed catalog extract, which records different queries (`only=dataset&limit=150`) with resultSetSize **71** and a second sweep (`q="Department of Buildings"` → **342**) the doc never mentions. Either a second 16:15-session capture happened and its artifacts were not committed (making the claims unevidenced), or the timestamps were written inaccurately (making them false). In a provenance-first project (PRD §9; permanent principle 2/3) where retrieval timestamps are themselves S1 acceptance material ("retrieval timestamps" is a literal S1 requirement), the primary deliverable misstating its own provenance is blocking.
**Repro:** compare `docs/research/dob-legacy-sources.md:5,27-28,34,100,154` and `README.md:3` against the six artifact timestamps above.
**Rework:** reconcile every timestamp claim to the committed artifacts (or commit the later session's evidence including the eabe 16:15:31Z metadata capture and the 82-result catalog responses), and disclose the session structure honestly.

### D2 — Fixture inventory misstated; README incomplete; "verbatim" claim false for six files (MEDIUM, BLOCKING as documentation correction)

Doc §9, producer report §1, and the README all claim "**26 files, ~77 KB**". Actual committed set: **43 fixture files + README, 146,865 bytes (~143 KB)**. The README's tables name only 25 files; **18 committed fixtures are undocumented**, including load-bearing evidence: the 3 `query_log_*.txt` files, `views_metadata_extract_17_datasets.json`, `catalog_dob_sweep_extract.json`, `response_headers_3h2n-5cm9_count.txt`, the ECB cross-reference join pair (`query_3h2n-5cm9_with_ecb_number.json` / `query_6bgk-3dad_ecb_34254160K_join.json` — the only committed proof of §3.2's "ecb_number cross-references 6bgk-3dad" claim), the 5 rejected-candidate samples, `sample_i296-73x5.json`, two `*_select.json` probes, `query_ic3t-wcy2_bin_0000000_nomatch.json`, and a stray duplicate `sample_e98g-f8hy.json` (byte-identical to `sample_e98g-f8hy_empty.json`, only the latter documented). The README's "Every file is a VERBATIM HTTP response body (no editing)" is false for the annotated logs and the two `_extract` files (which are structured extracts with producer-added `_retrieved_utc`/`_source_url_pattern` keys). Total size remains well within low-storage policy, so the violation is inventory accuracy, not storage.
**Repro:** `ls services/api/tests/fixtures/dob_legacy | wc -l` (44 incl. README) vs README tables; byte-sum 146,865.
**Rework:** complete the README inventory (URL or provenance note per file), correct the count/size claims everywhere, scope the "verbatim" statement to the files it is true for, delete or document the duplicate e98g sample.

### D3 — Doc understates/contradicts evidence it committed (MEDIUM, BLOCKING as documentation correction)

Committed logs contain results the doc says don't exist or omits:
1. **OQ-6 claims the 6bgk-3dad date range is "unquantified... LIKE-decade sweep not run (request budget)"** — but `query_log_key_probes.txt:44-52` contains `6bgk_range_filtered` = 19101004→20260714 with a garbage count of 64, and the same log quantifies 3h2n as 19011215→20260715 (garbage 31). §6's "3h2n… 1988→present observed" and "6bgk… range unquantified" are both contradicted by the producer's own committed probes.
2. **§5 and producer-report S3 claim "~60 requests… all 200; no 401/403/429"** — `query_log_key_probes.txt:59-62` records an **HTTP 500** (`internal-error`, tag c4361147…) on `ic3t-wcy2 … min/max(latest_action_date::floating_timestamp)`. That 500 is itself a connector-relevant failure mode (server-side cast aggregation can fail on the 95-column dataset) and went entirely unreported — the exact "silent uncertainty" class this project prohibits.
3. §3.1 calls lexicographic min/max on ipu4 "useless as a date range" without mentioning that the committed `cast_ipu4` probe (`::floating_timestamp`, log lines 132-135) successfully produced the true range 1989-05-11→2026-07-15 — a materially useful technique for the Stage A connector that the document buries.
**Rework:** fold the key-probes log findings into §3/§6/OQ-6, report the HTTP 500 as an observed failure signature, and correct the "all 200" claim.

### D4 — Minor observations (LOW, non-blocking; fold into D2/D3 rework or carry forward)

- Doc §4 table shows 3 rows each for 6bgk/eabe without noting they are `$limit=3` slices of 6 and 17 hits respectively (totals are in the undocumented cross-channel log).
- The ECB join fixture pair exposes an unremarked quirk: the same violation carries `issue_date "19390711"` in 3h2n vs `"20000711"` in 6bgk (MMDDYY `071139` mis-keyed year) — worth a line in the date-hazard list.
- A few §11/D10 quantifiers (eabe `count(distinct dobrundate)=1`, 3h2n category group-by, 6v9u `code=I2`) have no committed fixture; acceptable for a research doc but G1 should live-re-verify them.

## 3. Assessment

The research substance is excellent — arguably the strongest per-source hazard inventory in the repo so far. All twelve in-scope datasets have real sampled evidence; the four rejections are honest; scope, naming, credential, and low-storage discipline are clean; directive §2–§6 conformance is real, not asserted. Every *data* claim I could check against a committed artifact checked out. What fails is the evidence narrative itself: the deliverable repeatedly asserts precise provenance facts (session window, server-time anchor, catalog result sizes, "all 200", "26 files") that its own committed artifacts contradict. Under this project's standards — and the M2-T004 precedent that assertions contradicted by committed artifacts fail even when the underlying work is sound — this cannot pass G3 as submitted. The rework is documentation reconciliation only; no re-research is needed, and the fixtures should be retained as-is (they are the trustworthy half of the record).

**Rework re-review scope (only):** D1 timestamps/anchor/catalog claims reconciled or missing-session evidence committed; D2 inventory/README/size-count corrections; D3 HTTP 500 + quantified ranges surfaced; D4 optional.

Key files (worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T008\`):
- `docs\research\dob-legacy-sources.md` (D1: lines 5, 27–28, 34; D3: §5, §6, OQ-6)
- `services\api\tests\fixtures\dob_legacy\README.md` (D1 line 3; D2 whole inventory)
- `services\api\tests\fixtures\dob_legacy\query_log_key_probes.txt` (D3 evidence: lines 44–52, 59–62, 132–135)
- `services\api\tests\fixtures\dob_legacy\views_metadata_extract_17_datasets.json` (D1: `_retrieved_utc`, eabe `rowsUpdatedAt`)
- `project-control\reports\M1-T008-producer-report.md` (D1/D2 in §3 S3/S7, §1)

FAIL

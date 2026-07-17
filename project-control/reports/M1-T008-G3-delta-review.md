<!-- Verbatim reviewer return (agent-return channel; agentId a876871e89f32b360, code-reviewer, 2026-07-17). Saved by the orchestrator per the report-preservation rule. Delta G3 re-review after documentation-only rework commit 0a45aa5. Verdict: PASS (G3 gate as a whole, original scope + delta). One LOW non-blocking residual N1 noted for acceptance. -->

# G3 Gate Report — M1-T008 DELTA re-review (documentation rework)

- **Task:** M1-T008 — DOB-wide legacy source research (research-only)
- **Gate:** G3 delta re-review after documentation-only rework (code-reviewer, ADR-005 read-only protocol; fresh reviewer instance carrying the original G3 charge)
- **Producer:** official-source-researcher
- **Review target:** worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T008`, branch `task/M1-T008-dob-legacy-research`, rework commit `0a45aa5` on top of previously reviewed `b28d9d0`/`2813a07`. Worktree clean at HEAD = `0a45aa5`.
- **Date:** 2026-07-17
- **Binding scope:** prior G3 FAIL report "Rework re-review scope (only)" — D1 (provenance narrative), D2 (fixture inventory), D3 (contradicted/omitted evidence), D4 optional; plus G1 blocking corrections D1/D2 (same rework). Research substance NOT re-litigated (F1–F17 CONFIRMED at original G3; G1 PASS with independent live reproduction).
- **Method:** read prior G3 and G1 reports first; verified rework commit scope and fixture byte-identity via git; independently recounted the fixture directory; re-derived both epoch values myself; opened every committed artifact cited by the reconciled narrative (catalog extract, views extract, three query logs, response headers) and checked the new claims against them; grepped the three edited files for residual contradictions; walked the reconciled narrative as a future connector engineer.

## 1. Rework hygiene (method steps 2, 3, 9)

| Check | Expected | Actual | Result |
|---|---|---|---|
| `git show --stat 0a45aa5` | only the 3 allowed files | Exactly `docs/research/dob-legacy-sources.md` (96 ±), `project-control/reports/M1-T008-producer-report.md` (38 ±), `services/api/tests/fixtures/dob_legacy/README.md` (85 ±). No fixtures, no code, no contracts | PASS |
| `git diff 2813a07..0a45aa5 --stat -- services/api/tests/fixtures/dob_legacy/` | README.md only | README.md only (76 insertions, 9 deletions). All 43 fixture files byte-identical; independent recount: 43 files, **146,865 bytes** on disk (git blobs 142,982 + CRLF working-tree expansion, consistent with the M0-T010 git-blob-level identity convention) | PASS |
| No large/persistent artifacts written by rework | docs-only | 3 text files, net +153 lines; directory total 160,480 bytes — KB-scale | PASS |

## 2. Findings — D1 (provenance narrative) — RESOLVED

Every reconciled claim was checked against the committed artifact, not taken from the rework record:

| # | Claim in reworked docs | Committed artifact | Verified |
|---|---|---|---|
| D1-a | Doc header/§11, README header, report header: two-session structure; bulk capture ~10:55–11:05Z authoritative | `catalog_dob_sweep_extract.json` `_retrieved_utc` **2026-07-17T10:55Z**; `views_metadata_extract_17_datasets.json` **10:56Z**; `query_log_counts_and_ranges.txt` **11:01:25–11:01:58**; `query_log_key_probes.txt` **11:02:53–11:03:03**; `query_log_cross_channel_bin1006014.txt` **11:03:54**; `response_headers_3h2n-5cm9_count.txt` `Date: Fri, 17 Jul 2026 11:04:48 GMT` — all six read directly from the files; all match the doc's enumeration exactly | YES |
| D1-b | eabe anchor corrected: §2.2 shows committed `rowsUpdatedAt` 2026-07-16T16:49:33Z (epoch 1784220573); 16:15:31Z refresh labeled second-session/no-artifact | Views extract records `rowsUpdatedAt: 1784220573`, `rowsUpdatedAt_iso: 2026-07-16T16:49:33Z`. **Epoch arithmetic re-done by me:** 1784220573 = 2026-07-16T16:49:33+00:00; the removed anchor 1784304931 = 2026-07-17T16:15:31+00:00. Grep for `1784304931` across the three files: appears only in the producer report's rework record describing its removal | YES |
| D1-c | §2.1 rewritten to the committed catalog extract | Extract contains exactly two queries with `only=dataset&limit=150`: `q=DOB` → resultSetSize **71** with **43** `dob_attributed` entries; `q="Department of Buildings"` → **342** with **34** extracted — matches §2.1, §11 D1/D2 rows, README, and producer report §4 verbatim. The previously unmentioned 342-sweep is now documented | YES |
| D1-d | Every second-session-only claim labeled | Checked each: §2.1 82-result probe ("unevidenced convenience corroboration"), §2.2 eabe refresh, §3.1 ipu4 LIKE counts, §3.2 ic3t `%/2000`, 3h2n category group-by, eabe distinct-dobrundate, 6v9u code lookup, §3.3 AHV 28-result probe — all carry explicit "later re-verification session; no committed artifact" (or equivalent) labels; §11's "Committed evidence" column marks D2b/D7-partial/D10-partial/D11 as **none**; producer report §7 enumerates the same list | YES |
| D1-e | No G1-reviewer evidence cited as producer provenance | Grepped the three files: zero citations of the G1 re-queries (17:16–17:18Z) as producer evidence | YES |
| D1-f | Bonus consistency: README's cross-check that headers `Last-Modified` matches views-extract 3h2n | `Last-Modified: Thu, 16 Jul 2026 17:40:22 GMT` = views extract 3h2n `rowsUpdatedAt` 1784223622 = 2026-07-16T17:40:22Z — verified | YES |

## 3. Findings — D2 (fixture inventory) — RESOLVED

| # | Check | Actual | Verified |
|---|---|---|---|
| D2-a | Independent count vs corrected claims | 44 files = 43 fixtures (**146,865 bytes** fixtures-only, matching the corrected claim exactly) + README (13,615 bytes). "26 files"/"77 KB" appear only inside explicit correction notices | YES |
| D2-b | README documents every file | Programmatic cross-check: **all 43 fixture filenames appear in the README** with a URL or provenance note each — including the previously undocumented 18 (3 query logs, 2 extracts, headers capture, ECB join pair, 4 rejected-candidate samples, `sample_bf97-mjsy.json`, `sample_i296-73x5.json`, two `$select` variants, `bin__=0000000` no-match, the duplicate). Files without logged URLs carry honest "exact URL not logged at capture" notes rather than reconstructed fake URLs | YES |
| D2-c | Fixtures-only vs directory-total distinguished | Doc §9, README, and producer report all now state the distinction explicitly, including why G1's 152,100 differs (pre-rework README 5,235: 146,865 + 5,235 = 152,100 — arithmetic closes) | YES |
| D2-d | "Verbatim" claim scoped | README defines three provenance classes; verbatim is scoped to `sample_*.json`/`query_*.json`; the 2 extracts and 4 logs are re-labeled producer-assembled with their structure described accurately (I confirmed the log format: URL + HTTP status + verbatim body between `date -u` stamps) | YES |
| D2-e | Duplicate e98g documented, not deleted | README row for `sample_e98g-f8hy.json`: byte-identical duplicate, canonical file named. Verified: both files identical, 3 bytes `[]\n` | YES |

## 4. Findings — D3 (contradicted/omitted evidence) — RESOLVED

| # | Check | Committed evidence | Verified |
|---|---|---|---|
| D3-a | HTTP 500 disclosed | `query_log_key_probes.txt:59-62`: `ic3t_cast_range` → **HTTP: 500**, `errorCode "internal-error"`, tag `c4361147-3ff1-4403-b992-78910fb4c383`. Now disclosed in doc §3.1 (full treatment), §4 (second failure signature, 5xx-vs-400 classification requirement), §5, §11 D6, producer report S3 and §11 — with the "all 200" claim explicitly corrected in S3 | YES |
| D3-b | Quantified ranges folded in | Log lines 34–52: `3h2n_range_filtered` 19011215→20260715 / `3h2n_garbage_cnt` 31; `6bgk_range_filtered` 19101004→20260714 / `6bgk_garbage_cnt` 64 — now in §3.2, §6 (both channel rows), OQ-6 (re-scoped from "unquantified" to per-decade-distribution + mis-key question), and Stage B hardening (§7: "31/64 rows outside 1900–2026 quarantine") | YES |
| D3-c | `cast_ipu4` technique surfaced | `query_log_counts_and_ranges.txt:132-135`: 1989-05-11→2026-07-15 — now presented in §3.1 as the recommended Stage A range-check technique, in §5's SoQL capability list, and in §7 with the 500-fallback warning; `eabe_cast_range` (key-probes 54–57: 1988-12-30→2026-07-16) likewise surfaced in §3.2/§6 | YES |
| D3-d | Artifact attributions correct | Doc correctly places `cast_ipu4` in the counts log and `eabe_cast_range`/range-filtered probes in the key-probes log (the prior G3 report's own line references were slightly off; the doc's are right) | YES |

## 5. D4 (optional) — ADDRESSED

§4 now notes the table rows are `$limit=3` slices with committed full totals (eabe 17, 6bgk 6, from the cross-channel log — verified totals present there, incl. ic3t LIKE `%/1999`→0 and `%/2026`→8,941). The ECB `19390711`-vs-`20000711` year mis-key is now §1-5 with the fixture pair named, and propagates into §3.2/§6/§7/OQ-6 as the two-digit-year mis-key hazard. Unfixtured quantifiers are enumerated in producer report §7.

## 6. G1 blocking corrections D1/D2 — SATISFIED

G1-D1 (timestamp restatement in header/§2.2/§3/§4/README + eabe second-session note) and G1-D2 (44-file README inventory, count/size corrections, verbatim re-labeling) are the same rework, verified above. G1's non-blocking D3 (3h2n "1988→present") is also fixed — §6 now carries the committed probe values with the mis-key hedge; G1-D4 (eabe anchor) removed.

## 7. Consumer walkthrough of the reconciled narrative (normal / boundary / missing / failure)

- **Normal:** every §2.2 freshness value now traces to a named committed artifact (views extract 10:56Z); the one exception (eabe same-day refresh) is explicitly labeled no-artifact. The §11 register's "Committed evidence" column makes every row's backing checkable in one hop — I checked all 13 rows.
- **Boundary:** §11 D7 splits a single evidence row between committed (ic3t LIKE probes in the cross-channel log) and uncommitted (ipu4/eabe LIKE numbers, "none") portions, and notes the committed cast ranges answer the same question — the correct treatment.
- **Missing/ambiguous:** the three fixtures with unlogged URLs say so plainly ("exact URL not logged at capture" / "reconstructed from the response fields") instead of fabricating provenance; the duplicate sample is declared with a canonical-file pointer.
- **Failure:** a connector engineer now learns both failure signatures (400 no-such-column drift vs 500 internal-error on valid casts) and the requirement to classify them separately — a materially better deliverable than the pre-rework version.

## 8. NEW defects found in the delta

| ID | Severity | Blocking? | Description |
|---|---|---|---|
| N1 | LOW | **No** | **Stale self-referential directory-total in the producer report.** Report §1 and §11 state the post-rework directory total as "160,263 bytes", but the committed tree measures **160,480** on disk (146,865 fixtures + 13,615 README); the README evidently grew ~217 bytes after the producer measured it. Mitigating: the same sentences explicitly warn "the directory total varies with the README" and direct consumers to the fixtures-only figure, which is exact; the README itself states no post-rework total; all load-bearing corrected numbers (43 / 146,865 / 44 / 71 / 342 / 31 / 64) match my independent measurements. Also §11's phrasing "44 files / 146,865 fixture bytes" mildly conflates the file count with the fixtures-only byte figure (stated correctly in §1). Proportionality vs the M2-T004 precedent: this is a disclaimed convenience figure, not a provenance assertion — correct opportunistically (acceptance note or next touch of the report); does not warrant another rework cycle. Repro: `git ls-tree -r -l 0a45aa5 -- services/api/tests/fixtures/dob_legacy/` + on-disk byte sum vs `M1-T008-producer-report.md:15,104`. |

No other new defects. No residual sole-window claims, no "26 files"/"77 KB" outside correction notices, no unscoped "all 200"/"VERBATIM", no epoch-1784304931 presented as evidence (grep evidence in §2 above).

## 9. Prior blocking defects — explicit disposition

- **G3 D1 (HIGH):** **RESOLVED** — two-session structure disclosed; every timestamp claim now traces to a committed artifact or carries an explicit no-artifact label; false anchor removed; §2.1 matches the committed extract.
- **G3 D2 (MEDIUM):** **RESOLVED** — inventory complete and accurate; counts/sizes true and scoped; verbatim claim scoped; duplicate documented.
- **G3 D3 (MEDIUM):** **RESOLVED** — HTTP 500 surfaced as a classified failure signature; quantified ranges and cast technique folded in; "all 200" corrected.
- **G3 D4 (LOW, optional):** ADDRESSED.
- **G1 D1/D2 (blocking corrections):** **SATISFIED**; G1 D3/D4 also closed.

## 10. Assessment

The rework does exactly what both gates required and nothing else: fixtures byte-identical, scope surgical, and the reconciled narrative is now *stronger* than a merely corrected one — the artifact-per-claim register (§11) and the three-class provenance taxonomy in the README are a model for future research tasks. The original G3's verified substance (F1–F17) plus G1's independent live reproduction stand unchanged. One LOW non-blocking residual (N1) for the orchestrator to note at acceptance.

Key files (worktree `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M1-T008\`):
- `docs\research\dob-legacy-sources.md` (reconciled deliverable)
- `services\api\tests\fixtures\dob_legacy\README.md` (complete 44-file inventory)
- `project-control\reports\M1-T008-producer-report.md` (N1 residual at lines 15, 104)
- `services\api\tests\fixtures\dob_legacy\query_log_key_probes.txt` (HTTP 500 at 59–62; ranges at 34–52)

**Verdict (G3 gate as a whole, original scope + delta):**

PASS

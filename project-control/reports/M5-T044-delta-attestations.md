# M5-T044 — delta-attestations on the [ORCH-CORRECTED per M5-T044-G3 F1] correction (verbatim returns; transport entity-decoding only)

Saved by the orchestrator, 2026-09-19 (seq-118). Context: G3 returned PASS with Finding 1 as
a required correction (resolve_by_condo_key stamped retrieved_at before its fetch); the
orchestrator applied the tagged correction `a471e376` (stamp moved post-response + one
mutation-sensitive timing test; 55 passed / 881 connectors-wide / ruff clean) and resubmitted
at `0438a9ae`. All four reviewers re-attested on the corrected identity. Nothing added or
removed beyond decoding transport HTML entities.

---

## G3 code-reviewer — CARRIES, Finding 1 CLOSED

Verified. My G3 PASS **CARRIES** to the corrected identity (materials `1fd07e9a` + `a471e376`, frozen `0438a9ae`), with **Finding 1 now CLOSED**.

### Delta verification (read-only, reproduced)
- **Content identity:** both code files on disk are byte-identical (LF-normalized sha256) to `a471e376` — module `0ca9a024…431b`, test `67e6174c…0b715`; and the two code files are byte-identical at `0438a9ae` vs `a471e376` (`git diff` empty). The corrected code is faithfully frozen at the resubmission head.
- **Lineage:** `0438a9ae` carries `a471e376` in its ancestry (`git rev-list` confirms). Scope of the correction is exactly the two code files, +30/−1 (`git show --stat a471e376`) — nothing else in the material touched.
- **Finding 1 fix (correct):** `retrieved_at = _rfc3339(clock())` is removed from before the fetch and re-stamped AFTER `_fetch_rows` in `resolve_by_condo_key` (`:805`, tagged `[ORCH-CORRECTED per M5-T044-G3 F1]`), mirroring the `resolve()` post-response pattern I already verified. **No pre-I/O `retrieved_at` stamp now survives on any query path** (the NOT_A_CONDO branch stamp remains at classification, correctly disclosed — that path issues no query).
- **Test is genuinely mutation-sensitive:** `test_f1_correction_condo_key_stamp_is_post_response` (`test:772-797`) supplies a `clock()` that `assert calls` (transport ran) before returning its single moment — a pre-fetch stamp trips the assert (or StopIterations on a second call), and it asserts result-level and provenance `retrieved_at` both equal the post-fetch moment. Not a happy-path shadow.
- **Reproduced:** `python -m pytest tests/connectors/test_dtm_condo_soda.py -q` → **55 passed** (was 54); `ruff` → All checks passed. Connectors-wide 881 relied on orchestrator-captured evidence.

### Closure status at the corrected identity
- **G5 F1 / F2 / F3 — CLOSED** (unchanged by this delta; the correction does not touch the guard/URL/negative-test surface).
- **G3 #1 / item (d) — now FULLY CLOSED** across both `resolve()` and `resolve_by_condo_key`; criterion (3) "no stamp before I/O survives" holds on every query path.
- **G3 #2 / #3, (g/h/i) — CLOSED** (untouched by the delta).

### Conditions
None blocking. Advisories 2 (module at justify tier, exit 0), 3 (condo_key URL canonical asymmetry — safe under fullmatch), and 4 (`non_numeric` used for all shape failures) remain non-blocking and are accepted as routed to the wiring packet via the discovery ledger. Modularity disposition is unchanged (the delta adds a comment + one moved line in production; the new test is in the test file).

**Verdict: PASS CARRIES to `0438a9ae` (materials `1fd07e9a` + `a471e376`); Finding 1 CLOSED.**

---

## G4 qa-engineer — CARRIES

CARRIES.

I independently verified the correction at the new identity (read-only; nothing written outside my agent-memory):

- **Scope confined to F-1.** `git diff --stat 1fd07e9a a471e376 -- apps/ services/ packages/` shows *only* the two code files (module +4/-1, test +27); no other material change. Everything I originally PASSed is byte-unchanged except this improving fix.
- **The fix closes F-1.** In `resolve_by_condo_key`, the pre-fetch `retrieved_at = _rfc3339(clock())` (old `:792`) is removed and re-stamped *after* `_fetch_rows` (tagged `[ORCH-CORRECTED per M5-T044-G3 F1]`), now mirroring `resolve()`'s post-response stamps.
- **New test is genuinely mutation-sensitive.** `test_f1_correction_condo_key_stamp_is_post_response`: the injected `clock()` asserts `calls` is non-empty (transport ran) before returning its one moment. My probe — reverting the stamp back to pre-fetch in a throwaway scratchpad copy — makes it FAIL with exactly `AssertionError: retrieved_at was stamped before the fetch ran` (and a one-moment iterator would StopIteration on a second call). This is the sensitivity I probe for.
- **Reproduced green at the corrected tree** (`git archive 0438a9ae … | pytest`): `test_dtm_condo_soda.py` → **55 passed**; `tests/connectors` → **881 passed**. Matches the claim.
- **Resubmission head carries the code unchanged:** `git diff --stat a471e376 0438a9ae -- apps/ services/ packages/` empty.
- **F-2 and the informational notes (F-3/F-4)** routed to the wiring packet via the discovery ledger — consistent with my own recommendation.

My G4 **PASS carries to `0438a9ae`** with F-1 closed. No new findings; no regression. (Gate re-record, resubmission re-freeze, and CI-at-head remain orchestrator-owned.)

---

## G5 security-reviewer — CARRIES

Verified independently. The delta is exactly as represented and touches nothing in the security surface I reviewed.

**Delta verification (read-only, `git show`/`git diff`):**
- `git show --stat a471e376` = exactly the two allowed code files, +30/−1.
- Full diff `1fd07e9a → 0438a9ae` on both code files shows **only**:
  1. `dtm_condo_soda.py` — the single line `retrieved_at = _rfc3339(clock())` in `resolve_by_condo_key` **moved** from before the fetch (old `:792`) to **after** the successful `_fetch_rows` (now `:805`), plus a 2-line `[ORCH-CORRECTED per M5-T044-G3 F1]` comment. Net +3/−1.
  2. `test_dtm_condo_soda.py` — one added test `test_f1_correction_condo_key_stamp_is_post_response` (+27), a mutation-sensitive timing assertion (clock refuses to stamp until the transport has run).

**Security-surface delta = none.** Not present anywhere in the diff: the guards (`_STRICT_BBL_RE`/`_CONDO_KEY_RE`, the four `.fullmatch` sites at :357/:514/:708/:785), the canonical-value URL interpolation (all four f-string sites), `_build_headers`/token handling, the retry engine, and every typed error/`SchemaDriftError` path. All are byte-identical between the identity I reviewed and the resubmission. The `resolve_by_condo_key` input guard still precedes the fetch (the moved line was after the guard), so the "reject with zero transport calls" invariant is untouched.

**Assessment of the change itself:** moving the stamp post-response is a provenance-precision fix that mirrors `resolve()`; it does not weaken (marginally strengthens) fail-closed integrity — a fetch failure still raises before any stamp/provenance is produced. No new secret, injection, SSRF, DoS, or fail-closed surface. Orchestrator-reported ruff clean / 55 / 881 is consistent with a +1 test and no behavior change; the security-relevant behavior I empirically probed rests on byte-identical code.

**My F1, F2, and F3 remain CLOSED at the corrected identity.** My three advisories (dedicated response-side condo_key-guard test; `$limit`; `_ERROR_CODE_SAFE_RE` fullmatch) stay routed to the wiring packet.

**Reply: CARRIES** — G5 PASS (F1/F2/F3 CLOSED) carries to resubmission head `0438a9ae` (correction `a471e376`).

---

## Directive-compliance verifier — EXTENDED

Independently verified — the correction carries. Reply: **EXTENDED**.

### Delta-attestation verdict — D-066-R001 PASS carries to corrected material identity (`1fd07e9a` + `a471e376`)

Everything I reproduced (read-only; wrote nothing):

- **Correction commit `a471e376`** touches exactly the 2 allowed code files, `+30/-1`, tagged `[ORCH-CORRECTED per M5-T044-G3 F1]`. Content = the retrieved_at stamp moved from BEFORE `_fetch_rows` to AFTER the successful fetch in `resolve_by_condo_key` (the pluto post-response precedent, mirroring `resolve()`) + one mutation-sensitive timing test. Grep for added `source_registry|register|httpx|requests.|urlopen|import` = none (exit 1) → **no scope-boundary regression** (still no registry record, no fixture, no consumer wiring).
- **Code frozen since the correction:** `git diff a471e376 → 0438a9ae` and `→ 880a154d` for the 2 code files are both empty; producer report byte-identical to `1fd07e9a`. `a471e376` is an ancestor of `0438a9ae` and of resubmit tip `880a154d` (which touches only `state.json` + `M5-T044.json` control-plane).
- **Packet D-066-R001 surface untouched:** `M5-T044.json` diff since submit = only `updated_at` + two appended progress_log rows; `directive_refs` still `D-066:D-066-R001`, `allowed_paths` still the 3 files, nav block/inputs unchanged. `evaluate_task_refs` (loaded registry) = `ok=True`, applicable == cited == `['D-066-R001']`.
- **Leaf invariant holds:** zero consumer imports of `dtm_condo_soda` under `services/api/app/` at `880a154d` (grep exit 1). The corrected function `resolve_by_condo_key` is public but has no consumers.
- **Suites reproduced at corrected content:** ruff "All checks passed!", **55 passed** focused, **881 passed** connectors-wide.

The correction is a DB-029(d) stamp-timing fix inside the module; it is orthogonal to D-066-R001 (nav block + query.py instruction + advisory/leaf/verified-in-source), and it in fact applies the very pluto precedent the nav block cited. My PASS carries.

### Amended condition 1 (all other conditions 2–5 and the peer tolerance unchanged)

**Condition 1 (amended):** `git diff <corrected-material-base> <H>` is EMPTY (LF-normalized) for all three M5-T044 allowed_paths, where the corrected material base is **`1fd07e9a` as amended by exactly the tagged correction `a471e376`** — i.e. at `<H>`:
- `services/api/app/connectors/dtm_condo_soda.py` and `services/api/tests/connectors/test_dtm_condo_soda.py` are byte-identical to their content at `a471e376`, and
- `project-control/reports/M5-T044-producer-report.md` is byte-identical to its content at `1fd07e9a`,

with the ONLY material change over `1fd07e9a` being `a471e376` itself (the single `[ORCH-CORRECTED per M5-T044-G3 F1]` commit, touching only the two allowed code files, `+30/-1`); any further material edit to the 3 files voids this pre-authorization and requires REVIEW-AGAIN.

**Conditions 2–5 unchanged** (evaluate_task_refs ok=True with applicable==cited==['D-066-R001'] and allowed_paths = the 3 files; D-066 active and D-066-R001 unamended; module still a LEAF with ruff clean + 55 focused / 881 connectors-wide green + CI success at `<H>`; the five-element D-066-R001 nav block still present in the packet).

**Peer tolerance unchanged:** disjoint peer-task product commits (e.g. M5-T043 material, bookkeeping) landing between the corrected head and `<H>` are tolerated PROVIDED none touch any of M5-T044's 3 allowed_paths and the 3 files remain byte-identical to the corrected material base above.

**Exact read-only commands run this round:** `git log --oneline -6`; `git show a471e376 --stat`; `git show a471e376 -- services/api/app/connectors/dtm_condo_soda.py`; `git merge-base --is-ancestor a471e376 0438a9ae`; `git show 880a154d --stat`; `git diff --stat a471e376 880a154d -- <2 code files>`; `git diff --stat a471e376 0438a9ae -- <2 code files>`; `git diff --stat 1fd07e9a 880a154d -- <producer report>`; `git diff 11bed5f7 880a154d -- project-control/tasks/M5-T044.json`; `git grep -nE "import .*dtm_condo_soda|from .*dtm_condo_soda" 880a154d -- services/api/app/`; `python -c "load_registry(...).evaluate_task_refs(...)"`; `cd services/api && python -m ruff check ...`; `python -m pytest tests/connectors/test_dtm_condo_soda.py -q` (55); `python -m pytest tests/connectors -q` (881).

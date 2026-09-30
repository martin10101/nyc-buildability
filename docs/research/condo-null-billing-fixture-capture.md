# Condo NULL-billing-BBL fixture capture — byte-faithful (DB-002 §3.4 gap fill)

- **Task:** bounded one-shot capture dispatched by the orchestrator to close the DB-029(c)
  precondition ahead of the condo wiring packet. Research only — no production code, no
  git/gh/project_control.py.
- **Producer agent:** official-source-researcher (isolated worktree
  `.claude/worktrees/agent-aa9fac9f65a5bfe00`, branch `candidate/D-024-mrl-option-b`).
- **Gap this fills:** `docs/research/condo-base-lot-resolution-sources.md` §3.4 measured **28**
  condos with `condo_billing_bbl IS NULL` but embedded **no raw response** for a specific one.
  Contract-test pack fixture **C6** (§9) is `p8u6-a6it?condo_key=<a NULL-billing condo>` with the
  placeholder `<a NULL-billing condo>` unfilled. This document supplies one concrete, byte-faithful
  fixture so C6 (the resolver step-4a fallback) can be pinned offline.
- **Dataset under test:** DOF Digital Tax Map "Condominiums", NYC Open Data Socrata `p8u6-a6it`
  (attribution: Department of Finance; `viewType: tabular` — live SODA resource).
- **Capture method:** raw `curl` (tokenless), bodies written straight to disk and read back
  byte-for-byte — deliberately NOT WebFetch/summarizer, because these become offline test
  fixtures and byte-faithfulness is the whole point. No reformatting beyond markdown fencing.
- **Local capture date:** 2026-09-18 (evening; UTC had rolled to 2026-09-19 at request time —
  the exact UTC request timestamps are recorded per capture below).
- **Auth/limits note:** all requests tokenless; every response was HTTP 200 (no 429). A
  production connector should still send `X-App-Token` (tokenless requests share a throttled IP
  pool; `https://dev.socrata.com/docs/app-tokens`).

---

## Chosen NULL-billing condo

| Field | Value |
|---|---|
| `condo_key` | **103343** |
| `condo_number` | 3343 |
| `condo_name` | `THE 128 HESTER STREET CONDO` |
| base lot(s) | **1** base lot: `condo_base_bbl` = `1003030019` (boro 1, block 303, lot 19) |
| `condo_billing_bbl` | **absent** (field omitted — DOF has not assigned a billing lot) |
| base-lot count | **1** (single base lot — see multi-lot note below) |

Chosen because it is the richest of the three sampled null-billing condos: it carries a non-null
`condo_name` (a real, human-identifiable Manhattan condo at 128 Hester Street), so the fixture
exercises the maximal field set. The other two sampled null-billing condos (`condo_key` 100355 and
101962) carry no `condo_name` and are captured in the listing below as the minimal-shape variant.

**"Prefer 2+ base lots" — documented negative:** none of the 28 null-billing condos is multi-lot.
`count(condo_key)` and `count(distinct condo_key)` over `condo_billing_bbl IS NULL` are **both 28**
(captured below), so every null-billing condo contributes exactly one base-lot row. A 2+-base-lot
null-billing fixture does not exist in the current data; the chosen fixture is single-base-lot by
necessity, not by selection.

---

## Capture (a) — listing: null-billing condos

- **Request URL (effective):**
  `https://data.cityofnewyork.us/resource/p8u6-a6it.json?$where=condo_billing_bbl+IS+NULL&$order=condo_key&$limit=3`
  (constructed via `curl -G --data-urlencode '$where=condo_billing_bbl IS NULL' --data-urlencode
  '$order=condo_key' --data-urlencode '$limit=3'`; `$order=condo_key` added for a deterministic,
  reproducible sample.)
- **UTC at request:** 2026-09-19T02:06:42Z
- **HTTP status:** 200
- **Content-Type:** `application/json;charset=utf-8`
- **Last-Modified (response header):** `Tue, 01 Sep 2026 14:05:56 GMT`
- **Body size:** 599 bytes; ends with `}]\n` (trailing newline present)
- **Raw body (VERBATIM — element separator is `\n,` exactly as returned by SODA):**

```json
[{"condo_base_boro":"1","condo_base_block":"1003","condo_base_lot":"1","condo_base_bbl":"1010030001","condo_base_bbl_key":"1010030001100355","condo_key":"100355","condo_number":"355"}
,{"condo_base_boro":"1","condo_base_block":"1945","condo_base_lot":"29","condo_base_bbl":"1019450029","condo_base_bbl_key":"1019450029101962","condo_key":"101962","condo_number":"1962"}
,{"condo_base_boro":"1","condo_base_block":"303","condo_base_lot":"19","condo_base_bbl":"1003030019","condo_base_bbl_key":"1003030019103343","condo_key":"103343","condo_number":"3343","condo_name":"THE 128 HESTER STREET CONDO"}]
```

**Byte-shape observations (load-bearing for fixtures):**
- Every record **omits** `condo_billing_bbl` entirely — the key is absent, NOT present with a
  `null` value. This is SODA's documented null-field omission per record.
- `condo_name` is present only on the third record (103343); records 100355 and 101962 omit it too
  (also null → omitted). So a null-billing record may carry either 7 keys (no name) or 8 keys
  (with name); it never carries `condo_billing_bbl`.
- All BBL fields are zero-padded 10-digit **strings** (text type), e.g. `"1003030019"` — they match
  `^\d{10}$` with no trailing `.0000` (contrast the PLUTO number-typed `bbl` trap).

---

## Capture (b) — resolver fallback: `?condo_key=103343`

This is the exact step-4a fallback query the resolver issues when the billing-BBL path is empty
but a `condo_key`/`condo_number` is known (algorithm in `condo-base-lot-resolution-sources.md`
§7 step 4a; contract-test fixture C6).

- **Request URL (effective):**
  `https://data.cityofnewyork.us/resource/p8u6-a6it.json?condo_key=103343`
- **UTC at request:** 2026-09-19T02:09:46Z (identical body returned at an earlier probe
  2026-09-19T02:07:40Z)
- **HTTP status:** 200
- **Content-Type:** `application/json;charset=utf-8`
- **Last-Modified (response header):** `Tue, 01 Sep 2026 14:05:56 GMT`
- **X-SODA2-Truth-Last-Modified (response header):** `Tue, 01 Sep 2026 14:05:56 GMT`
- **Body size:** 229 bytes; ends with `}]\n` (trailing newline present)
- **Raw body (VERBATIM):**

```json
[{"condo_base_boro":"1","condo_base_block":"303","condo_base_lot":"19","condo_base_bbl":"1003030019","condo_base_bbl_key":"1003030019103343","condo_key":"103343","condo_number":"3343","condo_name":"THE 128 HESTER STREET CONDO"}]
```

**Result:** the fallback query returns the condo's base lot (`1003030019`) even though the
billing-BBL path would be empty — proving step 4a resolves a null-billing condo to its base land
lot. One row → one base lot. `condo_billing_bbl` is again absent.

**Independent freshness cross-check:** the response header `X-SODA2-Truth-Last-Modified`
(`Tue, 01 Sep 2026 14:05:56 GMT`) equals the dataset metadata `rowsUpdatedAt` unix value
(1788271556 = 2026-09-01T14:05:56Z) captured in (c) — the per-request header and the dataset
metadata agree on the same data-truth moment.

---

## Capture (c) — dataset metadata `rowsUpdatedAt` at capture time

- **Request URL:** `https://data.cityofnewyork.us/api/views/p8u6-a6it.json`
- **UTC at request:** 2026-09-19T02:06:46Z
- **HTTP status:** 200
- **Content-Type:** `application/json; charset=utf-8`
- **Raw timestamp integers (VERBATIM, read directly from the JSON — not summarizer-paraphrased):**

```
rowsUpdatedAt:    1788271556   ->  2026-09-01T14:05:56Z   (data-truth freshness signal)
createdAt:        1734102769   ->  2024-12-13T15:12:49Z
publicationDate:  1769016506   ->  2026-01-21T17:28:26Z
viewLastModified: 1789740270   ->  2026-09-18T14:04:30Z   (view/metadata change, not a row refresh)
```

**Consistency vs DB-002:** `rowsUpdatedAt` = **1788271556** is IDENTICAL to the value recorded in
`condo-base-lot-resolution-sources.md` §3.1 (2026-09-01T14:05:56Z). The row data has not been
refreshed since the DB-002 capture, so these fixtures are drawn from the same dataset version as
the rest of the DB-002 research. (`viewLastModified` advanced to 2026-09-18, i.e. a
metadata/view-definition edit only, not a data reload.)

---

## Supporting capture — null-billing population re-verification

Confirms the DB-002 §3.4 count of 28 is unchanged and establishes the single-base-lot fact.

| Request (`p8u6-a6it.json`, `$where=condo_billing_bbl IS NULL`) | UTC at request | HTTP | Raw body |
|---|---|---|---|
| `$select=count(condo_key)` | 2026-09-19T02:07:52Z | 200 | `[{"count_condo_key":"28"}]` |
| `$select=count(distinct condo_key)` | 2026-09-19T02:08:01Z | 200 | `[{"count_distinct_condo_key":"28"}]` |

Rows == distinct keys == **28** ⇒ every null-billing condo is single-base-lot (no multi-lot
null-billing condo exists in this dataset version).

---

## No-match / negative controls (from DB-002 §3.4, not re-run here)

For completeness, DB-002 already established the deterministic empty-result behavior that a
resolver relies on: `?condo_billing_bbl=<nonexistent 7501-series>` → `[]`, and
`?condo_billing_bbl=<a normal land lot>` → `[]`. The null-billing path is the complement of these:
the billing-BBL query is empty because the field is absent, so the resolver MUST branch to the
`condo_key` fallback (capture b) rather than treating `[]` as "not a condo".

---

## Field-for-field comparison vs the resolver's labeled synthetic fixture (3-sentence note)

*(No committed synthetic condo-resolver fixture exists in this checkout — the connector is a
future ledger task per DB-002 §11 — so the comparison is against the labeled reference shape in
`condo-base-lot-resolution-sources.md`: the 9-column schema (§3.2) and the has-billing worked
example (§3.3).)*

The chosen real null-billing record is field-for-field identical to the labeled synthetic base-lot
shape on every base-lot linkage field — `condo_base_boro/block/lot/bbl`, `condo_base_bbl_key`,
`condo_key`, `condo_number` are all present and correctly typed as zero-padded strings (BBL matches
`^\d{10}$`) — differing only in the two nullable fields. The decisive difference is that
`condo_billing_bbl` is **absent from the wire bytes**, not present as `null`, so a synthetic
fixture that models the null-billing case as `{"condo_billing_bbl": null, ...}` would be
byte-INFAITHFUL: the resolver must treat **key-absence** (not an explicit JSON null) as the
"no billing lot assigned" signal. Correspondingly `condo_name` is present here (103343) but absent
on the other two null-billing condos (100355, 101962), so the same key-absence rule the resolver
applies to `condo_billing_bbl` also governs `condo_name`, and any fixture or parser must tolerate a
7-or-8-key object rather than assuming a fixed 9-key shape.

---

## Contract-test pack impact

- **Fixture C6 (null-billing fallback)** — now pinnable with concrete bytes:
  - request: `p8u6-a6it?condo_key=103343`
  - assertion: 1 row; `condo_base_bbl == "1003030019"`; `condo_key == "103343"`;
    **`"condo_billing_bbl"` key NOT present** in the record.
- **New assertion recommended for C7 (BBL string shape) / C10 (schema drift):** assert on
  **key presence**, not value nullness — `condo_billing_bbl` absent ⇒ null-billing;
  parser must not KeyError.
- Store the two raw bodies above verbatim (599-byte listing; 229-byte single-record) with a
  trailing `\n`, plus the `rowsUpdatedAt` integer 1788271556, as the offline fixture triple.

---

## Provenance register (all captured 2026-09-18 local / 2026-09-19 UTC)

| Ref | Official URL | HTTP | Used for |
|---|---|---|---|
| N1 | `https://data.cityofnewyork.us/resource/p8u6-a6it.json?$where=condo_billing_bbl+IS+NULL&$order=condo_key&$limit=3` | 200 | listing of null-billing condos (capture a) |
| N2 | `https://data.cityofnewyork.us/resource/p8u6-a6it.json?condo_key=103343` | 200 | resolver step-4a fallback for chosen condo (capture b) |
| N3 | `https://data.cityofnewyork.us/api/views/p8u6-a6it.json` | 200 | dataset metadata / `rowsUpdatedAt` (capture c) |
| N4 | `https://data.cityofnewyork.us/resource/p8u6-a6it.json?$select=count(condo_key)&$where=condo_billing_bbl+IS+NULL` | 200 | null-billing row count = 28 |
| N5 | `https://data.cityofnewyork.us/resource/p8u6-a6it.json?$select=count(distinct+condo_key)&$where=condo_billing_bbl+IS+NULL` | 200 | distinct null-billing keys = 28 |

Related prior research: `docs/research/condo-base-lot-resolution-sources.md` (DB-002; primary
Condominiums-table analysis, §3.4 = the gap this document closes).

---

## Limitations / flags

- Single dataset version: `rowsUpdatedAt` 1788271556 (2026-09-01) — unchanged since DB-002; these
  fixtures share that version. Re-pin if a connector ingests after a row refresh.
- Base-lot reality of `1003030019` (that it is a live, zonable land lot) was NOT re-verified here
  (out of this bounded task's scope); DB-002's loop-closure method (ZTLDB `fdkv-4t4z?bbl=...`)
  would confirm it downstream.
- This worktree is on a stale branch base (`candidate/D-024-mrl-option-b`) that predates the DB-002
  doc; this file is self-contained and references DB-002 by path for the orchestrator to integrate
  onto the correct head.
- No blockers.

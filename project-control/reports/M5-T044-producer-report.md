# M5-T044 — producer report

**Task:** Condo resolver pre-wiring hardening (DB-029 a, d–i) — ASCII-fullmatch guards +
canonical-value URL interpolation + per-query post-response stamps + documented validation code +
honest condo_key input identity + error-branch / unit-path / drift-note test coverage.
**Producer:** backend-engineer. **Directive:** D-066-R001 (code-graph navigation block).
**Base:** the ACCEPTED M5-T042 module at HEAD `fe06f13a`; this pass is the hardening diff on top of it.
**Scope:** the three allowed-path files only. Registry record + official null-billing fixture + any
consumer wiring stay wiring-era (DB-029 b/c) — OUT of scope. Module stays a LEAF.

## What changed (file references, not verbatim)

- `services/api/app/connectors/dtm_condo_soda.py` (+128 / −35 vs HEAD). Hardening only; the verified
  billing / unit / condo_key resolution paths and the honest fail-closed contract are unchanged.
- `services/api/tests/connectors/test_dtm_condo_soda.py` (+343 vs HEAD). Adds the M5-T044 coverage
  block (`:495–771`), tests grouped by DB-029 letter (a, d–i). Suite grew 26 → **54 tests**.

## Item → implementation → test (DB-029 a, d–i)

- **(a) G5 F1+F2 must-fix — ASCII fullmatch + canonical URL + response-side guard.**
  - `_STRICT_BBL_RE = re.compile(r"\d{10}", re.ASCII)` and `_CONDO_KEY_RE = …r"\d{6}", re.ASCII` with
    `.fullmatch` (`dtm_condo_soda.py:193`, `:196`); the retired `$`-anchor / bare-`\d` shapes are gone,
    so trailing-newline, trailing-space, and Unicode-digit inputs all fail closed. Guards applied in
    `classify_lot` (`:357`), `resolve_by_condo_key` input (`:785`), the response-side condo_key guard
    (`:708`), and the response-side base-BBL guard `_collect_base_lots` (`:514`).
  - CANONICAL value interpolated (never raw input): `canonical_bbl = normalize_bbl(bbl).canonical`
    (`:619`) is used at all four URL f-string sites — billing (`:633`), unit (`:674`), condo_key
    expansion (`:717`), and direct condo_key (`:795`).
  - F3 negatives (typed refusal, ZERO transport calls via `_never_called`):
    `test_a_bbl_guard_rejects_anchor_leak_no_transport` (`test:508`),
    `test_a_condo_key_guard_rejects_anchor_leak_no_transport` (`:520`),
    `test_a_url_carries_canonical_value` (`:525`),
    `test_a_unit_and_expansion_urls_carry_canonical_value` (`:537`),
    `test_a_response_base_bbl_leaky_shape_rejected` (`:569`, AS-2: Unicode / newline / space → drift).
- **(d) G3 #1 — per-query POST-response `retrieved_at`** stamped after each successful `_fetch_rows`
  (`:638` billing, `:676` unit, `:721` expansion); the pluto_soda post-response precedent.
  `test_d_two_query_resolve_has_distinct_post_response_timestamps` (`test:576`) drives an advancing
  fake clock and asserts two distinct stamps + result-level = final retrieval (AS-3).
- **(e) G3 #2 — documented validation code.** `classify_lot` raises `BBLValidationError("non_numeric", …)`
  (`:358`); `resolve_by_condo_key` raises `"invalid_component"` (`:787`) — both from the `bbl.py`
  vocabulary; the ad-hoc `wrong_shape` is gone. `test_e_classify_lot_uses_documented_validation_code`
  (`test:600`) asserts `code == "non_numeric"`, in `DOCUMENTED_BBL_CODES`, and `!= "wrong_shape"` (AS-4).
- **(f) G3 #3 / G4 #5 — honest input identity.** New `INPUT_KIND_BBL` / `INPUT_KIND_CONDO_KEY`
  (`:142–143`) and `CondoBaseLotResult.input_kind` (`:299`); `resolve` results carry `input_kind=bbl`,
  condo_key results carry `input_kind=condo_key` + `lot_class=None` (no lot number) instead of
  overloading `input_bbl`/`lot_class`. Module-internal rename — docstrings, `__all__`, and tests moved
  together (no consumer exists). `test_f_*` (`test:609`, `:621`, `:634`) cover resolved / unresolved /
  BBL identities (AS-4).
- **(g) G3 #4 / G4 #2 — dtm-local error branches** (offline stubs, `_AlwaysTransport`): 400-drift vs
  400-other split, non-JSON / non-array / non-object body guards, terminal 429 / timeout / network
  errors — `test_g_*` (`test:645–701`), incl. `transport.calls >= 2` proving the retry budget was spent
  (AS-5).
- **(h) G4 #3 — unit-path branches:** unit-empty → UNRESOLVED single query
  (`test_h_unit_empty_is_unresolved_single_query`, `test:705`); unit-row-without-condo_key → direct
  base lot, NO expansion query, incompleteness note surfaced
  (`test_h_unit_without_condo_key_returns_direct_lot_no_expansion`, `:715`) (AS-6).
- **(i) G4 #4 — runtime drift-note paths:** unknown-columns advisory note (`test_i_…`, `:740`) and
  multiple-condo-key/number notes with ambiguous identifiers surfaced (not guessed) → `condo_key`/
  `condo_number` left `None` (`:756`) (AS-6).
- **(j) OPTIONAL `$limit`** — deliberately NOT added this pass: adding it would change every request
  URL shape and churn the canonical-URL exactness assertions (`test_a_url_carries_canonical_value`) for
  no correctness gain on a leaf whose result set is small and never collapsed. Surfaced here as an
  available defense-in-depth for the wiring packet, not silently dropped (D-069).

## Evidence handoff — WORKER-RUN vs SUPERVISOR/ORCHESTRATOR (kept explicitly separate)

This pass repairs the evidence handoff only; the implementation is UNCHANGED from the prior
submission (both code files are byte-identical to the prior submission — no code edit this pass). The
hardening lives in this worktree's WORKING TREE on top of the accepted M5-T042 module at HEAD
`fe06f13a`; results below are **working-tree validation of uncommitted changes**, not committed-head
evidence.

### Worker-run validation (this worktree; evidence-handoff repair pass)

All four documented commands re-run so the transcript records the correct cwd — this is the repair:
the prior transcripts did not record `services/api` as cwd. The supervisor RETAINS those prior failed
transcripts as distinct executions and adds these worker-run ones alongside them.

- `python -m ruff check .` — cwd `services/api` → **All checks passed!** (exit 0)
- `python -m pytest tests/connectors/test_dtm_condo_soda.py -q` — cwd `services/api` → **54 passed** (exit 0)
- `python -m pytest tests/connectors -q` — cwd `services/api` → **880 passed** (exit 0; no regression)
- `python tools/modularity_check.py --check` — cwd **repo root** → **selected 444 files; failures 0;
  warnings 22** (exit 0). Code is unchanged, so the verified modularity pass is PRESERVED; this re-run
  only re-confirms it. `dtm_condo_soda.py` sits at the `review_signal` (justification) tier — see the
  cohesion note.

CWD discipline: the first three run from `services/api` (the suites do not collect from repo root — a
known invocation artifact); the modularity check runs from repo root. Only the three allowed-path
files were touched.

### Supervisor / orchestrator responsibilities (NOT worker results — do not conflate)

- **Patch collection (priority over report text and unrelated listings):** collect the change as TWO
  separately-bounded patches so every hunk reaches the reviewer — the connector diff
  (`services/api/app/connectors/dtm_condo_soda.py`, +128/−35 vs `fe06f13a`) and the test diff
  (`services/api/tests/connectors/test_dtm_condo_soda.py`, +343 vs `fe06f13a`). Both full diffs take
  priority over this report's prose and over any repository listing.
- **Committed-head CI (AS-8) and gates** (G0 recorded at contract; G2/G3/G4/G5) are orchestrator-
  captured after commit/push (evidence-capture division of labor, `.claude/rules/project-control.md`).
  No CI or gate pass is claimed here.
- **Digest-bound full-file sha256** (LF-normalized) are supervisor-supplied at commit ("probe cannot
  self-bind") — see the digest table below.

## Leaf invariant / zero production consumer (AS-7 / D-066-R001) — bounded evidence

Bounded native-tool grep for `dtm_condo_soda` over `**/*.py` returns EXACTLY two files — the module
and its own test — i.e. ZERO production-consumer imports:

- `services/api/app/connectors/dtm_condo_soda.py` (the module itself)
- `services/api/tests/connectors/test_dtm_condo_soda.py` (its own test)

A wider grep (`dtm_condo_soda|p8u6-a6it|eguu-7ie3` over json/md/toml/cfg/py/ts/tsx) adds only
docs/reports/tasks/research references (the M5-T042 / M5-T044 control records, the DB-002 research
doc, `docs/DISCOVERY_BACKLOG.md`) — no route, no `source_registry` record, no pipeline/import wiring.
The module stays a LEAF; no ArcGIS failover, no zoning logic. Lane stays disjoint from M5-T043 (no
`rules/**`, `spatial/**`, or `apps/web/**` touched).

## Digest-bound evidence (supervisor-supplied at commit)

Per the "probe cannot self-bind" rule the producer does not fabricate a digest. The authoritative
sha256 (LF-normalized) full-file bindings are supplied by the supervisor/orchestrator at commit.

| File | Working-tree lines | sha256 (LF-normalized) |
|---|---|---|
| `services/api/app/connectors/dtm_condo_soda.py` | 910 | supervisor-supplied at commit |
| `services/api/tests/connectors/test_dtm_condo_soda.py` | 771 | supervisor-supplied at commit |

## Cohesion / modularity note (justification tier — code-architecture rule §6)

The module is a single cohesive responsibility: deterministic condo→base-lot resolution (lot
classification + billing / unit / condo_key query paths + one typed result + the shared SODA error
taxonomy). The hardening added ASCII guards, canonical interpolation, per-query stamps, and the
`input_kind` vocabulary, growing it to **910 lines** — now above the 750 justification threshold, under
the 1,000 hard threshold. The size is docstring/comment-heavy by the provenance and legal-boundary
discipline this legally-sensitive connector requires (every guard cites its research clause and the
divergent-zoning boundary), and is comparable to the accepted sibling SODA connectors (`pluto_soda.py`,
`ztldb_soda.py`). No responsibility mixing; keep as one module — a split would fragment one query-family
and its guards across files for no cohesion gain. Justification recorded here per §6.

## Deferred to the wiring packet (out of scope; discovery routing D-069)

- `source_registry` record + live `/api/views` freshness fetch (`RESEARCH_OBSERVED_ROWS_UPDATED_AT`
  carries the 2026-09-18 observed values as an injectable provenance hint).
- Official null-billing `condo_key` fixture (research embeds only the aggregate count 28; the mechanism
  is proven with real `condo_key=301313` + a labeled synthetic — DB-029 c, live-era).
- ArcGIS failover (research §5), PLUTO `appbbl` optional cross-check flag (§6.1), property-lookup /
  ZTLDB pipeline wiring, and the divergent-zoning qualified-human surface (§7 step 6).
- Optional `$limit` defense-in-depth (item j above).

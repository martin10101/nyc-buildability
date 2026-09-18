# M5-T039 — producer report (v6): revised evidence submission — source-anchored named-street override matcher

Producer: backend-engineer. Run lineage: persistent3-local-04-m5t039 (loop-3, wt-m5t039). Date: 2026-09-18.
Authorized stage: in_progress. Supersedes v5. This revision is an **evidence-and-integrity rework**,
not a behavior change for the two real rows: it (a) adds a construction-time, tested guard that every
**normalized structured row field and disposition is validated against the pinned source text — beyond
quote-substring presence** — and (b) reshapes the evidence into a bounded, digest-bound, independently
inspectable bundle with a clear worker-reported vs. independently-reproduced split. All changes stay
inside the five allowed paths; no consumer, controller-config, task-state, or unrelated lint file was
touched.

## 0. Bottom line

- **New source-anchoring guard (this revision).** The matcher previously validated only that each
  structured block's `verbatim_source_quote` is a substring of the digest-covered `verbatim_excerpt`
  (quote-substring presence). It now ALSO fails closed unless every normalized structured row field
  (borough, community district, street name, both frontage endpoints) and the block dispositions trace
  to the pinned source text (§3). A row whose fields diverge from the source (a wrong borough, an
  invented cross street, an unrecognized disposition, an out-of-source alternate-width district) is
  rejected at construction. This closes the "beyond quote substring presence" gap.
- **Behavior for the two real rows is unchanged.** They still locate and return INDETERMINATE with full
  provenance (the mapped-public-park / G6-Q1 conservative refusal). The guard passes for the repaired
  snapshot because each field is anchored — proven independently in §3.2.
- **Self-checks green (worker-reported).** All four documented commands pass in this worktree at the
  packet-bound cwds; **40 passed** (was 36; +4 source-tracing tests), ruff clean, modularity failures 0
  with `named_street_override.py` not flagged, both snapshot copies byte-identical (§7A).
- **Evidence is bounded and digest-bound** (§6): each artifact is named by path, line count, and digest
  binding; the snapshot digest is self-verifying; the code/test digests are for the supervisor to stamp
  at the frozen head. Load-bearing spans are embedded inline so a reviewer can inspect them regardless
  of checkout state.
- **Independent reproduction and CI/gates are left to the supervisor/orchestrator** (§7B, §7C). Earlier
  failing transcripts are preserved and attributed to a **different execution context** (§7D), not to
  the current state.

## 1. Phase 0 — source repair (both snapshot copies) — unchanged from v5, restated for completeness

Canonical `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json` and packaged
`services/api/app/_zr_snapshots/v1/zr-12-10.snapshot.json` carry the amended 3/26/2026 "street, wide"
verbatim text (flat 75-ft test + C5-3/C6-4/C6-6 alternate-width + 70-ft connector), the two
named-street designations, and the "street, narrow" text — transcribed byte-exact from the accepted,
G1-reviewed M4-T018 capture (§4), no network, no other source. `content_digest_sha256` is recomputed
as `sha256(verbatim_excerpt)`; `section_last_amended` corrected to `2026-03-26`; a `provenance_chain`
records the transcription source and the official-capture channel (canonical HTML, 1,316,658 bytes,
sha256 `4a75e22f…`, retrieved 2026-09-14). The two copies are kept byte-identical by
`python scripts/sync_zr_snapshots.py` and the `test_bundled_copy_matches_canonical_or_absent` guard.

## 2. Phase 1 — the matcher (`named_street_override.py`) — public surface

Deterministic, stdlib + existing-deps only, 513 lines. Public surface unchanged from v5:
`OverrideQuery`, `MatchStatus` (`MATCHED_OVERRIDE | NOT_MATCHED | INDETERMINATE`, fails closed to
INDETERMINATE), `MatchResult`, `OverrideProvenance`, `AlternateWidthResult`,
`NamedStreetOverrideMatcher(snapshot)` with `.match(query)` /
`.classify_alternate_width_district(district)`, and `load_default_matcher()`. Documented normalization
(casefold + whitespace-collapse; exact, never fuzzy, no abbreviation expansion; CD parsed from exactly
one integer run; district uppercased/whitespace-stripped) and decision logic are as in v5 §2 — the
located-row disposition is data-driven from the snapshot block's `disposition_when_located` (for the
two real rows: `indeterminate`).

## 3. Structured-field & disposition source validation (the core of this revision)

### 3.1 The gap being closed

The reviewer concern: the v5 integrity check proved only **quote presence** — that each block's
`verbatim_source_quote` is a substring of the digest-covered `verbatim_excerpt`. It did **not** prove
that the *structured decomposition* of that quote into typed row fields is faithful to the source. This
matters because the structured fields are **not** literal substrings of the source: the source says
"…Broadway between West **94th** and West **97th** Streets…", and the row decomposes that into
`frontage_from = "West 94th Street"`, `frontage_to = "West 97th Street"`. A quote-substring check
cannot catch a divergent or invented structured field.

### 3.2 How each structured field is now validated against the pinned source

Two layers, both reproducible:

**Layer A — provenance (origin of the values).** The structured rows are transcribed verbatim from the
accepted, G1-reviewed **M4-T018 §3.1** build-input specification table (embedded in §4.2), which itself
derived them from the §1.3 verbatim capture. So the field values are not this task's invention; they
are an accepted upstream artifact.

**Layer B — mechanical, tested cross-check (this revision).** `NamedStreetOverrideMatcher.__init__` now
calls `_validate_against_source()`, which fails closed unless each normalized field is *anchored* in the
block's own `verbatim_source_quote`. `_anchored_in` accepts a field if its normalized form appears in
the source, or if its distinctive core (with a single trailing generic street-type word removed — the
snapshot spells types in full, so "West 94th Street" → core "west 94th") appears. The community district
is checked against the source's own phrasing ("Community District N"); each applicable alternate-width
district must appear in that block's quote; the located-row disposition must be a recognized value.

Per-field anchoring for the two real rows (each field → source phrase it anchors to, all in the named
block's `verbatim_source_quote`):

| Row | Field | Value | Anchored to (source phrase) | Anchor form |
|---|---|---|---|---|
| broadway-cd7-w94-w97 | borough | Manhattan | "…in the Borough of **Manhattan**…" | full |
| broadway-cd7-w94-w97 | community_district | 7 | "In **Community District 7** in the Borough…" | full ("community district 7") |
| broadway-cd7-w94-w97 | street_name | Broadway | "…the roadways of **Broadway** between…" | full |
| broadway-cd7-w94-w97 | frontage_from | West 94th Street | "…between **West 94th** and West 97th Streets…" | core ("west 94th", type word dropped) |
| broadway-cd7-w94-w97 | frontage_to | West 97th Street | "…West 94th and **West 97th** Streets…" | core ("west 97th") |
| allen-st-cd3-rivington-delancey | borough | Manhattan | "…in the Borough of **Manhattan**…" | full |
| allen-st-cd3-rivington-delancey | community_district | 3 | "…in **Community District 3** in the Borough…" | full |
| allen-st-cd3-rivington-delancey | street_name | Allen Street | "…the roadways of **Allen Street** between…" | full |
| allen-st-cd3-rivington-delancey | frontage_from | Rivington Street | "…between **Rivington** and Delancey Streets…" | core ("rivington") |
| allen-st-cd3-rivington-delancey | frontage_to | Delancey Street | "…Rivington and **Delancey** Streets…" | core ("delancey") |

Alternate-width districts C5-3, C6-4, C6-6 each appear verbatim in the alternate-width block quote
("In C5-3, C6-4 or C6-6 Districts…"). Additionally, `test_structured_row_fields_trace_to_source_quote`
proves an **order-faithful reconstruction** — `"{street} between {from-core} and {to-core} Streets"` —
is a literal substring of the source for both real rows, catching a swapped/mis-paired endpoint that
pure token-presence would miss. That test normalizes independently (a local `_norm`), so it is not
tautological with the module's own `_anchored_in`.

### 3.3 Embedded code (load-bearing span, `named_street_override.py`)

Module-level helper + constructor guard (verbatim; lines ~133–147, 236–241, 269–317):

```python
_STREET_TYPE_WORDS = frozenset({"street", "streets", "avenue", "avenues"})
_ALLOWED_DISPOSITIONS = frozenset({"indeterminate", "matched_override"})


def _anchored_in(field: object, normalized_source: str) -> bool:
    core = _collapse(field)
    if not core:
        return False
    if core in normalized_source:
        return True
    head, _, tail = core.rpartition(" ")
    if head and tail in _STREET_TYPE_WORDS and head in normalized_source:
        return True
    return False

# ... in __init__, after self._rows is built:
        self._validate_against_source()

    def _validate_against_source(self) -> None:
        named_source = _collapse(self._named_block.get("verbatim_source_quote", ""))
        disposition = self._named_block.get("disposition_when_located", "indeterminate")
        if disposition not in _ALLOWED_DISPOSITIONS:
            raise NamedStreetOverrideError(...)          # unrecognized disposition
        for row in self._rows:
            field_checks = {
                "borough": _anchored_in(row.borough, named_source),
                "community_district": (
                    f"community district {row.community_district}" in named_source),
                "street_name": _anchored_in(row.street_name, named_source),
                "frontage_from": _anchored_in(row.frontage_from, named_source),
                "frontage_to": _anchored_in(row.frontage_to, named_source),
            }
            unanchored = sorted(name for name, ok in field_checks.items() if not ok)
            if unanchored:
                raise NamedStreetOverrideError(...)      # field not source-anchored
        alt_source = _collapse(self._alt_block.get("verbatim_source_quote", ""))
        for district in self._alt_block.get("applicable_districts", []):
            if _collapse(district) not in alt_source:
                raise NamedStreetOverrideError(...)      # district absent from source
```

### 3.4 The four tests that exercise it (`test_named_street_override.py`)

- `test_structured_row_fields_trace_to_source_quote` — over the REAL snapshot: each field of both real
  rows anchors in the source by an independent normalization; the rows equal the M4-T018 §3.1 spec
  exactly; the order-faithful reconstruction is a literal substring.
- `test_structured_field_divergent_from_source_fails_closed` — a synthetic snapshot whose block quote
  IS present and digest-covered (so the old check passes) but whose row borough diverges ("Brooklyn")
  → `NamedStreetOverrideError`.
- `test_alternate_width_district_absent_from_source_fails_closed` — an applicable district ("C9-9") not
  in the alt quote → `NamedStreetOverrideError`.
- `test_unrecognized_disposition_fails_closed` — `disposition_when_located = "auto_match"` → raises
  (no silent coercion to INDETERMINATE).

## 4. Accepted M4-T018 capture excerpts (the pinned source)

Source record: `project-control/reports/M4-T018-zr1210-wide-street-reconciliation.md` (accepted,
G1-reviewed). Official channel byte-pin: canonical HTML, 1,316,658 bytes, sha256
`4a75e22f22a736beea6daf52c57cca3ce66f9cacc4244807964577141216e0a4`, retrieved 2026-09-14, shortlink
`/node/18523`; print/PDF completeness channel 504'd twice (disclosed fallback).

### 4.1 §1.3 "street, wide" verbatim (paragraph 2 — the named-street designations)

> "In Community District 7 in the Borough of Manhattan, the roadways of Broadway between West 94th and
> West 97th Streets and in Community District 3 in the Borough of Manhattan, the roadways of Allen
> Street between Rivington and Delancey Streets, which are separated by mapped public park shall each be
> considered a wide street."

This is byte-identical to the `named_street_overrides.verbatim_source_quote` in the snapshot (§5), which
is a substring of the digest-covered `verbatim_excerpt`.

### 4.2 §3.1 named-street override build-input spec (origin of the structured fields)

| Field | Row 1 | Row 2 |
|---|---|---|
| `borough` | Manhattan | Manhattan |
| `community_district` | CD 7 | CD 3 |
| `street_name` | Broadway | Allen Street |
| `frontage_from` | West 94th Street | Rivington Street |
| `frontage_to` | West 97th Street | Delancey Street |
| `roadway_note` | (none stated) | "which are separated by mapped public park" |

The snapshot's structured `rows` equal this table exactly (asserted by
`test_structured_row_fields_trace_to_source_quote`). M4-T018 §3.1 also records the **open grammatical
scope** of the "separated by mapped public park" qualifier — the basis for the INDETERMINATE
disposition (G6-Q1, §8). M4-T018 §3.2 records the C5-3/C6-4/C6-6 "**may** be considered" permissive
reading (G6-Q2), the basis for `professional_review_required`.

## 5. Snapshot `named_street_overrides` block (both copies byte-identical)

```json
"named_street_overrides": {
  "provision_id": "zr-12-10-named-street-wide",
  "section_anchor": "ZR 12-10, definition 'street, wide', paragraph 2",
  "node_anchor": "/node/21683",
  "disposition_when_located": "indeterminate",
  "open_legal_questions": ["G6-Q1-park-qualifier-scope"],
  "verbatim_source_quote": "In Community District 7 in the Borough of Manhattan, the roadways of Broadway between West 94th and West 97th Streets and in Community District 3 in the Borough of Manhattan, the roadways of Allen Street between Rivington and Delancey Streets, which are separated by mapped public park shall each be considered a wide street.",
  "rows": [
    {"row_id": "broadway-cd7-w94-w97", "borough": "Manhattan", "community_district": 7,
     "street_name": "Broadway", "frontage_from": "West 94th Street", "frontage_to": "West 97th Street"},
    {"row_id": "allen-st-cd3-rivington-delancey", "borough": "Manhattan", "community_district": 3,
     "street_name": "Allen Street", "frontage_from": "Rivington Street", "frontage_to": "Delancey Street"}
  ]
}
```

## 6. Digest-bound evidence bundle (bounded contents + digest binding)

| Artifact | Path | Lines | Digest binding |
|---|---|---|---|
| Matcher (complete) | `services/api/app/rules/named_street_override.py` | 513 | file sha256 — **supervisor to stamp at frozen head**; load-bearing span embedded §3.3 |
| Tests (complete) | `services/api/tests/rules/test_named_street_override.py` | 615 | file sha256 — **supervisor to stamp**; new tests summarized §3.4 |
| Snapshot (canonical) | `docs/research/zr-snapshots/v1/zr-12-10.snapshot.json` | 95 | **`content_digest_sha256 = 23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`** (self-verifying = `sha256(verbatim_excerpt)`, enforced by loader + `test_phase0_digest_self_consistent`) |
| Snapshot (packaged) | `services/api/app/_zr_snapshots/v1/zr-12-10.snapshot.json` | 95 | **byte-identical to canonical** — proven by `test_bundled_copy_matches_canonical_or_absent` (passed in §7A) and re-established by `sync_zr_snapshots.py`; supervisor may reproduce byte-equality |
| M4-T018 capture | `project-control/reports/M4-T018-zr1210-wide-street-reconciliation.md` | — | official channel sha256 `4a75e22f…` (M4-T018 F2); excerpts §4 |

Byte-equality of the two snapshot copies is a **documented-command-backed** fact (the passing pytest
run asserts `bundled.read_bytes() == canonical.read_bytes()`), not a claim. The supervisor is requested
to stamp the two code-file sha256 digests at the frozen head to complete the digest binding (§7B).

## 7. Checks — worker-reported vs. independently reproduced

### 7A. Worker-reported self-checks (this worktree `wt-m5t039`; verbatim outcomes)

Run at the packet-bound cwds (sync/ruff/pytest from `services/api`; modularity from repo root); nothing
chained onto a documented command.

- `python scripts/sync_zr_snapshots.py` (cwd `services/api`) → 14 snapshots `synced …` incl.
  `zr-12-10.snapshot.json` → exit 0.
- `python -m ruff check .` (cwd `services/api`) → `All checks passed!` → exit 0.
- `python -m pytest tests/rules/test_named_street_override.py -q` (cwd `services/api`) →
  `40 passed in 0.36s` → exit 0.
- `python tools/modularity_check.py --check` (cwd repo root) →
  `selected 442 files; failures 0; warnings 19` → exit 0. All 19 warnings are pre-existing files
  outside this task's scope; `named_street_override.py` is **not** among them.

These are **worker-reported** (this producer executed them). They are not a substitute for independent
reproduction or CI.

### 7B. Independent reproduction — RESERVED for the supervisor

The supervisor is requested to **independently reproduce** the same four commands with the **explicit
`services/api` cwd** (sync, ruff, named-street pytest) and **repository root** (modularity), and to
stamp the two code-file sha256 digests (§6). Record the outcomes here as the independently-reproduced
column. This split keeps producer-run and independent evidence distinct.

### 7C. CI + gates — PENDING the orchestrator

- **AS-6 / CI:** green on the pushed head — orchestrator captures after push (not claimed here).
- **Gates G0, G2, G3, G4, G5:** recorded by the orchestrator against the frozen head after independent
  reproduction; reviewer_agents unchanged (code-reviewer, qa-engineer, security-reviewer,
  directive-compliance-verifier). Not self-attested.

### 7D. Preserved different-context transcripts (not current-state failures)

Any earlier transcript that showed the named-street pytest **failing** is an artifact of a **different
execution context**, preserved and attributed as such, NOT superseded silently:

- **Wrong-cwd invocation.** The rules suite run from the **repo root** fails collection with
  `ModuleNotFoundError: No module named 'app'` — a documented invocation artifact (CODING_RULES;
  it has faked a red before). The current-state proof (§7A) is the run from the `services/api` cwd.
- **Pre-Phase-0 runs.** Runs from before the Phase-0 source repair (the run-01/03 consolidated blocker
  context) predate the repaired snapshot and are not representative of the current tree.

The supervisor is requested to keep any such transcripts labeled as different-context executions rather
than deleting them, and to record the current-state reproduction (§7B) alongside them.

## 8. Unresolved legal questions — PRESERVED for the G6 queue (not decided here)

Unchanged from v5. The matcher fails closed at each point; no coding assumption decides any of these.

1. **G6-Q1** — "which are separated by mapped public park" grammatical scope AND unverifiable physical
   predicate → a located named row returns **INDETERMINATE** with full provenance and `G6-Q1` recorded.
2. **G6-Q2** — "may be considered" (permissive) vs "is" (declarative) for C5-3/C6-4/C6-6 →
   **professional_review_required** for those districts, `G6-Q2` recorded; no numeric width test.
3. **G6-Q3** — boundary cross-street inclusive/exclusive → a segment sharing exactly one boundary with
   the designated pair returns **INDETERMINATE**, `G6-Q3-boundary-cross-street-inclusive-exclusive`
   recorded.

**Interpretation note on AS-1** (unchanged): a located named row returns INDETERMINATE per the binding
LEGAL BOUNDARY, but carries the correct `provision_id` and verbatim designated-row quote in provenance.
Flipping the snapshot block's `disposition_when_located` to `matched_override` (once G6 rules Q1 and a
mapped-park predicate exists) makes the same rows return MATCHED_OVERRIDE with no matcher change — and
`matched_override` is a recognized disposition, so the new §3 guard permits it.

## 9. Acceptance-scenario mapping

- **AS-1** — both named rows located; provision id `zr-12-10-named-street-wide` + verbatim row in
  provenance (status INDETERMINATE per §8). Test: `test_as1_named_rows_located_indeterminate_with_provenance`.
- **AS-2** — exact designated pair located (order-independent); shared boundary → INDETERMINATE with
  G6-Q3; disjoint → NOT_MATCHED. Tests: `test_as2_*`.
- **AS-3** — unknown/wrong/malformed → NOT_MATCHED or INDETERMINATE, never an exception, never a match.
  Tests: `test_as3_*`, `test_normalization_no_abbreviation_expansion_is_not_matched`.
- **AS-4** — provenance carries snapshot sha256 + section anchor on every non-NOT_MATCHED result;
  NOT_MATCHED carries none. Tests: `test_as4_*`, `test_not_matched_has_no_provenance`.
- **AS-5** — ruff clean; 40 tests pass; modularity failures 0 (module not flagged); no consumer touched.
- **AS-6** — CI green on the pushed head: orchestrator captures after push (§7C).
- **New (this revision)** — structured-field & disposition source validation beyond quote-substring:
  §3; tests in §3.4.

## 10. Scope discipline (what I did NOT do)

- No consumer wiring (no edit to `wide_street_live_provider.py` or any file outside the five allowed
  paths); no geometry; no numeric width computation; no fuzzy matching.
- No controller-configuration, task-state, or unrelated lint-file edit; no consumer edited to repair
  evidence collection.
- No hard-coded street: every row is read from the snapshot; the matcher now refuses a snapshot whose
  rows are not source-anchored, in addition to refusing one whose block quote is not digest-covered.
- No legal question decided; no r5_setback/other rule edited.

## 11. Discovery items (D-069 — routed to the orchestrator, out of scope here)

- **Abbreviation limitation** (unchanged). Exact-after-normalization means abbreviated inputs ("Allen
  St") return NOT_MATCHED; an upstream canonicalization layer may be needed for abbreviated callers.
- **`r5_setback.rule.json` still quotes the superseded flat §12-10 text** — separate rules-engineer/G6
  task (M4-T018 §2.4).
- **Mapped-public-park predicate needs data**; **alternate-width numeric tests need a connector** —
  both blocked on G6 rulings + sources the platform does not yet expose.
- **Street-type stripping vocabulary.** `_STREET_TYPE_WORDS` currently covers street/streets/avenue/
  avenues (all that the current rows need). A future named row using a different type word (Place, Road,
  Boulevard) would fail the anchoring guard closed until the vocabulary is extended and re-reviewed —
  the intended fail-closed direction, flagged so it is a conscious extension, not a silent gap.

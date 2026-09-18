# M5-T040 — producer report (hardening rework unit)

Task **M5-T040** — named-street override WIRING. This unit delivers ONLY the
DB-023a hardening precondition (ORDER-OF-WORK step 1) so it is independently
reviewable BEFORE any matcher consumer lands. Wiring, DB-025 display gating, and
the DB-021(e) branch additions remain deferred to a later unit.

Status: **UNIT_COMPLETE** for the hardening rework; the matcher is still a LEAF
(no `import ... named_street_override` anywhere under `app/`).

## 1. The gap this unit closes (superseding the prior report §1)

The prior `_validate_unconditional_source_binding` judged "unconditional" by
decomposing `verbatim_source_quote` into a word whitelist + capitalized tokens +
numerals. But `verbatim_source_quote` is only constrained to be **a substring** of
the digest-covered `verbatim_excerpt`. So a tamperer can keep the real excerpt +
digest, strip all qualifier metadata, and **narrow** the quote to the real
sub-span:

> `In Community District 7 ... Broadway between West 94th and West 97th Streets and
> in Community District 3 ... Allen Street between Rivington and Delancey Streets`

which omits `, which are separated by mapped public park shall each be considered a
wide street.`. That narrowed span (a) is a genuine substring of the excerpt
(integrity passes), (b) still anchors **both** rows so `_validate_against_source`
passes, and (c) decomposes with **zero residual** — so the prior gate ALLOWED it
and returned `MATCHED_OVERRIDE`. A word whitelist, capitalization, or bare
substring membership was being treated as the binding, and it is defeatable.

## 2. The fix — bind to the AUTHENTICATED, COMPLETE source span

Implementation hunk: `services/api/app/rules/named_street_override.py`
`_validate_unconditional_source_binding(named, excerpt)` (now takes the
digest-covered excerpt; call site `_validate_disposition_against_qualifiers`
threads `self._snapshot.verbatim_excerpt`). A `matched_override` accept now
requires BOTH, in order:

1. **COMPLETE-SPAN (primary binding).** Locate the quote in the digest-covered
   excerpt and require it to occupy a whole sentence unit: begin at a span boundary
   (excerpt start / newline / prior sentence terminator) AND end at a sentence
   terminator followed by the span edge or whitespace. A quote cut before its
   terminator (a narrowing that drops a trailing/interposed clause) is refused —
   `DB-023a complete-span binding`.
2. **NO-QUALIFIER on that complete span (defense in depth, retained).** The token
   decomposition (`_UNCONDITIONAL_DESIGNATION_WORDS` + numeric/ordinal + capitalized
   locators) now runs only AFTER the complete-span binding has forced the quote to
   be the whole sentence, so a full conditional quote kept intact while metadata is
   stripped still fails on the residual clause words.

Both read ONLY digest-covered source (the excerpt and its substring quote) and NO
mutable qualifier metadata, so the binding is tamper-evident. It decides no legal
question and is scoped to `matched_override`; an `indeterminate` disposition (the
real snapshot's value) is unaffected — the real matcher still constructs and
returns INDETERMINATE for Broadway/Allen with full provenance.

The core added check (bounded excerpt of the real hunk):

```python
start = excerpt.find(quote)
...
starts_at_boundary = (
    start == 0 or preceding.endswith("\n") or preceding.rstrip(" ").endswith(".")
)
ends_at_boundary = quote.rstrip().endswith(".") and (
    following == "" or following[:1] in (" ", "\n")
)
if not (starts_at_boundary and ends_at_boundary):
    raise NamedStreetOverrideError(... "not a COMPLETE sentence span" ...)
```

## 3. Adversarial regression + retained coverage

New test (`tests/rules/test_named_street_override.py`):
`test_db023a_narrowed_source_quote_to_omit_condition_refused` — from the REAL
zr-12-10 snapshot it preserves `verbatim_excerpt` + `content_digest_sha256`,
removes all four qualifier signals, sets `disposition_when_located=matched_override`,
and narrows `verbatim_source_quote` to the sub-span that omits the condition. It
asserts the excerpt/digest are unchanged, the narrowed quote is a real substring of
the excerpt that omits the clause, and **every row locator still anchors** (so the
refusal is not incidental to source-tracing), then asserts construction refuses
with `match="COMPLETE sentence span"` — the refusal is the complete-span binding.

Retained (all green): the prior DB-023(a) metadata-bypass tests, the
all-four-signals-stripped parametrization (`remove` / `null` / `falsely_resolved`,
which keep the full conditional quote and are still caught by the defense-in-depth
decomposition), the source-bound isolation test, and the legitimate
unconditional-row coverage (`test_matched_override_for_unconditional_row`,
`test_db023a_unconditional_row_with_no_qualifier_signals_reaches_override`, and the
"allowed" half of the isolation test) — the complete-span gate does not over-refuse
a genuine single-sentence unconditional designation.

## 4. Cumulative FIVE-file diff (reconciled with the checkpoint)

The working tree carries five files vs the seam head; the checkpoint's
`changed_files` lists all five (the prior three-file list is superseded):

| file | this unit | content |
|---|---|---|
| `app/rules/named_street_override.py` | YES | DB-023a complete-span binding + defense-in-depth decomposition; docstring/comments corrected |
| `tests/rules/test_named_street_override.py` | YES | narrowed-quote adversarial regression (+1 test) |
| `app/spatial/wide_street_live_provider.py` | carried (DB-021, step 2) | provider-side `MAX_LOT_VERTICES` pre-check (`:425`), `wide_object_ids` cap before the geometry-fetch loop (`:467`), two-layer exceptions-attestation docstring (`_policy_decisions`), DB-020 page-`raw_digest` binding (`:368`) |
| `tests/spatial/test_wide_street_live_provider.py` | carried (DB-021) | provider ceiling / page-digest tests |
| `project-control/reports/M5-T040-producer-report.md` | YES | this report |

The provider + provider-test changes are the DB-021 provider-hardening (ORDER step
2); they are pre-wiring (no consumer import) and are exercised green by command 3.
They are part of the cumulative diff and are listed so the packet is bounded and
honest. DB-021(e) direct branch tests and the DB-025(d) multi-page fixture are NOT
claimed here — they land with the wiring unit.

## 5. Documented command runs (exact cwd / command / result)

Run separately (never chained). Commands 1–4 from `services/api`; the modularity
check from the repo root — per the packet's COMMAND CWD input. Supervisor captures
the directories/outcomes.

| # | cwd | command | result |
|---|-----|---------|--------|
| 1 | `wt-m5t040/services/api` | `python -m ruff check .` | `All checks passed!` |
| 2 | `wt-m5t040/services/api` | `python -m pytest tests/rules/test_named_street_override.py tests/rules/test_wide_street_wiring.py -q` | `83 passed` |
| 3 | `wt-m5t040/services/api` | `python -m pytest tests/spatial/test_wide_street_live_provider.py -q` | `37 passed` |
| 4 | `wt-m5t040/services/api` | `python -m pytest tests/api tests/rules/test_rules_integration.py -q` | `475 passed` |
| 5 | `wt-m5t040` (repo root) | `python tools/modularity_check.py --check` | `failures 0; warnings 20` |

Command 2 rose 82 → **83** (the one new adversarial regression). Commands 3/4
unchanged (37 / 475) — no consumer suite regressed. Modularity: **0 failures**;
`named_street_override.py` stays in the warning tier (below the 750 justify tier and
1000 hard tier), cohesive within its single responsibility (deterministic,
source-bound ZR 12-10 override matching with fail-closed construction validation).
No repository-root lint findings were touched and no supervisor configuration was
modified.

## 6. Scope preserved

- **No consumer import added** — the matcher is still a leaf; wiring, the
  fail-closed attestation truth table, DB-025 display gating, and the
  DB-021(e)/DB-025(d) additions are deferred until this precondition is reviewed.
- **Contract CLOSED, not widened** — no schema copy, no generated TS, no
  `integration.py` / `response.py` change.
- **No legal interpretation inferred** and **no out-of-scope snapshot/loader file
  modified** — the fix reads (never writes) the digest-covered source.

## 7. Discovery notes (D-069)

- Digest-covering the disposition/qualifier metadata in the snapshot schema is a
  separate, larger `docs/research/zr-snapshots` + loader change and remains out of
  this packet's paths. It is no longer the mechanism this bypass relies on — the
  accept is now bound to the already-digest-covered excerpt via the complete-span
  binding. Routed to the discovery backlog.
- The complete-span binding assumes the designation is a single sentence (true for
  the pinned zr-12-10 paragraph 2 and for any genuine unconditional designation);
  the fixed grammar should be revisited if a future unconditional designation uses
  vocabulary outside the template. This is the D-051-correct fail-closed direction.

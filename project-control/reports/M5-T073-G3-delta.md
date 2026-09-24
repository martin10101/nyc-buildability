# M5-T073 — G3 delta re-attestation (code-reviewer, read-only)

> Transmission history: returned complete in ONE message (END-OF-REPORT present). Saved
> verbatim by the orchestrator (transport entity-decoding only). This delta follows the
> full G3 review in M5-T073-G3.md (PASS with required F1 + recommended F2–F5); the two
> together are the G3 record — the full review carries the findings, this delta carries
> the per-item verification of the [ORCH-CORRECTED per G3 F1-F5] cluster at the corrected
> head and the PASS.

# M5-T073 — G3 delta re-attestation at `6de7f7a5`

HEAD verified = `6de7f7a56e730e9b90bd2c42b908fc3e655295c8`; correction cluster `114a6805` touches only the report, the manifest, and the harness (three allowed paths, no production edit). Self-check re-run at this head: scoped `ruff` → `All checks passed!` (exit 0); `pytest tests/connectors/test_bridge_ring_preconditions.py -q` → **14 passed** (exit 0).

**F1 — VERIFIED.** `pairs_manifest.json` side keys now include `dataset_version` on all 8 pairs, and I checked the recorded values against the fixture bytes rather than trusting the transcription: recorded == body `Version` for all 16 sides (P01–P04 display `26v2` / authoritative `26v1`; P05–P08 `26v2`/`26v2`). The report carries the disclosure as its own subsection ahead of the §7 disposition, correctly stating the ~54-day cross-release pairing, that the four same-release pairs are also `counts_equal=true`, and that production fetches both rings from one release — which is exactly the bound I asked for, and it names the assumption the mount packet inherits.

**F2 — VERIFIED, mutant now reddens.** Per-pair `expected_verdict`/`expected_refusal_class` are in the manifest and asserted at `test_bridge_ring_preconditions.py:486-487`. I confirmed recorded expectations equal measured output for all 8 (no baked-in wrong value), then re-ran my dropped-ambiguity-gate mutant: it is now **caught by P03, P05, P06** (previously `NONE`). The headline 3/8 can no longer flip silently.

**F3 — VERIFIED.** `:479` asserts `provenance["display"]["computed_sha256"] == pair["display"]["source_file_sha256"]`. Unlike the authoritative side it has no `if recorded:` guard, so a pair missing the field raises `KeyError` — fail-closed, which is the right direction here.

**F4 — VERIFIED.** Floor raised to `len(_PAIRS) >= 8` / `len(boroughs) >= 3` (`:463-464`), and both stale descriptions are reconciled by appended `[ORCH-CORRECTED]` notes that keep the pre-harvest text: module docstring (`:47-56`) and manifest `sample_bound`.

**F5 — VERIFIED.** A blockquoted `SUPERSEDED` pointer sits directly under the `STATUS — BLOCKED` heading, naming all three stale surfaces (the heading, §5's pending-harvest preamble, §9) and directing to the `[ORCH-HARVEST]` section, with the original text preserved.

**New concerns: none.** The manifest diff is large (406 lines) because it was reformatted, so I proved it content-preserving rather than eyeballing it: 8 pairs before and after, zero drift across `pair_id/bbl/borough/borough_code/geometry_class/notes` and every side's `source_fixture/endpoint/retrieved_at/kind/response_body_sha256/source_file_sha256`; the only additions are `expected_verdict`/`expected_refusal_class` plus the per-side `dataset_version`, and the only top-level change is `sample_bound`. The report diff is additions only — no measured value in §5 was touched. My F6 (authoritative-side BBL check) and F7 (first-member selection, harness-measured counts for P02/P04) were informational and remain as recorded advisories for the mount packet; nothing in the corrections affects them.

G3 DELTA VERDICT: PASS

END-OF-REPORT

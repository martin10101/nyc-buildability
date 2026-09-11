# M2-T021 — G3 data-contract RE-REVIEW (rework at eb6a15f8)

**Gate:** G3 (data-contract-verifier, independent — did not write this code)
**Task:** M2-T021, Geoclient v2 address-resolution connector
**Repo checkout:** `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`
**Reviewed SHA:** `eb6a15f8` (HEAD), gate-wave record `430773eb`, first-round review at `d4cdbe79`
**Reviewed:** 2026-09-11
**Discipline:** ADR-005 read-only. Reads, read-only git commands, and stdlib-only `python -c` snippets over fixture JSON. No `app` module imported, no pytest run, nothing written to the repository.

---

## VERDICT: **PASS** — one BLOCKING record correction, one MEDIUM test-integrity fix

All four of my first-round blocking corrections landed and are accurate against the tree. Fifteen of my seventeen findings are CLOSED, two are ADDRESSED-BY-DISCLOSURE, none is still open. The rework is a genuine improvement, not a paper one: the connector now preserves empty strings, deep-copies `raw_fields`, carries `digest_canonicalization`, and the suite grew from 36 to 98 collected cases — a number I reproduced exactly.

Two things did not survive scrutiny. The rewritten evidence map introduces one *new* overstatement of the same universal-quantifier class I struck last round, and the test offered as evidence for my finding 10 cannot fail.

---

## PART 1 — DISPOSITION OF THE ORIGINAL 17 FINDINGS

### The four BLOCKING record corrections

**1. Capture attribution — CLOSED.**
Evidence map (R004, live-call surface) now reads: *"each a single KB-scale GET EXECUTED BY THE ORCHESTRATOR/PRODUCER from the owner machine holding the owner-provisioned key (the owner did not personally run the GETs)."* `docs/MVP_AGENDA.md` section I now reads: *"§J1 executed: the owner provisioned the key and authorized the capture; the orchestrator ran the recorded GET."* Both now agree with G01's own `capture_method` field, which was the primary record I checked them against. The correction is exact, and the `_correction_record` at the top of the map names the defect rather than quietly editing it.

**2. The uncited owner-directive quote — CLOSED, with a LOW residual (see N5).**
`docs/MVP_AGENDA.md` section I now carries: *"**OWNER DIRECTIVE (2026-09-11, live session, verbatim): 'go ahead with the address entry connector.'** Given after the J1 capture and its why-explanation; discharged as task M2-T021. Recorded here so citations to this directive resolve to a control-plane document."* The map's corresponding sentence says the directive is *"now recorded verbatim as an OWNER DIRECTIVE line in docs/MVP_AGENDA.md section I so this citation resolves"* — the word "now" does the honest work. The citation resolves, and the record discloses that it was created to make it resolve.

**3. The unsupported key-acquisition date — CLOSED.**
The map now says the owner obtained the key *"(first documented as in the owner's possession 2026-09-11, docs/MVP_AGENDA.md section I; the 2026-09-10 handoff still lists it missing, and no earlier acquisition date is recorded anywhere)."* That is precisely what I found independently, including the handoff contradiction — the correction did not merely delete the bad date, it recorded the negative result. `project-control/blockers/B-004-geoclient-subscription-key.json` is now `"status": "resolved"` with `resolved_at` set to G01's own capture timestamp, and it discloses what remains unproven: *"Official rate limits REMAIN UNCONFIRMED — the owner has not recorded the portal subscription page's displayed quotas."* Recording the unconfirmed half is the right instinct. One stale-prose residual at N4.

**4. The inflated test enumeration — CLOSED in substance; a residual of the same class at N3.**
The map's R004 sentence is now itemized rather than universal: 98 collected; a module-wide socket guard; no real key with a positive control; three integrity tests that hash without invoking the connector; "many tests run on clearly-labeled CONSTRUCTED variants"; the recorded-body anchors named as the S1/S3/S4 tests. **I independently reproduced the 98**: 49 test functions expanding through their `parametrize` decorators to exactly 98 collected cases. The claim is exact, not rounded.

### The remaining thirteen

**5. `digest_canonicalization` missing — CLOSED.** `geoclient_address.py` now imports `CANONICALIZATION_SPEC` alongside `canonical_json_digest` from `app.connectors.pluto_soda` and emits `"digest_canonicalization": CANONICALIZATION_SPEC` in the provenance block. Asserted twice: in `test_s1_provenance_is_complete_and_key_free` and in the new all-six-statuses provenance test. The connector now matches the house pattern its four siblings established.

**6. Empty string reinterpreted as absence — CLOSED.** `_string_or_none` is now `return value if isinstance(value, str) else None`, with a docstring stating the rule: *"an empty-string SOURCE VALUE is preserved as `\"\"` (it is data, not absence — the mirror image of the fabrication rule)."* Pinned by `test_s8_empty_string_source_value_is_preserved_not_reinterpreted`, and published to consumers in the registry record's new `empty_string_rule`. See N6 for the one remaining case of the same shape.

**7. Provenance asserted on one status only — CLOSED.** `test_s8_provenance_is_complete_on_every_status` is parametrized over `_status_bodies()`, which supplies one body per status — recorded where one exists (G01 resolved, G02 ambiguous, G03 rejected), constructed otherwise. It asserts all eight provenance keys plus both GRC fields present, the digest recomputed, and sentinel absence. The packet's "every outcome" clause is now verified by the suite rather than by reading the code.

**8. GRC 50/75 narrowing — ADDRESSED-BY-DISCLOSURE (behavior deliberately unchanged).** The module docstring carries a **KNOWN NARROWING** paragraph naming 50 and 75 as UPG Appendix 4 alternative-carrying classes, stating that this connector classifies them `rejected` and extracts no alternatives *"because no recorded fixture pins their response shape,"* and pointing at a follow-up capture task. Echoed in the `RESOLUTION_STATUSES` comment, the registry record, `MVP_AGENDA` C4, and the producer report. Leaving the behavior alone until a fixture exists is the right call — widening on documentation alone is exactly the guessing this connector refuses elsewhere.

**9. Registry narrower than the research it cites — CLOSED.** `status_model.geocoding` now quotes both codes with their UPG meanings (50's reason code as the count of valid alternatives; 75's duplicate-address text), states the narrowing explicitly as disclosed per this gate, and names the widening path. `known_limitations` and two new `response_semantics` keys carry the rest.

**10. `raw_fields` aliasing — CLOSED IN CODE, but its test is tautological (see N2).** `raw_fields=copy.deepcopy(address)`, and both the module docstring and the dataclass comment explain why (*"caller mutation can never invalidate provenance['response_digest']"*).

**11. Leak-absence test could pass vacuously — CLOSED, thoroughly.** `test_s6_sentinel_never_leaks_from_any_path` now runs ten paths (three recorded bodies plus 401/403/429/500/timeout/network-failure/malformed, plus two pre-network typed errors) and asserts positive controls before the leak assertion: every transport actually received a call, every call carried the sentinel in the auth header, every failure path actually raised (`pytest.fail` otherwise), and `assert caplog.records` proves the log half captured something. It also harvests `caplog.text` rather than only `getMessage()`, so logger names and `exc_text` are in the swept surface. This is a better test than the one I asked for.

**12. Absent second sub-call code — CLOSED.** The docstring has a **Sub-call asymmetry** paragraph stating plainly that whether Geoclient omits the second code *"is NOT established by any fixture"* and that the connector fails closed rather than guessing. `test_s8_invalid_shape_grc_fails_closed_on_either_side` is now a 2×6 matrix (both sides × three-char, empty, one-char, bad-char, trailing-newline, absent) = 12 cases, so the second-side absence I flagged is now covered.

**13. Coordinate annotation — CLOSED.** `latitude: float | int | None`, with `test_s8_integer_coordinate_stays_int` asserting `type(res.latitude) is int` for an integer coordinate.

**14. Only the single-suggestion EE shape pinned — CLOSED for the code path.** `_extract_suggestions` no longer consults `numberOfStreetCodesAndNamesInList` at all, in either direction, and walks every slot to the bound — the docstring notes that trusting it downward *"would silently discard suggestions the source actually returned."* Covered by `test_s3_multi_suggestion_walk_with_gaps_and_codeless_slots` and a five-case `test_s3_declared_count_is_ignored_suggestions_come_from_slots`. The residual — no *recorded* multi-suggestion capture exists — is now disclosed in `MVP_AGENDA` C4 and the producer report rather than left silent.

**15. G0 gate SHA — CLOSED.** The map now reads *"PASS recorded at reviewed_sha acf54c63 (the gate record's own value; the packet itself was committed at 5937b1f4),"* which is exactly the distinction the two records support.

**16. `MVP_AGENDA B3` citation — CLOSED.** Now *"item 3 of section B (and row 4 of table A2)."* Resolves.

**17. Producer report line count — CLOSED.** The rework addendum opens by correcting its own claims: *"'~500 lines incl. documentation' was wrong: the module was **572** lines at review."* It also self-corrects two claims I had not caught — that the original S6 harvest covered six paths and not "every failure path," and that the second `caplog.set_level` on the transport logger was inert because the shared engine logs through the connector's logger. Self-reported corrections beyond what the gates found are worth noting favorably.

---

## PART 2 — NEW FINDINGS IN THE REWORKED TREE

**N1. BLOCKING — `project-control/reports/M2-T021-evidence-map.json`, R003 item 2: the ZERO-files claim is extended to "any producer commit" and is false as written.**

Verbatim: *"The producer diff is commit dc227c0a (six files: connector, tests, two fixtures, registry record, producer report) plus the gate-wave rework commit(s) that follow it; **ZERO files under tools/, .claude/, the supervisor, project-control machinery, or any loop/self-infrastructure path in any producer commit**."*

The rework commit `eb6a15f8` is a producer commit by its own message, and it touches ten files, of which three sit outside the packet's `allowed_paths` (unchanged at HEAD — still only connectors, tests, fixtures, `geoclient.json`, and the producer report):

- `project-control/blockers/B-004-geoclient-subscription-key.json`
- `project-control/reports/M2-T021-evidence-map.json`
- `docs/MVP_AGENDA.md`

Two of those are under `project-control/`. The original map scoped this claim to `dc227c0a` alone, where it was true and I verified it; the rewrite widened it to "any producer commit" at the same moment the producer commit stopped satisfying it.

**Consequence:** this is the sentence that discharges D-038 R003 ("product engineering, not self-infrastructure"). A reader who trusts it would not learn that the rework wrote two control-plane records and the owner agenda. Note that neither path is in `forbidden_paths` (which names `project-control/tasks/**` and `project-control/gates/**` but not `blockers/` or `reports/`), so this is an allowlist question, not a prohibition breach.

**Correction (mine to require, one sentence):** rescope the claim to `dc227c0a` and state the rework's record writes explicitly. **Not mine to rule on:** whether writing those three files was in scope. That is a G1/control-plane question — and the clean precedent already exists in this task's own history, since the first-round evidence map was committed separately by the orchestrator at `d4cdbe79` precisely to keep it out of the producer diff. Either amend `allowed_paths` or split the record writes back out.

**N2. MEDIUM — `services/api/tests/connectors/test_geoclient_address.py:165-168`: the assertion offered as evidence for the deep copy cannot fail.**

```python
# ...as an independent copy: caller mutation cannot reach the connector's
# parsed state (G3 finding 10).
res.raw_fields["bbl"] = "MUTATED"
assert _fixture_address(G01)["bbl"] == addr["bbl"]
```

`_fixture_address(G01)` re-reads the fixture from disk and re-parses it. The fixture file is never written by the connector, so this assertion holds identically whether `raw_fields` is `copy.deepcopy(address)` or the aliased `parsed["address"]` it was before. Delete the `copy.deepcopy` and this test still passes.

**Consequence:** the code fix is real and I verified it at the call site, but the suite does not pin it — a future refactor dropping the deep copy would go green. This is the M5-T004 pattern in miniature: an assertion that reads as proof and proves nothing. (The adjacent `assert res.raw_fields == addr` on line 164 *is* meaningful; only lines 167-168 are vacuous.)

**Honest caveat on the fix:** the recorded `address` objects are flat — all values are scalars — so a shallow `dict(address)` would be equally sufficient today, and the deep copy's only observable benefit arrives if a nested object ever appears or the connector starts retaining `parsed`. The clean repair is to assert non-identity directly (`assert res.raw_fields is not` the object the digest was taken over, via a transport that hands back a known dict), or to drop the assertion and label the deep copy as defense-in-depth in the docstring rather than as a tested property.

**N3. LOW — the reworked map's "every test that invokes the connector does so through an injected transport seam" has two exceptions.**

Inside `test_s6_sentinel_never_leaks_from_any_path`, lines 710-713 call `resolve_address` twice with neither a `transport=` argument nor a monkeypatched `mod.urllib_transport`:

```python
lambda: resolve_address("314", "w 100 st", borough="manhattan", env={}, sleep=_no_sleep),
lambda: resolve_address(314, "w 100 st", borough="manhattan", key=SENTINEL_KEY, sleep=_no_sleep),
```

Both raise (`KeyMissingError`, `InvalidInputError`) before transport is ever resolved, and the autouse socket guard would catch any attempt regardless — so nothing is at risk. Separately, the sentence says *"three integrity tests hash the fixtures without invoking the connector"* when six tests never invoke it (`test_s7_fixture_digest_matches_stored_sha256` ×3 and `test_s7_fixture_request_urls_are_key_free` ×3) — an undercount, not an inflation.

I raise this only because the identical universal-quantifier construction is what I struck last round and the standard should not move. **Suggested wording:** "every test that reaches transport does so through an injected seam; the pre-network error paths raise before transport is resolved, and a module-wide socket guard makes real network I/O mechanically impossible in every test." The guard claim is the load-bearing one and it is **true** — `socket.socket` and `socket.create_connection` are both monkeypatched by an autouse fixture, which is the pair `urllib` actually reaches through.

**N4. LOW — `project-control/blockers/B-004-geoclient-subscription-key.json`: stale prose beside corrected data.**
`status` is now `resolved` and `resolution` is thorough, but the untouched `detail` field still reads *"Research (M0-T002) is complete without it; live fixture capture and official rate-limit confirmation are blocked."* The capture is no longer blocked. This is the exact defect `MVP_AGENDA` section K catalogues for `master_plan.json` ("Stale prose beside correct data in the same file"). One clause.

**N5. LOW — the OWNER DIRECTIVE line does not record its own transcription provenance.**
`docs/MVP_AGENDA.md` section I presents the quote as verbatim from a live session and discloses that it was recorded so citations resolve — good. What it does not say is *who* transcribed it and *when* it entered the document: the orchestrator, during the rework at `eb6a15f8`, after a gate objected to the uncited quote. A reader six months out sees a verbatim human directive in a control-plane document with no indication that an agent wrote it down after the fact. Adding "transcribed by the orchestrator during the M2-T021 rework (eb6a15f8)" closes the loop, and costs nothing. An agent-transcribed quotation attributed to a person is the attribution class this gate exists to police, so I would rather it be over-labeled than under-labeled.

**N6. LOW — type drift still collapses into `None`, and the consumer-facing docstring does not say so.**
`test_s8_type_drift_is_never_coerced` pins that a numeric `bbl` or a string `latitude` yields `None` on the canonical field while `raw_fields` keeps the drifted value — a deliberate, documented fail-safe, and the right behavior. But the `AddressResolution` docstring still tells consumers that canonical fields are *"`None` when the source omitted them (null omission — never fabricated); an empty-string source value is preserved as `\"\"`."* A caller reading the dataclass contract concludes `None` means "omitted," when it now also means "present but wrong type." `_string_or_none`'s own docstring says "absent or non-string -> None" — so the fact is recorded at the function, just not where consumers read it. This is the residue of finding 6's class: the empty-string half was fixed, the type-drift half inherits the ambiguity.

**N7. LOW (no action) — the corrected fixture timestamps are internally consistent but not verifiable from the tree.**
All three fixtures now carry `retrieval_timestamp_basis` naming the filesystem write time of the raw capture file and disclosing the original hand-estimate error. The raw capture files live outside the repository, so I cannot verify the times directly. What I *can* check, and did, is internal consistency, and it holds: G01's `18:46:43Z` precedes its commit `ccf64f75` (14:48:07 -0400 = 18:48:07Z) by 84 seconds; G02/G03's `19:33:39Z` precedes `dc227c0a` (19:41:40Z) by about eight minutes, whereas the withdrawn estimate of `19:55:00Z` would have post-dated that commit by fourteen — which is what made the original values provably wrong. G02 and G03 sharing a single second is asserted as genuine ("issued by one loop"); plausible for two sequential sub-second GETs, and unverifiable from here. Disclosed correctly; noted so the next reviewer knows the limit of what the tree proves.

---

## PART 3 — OVERSTATEMENTS

**One new overstatement**, quoted verbatim at **N1**: the ZERO-files claim extended to *"any producer commit,"* contradicted by `eb6a15f8`'s three files outside `allowed_paths`, two of them under `project-control/`.

**One residual imprecision** at **N3**: *"every test that invokes the connector does so through an injected transport seam"* (two exceptions, both pre-network, both covered by the socket guard) and *"three integrity tests"* (six).

**Nothing else.** I checked every sentence of the rewritten map against the tree, as before. The following corrected claims are accurate, and several are more exact than they needed to be:

- The `_correction_record` preamble names all four struck claims and points at `d4cdbe79` for the superseded original rather than burying it.
- The **applicability disclosure now leads** R003: D-038 R003/R004 declare `task_ids` M5-T003…M5-T013, `M2-T021` is not among them, and `project-control/reports/M2-T021.json` computed `applicable_requirements` empty. I verified all three. Putting the fact that cuts *against* the map's own necessity in the first sentence, and routing the fix to an owner-gated amendment rather than arguing the constraint away, is the honest construction.
- The first-round wave verdicts (G1 FAIL, G3 PASS, G4 FAIL, G5 PASS) match `project-control/gates/M2-T021-G*.json` at `430773eb`, and the map claims nothing about the pending re-review.
- **The cross-cutting sibling-connector claim is true.** `MVP_AGENDA` C4 asserts that the `$`-anchored `_SAFE_TEXT_RE` + `re.match` newline defect also ships in three accepted connectors at named lines. I checked all three: `mappluto_geometry_arcgis.py:314`, `zoning_features_arcgis.py:266`, `ztldb_soda.py:345` each define a `^…$` pattern, and each is used with `.match()` at lines 445, 394 and 495 respectively. A producer volunteering a verifiable defect in already-accepted work, with line numbers that check out, is the opposite of the behavior this gate was created to catch.
- The arithmetic in the self-check claim is consistent: 375 (original, 36 new + 339 existing) → 437 (98 new + 339 existing). I cannot run the suite, so the pass/fail remains a producer self-claim, but the numbers do not contradict each other.

---

## PART 4 — WHAT I VERIFIED THIS ROUND

- **Fixture integrity, recomputed from scratch after the metadata edits.** All three fixtures were modified by `eb6a15f8`, so I re-hashed `response_body_raw` for each: G01 `e7bffd4b…`, G02 `6e7c6e35…`, G03 `675d9bd9…` — **all three still match** their stored `response_sha256`, confirming only metadata changed and the recorded bodies are untouched. Field counts unchanged at 171 / 23 / 17. All three `request_url` values remain key-free.
- **Test count, reproduced independently.** Parsed every `@pytest.mark.parametrize` decorator and expanded the case lists: 49 functions → **exactly 98 collected cases**. The claimed figure is exact. (My first pass stalled on four decorators referencing module constants and a helper; resolving `[G01, G02, G03]` ×3 and `_status_bodies()` ×6 accounts for the remaining 11.)
- **Every `resolve_address` call site in the suite**, to test the "injected seam" claim — fifteen call sites plus the `_resolve` helper. Result at N3.
- **The real-environment test**, specifically for the risk that it might pick up a live key: `test_s6_key_is_read_from_the_real_environment_at_call_time` uses `monkeypatch.setenv(KEY_ENV_VAR, SENTINEL_KEY)` before the first call and a rotated sentinel before the second, so the process environment is overwritten with a sentinel and restored afterwards. On the owner machine, where the real key *is* set, no test would ever read it. The map's "no test uses a real key" holds.
- **The socket guard**, that it patches the pair `urllib` actually reaches: `socket.socket` and `socket.create_connection`, via an autouse fixture, so `http.client`'s module-attribute lookup hits the block.
- **Verbatim transport, re-traced through the changed code** — `_string_or_none`, `_number_or_none`, `_classify`, `_extract_suggestions`, and the full `AddressResolution` construction. No coercion introduced by the rework; `fullmatch` replaces `match` in both `_GRC_SHAPE_RE` and `_SAFE_TEXT_RE`; the `repr()` fallback is capped at 300 chars; malformed-shape key reporting is capped at 20 with an explicit truncation marker.
- **The provenance block**, against the packet's five required elements plus the two additions: `digest_canonicalization` now rides beside `response_digest`, `request_params` is still a defensive copy, and the key still appears in no field.
- **URL encoding**, the new `quote_via=quote` path, and that `test_s1_constructed_url_equals_the_recorded_capture_url` asserts byte equality against each fixture's own recorded `request_url` — the anti-tautology form, comparing against the capture rather than a literal.
- **The three sibling connectors** named in the `MVP_AGENDA` C4 defect claim, at the exact lines cited.
- **Packet scope at HEAD**: `allowed_paths` unchanged, `status` now `rework` at 70%, with a `progress_log` entry recording all four gate verdicts. Cross-checked `eb6a15f8`'s ten files against it — result at N1.
- **B-004, the rewritten evidence map, the registry diff, the producer-report addendum, and `MVP_AGENDA` sections I and C4**, sentence by sentence against the tree.
- **Read-only discipline honored (ADR-005).** Reads, `git show`/`log`/`grep`, and stdlib-only `python -c` over fixture JSON. No `app` module imported, no pytest run, nothing written to the repository.
- **Could not verify, by design:** "437 connectors tests pass," "98 passed," ruff, modularity, and the secret scan — running them is outside my mandate, so they remain producer self-claims. Also unverifiable from the tree: the raw capture files' filesystem write times (N7) and the live-session provenance of the owner directive (N5).

---

## FILES REFERENCED (absolute)

- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\connectors\geoclient_address.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\connectors\test_geoclient_address.py`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\fixtures\geoclient\G01_address_documented_example.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\fixtures\geoclient\G02_address_ambiguous_ee.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\tests\fixtures\geoclient\G03_address_rejected_42.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M2-T021-evidence-map.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\reports\M2-T021-producer-report.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\blockers\B-004-geoclient-subscription-key.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\tasks\M2-T021.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\project-control\gates\M2-T021-G0.json` (and `-G1` / `-G3` / `-G4` / `-G5`)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\docs\research\source-registry-drafts\geoclient.json`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\docs\research\M0-T002-geoclient-address-resolution.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\docs\MVP_AGENDA.md`
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\connectors\mappluto_geometry_arcgis.py` (line 314 / 445)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\connectors\zoning_features_arcgis.py` (line 266 / 394)
- `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24\services\api\app\connectors\ztldb_soda.py` (line 345 / 495)

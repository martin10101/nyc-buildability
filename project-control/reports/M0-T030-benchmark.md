# M0-T030 — A/B navigation benchmark (AS-9, load-bearing per D-005-R085/R086)

**Repo state (both approaches, identical):** worktree `.claude/worktrees/M0-T030-codegraph`,
branch `task/M0-T030-codegraph` at `9c95e12` (base main `613c4b1` + M0-T030 implementation).
Graph pre-generated once (fingerprint `18d461e2910ab476`, 235 input files, 2907 nodes / 1491 edges).

## Protocol
- 18 questions (5 locate, 5 consumer/impact enumeration, 4 cross-layer traces, 2 control-plane, 2 CI/tooling), frozen before any run.
- **Approach A (baseline):** read-only agent, normal workflow (Glob/Grep/Read + committed docs); forbidden from tools/code_graph.
- **Approach B (graph-first):** read-only agent, REQUIRED to start with `tools/code_graph/query.py` queries, then verify every conclusion in actual source before answering (trust model enforced).
- **Independent judge per question:** separate read-only agent; derives ground truth exhaustively from source WITHOUT the graph; scores both answers (correctness first, completeness second, never speed). Producer of the tool wrote no answers and judged nothing.
- Metrics are observable tool operations self-reported by each agent (search = Grep/Glob, read = Read, graph = query.py invocations) plus judged correct/complete/missed/false.
- **No token counts are claimed** (D-005-R039). **Per-agent elapsed time is excluded**: the first benchmark run was interrupted mid-flight and resumed from the agent cache, which makes per-agent wall-clock non-comparable across runs; rather than report non-reproducible timings, they are omitted (D-005-R085 "where reproducible/useful").

## Per-question comparison

| # | Question (abbrev.) | A ok | A compl | A missed | A false | B ok | B compl | B missed | B false | A ops | B ops (graph) | A files | B files | Winner |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Where is the SourceFact contract defined, and which backen… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 7 | 13 (5) | 2+0 | 7+0 | tie |
| 2 | Trace property_profile from its JSON schema to the backend… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 5 | 11 (4) | 3+0 | 4+0 | tie |
| 3 | Which backend files consume/reference zoning_features? | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 3 | 15 (6) | 0+0 | 5+0 | tie |
| 4 | Which files would likely be affected by a change to the ru… | Y | Y | 0 | 1 | Y | N | 4 | 1 | 20 | 27 (4) | 6+0 | 8+0 | A |
| 5 | Where is exact-decimal legal arithmetic implemented (modul… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 7 | 15 (8) | 2+0 | 3+0 | tie |
| 6 | Which code paths can affect rounding of rule-evaluation re… | **N** | N | 4 | 2 | Y | Y | 0 | 0 | 17 | 38 (17) | 4+0 | 8+0 | B |
| 7 | Which modules know about staleness/cache states for offici… | Y | N | 1 | 0 | Y | N | 4 | 0 | 17 | 31 (10) | 1+0 | 15+1 | A |
| 8 | Where are geometry validity/repair semantics implemented? | Y | N | 2 | 0 | Y | Y | 0 | 0 | 5 | 16 (7) | 2+0 | 3+0 | B |
| 9 | Trace MapPLUTO geometry from its connector to spatial-inte… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 11 | 23 (14) | 4+0 | 5+0 | tie |
| 10 | Where do project-control acceptance checks live - the code… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 8 | 10 (6) | 3+0 | 3+0 | tie |
| 11 | Which CI job validates product-map integrity, and which sc… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 3 | 10 (6) | 1+0 | 3+0 | tie |
| 12 | Trace an API property lookup from the route in services/ap… | Y | Y | 5 | 0 | Y | Y | 3 | 0 | 9 | 13 (7) | 5+0 | 6+0 | B |
| 13 | Which files import (directly depend on) services/api/app/p… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 5 | 6 (3) | 1+0 | 2+0 | tie |
| 14 | Where is SUPPORTED_CONTRACT_VERSIONS pinned in the web cli… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 3 | 7 (2) | 2+0 | 3+0 | tie |
| 15 | Which test files exercise the scenario schema and/or servi… | **N** | N | 1 | 1 | Y | Y | 0 | 0 | 17 | 19 (8) | 4+0 | 5+0 | B |
| 16 | What are the internal upstream imports of services/api/app… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 7 | 3 (1) | 1+0 | 1+0 | tie |
| 17 | Where is the rules DSL evaluated, and which modules depend… | **N** | N | 2 | 1 | Y | Y | 0 | 0 | 11 | 15 (10) | 2+0 | 5+0 | B |
| 18 | Which files reference analysis_state transitions (schema +… | Y | Y | 0 | 0 | Y | Y | 0 | 0 | 11 | 19 (6) | 3+0 | 7+0 | tie |

(files column = relevant+irrelevant opened; "ops" = all navigation tool operations.)

## Overall scoring (18 questions)

| Dimension | A (baseline) | B (graph-first) |
|---|---|---|
| Correct | 15/18 | **18/18** |
| Complete | 13/18 | **16/18** |
| Questions with false claims | 4 | **1** |
| Judge winners | 2 | **5** (11 ties) |
| Total navigation ops | **166** (120 search + 46 read) | 291 (124 graph + 77 search + 90 read) |
| Files opened (relevant + irrelevant) | **46 + 0** | 93 + 1 |

## Honest findings

1. **Correctness improved, not merely maintained** (D-005-R086 gate): B answered all 18 correctly; A was materially wrong on Q6 (rounding paths), Q15 (serializer test coverage), Q17 (rules-DSL evaluator) and made false claims on 4 questions. No correctness regression exists in B; the load-bearing criterion PASSES.
2. **B did NOT reduce raw operation counts** — it used ~1.75x the operations and opened ~2x the files. The mandated trust model (verify every graph hit in source) converts cheap graph lookups into additional Reads. The benefit observed is *redirected, more complete* exploration (B's extra reads were nearly all relevant: 93 relevant vs 1 irrelevant), not less exploration. Claims that a graph "saves work" are NOT supported at this repo size; claims that it finds the right files more reliably ARE.
3. **Where the graph differentiated:** enumeration/impact questions (downstream importers, test coverage, rounding-affecting paths) — exactly the archetype committed docs do not cover exhaustively.
4. **Where the graph was weakest:** Q4 (rule_evaluation contract impact — B missed 4 affected files, 1 false claim) and Q7 (staleness modules — B missed 4): both involve relationships that are NOT import edges (byte-copied schema bundles, semantic "knows-about" relationships). The derived contract-touchpoint edges are heuristic by design; agents over-trusted breadth there. These are documented V1 blind spots, consistent with the honesty-label design, not silent failures.
5. **CLI wart found by agents:** `--limit` is a global flag and must precede the subcommand (`query.py --limit 50 find x`); two B agents lost one op each to a usage error. Improvement item: also accept per-subcommand placement. Not a correctness issue.
6. **Determinism/freshness held throughout:** all 124 graph queries ran against one pre-generated cache with a stable fingerprint; no agent received stale data (the CLI recomputes the source fingerprint on every invocation).

## Verdict vs the owner criteria (D-005-R085/R086, Part 18)
- Maintains or improves correctness: **PASS (improved: +3 correct, +3 complete, -3 false-claim questions)**
- Materially reduces unnecessary exploration: **NOT DEMONSTRATED** — operations increased; irrelevant-file waste was ~zero in both approaches at this repo size (~220 source files). The honest claim is *higher answer quality on dependency/impact questions*, not lower cost.
- No success is claimed from node/edge counts or generator completion (D-005-R086).

## Appendix: judge notes on the seven non-tie questions

**Q4 (winner A):** Both answers are of high quality and agree on the core dependency graph, and both correctly capture the subtle sync_contract_schemas.py exclusion + pytest byte-identity guard. Every checkable specific (line numbers, function/constant names, fixture lists, CI job commands) in both answers verified against source. A is strictly more complete: it includes the e2e layer (2 specs + harness + playwright config), the coverage_status/common $ref targets, PropertyLookup, and the weakly-coupled test_closed_contracts.py/test_contract_schema_packaging.py, none of which B lists. A's one blemish is an inter

**Q6 (winner B):** Every load-bearing line reference in both answers was verified by direct read. The two discriminators: (1) ruleset inventory — 7 rule files exist, none with a round step; B states this correctly, A claims only two shipped rulesets (materially wrong inventory, though the derived conclusion survives); (2) the mappluto coordinate-quantization dispute — the answers directly contradict each other and B is right: compute_area_sq_ft is called (L1028) on the unquantized geometry and is the preferred rule lot-area input, so COORD_DECIMALS rounding does not propagate into rule-consumed lot areas, contra

**Q7 (winner A):** Every checkable claim in both answers was verified against source: fetcher staleness stamping shapes and LKG_NOTE_PREFIX; cache.get_with_age; config 900s TTL / 24h LKG bound / cache_key_version / cache_max_entries; connector stamping sites (pluto_soda.py L395; ztldb L722/L754/L332/45.0; zoning_features ~L1735/L1842; mappluto ~L2060/L2168 — B's line numbers all exact); builder L714-722 fresh default; contract.py 1.3.0 rule; properties.py lru_cache singleton + L121 docstring; schema conditional rules; source_fact L108; generated TS L134; both answers' claim that no frontend consumes official-sou

**Q8 (winner B):** All line numbers and relationships in both answers were verified against source. A's minor imprecisions (omits the self_intersection exception to the area-drift guard; loosely calls the builder's geometry_validity dimension "a consumer of the taxonomy" when it is currently a separate two-value point-presence semantics) were judged non-material, as were B's omissions of the fetch-path repaired_geometry warning (line 1855, inside the file B identifies as primary and covered by B's cited policy/test), .claude/rules/geospatial.md (policy, not implementation), fixtures dir, and M2-T009 provenance. 

**Q12 (winner B):** Every checkable claim in both answers was verified against source in the M0-T030-codegraph worktree; all line numbers cited by both answers are accurate (properties.py L72/96/117/136/306/318/339/393/400; fetcher.py L206; pluto_soda.py L363/600/892; builder.py L557/512; main.py L31). FEASIBILITY_COLUMNS is indeed 19 columns (2 critical + 17). Two borderline items in B judged immaterial: "(line 742)" reads as wave_integration.py but 742 is the real build_wave_sections call site in builder.py (def is wave_integration.py L345); "anything else -> generic 500 internal_error" matches the documented d

**Q15 (winner B):** All of B's four files and its exclusion notes verified against source (format.test.ts:8 is prose 'scenario S5'; test_closed_contracts.py loads scenario schema only into its $ref registry). A's three named files and its marginal packaging callouts are accurate and well-evidenced, but its closing claim that no test files exist under packages/contracts is factually wrong and caused it to miss test_generate_scenario_ts.py, a material scenario-schema test. Both answers equally omit the marginal indirect coverage in test_generate_ts_types.py (main --check runs check_scenario() since M5-T001); judged

**Q17 (winner B):** Every line number cited by both answers was verified against source in the worktree. B is fully accurate: all evaluator internals (477/58/91/130/421), registry usage sites (18/157/167/68/73 with correct detect_rule_conflicts attribution), __init__.py line-18 direct re-export of evaluator, all four test-import line numbers, response.py line 43, endpoint flag/route, transitive test consumers, and both frontend files exist with no evaluator import. A is otherwise accurate (including the schema path, _default_registry 346-352, endpoint lines 59/256) but asserts registry.py is the only non-test dir


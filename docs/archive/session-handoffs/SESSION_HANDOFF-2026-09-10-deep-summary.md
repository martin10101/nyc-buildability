# Deep session summary — 2026-09-09 → 2026-09-10

**HISTORICAL** — narrative companion to `docs/SESSION_HANDOFF.md` (which is the current-only,
budget-constrained handoff and wins on any state question). This file exists because the owner asked
for the full detail; it is in `docs/archive/` and is exempt from the context-budget gate. Nothing here
overrides the ledger, git, or CI.

Session `01KCxUbUJdG1jvp8E6ura9g2`. Owner turnover reason, verbatim:

> *"i want you to also inculte the info about the graf not being build in to codex also sumrise our
> conver we had the last few very detelet and make a new md and tell me the file name so i can
> countinu the convo in new seasen"*

---

## 1. How the session started

The previous session died to an unplanned PC shutdown. It had accepted M5-T011 (174th) and asked the
owner "continue or hold?" — the machine died before an answer arrived. The owner's answer on resume was
*"restart loop and u just be the moniter if it breck or errors then step in otherwise keep building"*,
plus the signal that Supabase and NYC API keys were coming.

Reconciliation found nothing lost: 174 accepted, tree clean apart from two pre-existing untracked
qa-engineer memory files, supervisor in `PREFLIGHT` from a clean close (not `PAUSED_RECOVERY`), audit
chain healthy and unforked, no lock, no orphan process, and — importantly — **no autostart scheduled
task had fired on boot**, which would have relaunched a stale M5-T003 run. `docs/SESSION_HANDOFF.md`
was stale at seq 92; the ledger won, as designed.

---

## 2. Two features accepted (175th and 176th)

### M5-T012 — the optimization toolkit became reachable (accepted `b3fa1736`)

Four internal flag-gated POST endpoints:
`/api/v1/properties/{bbl}/scenario/sensitivity|ranking|comparison|threshold`. Each rebuilds
profile → rule_evaluation → scenario **server-side** over the accepted M5-T003 seams, then calls the
accepted engine **read-only** through the public `app.scenario` facade. Until this task, five gated
engine modules were reachable only from Python — no client, and specifically not the parked Compare UI,
could call them.

**Three defects the gates caught, all the same deep shape.**

1. *(pre-gate, found by the orchestrator before any reviewer was dispatched)* The AS-7 offline test
   replaced `socket.socket` globally to prove the feature opens no network connection. Starlette's
   `TestClient` drives the app through an anyio blocking portal whose event loop needs `socket.socket`
   for its own socketpair — so the test **deadlocked** and `pytest services/api/tests/api` never
   terminated. The producer's report had left its results as *"to be finalized"*, which was the tell.
   Fixed by asserting at the **egress seams** with landmines that **record as well as raise** — the
   recording is load-bearing because the route converts a raise into a typed 500, so a raise-only
   landmine would be swallowed and a naive test would still pass.

2. *(G5 BLOCKING-1)* An **unpaired surrogate** — `{"variable":"\ud800"}`, 22 ASCII bytes, under every
   documented cap — raised an unhandled `UnicodeEncodeError` on **all four** endpoints: untyped
   `text/plain` 500, no correlation id, a status/state pair absent from the documented matrix, full
   traceback logged. **Root cause worth remembering permanently:** `json.dumps(x, allow_nan=False)`
   defaults to `ensure_ascii=True`, which *escapes* surrogates and never raises, while Starlette renders
   with `ensure_ascii=False` + `.encode("utf-8")`, which *does*. The validator and the renderer
   disagreed about what is encodable, so the module's "strict-JSON-safe before send" guarantee was
   **false**, not merely incomplete. Any pre-send JSON assertion in this repo must use the same form the
   renderer uses.

3. *(G1 BLOCKING-1, reproduced by DCV, raised by G5 as MEDIUM)* `FORBIDDEN_FACT_KEYS` was enforced
   **top-level only**, so a fact-shaped object nested inside an assumption set was echoed verbatim in a
   200 body — a forged cap value, `coverage_status:"verified"`, `verified:true`, a fake
   `rule_evaluation.outputs`. The authoritative cap was never forgeable, but AS-2 and AS-6 were
   objectively unmet — **and the pack's own AS-6 helper would have failed on that body; no test sent a
   nested fact key.**

   Plus G1/G5 HIGH-1: the engine call and `_finish` sat outside **any** exception guard while the
   *trusted* rebuild stage **was** guarded. The asymmetry was backwards, and it is what let defect 2
   escape as an untyped 500.

### M5-T013 — the evidence / provenance endpoint (accepted `a84b85e4`)

`GET /api/v1/properties/{bbl}/evidence`. Assembles the provenance trail the accepted documents already
carried: profile closed-provenance records, per-citation provenance from the rule_evaluation trace,
input provenance, and a per-claim DRAFT-vs-Verified status. The data existed in `_closed_provenance`,
`_citations_with_provenance` and `_input_provenance`; **no API surface exposed any of it**, so a user
saw conclusions with no way to audit them. This is the Evidence view named in the original D-038 pivot
plan and never built.

Deliberately **body-less** — only the `bbl` path parameter — because M5-T012's two blocking defects were
both in its untrusted-body boundary and this endpoint needs no caller input. G5 confirmed that
structurally (every FastAPI param collection empty, `body_field: None`, GET only) and behaviourally (the
full document byte-identical across 11 hostile variants including a 1 MB body, a surrogate body, and
`?bbl=` shadowing the path parameter).

**The defect that mattered most in the whole session.** G1 FAILed it: the evidence document was a
**silent projection**. The `rule_evaluation` root has 20 required keys and each trace 19; the document
represented **14 and 7**, dropping **18 required contract fields** — including every qualification
attached to the cap it presented:

- `exceptions_applied` — *"A higher maximum residential FAR (up to 2.00 … per ZR 23-21) applies … the
  result is conditional"*, plus a documented 0.60 per-DU limitation
- `notes` — *"it is NOT an evidence-based determination"*
- `computation_steps` — the `10000.0 × 1.5 = 15000.0` derivation
- `rule_release` — including `verified_eligible: false`, the G6 approval state
- plus `lot_area_sq_ft`, `lot_area_source`, `zoning_district`, `rule_conflict`, `effective_window`,
  `evaluated_inputs`, `uncertainty`, `determination`, `spatial_context`, `spatial_uncertainty`,
  `applicability_outcome`, `applicability_trace`, `data_completeness`, `input_validation`

**So a qualified figure was rendered unqualified in the one surface built to audit it.** The endpoint
whose entire purpose is to prove nothing is overstated was itself overstating. It slipped past the
builder, past the orchestrator's own pre-gate validation, and past three of five reviewers. G1 caught it
by counting the contract's required fields, not by reading the code.

A second blocking item: `rule_conflict` — the typed competing-rules object the engine **deliberately
preserves for reviewers** — was dropped with no gap-marker branch, so a real conflict surfaced as a
generic "professional review required" with no statement of *what* conflicts.

**The fix that holds it shut** is schema-driven rather than hand-listed: wholesale deep-copy plus
**key-set equality against the app's own bundled `rule_evaluation.schema.json`**, so a field added to the
*source contract* and then dropped also fails. The two genuinely *relocated* fields are declared in the
response as `source_field_routing`, making "relocated, not omitted" machine-verifiable.

DCV re-ran its leaf classification across the rework: **1,339 → 1,413 leaves, 1,404 transported
byte-equal, 9 authored**, every one of the +74 newly carried leaves transported, and the authored set
growing by exactly the two routing-metadata entries. So the fix removed an omission and introduced **no
distortion** — which was the real risk, because a restored-but-reformatted legal qualification would have
been worse than the omission.

### The recurring pattern (write this on the wall)

**Every defect was a promise nobody had tested — and in almost every case the test that should have
caught it existed and was quietly checking something easier.** Hunt for it deliberately: take each
asserted invariant, ask what input would falsify it, then check whether any test sends that input.

### Process notes worth keeping

- **Carrying findings forward works.** M5-T012's two traps became M5-T013's *acceptance criteria*, and
  G5 verified they were **implemented rather than recited** by neutralising them in memory and watching
  exactly the right test fail. M5-T013 never repeated those defects — it failed a new way instead.
- **Orchestrator pre-gate validation earns its keep.** Run both documented commands, check diff scope,
  and read the producer report's evidence section *before* dispatching reviewers. An unfilled
  "to be finalized" section is a reliable tell that the documented command never completed.
- **Five agents corrected claims of their own** across the two tasks (producer SLOC and digest bases,
  G4's timing explanation, DCV's registry-row arithmetic, G1's mis-targeted mutation, G5's probe
  construction). That is the signal the review was adversarial rather than confirmatory.
- **Re-gate pattern:** rework in ONE consolidated pass, then `SendMessage` the SAME five reviewer agents
  a delta brief — they keep full context and re-verify cheaply. Tell each to reproduce **from the code**,
  not the producer's report.
- Accept drill matched first try both times because the DCV computed the material identity via the
  accept path's own `_task_git_identity(...)` and ran a **negative control** proving the staleness check
  is live. Always ask the DCV for the identity that way.

---

## 3. THE CODE GRAPH — built, but NOT wired into the loop (owner asked for this explicitly)

**It exists.** `tools/code_graph/` (a generator, a bounded query CLI, fixture tests) plus
`repo_index_assembly.py`, `repo_index_baseline.py`, `repo_index_cache.py`, `repo_index_incremental.py`,
`context_pack_index.py`, `memory_graph.py`. Built under task **M0-T030 (D-005 V1)**. The `code-graph` CI
job passes (determinism `--check` + fixture tests), as does `context-index-a1` and `context-pipeline`.

**It is advisory by its own design.** Its README's first section is a trust model stating: *"The graph is
an advisory navigation index, never authoritative truth."* The intended workflow is graph result →
likely locations → **read the actual source**, and source verification is **mandatory** for legal
semantics, security, the control plane, contracts, dependency impact, public interfaces, and any
acceptance or gate decision.

**It is NOT in the loop's execution path.** The supervisor contains exactly two references:

1. `tools/agent_supervisor/cli.py:1272` — a line that runs `python tools/test_code_graph.py`.
2. `tools/agent_supervisor/review_packet.py:294` — `full_code_graph` appears in
   **`PROHIBITED_MARKER_KEYS`**, the list of things a review packet may **not** contain, sitting next to
   `whole_repository`, `full_transcript`, `all_logs` and `all_historical_reports`.

So the supervisor's only substantive relationship with the graph is **forbidding anyone from dumping it
into a review packet**, as a token-budget defence.

**Neither Codex/the loop nor any producer or reviewer used it in this session.** They navigated with
Read/Grep/Glob. No report mentions it.

**Therefore no time or token saving can be claimed, and none should be.** There is no before/after
measurement and it was not in the path. Asserting a saving would be precisely the kind of untested label
that caused every defect in section 2.

**What actually controls tokens today:** the bounded review-packet ceiling (~64k tokens with a
conservative structural byte cap beneath it), the prohibited-dump list above, per-run budgets, and the
`context-budget` CI check that fails if `docs/SESSION_HANDOFF.md` exceeds ~4000 tokens.

**Measured per-run cost** (from the supervisor audit, runs `persistent-local-20` … `-29`): cumulative
context tokens 3.0M–5.8M per feature, peak live context 148k–243k. M5-T012's run was 5.33M cumulative /
212k peak; M5-T013's was 4.76M / 215k.

**Decision the successor should force, one way or the other:** either wire the index into the producer's
navigation step and **measure** whether it reduces tokens or wall-clock, or stop counting it as an asset.
It is a well-built tool nobody picks up. It is also fair to question whether a tool that requires
verifying every answer against source saves anything at all.

---

## 4. First push and first CI run — the big event

The owner authorised pushing the working branch (never `main`). Sequence actually executed:

1. `gh repo view` → **`"visibility": "PUBLIC"`** — correcting an in-session claim it was private (the
   handoff profile already documented it as public; it should have been read).
2. Because it is public, the whole unpushed history was scanned:
   `gitleaks detect --log-opts="origin/main..HEAD"` → **858 commits, 22.35 MB, 0 findings**, re-run
   immediately before the push.
3. `git push -u origin candidate/D-024-mrl-option-b` → 873 commits published; upstream now tracked.
4. `git ls-remote` verified **`main` untouched at `d8b3899f`** (19 August). No PR opened.

**CI fired for the first time in the project's life: 13 of 18 jobs green, 5 red.** Details and proven
causes are in `docs/SESSION_HANDOFF.md` item 5. The two most consequential:

- The **`exact-production-install`** job simulates Render's exact install path. 2,820 tests pass, 3 fail
  — and the 3 say the evidence route counts **zero** and the four analysis routes come back **empty** in
  the installed tree. Meaning the two features just accepted may **not register when deployed**. Cause
  undetermined; packaging config looks correct. This is the single most valuable thing the push found.
- The **`control-plane`** job says the directive registry is INVALID with 6 errors, while the identical
  command is EXIT 0 locally. Proven cause: the integrity digest is computed over **on-disk CRLF** bytes
  (`f62c6fc8`) while `.gitattributes` forces LF in git, so CI computes `0e9de4cc`. **The tamper-detection
  mechanism only validates on this one Windows machine.** Earlier sessions — including this one —
  recorded the CRLF behaviour as a trap to preserve. It is a defect.

**The unlock nobody expected:** `web` (lint + typecheck + build) and `web-e2e` (vitest + Playwright) both
**PASS**. The "no frontend-green path" wall that parked M5-T004 and every UI acceptance since **is gone**.
Also settled: Python 3.12 is fine (2,820 passed), so the local 3.11 collection gap was not hiding breakage.

---

## 5. Owner corrections and decisions (all binding going forward)

- **The repo is PUBLIC**, not private. Accept this and never place a secret in a committed artifact.
- **Never ask the owner to paste a key into chat.** The owner objected, correctly. A key in a transcript
  is a key that must be rotated. Secrets go to Render's encrypted env store or an OS secret store; code
  reads them from the environment; the assistant never possesses the value.
- **Render MCP:** the owner will grant a one-off exception to the zero-MCP posture so the assistant can
  create services, wire non-secret config, deploy and read logs. **The owner pastes every secret value
  personally.** The Render MCP *can* set env vars — deliberately do not use it for that.
- **Render's own database instead of Supabase for MVP.** Verified free-tier terms: Postgres is **1 GB,
  expires 30 days after creation**, 14-day grace, then permanently deleted; one per workspace; no
  backups. Free web services spin down after **15 minutes** idle with ~1 minute cold start; 750 instance
  hours/month. Recommendation given: use it now, treat everything in it as rebuildable from a script,
  and upgrade before day 30. `render.yaml` currently says `plan: starter` (paid) on both services and
  needs changing to free. It already declares `GEOCLIENT_SUBSCRIPTION_KEY` with `sync: false`, and
  `render.yaml` **is** present on `origin/main`, so Render can already see the blueprint.
- **"Draft, not a determination"** need not be surfaced to testers. Recommendation accepted: keep the
  marker **in the data** (it is what all the honesty machinery checks) and de-emphasise it **in the UI
  only**. Removing it from the engine would unpick accepted work and reintroduce the hole just fixed.
- **B-010 replaced by owner-proposed reverse-engineering validation** — see section 6.
- **B-011** (construction-code scope) explained and deliberately deferred: it gates *construction-code*
  work (egress, occupancy, structural), not the zoning MVP.

---

## 6. The reverse-engineering validation plan (owner's idea) — assessment

**The data exists and was verified.** NYC Open Data *DOB Job Application Filings* (`ic3t-wcy2`, 2.7M+
records) carries `existing_zoning_sqft`, `proposed_zoning_sqft`, existing/proposed dwelling units,
stories and height, `job_type` (NB = New Building), and `borough`/`block`/`lot` — i.e. a BBL. It is on
**Socrata**, the same platform `services/api/app/connectors/pluto_soda.py` already talks to, so the
connector pattern exists.

**The sharp edge — the comparison is a ONE-SIDED bound, not equality.** An architect files what the
client wanted to build, which is almost always **less** than the legal maximum. So:

- filed ≤ our computed maximum → consistent, expected, tells you little
- filed **>** our computed maximum → **our rule is wrong**, or there is a bonus/exception/overlay we have
  not modelled. Reality cannot exceed the law.

Run across a few hundred new-building filings, every violation is a genuine, ranked bug report. It finds
caps set **too low**. It **cannot** find caps set too high (an under-built site is indistinguishable from
a correctly-modelled one) — for that you would need a different signal, such as fully built-out sites or
DOB objection records.

**Terminology correction given to the owner:** the engine is deterministic and does not "learn". What
this produces is a **validation corpus** — a permanent regression suite of real properties with known
answers. That is more defensible than learning, because it is explainable to a client or a lawyer. Any
learning component belongs nowhere near the legal-number path.

**Storage is a non-issue.** ~2 KB per validation record: 300 buildings ≈ 0.6 MB; 5,000 ≈ 10 MB; 50,000 ≈
100 MB — against 1,000 MB free. The constraint is the 30-day expiry, not the gigabyte. The owner's
request for a low-space warning is a real, small feature: a scheduled check on database size **and the
expiry clock**, alerting at ~70% rather than at 99%.

---

## 7. npm / supply-chain investigation (owner asked before any front-end install)

**2026 incidents researched:** axios (March 2026, ~100M weekly downloads, compromised maintainer account,
postinstall payload); node-ipc (May 2026, credential/CI-secret stealer); Mastra + `@mastra` (June 2026,
140+ packages via one maintainer takeover, attributed to Sapphire Sleet). **Postinstall hooks are the
primary execution vector** in every case. npm v12 now blocks install scripts by default.

**Current state of this project — nothing compromised, evidence:**

- **No `node_modules` anywhere** — `apps/web`, repo root, `services/api` all absent. Zero project npm
  code has ever been unpacked or executed on this machine.
- Lockfile contains **no** known-compromised package: axios 0, node-ipc 0, `@mastra` 0, easy-day-js 0,
  plain-crypto-js 0.
- Seven packages from the chalk/debug incident **are** present but every one is on a **clean version**
  (checked against all 17 malicious versions; 0 matches). `debug` is on **4.4.3**, the post-fix release.
- `npm ci` in CI passed **lockfile + integrity verification** — every tarball matches its recorded hash.
- **Age gate run manually** (CI skipped it after the audit failure): **PASS — every committed package
  ≥ 7 days old**, newest `ws@8.21.1` at ~58 days. A fresh compromise means a fresh version; there are none.
- Python: pip-audit **zero advisories** on both production and tooling locks; age gate passed.

**The 7 CI findings are vulnerabilities, not compromises** — bugs written by the legitimate authors, not
hostile code. Nothing to rotate. But the **Next.js unauthenticated RCE is critical** and the web app must
not be deployed until it is fixed.

**Existing policy vs the owner's checklist** (`docs/DEPENDENCY_SECURITY_POLICY.md`): zero advisories at
any severity; **≥ 7 days old** (owner wants 14 — one number to change); exact pins + lockfile integrity +
deterministic installs; official registry only; audited on every change and on a schedule; provenance
review covering typosquats and maintainer/ownership changes; **no agent waiver, no allowlist, no
suppression, no exception path**. Four enforcement layers for npm plus a Python parallel.

**Two real gaps found:** (a) `ignore-scripts=true` is set at **user level** (`npm config get
ignore-scripts` = true) — so this machine is protected but **CI runners do not inherit it**; commit it
into the repo. (b) No download-count/popularity floor (noting axios had 100M weekly downloads and was
still compromised, so popularity is a weak signal alone).

Also noted on the machine, not part of this project: global `npm` is **11.4.2** while CI pins 11.18.0;
`expo@51.0.14` is old; `supabase` printed with **no version**, possibly a partial install.

---

## 8. What the MVP actually delivers (answer given to the owner)

**Rule coverage is R5-family only — seven rules:** `r5-residential-far` (max FAR + max residential floor
area), `r5-height`, `r5-qrs-height`, `r5a-height`, `r5b-height`, `r5d-height` (base/building/perimeter
wall heights), `r5-setback` (required setback depth). Anything outside R5/R5A/R5B/R5D correctly returns
no coverage rather than guessing.

**Screens that exist in the pushed branch:** home, `/property` (BBL lookup), `/property/confirm`,
`/dashboard`, `/survey/review` (+ `[documentId]`). **The Compare screen is on an unmerged branch and is
NOT in what was pushed.**

**The working tester journey:** type a BBL → live fetch from the real PLUTO database (**no key needed**)
→ profile built with every fact provenance-stamped → confirm → rule evaluation returns FAR, floor area,
heights, setback → evidence view shows the full chain.

**Built but with NO user interface:** the entire scenario toolkit (sensitivity, ranking, comparison,
break-even) and the evidence view. API endpoints only — a developer can call them; a tester clicking
cannot reach them. **Wiring screens to these endpoints is probably the highest-value remaining work.**

**Missing entirely:** address search (needs the Geoclient key — a tester must know the BBL, which no
normal person does), any login, any persistence, legal sign-off (everything stamped draft), construction
code.

**The honest client pitch:** not "it calculates your FAR" — a competent consultant does that better
today. It is **"every number is auditable, and the system tells you what it doesn't know."** Every value
arrives with its source, date, legal section, arithmetic, and an explicit statement of what is
conditional and unreviewed; when two rules conflict it names both; missing data is typed, never
defaulted. For an architect defending a pro-forma to a lender, that trail is the value.

Product-map launch weights, for prioritisation: rules_engine 22, scenario_engine 18, legal_corpus 15,
reporting_ops 15, property_intelligence 12, auth_tenancy 9, official_sources 6.

---

## 9. Mistakes made this session (recorded so they are not repeated)

1. **Claimed the repo was private.** It is public, and the handoff profile said so. Built a safety
   argument on an unverified premise.
2. **Asked the owner to hand over an API key in chat.** Wrong, and the owner was right to object.
3. **Asserted a "~10s" test-suite timing that did not reproduce**, then over-corrected by saying it was
   simply wrong. G4 settled it: the identical 312-test baseline ran 37.31s under concurrent-reviewer load
   and 9.52s idle — a 3.9× host-load spread. Both readings were real.
4. **Treated the CRLF digest behaviour as a trap to preserve** and documented it as such. CI proved it is
   a defect that makes directive integrity valid on exactly one machine.
5. **Assumed the code graph had never been built.** It had. Verified before asserting the second time.

---

## 10. Open decisions awaiting the owner

- **Next.js RCE upgrade** — pulls `next` outside its stated range, so it is a genuine dependency change
  under the security policy. Recommended as the first real exercise of that policy.
- **Render MCP setup** — owner to create the API key and add the MCP; then services can be created.
- **Age gate 7 → 14 days**, and whether to add a download-count floor.
- **Whether to wire the code graph into the loop and measure it, or retire it as an asset** (section 3).
- Supabase timing (deferred in favour of Render Postgres for MVP).
- B-010 formally superseded by the reverse-engineering corpus; B-011 deferred to the construction-code
  milestone.

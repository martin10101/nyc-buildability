# NYC Buildability — MVP Review Q&A (for professional review)

Prepared 2026-09-12. Purpose: a plain-language, yes/no walkthrough of (1) how the platform is
designed and operated, and (2) exactly what a professional user — an architect, zoning consultant,
or development advisor — gets back from the program in its current MVP state. Every answer reflects
the actual, independently reviewed state of the system on this date, not aspirations.

**Honest framing up front:** the MVP is an internal/development build. All zoning rules in it are
DRAFT engineering awaiting qualified legal review — nothing it outputs is legal advice, a
compliance determination, or a substitute for a zoning attorney or a licensed professional. Every
screen carries that disclaimer.

How to use this document: read each question, form your own expectation, then check the answer and
its one-line rationale. Disagreements or surprises are exactly the feedback we want.

## Part 0 — How the owner's companion sessions work (read this first if you are the next session)

This document is the running record of an owner ↔ orchestrator Q&A/strategy conversation that
spans multiple chat sessions. The working model, set by the owner on 2026-09-12:

- **Two sessions run side by side.** The BUILD session owns the ledger (`project-control/`), the
  task queue, and `docs/SESSION_HANDOFF.md` — never touch any of those from a companion session.
  The COMPANION session (this conversation's successor) does owner Q&A, strategy, valuation, and
  planning discussions, and writes ONLY to this document (plus directive captures when the owner
  decides something).
- **Companion-session discipline** (learned, works): before any commit, check `git status` and
  confirm the staging area is empty (the build session shares the working tree); stage EXACT
  paths only; keep commits doc-only; never run `/session-handoff` (that file belongs to the build
  session); when the owner makes a real decision, capture it as a directive
  (`/directive-compliance`, D-040/D-041 are the recent templates) and notify the build session via
  a cross-session message with the directive id and priorities.
- **The conversation format:** rounds of yes/no questions with plain-language answers (numbering
  continues — next is **Q76**), follow-up deep-dives appended as new Parts, and candid
  bigger-picture feedback the owner has explicitly asked for ("don't be shy"). The owner asked for
  simple, non-technical language throughout — short sentences, analogies, no jargon without an
  immediate explanation.
- **Open threads for the next session** (refreshed end-of-night 2026-09-12): (1) **Render deploy
  checklist** — D-043 authorized the internal web deploy; the build session will produce the
  exact Render service settings + env-var checklist as an owner return item; walk the owner
  through applying it, then the owner types real addresses into the live internal site. (2)
  **Supabase credentials** expected from the owner (dashboards/env ONLY, never chat/files) —
  unlocks storage, then the M3 legal-corpus capture chain. (3) **Design phase** — all inputs now
  exist: `docs/design/competitor-report-presentation-research.md` (2 passes),
  `docs/design/astra-presentation-research.md`, `docs/design/ui-inspiration/` (+README
  corrections), `docs/design/ui-prototype.html`, and Part 10's locked rules; next step is the
  design-director spec, Astra critique via its review channel, then implementation packets.
  Astra's companion mockup file (nyc_zoning_result_mockup.html) was never received — ask the
  owner for it. (4) **Valuation** — verify Part 9 price anchors live before any external use
  (partial verification already in the two research docs). (5) **Architect demo prep** using
  this document + the prototype. (6) The **clickable prototype artifact** ("Buildability
  Prototype") belongs to a prior session — find it via `/artifacts` (or Artifact action:list)
  and pass its URL as `url` when republishing `docs/design/ui-prototype.html`; keep the repo
  copy and the artifact in sync. (7) Pricing research already priced: G6 + coverage move
  willingness-to-pay most — keep nudging the owner on the lawyer call.
- **Where everything from the 2026-09-12 marathon lives:** decisions → directives D-039..D-043;
  design rules → Part 10; gap list → Part 4 (incl. B5 ACRIS, E3 assemblage, F build-tooling);
  valuation → Part 9; research → the two docs/design research files; the look → ui-inspiration/
  + ui-prototype.html. Nothing important exists only in a chat transcript.

---

## Part 1 — Platform design and safety (20 questions)

**Q1. Does the frontend ever calculate zoning or legal results itself, rather than just rendering
what the API returns?**
No — deterministic code calculates server-side; the frontend only transports and renders.

**Q2. Is the address search validated on the client before it's sent to the server (like the BBL
field is)?**
No — deliberately. The city-data connector is the sole validation authority; the only client guard
is an inert submit button when both house number and street are blank.

**Q3. When the city's Geoclient service returns multiple possible street matches, does the platform
pick the most likely one for the user?**
No — the source's `caller_selects` policy is honored literally: no default selection, no highlight,
and the confirm button stays disabled until the user actively chooses.

**Q4. Can the address-entry UI appear for users when the internal feature flag is off?**
No — flag off renders today's BBL-only screen byte-equivalently, and the address surface never
mounts or fetches.

**Q5. Does every material fact shown to a user (like a lot's BBL or a rule value) carry provenance
back to an official source?**
Yes — provenance (source ID, original value, retrieval time, dataset version, digest) is mandatory;
a value without it is treated as a defect.

**Q6. Is the Geoclient subscription key allowed to appear anywhere in the repository or in API
responses?**
No — it exists only in the owner's machine environment and the hosting dashboard.

**Q7. Can a worker agent mark its own task complete?**
No — producers submit evidence; only independent gates and the orchestrator accept.

**Q8. Does the platform run its frontend test suite locally on the owner's PC?**
No — thin-client policy (limited disk): no local `node_modules`; continuous integration is the
executable authority.

**Q9. If the API returns an HTTP status + error state combination that isn't in the documented
matrix, does the UI still try to interpret the body?**
No — it renders a distinct "unexpected response" card and refuses to trust the body.

**Q10. Are hostile strings echoed back by the server (like a `<script>` tag typed into the street
field) rendered as inert text?**
Yes — text-node escaping plus bounded-length/character filtering; tests assert no injected element
or attribute ever materializes.

**Q11. Does a "resolved with warnings" address result block the user from continuing?**
No — warnings render beside the result (visible, never hidden) but never gate continuing.

**Q12. Is the "Continue with this lot" button on the resolved-address card functional today?**
Yes — as of the current increment it links into the existing property-confirm flow, built only
from a client-re-validated lot identifier. (At the time of the first review set it was an honest
disabled stub; the follow-up increment made it live.)

**Q13. When two address lookups race, can the older response overwrite the newer result on
screen?**
No — a monotonic request sequence plus abort guard discards superseded responses even if the
transport ignores cancellation.

**Q14. Are screen-reader users told when a lookup outcome arrives, even if the same failure
repeats twice in a row?**
Yes — one persistent live region per state machine announces each arrival, clearing during loading
so identical repeats re-announce.

**Q15. Can a new npm package be added to the web app if it was published to the registry three
days ago?**
No — dependency policy requires every version to be at least 7 full days old, advisory-free, and
exact-pinned, with gates that fail closed.

**Q16. Is PR #241 allowed to be merged?**
No — standing owner hold; it must stay unmerged.

**Q17. Does an unknown `status` value from the address service get displayed as "address not
found"?**
No — it gets its own "form we don't recognize" card with the raw status shown as a bounded token;
unknown is never coerced to not-found.

**Q18. Are the ZoLa map deep-link and the real lot outline both shipped in the current address
packet?**
The ZoLa deep-link: yes (current increment, built only from the validated BBL). The drawn lot
outline: no — it is under an owner-review expansion hold; the ZoLa link is the authoritative
outline meanwhile.

**Q19. Does the backend state machine (not AI) control workflow states like whether a rule is
published?**
Yes — AI may not skip states or declare compliance; publication requires source linkage, tests,
independent review, and qualified-reviewer approval.

**Q20. If the city's service throttles the platform, does the error card blame the user's input?**
No — rate-limit, key, and server-side errors explicitly say nothing is wrong with the user's
input.

---

## Part 2 — What an architect gets back from the MVP (35 questions)

### A. Getting a property in

**Q21. Can I start from a street address instead of typing a 10-digit BBL?**
Yes — the new address search resolves a house number + street + borough (or ZIP) through the
city's official Geoclient service. (Internal feature flag in the MVP.)

**Q22. If my address matches more than one street, will the program guess which one I meant?**
No — it lists the city's own suggestions in the city's own order and waits for your choice.

**Q23. Do I get back the city's official tax-lot identifier (the 10-digit BBL) for the lot I
confirm?**
Yes — the canonical BBL, re-validated on the client before it is used anywhere.

**Q24. Can I jump straight from a resolved address to the city's official ZoLa map for that
parcel?**
Yes — a one-click link built exclusively from the validated BBL (never from anything typed or
echoed).

**Q25. Does the program draw the parcel outline itself in the MVP?**
No — honestly deferred (a pin or rough outline would mislead on corner and large lots); the ZoLa
link shows the authoritative outline.

### B. The property profile

**Q26. Do I get the lot's zoning district(s), including split-lot cases with more than one
district?**
Yes — split-zone lots show every district.

**Q27. Do commercial overlays appear when present?**
Yes — overlays are listed alongside the districts.

**Q28. Are lot facts (like lot area) returned with explicit units?**
Yes — values always carry their units (e.g., square feet), never bare numbers.

**Q29. Do I also get facts about the existing building on the lot?**
Yes — an existing-building facts section from the official data.

**Q30. If a fact is missing from the official data, will the program fill it in with an
estimate?**
No — missing inputs are listed as missing, by name. Nothing is silently defaulted.

**Q31. If two official sources disagree about a fact, is that conflict shown to me?**
Yes — a visible data-conflicts section; conflicts are never resolved silently.

**Q32. Can I trace every material fact to its official source, dataset version, and retrieval
time?**
Yes — per-fact provenance with a reproducibility line (source, dataset release, retrieval time,
reference ID).

**Q33. Does the profile tell me how complete the underlying data was?**
Yes — an explicit data-completeness statement against the documented feasibility field set.

### C. Zoning rules and analysis

**Q34. Does the MVP contain deterministic zoning rules for residential floor-area ratio (FAR)?**
Yes — a residential-FAR rule family (R1 through R12 districts) is implemented and tested.

**Q35. Are height/setback rules present as well?**
Yes — an R5-family height/setback rule set, same draft status.

**Q36. Are any of these rules legally approved ("published") yet?**
No — every rule is DRAFT / needs-review until a qualified human legal review (a hard,
owner-level gate). The output says so.

**Q37. Does each rule evaluation cite the legal text it relies on?**
Yes — citation anchors to the captured legal source, including a cryptographic fingerprint of the
exact cited text.

**Q38. If the cited legal text changes upstream, will the system silently keep computing on the
old understanding?**
No — a fingerprint mismatch makes the rule registry refuse to load: it fails closed rather than
computing on drifted law.

**Q39. Does AI ever calculate a zoning number in the output I receive?**
No — AI retrieves, classifies, drafts, and explains; deterministic code does every calculation.

**Q40. Can the program declare my project "compliant"?**
No — it never declares compliance; legal interpretation and approval are reserved to qualified
humans.

### D. Scenarios and numbers

**Q41. Do I get a draft residential zoning-floor-area cap for the lot?**
Yes — clearly labeled as a DRAFT cap, with the label text saying exactly that.

**Q42. When the program optimizes something, is the objective always named (never just "best")?**
Yes — e.g., "max residential floor area (sq ft)" is named on screen; "best" alone is banned.

**Q43. Are values shown exactly as computed — no silent rounding away of fractions?**
Yes — a fractional cap renders with its fraction; display-magnitude regressions are test-guarded.

**Q44. Does the MVP include sensitivity analysis around scenario inputs?**
Yes — an accepted scenario-sensitivity capability is part of the scenario engine.

**Q45. Is there a break-even style analysis in the scenario engine?**
Yes — an accepted break-even capability, with the same draft/provenance discipline.

**Q46. Are scenario results a building design or a 3D massing?**
No — they are caps and analyses, not designs; 3D/massing work is a later, owner-gated expansion.

**Q47. If the data cannot support a scenario (a conflict, an unsupported check, or a
professional-review trigger), does the screen show an explicit explanation instead of a number?**
Yes — dedicated branches state exactly why no number is shown; a professional-review flag is
raised where human judgment is required.

### E. Trust, labels, and delivery

**Q48. Will anything in the MVP output be labeled "Verified"?**
No — nothing is "Verified"; retrieval confidence is never dressed up as vouching.

**Q49. Are professional-review flags shown to me when human review is required?**
Yes — visibly, on the results, never buried.

**Q50. Is there an on-screen disclaimer that this is not legal advice?**
Yes — rendered on every page.

**Q51. Can I get at the evidence behind a rule evaluation (the audit trail)?**
Yes — an evidence endpoint exposes the evaluation trace (internal flag in the MVP).

**Q52. Is the MVP publicly deployed for outside users today?**
No — internal/development only; public hosting is owner-gated behind a pending security fix.

**Q53. Are the newest surfaces (rule evaluation, address search, evidence) behind an internal
feature flag?**
Yes — off by default; flag-off users see the stable base experience.

**Q54. Does every screen outcome — including failures — show a reference ID I can quote to
support?**
Yes — a correlation ID on every outcome card, tied to the server logs.

**Q55. Was every user-facing feature above independently reviewed (code, QA, security, and
design/accessibility) before being accepted?**
Yes — every task passes producer-independent review gates before acceptance; reviewer and producer
are never the same identity.

---

## Part 3 — Professional follow-up questions, round 1 (owner, 2026-09-12)

**F1 (re Q25). Can the drawn parcel outline be added to the MVP and fully tested end to end?**
Yes — it is technically feasible and already designed as the third increment of the address flow:
the city's MapPLUTO parcel geometry (official DCP dataset) rendered with a standard map library,
under the same connector/fixture/test/review discipline as everything else, and it can be tested
end to end against recorded official geometry the same way the rest of the UI is. Two honest
caveats: (1) it currently sits under an explicit owner-review hold on expansion work, so the owner
must release that hold before it is planned or built — that hold, not difficulty, is why it is not
in the MVP; (2) it needs a new data connector (parcel geometry), which is a real, bounded piece of
work with its own review gates.

**F2 (re Q24). How does the ZoLa link work — new tab? security risks? what if the city's site is
down or errors?**
Mechanics: the link is `https://zola.planning.nyc.gov/bbl/<10-digit BBL>` — ZoLa's own documented
inbound route for exactly this purpose (verified against the city's published source code); ZoLa
itself then shows that lot's view. The address part of the URL is a fixed constant; the only
variable part is the 10-digit BBL, and only after it passes our own re-validation.
New tab: yes — it opens in a new browser tab, with the `noopener noreferrer` protections, meaning
the opened site cannot reach back and control our page (a known attack called tabnabbing) and our
page's address is not leaked to it.
Security posture: (1) no typed or echoed text can ever enter the link — only the validated
digits; (2) it is a plain outbound link — we never embed or load ZoLa content inside our app, so
nothing from their site executes in ours; (3) the residual risk is simply that it is an external
government website we do not control.
If the city's site is down or errors: the failure happens in the new tab, on the city's side —
our app is unaffected and keeps working. One honest limitation: ZoLa is built so its server
answers "OK" for almost any address path and reports problems inside its own page (for example,
certain condo billing lots it cannot display) — so we cannot cheaply pre-check "will ZoLa show
this lot?" before you click, and we deliberately do not pretend to.

**F3 (re Q29). What existing-building data, and can an architect use it to redesign?**
What the MVP returns today: the official citywide property record of what stands on the lot — the
attributes in the documented feasibility field set, such as existing built floor area, stories,
year built, building class, and unit counts — each with explicit units, a coverage status, and a
source trail. Think "the city's data sheet for the building," not drawings.
Can an architect redesign from it? It supports FEASIBILITY-stage judgments well: how much floor
area exists versus the draft cap (i.e., what development rights remain), whether an existing
building already exceeds today's draft cap (a likely grandfathered condition worth flagging to
counsel), enlargement-versus-new-build framing, and unit-count context. It is NOT sufficient for
actual redesign documents: there are no floor plans, sections, facades, structural data, interior
layouts, or survey-grade dimensions — a licensed survey and site investigation remain necessary,
exactly as they would with any data service.
What a professional would reasonably expect next from a program like this (candidly, not all in
the MVP): remaining-development-rights math shown explicitly, DOB permit/violation/certificate-of-
occupancy history, landmark/historic-district status, and the parcel footprint. Those are known,
tracked directions — feedback on their priority is exactly what this review is for.

**F4 (re Q30). If a fact is missing, will it still show the other info?**
Yes. Missing data never blanks the screen: everything that IS available renders normally; the
missing items are listed by name in their own section; the completeness statement reflects the
gap; and any calculation that NEEDS the missing fact is shown as blocked/unsupported with the
reason, rather than silently computed. One missing fact degrades exactly the parts that depend on
it, nothing more.

**F5 (re Q34). Is all of R1–R12 built? Special zonings, waterfront? Sub-calculations like street
width, overhangs?**
Precisely: what exists is the BASE residential floor-area-ratio rule family for the R1–R12
districts — implemented, machine-tested, citation-anchored, and DRAFT. What does NOT exist yet,
and the output never pretends otherwise: special purpose districts, waterfront zoning, contextual
and bonus programs (e.g., inclusionary housing), and the geometry-dependent computations — street-
width-dependent height rules, sky-exposure planes, permitted obstructions/overhangs. Those need
both new rule sets and, in some cases, new data inputs (street width and parcel geometry are data
the MVP does not ingest yet). The architecture is deliberately built so each of these lands as its
own bounded, cited, independently reviewed rule set; anything not implemented shows up as
unsupported rather than guessed.

**F6 (re Q35). Height/setback for the other districts besides R5?**
Not yet. R5 was the pilot height/setback family; it proved the pattern (citations, deterministic
evaluation, tests, independent review). FAR coverage is R1–R12; height/setback coverage is R5
only today. The remaining districts are roadmap items that follow the identical pattern, one
reviewed family at a time — breadth is added deliberately, never by loosening the discipline.

**F7 (re Q38). Explain the legal-text fingerprint much better.**
When a zoning rule is built, we store the exact text of the Zoning Resolution passage it relies
on, and we compute a digital fingerprint of that exact text — a SHA-256 hash, which works like a
tamper-evident seal: change even one character of the text and the fingerprint comes out
completely different. That fingerprint is recorded inside the rule itself.
Every time the system starts and loads its rules, it re-reads the stored legal text and recomputes
the fingerprint. If the recomputed fingerprint does not match the recorded one — because the law
was amended, our captured copy was updated, or anything corrupted the text — the rule registry
REFUSES to load. It does not warn-and-continue, it does not fall back to the old understanding; it
stops, and a human must re-review the rule against the changed text and re-approve it.
The principle: no answer is safer than an answer computed on law that shifted underneath us.

**F8 (re Q42). Where does the optimized number come from if the zoning laws "aren't built yet"?**
The laws it uses ARE built — that is exactly what the R1–R12 draft FAR rules are. The draft cap is
plain deterministic arithmetic: the lot's official area (from city data, with provenance) times
the district's residential FAR (from the draft rule, which cites the exact Zoning Resolution text
it encodes). "Draft" does not mean invented — it means engineered, machine-tested, and
independently reviewed, but NOT yet signed off by a qualified legal reviewer; that is why every
number carries the DRAFT label and its citation trail. And the program only optimizes within the
rules it actually has: the named objective ("max residential floor area, sq ft") tells you exactly
which quantity was maximized, and anything the rule set cannot support is declared unsupported
instead of estimated.

**F9 (re Q44). Explain sensitivity analysis better.**
It answers the question: "how fragile is this number?" The engine re-runs the scenario with key
inputs varied — for example, if the lot area were slightly different, or a disputed input took its
other plausible value — and reports how much the result moves in each case. The output shows which
inputs the answer is most sensitive to. For a professional, that is the difference between "this
cap is robust" and "this cap hinges entirely on one uncertain fact — commission the survey before
relying on it." Same rules apply as everywhere else: explicit inputs, draft labels, provenance,
nothing hidden.

**F10 (re Q45). What does break-even mean here?**
Break-even is the point where a project stops losing money — where the value it creates equals
what it costs. In the scenario engine it is a screening calculation: from a scenario's draft
buildable area and a set of explicitly stated assumptions, it computes the threshold at which the
scenario's economics cross from loss to viability — the "it must clear at least this bar, or it
does not pencil" line. Every assumption is a visible, recorded input (never a hidden default), and
the output carries the same draft/provenance discipline as everything else. It is an early
screening aid — not an appraisal, not a lender-grade pro forma, and not investment advice.

---

## Part 4 — Gap list: what the MVP still needs (candidate backlog for OWNER TRIAGE)

Compiled 2026-09-12 from Parts 1–3 and the live project state. **Status of this list: candidates
only.** Nothing here is planned, contracted, or authorized by this document; items marked
OWNER-GATED or ON HOLD require an explicit owner action before anyone may even plan them. Order
within each group is a suggested priority, not a decision.

### A. Zoning-rule coverage (buildable under the normal task/gate process)

1. **Height/setback rule families beyond R5** — R1–R4 and R6–R12, one cited, tested,
   independently reviewed family at a time (the R5 pilot proved the pattern). Unlocks: a real
   envelope picture per district instead of FAR-only.
2. **Geometry-dependent rule mechanics** — street-width-dependent height limits, sky-exposure
   planes, permitted obstructions/overhangs. Depends on new data inputs (street width, parcel
   geometry — see B1/B2); rules and inputs should be sequenced together.
3. **Contextual and bonus programs** — Quality Housing/contextual variants, inclusionary-housing
   style bonuses. Materially changes caps; high professional value; needs careful legal sourcing.
4. **Special purpose districts and waterfront zoning** — large, self-contained rule bodies;
   candidates for later waves after the citywide base is broad.

### B. Data connectors (each needs a source-registry record, fixtures, contract tests)

1. **Parcel geometry (MapPLUTO)** — the footprint/outline data. Prerequisite for the drawn lot
   outline (D1) and for geometry-dependent rules (A2). *The outline UI itself is ON HOLD — see D1
   — but the geometry connector is also independently useful for rule inputs.*
2. **Street width / mapped-street data** — required by A2's street-width rules.
3. **DOB records** — permits, violations, certificates of occupancy. Directly requested in the
   professional review (F3): "what has the city already said about this building?"
4. **Landmark / historic-district status** — a binary that changes everything about a project;
   cheap to surface once connected.
5. **ACRIS zoning-lot-agreement check** (added 2026-09-12 from the merged-lot discussion) — query
   the city's recorded-documents system for zoning-lot agreements touching the block/lot, turning
   the "assumes tax lot = zoning lot" blind spot into a real warning with the document reference.
   Official public data; few competitors do this well — a candidate signature feature.

### C. Professional-workflow output (what an architect asked for in this review)

1. **Explicit remaining-development-rights math** — existing built floor area vs. the draft cap,
   shown as its own labeled line ("approximately X sq ft of unused draft floor area"), with the
   same draft/provenance discipline. Most of the inputs already exist in the profile today.
2. **Grandfathered/over-built flag** — when the existing building already exceeds the current
   draft cap, say so explicitly and route it to the professional-review flag (counsel question,
   never a program conclusion).
3. **Condo/billing-lot honesty note** — surface the known caveat (some condo billing lots
   resolve oddly and may not display on ZoLa) directly on the confirm card when it applies.

### D. OWNER-GATED / ON HOLD (require an owner decision before any planning)

1. **Drawn parcel outline + map view (address Packet 3)** — ON THE OWNER-REVIEW EXPANSION HOLD.
   Feasible and designed (F1), but the hold must be lifted first. Also depends on B1.
2. **3D massing / envelope visualization** — same expansion hold; later tier of the same
   decision.
3. **G6 qualified legal review of the draft rule families** — the single step that turns DRAFT
   rules into published ones. Owner-only (Section 20 hard stop). Until then, every number stays
   DRAFT — correctly.
4. **Public deployment** — blocked on the owner-authorized Next.js security-fix upgrade (the
   standing npm-audit red) and a deployment posture decision; includes deciding when the
   internal feature flags (rule evaluation, address search, evidence) come off.
5. **Durable cloud storage / accounts (Supabase, blocker B-001)** — owner credentials required.
   Unlocks saved lookups, user accounts, persisted scenarios — the "come back tomorrow" workflow
   a professional expects.
6. **Feature-flag unification** — frontend `INTERNAL_RULE_EVAL_UI` vs backend
   `INTERNAL_RULE_EVAL_ENABLED` (security review's carried note). Deploy-affecting rename; small,
   but owner-scheduled.
7. **Control-plane digest normalization** — the second standing CI red; an internal bookkeeping
   decision with no user-facing effect.

### F. Build-tooling notes (owner Q&A 2026-09-12; developer tooling, NOT product features)

1. **LSP (Language Server Protocol) — assessed, DEFERRED.** Would catch typing mistakes before
   push (one such miss cost a CI round-trip on M5-T016 night), but the TypeScript server is
   blind without a local `node_modules` (~0.5 GB), which the thin-client disk policy deliberately
   excludes, and the local Python 3.11 would false-alarm on the repo's 3.12 syntax. Navigation
   needs are already covered by the homegrown code-graph (D-005). Revisit if the disk constraint
   lifts or CI wait times start dragging the loop; enabling it is an owner policy tweak + one
   install.
2. **Code-graph use by the Codex loop — status and why.** The loop does NOT automatically consult
   `tools/code_graph`: (a) D-005 amendment 2 made graph use selective/advisory, and packets
   pre-name exact files so producers rarely need discovery; (b) the Codex reviewer (Astra)
   receives bounded text packets through the bridge — no shell — and the packet guard explicitly
   forbids full-graph dumps (bulk-payload denylist in `review_packet.py`); (c) the D-006
   auto-wiring idea predates the supervisor freeze (D-024), so it was never built. Known cost:
   the M4-T009 cross-suite miss (consumers assuming a single-member rule family). Actions: NOW —
   contracting checklist requires a who-consumes graph query for any task growing a shared
   family/collection (orchestrator practice, no governance change); LATER (owner-gated) —
   targeted graph excerpts in Astra review packets = a supervisor change under the D-024 freeze.

### E. Adjacent professional expectations (surfaced by this review; not yet scoped)

1. **Shareable report/export** — a professional will eventually want to hand a client a document,
   not a screen. Known product direction; not yet scoped as tasks.
2. **Saved searches / portfolio view** — depends on D5 (storage) landing first.
3. **Assemblage mode** (added 2026-09-12 from the merged-lot discussion) — select multiple tax
   lots, compute the combined draft floor area with an explicit "Assumed: these lots form one
   zoning lot" tag. The single-lot-inside-a-merger case stays a professional-review flag (only
   the recorded agreement can answer it).

*Reading guide for the reviewer: groups A–C proceed under the project's normal independent-review
process once prioritized; group D items each wait on a specific owner action; group E is
direction, not commitment. The right output of your review is a priority order over A–C and E,
plus any missing rows.*

---

## Part 5 — How the program is organized (a plain-language tour)

Think of the program as an office building. Each floor has one job and is not allowed to do the
others' jobs. That separation is the most important design decision in the system.

- **Floor 1 — the storefront (`apps/web`).** Everything a person sees and touches. Each screen
  piece is its own file (the address form, the match chooser, the confirm card, the traffic-cop
  that decides which to show). Small toolboxes handle the phone line to the back office, the
  "safety gloves" for anything the outside world sends, and the announcer for blind users. A test
  file sits next to every screen, like a fire extinguisher next to every stove. **House rule: the
  storefront may not do math.** It only displays what the back office says — so a wrong number can
  only ever come from one place.
- **Floor 2 — the back office (`services/api`).** The brain. Its departments: **connectors** (the
  clerks who call the city and write answers down word-for-word, with date/time and a receipt
  number — forbidden from interpreting; a strange answer stops the line); **rules** (the law
  library — each rule stapled to the exact sentence of law it came from, plus the tamper-evident
  fingerprint); **scenario** (the calculators: cap, sensitivity, break-even — official inputs
  only); **api/v1** (the service windows the storefront asks questions at). Tests mirror
  everything.
- **Floor 3 — the shared dictionary (`packages/contracts`).** The storefront and back office
  agree on exactly what every word means. Breaking the dictionary sets off automatic alarms.
- **Floor 4 — the filing room (`project-control`).** Every task's paper trail: what was asked,
  who built it, which independent reviewers checked it, what they found, when it was accepted.
  The owner's instructions are stored word-for-word. Nothing important lives in anyone's memory.
- **Floor 5 — the manuals (`docs`).** Design plans, policies, session handoffs, this document.
- **The basement (`tools`, `.claude/rules`).** The machinery that runs the project itself, plus
  house rules that load automatically per work area.
- **The inspection line (CI).** Every change triggers thousands of automatic checks — tests,
  security scans, size checks, dictionary checks. Nothing lands without passing.

Why divided this way: (1) small pieces can be truly checked; (2) lies get caught at the borders —
screens can't calculate and clerks can't interpret, so blame always has one address; (3) any piece
can be replaced without breaking the rest.

## Part 6 — What will make a professional shrug, and what will make them lean in

**Honest premise: almost every raw fact in the MVP is publicly look-up-able.** The value is not
the data; it is the work done on the data, with receipts.

The shrug list ("I could get this myself"): the zoning district name (ZoLa), lot area / year
built / building size (PLUTO), address-to-lot, the ZoLa link itself.

The lean-in list ("I can't get this anywhere"):
1. **The math, done, with the receipt stapled on** — the draft cap computed and tied to the exact
   sentence of law, fingerprinted. Compresses an hour of careful cross-referencing into a second
   and shows its work. No public tool does the math.
2. **The honesty layer** — "this fact is missing", "these sources disagree", "ask a lawyer".
   Public tools never confess what they don't know; professionals get burned by that constantly.
3. **"How fragile is this number?"** — the sensitivity view; judgment support no public tool
   offers.
4. **"How much MORE can I build?"** — remaining development rights as one clear line. The
   ingredients exist in the MVP; the explicit line is gap-list item C1 — OWNER-APPROVED
   2026-09-12 (directive D-041) and queued for build.
5. **The paper trail as a service** — source, date, law text, reference number: protection the
   professional can pass to their own client.

The sentence the demo aims for: *"ZoLa tells me what zone I'm in. This tells me what I can do
with the lot — and proves it."*

## Part 7 — 20 more yes/no questions (the build itself) — Q56–Q75

**Q56.** Is the screen part ever allowed to do zoning math? **No** — screens display; the brain
calculates.
**Q57.** Is every screen, calculator, and city-clerk in its own file with one job? **Yes** —
machine-enforced size/responsibility checks.
**Q58.** If every screen were deleted, would the zoning brain still work? **Yes** — the back
office stands alone.
**Q59.** Can two parts share code nobody reviewed? **No.**
**Q60.** Does every piece have tests sitting next to it? **Yes** — thousands run on every change.
**Q61.** Can code reach users before an independent reviewer approves it? **No** — builder is
never approver.
**Q62.** Do the storefront and back office speak through one agreed dictionary? **Yes** — with
automatic alarms on breakage.
**Q63.** If the city changes its data shape, does the program quietly adapt? **No** — it stops
and flags; quiet adapting is how tools start lying.
**Q64.** Is there a drawer with every big owner decision saved word-for-word? **Yes.**
**Q65.** Could a new team reconstruct why everything was built from the files alone? **Yes.**
**Q66.** Can the program answer "where did this number come from" down to the sentence of law?
**Yes**, for every implemented rule.
**Q67.** Is any raw MVP data secret or exclusive? **No** — official public data; the value is the
work done on it.
**Q68.** Will the district name alone impress an architect? **No** — shrug list.
**Q69.** Is "how much more can I build" one clear line today? **No** — approved (D-041), not yet
built.
**Q70.** Does the program ever secretly pick "the best" option? **No** — every optimization names
its objective.
**Q71.** Do saved accounts instantly exist when Supabase plugs in? **No** — keys unlock building
it, through the same reviewed process.
**Q72.** Did the owner's unblocked items enter the queue? **Yes** — under full review like
everything else.
**Q73.** Is any part a black box even to the builders? **No** — deterministic, logged, reviewable.
**Q74.** Ready to show an architect for feedback? **Yes** — that is exactly what it is ready for.
**Q75.** Ready to sell today? **No** — rules are draft until legal sign-off and it is not publicly
deployed; both paths run through the owner.

## Part 8 — Candid notes to the owner (recorded at the owner's request)

1. **The moat is not the data.** Anyone can wrap ZoLa in a prettier screen. The defensible asset
   is the rules engine with receipts plus the honesty discipline. Weigh the backlog that way.
2. **C1 is the demo-maker** — small work, existing inputs, the line a professional leans in for.
   (Owner approved 2026-09-12; captured as D-041.)
3. **Start the G6 lawyer conversation now, in parallel.** It is the slowest item on the map, a
   relationship with lead time, and nothing technical substitutes for it.
4. **Show the real architect the current MVP now** — this document exists for that conversation;
   real feedback will re-order the backlog better than any internal plan.
5. **Decide who the customer is** (developer / architect / broker) before the product grows a
   personality; it shapes copy, priorities, and reports.
6. **The repository is public** — plans, strategy, and decisions included (no secrets; machines
   check every commit). As this nears a business, "competitors can read the roadmap" deserves a
   deliberate five minutes.
7. **Keep the "does the program lie?" instinct.** Demanding sources, refusing guesses, keeping
   humans over legal judgment — that discipline IS the product.

---

## Part 9 — What is this worth? (orchestrator's estimate, 2026-09-12 — informed opinion, NOT
market research; the next companion session should verify pricing live)

**What the manual work costs today.** For a straightforward NYC lot, an architect or zoning
consultant spends roughly **3–8 hours** on the first zoning pass: pull ZoLa/PLUTO, read the
relevant Zoning Resolution sections, compute max FAR, existing area, remaining rights, check
overlays, and write it up with citations. Complex lots (split zones, overlays, special districts)
run **10–30+ hours**. NYC professional rates run roughly **$150–$300/hour**; a purchased
preliminary zoning analysis for a small building commonly costs **$1,500–$5,000**.

**Honest correction to the 5-unit vs 10-unit framing:** zoning-analysis time scales with the
LOT's complexity, not the unit count. A 5-unit and a 10-unit on similar lots cost about the same
analysis time. The right unit of value is **per lot screened**.

**What the MVP + C1 saves per simple lot:** the data gathering, the FAR math with citations, the
remaining-rights arithmetic, and the write-up skeleton — realistically **2–4 hours per lot**
today (call it **$400–$1,000 of professional time**), growing toward most of the 3–8 hours as
rule coverage widens (heights, yards, more districts). The compounding win is **screening
volume**: evaluating 10 candidate lots is 30–80 manual hours versus an afternoon with the tool —
kill the bad deals in minutes, spend the expensive hours only on survivors.

**What that supports charging (anchors, to be verified live):** comparable property-data and
zoning-feasibility tools have charged roughly **$50–$300 per user per month**, with
generative-feasibility products (TestFit-class) reaching into the **thousands per seat per
year**. Sensible posture for THIS product: at MVP (draft rules, pre-legal-review) it is a
**screening tool with receipts** — pilot pricing around **$50–$150/user/month** (or ~$25–$75 per
lot report) is defensible because one saved lot-screen pays for the month. After G6 legal review
plus broader rule coverage, **$200–$500+/user/month** becomes defensible, and developer/brokerage
teams price higher than solo architects. The pitch math: ~3 hours saved × $200/hour = **$600 of
time per lot** against a ~$100/month subscription.

**The two things that most move the price:** (1) G6 — a lawyer-reviewed rule set moves the
product from "helpful screening" toward "relied-upon analysis"; (2) coverage breadth — every
added rule family converts more of the manual hours. Nothing else on the roadmap moves
willingness-to-pay as much as those two.

---

## Part 10 — Design lessons locked in (2026-09-12; from the three-way research + owner review)

Sources: `docs/design/competitor-report-presentation-research.md` (two research passes),
`docs/design/astra-presentation-research.md` (owner-supplied Codex research),
`docs/design/ui-inspiration/` (mockups + corrections README), and the owner's live review of the
clickable prototype (`docs/design/ui-prototype.html`, kept in sync with the published artifact).
These are the rules the future production UI must follow.

### For the PROGRAM (the engine)

1. **State the zoning-lot assumption on every result** — "treats the selected tax lot as the
   whole zoning lot" (ZR §12-10: tax lot ≠ zoning lot; recorded agreements can merge lots).
   Preferably a machine-readable assumption field, not just display copy.
2. **Five-tag status on every value:** Reported / Calculated / Assumed / Not assessed (shown as
   NOT CHECKED) / Needs review. "Not assessed" is never rendered as zero.
3. **Missing rule or input ⇒ "no supported estimate"** for that item — never a manufactured
   number.
4. **Name the computation precisely** — a FAR-only result is a *zoning floor-area* figure, never
   "maximum buildable area"; zoning floor area, gross building area, net area, and remaining
   capacity stay distinct terms.
5. **Frozen snapshots** — a saved/shared result keeps its date, inputs, and rule versions; an
   edited assumption produces a new marked result and retains the original.
6. **Merged-lot behavior:** single lot in a possible merger ⇒ review flag pointing at the
   recorded agreement (ACRIS); over-built-vs-own-FAR is the standing clue detector. Assemblage =
   user-asserted multi-lot selection tagged ASSUMED (gap-list E3); ACRIS agreement check is
   gap-list B5.

### For the WEBSITE (screens + report)

1. **Hero number first with its honest name and a one-line scope** ("FAR calculation only ·
   height, yards, building shape not assessed · treats this tax lot as the whole zoning lot").
2. **Report page 1 is the decision summary** — answer, formula, warnings; no decorative cover
   (competitor sample buries its answer on page 13 of 16).
3. **Every number opens its evidence** — exact record, law section with date, retrieval date,
   link to the exact page (never a vendor homepage; never ZoLa for a non-ZoLa value).
4. **Two warning kinds kept separate:** open questions on checked items vs items not checked at
   all; the ASSUMED single-zoning-lot row leads the checklist.
5. **No "verified"/"compliant"/PASS columns/scores** — only the five tags; digest checks read as
   "text matched" (mechanism, not vouching).
6. **PRELIMINARY, small, on every report page** — trade-standard phrasing ("Preliminary zoning
   analysis. Subject to verification and DOB review."), stated once per surface, never shouted.
7. **Screen, share view, and PDF render the same frozen snapshot.**
8. **No decorative 3D** — massing appears only when geometry was actually computed.
9. **Map stays subordinate** to the number; professional register throughout (no tutorial copy,
   no scare banners, plain words — owner corrections of 2026-09-12).
10. **Validate before locking:** number-first vs map-first is a hypothesis — test with real NYC
    architects on their own lots; if a user calls the draft "approved," the design failed.

*Status: all ten website rules are already applied in the clickable prototype (artifact label
`astra-lessons-applied`); program items 1 and 4 were handed to the build session for the C1
packet; the rest enter packets as their features are contracted.*

---

*End of Q&A. Feedback from professional reviewers — wrong emphasis, missing questions, answers
that don't match professional expectations — should go back to the owner for triage into the
project's tracked backlog.*

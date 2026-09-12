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

*End of Q&A. Feedback from professional reviewers — wrong emphasis, missing questions, answers
that don't match professional expectations — should go back to the owner for triage into the
project's tracked backlog.*

# Back and forth: owner ↔ developer (AI), 2026-10-11

A shortened but complete record of the conversation between the owner (not a developer; building the app with AI) and
the developer AI on 11 October 2026: what the owner asked, what was answered, what was decided, what is done and what
is still to do. Written so another AI or an architect can follow it without the chat.

Status words used below: **DONE** (finished and checked), **RECORDED** (saved as an owner instruction the build must
follow), **TO DO** (owed work), **OPEN** (waiting for the owner's decision), **ANSWERED** (a question answered, nothing
to build).

## Background in three lines

- The app: a New York City zoning feasibility tool. You type an address; it gathers official city data, applies
  zoning rules step by step, and produces results on a website and in a PDF report for architects.
- The test property: 215-16 Northern Boulevard, Bayside, Queens (block 7334, lot 70; R6B with a C2-2 commercial
  overlay; a corner lot). The owner chose it on 28 September by giving the competitor's report on the same lot.
- The competitor: an 88-page "Zoning Analysis and Massing Study" of the same lot (dated 18 September 2026). It looks
  finished (11 options worked, section drawings, 3D blocks, floor plans) but some figures have no stated conditions
  and the owner's outside reviewer found errors in it.

## 1. Morning: finishing the previous round of work

- **What happened:** on resuming, the AI found that one automatic browser test had been failing on every upload since
  05:48 UTC, and that four pieces of work had been approved while it was failing, without anyone reading the test
  results. That broke the owner's rule that the full tests must pass before anything is approved.
  - **DONE:** the test was out of date (the result was right); a small repair fixed it. Every later approval was made
    only after the full test results were read green. The lesson is saved: read the test results before every
    approval, merge and handoff.
- **What happened:** a test print of the report showed a contradiction: page 1 and open item 6 said "No legal
  apartment limit is shown" while page 8 showed the conditional 29-unit limit.
  - **DONE:** the wording now follows the results ("shown as a conditional ceiling for standard residences; not known
    for qualifying affordable or senior housing"), each with its own reason. "Conditional" is said only when the
    limit's own recorded state is conditional.
- **DONE:** the round was merged into the main version. It includes:
  - the special density area read from the city's records (this Queens lot is outside both areas, so the standard
    legal apartment limit shows as a conditional 29);
  - the zoning-lot warning from the city's register of recorded documents (a 2022 zoning lot description names lot
    70 together with lot 1, so every lot-area figure carries that condition; the documents themselves were not read);
  - law links that open the exact section of the Zoning Resolution;
  - a research record on the street wall, setback and side yard;
  - the browser-test repair and the apartment-limit wording fix.
- **TO DO:** one research record (the zoning-lot documents record) needs its links to the program refreshed after
  the wording fix; no fact in it changed.

## 2. The new PDF

- **Owner:** waiting for the new PDF. **Developer:** sent it (9 pages, printed from the merged main version) with
  website screenshots at desktop and phone size and a change list. Every page was inspected; every law link was
  opened and lands on the right section.
- **Owner:** "Give me the link." **Developer:** gave the pull request link, the research-records link and the local
  preview link; the PDF itself was an attachment.
- **Owner:** "Yes give me the PDF." **Developer:** re-sent it and made a private web page with all 9 pages and the
  PDF.
- **Still unresolved in that PDF (TO DO):** page 1's answer table has no row for the legal apartment limit; the
  opening lot sentence is generic; rear yard beyond the corner, setback above the base and the street wall are not
  worked out; "see item 4" references are plain text, not links.

## 3. The outside reviewer's audit of that PDF (forwarded by the owner: "Do u get this?")

- **Reviewer's points:** the facts improved, but the presentation did not.
  - Improvements to keep: the zoning-lot flag (lots 70 and 1); the conditional 29 calculation; exact law links.
  - The 29 does not prove 29 units can be built.
  - Page 1: results compete with warnings, assumptions and a feature list; the architect has to assemble the answer.
  - Pages 2-3: repeated maps; the property stays small; the constraints page needs a close-up with dimensions on the
    boundaries.
  - Page 4: five limitation paragraphs come before the comparison; most rows describe unfinished work.
  - Page 5: three stacked rectangles show floors, but no footprint, placement, circulation or apartment arrangement.
  - Pages 6-9: explanations repeat; much belongs in one organized evidence appendix.
  - The "17-22 apartments" estimate is on page 1 but the "29-unit ceiling" is on page 8; they belong together, with
    one line telling them apart; neither is a demonstrated layout.
  - The rear-yard analysis omits the short-block exception, ZR 23-344(b); it needs an explicit applicability check
    (the reviewer did not say the exemption applies).
  - The report gained about 10% more text; the next version must not grow.
  - Next pass: (1) rebuild page 1; (2) finish one meaningful option (dimensioned footprint on the site, a section, a
    floor schedule that adds up, untested constraints named); (3) before-and-after screenshots of every changed page
    and website view, checked against the design rules. Keep all eleven options in scope. The goal is an architect
    understanding the property faster.
- **Developer:** yes, understood. **RECORDED** as owner instructions (18 numbered requirements).
- **Developer on the rear yard:** the research already exists (a conditional reading that no rear yard may be needed
  under 23-344(b), awaiting independent review), but the program only applies the 100-foot corner rule, so the
  report never shows the check. **TO DO:** build the check into the program and the report; never present the
  exemption as settled.

## 4. The competitor's PDF ("for reference")

- **Developer:** it is the same file the owner sent on 4 October; the reviewer compared against all 88 pages.
- **We borrow the form, not the numbers:**
  - one headline figure with a one-sentence summary and a strip of the lot's key facts;
  - one comparison table with all eleven options;
  - a scenario sheet with the assumed conditions as small tags, a section with the zoning height lines next to a
    summary table, a dimensioned footprint (ours on our real lot outline), and a floor-area schedule showing
    deductions and adding up to the zoning floor area.
- **We do not copy:** room-by-room apartment layouts (the owner ruled them out); figures without their conditions;
  its mistakes (for example treating the rear-yard relief as the corner rule only).
- **DONE:** the sample is stored in a stable private reference folder (never published; it is a third party's
  document).

## 5. Time estimates

- **Owner:** "Can I expect a new PDF shortly?" **Developer:** gave a first guess, then corrected it once the plan
  showed more work before the new page 1.
- **Owner (later):** no more time estimates; it was a one-time question. **RECORDED:** updates name what comes next,
  never when, unless the owner asks.
- **Owner (later, asked directly):** how long until all 11 options are in the PDF? **Developer (one-time answer):**
  very roughly two to four weeks of working sessions at about one session a day: the first fully worked option takes
  the longest (it builds the shared machinery), then about half a session to one session per remaining option.

## 6. "What if this conversation stops? Will the next session know everything?"

- **Developer:** yes, through files, not memory:
  - every owner instruction saved word for word and split into numbered requirements;
  - every task, review and approval in the project's records;
  - a step-by-step session log on the build server;
  - a short handoff note plus a detailed next-session brief (what to build, how, what is missing, the sample PDF).
- **DONE:** handoff note rewritten; full handoff done when the owner asked for it (all running helpers allowed to
  finish first; nothing new started).
- **TO DO:** add the lesson "always read the test results before approving" to the project's shared knowledge file,
  so any model sees it (today it is in the handoff and the AI's own memory only).

## 7. Two decisions asked of the owner

- **Paper size: OPEN.** Recommendation: US Letter (New York architects print Letter; the competitor uses it).
  Meanwhile A4. It matters for the page-1 rebuild.
- **The worked option's floor plate: ANSWERED, RECORDED.** The owner said yes to a simple two-zone illustration, with
  these rules:
  - labels exactly "Apartment area" and "Other building area: core, circulation, walls and services" (never "core
    and corridors", which would make a rough assumption look like a calculated layout);
  - caption "Illustrative area allocation—not a floor plan";
  - one stated percentage from the existing 60-75% assumption, shown beside it; drawing and calculation agree;
  - the estimate and the drawing use compatible area measures; zoning floor area is never treated automatically as
    the physical floor-plate area;
  - no rooms, unit walls, apartment counts, or invented stair or elevator locations;
  - zones inside the footprint only once the footprint is actually fitted to the site; until then a simple
    proportional bar beside the building diagram;
  - one short caption, the method in the appendix;
  - the same on the website and in the PDF; the rendered result checked for readability before it is called done;
  - recorded in the design rules and the questionnaire (questionnaire DONE; design rules TO DO in the first task).

## 8. The owner's big question: where do we stand, and is it better than the competition?

- **Where we stand:**
  - The foundation is built and solid: official data with a receipt for every fact, rules applied step by step by
    plain calculation (the AI never does the zoning math), honest labels on every answer, a website and a PDF.
  - What is missing is most of what an architect looks at: worked building options with drawings.
  - For the test property: very roughly a third of the way to the full report. For the whole city: much less (only
    part of the residential rules; no commercial, manufacturing or special-district rules yet).
- **How the app is built ("a kitchen"):**
  - shopping (official city data, each fact with its source, date and exact value; missing facts stay "not known");
  - recipe cards (each zoning rule with its exact law section);
  - the cook (combines facts and rules into floor area, height, legal apartment limit, building options);
  - the label maker (every answer: conditional, provisional, illustrative, pending verification or unresolved, with
    what it depends on);
  - plating (website and PDF).
- **How numbers are checked:**
  - thousands of automatic tests on every change;
  - a test property worked by hand, separately from the program, and compared;
  - exact saved copies of the real city data for that lot;
  - a research record for every tricky question;
  - independent AI reviewers who try to prove each change wrong.
  - Gap: no licensed New York City professional has checked any rule yet.
- **Are the rules the same for every district?**
  - Partly: every district has the same kinds of rules (floor area, height, coverage, yards, apartments, parking)
    with different numbers, mostly in tables.
  - Each district family adds twists (contextual R6B, choices in plain R6, towers and wide/narrow streets in R7-R10,
    commercial and special districts, and the 2024 City of Yes changes). The machinery is built once; the number of
    rule cards grows and each needs checking.
- **Can an expert mark the rules right or wrong? How many questions?**
  - Yes: there is a review list with one plain-English entry per rule (law, district, the program's reading, a worked
    example, a link, and a blank box for a New York architect or zoning examiner). Every box says "not reviewed".
  - Today about 35-40 questions (23 rules, about 6 calculations, about 6 research readings).
  - The whole city: a few hundred for all residential districts, several hundred more with commercial,
    manufacturing and special districts. The expert can start with the districts that matter most.
- **Versus the competitor:**
  - Today they are more complete and visual (11 options, drawings, plans); we are more trustworthy (every number says
    what it depends on, links to the law, nothing invented). We also caught things their report misses (the possible
    shared zoning lot with lot 1; the short-block rear-yard rule).
  - Final product: better, if we finish the worked options and drawings while keeping the honesty.
- **Would an architect say "wow"?**
  - Today: no; careful facts, but no building to look at, so they would still do their own study.
  - After the new page 1, the dimensioned lot drawing and one worked option: "this saves me time".
  - "Wow" when all 11 options are worked with drawings and every number traces to the law.
- **Why does the owner's other AI sometimes find answers the developer misses?**
  - Strict rules here (only official sources, exact quotes recorded, "not sure" when not sure).
  - A fresh outside view (example: the failing test nobody read here).
  - Some official sites are slow or block automated tools.
  - Sometimes the developer is simply wrong.
  - The other AI can also be confidently wrong, so its findings are strong leads that are then checked against the
    law text (the owner's own rule).
- **How is the law interpreted when experts can disagree?**
  - Read the exact words and the definitions; look for exceptions and official guidance; write the reading as a draft
    with reasons; an independent reviewer tries to break it.
  - Where it truly could go two ways, the app shows the answer as conditional or says "not sure", never quietly picks
    a side.
  - The final word belongs to a licensed professional through the review list.

## 9. Follow-up questions

- **How often does "not known" happen?**
  - For the test property about 1 in 3 answers is "not known" or "not worked out"; the rest show a number, every one
    conditional (mainly on this tax lot being the whole zoning lot); none is settled; 10 of the 11 options are not
    worked yet.
  - Two kinds: the city's information does not settle it (lot size disagreement, unread recorded documents,
    neighbours' exact lot lines; these need a survey, deed or documents), or the program has not learned the rule
    yet (setback, street wall, parking, affordable apartment limit; these shrink as we build).
- **Who gave us the test property?** The owner, on 28 September, with the competitor's report on the same lot. It is
  also a tricky lot, which tests many rules.
- **How do we know nothing was missed?**
  - Not one hundred percent yet. Today: a master checklist of zoning topics per residential district, the report
    saying out loud what it did not check, the review list's known-gaps section, outside reviews and hand-worked
    examples.
  - The remaining risk is a rule nobody has thought of yet. The proper protection is a complete law library that
    follows every cross-reference (see I1 below), plus the professional review.
- **When something new is added (for example affordable housing), does everything update from the ground up?**
  - Every rule lives in one place and is shared by the website, the PDF, the drawings and every option.
  - Tests act as tripwires: a changed rule makes every affected test fail until it is updated on purpose.
  - Research records flag themselves as out of date when the program parts they depend on change.
  - Law sections carry dates and fingerprints, so an amended section must be reviewed before use.
- **Where does pitfall knowledge come from?** The Buildings Department's guidance notes; the city's formal
  interpretations; appeal-board decisions; the planning department's guides; past permit filings on the same lot;
  our own reviews. The plan: collect these into a "watch out for this" checklist per kind of rule.
- **Is that guidance built into the program?**
  - Buildings Department guidance and formal interpretations: no (researched and listed as planned sources only).
  - Appeal-board decisions: no (not even listed yet).
  - Both go into the law library work.
- **Past permit filings for a real client's address:**
  - A reader of a lot's past permit filings from the city's open data exists and works for any address. It is used
    for the existing building's size and for filings that mention a zoning lot shared with other lots.
  - It has been tested on saved data for the test lot but is not switched on for real visitors yet. Switching it on
    is a live-site change for the owner to approve later.
  - Limit: the city publishes the filings, not the examiners' written objections.
- **When something stays "not known":**
  - Does the website accept the architect's answers and recalculate? Partly. Today three entries change the results:
    housing type, floor-to-floor height, and a statement about the special density area. The setup screen saves the
    architect's lot size, dimensions, which lots belong together and the existing building size beside the city's
    values, but these do not feed the calculation yet (see I3 below).
  - Is a full report still produced? Yes, always. Answers that do not depend on the missing fact show normally;
    answers that do are shown with their condition; only what truly cannot be worked out says "not known", with what
    would settle it.
  - Survey and drawing readers:
    - The survey reader reads digital PDFs only (not scans). So far it pulls out the scale and the lot number;
      distances, angles, area and boundary are designed but not finished. It has an accept / correct / reject step
      per value, with a kept history. It is tested on made-up surveys only and not connected to the results.
    - The drawing reader reads DXF files (AutoCAD can export them). It lists closed shapes for the architect to label
      as building, property line or street, and to confirm the units. It has no web screen yet and is not connected.
    - AutoCAD's native DWG format is not supported (left as the owner's licensing decision).
    - An unconfirmed value is not used: the affected answers stay conditional or "not known" and the rest of the
      report is produced. It is a warning, not a wall.
    - The reader shows where on the document it found each value, so the architect can compare; corrections are
      kept; if it cannot find a value it says so and the architect can type it in.
- **Would 25 helpers speed up the 11 options?** Not much, and riskier: all options run through the same calculation
  and report files, so parallel builders would collide, and every change still needs independent review and the full
  tests, one at a time. Research can go wider because researchers only read (see I2 below).
- **Financial estimates (AMI, affordable rents, 421-a, 485-x, the City of Yes bonus)?**
  - Not built today; the Financials part of the app is a placeholder.
  - Affordable rents are set by formula: area median income (AMI, published yearly) for the household size implied by
    the apartment size, the program's income band (for example 60% of AMI), about 30% of that income per year divided
    by 12, minus a utility allowance. With the unit mix and band assignment, affordable rents can be calculated
    exactly from published tables.
  - The hard part is which apartments get which band: programs require spreading affordable units across sizes and
    floors and averaging income bands (the new affordable bonus requires an average of 60% AMI). That is a visible,
    editable assumption at feasibility stage.
  - Market rents have no official source: the owner's numbers or a labelled estimate.
  - 421-a ended for new projects in 2022; 485-x (2024) replaces it, with tiers by size, affordable share, income
    levels and wage rules. The City of Yes bonus adds floor area for affordable apartments.
  - Each incentive would appear as a "with" and "without" pair per option (floor area, affordable apartments, yearly
    rent, tax savings), all labelled estimates.
  - The owner has already built an AMI and affordable-bonus calculator; its logic can be the starting point, checked
    against the official tables, when this stage comes (after the building options).

## 10. Questions I1, I2, I3 and the owner's answers (all RECORDED)

- **I1. Start the zoning-law library now?** Owner: yes, in the next session. A second line of work beside the report:
  every section connected to the rules this lot uses, every cross-reference followed, a list of what the app handles
  and what it does not yet, and a pitfall checklist from official guidance (Buildings Department guidance and
  interpretations, appeal-board decisions, planning guides). The handoff tells the next session to start it.
- **I2. More helpers?** Owner: yes, and spin up agents. Up to 8 helpers at once when every helper beyond 5 only reads
  and researches; still at most 3 building, never on the same files. The next session starts research helpers for the
  library and for the remaining options' rules.
- **I3. Architect-entered facts and the survey reader?** Owner: yes, recorded for the build. Right after the first
  fully worked option, the architect's entered lot size, dimensions, lot grouping and existing building size feed the
  results, each result labelled as resting on the architect's value so nobody mistakes it for a city record; then the
  survey reader is finished and tested with real surveys.

## 11. Rules now in force (owner decisions)

- Updates: four short plain bullets; no time estimates unless asked.
- Approvals and merges only after the full test results are read green on exactly the version approved.
- Nothing is labelled Verified until the owner settles what Verified requires.
- Every production switch stays off unless the owner approves it.
- All eleven options stay in scope; no detailed apartment layouts or permit-ready plans.
- The two-zone illustration rules of section 7.
- Helpers: up to 8 when the extra ones only research; at most 3 building; never sharing files.
- The owner's newer instruction to show fewer maps (one neighbourhood map plus one dimensioned close-up) replaces the
  earlier location-sheet decision; the old map stays restorable.
- The outside reviewer's forwarded audits count as owner instructions; the other AI's findings are leads to verify
  against the law, not facts.

## 12. What happens next, in order (TO DO)

1. One independent check of the revised plan, then the design rules updated (page 1 layout, type sizes, fewer maps,
   the two-zone illustration rules).
2. The new page 1 and the dimensioned close-up of the lot, side by side; the first new PDF follows, with
   before-and-after screenshots.
3. In parallel: the zoning-law library with research helpers (I1, I2); the rear-yard short-block check (23-344(b)).
4. The one fully worked option: footprint placed and dimensioned on the lot, a section with the height lines, a floor
   schedule that adds up, the two-zone illustration, untested constraints listed.
5. Architect-entered facts feed the results (I3); then the survey reader with real surveys.
6. The website matching the PDF.
7. The remaining 10 options, the comparison table and the evidence appendix.
8. The other promised sections: nearby sales, block description, parking, photos, tax-abatement eligibility,
   financial inputs.
9. More districts beyond R6B, family by family.
10. A licensed New York City professional goes through the review list.
11. Small upkeep: the zoning-lot documents record refreshed after the wording fix; one rules file that the automatic
    style check never reads fixed; the "read the test results before approving" lesson added to the shared knowledge file.

## 13. Open questions for the owner

- Paper size (recommend US Letter; meanwhile A4).
- Whether the six status labels also replace the statuses on the website screen.
- Older open items in the questionnaire: what must be true before anything is labelled Verified; how the lot-area
  disagreement is shown; which building the results show when two can be worked; optional help saving three recorded
  documents from the city register; and several housekeeping items.
- Later: switching on the permit-filings reader for real visitors (a live-site change).

## Where the records live (for an AI picking this up)

- Owner instructions, word for word, with numbered requirements: the project's directive records (this conversation
  is directive D-094, sources 001 to 004).
- Work records (tasks, reviews, approvals): the project's control records in the repository.
- Handoff note and next-session brief: the repository's session handoff file and the private session folder of
  2026-10-11.
- Questions to the owner and their answers: the private owner questionnaire.
- Reference PDFs (competitor sample, our latest report): the private reference folder.

## 14. Last question before the next session: "Any blind spots?"

- **Developer's answer (ANSWERED; three new OPEN questions):**
  - **Professional check early (OPEN, J1):** no licensed professional has checked any rule yet; a wrong early reading
    would repeat in every option and district. Recommendation: a few paid hours of an expediter or zoning-savvy
    architect on the review list (about 35-40 items) before the work spreads beyond R6B.
  - **Addresses with known answers (OPEN, J2):** everything is tested on one lot. Recommendation: the owner sends 5-10
    addresses from past projects (different lot shapes and districts) with what was approved; they become test cases.
  - **Private backup (OPEN, J3):** the questionnaire, session logs, reference PDFs and working notes live only on the
    build server. Recommendation: a private backup the owner controls (a private repository or cloud drive; the
    owner creates it).
  - **Real addresses end to end:** several live data connections are built but switched off (the zoning-lot document
    index, the permit-filings reader); the real-address experience is not proven yet. Before showing clients: an
    internal trial on real addresses, then the owner approves each live switch.
  - **Law changes over time:** the city amends the zoning law; a routine re-check of the saved law sections is part
    of the law library work.
  - **Process weight:** every small fix goes through building, two reviews, a rule check and the full tests; good for
    accuracy, slower; the owner's outside reviews keep the focus on what architects see.
  - **Financial stage inputs:** beyond AMI rents and incentives, projections need construction and financing costs,
    which have no official source; the owner will supply or approve those assumptions.
  - **DWG:** many architects work in DWG; reading or writing DWG is still the owner's licensing decision.
  - **Liability wording:** before selling to clients, a lawyer may want to review the disclaimer and terms (the app
    already labels results as preliminary, unreviewed drafts with law links).

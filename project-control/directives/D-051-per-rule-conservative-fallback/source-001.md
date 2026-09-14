# D-051 source-001 (verbatim) — owner directive, interactive chat (build session), 2026-09-13

Capture context: immediately after the build session summarized the RQ-005 state in simple
English, the owner ran an independent review/research pass and pasted the following message to
the build session verbatim. The message (a) corrects two claims the build session made, (b)
issues a binding engineering instruction on conservative fallbacks, (c) hands over a second
research report (attachment archived at
`docs/research/owner-research/RQ005_Independent_Confirmation_2026-09-13.md`, received via the
D-050 channel), and (d) asks whether the latest research answer works. The attachment reference
in the first line is the owner's upload path.

## owner-message-verbatim

> @"C:\Users\MLFLL\.claude\uploads\6002a07a-b78c-415c-aea3-e97f45c6627d\621e4e24-RQ005_Independent_Confirmation_2026-09-13.md" Worked for 1m 10s
>
> CC handled the research handoff correctly, but two claims need correcting. I checked the current GitHub queue: the statuses match his summary, and the requirements for independent official-source capture remain intact.
>
> 1. I did not establish that the city “never wrote it down anywhere public.”
>
> The accurate finding is: we did not find the precise field definition in the official sources examined, including the metadata PDF and embedded XML. Asking DCP is a sensible next step; claiming that further research cannot uncover it goes beyond the evidence.
>
> The metadata lists DCPOpendata@planning.nyc.gov as the dataset contact—a useful starting point for obtaining or locating that specification. Official DCM metadata
>
> 2. “Unknown means narrow, which can never over-promise” is too broad.
>
> Narrow-street assumptions can be conservative for particular calculations. For example, the standard upper-building setback is generally 15 feet on narrow streets versus 10 feet on wide streets. §23-433
>
> But other requirements work differently: the general street-wall placement rule requires at least 70% within eight feet of the street line on wide streets, versus ten feet on narrow streets, subject to the section’s exceptions. §23-431
>
> My conclusion: a smaller floor-area estimate does not automatically make the generated building shape or compliance result safe. A narrow-street assumption could permit placement that fails the actual wide-street requirement.
>
> The practical instruction for CC is to preserve “unknown” as the factual status and validate any conservative fallback separately for each rule that consumes it. Until validated, affected results should retain their assumption or review label.
>
> The build can continue through its existing gates. Just keep the distinction clear: research answered means the evidence has been located—not that the rules are implemented or professionally approved.
> Worked for 33s
>
> RQ-005 has three parts. Two are answered; one remains open.
>
> Part	Status	Finding
>
> Exact DCM download and filename	Answered	The official ZIP was downloaded and its street-centerline files verified.
> What LION’s width measures	Answered	It measures paved street width, not the full mapped street width.
> Precisely what DCM’s Streetwidth field records	Still open	DCP describes mapped widths, but the sources examined lack a precise field definition and encoding instructions.
>
> The remaining question is not “Does DCM contain street widths?” It does. We need authoritative confirmation of:
>
> Measurement boundaries: exactly which lines define the width, and in what units?
>
> Variable widths: what does the value represent when the street widens or narrows?
>
> Unusual values: how should ranges, text, blanks and other nonnumeric entries be interpreted?
>
> The official metadata lists DCPOpendata@planning.nyc.gov as the dataset contact. Requesting that field specification is the strongest next step; they can route it to the responsible mapping team. DCP metadata
>
> Keep RQ-005(1) open until that evidence arrives. The rest of the build can progress, but uncertain width must remain an identified assumption. Automatically treating every unknown as narrow is not a universal guarantee that every affected rule produces a conservative result.
> Worked for 16m 49s
>
> Yes. I ran a separate research agent and independently checked its findings. RQ-005(1) remains partly unresolved, but we now have stronger official evidence.
>
> The new findings:
>
> Mapped width and sidewalks: DCP’s own application explicitly says “Mapped street widths (usually includes sidewalks).” Official application source
>
> Units: the city’s map code displays the width field in feet. Official map configuration
>
> Missing definition confirmed more thoroughly: we found DCP’s metadata-authoring file and checked 14 historical versions. The width entry has a name and text type, but no explanatory definition or code list. Official metadata source
>
> I also checked the actual data. Among 54,051 records, 6,908 contain something other than a plain number, including 60-75, ~75, and Unknown but >75. Some occur on records explicitly marked as mapped city streets. Official service
>
> What remains unresolved: the precise measurement boundaries, how widths apply along changing street segments, and the authoritative interpretation of those unusual values.
>
> For CC: add these confirmed findings, keep that specific residual question open, and retain RQ-005(2) and (3) as answered. The evidence does not establish that the city never documented it anywhere.
>
> Worked for 3m 58s
>
> We resolve it through a written explanation from DCP, followed by map verification where individual records remain unclear.
>
> 1. Ask DCP to define the field.
>
> Email DCPOpendata@planning.nyc.gov, the contact listed in the official metadata. Ask for the existing specification or a written explanation from the team maintaining the dataset.
>
> Source: DCP metadata — https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/dcm_street_centerline.pdf
>
> Here is the inquiry ready to copy:
>
> Hello,
>
> I’m reviewing DCP’s Digital City Map Street Center Line dataset and need clarification of the Streetwidth field, named Streetwidt in the shapefile.
>
> Could you provide its data dictionary or authoring specification, or confirm the following in writing?
>
> 1. Which boundaries define the recorded width? Is it measured between mapped street lines, and are there exceptions concerning sidewalks or particular feature types?
>
> 2. Where a street changes width, what does a single numeric value represent: minimum, maximum, nominal width, or a measurement at a particular location?
>
> 3. How should entries such as “60-75,” “~75,” “Unknown but >75,” “Width Irregular,” and “n/a” be interpreted? How do those values apply along the segment and to adjoining property frontages?
>
> 4. When the field is insufficient, which adopted map or other authoritative record should be consulted, and how can that record be identified?
>
> If another GIS or Technical Review team maintains these conventions, please route this inquiry to them.
>
> Thank you.2. Resolve individual properties from the controlling map when necessary.
>
> If DCP explains the field but a record still says “Unknown” or “Width Irregular,” an architect or surveyor may need the applicable adopted Section Map and subsequent Alteration Maps to establish the relevant width.
>
> DCP’s current guidance directs City Map research requests to the relevant Borough President’s topographical bureau until those functions transfer.
>
> Source: Current City Map guidance — https://www.nyc.gov/content/planning/pages/planning/city-map-and-address-assignment
>
> 3. Have CC close only what the evidence answers.
>
> CC should capture DCP’s response, update the documented field conventions, and validate the affected parsing and rules under your existing review process.
>
> The distinction matters: DCP’s explanation could close the documentation question. It will not necessarily make every unknown street-width record automatically computable. Those properties can retain a specific review requirement while the rest of the product progresses.
> This wont work i need the answer now can u check reddit or any form to get a better answer
> Worked for 6m 55s
>
> The strongest supported answer is that DCM’s Streetwidth represents mapped street width in feet, normally including sidewalks. The ordinary measurement is between the mapped street boundaries. DCP’s own application describes “Mapped street widths (usually includes sidewalks)” and displays the Streetwidt field with “ft.” DCP’s explanatory text, DCP’s field-display code.
>
> I searched Reddit and GIS/architecture forums. I didn’t find a reliable explanation of this particular field there. I did find additional official evidence that sharpens the answer:
>
> NYC DEP explicitly distinguishes the measurements. Its survey instructions, printed page 1, require both “Street width (property line to property line)” and “Roadway width (curb line to curb line).” Page 2 separately requires the legal right-of-way width. This corroborates the measurement distinction, although it is a survey standard rather than DCM’s data dictionary. Read the official DEP PDF.
>
> DOB explains why “property line” needs care. Buildings Bulletin 2014-001, page 2, defines the mapped street boundary and explains that a mapped street can include privately owned land or a widening area. Consequently, current tax-lot boundaries and building façades are not universal substitutes for mapped street boundaries. Read the official DOB bulletin. The practitioner explanation that led me there is Design 2147’s street-widening guide.
>
> What remains unproved is narrower: how DCP assigns a single value to a variable-width segment, and the complete conventions behind its unusual text entries. These sources do not establish that every numeric value is the minimum, maximum, or width at the selected lot.
>
> You can still make a useful decision now. My recommended DRAFT policy, subject to your existing owner/professional decision process, is:
>
> Evidence for the relevant frontage	Proposed treatment
>
> Clear, applicable mapped width below 75 ft	Apply the ordinary narrow-street test
> Clear, applicable mapped width at least 75 ft	Apply the ordinary wide-street test
> Explicit bound such as >75	Could support wide classification under a documented owner-approved reading
> 60-75, ~75, Width Irregular, or Unknown	Resolve from the applicable map; preserve uncertainty meanwhile
>
> The 75-foot test has express exceptions, including certain variable-width streets and named street portions, so those must be checked separately. Current ZR §12-10 definitions.
>
> My earlier “contact the city” answer was too absolute. For a specific ambiguous frontage, an effective, dimensioned Section Map or Alteration Map can resolve its width without waiting for a general explanation of the dataset. Those records are accessible through NYC Street Map — streets.planning.nyc.gov; check that an alteration has taken effect.
>
> RQ-005’s general mapped-width reading now has substantial support. Its universal decoding convention remains unverified. That distinction lets you consider clear cases for DRAFT coverage without pretending every ambiguous record has been solved.
>
> How is this answer does this work ?

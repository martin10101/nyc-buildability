# R6B minimum base height vs. the 20 ft sample building (D-090-R107 step 1)

Lane A finding. This is a DRAFT reading from the official text. The legal
interpretation waits for G6 qualified-human approval. No legal determination is
made here; this note quotes the official text and says what it provides on its
face.

Sources pinned this step (official DCP portal, Last Amended 12/5/2024):
- `zr-23-431` Street wall location requirements (node 18084)
- `zr-23-433` Standard setback regulations (node 22773)
- `zr-23-432` Height and setback requirements (node 18085) - already in the repo

## (a) The question

The generator's 215-16 Northern (R6B) sample building is 20 ft tall (a 2-floor,
FAR-limited building), while the report lists a 30 ft minimum base height. Under
the current Zoning Resolution, may a building in R6B be lower than the 30 ft
minimum base height - i.e. is a 20 ft street wall permitted - or must the street
wall rise to at least 30 ft? And does the R6B table carry a separate minimum
base height for the qualifying-housing columns, or the same 30 ft?

## (b) The text that answers it (quoted)

Minimum base height / maximum base height / setback trigger - ZR 23-432
(`zr-23-432`):

> For portions of a #building# #street wall# that exceed the maximum base
> height, a setback shall be provided at a height not lower than the minimum
> base height or higher than the maximum base height in accordance with Section
> 23-433.

Street wall location, where the minimum base height "rise to" requirement lives
- ZR 23-431 (`zr-23-431`), paragraph (b)(1), wide streets (identical clause in
(b)(2) narrow streets and in (c) large lots):

> Along #wide streets#, at least 70 percent of the #aggregate width of street
> walls# shall be located within eight feet of the #street line# and extend to
> at least the minimum base height specified in Section 23-432, or the height of
> the #building#, whichever is less.

ZR 23-431 paragraph (a) "Line-up rules", which names R6B, is a horizontal
location rule only (no minimum height):

> In R6B, R7B, and R8B Districts, the #street wall# of a #building# shall be
> located no closer to the #street line# than the closest #street wall# ... nor
> further from the #street line# than the furthest #street wall# ... of an
> existing adjacent #building# ...

Setback mechanics - ZR 23-433 (`zr-23-433`):

> At a height not lower than the minimum base height or higher than the maximum
> base height specified for the applicable district, a setback with a depth of
> at least 10 feet shall be provided from any #street wall# fronting on a #wide
> street#, and a setback with a depth of at least 15 feet shall be provided from
> any #street wall# fronting on a #narrow street#.

## (c) The finding, as a draft reading of the captured text

On a reading of the captured text, no captured provision requires a 20 ft building
in R6B to rise to the 30 ft minimum base height. Three points, none of which
requires a building to reach 30 ft:

1. The setback is triggered only "For portions of a #building# #street wall#
   that exceed the maximum base height" (ZR 23-432). R6B maximum base height is
   45 ft; a 20 ft building never exceeds it, so no setback is required at all.
2. The only "rise to the minimum base height" language (ZR 23-431 (b)(1),
   (b)(2), (c)) is capped by "or the height of the #building#, whichever is
   less." For a 20 ft building the lesser of 30 ft and 20 ft is 20 ft, so the
   street wall need only rise to its own 20 ft height. The 30 ft minimum base
   height is a street-wall threshold, not a floor on total building height.
3. The paragraph (a) "Line-up rule" that names R6B governs how far the street
   wall sits from the street line; it states no minimum building height.

So no captured provision requires the 20 ft building to rise to the minimum base
height; the minimum base height is reconciled with a shorter building by the
"whichever is less" clause. This does not establish the site's compliance:
qualified zoning review (G6) decides which paragraph of ZR 23-431 governs this lot
and the legal effect. The report's "30 ft minimum" is a correct table value but is
shown without that clause, which is what makes it read as a contradiction. Residual, for G6: which
of 23-431 (a)/(b) governs turns on a "prevailing street wall frontage" factual
determination; Sections 23-434, 23-436, 23-44 and any overlay/special district
were not captured and must be confirmed (none of them is a minimum-height source
in the captured text).

## (d) Qualifying-housing minimum base height (table row)

The R6B row of the ZR 23-432 table (`zr-23-432`) carries a single
"Minimum base height (in feet)" column that spans the whole row (it is not
repeated under either program heading):

- District: R6B (no footnote marker)
- Minimum base height: 30
- Standard residences - Maximum base height: 45; Maximum building height: 55
- Qualifying affordable or qualifying senior housing - Maximum base height: 45;
  Maximum building height: 65

So the qualifying-housing heights read 30 / 45 / 65 ft: the 30 ft minimum base
height is SHARED (same column), and only the maximum base height (45) and
maximum building height (65) are the qualifying-specific values.

## Recheck 2026-10-04 - §23-432 official-HTML fingerprint

The owner's reviewer noted that §§23-431 and 23-433 were fingerprint-reproduced in
this step but §23-432 was not: its retrieved operative text and R6B row matched the
snapshot, but the raw-HTML digest had not been re-fetched, so this was an
unreproduced fingerprint, not proof the law changed. Rechecked here against the
exact channel the snapshot records (docs/research/zr-snapshots/v1/
zr-23-432.snapshot.json).

- Channel: one direct HTTPS GET of the official DCP portal page with a browser
  user-agent (`curl -A "Mozilla/5.0"`), exactly as the snapshot's capture_method
  records.
- URL fetched: https://zoningresolution.planning.nyc.gov/article-ii/chapter-3/23-432
- Fetched 2026-10-04; HTTP 200; 182,022 bytes (pinned capture was 182,068 bytes).
- raw_html_sha256 obtained:
  4abaa14913b0d75cba8de20ea2866de9e059c6de9f936eeba5d0e505fa71f2f7
- raw_html_sha256 pinned in the snapshot:
  06ca2245cd0a7b463c268d617dc0c6a8cb908d90c5fa13f5800d72c85226b177
- Digest match: NO. The pinned byte capture did not reproduce.

Operative text and R6B row comparison (parsed from the fetched HTML, defined-term
markup stripped):

- Setback paragraph, verbatim: "For portions of a #building# #street wall# that
  exceed the maximum base height, a setback shall be provided at a height not lower
  than the minimum base height or higher than the maximum base height in accordance
  with Section 23-433." - MATCHES the snapshot verbatim_excerpt.
- Table intro ("... the minimum base height, maximum base height, and maximum
  #building# height shall be as set forth in the following table. Separate maximum
  base heights and maximum #building# heights are set forth for #zoning lots#
  containing standard #residences# and #zoning lots# containing #qualifying
  affordable housing# or #qualifying senior housing#.") - MATCHES.
- R6B row: District R6B, Minimum base height 30, Standard residences max base 45 /
  max building 55, Qualifying max base 45 / max building 65 - i.e. 30 / 45 / 55;
  qualifying 45 / 65 - MATCHES the snapshot's R6B row exactly.
- Last Amended still 12/5/2024 (machine-readable 2024-12-05T12:00:00Z present).

Conclusion: the page's bytes changed; the operative text and the R6B row did not.
An unreproduced fingerprint is not evidence that the law changed - it means the
point-in-time byte capture no longer reproduces (the portal is a Drupal site that
emits per-request markup, so the raw bytes drift while the published text is
stable). The snapshot file is deliberately NOT edited: its pin is a point-in-time
record. Only the HTML channel was re-fetched here; the print/PDF cross-check was
not re-run and nothing beyond the HTML GET is claimed. The §23-432 operative text
and R6B row this finding relies on are confirmed unchanged as of this recheck; the
legal effect still waits for G6.

## (e) What the generator should do (step 2 engine change + test)

Legally grounded fix (recommended): keep the 20 ft FAR-limited sample and add a
note on the building option (the engine's compliance_notes field) recording that,
on a reading of the captured text, no captured provision requires the building to
rise to the minimum base height. Forcing the street wall to 30 ft is NOT required
by the captured text; presenting it as required would read a requirement into the
text that the text does not state. This does not establish the site's compliance;
qualified zoning review (G6) decides which paragraph of ZR 23-431 governs this lot
and the legal effect. The note should say, in plain words: the
building's height (20 ft) is below the R6B minimum base height (30 ft); per ZR
23-431 the street wall need only rise to the lesser of the minimum base height or
the building's height ("whichever is less"), and per ZR 23-432 no setback is
required because the building does not exceed the 45 ft maximum base height. Cite
ZR 23-431 and 23-432 (and 23-433 for the setback mechanics), snapshots
`zr-23-431` / `zr-23-432` / `zr-23-433`.

Also surface the qualifying-housing heights as the triple 30 / 45 / 65 ft:
include the shared `min_base_height` (30) beside `qualifying_max_base_height`
(45) and `qualifying_max_building_height` (65), rather than showing only 45 / 65.

Alternative the owner mentioned (a 30 ft street wall = at least 3 floors at the
10 ft default, which with the 20,150 sq ft allowance means a smaller plate) is a
PRODUCT choice about which sample to show, not a legal requirement; if taken, it
must not be presented as "the minimum base height forces 30 ft."

Test to pin it (step 2): a rules/scenario test on the 215-16 Northern R6B
benchmark asserting (1) when the FAR-limited building height is below the minimum
base height, the building option carries the "whichever is less" + "no setback
below max base height" compliance note citing ZR 23-431/23-432; (2) the
qualifying-housing heights are surfaced as 30 / 45 / 65 (min_base 30,
qualifying_max_base 45, qualifying_max_building 65). Make it a meaningful (red
first) test: revert the note / the shared-30 output and confirm the asserted
value moves, so the test cannot pass on the pre-fix code.

## (f) Status

This is a draft reading from the official text; the legal interpretation waits
for G6.

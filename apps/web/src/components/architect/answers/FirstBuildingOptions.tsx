import type {
  BuildingAlternativeView,
  BuildingNotWorkedView,
  CapacityView,
  CoverageView,
  FirstBuildingOptionsView,
  FloorRowView,
} from "@/lib/architect/first-building-options";
import { APARTMENT_SIZE_BASIS_NOTE, storeyText } from "@/lib/architect/first-building-options";
import { scheduledFloorAreaLine } from "@/lib/architect/presented-results";
import { BuildingOptionsComparison } from "./BuildingOptionsComparison";
import { ResultDetails } from "./ResultDetails";
import "./building-options.css";

/**
 * The first-building-options section (results contract 1.4.0; M5-T146 / M5-T147 / M5-T149 part B;
 * rulings V2/V5/V8, W1–W5; rows R894/R895; D-090-R509/R526/R540/R541/R543/R544/R556/R570/R688). It
 * reads the view built by firstBuildingOptionsView and shows, from the document and never from a
 * typed value: each worked building leads with the SAME one-line phrase the rest of the screen uses,
 * "Scheduled floor area: N sq ft; site fit unverified" — NEVER "achieved", and never "no allowance
 * left unused" (rows R895/R922, scenario S1) — so the answer and its site-fit caveat read together
 * before the reader reaches the detail; then, behind a named disclosure (R928 expandable detail), the
 * conditions (the 'Conditional' marker + "Applies: Condition N"), its floor schedule as a table, what
 * was NOT checked, and its own preliminary capacity estimate under the owner's label. Below the
 * buildings comes one
 * comparison of the method's buildings (row R894), then coverage by portion — withheld with NO
 * figure, or its figures when available. Nothing is called feasible; a withheld result carries no
 * number and no substitute (R556/R570). The state is told by the WORDS, never by colour alone.
 *
 * On a draft architect surface the numbers are hidden behind the same gate the three answer cards
 * use (results.draft && !showDraftValues); the section then shows one not-reviewed line.
 */

/** The fixed marker beside a conditional figure so it never reads as confirmed (ruling L3). Plain
 * text, normal weight — the state is told by the word, never by colour alone. */
const CONDITIONAL_MARKER = "Conditional";
/** Leading words for a withheld value: it is not known, with the reason, NEVER a number (R556/R570). */
const NOT_KNOWN = "Not known";

/** The lead under the heading, chosen to FIT the state and saying nothing the document does not
 * (ruling W15): a lead about worked shapes ONLY when at least one building is worked; otherwise a
 * plain statement that no shape was worked, so the not-worked reasons below carry the explanation. */
const LEAD_WORKED =
  "Draft building shapes worked from the floor-area allowance. None is ranked ahead of the others, and none is checked against where it would sit on the lot.";
const LEAD_NONE_WORKED =
  "No building shape could be worked for this lot at these inputs. For each building of the method, why:";

export function FirstBuildingOptions({ view }: { view: FirstBuildingOptionsView }) {
  const hasWorked = view.alternatives.length > 0;
  return (
    <section className="ta-options" data-testid="first-building-options" aria-label="Building options">
      <h3 className="ta-options-title">Building options</h3>
      {view.draftHidden ? (
        <p className="ta-not-available" data-testid="first-building-options-draft-hidden">
          {view.draftHiddenText}
        </p>
      ) : (
        <>
          <p className="ta-options-lead" data-testid="first-building-options-lead">
            {hasWorked ? LEAD_WORKED : LEAD_NONE_WORKED}
          </p>
          {view.alternatives.map((alternative, index) => (
            <AlternativeBlock key={`${alternative.building}-${index}`} view={alternative} />
          ))}
          {view.notWorked.map((entry, index) => (
            <NotWorkedBlock key={`${entry.building}-${index}`} view={entry} />
          ))}
          {view.comparison ? <BuildingOptionsComparison view={view.comparison} /> : null}
          {view.coverage ? <CoverageBlock view={view.coverage} /> : null}
        </>
      )}
    </section>
  );
}

/** One building of the method that was NOT worked (ruling W14/W15): its label, its reason and what
 * would let it be worked, all read from the document; no figure is a result here. */
function NotWorkedBlock({ view }: { view: BuildingNotWorkedView }) {
  return (
    <section className="ta-option ta-option-not-worked" data-testid="building-not-worked">
      <h4 className="ta-option-label" data-testid="building-not-worked-label">
        {view.label}
      </h4>
      <p className="ta-withheld-reason" data-testid="building-not-worked-reason">
        {NOT_KNOWN} — {view.reason}
      </p>
      {/* One wording per situation (ruling V11 (3)): a missing property fact carries a short tag; a
          building the method cannot yet work carries none — no "Not worked" / "still owed" line. */}
      {view.propertyInfoTag !== null ? (
        <p className="ta-property-info-tag" data-testid="building-not-worked-tag">
          {view.propertyInfoTag}
        </p>
      ) : null}
      <p className="ta-option-resolved" data-testid="building-not-worked-resolved">
        What would let it be worked: {view.resolvedBy}
      </p>
    </section>
  );
}

function AlternativeBlock({ view }: { view: BuildingAlternativeView }) {
  return (
    <section className="ta-option" data-testid="building-alternative">
      <h4 className="ta-option-label" data-testid="building-alternative-label">
        {view.label}
      </h4>
      {/* The answer AND its limitation on ONE line, the same phrase the report uses (ruling X5,
          scenario S1): "Scheduled floor area: 20,150 sq ft; site fit unverified". The figure is read
          from the document; never "achieved", never "no allowance left unused" (row R895). */}
      <p className="ta-option-scheduled" data-testid="building-alternative-scheduled">
        {scheduledFloorAreaLine(view.totalFloorArea)}
      </p>
      <p className="ta-option-summary" data-testid="building-alternative-summary">
        {storeyText(view.storeyCount)} · {view.height}
      </p>
      {view.fitNote !== null ? (
        <p className="ta-option-fit-note" data-testid="building-alternative-fit-note">
          {view.fitNote}
        </p>
      ) : null}
      {view.isWithheld && view.withheldReason !== null ? (
        <p className="ta-withheld-reason" data-testid="building-alternative-withheld">
          {NOT_KNOWN} — {view.withheldReason}
        </p>
      ) : null}
      {/* Supporting detail opens from a disclosure (ruling R928 "expandable supporting detail",
          scenario S3): the conditions this shape rests on, its floor schedule, what was not checked
          and its preliminary capacity estimate. The first view keeps the answer and its limitation;
          the detail stays in the DOM (ResultDetails uses the `hidden` attribute) so assistive tech
          and in-page search still reach it. The disclosure carries an accessible name. */}
      <ResultDetails name={`${view.label} — conditions and floor schedule`}>
        {view.isConditional ? <AppliesConditions refs={view.conditionRefs} /> : null}
        <FloorScheduleTable rows={view.floorSchedule} />
        <div className="ta-option-not-checked" data-testid="building-alternative-not-checked">
          <p className="ta-option-not-checked-heading">Not checked for this option:</p>
          <ul className="ta-option-not-checked-list">
            {view.notChecked.map((item, index) => (
              <li key={`${index}-${item}`} data-testid="building-alternative-not-checked-item">
                {item}
              </li>
            ))}
          </ul>
        </div>
        <CapacityBlock view={view.capacity} />
      </ResultDetails>
    </section>
  );
}

function FloorScheduleTable({ rows }: { rows: readonly FloorRowView[] }) {
  return (
    // N4 (ruling W15 b): on a narrow screen the six-column table scrolls INSIDE this box, not the
    // page. The box is a keyboard-reachable, named region (tabIndex 0 + role + aria-label), so a
    // keyboard or touch user can reach every column, including "Running total"; the page itself never
    // scrolls sideways (CSS overflow-x on .ta-floor-schedule-scroll).
    <div
      className="ta-floor-schedule-scroll"
      data-testid="floor-schedule-scroll"
      role="region"
      aria-label="Floor schedule"
      tabIndex={0}
    >
      <table className="ta-floor-schedule" data-testid="floor-schedule">
        <caption className="ta-floor-schedule-caption">Floor schedule</caption>
        <thead>
        <tr>
          <th scope="col">Storey</th>
          <th scope="col">Floor-to-floor</th>
          <th scope="col">Top</th>
          <th scope="col">Plan area</th>
          <th scope="col">Floor area</th>
          <th scope="col">Running total</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(row => (
          <tr key={row.storey} data-testid="floor-schedule-row">
            <th scope="row">{row.storey}</th>
            <td>{row.floorToFloor}</td>
            <td>{row.top}</td>
            <td>{row.planArea}</td>
            <td>{row.floorArea}</td>
            <td>{row.runningTotal}</td>
          </tr>
        ))}
        </tbody>
      </table>
    </div>
  );
}

function CapacityBlock({ view }: { view: CapacityView }) {
  if (view.kind === "not_known") {
    return (
      <div className="ta-capacity" data-testid="capacity-estimate">
        <p className="ta-withheld-reason" data-testid="capacity-estimate-not-known">
          {view.label} — {view.reason}
        </p>
      </div>
    );
  }
  return (
    <div className="ta-capacity" data-testid="capacity-estimate">
      <p className="ta-capacity-label" data-testid="capacity-estimate-label">
        {view.label}
      </p>
      <p className="ta-capacity-range" data-testid="capacity-estimate-range">
        {view.low} to {view.high} apartments
      </p>
      <p className="ta-capacity-wholes" data-testid="capacity-estimate-wholes">
        Between {view.wholeBelowLow} and {view.wholeAboveHigh} whole apartments, from {view.floorArea}{" "}
        of residential floor area.
      </p>
      <div className="ta-capacity-assumptions" data-testid="capacity-estimate-assumptions">
        <p className="ta-capacity-assumptions-heading">Preliminary assumptions used (not editable here):</p>
        <ul className="ta-capacity-assumptions-list">
          <li data-testid="capacity-estimate-share">
            Residential share: {view.shareLow} to {view.shareHigh}
          </li>
          <li data-testid="capacity-estimate-size">
            Apartment size: {view.apartmentSize} ({APARTMENT_SIZE_BASIS_NOTE})
          </li>
        </ul>
      </div>
    </div>
  );
}

function CoverageBlock({ view }: { view: CoverageView }) {
  if (view.kind === "withheld") {
    return (
      <section className="ta-coverage" data-testid="coverage-by-portion">
        <h4 className="ta-coverage-label" data-testid="coverage-by-portion-label">
          {view.label}
        </h4>
        <p className="ta-withheld-reason" data-testid="coverage-by-portion-reason">
          {NOT_KNOWN} — {view.reason}
        </p>
        {view.gapKindLine !== null ? (
          <p className="ta-gap-kind" data-testid="coverage-by-portion-gap-kind">
            {view.gapKindLine}
          </p>
        ) : null}
        <p className="ta-coverage-resolved" data-testid="coverage-by-portion-resolved">
          What would settle it: {view.resolvedBy}
        </p>
        <RuleSections sections={view.zrSections} />
      </section>
    );
  }
  return (
    <section className="ta-coverage" data-testid="coverage-by-portion">
      <h4 className="ta-coverage-label" data-testid="coverage-by-portion-label">
        Maximum lot coverage by portion
      </h4>
      <dl className="ta-coverage-figures">
        <div className="ta-row">
          <dt>Corner-lot portion (within {view.cornerDistance} of each street line)</dt>
          <dd>
            {view.cornerRatio}, {view.cornerArea}
          </dd>
        </div>
        <div className="ta-row">
          <dt>Interior-lot portion (the rest)</dt>
          <dd>
            {view.interiorRatio}, {view.interiorArea}
          </dd>
        </div>
        <div className="ta-row">
          <dt>Footprint the portions allow</dt>
          <dd data-testid="coverage-footprint">{view.footprint}</dd>
        </div>
      </dl>
      {view.conditions.length > 0 ? <ConditionList conditions={view.conditions} /> : null}
      <RuleSections sections={view.zrSections} />
    </section>
  );
}

/** Under the building option the shared conditions are referred to BY NAME (ruling V11 (5)): the
 * "Conditional" marker, then "Applies: Condition 1, Condition 2" in the shared-conditions card's
 * order. The full "If …" text is stated once in that card, never repeated here. */
function AppliesConditions({ refs }: { refs: readonly string[] }) {
  return (
    <div className="ta-conditional" data-testid="option-conditional">
      <span className="ta-conditional-marker" data-testid="option-conditional-marker">
        {CONDITIONAL_MARKER}
      </span>
      {refs.length > 0 ? (
        <span className="ta-applies" data-testid="option-applies">
          Applies: {refs.join(", ")}
        </span>
      ) : null}
    </div>
  );
}

function ConditionList({ conditions }: { conditions: readonly string[] }) {
  if (conditions.length === 0) return null;
  return (
    <div className="ta-conditional" data-testid="option-conditional">
      <span className="ta-conditional-marker" data-testid="option-conditional-marker">
        {CONDITIONAL_MARKER}
      </span>
      <ul className="ta-conditions">
        {conditions.map((condition, index) => (
          <li className="ta-condition" data-testid="option-condition" key={`${index}-${condition}`}>
            {condition}
          </li>
        ))}
      </ul>
    </div>
  );
}

function RuleSections({ sections }: { sections: readonly string[] }) {
  if (sections.length === 0) return null;
  return (
    <p className="ta-option-sections" data-testid="option-rule-sections">
      Based on {sections.join(", ")} as captured
    </p>
  );
}

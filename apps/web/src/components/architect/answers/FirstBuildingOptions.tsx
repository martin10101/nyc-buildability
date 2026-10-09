import type {
  BuildingAlternativeView,
  CapacityView,
  CoverageView,
  FirstBuildingOptionsView,
  FloorRowView,
  LegalLimitView,
} from "@/lib/architect/first-building-options";

/**
 * The first-building-options section (results contract 1.4.0; M5-T146 / M5-T147; rulings W1–W5;
 * D-090-R509/R526/R540/R541/R543/R544/R556/R570/R688). It reads the view built by
 * firstBuildingOptionsView and shows, from the document and never from a typed value: each worked
 * building as a LABELLED alternative (NONE preferred) with its floor schedule as a table, its way
 * (the 'Conditional' marker and each condition on its own line), what was NOT checked, and its own
 * preliminary capacity estimate under the owner's label; the legal dwelling-unit limit kept SEPARATE
 * (never a substitute); and coverage by portion — withheld with NO figure, or its figures when
 * available. Nothing is called feasible; a withheld result carries no number and no substitute
 * (R556/R570). The state is told by the WORDS, never by colour alone.
 *
 * On a draft architect surface the numbers are hidden behind the same gate the three answer cards
 * use (results.draft && !showDraftValues); the section then shows one not-reviewed line.
 */

/** The fixed marker beside a conditional figure so it never reads as confirmed (ruling L3). Plain
 * text, normal weight — the state is told by the word, never by colour alone. */
const CONDITIONAL_MARKER = "Conditional";
/** Leading words for a withheld value: it is not known, with the reason, NEVER a number (R556/R570). */
const NOT_KNOWN = "Not known";

export function FirstBuildingOptions({ view }: { view: FirstBuildingOptionsView }) {
  return (
    <section className="ta-options" data-testid="first-building-options" aria-label="Building options">
      <h3 className="ta-options-title">Building options</h3>
      <p className="ta-options-lead">
        Draft building shapes worked from the floor-area allowance. None is preferred, and none is
        checked against where it would sit on the lot.
      </p>
      {view.draftHidden ? (
        <p className="ta-not-available" data-testid="first-building-options-draft-hidden">
          {view.draftHiddenText}
        </p>
      ) : (
        <>
          {view.alternatives.map((alternative, index) => (
            <AlternativeBlock key={`${alternative.building}-${index}`} view={alternative} />
          ))}
          {view.legalLimit ? <LegalLimitBlock view={view.legalLimit} /> : null}
          {view.coverage ? <CoverageBlock view={view.coverage} /> : null}
        </>
      )}
    </section>
  );
}

function storeyCountText(count: number): string {
  return `${count} ${count === 1 ? "storey" : "storeys"}`;
}

function AlternativeBlock({ view }: { view: BuildingAlternativeView }) {
  return (
    <section className="ta-option" data-testid="building-alternative">
      <h4 className="ta-option-label" data-testid="building-alternative-label">
        {view.label}
      </h4>
      <p className="ta-option-summary" data-testid="building-alternative-summary">
        {storeyCountText(view.storeyCount)} · {view.height} · {view.totalFloorArea} total floor area
        {" · "}
        {view.unusedFloorArea} unused
      </p>
      {view.isConditional ? <ConditionList conditions={view.conditions} /> : null}
      {view.isWithheld && view.withheldReason !== null ? (
        <p className="ta-withheld-reason" data-testid="building-alternative-withheld">
          {NOT_KNOWN} — {view.withheldReason}
        </p>
      ) : null}
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
    </section>
  );
}

function FloorScheduleTable({ rows }: { rows: readonly FloorRowView[] }) {
  return (
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
        <p className="ta-capacity-assumptions-heading">Preliminary assumptions you can change:</p>
        <ul className="ta-capacity-assumptions-list">
          <li data-testid="capacity-estimate-share">
            Residential share: {view.shareLow} to {view.shareHigh}
          </li>
          <li data-testid="capacity-estimate-size">
            Apartment size: {view.apartmentSize} (on the HPD measurement basis)
          </li>
        </ul>
      </div>
    </div>
  );
}

function LegalLimitBlock({ view }: { view: LegalLimitView }) {
  return (
    <section className="ta-legal-limit" data-testid="legal-unit-limit">
      <h4 className="ta-legal-limit-label" data-testid="legal-unit-limit-label">
        {view.label}
      </h4>
      {view.kind === "value" ? (
        <>
          <p className="ta-legal-limit-value" data-testid="legal-unit-limit-value">
            {view.valueText}
          </p>
          <RuleSections sections={view.zrSections} />
        </>
      ) : (
        <p className="ta-withheld-reason" data-testid="legal-unit-limit-not-known">
          {NOT_KNOWN} — {view.reason}
        </p>
      )}
      <p className="ta-legal-limit-note">
        The legal dwelling-unit limit is kept separate from the preliminary capacity estimate above;
        it is not a substitute for it.
      </p>
    </section>
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

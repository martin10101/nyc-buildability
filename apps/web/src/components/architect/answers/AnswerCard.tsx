import type { ReactNode } from "react";
import {
  ANSWER_TITLES,
  REACHES_ALLOWANCE_TEXT,
  displayQuantity,
  quantityText,
  uniqueSections,
  type AnswerKey,
  type AnswerValue,
  type AnswerView,
  type BuildingOptionNoteView,
  type ExceptionLabel,
  type ShortfallView,
  type SupplementView,
  type Unit,
  type WithheldValueView,
} from "@/lib/architect/three-answers";
import { ResultDetails } from "./ResultDetails";

/** Leading words shown for a withheld value (results contract 1.3.0): it is not known, with the
 * reason, and NEVER a number falling back from another value (R556, R570). */
const NOT_KNOWN = "Not known";

/** The fixed marker word the website puts beside a conditional figure so the figure never reads as
 * confirmed (ruling L3; R229/R267/R269). Plain text, normal weight, never a colour-only signal. */
const CONDITIONAL_MARKER = "Conditional";

/** The building-option card's title of the figure, and the standing honesty line that leads it
 * before any caveat (ruling V11 (2); R895 "the distinction should be clear before the reader reaches
 * the caveats"). Fixed labels, never a document value. */
const SCHEDULED_AREA_LABEL = "Scheduled area";
export const SITE_FIT_NOT_VERIFIED = "Site fit not verified";

/** One lookup from a result id ("floor_area_allowance.max_residential_floor_area",
 * "building_alternative.B") to the shared conditions it refers to, by name ("Condition 1"). */
export type ConditionNames = (resultId: string) => readonly string[];

/**
 * One of the three answers, in the presentation contract's reading order (§4; M5-T149 part A, rulings
 * V11/V12 + the local-exception rule). The FACE is short: the title, the headline value (or its
 * "Not known"/"Not available" state with its short gap tag), the 'Conditional' marker, at most one
 * exception, and a Details button. The derivation opens on demand in ResultDetails — the other value
 * rows, each result's OWN exceptions, the conditions a value rests on (a one-result condition IN
 * FULL with the value; a shared condition referred to BY NAME, stated once in the shared list — §3,
 * ruling V11 (5)), the rule sections and the measurement basis. A withheld value reads one wording:
 * "Not known", the reason, then what would settle it (ruling V11 (3)).
 *
 * The split between local and shared conditions is carried on the view (three-answers.ts); the
 * `conditionNames` prop is retained for the panel's call shape and is no longer read here.
 */
export function AnswerCard({
  answerKey,
  view,
  children,
}: {
  answerKey: AnswerKey;
  view: AnswerView;
  /** Retained for the panel's call shape; the local/shared split now rides on the view. */
  conditionNames?: ConditionNames;
  /** Extra detail shown only while the answer itself is shown (remaining area, shortfall, notes). */
  children?: ReactNode;
}) {
  const title = ANSWER_TITLES[answerKey];
  if (view.kind === "not_available") {
    return (
      <section className="ta-answer" data-testid={`answer-${answerKey}`}>
        <h3 className="ta-answer-title">{title}</h3>
        <p className="ta-not-available" data-testid="answer-not-available">
          {view.text}
        </p>
        {view.gapKindLine !== null ? (
          <p className="ta-gap-kind" data-testid="answer-gap-kind">
            {view.gapKindLine}
          </p>
        ) : null}
      </section>
    );
  }
  const headlineLocal =
    view.headline.kind === "value" ? view.headline.shown.localConditions : [];
  const headlineSharedNames =
    view.headline.kind === "value" ? view.headline.shown.sharedConditionNames : [];
  const headlineConditional = headlineLocal.length > 0 || headlineSharedNames.length > 0;
  const shownValues: AnswerValue[] =
    view.headline.kind === "value"
      ? [view.headline.shown.value, ...view.rows.map(row => row.value)]
      : view.rows.map(row => row.value);
  const hasDetail =
    view.rows.length > 0 ||
    view.withheld.length > 0 ||
    shownValues.length > 0 ||
    headlineConditional ||
    children != null;
  return (
    <section className="ta-answer" data-testid={`answer-${answerKey}`}>
      <h3 className="ta-answer-title">{title}</h3>
      {view.headline.kind === "value" ? (
        <p className="ta-headline" data-testid="answer-headline">
          <span className="ta-headline-label">{view.headline.shown.value.label}</span>{" "}
          <HeadlineValue
            value={view.headline.shown.value.value}
            unit={view.headline.shown.value.unit}
          />
          <ExceptionTag label={view.headline.shown.value.exception_label} />
          {headlineConditional ? <ConditionalMarker /> : null}
        </p>
      ) : (
        <WithheldLine entry={view.headline.withheld} testid="answer-headline-withheld" />
      )}
      {hasDetail ? (
        <ResultDetails name={title}>
          {headlineConditional ? (
            <div className="ta-conditional" data-testid="answer-headline-conditions">
              {headlineLocal.length > 0 ? <LocalConditions conditions={headlineLocal} /> : null}
              {headlineSharedNames.length > 0 ? <ConditionRefs names={headlineSharedNames} /> : null}
            </div>
          ) : null}
          {view.rows.length > 0 ? (
            <dl className="ta-rows">
              {view.rows.map((row, index) => (
                <div className="ta-row" key={`${row.value.key}-${index}`} data-testid="answer-value">
                  <dt>{row.value.label}</dt>
                  <dd>
                    {quantityText(displayQuantity(row.value.value, row.value.unit))}
                    <ExceptionTag label={row.value.exception_label} />
                    {row.localConditions.length > 0 || row.sharedConditionNames.length > 0 ? (
                      <span className="ta-conditional" data-testid="answer-conditional">
                        <ConditionalMarker />
                        {row.localConditions.length > 0 ? (
                          <LocalConditions conditions={row.localConditions} />
                        ) : null}
                        {row.sharedConditionNames.length > 0 ? (
                          <ConditionRefs names={row.sharedConditionNames} />
                        ) : null}
                      </span>
                    ) : null}
                  </dd>
                </div>
              ))}
            </dl>
          ) : null}
          {view.withheld.length > 0 ? (
            <dl className="ta-withheld" data-testid="answer-withheld">
              {view.withheld.map((entry, index) => (
                <div
                  className="ta-row"
                  key={`${entry.key}-${index}`}
                  data-testid="answer-withheld-value"
                >
                  <dt>{entry.label}</dt>
                  <dd>
                    <WithheldLine entry={entry} />
                  </dd>
                </div>
              ))}
            </dl>
          ) : null}
          {children}
          {shownValues.length > 0 ? (
            <>
              <p className="ta-sections-heading">Rule sections</p>
              <ul className="ta-sections">
                {shownValues.map((value, index) => (
                  <li key={`${value.key}-${index}`} data-testid="answer-section">
                    {value.label}: {uniqueSections(value.zr_sections).join(", ")}
                  </li>
                ))}
              </ul>
              <p className="ta-measurement">Measurements: {view.measurementLabel}</p>
            </>
          ) : null}
        </ResultDetails>
      ) : null}
    </section>
  );
}

/** The building-option card as the SCHEDULED area (ruling V11 (2); R895): when a building is listed
 * it reads "Scheduled area: 20,150 sq ft" with "Site fit not verified" ahead of any caveat, and
 * never "Not available"/"shown below"; when none is listed it reads "Not known" with the document's
 * reason and what would settle it (one wording — ruling V11 (3)). The area is read from the listed
 * building through Part B's view model; the standing lines are fixed labels. */
export type BuildingOptionCardView =
  | { kind: "not_reviewed"; text: string }
  | { kind: "scheduled"; scheduledArea: string; conditionNames: readonly string[] }
  | { kind: "not_known"; reason: string; gapTag: string | null; resolvedBy: string | null };

export function BuildingOptionCard({ view }: { view: BuildingOptionCardView }) {
  const title = ANSWER_TITLES.building_option;
  if (view.kind === "not_reviewed") {
    return (
      <section className="ta-answer" data-testid="answer-building_option">
        <h3 className="ta-answer-title">{title}</h3>
        <p className="ta-not-available" data-testid="answer-not-available">
          {view.text}
        </p>
      </section>
    );
  }
  if (view.kind === "not_known") {
    return (
      <section className="ta-answer" data-testid="answer-building_option">
        <h3 className="ta-answer-title">{title}</h3>
        <p className="ta-not-available" data-testid="answer-not-known">
          {NOT_KNOWN} — {view.reason}
        </p>
        {view.gapTag !== null ? (
          <p className="ta-gap-kind" data-testid="answer-gap-kind">
            {view.gapTag}
          </p>
        ) : null}
        {view.resolvedBy !== null ? (
          <p className="ta-resolver" data-testid="answer-resolver">
            What would settle it: {view.resolvedBy}
          </p>
        ) : null}
      </section>
    );
  }
  return (
    <section className="ta-answer" data-testid="answer-building_option">
      <h3 className="ta-answer-title">{title}</h3>
      <p className="ta-headline" data-testid="answer-headline">
        <span className="ta-headline-label">{SCHEDULED_AREA_LABEL}</span>{" "}
        <span className="ta-scheduled-area" data-testid="answer-scheduled-area">
          {view.scheduledArea}
        </span>
      </p>
      <p className="ta-site-fit" data-testid="answer-site-fit">
        {SITE_FIT_NOT_VERIFIED}
      </p>
      {view.conditionNames.length > 0 ? (
        <ResultDetails name={title}>
          <ConditionRefs names={view.conditionNames} />
        </ResultDetails>
      ) : null}
    </section>
  );
}

/** A withheld value: one wording (ruling V11 (3)) — "Not known", the reason, the short gap tag when
 * a property fact is missing, then what would settle it. NEVER a number (R556, R570). As a headline
 * (no dt) or a row. */
function WithheldLine({
  entry,
  testid,
}: {
  entry: WithheldValueView;
  testid?: string;
}) {
  return (
    <>
      <span className="ta-withheld-reason" data-testid={testid ?? "answer-withheld-reason"}>
        {testid ? `${entry.label}: ` : null}
        {NOT_KNOWN} — {entry.reason}
      </span>
      {entry.gapKindLine !== null ? (
        <span className="ta-gap-kind" data-testid="answer-gap-kind">
          {entry.gapKindLine}
        </span>
      ) : null}
      {entry.resolvedBy !== null ? (
        <span className="ta-resolver" data-testid="answer-resolver">
          What would settle it: {entry.resolvedBy}
        </span>
      ) : null}
    </>
  );
}

/** The fixed 'Conditional' marker beside a conditional figure (ruling L1/L3), normal weight: told
 * apart by the WORD, never by colour alone. The condition texts are stated once at the top. */
function ConditionalMarker() {
  return (
    <>
      {" "}
      <span className="ta-conditional-marker" data-testid="answer-conditional-marker">
        {CONDITIONAL_MARKER}
      </span>
    </>
  );
}

/** Refers to the shared conditions BY NAME (ruling V11 (5)): "Applies: Condition 1, Condition 2" —
 * never the full text again. Nothing is drawn when the value refers to no shared condition. */
function ConditionRefs({ names }: { names: readonly string[] }) {
  if (names.length === 0) return null;
  return (
    <span className="ta-condition-refs" data-testid="answer-condition-refs">
      Applies: {names.join(", ")}
    </span>
  );
}

/** A condition that applies to THIS result only, shown IN FULL with the value — one sentence per
 * line (the contract's local-exception rule, "a condition that changes a number stays attached to
 * that number"). Each line is the document's assumption, never retyped. */
function LocalConditions({ conditions }: { conditions: readonly string[] }) {
  if (conditions.length === 0) return null;
  return (
    <ul className="ta-conditions">
      {conditions.map((condition, index) => (
        <li className="ta-condition" data-testid="answer-condition" key={`${index}-${condition}`}>
          {condition}
        </li>
      ))}
    </ul>
  );
}

function HeadlineValue({ value, unit }: { value: number; unit: Unit }) {
  const quantity = displayQuantity(value, unit);
  return (
    <span className="ta-headline-value">
      <span className="ta-headline-number" data-testid="answer-headline-number">
        {quantity.number}
      </span>
      {quantity.unit === "%" ? (
        <span className="ta-headline-unit ta-headline-unit-tight">%</span>
      ) : quantity.unit ? (
        <>
          {" "}
          <span className="ta-headline-unit">{quantity.unit}</span>
        </>
      ) : null}
    </span>
  );
}

/** At most one exception beside a number, only one that changes how to read it (§4). */
function ExceptionTag({ label }: { label: ExceptionLabel }) {
  if (!label) return null;
  return (
    <>
      {" "}
      <span className="ta-exception" data-testid="answer-exception">
        {label}
      </span>
    </>
  );
}

/** A value row added to an available answer, or its own not-available line and, when the view
 * carries one, its reason line under it (D-090-R038). Shown inside the answer's details. */
export function SupplementRow({ view }: { view: SupplementView }) {
  return (
    <dl className="ta-rows ta-supplement" data-testid="answer-supplement">
      <div className="ta-row">
        <dt>{view.label}</dt>
        <dd>
          {view.kind === "value" ? (
            quantityText(view.quantity)
          ) : (
            <span className="ta-not-available" data-testid="answer-supplement-not-available">
              {view.text}
            </span>
          )}
        </dd>
        {view.kind === "not_available" && view.reason ? (
          <dd className="ta-supplement-reason" data-testid="answer-supplement-reason">
            {view.reason}
          </dd>
        ) : null}
      </div>
    </dl>
  );
}

/** How much of the allowance the building option reaches, and why (plan §5 answer 3). */
export function ShortfallBlock({ view }: { view: ShortfallView }) {
  if (view.kind === "not_available") {
    return <SupplementRow view={view} />;
  }
  if (view.kind === "reaches_allowance") {
    return (
      <p className="ta-shortfall" data-testid="answer-shortfall">
        {REACHES_ALLOWANCE_TEXT}
      </p>
    );
  }
  return (
    <div className="ta-shortfall" data-testid="answer-shortfall">
      <p>
        Falls short of the allowance by{" "}
        <strong data-testid="answer-shortfall-amount">{quantityText(view.amount)}</strong>. Why:
      </p>
      <ul className="ta-shortfall-reasons">
        {view.reasons.map((reason, index) => (
          <li key={`${index}-${reason}`} data-testid="answer-shortfall-reason">
            {reason}
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * The building option's draft notes (results contract 1.2.0, D-090-R132): each a DRAFT reading of
 * the captured zoning text, under a fixed heading marking it pending qualified review — never a
 * compliance statement. An empty list draws nothing. The note text and "Based on …" line cite ZR
 * sections, so they carry the `answer-section` testid the panel guard strips.
 */
export function BuildingOptionNotes({ notes }: { notes: readonly BuildingOptionNoteView[] }) {
  if (notes.length === 0) return null;
  return (
    <section
      className="ta-option-notes"
      data-testid="building-option-notes"
      aria-label="Draft reading pending qualified review"
    >
      {notes.map((note, index) => (
        <div className="ta-option-note" data-testid="building-option-note" key={index}>
          <p className="ta-option-note-heading" data-testid="building-option-note-heading">
            {note.draftLabel}
          </p>
          <p className="ta-option-note-kind">{note.kindLabel}</p>
          <p className="ta-option-note-text" data-testid="answer-section">
            {note.text}
          </p>
          <p className="ta-option-note-sections" data-testid="answer-section">
            Based on {note.zrSections.join(", ")} as captured
          </p>
          {note.snapshotIds.length > 0 ? (
            <details className="ta-option-note-snapshots">
              <summary>Captured snapshots</summary>
              <ul
                className="ta-option-note-snapshot-list"
                data-testid="building-option-note-snapshots"
              >
                {note.snapshotIds.map((id, snapshotIndex) => (
                  <li key={`${id}-${snapshotIndex}`}>{id}</li>
                ))}
              </ul>
            </details>
          ) : null}
        </div>
      ))}
    </section>
  );
}

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

/**
 * One of the three answers, in the presentation contract's reading order (§4 "label → value and
 * unit, or unavailable state → material exception → details action"; M5-T149 part A). The FACE is
 * deliberately short: the answer's title, its headline value (or its "Not known"/"Not available"
 * state with the kind of gap), the one marker that qualifies the figure ('Conditional'), at most one
 * exception, and a Details button. The derivation — the other value rows, the condition texts, the
 * withheld values, the rule sections and the measurement basis — opens on demand in ResultDetails
 * (focus moves in; Escape returns to the button). A not-available answer shows only its one line and
 * its kind-of-gap line: no number, no exception, no details.
 */
export function AnswerCard({
  answerKey,
  view,
  children,
}: {
  answerKey: AnswerKey;
  view: AnswerView;
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
  const headlineConditions =
    view.headline.kind === "value" ? view.headline.shown.conditions : [];
  const shownValues: AnswerValue[] =
    view.headline.kind === "value"
      ? [view.headline.shown.value, ...view.rows.map(row => row.value)]
      : view.rows.map(row => row.value);
  const hasDetail =
    view.rows.length > 0 ||
    view.withheld.length > 0 ||
    shownValues.length > 0 ||
    headlineConditions.length > 0 ||
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
          {headlineConditions.length > 0 ? <ConditionalMarker /> : null}
        </p>
      ) : (
        <WithheldLine entry={view.headline.withheld} testid="answer-headline-withheld" />
      )}
      {hasDetail ? (
        <ResultDetails name={title}>
          {headlineConditions.length > 0 ? (
            <div className="ta-conditional" data-testid="answer-headline-conditions">
              <p className="ta-conditional-note">This figure applies when:</p>
              <ConditionLines conditions={headlineConditions} />
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
                    {row.conditions.length > 0 ? (
                      <ConditionBlock conditions={row.conditions} />
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

/** A withheld value: its reason, never a number (R556, R570), then — when the document carries
 * one — the plain-words kind of gap (missing information or work still owed; R258, ruling R6).
 * As a headline (no dt) or a row. */
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
    </>
  );
}

/** The fixed 'Conditional' marker shown beside a conditional figure (ruling L1/L3), in normal
 * weight: the figure is told apart by the WORD, never by colour alone. The condition texts
 * themselves are stated once at the top (shared conditions) and in the answer's details. */
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

/** One "If <assumption>" line per condition, read from the document (ruling L1). */
function ConditionLines({ conditions }: { conditions: readonly string[] }) {
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

/** A conditional value's marker and its condition lines together (used for a non-headline row). */
function ConditionBlock({ conditions }: { conditions: readonly string[] }) {
  if (conditions.length === 0) return null;
  return (
    <div className="ta-conditional" data-testid="answer-conditional">
      <ConditionalMarker />
      <ConditionLines conditions={conditions} />
    </div>
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
 * The building option's draft notes beside the heights (results contract 1.2.0, D-090-R132):
 * each is a DRAFT reading of the captured zoning text, shown openly under a fixed heading that
 * marks it pending qualified review — never a compliance statement. Rendered as a child of the
 * building-option card's details, so it appears only while that card shows its heights; an empty
 * list draws nothing.
 *
 * The note text and the "Based on …" line cite ZR sections (e.g. "ZR 23-432"), which is also a
 * building-option value's `zoning_resolution` source. The panel guard
 * (three-answers-panel.test.tsx) requires every such citation to live only inside the
 * `answer-section` citation surface it strips, so these two visible lines carry that testid.
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

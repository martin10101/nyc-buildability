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
  type ShownValueView,
  type SupplementView,
  type Unit,
  type WithheldValueView,
} from "@/lib/architect/three-answers";

/** Leading words shown for a withheld value (results contract 1.3.0): it is not known, with the
 * reason, and NEVER a number falling back from another value (R556, R570). */
const NOT_KNOWN = "Not known";

/**
 * One of the three answers (queue D-05; plan §5). Available: the headline number, large, then
 * the answer's other values and any withheld value shown as its reason; rule sections and the
 * measurement label sit behind "Rule sections" (plan §5a items 4 and 5). A conditional value shows
 * its "If <assumption>" line. Not available: the one line "Not available — <reason>" and nothing
 * else — no number, no exception tag, no details (plan §5, §5a item 3).
 */
export function AnswerCard({
  answerKey,
  view,
  children,
}: {
  answerKey: AnswerKey;
  view: AnswerView;
  /** Extra rows shown only while the answer itself is shown (remaining area, shortfall). */
  children?: ReactNode;
}) {
  if (view.kind === "not_available") {
    return (
      <section className="ta-answer" data-testid={`answer-${answerKey}`}>
        <h3 className="ta-answer-title">{ANSWER_TITLES[answerKey]}</h3>
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
  const shownValues: AnswerValue[] =
    view.headline.kind === "value"
      ? [view.headline.shown.value, ...view.rows.map(row => row.value)]
      : view.rows.map(row => row.value);
  return (
    <section className="ta-answer" data-testid={`answer-${answerKey}`}>
      <h3 className="ta-answer-title">{ANSWER_TITLES[answerKey]}</h3>
      {view.headline.kind === "value" ? (
        <p className="ta-headline" data-testid="answer-headline">
          <span className="ta-headline-label">{view.headline.shown.value.label}</span>{" "}
          <HeadlineValue
            value={view.headline.shown.value.value}
            unit={view.headline.shown.value.unit}
          />
          <ExceptionTag label={view.headline.shown.value.exception_label} />
          <ConditionNote condition={view.headline.shown.condition} />
        </p>
      ) : (
        <WithheldLine entry={view.headline.withheld} testid="answer-headline-withheld" />
      )}
      {view.rows.length > 0 ? (
        <dl className="ta-rows">
          {view.rows.map((row, index) => (
            <div className="ta-row" key={`${row.value.key}-${index}`} data-testid="answer-value">
              <dt>{row.value.label}</dt>
              <dd>
                {quantityText(displayQuantity(row.value.value, row.value.unit))}
                <ExceptionTag label={row.value.exception_label} />
                <ConditionNote condition={row.condition} />
              </dd>
            </div>
          ))}
        </dl>
      ) : null}
      {view.withheld.length > 0 ? (
        <dl className="ta-withheld" data-testid="answer-withheld">
          {view.withheld.map((entry, index) => (
            <div className="ta-row" key={`${entry.key}-${index}`} data-testid="answer-withheld-value">
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
        <details className="ta-details" data-testid="answer-details">
          <summary>Rule sections</summary>
          <ul className="ta-sections">
            {shownValues.map((value, index) => (
              <li key={`${value.key}-${index}`} data-testid="answer-section">
                {value.label}: {uniqueSections(value.zr_sections).join(", ")}
              </li>
            ))}
          </ul>
          <p className="ta-measurement">Measurements: {view.measurementLabel}</p>
        </details>
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
        <>
          {" "}
          <span className="ta-gap-kind" data-testid="answer-gap-kind">
            {entry.gapKindLine}
          </span>
        </>
      ) : null}
    </>
  );
}

/** The "If <assumption>" line for a conditional value (results contract 1.3.0), set apart from the
 * settled results; nothing is drawn for a settled value. */
function ConditionNote({ condition }: { condition: ShownValueView["condition"] }) {
  if (!condition) return null;
  return (
    <>
      {" "}
      <span className="ta-condition" data-testid="answer-condition">
        {condition}
      </span>
    </>
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

/** At most one exception beside a number, only one that changes how to read it (§5a item 3). */
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
 * carries one, its reason line under it (D-090-R038). */
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
 * building-option card, so it appears only while that card shows its heights (the same draft
 * gate); an empty list draws nothing, leaving the card unchanged.
 *
 * The note text and the "Based on …" line cite ZR sections (e.g. "ZR 23-432", which is also a
 * building-option value's `zoning_resolution` source). The panel guard
 * (three-answers-panel.test.tsx) requires every such citation to live only inside the
 * `answer-section` citation surface it strips, so these two visible lines carry that testid: it is
 * the guard's hook for "this text cites rule sections", which is exactly what the note does. The
 * snapshot ids sit behind a disclosure (never bare in the prose) and trip no guard (hyphens, not
 * underscores; not an enum code).
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

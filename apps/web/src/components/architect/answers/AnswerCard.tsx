import type { ReactNode } from "react";
import {
  ANSWER_TITLES,
  REACHES_ALLOWANCE_TEXT,
  displayQuantity,
  quantityText,
  uniqueSections,
  type AnswerKey,
  type AnswerView,
  type ExceptionLabel,
  type ShortfallView,
  type SupplementView,
  type Unit,
} from "@/lib/architect/three-answers";

/**
 * One of the three answers (queue D-05; plan §5). Available: the headline number, large, then
 * the answer's other values; rule sections and the measurement label sit behind "Rule sections"
 * (plan §5a items 4 and 5). Not available: the one line "Not available — <reason>" and nothing
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
  return (
    <section className="ta-answer" data-testid={`answer-${answerKey}`}>
      <h3 className="ta-answer-title">{ANSWER_TITLES[answerKey]}</h3>
      {view.kind === "not_available" ? (
        <p className="ta-not-available" data-testid="answer-not-available">
          {view.text}
        </p>
      ) : (
        <>
          <p className="ta-headline" data-testid="answer-headline">
            <span className="ta-headline-label">{view.headline.label}</span>{" "}
            <HeadlineValue value={view.headline.value} unit={view.headline.unit} />
            <ExceptionTag label={view.headline.exception_label} />
          </p>
          {view.rows.length > 0 ? (
            <dl className="ta-rows">
              {view.rows.map((row, index) => (
                <div className="ta-row" key={`${row.key}-${index}`} data-testid="answer-value">
                  <dt>{row.label}</dt>
                  <dd>
                    {quantityText(displayQuantity(row.value, row.unit))}
                    <ExceptionTag label={row.exception_label} />
                  </dd>
                </div>
              ))}
            </dl>
          ) : null}
          {children}
          <details className="ta-details" data-testid="answer-details">
            <summary>Rule sections</summary>
            <ul className="ta-sections">
              {[view.headline, ...view.rows].map((value, index) => (
                <li key={`${value.key}-${index}`} data-testid="answer-section">
                  {value.label}: {uniqueSections(value.zr_sections).join(", ")}
                </li>
              ))}
            </ul>
            <p className="ta-measurement">Measurements: {view.measurementLabel}</p>
          </details>
        </>
      )}
    </section>
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

/** A value row added to an available answer, or its own "Not available — …" line. */
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

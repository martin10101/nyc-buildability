"use client";

/**
 * Step 4 "Existing building" of the lot & site setup window (queue D-06 slice 2; plan §3 step 4).
 * Presentation only, over the view model in @/lib/architect/existing-building-view:
 *  - a three-way choice (keep / remove / no existing building) as a labelled radio group, written
 *    to the study option through the store (the parent wires `onChoosePlan`); nothing is pre-selected
 *    — an unchosen plan shows an honest "no choice made yet" line;
 *  - when "keep" is chosen, the existing ZONING floor area: a known value with its unit and source
 *    label (and the architect's "Entered"/"Assumed" value beside a kept city filing), or
 *    "Unknown — enter" naming what it blocks, with an entry whose source the architect picks
 *    explicitly (architect entry or stated assumption) — never a city source;
 *  - remove / no existing building hides the floor-area entry.
 *
 * No remaining capacity is computed or shown here (plan §3 step 4; owner D-090-R038): that stays
 * "Remaining development capacity: Not confirmed" elsewhere. No legal logic lives here.
 */

import { useState, type FormEvent } from "react";
import { MEASUREMENT_LABELS, type SiteFact } from "@/lib/study/study-vocabulary";
import {
  CHOOSE_SOURCE_REASON,
  EXISTING_BUILDING_GROUP_LABEL,
  EXISTING_BUILDING_STEP_HEADING,
  EXISTING_BUILDING_UNCHOSEN_NOTE,
  EXISTING_FLOOR_AREA_INPUT_LABEL,
  EXISTING_FLOOR_AREA_SOURCE_CHOICES,
  EXISTING_FLOOR_AREA_SOURCE_LEGEND,
  existingBuildingPlanOptions,
  existingFloorAreaGroup,
  validateExistingFloorAreaInput,
  type ExistingBuildingPlan,
  type ExistingFloorAreaSourceKind,
} from "@/lib/architect/existing-building-view";

export interface ExistingBuildingStepProps {
  /** The study's current plan, or null when no study/option exists yet (setup-only working copy). */
  plan: ExistingBuildingPlan | null;
  onChoosePlan: (plan: ExistingBuildingPlan) => void;
  /** The source site facts (the existing-zfa fact is found here). */
  facts: SiteFact[];
  /** Records the entered value; returns null on success, or a plain reason to show on the row. */
  onRecordFloorArea: (value: number, sourceKind: ExistingFloorAreaSourceKind) => string | null;
}

/** The existing zoning floor area entry: the number plus the architect's explicit source choice. */
function ExistingFloorAreaEntry({
  onRecordFloorArea,
  onDone,
  cancellable,
}: {
  onRecordFloorArea: ExistingBuildingStepProps["onRecordFloorArea"];
  onDone: () => void;
  cancellable: boolean;
}) {
  const [value, setValue] = useState("");
  const [sourceKind, setSourceKind] = useState<ExistingFloorAreaSourceKind | null>(null);
  const [error, setError] = useState<string | null>(null);

  function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const parsed = validateExistingFloorAreaInput(value);
    if (!parsed.ok) {
      setError(parsed.reason);
      return;
    }
    if (sourceKind === null) {
      setError(CHOOSE_SOURCE_REASON);
      return;
    }
    const reason = onRecordFloorArea(parsed.value as number, sourceKind);
    if (reason) {
      setError(reason);
      return;
    }
    setValue("");
    setSourceKind(null);
    setError(null);
    onDone();
  }

  return (
    <form className="existing-building__entry" onSubmit={save}>
      <label>
        {EXISTING_FLOOR_AREA_INPUT_LABEL}
        <input
          type="text"
          inputMode="numeric"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          data-testid="existing-floor-area-input"
        />
      </label>
      <fieldset className="existing-building__source">
        <legend>{EXISTING_FLOOR_AREA_SOURCE_LEGEND}</legend>
        {EXISTING_FLOOR_AREA_SOURCE_CHOICES.map((choice) => (
          <label key={choice.kind}>
            <input
              type="radio"
              name="existing-floor-area-source"
              value={choice.kind}
              checked={sourceKind === choice.kind}
              onChange={() => setSourceKind(choice.kind)}
              data-testid={`existing-floor-area-source-${choice.kind}`}
            />
            {choice.label}
          </label>
        ))}
      </fieldset>
      <div className="existing-building__entry-actions">
        <button type="submit" className="secondary-button" data-testid="existing-floor-area-save">
          Save
        </button>
        {cancellable ? (
          <button type="button" className="architect-text-button" onClick={onDone}>
            Cancel
          </button>
        ) : null}
      </div>
      {error ? (
        <p className="lot-site-fact__error" role="alert" data-testid="existing-floor-area-error">
          {error}
        </p>
      ) : null}
    </form>
  );
}

/** The existing zoning floor area block, shown only when the plan is "keep". */
function ExistingFloorArea({
  facts,
  onRecordFloorArea,
}: {
  facts: SiteFact[];
  onRecordFloorArea: ExistingBuildingStepProps["onRecordFloorArea"];
}) {
  const [editing, setEditing] = useState(false);
  const group = existingFloorAreaGroup(facts);
  const primary = group?.primary ?? null;

  return (
    <div className="existing-building__floor-area" data-testid="existing-floor-area">
      <h3>Existing zoning floor area</h3>
      {primary !== null && !primary.isUnknown ? (
        <>
          <p>
            <span className="lot-site-fact__value" data-testid="existing-floor-area-value">
              {primary.valueText}
            </span>
            <span className="lot-site-fact__source" data-testid="existing-floor-area-source-label">
              {primary.sourceLabel}
            </span>
          </p>
          {group?.entered ? (
            <p className="lot-site-fact__entered" data-testid="existing-floor-area-entered">
              {group.entered.sourceLabel}: {group.entered.valueText}
            </p>
          ) : null}
          <details className="lot-site-fact__detail">
            <summary>Source</summary>
            <ul>
              {primary.sourceLines.map((line, index) => (
                <li key={index}>{line}</li>
              ))}
            </ul>
          </details>
          {editing ? (
            <ExistingFloorAreaEntry onRecordFloorArea={onRecordFloorArea} onDone={() => setEditing(false)} cancellable />
          ) : (
            <button
              type="button"
              className="architect-text-button"
              data-testid="existing-floor-area-change"
              onClick={() => setEditing(true)}
            >
              Change value
            </button>
          )}
        </>
      ) : (
        <>
          <p className="lot-site-fact__value lot-site-fact__value--unknown">{MEASUREMENT_LABELS.unknown}</p>
          {primary && primary.blocks.length ? (
            <p className="lot-site-fact__blocks">Needed for: {primary.blocks.join(", ")}.</p>
          ) : null}
          <ExistingFloorAreaEntry onRecordFloorArea={onRecordFloorArea} onDone={() => setEditing(false)} cancellable={false} />
        </>
      )}
    </div>
  );
}

export function ExistingBuildingStep({ plan, onChoosePlan, facts, onRecordFloorArea }: ExistingBuildingStepProps) {
  return (
    <section className="card" aria-label="Existing building" data-testid="existing-building-step">
      <h2>{EXISTING_BUILDING_STEP_HEADING}</h2>
      <fieldset className="existing-building__plan">
        <legend>{EXISTING_BUILDING_GROUP_LABEL}</legend>
        {existingBuildingPlanOptions().map((option) => (
          <label key={option.value}>
            <input
              type="radio"
              name="existing-building-plan"
              value={option.value}
              checked={plan === option.value}
              onChange={() => onChoosePlan(option.value)}
              data-testid={`existing-building-plan-${option.value}`}
            />
            {option.label}
          </label>
        ))}
      </fieldset>
      {plan === null ? (
        <p className="section-note" data-testid="existing-building-unchosen">
          {EXISTING_BUILDING_UNCHOSEN_NOTE}
        </p>
      ) : null}
      {plan === "keep" ? (
        <ExistingFloorArea facts={facts} onRecordFloorArea={onRecordFloorArea} />
      ) : null}
    </section>
  );
}

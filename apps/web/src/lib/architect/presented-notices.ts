// Presentation adapter: shared conditions stated once, and a cap of three notices (M5-T148 part B;
// presentation contract §1 "State shared context once; retain a local exception only where it
// changes that result", §3 "Show at most three important notices at once; group additional notices
// behind a meaningful count"). Pure. It decides no law and recalculates nothing (ruling V2): every
// condition line is READ from the document (through three-answers' conditionList), only grouped.
//
// Two jobs, no number produced by either:
//  - collectConditions: the "If …" lines that repeat under many results are listed ONCE, in
//    first-appearance order, and each result refers to the shared lines; none is lost.
//  - capNotices: at most three notices are shown; the rest are counted ("2 more"), never dropped.

import { conditionList, type ThreeAnswersResults } from "./three-answers";
import type { ValueState } from "../../../../../packages/contracts/generated/results";

/** At most three notices are shown at once (presentation contract §3). */
export const MAX_NOTICES = 3;

/** One distinct condition, listed once and referred to by id from each result it applies to. */
export interface SharedCondition {
  /** A stable reference id, "C1", "C2", … in first-appearance order. */
  id: string;
  /** The "If …" line, read from the document (three-answers' conditionList). */
  text: string;
}

/** One result and the shared conditions it refers to, by id (never the text again). */
export interface ResultConditionRefs {
  /** A stable id for the result, e.g. "floor_area_allowance.max_residential_floor_area". */
  resultId: string;
  conditionIds: readonly string[];
}

export interface PresentedConditions {
  /** The distinct conditions, each once, in first-appearance order. */
  shared: readonly SharedCondition[];
  /** Each result that carries at least one condition, with the ids it refers to. */
  references: readonly ResultConditionRefs[];
}

// The answers whose values can carry conditional value_states.
const ANSWER_KEYS = ["floor_area_allowance", "permitted_envelope", "building_option"] as const;

function valueStates(answer: ThreeAnswersResults["answers"][keyof ThreeAnswersResults["answers"]]):
  Record<string, ValueState> {
  if (answer.status !== "available") return {};
  const states = answer.value_states;
  return states ? (states as Record<string, ValueState>) : {};
}

/**
 * Collect the document's conditions once. Walks every conditional value_state of the three answers,
 * each worked building alternative's `way`, and a conditional coverage-by-portion `way`; reads each
 * "If …" line through three-answers' conditionList; dedupes by exact text in first-appearance order;
 * and records, per result, the shared ids it refers to. A result with no condition is omitted from
 * `references`. No line is lost: every distinct condition text in the document appears once in
 * `shared`, and `references` preserves which result carried it.
 */
export function collectConditions(results: ThreeAnswersResults): PresentedConditions {
  const idByText = new Map<string, string>();
  const shared: SharedCondition[] = [];
  const references: ResultConditionRefs[] = [];

  const idFor = (text: string): string => {
    const existing = idByText.get(text);
    if (existing) return existing;
    const id = `C${shared.length + 1}`;
    idByText.set(text, id);
    shared.push({ id, text });
    return id;
  };

  const record = (resultId: string, state: ValueState | undefined): void => {
    const lines = conditionList(state);
    if (lines.length === 0) return;
    references.push({ resultId, conditionIds: lines.map(idFor) });
  };

  for (const key of ANSWER_KEYS) {
    const states = valueStates(results.answers[key]);
    for (const [stateKey, state] of Object.entries(states)) {
      record(`${key}.${stateKey}`, state);
    }
  }
  for (const alternative of results.building_alternatives ?? []) {
    record(`building_alternative.${alternative.building}`, alternative.way);
  }
  const coverage = results.coverage_by_portion;
  if (coverage && coverage.status === "available") {
    record("coverage_by_portion", coverage.way);
  }

  return { shared, references };
}

/** At most `max` notices shown; the rest counted behind a "N more" label, never dropped. */
export interface CappedNotices<T> {
  visible: readonly T[];
  hidden: readonly T[];
  /** "N more" when some are hidden, else null. */
  moreLabel: string | null;
}

/**
 * Show at most `max` notices (default three); the rest are hidden but counted, so a reader always
 * sees how many are behind the count. Five notices give three visible and "2 more"; three or fewer
 * give them all and no label. No notice is ever dropped: `visible` and `hidden` partition the input.
 */
export function capNotices<T>(notices: readonly T[], max: number = MAX_NOTICES): CappedNotices<T> {
  const visible = notices.slice(0, max);
  const hidden = notices.slice(max);
  return {
    visible,
    hidden,
    moreLabel: hidden.length > 0 ? `${hidden.length} more` : null,
  };
}

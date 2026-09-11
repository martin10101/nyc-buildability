import { formatValue } from "@/lib/format";
import {
  SCENARIO_KIND_LABELS,
  baseDistrictCandidates,
  findConstraint,
  ruleConflicts,
} from "@/lib/scenario-display";
import type { Scenario } from "@/lib/scenario-contract";

/**
 * The informative "no maximum can be stated" block for a `no_scenario` or
 * `unsupported` document (task M5-T004; extracted from ScenarioResult in the
 * rework so the competing-rule display has somewhere cohesive to live).
 *
 * THE COMPETING-RULE DISPLAY IS THE POINT OF THIS REWORK HERE. The
 * `data_conflict` coverage gloss reads "Official sources disagree; both values
 * are shown, nothing was resolved" and the screen printed it TWICE while
 * showing NEITHER value, because `ruleConflict()` had zero consumers repo-wide
 * — exported, so no-unused-vars never fired (G1-6, G3-7, G4-3, DCV-6). A UI
 * must not claim something its own render path contradicts. The competing rules
 * are now surfaced verbatim, and the platform still selects no winner: which
 * rule governs is a legal determination.
 *
 * `reasons` is NOT rendered here any more — it moved to ScenarioReasons, which
 * every branch mounts (it used to render only on this branch, so the branch
 * that shows a number dropped it).
 */

function RuleConflictBlock({ document }: { document: Scenario }) {
  const conflicts = ruleConflicts(document);
  const conflictingConstraints = document.constraints.filter(
    (constraint) => constraint.state === "conflicting",
  );
  if (conflicts.length === 0 && conflictingConstraints.length === 0) return null;
  return (
    <div data-testid="scenario-rule-conflict">
      <h3 className="section-subtitle">
        Competing rules and conflicting values (nothing was resolved)
      </h3>
      <p className="section-note">
        More than one draft rule is simultaneously in effect over the same
        output, or sources disagree. Which one governs is a legal determination,
        so the platform picked no winner and produced no value. Both sides are
        shown below.
      </p>

      {conflictingConstraints.length > 0 ? (
        <ul className="missing-list" data-testid="scenario-conflicting-values">
          {conflictingConstraints.map((constraint, index) => (
            <li key={`conflicting-${index}`}>
              <strong>{constraint.key}</strong>
              {": "}
              <span className="fact-value">{formatValue(constraint.value)}</span>
              {constraint.unit !== null ? (
                <span className="fact-units"> {constraint.unit}</span>
              ) : null}{" "}
              <span className="section-note">
                (state: <code>{constraint.state}</code>)
              </span>
            </li>
          ))}
        </ul>
      ) : null}

      {conflicts.map(({ constraintKey, conflict }, conflictIndex) => (
        <div key={`conflict-${conflictIndex}`}>
          <p className="section-note" style={{ marginBottom: 0 }}>
            Recorded on constraint <code>{constraintKey}</code>
            {conflict.competingOutputNames.length > 0 ? (
              <>
                {" "}— the conflict is over output(s):{" "}
                <strong>{conflict.competingOutputNames.join(", ")}</strong>
              </>
            ) : (
              " — the document names no competing output"
            )}
            .
          </p>
          {conflict.competingRules.length === 0 ? (
            <p className="section-note">
              No competing rules are listed on this constraint, only the
              competing output name(s) above.
            </p>
          ) : (
            <ul className="missing-list" data-testid="scenario-competing-rules">
              {conflict.competingRules.map((rule, ruleIndex) => (
                <li key={`rule-${conflictIndex}-${ruleIndex}`}>
                  <code>{rule.ruleId ?? "rule id not stated"}</code> (
                  {rule.ruleVersion ?? "version not stated"}) — in effect{" "}
                  {rule.effectiveFrom ?? "start not stated"} to{" "}
                  {rule.effectiveTo ?? "present"}
                  {rule.outputNames.length > 0
                    ? ` · emits ${rule.outputNames.join(", ")}`
                    : ""}
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}

function ShareRangeBlock({ document }: { document: Scenario }) {
  const candidates = baseDistrictCandidates(findConstraint(document, "zoning_district"));
  if (candidates.length === 0) return null;
  return (
    <>
      <h3 className="section-subtitle">
        Preserved base-district share ranges (never collapsed)
      </h3>
      <ul className="missing-list" data-testid="scenario-share-ranges">
        {candidates.map((candidate, index) => (
          <li key={`candidate-${index}`} data-testid="scenario-share-range">
            <strong>{candidate.districtLabel ?? "Unlabelled district"}</strong>
            {": "}
            share range min {formatValue(candidate.shareMin)} / point{" "}
            {formatValue(candidate.sharePoint)} / max{" "}
            {formatValue(candidate.shareMax)}
            {candidate.minorPortion === true
              ? " (minor portion)"
              : candidate.minorPortion === false
                ? " (not a minor portion)"
                : " (minor portion not stated)"}
            {candidate.pairClass !== null ? (
              <span className="section-note">
                {" "}
                (classification: <code>{candidate.pairClass}</code>)
              </span>
            ) : null}
          </li>
        ))}
      </ul>
    </>
  );
}

export function NoScenarioBlock({ document }: { document: Scenario }) {
  return (
    <section className="card" data-testid="scenario-no-scenario">
      <h2 className="section-title">
        {SCENARIO_KIND_LABELS[document.scenario_kind]} (
        <code>{document.scenario_kind}</code>) — no maximum can be stated
      </h2>
      <p>
        No draft maximum development potential could be stated for this
        property. This is an informative result from the deterministic engine,
        not an error: the recorded reasons explain what stopped a scenario, and
        any preserved ranges are shown rather than collapsed into a single
        value.
      </p>
      {document.professional_review_required ? (
        <p className="status-label" data-testid="scenario-review-required">
          Professional review required before any reliance.
        </p>
      ) : null}

      <RuleConflictBlock document={document} />
      <ShareRangeBlock document={document} />
    </section>
  );
}

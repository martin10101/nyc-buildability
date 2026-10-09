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

/**
 * Absence, for a value read out of the weakly-typed `provenance` blob.
 *
 * Every reader in scenario-display.ts runs its result through `boundedText`,
 * which yields the EMPTY STRING for a value that is present but cleans to
 * nothing (whitespace, control characters). So `null` is not the only absence
 * these fields can carry, and `?? "…"` catches only half of it — the other half
 * rendered as an invisible empty element, which reads as "the screen chose not
 * to show this" rather than "the document did not state it". Same failure as
 * the empty `<code>` in ScenarioCard, one file over.
 *
 * `absent` is always a statement about the DOCUMENT, never a value: it marks
 * that nothing was stated, and never stands in for something that was.
 */
function isAbsent(value: string | null): boolean {
  return value === null || value === "";
}

function stated(value: string | null, absent: string): string {
  return isAbsent(value) ? absent : (value as string);
}

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
                  <code>{stated(rule.ruleId, "rule id not stated")}</code> (
                  {stated(rule.ruleVersion, "version not stated")}) —{" "}
                  {/* A READOUT OF RECORDED DATES, NOT A STATEMENT OF LEGAL
                      EFFECT. Substituting "present" for an absent end date was
                      the obvious half of this — it asserts the rule is in force
                      RIGHT NOW when the document said nothing — but the
                      SENTENCE was the other half: "in effect {from} to {to}"
                      frames the pair as a live range whatever fills the slots,
                      so "in effect 2024-12-05 to end not stated" still reads as
                      a rule currently running. Whether a draft rule is in legal
                      effect is a determination this platform never makes, and
                      it is worse in this block than anywhere else: these are
                      COMPETING rules, and characterising both as in effect
                      edges towards asserting both currently govern — the one
                      thing this block exists to refuse. So the dates are
                      reported under their own contract field names and nothing
                      is concluded from them. */}
                  {isAbsent(rule.effectiveFrom) && isAbsent(rule.effectiveTo)
                    ? "no effective dates are recorded for this rule"
                    : `recorded effective dates: from ${stated(
                        rule.effectiveFrom,
                        "not stated",
                      )}, to ${stated(rule.effectiveTo, "not stated")}`}
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
            <strong>{stated(candidate.districtLabel, "district not stated")}</strong>
            {": "}
            share range min {formatValue(candidate.shareMin)} / point{" "}
            {formatValue(candidate.sharePoint)} / max{" "}
            {formatValue(candidate.shareMax)}
            {candidate.minorPortion === true
              ? " (minor portion)"
              : candidate.minorPortion === false
                ? " (not a minor portion)"
                : " (minor portion not stated)"}
            {candidate.pairClass !== null && candidate.pairClass !== "" ? (
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

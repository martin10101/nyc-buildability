import type { PropertyProfile } from "@/lib/contract";

/**
 * Professional-review affordance (task M2-T001 output 1). Honest by
 * design: the structured review workflow arrives with the M4 rule-review
 * milestone, so this panel states the review obligation and the current
 * coverage reality instead of pretending a submission workflow exists.
 */
export function ProfessionalReviewPanel({ profile }: { profile: PropertyProfile }) {
  const reviewRequired = [
    ...Object.values(profile.lot_facts),
    ...Object.values(profile.existing_building_facts),
  ].filter((fact) => fact.coverage_status === "professional_review_required").length;

  return (
    <section className="card" aria-labelledby="review-title">
      <h2 className="section-title" id="review-title">
        Professional review
      </h2>
      <p className="section-note" data-testid="review-affordance">
        Every value on this screen is an unreviewed official-source fact — no
        value has been confirmed under a published rule, and none is a legal
        determination. Results must be reviewed by qualified New York
        professionals before reliance. The platform&apos;s structured
        professional-review workflow is not yet available; it arrives with
        the rule-review milestone.
      </p>
      {reviewRequired > 0 ? (
        <p>
          {reviewRequired} fact{reviewRequired === 1 ? "" : "s"} on this
          profile {reviewRequired === 1 ? "is" : "are"} explicitly marked{" "}
          <code>professional_review_required</code>.
        </p>
      ) : null}
      {profile.reproducibility ? (
        <details className="provenance-details">
          <summary>Coverage labeling policy for this profile</summary>
          <div className="provenance-body">
            <p style={{ margin: 0 }}>{profile.reproducibility.coverage_policy}</p>
          </div>
        </details>
      ) : null}
    </section>
  );
}
